"""Testing module for :py:mod:`deploy` module."""

from pathlib import Path
from unittest import mock

import permissiondapp.deploy
from permissiondapp.deploy import deploy_app


# # VALUES
class TestDeployFunctions:
    """Testing class for :py:mod:`deploy` functions."""

    # # deploy_app
    def test_deploy_deploy_app_functionality(self, mocker):
        algod_token, algod_address, creator_mnemonic = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        env = {
            "algod_token": algod_token,
            "algod_address": algod_address,
            "creator_mnemonic": creator_mnemonic,
        }
        mocked_env = mocker.patch(
            "permissiondapp.deploy.environment_variables", return_value=env
        )
        client = mocker.MagicMock()
        mocked_client = mocker.patch(
            "permissiondapp.deploy.AlgodClient", return_value=client
        )
        creator_private_key = mocker.MagicMock()
        mocked_private_key = mocker.patch(
            "permissiondapp.deploy.private_key_from_mnemonic",
            return_value=creator_private_key,
        )
        approval_program, clear_program = mocker.MagicMock(), mocker.MagicMock()
        mocked_compile = mocker.patch(
            "permissiondapp.deploy.compile_program",
            side_effect=[approval_program, clear_program],
        )
        app_id = 5050
        mocked_create = mocker.patch(
            "permissiondapp.deploy.create_app", return_value=app_id
        )
        approval_source, clear_source = mocker.MagicMock(), mocker.MagicMock()
        with mock.patch(
            "permissiondapp.deploy.open", side_effect=[approval_source, clear_source]
        ) as mocked_open:
            returned = deploy_app()
            assert returned == app_id
            calls = [
                mocker.call(
                    Path(permissiondapp.deploy.__file__).resolve().parent
                    / "artifacts"
                    / "approval.teal"
                ),
                mocker.call(
                    Path(permissiondapp.deploy.__file__).resolve().parent
                    / "artifacts"
                    / "clear.teal"
                ),
            ]
            mocked_open.assert_has_calls(calls, any_order=True)
            assert mocked_open.call_count == 2
            approval_source.read.assert_called_once()
            approval_source.read.assert_called_with()
            approval_source.read.return_value.encode.assert_called_once()
            approval_source.read.return_value.encode.assert_called_with()
            clear_source.read.assert_called_once()
            clear_source.read.assert_called_with()
            clear_source.read.return_value.encode.assert_called_once()
            clear_source.read.return_value.encode.assert_called_with()
        mocked_env.assert_called_once()
        mocked_env.assert_called_with()
        mocked_client.assert_called_once()
        mocked_client.assert_called_with(algod_token, algod_address)
        mocked_private_key.assert_called_once()
        mocked_private_key.assert_called_with(creator_mnemonic)
        calls = [
            mocker.call(client, approval_source.read.return_value.encode.return_value),
            mocker.call(client, clear_source.read.return_value.encode.return_value),
        ]
        mocked_compile.assert_has_calls(calls, any_order=True)
        assert mocked_compile.call_count == 2
        mocked_create.assert_called_once()
        mocked_create.assert_called_with(
            client, creator_private_key, approval_program, clear_program
        )
