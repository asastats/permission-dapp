import base64
import datetime
import json
import os
from pathlib import Path

from algosdk import transaction
from algosdk import account, mnemonic
from algosdk.abi.contract import Contract
from algosdk.v2client import algod

from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
)

# user declared account mnemonics
creator_mnemonic = (
    "fruit jeans surface glide metal "
    "relax mutual capital supreme repeat "
    "scorpion indicate matrix guess decade "
    "mountain observe suspect poem forward "
    "dismiss figure lemon about dumb"
)
user_mnemonic = (
    "grain frame soap tray clock "
    "salmon travel chunk public planet "
    "disagree essay clay call volume "
    "moment chair mystery scissors goddess "
    "invest tribe grit able sketch"
)

# user declared algod connection parameters
algod_address = "https://testnet-api.4160.nodely.dev"
algod_token = ""

# declare application state storage (immutable)
local_ints = 0
local_bytes = 0
global_ints = 0
global_bytes = 0
global_schema = transaction.StateSchema(global_ints, global_bytes)
local_schema = transaction.StateSchema(local_ints, local_bytes)


# helper function to compile program source
def compile_program(client, source_code):
    compile_response = client.compile(source_code.decode("utf-8"))
    return base64.b64decode(compile_response["result"])


# helper function that converts a mnemonic passphrase into a private signing key
def get_private_key_from_mnemonic(mn):
    private_key = mnemonic.to_private_key(mn)
    return private_key


# helper function that waits for a given txid to be confirmed by the network
def wait_for_confirmation(client, txid):
    last_round = client.status().get("last-round")
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get("confirmed-round") and txinfo.get("confirmed-round") > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print(
        "Transaction {} confirmed in round {}.".format(
            txid, txinfo.get("confirmed-round")
        )
    )
    return txinfo


# create new application
def create_app(
    client, private_key, approval_program, clear_program, global_schema, local_schema
):
    # define sender as creator
    sender = account.address_from_private_key(private_key)

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

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


# opt-in to application
def opt_in_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)
    print("OptIn from account: ", sender)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationOptInTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("OptIn to app-id: ", transaction_response["txn"]["txn"]["apid"])


# # call application
# def call_app(client, private_key, index, app_args):
#     # declare sender
#     sender = account.address_from_private_key(private_key)
#     print("Call from account: ", sender)

#     # get node suggested parameters
#     params = client.suggested_params()
#     # comment out the next two (2) lines to use suggested fees
#     params.flat_fee = True
#     params.fee = 1000

#     # create unsigned transaction
#     txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args)

#     # sign transaction
#     signed_txn = txn.sign(private_key)
#     tx_id = signed_txn.transaction.get_txid()

#     # send transaction
#     client.send_transactions([signed_txn])

#     # await confirmation
#     wait_for_confirmation(client, tx_id)

#     # display results
#     transaction_response = client.pending_transaction_info(tx_id)
#     print("Called app-id: ", transaction_response["txn"]["txn"]["apid"])
#     if "global-state-delta" in transaction_response:
#         print("Global State updated :\n", transaction_response["global-state-delta"])
#     if "local-state-delta" in transaction_response:
#         print("Local State updated :\n", transaction_response["local-state-delta"])


# # read user local state
# def read_local_state(client, addr, app_id):
#     results = client.account_info(addr)
#     local_state = results["apps-local-state"][0]
#     for index in local_state:
#         if local_state[index] == app_id:
#             print(
#                 f"local_state of account {addr} for app_id {app_id}: ",
#                 local_state["key-value"],
#             )


# # read app global state
# def read_global_state(client, addr, app_id):
#     results = client.account_info(addr)
#     apps_created = results["created-apps"]
#     for app in apps_created:
#         if app["id"] == app_id:
#             print(f"global_state for app_id {app_id}: ", app["params"]["global-state"])


# # update existing application
# def update_app(client, private_key, app_id, approval_program, clear_program) :
#     # declare sender
#     sender = account.address_from_private_key(private_key)

# #    # define initial value for key "timestamp"
# #    app_args = [b'initial value']

# 	# get node suggested parameters
#     params = client.suggested_params()
#     # comment out the next two (2) lines to use suggested fees
#     params.flat_fee = True
#     params.fee = 1000

#     # create unsigned transaction
#     txn = transaction.ApplicationUpdateTxn(sender, params, app_id, \
#                                             approval_program, clear_program) #, app_args)

