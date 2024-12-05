import base64

from algosdk.v2client import algod


def deserialize_uint64(data: str) -> list[int]:
    decoded = base64.b64decode(data)
    return [extract_uint64(decoded, offset) for offset in range(0, len(decoded), 8)]


def extract_uint64(byte_str: bytes, index: int) -> int:
    """Extract a uint64 from a byte string"""
    return int.from_bytes(byte_str[index : index + 8], byteorder="big")


algod_address = "https://testnet-api.4160.nodely.dev"
algod_token = ""

algod_client = algod.AlgodClient(algod_token, algod_address)

APP_ID = 730132583

boxes = algod_client.application_boxes(APP_ID)
for box in boxes.get("boxes", []):
    box_name = base64.b64decode(box.get("name"))
    response = algod_client.application_box_by_name(APP_ID, box_name)
    value = base64.b64decode(response.get("value")).decode("utf8")
    print(box_name, deserialize_uint64(value))
