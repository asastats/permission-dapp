"""Module with functions for importing DAO docs and staking data."""

from collections import defaultdict
from pathlib import Path

from algosdk.v2client.algod import AlgodClient

from config import (
    CURRENT_STAKING_POSITION,
    DAO_DISCUSSIONS_DOCS,
    DAO_DISCUSSIONS_DOCS_STARTING_INDEX,
    DOCS_STARTING_POSITION,
    MERGED_ACCOUNTS,
    STAKING_DOCS,
    STAKING_DOCS_STARTING_INDEX,
)
from helpers import (
    box_writing_parameters,
    calculate_votes_and_permission,
    environment_variables,
    governance_staking_addresses,
    permission_dapp_id,
    permission_for_amount,
    read_json,
)
from network import (
    check_and_update_changed_subscriptions_and_staking,
    check_and_update_new_stakers,
    check_and_update_new_subscribers,
    current_governance_staking_for_address,
    fetch_subscriptions_from_boxes,
    permission_dapp_values_from_boxes,
    write_foundation_boxes,
)


# # HELPERS
def _calculate_and_update_votes_and_permissions(data):
    """Calculate and update votes and permission values for all addresses in `data`.

    :param data: collection of addresses and related permission and votes values
    :type data: dict
    :var address: currently processed governance seat address
    :type address: str
    :var values: collection of integer values
    :type values: list
    :var votes: total address' votes from foundation and staking documents
    :type votes: int
    :var permission: total address' permission value
    :type permission: int
    """
    for address, values in list(data.items()):
        votes, permission = calculate_votes_and_permission(values)
        data[address][0] = votes
        data[address][1] = permission


def _initial_check(network="testnet"):
    """Return environment variables and client instances.

    Raise ValueError if Permission dApp ID isn't set.
    Raise ValueError if there are existing dApp boxes.

    :param network: network to deploy to (e.g., "testnet")
    :type network: str
    :var env: environment variables collection
    :type env: dict
    :var client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :var boxes: collection of app's boxes fetched from Node
    :type boxes: dict
    :return: two-tuple
    """
    env = environment_variables()
    client = AlgodClient(
        env.get(f"algod_token_{network}"), env.get(f"algod_address_{network}")
    )

    boxes = client.application_boxes(permission_dapp_id(network))
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
            data[address].append(int(value * 1_000_000))
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


def _prepare_data(env, network="testnet"):
    """Collect and return collection of addresses and related values.

    :param env: environment variables collection
    :type env: dict
    :param network: network to deploy to (e.g., "testnet")
    :type network: str
    :var data: collection of addresses and related permission and votes values
    :type data: dict
    :var client: Algorand Node Mainnet client instance
    :type client: :class:`AlgodClient`
    :return: dict
    """
    data = defaultdict(lambda: [0] * DOCS_STARTING_POSITION)
    _load_and_parse_foundation_data(data, items=DAO_DISCUSSIONS_DOCS)
    _load_and_parse_staking_data(data, items=STAKING_DOCS)

    client = AlgodClient(
        env.get(f"algod_token_{network}"), env.get(f"algod_address_{network}")
    )
    _update_current_staking_for_foundation(
        client, data, starting_position=CURRENT_STAKING_POSITION
    )
    _update_current_staking_for_non_foundation(
        client, data, starting_position=CURRENT_STAKING_POSITION
    )

    _calculate_and_update_votes_and_permissions(data)
    return data


def prepare_and_write_data(network="testnet"):
    """Collect and write collection of DAO addresses and related values.

    :param network: network to deploy to (e.g., "testnet")
    :type network: str
    :var env: environment variables collection
    :type env: dict
    :var client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :var data: collection of addresses and related permission and votes values
    :type data: dict
    :var writing_parameters: instances sneeded for writing boxes to blockchain
    :type writing_parameters: dict
    """
    env, client = _initial_check(network=network)
    data = _prepare_data(env, network=network)
    writing_parameters = box_writing_parameters(env, network=network)
    write_foundation_boxes(
        client, permission_dapp_id(network), writing_parameters, data
    )


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
        current_staking_amount = current_governance_staking_for_address(client, address)
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
        address: current_governance_staking_for_address(client, address)
        for address in governance_staking_addresses()
        if address not in data
    }
    for address, amount in non_foundation.items():
        if amount:
            permission = permission_for_amount(amount)
            if permission:
                data[address][starting_position] = amount
                data[address][starting_position + 1] = permission


# # UPDATE
def check_and_update_permission_dapp_boxes(network="testnet"):
    """Check and update boxes if staking and/or subscription values have changed.

    :param network: network to deploy to (e.g., "testnet")
    :type network: str
    :var env: environment variables collection
    :type env: dict
    :var client: Algorand Node client instance
    :type client: :class:`AlgodClient`
    :var mainnet_client: Algorand Mainnet Node client instance
    :type mainnet_client: :class:`AlgodClient`
    :var app_id: Pewrmission dApp identifier
    :type app_id: int
    :var writing_parameters: instances sneeded for writing boxes to blockchain
    :type writing_parameters: dict
    :var subscriptions: Subtopia subscribers addresses and related tiers' values
    :type subscriptions: dict
    :var stakings: collection  of all governance staking addresses and related amounts
    :type stakings: dict
    :var permissions: collection of addresses and related votes and permission values
    :type permissions: dict
    """
    env = environment_variables()
    app_id = permission_dapp_id(network)
    client = AlgodClient(
        env.get(f"algod_token_{network}"), env.get(f"algod_address_{network}")
    )
    mainnet_client = AlgodClient(
        env.get("algod_token_mainnet"), env.get("algod_address_mainnet")
    )
    writing_parameters = box_writing_parameters(env, network=network)

    subscriptions = fetch_subscriptions_from_boxes(client)
    stakings = {
        address: current_governance_staking_for_address(mainnet_client, address)
        for address in governance_staking_addresses()
    }
    permissions = permission_dapp_values_from_boxes(client, app_id)

    check_and_update_new_subscribers(
        client, app_id, writing_parameters, permissions, subscriptions
    )
    check_and_update_new_stakers(
        client, app_id, writing_parameters, permissions, stakings
    )
    check_and_update_changed_subscriptions_and_staking(
        client, app_id, writing_parameters, permissions, subscriptions, stakings
    )


if __name__ == "__main__":  # pragma: no cover
    prepare_and_write_data()
    # import time

    # start = time.time()
    # check_and_update_permission_dapp_boxes()
    # print("Duration:", time.time() - start)
