"""Testing module for :py:mod:`foundation` module."""

from collections import defaultdict
from pathlib import Path

import pytest

from config import (
    CURRENT_STAKING_POSITION,
    DAO_DISCUSSIONS_DOCS,
    DOCS_STARTING_POSITION,
    PERMISSION_APP_ID,
    STAKING_DOCS,
)
import foundation
from foundation import (
    _calculate_and_update_votes_and_permissions,
    _initial_check,
    _load_and_merge_accounts,
    _load_and_parse_foundation_data,
    _load_and_parse_staking_data,
    _prepare_data,
    _update_current_staking_for_foundation,
    _update_current_staking_for_non_foundation,
    check_and_update_permission_dapp_boxes,
    prepare_and_write_data,
)


# # HELPERS
class TestFoundationHelpersFunctions:
    """Testing class for :py:mod:`foundation` helpers functions."""

    # # _calculate_and_update_votes_and_permissions
    def test_foundation_calculate_and_update_votes_and_permissions_functionality(
        self, mocker
    ):
        address1, address2, address3, address4, address5 = (
            "address1",
            "address2",
            "address3",
            "address4",
            "address5",
        )
        values1 = [0, 0, 100000, 200000, 300000, 400000, 5000000, 1, 10000000, 2]
        values2 = [
            0,
            0,
            500000,
            600000,
            700000,
            800000,
            15000000,
            3,
            20000000,
            4,
            30000000,
            201,
        ]
        values3 = [0, 0, 900000, 1000000, 1100000, 1200000, 25000000, 5]
        values4 = [0, 0, 1300000, 1400000, 1500000, 1600000, 35000000, 6, 40000000, 202]
        values5 = [0, 0, 1700000, 1800000, 1900000, 200000]
        data = {
            address1: values1,
            address2: values2,
            address3: values3,
            address4: values4,
            address5: values5,
        }
        _calculate_and_update_votes_and_permissions(data)
        assert data == {
            address1: [
                15,
                15600000,
                100000,
                200000,
                300000,
                400000,
                5000000,
                1,
                10000000,
                2,
            ],
            address2: [
                65,
                66400000,
                500000,
                600000,
                700000,
                800000,
                15000000,
                3,
                20000000,
                4,
                30000000,
                201,
            ],
            address3: [25, 27200000, 900000, 1000000, 1100000, 1200000, 25000000, 5],
            address4: [
                75,
                78000000,
                1300000,
                1400000,
                1500000,
                1600000,
                35000000,
                6,
                40000000,
                202,
            ],
            address5: [0, 2000000, 1700000, 1800000, 1900000, 200000],
        }

    # # _initial_check
    def test_foundation_initial_check_raises_for_existing_boxes(self, mocker):
        client = mocker.MagicMock()
        mocked_client = mocker.patch("foundation.AlgodClient", return_value=client)
        boxes = {"boxes": [1, 2, 3, 4]}
        client.application_boxes.return_value = boxes
        algod_token, algod_address = mocker.MagicMock(), mocker.MagicMock()
        env = {"algod_token": algod_token, "algod_address": algod_address}
        mocked_env = mocker.patch("foundation.environment_variables", return_value=env)
        with pytest.raises(ValueError) as exception:
            _initial_check()
            assert str(exception.value) == "Some boxes are already populated!"
        mocked_env.assert_called_once()
        mocked_env.assert_called_with()
        mocked_client.assert_called_once()
        mocked_client.assert_called_with(algod_token, algod_address)
        client.application_boxes.assert_called_once()
        client.application_boxes.assert_called_with(PERMISSION_APP_ID)

    def test_foundation_initial_check_functionality(self, mocker):
        client = mocker.MagicMock()
        mocked_client = mocker.patch("foundation.AlgodClient", return_value=client)
        boxes = {"boxes": []}
        client.application_boxes.return_value = boxes
        algod_token, algod_address = mocker.MagicMock(), mocker.MagicMock()
        env = {"algod_token": algod_token, "algod_address": algod_address}
        mocked_env = mocker.patch("foundation.environment_variables", return_value=env)
        returned = _initial_check()
        assert returned == (env, client)
        mocked_env.assert_called_once()
        mocked_env.assert_called_with()
        mocked_client.assert_called_once()
        mocked_client.assert_called_with(algod_token, algod_address)
        client.application_boxes.assert_called_once()
        client.application_boxes.assert_called_with(PERMISSION_APP_ID)


