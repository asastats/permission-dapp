import base64

from algosdk.v2client import algod


algod_address = "https://testnet-api.4160.nodely.dev"
algod_token = ""

algod_client = algod.AlgodClient(algod_token, algod_address)

APP_ID = 730129052

boxes = algod_client.application_boxes(APP_ID)
for box in boxes.get("boxes", []):
    box_name = base64.b64decode(box.get("name"))

    response = algod_client.application_box_by_name(APP_ID, box_name)
    print(box_name, response.get("value"))
    # hexed = base64.b64decode(response.get("value")).hex()
