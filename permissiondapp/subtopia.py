"""Module with functions for fetching Subtopia.io subscriptions."""

import base64
from datetime import datetime, UTC
from collections import defaultdict

from algosdk.encoding import encode_address
from algosdk.v2client.algod import AlgodClient

from config import     SUBSCRIPTION_PERMISSIONS
from helpers import environment_variables


def fetch_subscriptions_from_boxes():
    """Return collection of all subscribed addresses with related subscription values.

    TODO: tests

    Box value contains the following uints:
    (tier_asset_id, 2, subscription_start, subscription_end, subscription_duration)
    
    :var env: environment variables collection
    :type env: dict
    :var client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :var subscriptions: Subtopia subscribers addresses and related tiers' values
    :type subscriptions: dict
    :var app_id: currently processed subscription tier app
    :type app_id: int
    :var amount: currently processed app's subscription amount
    :type amount: int
    :var permission: currently processed subscription app's permission
    :type permission: int
    :var boxes: collection of currently processed app's boxes fetched from Node
    :type boxes: dict
    :var box_name: currently processed box's name
    :type box_name: bytes
    :var address: currently processed box's user address
    :type address: str
    :var response: user's box response instance
    :type response: dict
    :var hexed: user box value's hexadecimal string representation
    :type hexed: str
    :var start: starting position of subscription's end value 
    :type start: int
    :return: dict
    """
    env = environment_variables()
    client = AlgodClient(env.get("algod_token"), env.get("algod_address"))
    subscriptions = defaultdict(list)

    for app_id, (amount, permission) in SUBSCRIPTION_PERMISSIONS.items():
        boxes = client.application_boxes(app_id)
        for box in boxes.get("boxes", []):
            box_name = base64.b64decode(box.get("name"))
            address = encode_address(box_name)
            response = client.application_box_by_name(app_id, box_name)
            hexed = base64.b64decode(response.get("value")).hex()
            assert len(hexed) == 80, hexed
            start = 48
            subscription_end = int(hexed[start : start + 16], 16)
            if (
                subscription_end > datetime.now(UTC).timestamp()
                or subscription_end == 0
            ):
                subscriptions[address].append((amount, permission))

    return subscriptions


if __name__ == "__main__":
    print(fetch_subscriptions_from_boxes())
