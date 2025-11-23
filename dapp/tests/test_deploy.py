"""Testing module for :py:mod:`deploy` module."""

from pathlib import Path
from unittest import mock

import deploy
from deploy import deploy_app, fund_app


# # VALUES
class TestDeployFunctions:
    """Testing class for :py:mod:`deploy` functions."""

    # # deploy_app
    def test_deploy_deploy_app_for_provided_network(self, mocker):
        algod_token, algod_address, creator_mnemonic = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        dapp_name = "PermissionDApp"
        env = {
            "algod_token_mainnet": algod_token,
            "algod_address_mainnet": algod_address,
            "creator_mainnet_mnemonic": creator_mnemonic,
            "algod_token_testnet": mocker.MagicMock(),
            "algod_address_testnet": mocker.MagicMock(),
            "creator_testnet_mnemonic": mocker.MagicMock(),
        }
        mocked_env = mocker.patch("deploy.environment_variables", return_value=env)
        client = mocker.MagicMock()
        mocked_client = mocker.patch("deploy.AlgodClient", return_value=client)
        creator_private_key = mocker.MagicMock()
        mocked_private_key = mocker.patch(
            "deploy.private_key_from_mnemonic",
            return_value=creator_private_key,
        )
        contract_json = {"contract": "json"}
        mocked_json = mocker.patch("deploy.read_json", return_value=contract_json)
        approval_program, clear_program = mocker.MagicMock(), mocker.MagicMock()
        mocked_compile = mocker.patch(
            "deploy.compile_program",
            side_effect=[approval_program, clear_program],
        )
        app_id = 5050
        genesis_hash = "SGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiI="
        mocked_create = mocker.patch(
            "deploy.create_app", return_value=(app_id, genesis_hash)
        )
        approval_source, clear_source, json_file = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        contract_json_path = (
            Path(deploy.__file__).resolve().parent
            / "artifacts"
            / f"{dapp_name}.arc56.json"
        )
        with mock.patch(
            "deploy.open",
            side_effect=[approval_source, clear_source, json_file],
        ) as mocked_open, mock.patch("deploy.json.dump") as mocked_dump:
            returned = deploy_app(network="mainnet")
            assert returned == app_id
            calls = [
                mocker.call(
                    Path(deploy.__file__).resolve().parent
                    / "artifacts"
                    / f"{dapp_name}.approval.teal"
                ),
                mocker.call(
                    Path(deploy.__file__).resolve().parent
                    / "artifacts"
                    / f"{dapp_name}.clear.teal"
                ),
                mocker.call(contract_json_path, "w"),
            ]
            mocked_open.assert_has_calls(calls, any_order=True)
            assert mocked_open.call_count == 3
            mocked_dump.assert_called_once_with(
                contract_json, json_file.__enter__.return_value, indent=4
            )
            approval_source.read.assert_called_once_with()
            approval_source.read.return_value.encode.assert_called_once_with()
            clear_source.read.assert_called_once_with()
            clear_source.read.return_value.encode.assert_called_once_with()
        mocked_env.assert_called_once_with()
        mocked_client.assert_called_once_with(algod_token, algod_address)
        mocked_private_key.assert_called_once_with(creator_mnemonic)
        mocked_json.assert_called_once_with(contract_json_path)
        calls = [
            mocker.call(client, approval_source.read.return_value.encode.return_value),
            mocker.call(client, clear_source.read.return_value.encode.return_value),
        ]
        mocked_compile.assert_has_calls(calls, any_order=True)
        assert mocked_compile.call_count == 2
        mocked_create.assert_called_once_with(
            client, creator_private_key, approval_program, clear_program, contract_json
        )

    def test_deploy_deploy_app_functionality(self, mocker):
        algod_token, algod_address, creator_mnemonic = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        dapp_name = "PermissionDApp"
        env = {
            "algod_token_mainnet": mocker.MagicMock(),
            "algod_address_mainnet": mocker.MagicMock(),
            "creator_mainnet_mnemonic": mocker.MagicMock(),
            "algod_token_testnet": algod_token,
            "algod_address_testnet": algod_address,
            "creator_testnet_mnemonic": creator_mnemonic,
        }
        mocked_env = mocker.patch("deploy.environment_variables", return_value=env)
        client = mocker.MagicMock()
        mocked_client = mocker.patch("deploy.AlgodClient", return_value=client)
        creator_private_key = mocker.MagicMock()
        mocked_private_key = mocker.patch(
            "deploy.private_key_from_mnemonic",
            return_value=creator_private_key,
        )
        contract_json = {"contract": "json", "networks": {"foo": "bar"}}
        mocked_json = mocker.patch("deploy.read_json", return_value=contract_json)
        approval_program, clear_program = mocker.MagicMock(), mocker.MagicMock()
        mocked_compile = mocker.patch(
            "deploy.compile_program",
            side_effect=[approval_program, clear_program],
        )
        app_id = 5050
        genesis_hash = "SGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiI="
        mocked_create = mocker.patch(
            "deploy.create_app", return_value=(app_id, genesis_hash)
        )
        approval_source, clear_source, json_file = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        contract_json_path = (
            Path(deploy.__file__).resolve().parent
            / "artifacts"
            / f"{dapp_name}.arc56.json"
        )
        with mock.patch(
            "deploy.open",
            side_effect=[approval_source, clear_source, json_file],
        ) as mocked_open, mock.patch("deploy.json.dump") as mocked_dump:
            returned = deploy_app()
            assert returned == app_id
            assert (
                "SGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiI="
                in contract_json["networks"]
            )
            assert contract_json["networks"][
                "SGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiI="
            ] == {"appID": 5050}
            calls = [
                mocker.call(
                    Path(deploy.__file__).resolve().parent
                    / "artifacts"
                    / f"{dapp_name}.approval.teal"
                ),
                mocker.call(
                    Path(deploy.__file__).resolve().parent
                    / "artifacts"
                    / f"{dapp_name}.clear.teal"
                ),
                mocker.call(contract_json_path, "w"),
            ]
            mocked_open.assert_has_calls(calls, any_order=True)
            assert mocked_open.call_count == 3
            mocked_dump.assert_called_once_with(
                contract_json, json_file.__enter__.return_value, indent=4
            )
            approval_source.read.assert_called_once_with()
            approval_source.read.return_value.encode.assert_called_once_with()
            clear_source.read.assert_called_once_with()
            clear_source.read.return_value.encode.assert_called_once_with()
        mocked_env.assert_called_once_with()
        mocked_client.assert_called_once_with(algod_token, algod_address)
        mocked_private_key.assert_called_once_with(creator_mnemonic)
        mocked_json.assert_called_once_with(contract_json_path)
        calls = [
            mocker.call(client, approval_source.read.return_value.encode.return_value),
            mocker.call(client, clear_source.read.return_value.encode.return_value),
        ]
        mocked_compile.assert_has_calls(calls, any_order=True)
        assert mocked_compile.call_count == 2
        mocked_create.assert_called_once_with(
            client, creator_private_key, approval_program, clear_program, contract_json
        )

    # # fund_app
    def test_deploy_fund_app_for_provided_amount(self, mocker):
        app_id = 5059
        network = "testnet"
        amount = 500_000

        env = {
            "algod_token_testnet": "token",
            "algod_address_testnet": "address",
            "creator_testnet_mnemonic": "mnemonic",
        }

        mocked_env = mocker.patch("deploy.environment_variables", return_value=env)

        client = mocker.MagicMock()
        mocked_client = mocker.patch("deploy.AlgodClient", return_value=client)

        creator_private_key = mocker.MagicMock()
        mocked_private_key = mocker.patch(
            "deploy.private_key_from_mnemonic",
            return_value=creator_private_key,
        )

        sender = "sender-address"
        mocked_address = mocker.patch(
            "deploy.address_from_private_key",
            return_value=sender,
        )

        app_address = "app-escrow-address"
        mocked_app_address = mocker.patch(
            "deploy.get_application_address", return_value=app_address
        )

        suggested_params = mocker.MagicMock()
        client.suggested_params.return_value = suggested_params

        mock_tx = mocker.MagicMock()
        mock_signed = mocker.MagicMock()
        mock_signed.transaction.get_txid.return_value = "tx123"

        mocked_payment = mocker.patch("deploy.PaymentTxn", return_value=mock_tx)
        mock_tx.sign.return_value = mock_signed

        mocked_wait = mocker.patch("deploy.wait_for_confirmation")
        mocker.patch("builtins.print")  # suppress output

        fund_app(app_id, network, amount=amount)

        mocked_env.assert_called_once_with()
        mocked_client.assert_called_once_with("token", "address")
        mocked_private_key.assert_called_once_with("mnemonic")
        mocked_address.assert_called_once_with(creator_private_key)
        mocked_app_address.assert_called_once_with(app_id)

        mocked_payment.assert_called_once_with(
            sender=sender,
            sp=suggested_params,
            receiver=app_address,
            amt=amount,
        )

        client.send_transactions.assert_called_once_with([mock_signed])
        mocked_wait.assert_called_once_with(client, "tx123")

    def test_deploy_fund_app_for_no_env_variable(self, mocker):
        app_id = 5059
        network = "testnet"

        env = {
            "algod_token_testnet": "token",
            "algod_address_testnet": "address",
            "creator_testnet_mnemonic": "mnemonic",
        }

        mocked_env = mocker.patch("deploy.environment_variables", return_value=env)

        client = mocker.MagicMock()
        mocked_client = mocker.patch("deploy.AlgodClient", return_value=client)

        creator_private_key = mocker.MagicMock()
        mocked_private_key = mocker.patch(
            "deploy.private_key_from_mnemonic",
            return_value=creator_private_key,
        )

        sender = "sender-address"
        mocked_address = mocker.patch(
            "deploy.address_from_private_key",
            return_value=sender,
        )

        app_address = "app-escrow-address"
        mocked_app_address = mocker.patch(
            "deploy.get_application_address", return_value=app_address
        )

        suggested_params = mocker.MagicMock()
        client.suggested_params.return_value = suggested_params

        mock_tx = mocker.MagicMock()
        mock_signed = mocker.MagicMock()
        mock_signed.transaction.get_txid.return_value = "tx123"

        mocked_payment = mocker.patch("deploy.PaymentTxn", return_value=mock_tx)
        mock_tx.sign.return_value = mock_signed

        mocked_wait = mocker.patch("deploy.wait_for_confirmation")
        mocker.patch("builtins.print")  # suppress output

        fund_app(app_id, network)

        mocked_env.assert_called_once_with()
        mocked_client.assert_called_once_with("token", "address")
        mocked_private_key.assert_called_once_with("mnemonic")
        mocked_address.assert_called_once_with(creator_private_key)
        mocked_app_address.assert_called_once_with(app_id)

        mocked_payment.assert_called_once_with(
            sender=sender,
            sp=suggested_params,
            receiver=app_address,
            amt=1_000_000,
        )

        client.send_transactions.assert_called_once_with([mock_signed])
        mocked_wait.assert_called_once_with(client, "tx123")

    def test_deploy_fund_app_functionality(self, mocker):
        app_id = 5059
        network = "testnet"

        env = {
            "algod_token_testnet": "token",
            "algod_address_testnet": "address",
            "creator_testnet_mnemonic": "mnemonic",
        }

        mocked_env = mocker.patch("deploy.environment_variables", return_value=env)

        client = mocker.MagicMock()
        mocked_client = mocker.patch("deploy.AlgodClient", return_value=client)

        creator_private_key = mocker.MagicMock()
        mocked_private_key = mocker.patch(
            "deploy.private_key_from_mnemonic",
            return_value=creator_private_key,
        )

        sender = "sender-address"
        mocked_address = mocker.patch(
            "deploy.address_from_private_key",
            return_value=sender,
        )

        app_address = "app-escrow-address"
        mocked_app_address = mocker.patch(
            "deploy.get_application_address", return_value=app_address
        )

        suggested_params = mocker.MagicMock()
        client.suggested_params.return_value = suggested_params

        mock_tx = mocker.MagicMock()
        mock_signed = mocker.MagicMock()
        mock_signed.transaction.get_txid.return_value = "tx123"

        mocked_payment = mocker.patch("deploy.PaymentTxn", return_value=mock_tx)
        mock_tx.sign.return_value = mock_signed

        mocked_wait = mocker.patch("deploy.wait_for_confirmation")
        mocker.patch("builtins.print")  # suppress output

        fund_app(app_id, network)

        mocked_env.assert_called_once_with()
        mocked_client.assert_called_once_with("token", "address")
        mocked_private_key.assert_called_once_with("mnemonic")
        mocked_address.assert_called_once_with(creator_private_key)
        mocked_app_address.assert_called_once_with(app_id)

        mocked_payment.assert_called_once_with(
            sender=sender,
            sp=suggested_params,
            receiver=app_address,
            amt=1_000_000,
        )

        client.send_transactions.assert_called_once_with([mock_signed])
        mocked_wait.assert_called_once_with(client, "tx123")
