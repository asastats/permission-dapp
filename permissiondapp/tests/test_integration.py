"""Permission dApp integration tests module."""

import pytest
from algosdk import account
from algosdk.atomic_transaction_composer import AccountTransactionSigner
from algosdk.error import AlgodHTTPError
from algosdk.v2client.algod import AlgodClient

from helpers import (
    box_name_from_address,
    environment_variables,
    load_contract,
    private_key_from_mnemonic,
    serialize_values,
)
from network import delete_box, read_box, write_box


# # VALUES
class TestIntegrationForNonCreator:
    """Testing class for Permission dApp integration tests."""

    # # delete_box
    def test_helpers_delete_box_raises_error_for_non_creator_caller(self):
        env = environment_variables()
        client = AlgodClient(env.get("algod_token"), env.get("algod_address"))
        user_private_key = private_key_from_mnemonic(env.get("user_mnemonic"))
        sender = account.address_from_private_key(user_private_key)
        signer = AccountTransactionSigner(user_private_key)
        app_id = int(env.get("permission_app_id"))
        contract = load_contract()
        address = "2EVGZ4BGOSL3J64UYDE2BUGTNTBZZZLI54VUQQNZZLYCDODLY33UGXNSIU"
        with pytest.raises(AlgodHTTPError) as exception:
            delete_box(client, sender, signer, app_id, contract, address)
        assert "logic eval error" in str(exception.value)

    def test_helpers_delete_box_for_creator_caller(self):
        env = environment_variables()
        if "testnet" not in env.get("algod_address"):
            return

        client = AlgodClient(env.get("algod_token"), env.get("algod_address"))
        creator_private_key = private_key_from_mnemonic(env.get("creator_mnemonic"))
        sender = account.address_from_private_key(creator_private_key)
        signer = AccountTransactionSigner(creator_private_key)
        app_id = int(env.get("permission_app_id"))
        contract = load_contract()
        address = "2EVGZ4BGOSL3J64UYDE2BUGTNTBZZZLI54VUQQNZZLYCDODLY33UGXNSIU"
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        value = serialize_values(values)
        write_box(client, sender, signer, app_id, contract, address, value)
        box_name = box_name_from_address(address).encode()
        returned = read_box(client, app_id, box_name)
        assert returned == values
        delete_box(client, sender, signer, app_id, contract, address)
        returned = read_box(client, app_id, box_name)
        assert returned is None

    # # write_box
    def test_helpers_write_box_raises_error_for_non_creator_caller(self):
        env = environment_variables()
        client = AlgodClient(env.get("algod_token"), env.get("algod_address"))
        user_private_key = private_key_from_mnemonic(env.get("user_mnemonic"))
        sender = account.address_from_private_key(user_private_key)
        signer = AccountTransactionSigner(user_private_key)
        app_id = int(env.get("permission_app_id"))
        contract = load_contract()
        address = "2EVGZ4BGOSL3J64UYDE2BUGTNTBZZZLI54VUQQNZZLYCDODLY33UGXNSIU"
        value = serialize_values([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        with pytest.raises(AlgodHTTPError) as exception:
            write_box(client, sender, signer, app_id, contract, address, value)
        assert "logic eval error" in str(exception.value)

    def test_helpers_write_box_for_creator_caller(self):
        env = environment_variables()
        if "testnet" not in env.get("algod_address"):
            return

        client = AlgodClient(env.get("algod_token"), env.get("algod_address"))
        creator_private_key = private_key_from_mnemonic(env.get("creator_mnemonic"))
        sender = account.address_from_private_key(creator_private_key)
        signer = AccountTransactionSigner(creator_private_key)
        app_id = int(env.get("permission_app_id"))
        contract = load_contract()
        address = "2EVGZ4BGOSL3J64UYDE2BUGTNTBZZZLI54VUQQNZZLYCDODLY33UGXNSIU"
        box_name = box_name_from_address(address).encode()
        returned = read_box(client, app_id, box_name)
        if returned:
            delete_box(client, sender, signer, app_id, contract, address)
        returned = read_box(client, app_id, box_name)
        assert returned is None
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        value = serialize_values(values)
        write_box(client, sender, signer, app_id, contract, address, value)
        returned = read_box(client, app_id, box_name)
        assert returned == values
        delete_box(client, sender, signer, app_id, contract, address)        
