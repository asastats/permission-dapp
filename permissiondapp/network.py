import base64

from algosdk import transaction
from algosdk.account import address_from_private_key
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    AccountTransactionSigner,
)
from algosdk.error import AlgodHTTPError

from config import STAKING_APP_ID, STAKING_KEY
from helpers import (
    app_schemas,
    box_name_from_address,
    deserialize_values_data,
    serialize_values,
    wait_for_confirmation,
)


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
    :param address: public Algorand address
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


def create_app(client, private_key, approval_program, clear_program):
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


def current_staking(client, address):
    state = _cometa_app_local_state_for_address(client, address)
    return _cometa_app_amount(STAKING_KEY, state) if state else 0


def delete_app(client, private_key, index):
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
    :param address: public Algorand address associated with the box
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


def read_box(client, app_id, box_name):
    try:
        response = client.application_box_by_name(app_id, box_name)
    except AlgodHTTPError as exception:
        if "box not found" in exception.args:
            return None
        raise exception

    return deserialize_values_data(
        base64.b64decode(response.get("value")).decode("utf8")
    )


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
    :param address: public Algorand address associated with the box
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
    :var address: currently processed public Algorand address
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
