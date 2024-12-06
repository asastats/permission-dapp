"""Module with functions for importing DAO docs and staking data."""

from collections import defaultdict
from pathlib import Path

from algosdk.v2client.algod import AlgodClient

from config import (
    CURRENT_STAKING_STARTING_POSITION,
    DAO_DISCUSSIONS_DOCS,
    DOCS_STARTING_POSITION,
    MERGED_ACCOUNTS,
    STAKING_DOCS,
    STAKING_DOCS_STARTING_INDEX,
    SUBSCRIPTION_POSITION,
)
from helpers import (
    environment_variables,
    load_contract,
    permission_for_amount,
    private_key_from_mnemonic,
    read_json,
)
from network import current_staking, write_foundation_boxes


def _calculate_and_update_votes_and_permissions(data):
    for address, value in list(data.items()):
        docs_permission = sum(amount for amount in value[DOCS_STARTING_POSITION:][::2])
        votes = int(docs_permission / 1_000_000)

        subscription_permission = value[SUBSCRIPTION_POSITION + 1]  # initally 0
        staking_permission = value[CURRENT_STAKING_STARTING_POSITION + 1]

        data[address][0] = votes
        data[address][1] = (
            subscription_permission + staking_permission + docs_permission
        )


def _initial_check():
    env = environment_variables()
    if env.get("permission_app_id") is None:
        raise ValueError("Permission dApp ID isn't set!")

    client = AlgodClient(env.get("algod_token"), env.get("algod_address"))
    boxes = client.application_boxes(int(env.get("permission_app_id")))
    if len(boxes.get("boxes", [])):
        raise ValueError("Some boxes are already populated!")

    return env, client


def _load_and_merge_accounts(doc_id, stem="allocations"):
    doc_data = read_json(
        Path(__file__).resolve().parent / "DAO" / doc_id / f"{stem}.json"
    )
    return {
        MERGED_ACCOUNTS.get(address, address): value
        for address, value in doc_data.items()
    }


def _load_and_parse_foundation_data(data, items):
    for index, doc_id in enumerate(items):
        doc_data = _load_and_merge_accounts(doc_id)
        for address, value in doc_data.items():
            data[address].append(value * 1_000_000)
            data[address].append(index)


def _load_and_parse_staking_data(data, items):
    for index, doc_id in enumerate(items):
        governors_data = _load_and_merge_accounts(doc_id, stem="dao_governors")
        for address, value in governors_data.items():
            data[address].append(int(value[0] * 1_000_000))
            data[address].append(STAKING_DOCS_STARTING_INDEX + index)

        ongoing_governors_data = _load_and_merge_accounts(
            doc_id, stem="dao_ongoing_governors"
        )
        for address, value in ongoing_governors_data.items():
            data[address].append(int(value[0] * 1_000_000))
            data[address].append(STAKING_DOCS_STARTING_INDEX + index)


def _prepare_data(client):
    """Collect and return collection of addresses and related values.

    :param client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :var data: collection of addresses and related permission and votes values
    :type data: dict
    :return: dict
    """
    data = defaultdict(lambda: [0] * DOCS_STARTING_POSITION)
    _load_and_parse_foundation_data(data, items=DAO_DISCUSSIONS_DOCS)
    _load_and_parse_staking_data(data, items=STAKING_DOCS)
    _update_current_staking(
        client, data, starting_position=CURRENT_STAKING_STARTING_POSITION
    )
    _calculate_and_update_votes_and_permissions(data)
    return data


def _update_current_staking(client, data, starting_position):
    """Check and update cutrent staking values for all data` addresses.

    :param client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :var data: collection of addresses and related permission and votes values
    :type data: dict
    :var starting_position: staking permission's index in values collection
    :type starting_position: int
    :var address: currentrly processed public Algorand address
    :type address: str
    :var current_staking_amount: current address' staking amount
    :type current_staking_amount: int
    """
    for address in data:
        print(f"Checking current staking for {address[:5]}..{address[-5:]}")
        current_staking_amount = current_staking(client, address)
        if current_staking_amount:
            data[address][starting_position] = current_staking_amount
            data[address][starting_position + 1] = permission_for_amount(
                current_staking_amount
            )


def prepare_and_write_data():
    """Collect and write collection of DAO addresses and related values.

    :var env: environment variables collection
    :type env: dict
    :var client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :var data: collection of addresses and related permission and votes values
    :type data: dict
    :var creator_private_key: application creator's base64 encoded private key
    :type creator_private_key: str
    :var app_id: Permission dApp identifier
    :type app_id: int
    :var contract: application caller's address
    :type contract: :class:`Contract`
    """
    env, client = _initial_check()
    data = _prepare_data(client)
    creator_private_key = private_key_from_mnemonic(env.get("creator_mnemonic"))
    app_id = int(env.get("permission_app_id"))
    contract = load_contract()
    write_foundation_boxes(client, creator_private_key, app_id, contract, data)


if __name__ == "__main__":
    prepare_and_write_data()