#     # sign transaction
#     signed_txn = txn.sign(private_key)
#     tx_id = signed_txn.transaction.get_txid()

#     # send transaction
#     client.send_transactions([signed_txn])

#     # await confirmation
#     wait_for_confirmation(client, tx_id)

#     # display results
#     transaction_response = client.pending_transaction_info(tx_id)
#     app_id = transaction_response['txn']['txn']['apid']
#     print("Updated existing app-id: ",app_id)


# delete application
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


# close out from application
def close_out_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationCloseOutTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Closed out from app-id: ", transaction_response["txn"]["txn"]["apid"])


# clear application
def clear_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationClearStateTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Cleared app-id: ", transaction_response["txn"]["txn"]["apid"])


# example: APP_ROUTER_CALLER
# call application
# convert 64 bit integer i to byte string
def intToBytes(i):
    return i.to_bytes(8, "big")


# Not used but may be handy for e.g. users of the lib when writing unit tests.
def serialize_uint64(values):
    _bytes = bytes(
        x
        for i in values
        for x in int.to_bytes(i, length=8, byteorder="big", signed=False)
    )
    return base64.b64encode(_bytes).decode("ascii")


def deserialize_uint64(data: str) -> list[int]:
    decoded = base64.b64decode(data)
    return [extract_uint64(decoded, offset) for offset in range(0, len(decoded), 8)]


def extract_uint64(byte_str: bytes, index: int) -> int:
    """Extract a uint64 from a byte string"""
    return int.from_bytes(byte_str[index : index + 8], byteorder="big")


def call_app(client, private_key, app_id, contract, box_name):
    # get sender address
    sender = account.address_from_private_key(private_key)
    # create a Signer object
    signer = AccountTransactionSigner(private_key)

    # get node suggested parameters
    sp = client.suggested_params()

    # values = intToBytes(2000) + intToBytes(100) + intToBytes(10) + intToBytes(1)
    values = serialize_uint64([2000, 100, 10])

    # Create an instance of AtomicTransactionComposer
    atc = AtomicTransactionComposer()
    atc.add_method_call(
        app_id=app_id,
        # method=contract.get_method_by_name("createBoxWithPut"),
        method=contract.get_method_by_name("writeBox"),
        sender=sender,
        sp=sp,
        signer=signer,
        # method_args=["first_name"],
        # method_args=["new_name", values.decode()],
        method_args=[box_name, values],
        boxes=[(app_id, box_name.encode())],
    )

    # send transaction
    results = atc.execute(client, 2)

    # wait for confirmation
    print("TXID: ", results.tx_ids[0])
    print("Result confirmed in round: {}".format(results.confirmed_round))


def read_json(filename):
    if os.path.exists(filename):
        with open(filename, "r") as json_file:
            try:
                return json.load(json_file)
            except json.JSONDecodeError:
                pass
    return {}


def _create(algod_client, creator_private_key):
    approval_program_source = (
        open(Path(__file__).resolve().parent / "artifacts" / "approval.teal")
        .read()
        .encode()
    )

    clear_program_source = (
        open(Path(__file__).resolve().parent / "artifacts" / "clear.teal")
        .read()
        .encode()
    )

    # compile programs
    approval_program = compile_program(algod_client, approval_program_source)
    clear_program = compile_program(algod_client, clear_program_source)

    # create new application
    app_id = create_app(
        algod_client,
        creator_private_key,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
    )
    print("App ID: ", app_id)


def _call(algod_client, creator_private_key, app_id, box_name="box_name1"):
    contract_json = read_json(
        Path(__file__).resolve().parent / "artifacts" / "contract.json"
    )
    contract = Contract.undictify(contract_json)

    # TODO: only creator should be able to make a call

    call_app(algod_client, creator_private_key, app_id, contract, box_name=box_name)


def main():
    # initialize an algodClient
    algod_client = algod.AlgodClient(algod_token, algod_address)

    # define private keys
    creator_private_key = get_private_key_from_mnemonic(creator_mnemonic)
    user_private_key = get_private_key_from_mnemonic(user_mnemonic)

    # app_id = _create(algod_client, creator_private_key)

    app_id = 730129052
    _call(algod_client, creator_private_key, app_id, box_name="box_name3")

    # # delete application
    # delete_app(algod_client, creator_private_key, app_id)


main()
