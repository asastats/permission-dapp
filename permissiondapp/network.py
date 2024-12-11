"""Module with functions for retrieving and saving blockchain data."""

import base64
from collections import defaultdict
from datetime import datetime, UTC

from algosdk import transaction
from algosdk.account import address_from_private_key
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    AccountTransactionSigner,
)
from algosdk.encoding import encode_address
from algosdk.error import AlgodHTTPError
from algosdk.v2client.algod import AlgodClient

from config import STAKING_APP_ID, STAKING_KEY, SUBSCRIPTION_PERMISSIONS
from helpers import (
    app_schemas,
    box_name_from_address,
    deserialize_values_data,
    environment_variables,
    serialize_values,
    wait_for_confirmation,
)


# # SUBCRIPTIONS
def fetch_subscriptions_from_boxes():
    """Return collection of all subscribed addresses with related subscription values.

    Box value contains the following uints:
    (tier_asset_id, 2, subscription_start, subscription_end, subscription_duration)

    :var env: environment variables collection
    :type env: dict
    :var client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :var subscriptions: Subtopia subscribers addresses and related tiers' values
    :type subscriptions: dict
    :var app_id: currently processed subscription tier app
    :type app_id: int
    :var amount: currently processed app's subscription amount
    :type amount: int
    :var permission: currently processed subscription app's permission
    :type permission: int
    :var boxes: collection of currently processed app's boxes fetched from Node
    :type boxes: dict
    :var box_name: currently processed box's name
    :type box_name: bytes
    :var address: currently processed box's user address
    :type address: str
    :var response: user's box response instance
    :type response: dict
    :var hexed: user box value's hexadecimal string representation
    :type hexed: str
    :var start: starting position of subscription's end value
    :type start: int
    :return: dict
    """
    env = environment_variables()
    client = AlgodClient(env.get("algod_token"), env.get("algod_address"))
    subscriptions = defaultdict(list)

    for app_id, (amount, permission) in SUBSCRIPTION_PERMISSIONS.items():
        boxes = client.application_boxes(app_id)
        for box in boxes.get("boxes", []):
            box_name = base64.b64decode(box.get("name"))
            address = encode_address(box_name)
            response = client.application_box_by_name(app_id, box_name)
            hexed = base64.b64decode(response.get("value")).hex()
            assert len(hexed) == 80, hexed
            start = 48
            subscription_end = int(hexed[start : start + 16], 16)
            if (
                subscription_end > datetime.now(UTC).timestamp()
                or subscription_end == 0
            ):
                subscriptions[address].append((amount, permission))

    return subscriptions


# #  STAKING
def _cometa_app_amount(key, state):
    """Return amount behind provided key for provided Cometa app.

    :param key: app key to look for
    :type key: str
    :param state: Cometa smart contract application's local state data
    :type state: dict
    :return: int
    """
    try:
        return next(
            int(base64.b64decode(row.get("value", {}).get("bytes")).hex()[2:18], 16)
            for row in state.get("key-value")
            if row.get("key") == key and len(row.get("value", {}).get("bytes")) >= 16
        )
    except (StopIteration, TypeError):
        return 0


def _cometa_app_local_state_for_address(client, address):
    """Return Cometa's ASASTATS staking dApp's local state instance from account info.

    :param client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :param address: governance seat address
    :type address: str
    :var account_info: account's information object
    :type account_info: dict
    :return: dict
    """
    try:
        account_info = client.account_info(address)
    except AlgodHTTPError:
        return None

    return next(
        (
            state
            for state in account_info.get("apps-local-state", [])
            if state.get("id") == STAKING_APP_ID
        ),
        None,
    )


def current_governance_staking_for_address(client, address):
    """Return staking amount for `address` from Cometa's staking program.

    :param client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :param address: governance seat address associated with the box
    :type address: str
    :var state: staking application's local state object
    :type state: dict
    :return: int
    """
    print(f"Checking current staking for {address[:5]}..{address[-5:]}")
    state = _cometa_app_local_state_for_address(client, address)
    return _cometa_app_amount(STAKING_KEY, state) if state else 0


# # PERMISSION DAPP
def create_app(client, private_key, approval_program, clear_program):
    """TODO: docstring and tests"""
    # define sender as creator
    sender = address_from_private_key(private_key)

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()
    # # comment out the next two (2) lines to use suggested fees
    # params.flat_fee = True
    # params.fee = 1000

    global_schema, local_schema = app_schemas()

    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(
        sender,
        params,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
    )

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    print("Created new app-id: ", app_id)

    return app_id


def delete_app(client, private_key, index):
    """TODO: docstring and tests"""
    # declare sender
    sender = address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationDeleteTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Deleted app-id: ", transaction_response["txn"]["txn"]["apid"])


