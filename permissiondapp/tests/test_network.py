"""Testing module for :py:mod:`network` module."""

from algosdk.error import AlgodHTTPError

from config import STAKING_KEY
from network import (
    _cometa_app_amount,
    _cometa_app_local_state_for_address,
    current_staking,
    delete_box,
    write_box,
    write_foundation_boxes,
)


# # VALUES
class TestNetworkFunctions:
    """Testing class for :py:mod:`network` functions."""

    # # _cometa_app_amount
    def test_network_cometa_app_amount_returns_amount_for_staking_app(self):
        state = {
            "id": 2333078684,
            "key-value": [
                {
                    "key": "AA==",
                    "value": {
                        "bytes": "AQAAAAAL68IAAQAAAAAAACMnAQAAAAABYspUAQAAAAAAAAAAAAAAAAAAAAAAAAAAABXBdBEic6PeGeRg",
                        "type": 1,
                        "uint": 0,
                    },
                }
            ],
            "opted-in-at-round": 23251531,
            "schema": {"num-byte-slice": 1, "num-uint": 0},
        }
        returned = _cometa_app_amount(STAKING_KEY, state)
        assert returned == 200000000

    def test_network_cometa_app_amount_returns_zero_when_is_not_cometa_app(self):
        state = {
            "id": 2333078684,
            "key-value": [
                {
                    "key": "VXNlcl9DbGFpbWFibGU=",
                    "value": {"bytes": "", "type": 1, "uint": 0},
                },
                {
                    "key": "VXNlcl9SYXRpbw==",
                    "value": {"bytes": "LaXetdr3fITQuNzj", "type": 1, "uint": 0},
                },
            ],
            "schema": {"num-byte-slice": 8, "num-uint": 8},
        }
        returned = _cometa_app_amount(STAKING_KEY, state)
        assert returned == 0

    def test_network_cometa_app_amount_returns_zero_for_too_small_bytes_value(self):
        state = {
            "id": 2333078684,
            "key-value": [
                {
                    "key": "Y29tbWl0bWVudA==",
                    "value": {"bytes": "", "type": 2, "uint": 1850000},
                },
                {
                    "key": "Y29tbWl0bWVudF9jbGFpbWVk",
                    "value": {"bytes": "", "type": 2, "uint": 0},
                },
                {
                    "key": "cHJlbWludA==",
                    "value": {"bytes": "", "type": 2, "uint": 1850000},
                },
            ],
            "schema": {"num-byte-slice": 0, "num-uint": 3},
        }
        state["key-value"][0]["value"]["bytes"] = "AAAVfSUw=="
        returned = _cometa_app_amount(STAKING_KEY, state)
        assert returned == 0

    # # _cometa_app_local_state_for_address
    def test_network_cometa_app_local_state_for_address_for_error(self, mocker):
        client = mocker.MagicMock()
        client.account_info.side_effect = AlgodHTTPError("")
        address = "address"
        returned = _cometa_app_local_state_for_address(client, address)
        assert returned is None
        client.account_info.assert_called_once()
        client.account_info.assert_called_with(address)

    def test_network_cometa_app_local_state_functionality(self, mocker):
        client = mocker.MagicMock()
        state1 = {
            "id": 505,
            "key-value": [
                {
                    "key": "Y29tbWl0bWVudA==",
                    "value": {"bytes": "", "type": 2, "uint": 1850000},
                }
            ],
            "schema": {"num-byte-slice": 0, "num-uint": 3},
        }
        state2 = {
            "id": 2333078684,
            "key-value": [
                {
                    "key": "Y29tbWl0bWVudA==",
                    "value": {"bytes": "", "type": 2, "uint": 1850000},
                },
                {
                    "key": "Y29tbWl0bWVudF9jbGFpbWVk",
                    "value": {"bytes": "", "type": 2, "uint": 0},
                },
                {
                    "key": "cHJlbWludA==",
                    "value": {"bytes": "", "type": 2, "uint": 1850000},
                },
            ],
            "schema": {"num-byte-slice": 0, "num-uint": 3},
        }
        state3 = {
            "id": 506,
            "schema": {"num-byte-slice": 0, "num-uint": 3},
        }
        account_info = {"apps-local-state": [state1, state2, state3]}
        client.account_info.return_value = account_info
        address = "address"
        returned = _cometa_app_local_state_for_address(client, address)
        assert returned == state2
        client.account_info.assert_called_once()
        client.account_info.assert_called_with(address)

    # # current_staking
    def test_network_current_staking_for_no_state(self, mocker):
        client, address = mocker.MagicMock(), mocker.MagicMock()
        mocked_state = mocker.patch(
            "network._cometa_app_local_state_for_address", return_value=None
        )
        mocked_amount = mocker.patch("network._cometa_app_amount")
        returned = current_staking(client, address)
        assert returned == 0
        mocked_state.assert_called_once()
        mocked_state.assert_called_with(client, address)
        mocked_amount.assert_not_called()

    def test_network_current_staking_functionality(self, mocker):
        client, address = mocker.MagicMock(), mocker.MagicMock()
        state = mocker.MagicMock()
        mocked_state = mocker.patch(
            "network._cometa_app_local_state_for_address", return_value=state
        )
        mocked_amount = mocker.patch("network._cometa_app_amount")
        returned = current_staking(client, address)
        assert returned == mocked_amount.return_value
        mocked_state.assert_called_once()
        mocked_state.assert_called_with(client, address)
        mocked_amount.assert_called_once()
        mocked_amount.assert_called_with(STAKING_KEY, state)

    # # delete_box
    def test_network_delete_box_functionality(self, mocker):
        client, sender, signer, app_id, contract = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        address = "2EVGZ4BGOSL3J64UYDE2BUGTNTBZZZLI54VUQQNZZLYCDODLY33UGXNSIU"
        box_name = "0Sps8CZ0l7T7lMDJoNDTbMOc5WjvK0hBucrwIbhrxvc="
        atc = mocker.MagicMock()
        mocked_composer = mocker.patch(
            "network.AtomicTransactionComposer", return_value=atc
        )
        method = mocker.MagicMock()
        contract.get_method_by_name.return_value = method
        delete_box(client, sender, signer, app_id, contract, address)
        mocked_composer.assert_called_once()
        mocked_composer.assert_called_with()
        client.suggested_params.assert_called_once()
        client.suggested_params.assert_called_with()
        contract.get_method_by_name.assert_called_once()
        contract.get_method_by_name.assert_called_with("deleteBox")
        atc.add_method_call.assert_called_once()
        atc.add_method_call.assert_called_with(
            app_id=app_id,
            method=contract.get_method_by_name.return_value,
            sender=sender,
            sp=client.suggested_params.return_value,
            signer=signer,
            method_args=[box_name],
            boxes=[(app_id, box_name.encode())],
        )
        atc.execute.assert_called_once()
        atc.execute.assert_called_with(client, 2)

    # # write_box
    def test_network_write_box_functionality(self, mocker):
        client, sender, signer, app_id, contract, value = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        address = "2EVGZ4BGOSL3J64UYDE2BUGTNTBZZZLI54VUQQNZZLYCDODLY33UGXNSIU"
        box_name = "0Sps8CZ0l7T7lMDJoNDTbMOc5WjvK0hBucrwIbhrxvc="
        atc = mocker.MagicMock()
        mocked_composer = mocker.patch(
            "network.AtomicTransactionComposer", return_value=atc
        )
        method = mocker.MagicMock()
        contract.get_method_by_name.return_value = method
        write_box(client, sender, signer, app_id, contract, address, value)
        mocked_composer.assert_called_once()
        mocked_composer.assert_called_with()
        client.suggested_params.assert_called_once()
        client.suggested_params.assert_called_with()
        contract.get_method_by_name.assert_called_once()
        contract.get_method_by_name.assert_called_with("writeBox")
        atc.add_method_call.assert_called_once()
        atc.add_method_call.assert_called_with(
            app_id=app_id,
            method=contract.get_method_by_name.return_value,
            sender=sender,
            sp=client.suggested_params.return_value,
            signer=signer,
            method_args=[box_name, value],
            boxes=[(app_id, box_name.encode())],
        )
        atc.execute.assert_called_once()
        atc.execute.assert_called_with(client, 2)

    # # write_foundation_boxes
    def test_network_write_foundation_boxes_functionality(self, mocker):
        client, creator_private_key, app_id, contract = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        sender, signer = mocker.MagicMock(), mocker.MagicMock()
        mocked_sender = mocker.patch(
            "network.address_from_private_key", return_value=sender
        )
        mocked_signer = mocker.patch(
            "network.AccountTransactionSigner", return_value=signer
        )
        value1, value2, value3 = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        mocked_serialize = mocker.patch(
            "network.serialize_values", side_effect=[value1, value2, value3]
        )
        mocked_write = mocker.patch("network.write_box")
        address1, address2, address3 = "address1", "address2", "address3"
        values1, values2, values3 = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        data = {address1: values1, address2: values2, address3: values3}
        write_foundation_boxes(client, creator_private_key, app_id, contract, data)
        mocked_sender.assert_called_once()
        mocked_sender.assert_called_with(creator_private_key)
        mocked_signer.assert_called_once()
        mocked_signer.assert_called_with(creator_private_key)
        calls = [mocker.call(values1), mocker.call(values2), mocker.call(values3)]
        mocked_serialize.assert_has_calls(calls, any_order=True)
        assert mocked_serialize.call_count == 3
        calls = [
            mocker.call(client, sender, signer, app_id, contract, address1, value1),
            mocker.call(client, sender, signer, app_id, contract, address2, value2),
            mocker.call(client, sender, signer, app_id, contract, address3, value3),
        ]
        mocked_write.assert_has_calls(calls, any_order=True)
        assert mocked_write.call_count == 3