# # FOUNDATION
class TestFoundationFoundationFunctions:
    """Testing class for :py:mod:`foundation` foundation functions."""

    # # _load_and_merge_accounts
    def test_foundation_load_and_merge_accounts_functionality(self, mocker):
        address1, address2, address3, address4, address5 = (
            "address1",
            "address2",
            "I3LE7Y6XHOXLBTOO26XVCOLQEUUPO4CN5ATOK3BOBVM3PZ52R7I66SACAM",
            "address4",
            "NKWAXEKZCDMBPYLRU3PKVHBAW7AO774HWIXSOCZCCMPAATLYPIK2DL6UHA",
        )
        value1, value2, value3, value4, value5 = 100, 200, 300, 400, 500
        doc_data = {
            address1: value1,
            address2: value2,
            address3: value3,
            address4: value4,
            address5: value5,
        }
        mocked_read = mocker.patch("foundation.read_json", return_value=doc_data)
        doc_id = "doc1"
        returned = _load_and_merge_accounts(doc_id)
        assert returned == {
            address1: value1,
            address2: value2,
            "5L2CUFOR7LYVIV7KOGU6L3TXM3CZVF3P2PRDLPTAGBC2AHDSNMRZX6GKOI": value3,
            address4: value4,
            "ZJEPH66G4C2YLVAOL6NH6ZP3GPCRG3BDZQJ4KCHDN3BD6GZ3YWCHTGOTMA": value5,
        }
        mocked_read.assert_called_once()
        mocked_read.assert_called_with(
            Path(foundation.__file__).resolve().parent
            / "DAO"
            / doc_id
            / "allocations.json"
        )

    def test_foundation_load_and_merge_accounts_for_provided_stem(self, mocker):
        address1, address2, address3 = "address1", "address2", "address3"
        value1, value2, value3 = 100, 200, 300
        doc_data = {address1: value1, address2: value2, address3: value3}
        mocked_read = mocker.patch("foundation.read_json", return_value=doc_data)
        doc_id = "doc1"
        stem = "some_stem"
        returned = _load_and_merge_accounts(doc_id, stem=stem)
        assert returned == {address1: value1, address2: value2, address3: value3}
        mocked_read.assert_called_once()
        mocked_read.assert_called_with(
            Path(foundation.__file__).resolve().parent / "DAO" / doc_id / f"{stem}.json"
        )

    # # _load_and_parse_foundation_data
    def test_foundation_load_and_parse_foundation_data_functionality(self, mocker):
        address1, address2, address3, address4, address5, address6 = (
            "address1",
            "address2",
            "address3",
            "address4",
            "address5",
            "address6",
        )
        data = {
            address1: [0, 1, 2, 3, 0, 0],
            address2: [0, 1, 2, 3, 0, 0],
            address3: [0, 1, 2, 3, 0, 0],
            address4: [0, 1, 2, 3, 0, 0],
            address5: [0, 1, 2, 3, 0, 0],
            address6: [0, 1, 2, 3, 0, 0],
        }
        value1, value2, value3, value4, value5, value6, value7, value8, value9 = (
            100,
            200,
            300,
            400.055210,
            500,
            600,
            700,
            800,
            900,
        )
        doc_data1 = {address1: value1, address3: value2}
        doc_data2 = {address1: value3, address5: value4}
        doc_data3 = {address2: value5}
        doc_data4 = {address4: value6, address5: value6}
        doc_data5 = {address1: value7, address2: value8, address5: value9}
        mocked_load = mocker.patch(
            "foundation._load_and_merge_accounts",
            side_effect=[doc_data1, doc_data2, doc_data3, doc_data4, doc_data5],
        )
        items = ("doc1", "doc2", "doc3", "doc4", "doc5")
        _load_and_parse_foundation_data(data, items)
        assert data == {
            address1: [
                0,
                1,
                2,
                3,
                0,
                0,
                100_000_000,
                1,
                300_000_000,
                2,
                700_000_000,
                5,
            ],
            address2: [0, 1, 2, 3, 0, 0, 500_000_000, 3, 800_000_000, 5],
            address3: [0, 1, 2, 3, 0, 0, 200_000_000, 1],
            address4: [0, 1, 2, 3, 0, 0, 600_000_000, 4],
            address5: [
                0,
                1,
                2,
                3,
                0,
                0,
                400_055_210,
                2,
                600_000_000,
                4,
                900_000_000,
                5,
            ],
            address6: [0, 1, 2, 3, 0, 0],
        }
        calls = [mocker.call(doc_id) for doc_id in items]
        mocked_load.assert_has_calls(calls, any_order=True)
        assert mocked_load.call_count == len(items)

    # # _load_and_parse_staking_data
    def test_foundation_load_and_parse_staking_data_functionality(self, mocker):
        address1, address2, address3, address4, address5, address6 = (
            "address1",
            "address2",
            "address3",
            "address4",
            "address5",
            "address6",
        )
        data = {
            address1: [0, 1, 2, 3, 0, 0],
            address2: [0, 1, 2, 3, 0, 0],
            address3: [0, 1, 2, 3, 0, 0],
            address4: [0, 1, 2, 3, 0, 0],
            address5: [0, 1, 2, 3, 0, 0],
            address6: [0, 1, 2, 3, 0, 0],
        }
        value1, value2, value3, value4, value5, value6 = (
            100.0,
            200,
            300,
            400,
            500,
            600.0,
        )
        doc_data1 = {address1: [value1], address3: [value2]}
        doc_data2 = {address1: [value3], address5: [value4]}
        doc_data3 = {address2: [value5]}
        doc_data4 = {address4: [value6], address5: [value6]}
        mocked_load = mocker.patch(
            "foundation._load_and_merge_accounts",
            side_effect=[doc_data1, doc_data2, doc_data3, doc_data4],
        )
        items = ("doc1", "doc2")
        _load_and_parse_staking_data(data, items)
        assert data == {
            address1: [
                0,
                1,
                2,
                3,
                0,
                0,
                100_000_000,
                201,
                300_000_000,
                201,
            ],
            address2: [0, 1, 2, 3, 0, 0, 500_000_000, 202],
            address3: [0, 1, 2, 3, 0, 0, 200_000_000, 201],
            address4: [0, 1, 2, 3, 0, 0, 600_000_000, 202],
            address5: [
                0,
                1,
                2,
                3,
                0,
                0,
                400_000_000,
                201,
                600_000_000,
                202,
            ],
            address6: [0, 1, 2, 3, 0, 0],
        }
        calls = [
            mocker.call("doc1", stem="dao_governors"),
            mocker.call("doc1", stem="dao_ongoing_governors"),
            mocker.call("doc2", stem="dao_governors"),
            mocker.call("doc2", stem="dao_ongoing_governors"),
        ]
        mocked_load.assert_has_calls(calls, any_order=True)
        assert mocked_load.call_count == len(items) * 2

    # # _prepare_data
    def test_foundation_prepare_data_functionality(self, mocker):
        client = mocker.MagicMock()
        mocked_foundation = mocker.patch("foundation._load_and_parse_foundation_data")
        mocked_staking = mocker.patch("foundation._load_and_parse_staking_data")
        mocked_client = mocker.patch("foundation.AlgodClient", return_value=client)
        mocked_staking_foundation = mocker.patch(
            "foundation._update_current_staking_for_foundation"
        )
        mocked_staking_non_foundation = mocker.patch(
            "foundation._update_current_staking_for_non_foundation"
        )
        mocked_calculate = mocker.patch(
            "foundation._calculate_and_update_votes_and_permissions"
        )
        data = defaultdict(lambda: [0] * DOCS_STARTING_POSITION)
        algod_token, algod_address = mocker.MagicMock(), mocker.MagicMock()
        env = {"algod_token": algod_token, "algod_address": algod_address}
        returned = _prepare_data(env)
        assert returned == data
        mocked_foundation.assert_called_once()
        mocked_foundation.assert_called_with(data, items=DAO_DISCUSSIONS_DOCS)
        mocked_staking.assert_called_once()
        mocked_staking.assert_called_with(data, items=STAKING_DOCS)
        mocked_client.assert_called_once()
        mocked_client.assert_called_with(algod_token, algod_address)
        mocked_staking_foundation.assert_called_once()
        mocked_staking_foundation.assert_called_with(
            client, data, starting_position=CURRENT_STAKING_POSITION
        )
        mocked_staking_non_foundation.assert_called_once()
        mocked_staking_non_foundation.assert_called_with(
            client, data, starting_position=CURRENT_STAKING_POSITION
        )
        mocked_calculate.assert_called_once()
        mocked_calculate.assert_called_with(data)

    # # prepare_and_write_data
    def test_foundation_prepare_and_write_data_functionality(self, mocker):
        env, client = mocker.MagicMock(), mocker.MagicMock()
        mocked_initial = mocker.patch(
            "foundation._initial_check", return_value=[env, client]
        )
        mocked_data = mocker.patch("foundation._prepare_data")
        mocked_parameters = mocker.patch("foundation.box_writing_parameters")
        mocked_write = mocker.patch("foundation.write_foundation_boxes")
        prepare_and_write_data()
        mocked_initial.assert_called_once()
        mocked_initial.assert_called_with()
        mocked_data.assert_called_once()
        mocked_data.assert_called_with(env)
        mocked_parameters.assert_called_once()
        mocked_parameters.assert_called_with(env)
        mocked_write.assert_called_once()
        mocked_write.assert_called_with(
            client,
            PERMISSION_APP_ID,
            mocked_parameters.return_value,
            mocked_data.return_value,
        )


