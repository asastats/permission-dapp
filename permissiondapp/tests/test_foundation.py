"""Testing module for :py:mod:`foundation` module."""

from collections import defaultdict

from config import (
    CURRENT_STAKING_STARTING_POSITION,
    DAO_DISCUSSIONS_DOCS,
    DOCS_STARTING_POSITION,
    STAKING_DOCS,
)
from foundation import _prepare_data, _update_current_staking, prepare_and_write_data


# # VALUES
class TestFoundationFunctions:
    """Testing class for :py:mod:`foundation` functions."""

    # # _prepare_data
    def test_foundation_prepare_data_functionality(self, mocker):
        client = mocker.MagicMock()
        mocked_foundation = mocker.patch("foundation._load_and_parse_foundation_data")
        mocked_staking = mocker.patch("foundation._load_and_parse_staking_data")
        mocked_update = mocker.patch("foundation._update_current_staking")
        mocked_calculate = mocker.patch(
            "foundation._calculate_and_update_votes_and_permissions"
        )
        data = defaultdict(lambda: [0] * DOCS_STARTING_POSITION)
        returned = _prepare_data(client)
        assert returned == data
        mocked_foundation.assert_called_once()
        mocked_foundation.assert_called_with(data, items=DAO_DISCUSSIONS_DOCS)
        mocked_staking.assert_called_once()
        mocked_staking.assert_called_with(data, items=STAKING_DOCS)
        mocked_update.assert_called_once()
        mocked_update.assert_called_with(
            client, data, starting_position=CURRENT_STAKING_STARTING_POSITION
        )
        mocked_calculate.assert_called_once()
        mocked_calculate.assert_called_with(data)

    # # _update_current_staking
    def test_foundation_update_current_staking_functionality(self, mocker):
        client = mocker.MagicMock()
        starting_position = 4
        mocked_staking = mocker.patch(
            "foundation.current_staking", side_effect=[50000, 0, 100000]
        )
        mocked_permission = mocker.patch(
            "foundation.permission_for_amount", side_effect=[2000, 3000]
        )
        address1, address2, address3 = "address1", "address2", "address3"
        data = {
            address1: [0, 1, 2, 3, 0, 0],
            address2: [0, 1, 2, 3, 0, 0],
            address3: [0, 1, 2, 3, 0, 0],
        }
        _update_current_staking(client, data, starting_position)
        assert data == {
            address1: [0, 1, 2, 3, 50000, 2000],
            address2: [0, 1, 2, 3, 0, 0],
            address3: [0, 1, 2, 3, 100000, 3000],
        }
        calls = [
            mocker.call(client, address1),
            mocker.call(client, address2),
            mocker.call(client, address3),
        ]
        mocked_staking.assert_has_calls(calls, any_order=True)
        assert mocked_staking.call_count == 3
        calls = [mocker.call(50000), mocker.call(100000)]
        mocked_permission.assert_has_calls(calls, any_order=True)
        assert mocked_permission.call_count == 2

    # # prepare_and_write_data
    def test_foundation_prepare_and_write_data_functionality(self, mocker):
        client = mocker.MagicMock()
        creator_mnemonic = mocker.MagicMock()
        permission_app_id = 5050
        env = {
            "creator_mnemonic": creator_mnemonic,
            "permission_app_id": permission_app_id,
        }
        mocked_initial = mocker.patch(
            "foundation._initial_check", return_value=[env, client]
        )
        mocked_data = mocker.patch("foundation._prepare_data")
        mocked_private_key = mocker.patch("foundation.private_key_from_mnemonic")
        mocked_contract = mocker.patch("foundation.load_contract")
        mocked_write = mocker.patch("foundation.write_foundation_boxes")
        prepare_and_write_data()
        mocked_initial.assert_called_once()
        mocked_initial.assert_called_with()
        mocked_data.assert_called_once()
        mocked_data.assert_called_with(client)
        mocked_private_key.assert_called_once()
        mocked_private_key.assert_called_with(creator_mnemonic)
        mocked_contract.assert_called_once()
        mocked_contract.assert_called_with()
        mocked_write.assert_called_once()
        mocked_write.assert_called_with(
            client,
            mocked_private_key.return_value,
            permission_app_id,
            mocked_contract.return_value,
            mocked_data.return_value,
        )
