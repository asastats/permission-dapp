import base64
import sys

from algosdk import account
from algosdk.encoding import decode_address, encode_address
from algosdk.v2client.algod import AlgodClient
from algosdk.atomic_transaction_composer import AccountTransactionSigner

from helpers import box_writing_parameters, environment_variables, load_contract, private_key_from_mnemonic
from network import delete_box, permission_dapp_values_from_boxes


def delete_boxes():
    env = environment_variables()
    if env.get("permission_app_id") is None:
        raise ValueError("Permission dApp ID isn't set!")

    if "testnet" not in env.get("algod_address"):
        raise ValueError("Can't delete non-testnet dApp!")

    app_id = int(env.get("permission_app_id"))
    client = AlgodClient(env.get("algod_token"), env.get("algod_address"))
    writing_parameters = box_writing_parameters(env)

    boxes = client.application_boxes(app_id)
    for box in boxes.get("boxes", []):
        box_name = base64.b64decode(box.get("name"))
        address = encode_address(base64.b64decode(box_name))
        print(f"Deleting box for {address[:5]}..{address[-5:]}")
        delete_box(client, app_id, writing_parameters, address)


def print_box_values():
    env = environment_variables()
    client = AlgodClient(env.get("algod_token"), env.get("algod_address"))
    app_id = int(env.get("permission_app_id"))
    permissions = permission_dapp_values_from_boxes(client, app_id)
    if not permissions:
        print("There are no boxes!")

    print(sorted(permissions.items(), key=lambda e: e[1][1], reverse=True))


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
