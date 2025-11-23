"""Module with smart contract's utility functions ."""

import base64
import sys

from algosdk.encoding import encode_address
from algosdk.v2client.algod import AlgodClient

from helpers import box_writing_parameters, environment_variables, permission_dapp_id
from network import delete_box, permission_dapp_values_from_boxes


def delete_boxes():
    """Delete all boxes from the Permission dApp on testnet.

    This function:
    1. Retrieves environment variables and creates an Algod client
    2. Gets the application ID for the Permission dApp on testnet
    3. Fetches all boxes associated with the application
    4. Deletes each box by encoding the box name to an address

    :var env: environment variables collection
    :type env: dict
    :var app_id: Permission dApp application ID on testnet
    :type app_id: int
    :var client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :var writing_parameters: transaction parameters for box operations
    :type writing_parameters: :class:`transaction.SuggestedParams`
    :var boxes: collection of boxes associated with the application
    :type boxes: dict
    :var box_name: base64 decoded box name
    :type box_name: bytes
    :var address: Algorand address derived from box name
    :type address: str
    """
    env = environment_variables()
    app_id = permission_dapp_id(network="testnet")
    client = AlgodClient(
        env.get("algod_token_testnet"), env.get("algod_address_testnet")
    )
    writing_parameters = box_writing_parameters(env)

    boxes = client.application_boxes(app_id)
    for box in boxes.get("boxes", []):
        box_name = base64.b64decode(box.get("name"))
        address = encode_address(box_name)
        print(f"Deleting box for {address[:5]}..{address[-5:]}")
        delete_box(client, app_id, writing_parameters, address)


def print_box_values(network="testnet"):
    """Print all box values from the Permission dApp in sorted order.

    Retrieves and displays permission values from application boxes,
    sorted by the second value in descending order. Shows a message
    if no boxes are found.

    :param network: network to query (e.g., "testnet")
    :type network: str
    :var env: environment variables collection
    :type env: dict
    :var client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :var app_id: Permission dApp application ID
    :type app_id: int
    :var permissions: dictionary of address to permission values
    :type permissions: dict
    """
    env = environment_variables()
    client = AlgodClient(
        env.get(f"algod_token_{network}"), env.get(f"algod_address_{network}")
    )
    app_id = permission_dapp_id(network=network)
    permissions = permission_dapp_values_from_boxes(client, app_id)
    if not permissions:
        print("There are no boxes!")

    print(sorted(permissions.items(), key=lambda e: e[1][1], reverse=True))


def check_test_box(app_id_str):
    """Check and display test box contents for a given application ID.

    Decodes and displays box contents for testing purposes, showing:
    - The address associated with each box
    - Hexadecimal representation of box values
    - Parsed integer values in 16-byte chunks

    :param app_id_str: application ID as string
    :type app_id_str: str
    :var app_id: application ID converted to integer
    :type app_id: int
    :var env: environment variables collection
    :type env: dict
    :var client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :var boxes: collection of boxes associated with the application
    :type boxes: dict
    :var box_name: base64 decoded box name
    :type box_name: bytes
    :var address: Algorand address derived from box name
    :type address: str
    :var response: box value response from the node
    :type response: dict
    :var hexed: hexadecimal representation of box value
    :type hexed: str
    """
    app_id = int(app_id_str)
    env = environment_variables()
    client = AlgodClient(
        env.get("algod_token_testnet"), env.get("algod_address_testnet")
    )

    boxes = client.application_boxes(app_id)
    for box in boxes.get("boxes", []):
        box_name = base64.b64decode(box.get("name"))
        address = encode_address(box_name)
        response = client.application_box_by_name(app_id, box_name)
        hexed = base64.b64decode(response.get("value")).hex()
        assert len(hexed) == 80, hexed
        print(address)
        for start in range(0, 80, 16):
            value = int(hexed[start : start + 16], 16)
            print(start, value)
        print()


if __name__ == "__main__":  # pragma: no cover
    args = sys.argv
    if len(args) == 1:
        print_box_values()

    elif len(args) == 2:
        this_module = sys.modules[__name__]
        getattr(this_module, args[1])()

    else:
        this_module = sys.modules[__name__]
        getattr(this_module, args[1])(*args[2:])