# # STAKING
class TestFoundationStakingFunctions:
    """Testing class for :py:mod:`foundation` staking functions."""

    # # _update_current_staking_for_foundation
    def test_foundation_update_current_staking_for_foundation_functionality(
        self, mocker
    ):
        client = mocker.MagicMock()
        starting_position = 4
        mocked_staking = mocker.patch(
            "foundation.current_governance_staking_for_address",
            side_effect=[50000, 0, 100000],
        )
        mocked_permission = mocker.patch(
            "foundation.permission_for_amount", side_effect=[2000, 3000]
        )
        address1, address2, address3 = "address1", "address2", "address3"
        data = {
            address1: [0, 1, 2, 3, 0, 0],
            address2: [0, 1, 2, 3, 1, 1],
            address3: [0, 1, 2, 3, 0, 0],
        }
        _update_current_staking_for_foundation(client, data, starting_position)
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

    # # _update_current_staking_for_non_foundation
    def test_foundation_update_current_staking_for_non_foundation_functionality(
        self, mocker
    ):
        client = mocker.MagicMock()
        starting_position = 4
        address1, address2, address3, address4, address5, address6, address7 = (
            "address1",
            "address2",
            "address3",
            "address4",
            "address5",
            "address6",
            "address7",
        )
        mocked_addresses = mocker.patch(
            "foundation.governance_staking_addresses",
            return_value=[address1, address3, address4, address5, address6, address7],
        )
        mocked_staking = mocker.patch(
            "foundation.current_governance_staking_for_address",
            side_effect=[100000, 0, 20000, 0],
        )
        mocked_permission = mocker.patch(
            "foundation.permission_for_amount", side_effect=[5000, 0]
        )
        data = defaultdict(lambda: [0] * DOCS_STARTING_POSITION)
        data[address1] = [0, 1, 2, 3, 0, 0]
        data[address2] = [0, 1, 2, 3, 0, 0]
        data[address3] = [0, 1, 2, 3, 0, 0]
        _update_current_staking_for_non_foundation(client, data, starting_position)
        mocked_addresses.assert_called_once()
        mocked_addresses.assert_called_with()
        assert data == {
            address1: [0, 1, 2, 3, 0, 0],
            address2: [0, 1, 2, 3, 0, 0],
            address3: [0, 1, 2, 3, 0, 0],
            address4: [0, 0, 0, 0, 100000, 5000],
        }
        calls = [
            mocker.call(client, address4),
            mocker.call(client, address5),
            mocker.call(client, address6),
            mocker.call(client, address7),
        ]
        mocked_staking.assert_has_calls(calls, any_order=True)
        assert mocked_staking.call_count == 4
        calls = [mocker.call(100000), mocker.call(20000)]
        mocked_permission.assert_has_calls(calls, any_order=True)
        assert mocked_permission.call_count == 2


