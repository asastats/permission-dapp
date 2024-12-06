import base64
import sys

from algosdk import account
from algosdk.encoding import decode_address, encode_address
from algosdk.v2client.algod import AlgodClient
from algosdk.atomic_transaction_composer import AccountTransactionSigner

from helpers import (
    deserialize_uint64,
    environment_variables,
    load_contract,
    private_key_from_mnemonic,
)
from network import delete_box


def print_box_values():
    env = environment_variables()
    if env.get("permission_app_id") is None:
        raise ValueError("Permission dApp ID isn't set!")

    app_id = int(env.get("permission_app_id"))
    client = AlgodClient(env.get("algod_token"), env.get("algod_address"))

    boxes = client.application_boxes(app_id)
    for box in boxes.get("boxes", []):
        box_name = base64.b64decode(box.get("name"))
        address = encode_address(base64.b64decode(box_name))
        response = client.application_box_by_name(app_id, box_name)
        value = base64.b64decode(response.get("value")).decode("utf8")
        print(address, deserialize_uint64(value))

    else:
        if len(boxes.get("boxes", [])) == 0:
            print(f"There are no boxes for dApp ID: {app_id}")


def delete_boxes():
    env = environment_variables()
    if env.get("permission_app_id") is None:
        raise ValueError("Permission dApp ID isn't set!")

    if "testnet" not in env.get("algod_address"):
        raise ValueError("Can't delete non-testnet dApp!")

    app_id = int(env.get("permission_app_id"))
    client = AlgodClient(env.get("algod_token"), env.get("algod_address"))

    creator_private_key = private_key_from_mnemonic(env.get("creator_mnemonic"))

    sender = account.address_from_private_key(creator_private_key)
    # create a Signer object
    signer = AccountTransactionSigner(creator_private_key)

    contract = load_contract()

    boxes = client.application_boxes(app_id)
    for box in boxes.get("boxes", []):
        box_name = base64.b64decode(box.get("name"))
        address = encode_address(base64.b64decode(box_name))
        print(f"Deleting box for {address[:5]}..{address[-5:]}")
        delete_box(client, sender, signer, app_id, contract, address)


def to_bytes(address):
    print(base64.b64encode(decode_address(address)).decode("utf-8"))


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        print_box_values()

    elif len(args) == 2:
        this_module = sys.modules[__name__]
        getattr(this_module, args[1])()

    else:
        this_module = sys.modules[__name__]
        getattr(this_module, args[1])(*args[2:])
