import base64
import json
import os
from pathlib import Path

from algosdk import transaction
from algosdk import account, mnemonic
from algosdk.abi.contract import Contract
from algosdk.error import AlgodHTTPError
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


def serialize_uint64(values):
    _bytes = bytes(
        x
        for i in values
        for x in int.to_bytes(i, length=8, byteorder="big", signed=False)
    )
    return base64.b64encode(_bytes).decode("ascii")


def call_app(client, private_key, app_id, contract, box_name):
    # get sender address
    sender = account.address_from_private_key(private_key)
    # create a Signer object
    signer = AccountTransactionSigner(private_key)

    # get node suggested parameters
    sp = client.suggested_params()

    values = serialize_uint64([2000, 10084793375367, 10, 1])

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

    # app_id = _create(algod_client, creator_private_key)

    app_id = 730132583
    try:
        user_private_key = get_private_key_from_mnemonic(user_mnemonic)
        _call(algod_client, user_private_key, app_id, box_name="box_name_user")

    except AlgodHTTPError as exception:
        assert "logic eval error" in exception.args[0]

    _call(algod_client, creator_private_key, app_id, box_name="box_name2")

    # # delete application
    # delete_app(algod_client, creator_private_key, app_id)


main()
