"""Testing module for :py:mod:`utils` module."""

from utils import check_test_box, delete_boxes, print_box_values


class TestUtilsFunctions:
    """Testing class for :py:mod:`utils` functions."""

    # # delete_boxes
    def test_utils_delete_boxes_functionality(self, mocker):
        env = {
            "algod_token_testnet": "test_token",
            "algod_address_testnet": "test_address",
        }
        mocked_env = mocker.patch("utils.environment_variables", return_value=env)
        app_id = 5050
        mocked_permission_id = mocker.patch(
            "utils.permission_dapp_id", return_value=app_id
        )
        client = mocker.MagicMock()
        mocked_client = mocker.patch("utils.AlgodClient", return_value=client)
        writing_params = mocker.MagicMock()
        mocked_writing_params = mocker.patch(
            "utils.box_writing_parameters", return_value=writing_params
        )
        boxes_data = {
            "boxes": [
                {"name": "dGVzdF9hZGRyZXNzXzAx"},
                {"name": "dGVzdF9hZGRyZXNzXzAy"},
            ]
        }
        client.application_boxes.return_value = boxes_data
        mocked_encode = mocker.patch("utils.encode_address")
        mocked_encode.side_effect = [
            "test_address_01_encoded",
            "test_address_02_encoded",
        ]
        mocked_delete = mocker.patch("utils.delete_box")
        mocker.patch("builtins.print")  # suppress output
        delete_boxes()
        mocked_env.assert_called_once_with()
        mocked_permission_id.assert_called_once_with(network="testnet")
        mocked_client.assert_called_once_with("test_token", "test_address")
        mocked_writing_params.assert_called_once_with(env)
        client.application_boxes.assert_called_once_with(app_id)
        assert mocked_encode.call_count == 2
        mocked_encode.assert_any_call(b"test_address_01")
        mocked_encode.assert_any_call(b"test_address_02")
        assert mocked_delete.call_count == 2
        mocked_delete.assert_any_call(
            client, app_id, writing_params, "test_address_01_encoded"
        )
        mocked_delete.assert_any_call(
            client, app_id, writing_params, "test_address_02_encoded"
        )

    def test_utils_delete_boxes_with_no_boxes(self, mocker):
        env = {
            "algod_token_testnet": "test_token",
            "algod_address_testnet": "test_address",
        }
        mocked_env = mocker.patch("utils.environment_variables", return_value=env)
        app_id = 5050
        mocked_permission_id = mocker.patch(
            "utils.permission_dapp_id", return_value=app_id
        )
        client = mocker.MagicMock()
        mocked_client = mocker.patch("utils.AlgodClient", return_value=client)
        writing_params = mocker.MagicMock()
        mocked_writing_params = mocker.patch(
            "utils.box_writing_parameters", return_value=writing_params
        )
        boxes_data = {"boxes": []}
        client.application_boxes.return_value = boxes_data
        mocked_encode = mocker.patch("utils.encode_address")
        mocked_delete = mocker.patch("utils.delete_box")
        mocker.patch("builtins.print")  # suppress output
        delete_boxes()
        mocked_env.assert_called_once_with()
        mocked_permission_id.assert_called_once_with(network="testnet")
        mocked_client.assert_called_once_with("test_token", "test_address")
        mocked_writing_params.assert_called_once_with(env)
        client.application_boxes.assert_called_once_with(app_id)
        mocked_encode.assert_not_called()
        mocked_delete.assert_not_called()

    # # print_box_values
    def test_utils_print_box_values_for_provided_network(self, mocker):
        network = "mainnet"
        env = {
            "algod_token_mainnet": "mainnet_token",
            "algod_address_mainnet": "mainnet_address",
        }
        mocked_env = mocker.patch("utils.environment_variables", return_value=env)
        client = mocker.MagicMock()
        mocked_client = mocker.patch("utils.AlgodClient", return_value=client)
        app_id = 5050
        mocked_permission_id = mocker.patch(
            "utils.permission_dapp_id", return_value=app_id
        )
        permissions = {
            "addr1": (True, 1000),
            "addr2": (False, 500),
            "addr3": (True, 1500),
        }
        mocked_permissions = mocker.patch(
            "utils.permission_dapp_values_from_boxes", return_value=permissions
        )
        mocker.patch("builtins.print")  # suppress output
        print_box_values(network=network)
        mocked_env.assert_called_once_with()
        mocked_client.assert_called_once_with("mainnet_token", "mainnet_address")
        mocked_permission_id.assert_called_once_with(network=network)
        mocked_permissions.assert_called_once_with(client, app_id)

    def test_utils_print_box_values_with_no_boxes(self, mocker):
        env = {
            "algod_token_testnet": "test_token",
            "algod_address_testnet": "test_address",
        }
        mocked_env = mocker.patch("utils.environment_variables", return_value=env)
        client = mocker.MagicMock()
        mocked_client = mocker.patch("utils.AlgodClient", return_value=client)
        app_id = 5050
        mocked_permission_id = mocker.patch(
            "utils.permission_dapp_id", return_value=app_id
        )
        mocked_permissions = mocker.patch(
            "utils.permission_dapp_values_from_boxes", return_value={}
        )
        mocked_print = mocker.patch("builtins.print")
        print_box_values()
        mocked_env.assert_called_once_with()
        mocked_client.assert_called_once_with("test_token", "test_address")
        mocked_permission_id.assert_called_once_with(network="testnet")
        mocked_permissions.assert_called_once_with(client, app_id)
        mocked_print.assert_any_call("There are no boxes!")

    def test_utils_print_box_values_functionality(self, mocker):
        env = {
            "algod_token_testnet": "test_token",
            "algod_address_testnet": "test_address",
        }
        mocked_env = mocker.patch("utils.environment_variables", return_value=env)
        client = mocker.MagicMock()
        mocked_client = mocker.patch("utils.AlgodClient", return_value=client)
        app_id = 5050
        mocked_permission_id = mocker.patch(
            "utils.permission_dapp_id", return_value=app_id
        )
        permissions = {
            "addr1": (True, 1000),
            "addr2": (False, 500),
            "addr3": (True, 1500),
        }
        mocked_permissions = mocker.patch(
            "utils.permission_dapp_values_from_boxes", return_value=permissions
        )
        mocked_print = mocker.patch("builtins.print")
        print_box_values()
        mocked_env.assert_called_once_with()
        mocked_client.assert_called_once_with("test_token", "test_address")
        mocked_permission_id.assert_called_once_with(network="testnet")
        mocked_permissions.assert_called_once_with(client, app_id)
        mocked_print.assert_called_once_with(
            [("addr3", (True, 1500)), ("addr1", (True, 1000)), ("addr2", (False, 500))]
        )

    # # check_test_box
    def test_utils_check_test_box_functionality(self, mocker):
        app_id_str = "5050"
        app_id = 5050
        env = {
            "algod_token_testnet": "test_token",
            "algod_address_testnet": "test_address",
        }
        mocked_env = mocker.patch("utils.environment_variables", return_value=env)
        client = mocker.MagicMock()
        mocked_client = mocker.patch("utils.AlgodClient", return_value=client)
        boxes_data = {
            "boxes": [
                {"name": "dGVzdF9hZGRyZXNzXzAx"},
                {"name": "dGVzdF9hZGRyZXNzXzAy"},
            ]
        }
        client.application_boxes.return_value = boxes_data
        mocked_encode = mocker.patch("utils.encode_address")
        mocked_encode.side_effect = [
            "test_address_01",
            "test_address_02",
        ]
        # Create proper mock responses - 80 character hex strings (from 40 bytes)
        mock_hex_value = "0" * 80  # 80 zeros from 40 bytes of data

        # Mock the base64.b64decode().hex() chain to return the proper length
        mock_binary_data = mocker.MagicMock()
        mock_binary_data.hex.return_value = mock_hex_value

        mocked_b64decode = mocker.patch("utils.base64.b64decode")
        # Set up side effect for box names and box values
        mocked_b64decode.side_effect = [
            b"test_address_01",  # first box name decode
            mock_binary_data,  # first box value decode
            b"test_address_02",  # second box name decode
            mock_binary_data,  # second box value decode
        ]
        mocked_print = mocker.patch("builtins.print")
        check_test_box(app_id_str)
        mocked_env.assert_called_once_with()
        mocked_client.assert_called_once_with("test_token", "test_address")
        client.application_boxes.assert_called_once_with(app_id)
        assert mocked_encode.call_count == 2
        mocked_encode.assert_any_call(b"test_address_01")
        mocked_encode.assert_any_call(b"test_address_02")
        # Verify print was called for each address and the values
        assert (
            mocked_print.call_count >= 4
        )  # address + multiple value lines for each box

    def test_utils_check_test_box_with_assertion_error(self, mocker):
        app_id_str = "5050"
        app_id = 5050
        env = {
            "algod_token_testnet": "test_token",
            "algod_address_testnet": "test_address",
        }
        mocked_env = mocker.patch("utils.environment_variables", return_value=env)
        client = mocker.MagicMock()
        mocked_client = mocker.patch("utils.AlgodClient", return_value=client)
        boxes_data = {
            "boxes": [
                {"name": "dGVzdF9hZGRyZXNz"},
            ]
        }
        client.application_boxes.return_value = boxes_data
        mocker.patch("utils.encode_address", return_value="test_address")
        response_data = {"value": "dGVzdA=="}  # base64 for "test" (4 bytes)
        client.application_box_by_name.return_value = response_data
        mocked_b64decode = mocker.patch("utils.base64.b64decode")
        mocked_b64decode.side_effect = [
            b"test_address",
            b"test",  # only 4 bytes, should trigger assertion error
        ]
        mocker.patch("builtins.print")  # suppress output
        try:
            check_test_box(app_id_str)
            assert False, "Expected assertion error"
        except AssertionError as e:
            assert str(e) == "74657374"  # hex of "test"
        mocked_env.assert_called_once_with()
        mocked_client.assert_called_once_with("test_token", "test_address")
        client.application_boxes.assert_called_once_with(app_id)