def delete_box(client, sender, signer, app_id, contract, address):
    """Delete  box owned by `app_id` defined by provided `address`.

    :param client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :param sender: application caller's address
    :type sender: str
    :param signer: application caller's address
    :type signer: :class:`AccountTransactionSigner`
    :param app_id: Permission dApp identifier
    :type app_id: int
    :param contract: application caller's address
    :type contract: :class:`Contract`
    :param address: governance seat address associated with the box
    :type address: str
    :var atc: transaction composer instance
    :type atc: :class:`AtomicTransactionComposer`
    :var box_name: base64 encoded box name
    :type box_name: str
    :var response: application call's response
    :type response: :class:`AtomicTransactionResponse`
    """
    atc = AtomicTransactionComposer()

    box_name = box_name_from_address(address)

    atc.add_method_call(
        app_id=app_id,
        method=contract.get_method_by_name("deleteBox"),
        sender=sender,
        sp=client.suggested_params(),
        signer=signer,
        method_args=[box_name],
        boxes=[(app_id, box_name.encode())],
    )

    # send transaction
    response = atc.execute(client, 2)

    # wait for confirmation
    print("TXID: ", response.tx_ids[0])
    print("Result confirmed in round: {}".format(response.confirmed_round))


def deserialized_permission_dapp_box_value(client, app_id, box_name):
    """Fetch `box_name`  value and return deserialized values from it.

    :param client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :param app_id: Permission dApp identifier
    :type app_id: int
    :param box_name: base64 encoded box name
    :type box_name: str
    :var response: fetch application box call's response
    :type response: :class:`AtomicTransactionResponse`
    :return: list
    """
    try:
        response = client.application_box_by_name(app_id, box_name)
    except AlgodHTTPError as exception:
        if "box not found" in exception.args:
            return None
        raise exception

    return deserialize_values_data(
        base64.b64decode(response.get("value")).decode("utf8")
    )


def permission_dapp_values_from_boxes():
    """Return collection of all addresses with related votes and permission values.

    :var env: environment variables collection
    :type env: dict
    :var permissions: collection of addresses and related votes and permission values
    :type permissions: dict
    :var app_id: currently processed subscription tier app
    :type app_id: int
    :var client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :var boxes: collection of Pewrmission dApp's boxes fetched from Node
    :type boxes: dict
    :var box_name: currently processed box's name
    :type box_name: bytes
    :var address: currently processed box's user address
    :type address: str
    :var values: collection of deserialized values for currently processed address
    :type values: int
    :return: dict
    """
    env = environment_variables()
    if env.get("permission_app_id") is None:
        raise ValueError("Permission dApp ID isn't set!")

    permissions = {}
    app_id = int(env.get("permission_app_id"))
    client = AlgodClient(env.get("algod_token"), env.get("algod_address"))
    boxes = client.application_boxes(app_id)
    for box in boxes.get("boxes", []):
        box_name = base64.b64decode(box.get("name"))
        address = encode_address(box_name)
        values = deserialized_permission_dapp_box_value(client, app_id, box_name)
        if not values:
            continue

        permissions[address] = values
    return permissions


def write_box(client, sender, signer, app_id, contract, address, value):
    """Write `value` to the box owned by `app_id` defined by provided `address`.

    :param client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :param sender: application caller's address
    :type sender: str
    :param signer: application caller's signer instance
    :type signer: :class:`AccountTransactionSigner`
    :param app_id: Permission dApp identifier
    :type app_id: int
    :param contract: application caller's address
    :type contract: :class:`Contract`
    :param address: governance seat address associated with the box
    :type address: str
    :param value: serialized base64 encoded values collection
    :type value: str
    :var atc: transaction composer instance
    :type atc: :class:`AtomicTransactionComposer`
    :var box_name: base64 encoded box name
    :type box_name: str
    :var response: application call's response
    :type response: :class:`AtomicTransactionResponse`
    """
    atc = AtomicTransactionComposer()

    box_name = box_name_from_address(address)

    atc.add_method_call(
        app_id=app_id,
        method=contract.get_method_by_name("writeBox"),
        sender=sender,
        sp=client.suggested_params(),
        signer=signer,
        method_args=[box_name, value],
        boxes=[(app_id, box_name.encode())],
    )

    response = atc.execute(client, 2)

    # wait for confirmation
    print("TXID: ", response.tx_ids[0])
    print("Result confirmed in round: {}".format(response.confirmed_round))


def write_foundation_boxes(client, creator_private_key, app_id, contract, data):
    """Write to the boxes owned by `app_id` values extracted from provided `data`.

    :param client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :param creator_private_key: application creator's base64 encoded private key
    :type creator_private_key: str
    :param app_id: Permission dApp identifier
    :type app_id: int
    :param contract: application caller's address
    :type contract: :class:`Contract`
    :var data: collection of addresses and associated integer values
    :type data: dict
    :var sender: application caller's address
    :type sender: str
    :var signer: application caller's signer instance
    :type signer: :class:`AccountTransactionSigner`
    :var address: currently processed governance seat address
    :type address: str
    :var values: currently processed integer values collection
    :type values: list
    :var value: currently processed serialized base64 encoded values collection
    :type value: str
    """
    sender = address_from_private_key(creator_private_key)
    signer = AccountTransactionSigner(creator_private_key)

    for address, values in data.items():
        value = serialize_values(values)
        print(f"Writting box for {address[:5]}..{address[-5:]}")
        write_box(client, sender, signer, app_id, contract, address, value)
