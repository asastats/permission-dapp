"""Module with Permission dApp helpers functions."""

import base64
import json
import os
import time
from copy import deepcopy
from pathlib import Path

from algosdk.abi.contract import Contract
from algosdk.account import address_from_private_key
from algosdk.atomic_transaction_composer import AccountTransactionSigner
from algosdk.encoding import decode_address
from algosdk.mnemonic import to_private_key
from algosdk.transaction import StateSchema
from algosdk.v2client.indexer import IndexerClient
from dotenv import load_dotenv

from config import (
    CURRENT_STAKING_POSITION,
    DOCS_STARTING_POSITION,
    INDEXER_ADDRESS,
    INDEXER_TOKEN,
    MANDATORY_VALUES_SIZE,
    PERMISSION_APP_ID,
    PERMISSION_APP_ID_TESTNET,
    STAKING_AMOUNT_VOTES,
    SUBSCRIPTION_POSITION,
)


# # VALUES
def _docs_positions_offset_and_length_pairs(
    docs_data_size, start=MANDATORY_VALUES_SIZE
):
    """Return offset/position and size pairs for docs values with size `docs_data_size`

    :param docs_data_size: size of serialized docs values
    :type docs_data_size: int
    :param start: starting position of documents' values
    :type start: int
    :return: list
    """
    return [
        (
            (start + (index // 2) * 9, 8)
            if divmod(index, 2)[1] == 0
            else (start + (index // 2) * 9 + 8, 1)
        )
        for counter, index in enumerate(range(30))
        if counter // 2 < docs_data_size // 9
    ]


def _extract_uint(byte_str, index, length):
    """Return extarcted uint from providedc byte string.

    :param byte_str: base64 encoded values
    :type byte_str: bytes
    :param index: target value's position/index in data
    :type index: int
    :param length: target value's bytes size/length
    :type length: int
    :return: int
    """
    return int.from_bytes(byte_str[index : index + length], byteorder="big")


def _starting_positions_offset_and_length_pairs(end=MANDATORY_VALUES_SIZE):
    """Return offset/position and related bytes size/length for starting values.

    Starting three pairs are:
    CALCULATED_DATA = ["votes", "permission"]
    SUBSCRIPTION_DATA = ["amount", "permission"]
    CURRENT_STAKING_DATA = ["amount", "permission"]

    :param end: starting values right boundary
    :type end: int
    :return: list
    """
    return [(offset, 8) for offset in range(0, end, 8)]


def _value_length_from_values_position(position):
    """Return bytes length of the value defined by providced `position`

    First three pairs are:
    CALCULATED_DATA = ["votes", "permission"]
    SUBSCRIPTION_DATA = ["amount", "permission"]
    CURRENT_STAKING_DATA = ["amount", "permission"]

    After those 6, pairs are (permission, doc_index).

    :param position: value index/position in values collection
    :type position: int
    :return: int
    """
    return 8 if position < 6 or divmod(position, 2)[1] == 0 else 1


def _values_offset_and_length_pairs(docs_data_size):
    """Return offset/position and related bytes size/length of serialized values data.

    Provided `docs_data_size` represents size after mandatory starting size.

    :param docs_data_size: size of docs values pairs
    :type docs_data_size: int
    :return: list
    """
    return (
        _starting_positions_offset_and_length_pairs()
        + _docs_positions_offset_and_length_pairs(docs_data_size)
    )


def deserialize_values_data(data):
    """Return collection of integer values deserialized from base64 encoded `data`.

    :param data: base64 encoded values collection
    :type data: str
    :var decoded: base64 decoded values collection
    :type decoded: bytes
    :var offset: current value's offset/position in encoded data
    :type offset: int
    :var length: current value's size in bytes
    :type length: int
    :return: list
    """
    decoded = base64.b64decode(data)
    return [
        _extract_uint(decoded, offset, length)
        for offset, length in _values_offset_and_length_pairs(
            len(decoded) - MANDATORY_VALUES_SIZE
        )
    ]


def serialize_values(values):
    """Return base64 encoded data serialized from `values` collection of integers.

    :param values: collection of integer values to serialize
    :type values: list
    :var _bytes: serialized values collection
    :type _bytes: bytes
    :var position: current byte's position in serialized data
    :type position: int
    :var val: current byte's value in serialized data
    :type val: int
    :return: str
    """
    _bytes = bytes(
        x
        for position, val in enumerate(values)
        for x in int.to_bytes(
            val,
            length=_value_length_from_values_position(position),
            byteorder="big",
            signed=False,
        )
    )
    return base64.b64encode(_bytes).decode("ascii")


# # CONTRACT
def app_schemas(contract_json):
    """Return instances of state schemas for smart contract's global and local apps.

    :param contract_json: full path to smart contract's JSON file
    :type contract_json: dict
    :var schema: smart contract's schema
    :type schema: dict
    :var global_schema: smart contract's global schema
    :type global_schema: dict
    :var local_schema: smart contract's local schema
    :type local_schema: dict
    :var local_bytes: total number of local bytes states
    :type local_bytes: int
    :var global_ints: total number of global uint states
    :type global_ints: int
    :var global_bytes: total number of global bytes states
    :type global_bytes: int
    :return: two-tuple
    """
    schema = contract_json.get("state", {}).get("schema", {})
    global_schema = schema.get("global", {})
    local_schema = schema.get("local", {})

    global_ints = global_schema.get("ints", 0)
    global_bytes = global_schema.get("bytes", 0)
    local_ints = local_schema.get("ints", 0)
    local_bytes = local_schema.get("bytes", 0)

    return StateSchema(global_ints, global_bytes), StateSchema(local_ints, local_bytes)


def compile_program(client, source_code):
    """Collect and return collection of addresses and related values.

    :param client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :var source_code: approval/clear program code
    :type source_code: bytes
    :var compile_response: compilation response from Node instance
    :type compile_response: dict
    :return: str
    """
    compile_response = client.compile(source_code.decode("utf-8"))
    return base64.b64decode(compile_response["result"])


def load_contract(dapp_name="PermissionDApp"):
    """Load from disk, instantiate and return Permission dApp smart contract object.

    :var contract_json: full path to Permission dApp smart contract file
    :type contract_json: dict
    :return: :class:`Contract`
    """
    contract_json = read_json(
        Path(__file__).resolve().parent / "artifacts" / f"{dapp_name}.arc56.json"
    )
    return Contract.undictify(contract_json)


# # STAKING
def _application_transaction(params, indexer_client):
    """Yield transaction connected with application defined by provided `params`.

    :param params: collection of arguments to search transactions endpoint
    :type params: dict
    :param indexer_client: Algorand Indexer client instance
    :type indexer_client: :class:`IndexerClient`
    :var results: fetched page of transactions
    :type results: dict
    :var transaction: transaction instance
    :type transaction: dict
    :yield: dict
    """
    results = _application_transactions(params, indexer_client, delay=1)
    while results.get("transactions"):
        for transaction in results.get("transactions"):
            yield transaction

        pause(1)
        results = _application_transactions(
            params,
            indexer_client,
            next_page=results.get("next-token"),
            delay=1,
        )


def _application_transactions(
    params, indexer_client, next_page=None, delay=1, error_delay=5, retries=20
):
    """Fetch and return transactions from indexer instance based on provided params.

    :param params: collection of parameters to indexer search method
    :type params: dict
    :param indexer_client: Algorand Indexer client instance
    :type indexer_client: :class:`IndexerClient`
    :param next_page: custom code identifying very next page of search results
    :type next_page: str
    :param delay: delay in seconds before Indexer call
    :type delay: float
    :param error_delay: delay in seconds after error
    :type error_delay: int
    :param retries: maximum number of retries before system exit
    :type retries: int
    :var _params: updated parameters to indexer search method
    :type _params: dict
    :var counter: current number of retries to fetch the block
    :type counter: int
    :return: dict
    """
    _params = deepcopy(params)
    if next_page:
        _params.update({"next_page": next_page})

    counter = 0
    while True:
        try:
            pause(delay)
            return indexer_client.search_transactions(**_params)

        except Exception as e:
            if counter >= retries:
                print("Maximum number of retries reached. Exiting...")
                return {}

            print(
                "Exception %s raised searching transactions: %s; Paused..."
                % (
                    e,
                    _params,
                )
            )
            pause(error_delay)
            counter += 1


def _indexer_instance():
    """Return Algorand Indexer instance.

    :return: :class:`IndexerClient`
    """
    return IndexerClient(
        INDEXER_TOKEN, INDEXER_ADDRESS, headers={"User-Agent": "algosdk"}
    )


def governance_staking_addresses(staking_app_id=None, staking_min_round=None):
    """Return all addresses involved in the staking program run by `staking_app_id`.

    :param staking_app_id: Algorand application identifier
    :type staking_app_id: int
    :var addresses: collection of public Algorand adresses
    :type addresses: set
    :var indexer_client: Algorand Indexer client instance
    :type indexer_client: :class:`IndexerClient`
    :var params: collection of arguments provided to Indexer method
    :type params: dict
    :var transaction: currently processed application transaction instance
    :type transaction: dict
    :return: set
    """
    if staking_app_id is None:
        return set()

    addresses = set()
    indexer_client = _indexer_instance()
    params = {
        "application_id": staking_app_id,
        "limit": 1000,
        "min_round": staking_min_round,
    }
    for transaction in _application_transaction(params, indexer_client):
        addresses.add(transaction.get("sender"))

    return addresses


# # HELPERS
def box_name_from_address(address):
    """Return string representation of base64 encoded public Algorand `address`.

    :param address: governance seat address
    :type address: bytes
    :return: str
    """
    return decode_address(address)


def box_writing_parameters(env, network="testnet"):
    """Instantiate and return arguments needed for writing boxes to blockchain.

    :param env: environment variables collection
    :type env: dict
    :param network: network suffix for environment variable keys
    :type network: str
    :var creator_private_key: application creator's base64 encoded private key
    :type creator_private_key: str
    :var sender: application caller's address
    :type sender: str
    :var signer: application caller's signer instance
    :type signer: :class:`AccountTransactionSigner`
    :var contract: application caller's address
    :type contract: :class:`Contract`
    :return: dict
    """
    creator_private_key = private_key_from_mnemonic(
        env.get(f"creator_{network}_mnemonic")
    )
    sender = address_from_private_key(creator_private_key)
    signer = AccountTransactionSigner(creator_private_key)
    contract = load_contract()

    return {"sender": sender, "signer": signer, "contract": contract}


def calculate_votes_and_permission(values):
    """Calculate and update votes and permission values for all addresses in `data`.

    :param data: collection of addresses and related permission and votes values
    :type data: dict
    :var address: currently processed governance seat address
    :type address: str
    :var values: collection of integer values
    :type values: list
    :var docs_permission: total permission from foundation and staking documents
    :type docs_permission: tuple
    :var votes: total votes from foundation and staking documents
    :type votes: int
    :var subscription_permission: permission value from address' subcription tier
    :type subscription_permission: int
    :var staking_permission: permission value from address' current governance staking
    :type staking_permission: int
    :return: two-tuple
    """
    docs_permission = sum(amount for amount in values[DOCS_STARTING_POSITION:][::2])
    votes = int(docs_permission / 1_000_000)
    subscription_permission = values[SUBSCRIPTION_POSITION + 1]
    staking_permission = values[CURRENT_STAKING_POSITION + 1]

    return votes, subscription_permission + staking_permission + docs_permission


def environment_variables():
    """Return collection of required environment variables.

    :return: dict
    """
    load_dotenv()
    return {
        "algod_token_testnet": os.getenv("ALGOD_TOKEN_TESTNET"),
        "algod_token_mainnet": os.getenv("ALGOD_TOKEN_MAINNET"),
        "algod_address_testnet": os.getenv("ALGOD_ADDRESS_TESTNET"),
        "algod_address_mainnet": os.getenv("ALGOD_ADDRESS_MAINNET"),
        "creator_testnet_mnemonic": os.getenv("CREATOR_TESTNET_MNEMONIC"),
        "creator_mainnet_mnemonic": os.getenv("CREATOR_MAINNET_MNEMONIC"),
        "user_testnet_mnemonic": os.getenv("USER_TESTNET_MNEMONIC"),
        "user_mainnet_mnemonic": os.getenv("USER_MAINNET_MNEMONIC"),
    }


def pause(seconds=1):
    """Sleep for provided number of seconds.

    :param seconds: number of seconds to pause
    :type seconds: int
    """
    time.sleep(seconds)


def permission_dapp_id(network="testnet"):
    """Return Permission dApp identifier for provided `network`.

    :param network: network to check the dapp ID for (e.g., "testnet")
    :type network: str
    :return: int
    """
    return PERMISSION_APP_ID if network == "mainnet" else PERMISSION_APP_ID_TESTNET


def permission_for_amount(amount):
    """Calculate and return permission value from provided `amount`.

    :param amount: amount in ASASTATS to calculate permission value for
    :type amount: int
    :param boundary: currently processed minimum staking amount boundary
    :type boundary: int
    :param votes: number of votes for currently processed boundary
    :type votes: float
    :return: int
    """
    for boundary, votes in STAKING_AMOUNT_VOTES[::-1]:
        if amount > boundary:
            return int((votes + ((amount - boundary) / boundary) * votes) * 1_000_000)

    else:
        return 0


def private_key_from_mnemonic(passphrase):
    """Return base64 encoded private key created from provided mnemonic `passphrase`.

    :param passphrase: collection of English words separated by spaces
    :type passphrase: str
    :return: str
    """
    return to_private_key(passphrase)


def read_json(filename):
    """Return collection of key and values created from provided `filename` JSON file.

    :param filename: full path to JSON file
    :type filename: :class:`pathlib.Path`
    :return: dict
    """
    if os.path.exists(filename):
        with open(filename, "r") as json_file:
            try:
                return json.load(json_file)
            except json.JSONDecodeError:
                pass
    return {}


def wait_for_confirmation(client, txid):
    """Wait for a blockchain transaction to be confirmed.

    Polls Algorand node until the transaction referenced by `txid`
    is confirmed in a round. Prints waiting messages until confirmation
    then returns full pending transaction information.

    :param client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :param txid: blockchain transaction ID
    :type txid: str
    :return: pending transaction info including confirmed round
    :rtype: dict
    """
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
