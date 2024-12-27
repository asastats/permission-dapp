import base64
import sys

from algosdk.encoding import encode_address
from algosdk.v2client.algod import AlgodClient

from helpers import box_writing_parameters, environment_variables
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
        address = encode_address(box_name)
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


def check_test_box(app_id_str):
    app_id = int(app_id_str)
    env = environment_variables()
    client = AlgodClient(env.get("algod_token"), env.get("algod_address"))

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

        # KGTSKYBFYC4WHYQ5PLP7FAMGET7OUWPE6AZXJWQAKTMCI4BMZ6FGCPSHPQ
        # 0 730727847
        # 16 2
        # 32 1734003205
        # 48 1734089605
        # 64 86400

        # OECZJTT5M2RTJMAWG7N3RBIJSU4M37O47DGHKLHLI6ZNHK5Q7ZDM2VMI6I
        # 0 730727773
        # 16 2
        # 32 1734003053
        # 48 1734089453
        # 64 86400

        # # AFTER EXPIRATION EVERYTHING'S THE SAME:
        # KGTSKYBFYC4WHYQ5PLP7FAMGET7OUWPE6AZXJWQAKTMCI4BMZ6FGCPSHPQ
        # 0 730727847
        # 16 2
        # 32 1734003205
        # 48 1734089605
        # 64 86400

        # OECZJTT5M2RTJMAWG7N3RBIJSU4M37O47DGHKLHLI6ZNHK5Q7ZDM2VMI6I
        # 0 730727773
        # 16 2
        # 32 1734003053
        # 48 1734089453
        # 64 86400

        # # AFTER CANCELING KGTSK..PSHPQ:
        # OECZJTT5M2RTJMAWG7N3RBIJSU4M37O47DGHKLHLI6ZNHK5Q7ZDM2VMI6I
        # 0 730727773
        # 16 2
        # 32 1734003053
        # 48 1734089453
        # 64 86400


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
