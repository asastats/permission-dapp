import base64

from algosdk import account, transaction
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    AccountTransactionSigner,
)
from algosdk.error import AlgodHTTPError

from config import STAKING_APP_ID, STAKING_KEY
from helpers import (
    app_schemas,
    box_name_from_address,
    deserialize_uint64,
    serialize_uint64,
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
    sender = account.address_from_private_key(private_key)

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
    sender = account.address_from_private_key(private_key)

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
    sp = client.suggested_params()
    atc = AtomicTransactionComposer()

    box_name = box_name_from_address(address)

    atc.add_method_call(
        app_id=app_id,
        # method=contract.get_method_by_name("createBoxWithPut"),
        method=contract.get_method_by_name("deleteBox"),
        sender=sender,
        sp=sp,
        signer=signer,
        method_args=[box_name],
        boxes=[(app_id, box_name.encode())],
    )

    # send transaction
    results = atc.execute(client, 2)

    # wait for confirmation
    print("TXID: ", results.tx_ids[0])
    print("Result confirmed in round: {}".format(results.confirmed_round))


def read_box(client, app_id, box_name):
    try:
        response = client.application_box_by_name(app_id, box_name)
    except AlgodHTTPError as exception:
        if "box not found" in exception.args:
            return None
        raise exception

    return deserialize_uint64(base64.b64decode(response.get("value")).decode("utf8"))


def write_box(client, sender, signer, app_id, contract, address, value):
    sp = client.suggested_params()
    atc = AtomicTransactionComposer()

    box_name = box_name_from_address(address)

    atc.add_method_call(
        app_id=app_id,
        method=contract.get_method_by_name("writeBox"),
        sender=sender,
        sp=sp,
        signer=signer,
        method_args=[box_name, value],
        boxes=[(app_id, box_name.encode())],
    )

    results = atc.execute(client, 2)

    # wait for confirmation
    print("TXID: ", results.tx_ids[0])
    print("Result confirmed in round: {}".format(results.confirmed_round))


def write_foundation_boxes(client, creator_private_key, app_id, contract, data):
    sender = account.address_from_private_key(creator_private_key)
    signer = AccountTransactionSigner(creator_private_key)

    for address, values in data.items():
        value = serialize_uint64(values)
        print(f"Writting box for {address[:5]}..{address[-5:]}")
        write_box(client, sender, signer, app_id, contract, address, value)