# # UPDATE
class TestFoundationUpdateFunctions:
    """Testing class for :py:mod:`foundation` update functions."""

    # # check_and_update_permission_dapp_boxes
    def test_foundation_check_and_update_permission_dapp_boxes_functionality(
        self, mocker
    ):
        algod_token, algod_address = mocker.MagicMock(), mocker.MagicMock()
        algod_token_mainnet, algod_address_mainnet = (
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        env = {
            "algod_token": algod_token,
            "algod_address": algod_address,
            "algod_token_mainnet": algod_token_mainnet,
            "algod_address_mainnet": algod_address_mainnet,
        }
        mocked_env = mocker.patch("foundation.environment_variables", return_value=env)
        client, mainnet_client = mocker.MagicMock(), mocker.MagicMock()
        mocked_client = mocker.patch(
            "foundation.AlgodClient", side_effect=[client, mainnet_client]
        )
        writing_parameters = mocker.MagicMock()
        mocked_parameters = mocker.patch(
            "foundation.box_writing_parameters", return_value=writing_parameters
        )
        mocked_subscriptions = mocker.patch("foundation.fetch_subscriptions_from_boxes")
        address1, address2, address3 = "address1", "address2", "address3"
        mocked_governance = mocker.patch(
            "foundation.governance_staking_addresses",
            return_value=[address1, address2, address3],
        )
        staking1, staking2, staking3 = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        mocked_staking = mocker.patch(
            "foundation.current_governance_staking_for_address",
            side_effect=[staking1, staking2, staking3],
        )
        mocked_permissions = mocker.patch(
            "foundation.permission_dapp_values_from_boxes"
        )
        mocked_check_subscribers = mocker.patch(
            "foundation.check_and_update_new_subscribers"
        )
        mocked_check_stakers = mocker.patch("foundation.check_and_update_new_stakers")
        mocked_check_changed = mocker.patch(
            "foundation.check_and_update_changed_subscriptions_and_staking"
        )
        check_and_update_permission_dapp_boxes()
        mocked_env.assert_called_once()
        mocked_env.assert_called_with()
        calls = [
            mocker.call(algod_token, algod_address),
            mocker.call(algod_token_mainnet, algod_address_mainnet),
        ]
        mocked_client.assert_has_calls(calls, any_order=True)
        assert mocked_client.call_count == 2
        mocked_parameters.assert_called_once()
        mocked_parameters.assert_called_with(env)
        mocked_subscriptions.assert_called_once()
        mocked_subscriptions.assert_called_with(client)
        mocked_governance.assert_called_once()
        mocked_governance.assert_called_with()
        calls = [
            mocker.call(mainnet_client, address1),
            mocker.call(mainnet_client, address2),
            mocker.call(mainnet_client, address3),
        ]
        mocked_staking.assert_has_calls(calls, any_order=True)
        assert mocked_staking.call_count == 3
        mocked_permissions.assert_called_once()
        mocked_permissions.assert_called_with(client, PERMISSION_APP_ID)
        mocked_check_subscribers.assert_called_once()
        mocked_check_subscribers.assert_called_with(
            client,
            PERMISSION_APP_ID,
            writing_parameters,
            mocked_permissions.return_value,
            mocked_subscriptions.return_value,
        )
        mocked_check_stakers.assert_called_once()
        mocked_check_stakers.assert_called_with(
            client,
            PERMISSION_APP_ID,
            writing_parameters,
            mocked_permissions.return_value,
            {address1: staking1, address2: staking2, address3: staking3},
        )
        mocked_check_changed.assert_called_once()
        mocked_check_changed.assert_called_with(
            client,
            PERMISSION_APP_ID,
            writing_parameters,
            mocked_permissions.return_value,
            mocked_subscriptions.return_value,
            {address1: staking1, address2: staking2, address3: staking3},
        )
