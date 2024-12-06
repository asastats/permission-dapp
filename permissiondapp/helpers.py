"""Module with Permisssion dApp helpers functions."""

import base64
import json
import os
from pathlib import Path

from algosdk import mnemonic, transaction
from algosdk.abi.contract import Contract
from algosdk.encoding import decode_address
from dotenv import load_dotenv

from permissiondapp.config import DAO_VOTES_PER_STAKING_AMOUNT


# # DEPRECATED
def extract_uint64(byte_str, index):
    """Extract a uint64 from a byte string"""
    return int.from_bytes(byte_str[index : index + 8], byteorder="big")


def deserialize_uint64(data):
    decoded = base64.b64decode(data)
    return [extract_uint64(decoded, offset) for offset in range(0, len(decoded), 8)]


def serialize_uint64(values):
    _bytes = bytes(
        x
        for i in values
        for x in int.to_bytes(i, length=8, byteorder="big", signed=False)
    )
    return base64.b64encode(_bytes).decode("ascii")


# # VALUES
def _docs_positions_offset_and_length_pairs(start=48):
    return [
        (start + (index // 2) * 10, 8)
        if divmod(index, 2)[1] == 0
        else (start + (index // 2) * 10 + 8, 1)
        for index in range(20)
    ]


def _extract_uint(byte_str, index, length):
    """Extract a uint64 from a byte string"""
    return int.from_bytes(byte_str[index : index + length], byteorder="big")


def _starting_positions_offset_and_length_pairs(end=48):
    return [(offset, 8) for offset in range(0, end, 8)]


def _value_length_from_values_position(position):
    """

    First three pairs are:
    CALCULATED_DATA = ["votes", "permission"]
    SUBSCRIPTION_DATA = ["amount", "permission"]
    CURRENT_STAKING_DATA = ["amount", "permission"]

    After those 6, pairs are (permission, doc_index).

    """
    return 8 if position < 7 or divmod(position, 2)[1] else 1


def _values_offset_and_length_pairs():
    return (
        _starting_positions_offset_and_length_pairs()
        + _docs_positions_offset_and_length_pairs()
    )


def deserialize_values_data(data):
    decoded = base64.b64decode(data)
    return [
        _extract_uint(decoded, offset, length)
        for offset, length in _values_offset_and_length_pairs()
    ]


def serialize_values(values):
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
    local_ints = 0
    local_bytes = 0
    global_ints = 0
    global_bytes = 0
    return transaction.StateSchema(global_ints, global_bytes), transaction.StateSchema(
        local_ints, local_bytes
    )


def box_name_from_address(address):
    return base64.b64encode(decode_address(address)).decode("utf-8")


def compile_program(client, source_code):
    compile_response = client.compile(source_code.decode("utf-8"))
    return base64.b64decode(compile_response["result"])


def environment_variables():
    load_dotenv()
    return {
        "creator_mnemonic": os.getenv("CREATOR_MNEMONIC"),
        "user_mnemonic": os.getenv("USER_MNEMONIC"),
        "algod_token": os.getenv("ALGOD_TOKEN"),
        "algod_address": os.getenv("ALGOD_ADDRESS"),
        "permission_app_id": os.getenv("PERMISSION_APP_ID"),
    }


def load_contract():
    contract_json = read_json(
        Path(__file__).resolve().parent / "artifacts" / "contract.json"
    )
    return Contract.undictify(contract_json)


def permission_for_amount(amount):
    for limit, votes in DAO_VOTES_PER_STAKING_AMOUNT[::-1]:
        if amount > limit:
            return (
                int((votes + ((amount - limit) / limit) * votes) * 1_000_000)
                / 1_000_000
            )
    else:
        return 0


def private_key_from_mnemonic(passphrase):
    return mnemonic.to_private_key(passphrase)


def read_json(filename):
    if os.path.exists(filename):
        with open(filename, "r") as json_file:
            try:
                return json.load(json_file)
            except json.JSONDecodeError:
                pass
    return {}


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
