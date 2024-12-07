"""Module with Permisssion dApp helpers functions."""

import base64
import json
import os
from pathlib import Path

from algosdk.abi.contract import Contract
from algosdk.encoding import decode_address
from algosdk.mnemonic import to_private_key
from algosdk.transaction import StateSchema
from dotenv import load_dotenv

from config import STAKING_AMOUNT_VOTES_BOUNDARIES, MANDATORY_VALUES_SIZE


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
        (start + (index // 2) * 9, 8)
        if divmod(index, 2)[1] == 0
        else (start + (index // 2) * 9 + 8, 1)
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
def app_schemas():
    """Return instances of state schemas for smart contract's global and local apps.

    :param local_ints: total number of local uint states
    :type local_ints: int
    :var local_bytes: total number of local bytes states
    :type local_bytes: int
    :var global_ints: total number of global uint states
    :type global_ints: int
    :var global_bytes: total number of global bytes states
    :type global_bytes: int
    :return: two-tuple
    """
    local_ints = 0
    local_bytes = 0
    global_ints = 0
    global_bytes = 0
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


def load_contract():
    """Load from disk, instantiate and return Permission dApp smart contract object.

    :var contract_json: full path to Permission dApp smart contract file
    :type contract_json: dict
    :return: :class:`Contract`
    """
    contract_json = read_json(
        Path(__file__).resolve().parent / "artifacts" / "contract.json"
    )
    return Contract.undictify(contract_json)


# # HELPERS
def box_name_from_address(address):
    """Return string representation of base64 encoded public Algorand `address`.

    :param address: governance seat address
    :type address: str
    :return: str
    """
    return base64.b64encode(decode_address(address)).decode("utf-8")


def environment_variables():
    """Return collection of required environment variables.

    :return: dict
    """
    load_dotenv()
    return {
        "creator_mnemonic": os.getenv("CREATOR_MNEMONIC"),
        "user_mnemonic": os.getenv("USER_MNEMONIC"),
        "algod_token": os.getenv("ALGOD_TOKEN"),
        "algod_address": os.getenv("ALGOD_ADDRESS"),
        "permission_app_id": os.getenv("PERMISSION_APP_ID"),
    }


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
    for boundary, votes in STAKING_AMOUNT_VOTES_BOUNDARIES[::-1]:
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
    """TODO: docstring and tests"""
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
