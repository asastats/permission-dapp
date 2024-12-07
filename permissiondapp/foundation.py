"""Module with functions for importing DAO docs and staking data."""

from collections import defaultdict
from pathlib import Path

from algosdk.v2client.algod import AlgodClient

from config import (
    CURRENT_STAKING_STARTING_POSITION,
    DAO_DISCUSSIONS_DOCS,
    DAO_DISCUSSIONS_DOCS_STARTING_INDEX,
    DOCS_STARTING_POSITION,
    MERGED_ACCOUNTS,
    STAKING_DOCS,
    STAKING_DOCS_STARTING_INDEX,
    SUBSCRIPTION_POSITION,
)
from helpers import (
    environment_variables,
    governance_staking_addresses,
    load_contract,
    permission_for_amount,
    private_key_from_mnemonic,
    read_json,
)
from network import current_staking, write_foundation_boxes


# # HELPERS
def _calculate_and_update_votes_and_permissions(data):
    """Calculkate and update votes and permission values for all addresses in `data`.

    :param data: collection of addresses and related permission and votes values
    :type data: dict
    :var address: currently processed governance seat address
    :type address: str
    :var values: collection of integer values
    :type values: list
    :var docs_permission: total permission from foundation and staking documents
    :type docs_permission: tuple
    :var votes: total votes from foundation and staking documents
    :type votes: int
    :var subscription_permission: permission value from address' subcription tier
    :type subscription_permission: int
    :var staking_permission: permission value from address' current governance staking
    :type staking_permission: int
    """
    for address, values in list(data.items()):
        docs_permission = sum(amount for amount in values[DOCS_STARTING_POSITION:][::2])
        votes = int(docs_permission / 1_000_000)

        subscription_permission = values[SUBSCRIPTION_POSITION + 1]  # initally 0
        staking_permission = values[CURRENT_STAKING_STARTING_POSITION + 1]

        data[address][0] = votes
        data[address][1] = (
            subscription_permission + staking_permission + docs_permission
        )


def _initial_check():
    """Return environment variables and client instances.

    Raise ValueError if Permission dApp ID isn't set.
    Raise ValueError if there are existing dApp boxes.

    :var env: environment variables collection
    :type env: dict
    :var client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :var boxes: collection of app's boxes fetched from Node
    :type boxes: dict
    """
    env = environment_variables()
    if env.get("permission_app_id") is None:
        raise ValueError("Permission dApp ID isn't set!")

    client = AlgodClient(env.get("algod_token"), env.get("algod_address"))
    boxes = client.application_boxes(int(env.get("permission_app_id")))
    if len(boxes.get("boxes", [])):
        raise ValueError("Some boxes are already populated!")

    return env, client


# # FOUNDATION
def _load_and_merge_accounts(doc_id, stem="allocations"):
    """Update `data` with the values collected from foundation docs found in `items`.

    :param doc_id: document identifier
    :type doc_id: str
    :param stem: JSON file name to read data from
    :type stem: str
    :var doc_data: curently processed document's addresses and values collections
    :type doc_data: dict
    """
    doc_data = read_json(
        Path(__file__).resolve().parent / "DAO" / doc_id / f"{stem}.json"
    )
    return {
        MERGED_ACCOUNTS.get(address, address): value
        for address, value in doc_data.items()
    }


def _load_and_parse_foundation_data(data, items):
    """Update `data` with the values collected from foundation docs found in `items`.

    :param data: collection of addresses and related permission and votes values
    :type data: dict
    :param items: collection of document identifiers
    :type items: tuple
    :var index: curently processed document index
    :type index: int
    :var doc_id: curently processed document identifier
    :type doc_id: str
    :var doc_data: curently processed document's addresses and values collections
    :type doc_data: dict
    """
    for index, doc_id in enumerate(items):
        doc_data = _load_and_merge_accounts(doc_id)
        for address, value in doc_data.items():
            data[address].append(value * 1_000_000)
            data[address].append(DAO_DISCUSSIONS_DOCS_STARTING_INDEX + index)


def _load_and_parse_staking_data(data, items):
    """Update `data` with the values collected from staking documents found in `items`.

    :param data: collection of addresses and related permission and votes values
    :type data: dict
    :param items: collection of document identifiers
    :type items: tuple
    :var index: curently processed document index
    :type index: int
    :var doc_id: curently processed document identifier
    :type doc_id: str
    :var governors_data: curently processed document's governors data
    :type governors_data: dict
    :var ongoing_governors_data: curently processed document's eligible governors data
    :type ongoing_governors_data: dict
    """
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
    _update_current_staking_for_foundation(
        client, data, starting_position=CURRENT_STAKING_STARTING_POSITION
    )
    _update_current_staking_for_non_foundation(
        client, data, starting_position=CURRENT_STAKING_STARTING_POSITION
    )
    _calculate_and_update_votes_and_permissions(data)
    return data


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


# # STAKING
def _update_current_staking_for_foundation(client, data, starting_position):
    """Check and update cutrent staking values for all data` addresses.

    :param client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :param data: collection of addresses and related permission and votes values
    :type data: dict
    :param starting_position: staking permission's index in values collection
    :type starting_position: int
    :var address: currentrly processed governance seat address
    :type address: str
    :var current_staking_amount: current address' staking amount
    :type current_staking_amount: int
    """
    for address in data:
        current_staking_amount = current_staking(client, address)
        data[address][starting_position] = current_staking_amount
        data[address][starting_position + 1] = (
            permission_for_amount(current_staking_amount)
            if current_staking_amount
            else 0
        )


def _update_current_staking_for_non_foundation(client, data, starting_position):
    """Check and update cutrent staking values for addresses not found in `data`.

    :param client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :param data: collection of addresses and related permission and votes values
    :type data: dict
    :param starting_position: staking permission's index in values collection
    :type starting_position: int
    :var non_foundation: collection of adresses and staking amounts for non-foundation
    :type non_foundation: dict
    :var address: currentrly processed governance seat address
    :type address: str
    :var amount: current address' staking amount
    :type amount: int
    :var permission: current address' permission value
    :type permission: int
    """
    non_foundation = {
        address: current_staking(client, address)
        for address in governance_staking_addresses()
        if address not in data
    }
    for address, amount in non_foundation.items():
        if amount:
            permission = permission_for_amount(amount)
            if permission:
                data[address][starting_position] = amount
                data[address][starting_position + 1] = permission


if __name__ == "__main__":
    prepare_and_write_data()
