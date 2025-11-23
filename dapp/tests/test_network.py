"""Testing module for :py:mod:`network` module."""

import base64
from unittest import mock

import pytest
from algosdk.error import AlgodHTTPError

from config import (
    STAKING_KEY,
    SUBSCRIPTION_PERMISSIONS,
    SUBTOPIA_ASASTATSER_APP_ID,
    SUBTOPIA_CLUSTER_APP_ID,
    SUBTOPIA_INTRO_APP_ID,
    SUBTOPIA_PROFESSIONAL_APP_ID,
)
from helpers import box_name_from_address
from network import (
    _cometa_app_amount,
    _cometa_app_local_state_for_address,
    check_and_update_changed_subscriptions_and_staking,
    check_and_update_new_stakers,
    check_and_update_new_subscribers,
    create_app,
    current_governance_staking_for_address,
    delete_app,
    delete_box,
    deserialized_permission_dapp_box_value,
    fetch_subscriptions_for_address,
    fetch_subscriptions_from_boxes,
    permission_dapp_values_from_boxes,
    write_box,
    write_foundation_boxes,
)


# # SUBSCRIPTIONS
class TestNetworkSubscriptionsFunctions:
    """Testing class for :py:mod:`network` subscriptions functions."""

    # # fetch_subscriptions_for_address``
    def test_network_fetch_subscriptions_for_address_functionality(self, mocker):
        client = mocker.MagicMock()
        address = "OECZJTT5M2RTJMAWG7N3RBIJSU4M37O47DGHKLHLI6ZNHK5Q7ZDM2VMI6I"
        response1 = {
            "value": "AAAAACuMc0sAAAAAAAAAAgAAAABnWCsBAAAAAGdp/8AAAAAAACeNAA=="
        }
        response2 = {
            "value": "AAAAACuMc0sAAAAAAAAAAgAAAABnWDCdAAAAAGd/vZ0AAAAAACeNAA=="
        }
        response3 = {
            "value": "AAAAACuMejoAAAAAAAAAAgAAAABnWDPFAAAAAGd/wMUAAAAAACeNAA=="
        }
        client.application_box_by_name.side_effect = [
            response1,
            AlgodHTTPError(""),
            response2,
            response3,
        ]
        returned = fetch_subscriptions_for_address(client, address)
        assert returned == {
            "Intro": 1735000000,
            "Professional": 1736424861,
            "Cluster": 1736425669,
        }
        calls = [
            mocker.call(SUBTOPIA_INTRO_APP_ID, box_name_from_address(address)),
            mocker.call(SUBTOPIA_ASASTATSER_APP_ID, box_name_from_address(address)),
            mocker.call(SUBTOPIA_PROFESSIONAL_APP_ID, box_name_from_address(address)),
            mocker.call(SUBTOPIA_CLUSTER_APP_ID, box_name_from_address(address)),
        ]
        client.application_box_by_name.assert_has_calls(calls, any_order=True)
        assert client.application_box_by_name.call_count == 4

    # # fetch_subscriptions_from_boxes
    def test_network_fetch_subscriptions_from_boxes_functionality(self, mocker):
        client = mocker.MagicMock()
        boxes1 = {
            "boxes": [
                {"name": "cQWUzn1mozSwFjfbuIUJlTjN/dz4zHUs60ey06uw/kY="},
                {"name": "UaclYCXAuWPiHXrf8oGGJP7qWeTwM3TaAFTYJHAsz4o="},
                {"name": "0Sps8CZ0l7T7lMDJoNDTbMOc5WjvK0hBucrwIbhrxvc="},
            ]
        }
        boxes2 = {
            "boxes": [
                {"name": "rbvVZ20vDDdZH0Pss2Rls29lSiPryTisYA5rTt3qilM="},
                {"name": "UaclYCXAuWPiHXrf8oGGJP7qWeTwM3TaAFTYJHAsz4o="},
            ]
        }
        boxes3 = {"boxes": [{"name": "XdO4ejnU0+qJIyskzmatxjBOKrJe26niOtvW0SRIuFk="}]}
        boxes4 = {
            "boxes": [
                {"name": "qojQu7bQ8gyWEedk6DvIZaXaMrkR1vIATXIR8I0zMHI="},
                {"name": "cQWUzn1mozSwFjfbuIUJlTjN/dz4zHUs60ey06uw/kY="},
            ]
        }
        boxes5 = {
            "boxes": [
                {"name": "qojQu7bQ8gyWEedk6DvIZaXaMrkR1vIATXIR8I0zMHI="},
                {"name": "cQWUzn1mozSwFjfbuIUJlTjN/dz4zHUs60ey06uw/kY="},
                {"name": "rbvVZ20vDDdZH0Pss2Rls29lSiPryTisYA5rTt3qilM="},
            ]
        }
        client.application_boxes.side_effect = [boxes1, boxes2, boxes3, boxes4, boxes5]
        response1 = {
            "value": "AAAAACuMc0sAAAAAAAAAAgAAAABnWCsBAAAAAGdp/8AAAAAAACeNAA=="
        }
        response2 = {
            "value": "AAAAACuMc0sAAAAAAAAAAgAAAABnWDPFAAAAAGd/wMUAAAAAACeNAA=="
        }
        response3 = {
            "value": "AAAAACuMc0sAAAAAAAAAAgAAAABnWDCdAAAAAGd/vZ0AAAAAACeNAA=="
        }
        response4 = {
            "value": "AAAAACuMejoAAAAAAAAAAgAAAABnWDPFAAAAAGd/wMUAAAAAACeNAA=="
        }
        response5 = {
            "value": "AAAAACuMejoAAAAAAAAAAgAAAABnWDPFAAAAAGd/wMUAAAAAACeNAA=="
        }
        response6 = {
            "value": "AAAAACuMd3YAAAAAAAAAAgAAAABnWDCdAAAAAGd/vZ0AAAAAACeNAA=="
        }
        response7 = {
            "value": "AAAAACuMeFsAAAAAAAAAAgAAAABnWDFuAAAAAGd/vm4AAAAAACeNAA=="
        }
        response8 = {
            "value": "AAAAACuMeFsAAAAAAAAAAgAAAABnWDFuAAAAAGd/vm4AAAAAACeNAA=="
        }
        response9 = {
            "value": "AAAAACuMe5cAAAAAAAAAAgAAAABnWDVkAAAAAAAAAAAAAAAAAAAAAA=="
        }
        response10 = {
            "value": "AAAAACuMe3UAAAAAAAAAAgAAAABnWDUzAAAAAAAAAAAAAAAAAAAAAA=="
        }
        response11 = {
            "value": "AAAAACuMe5cAAAAAAAAAAgAAAABnWDVkAAAAAAAAAAAAAAAAAAAAAA=="
        }
        client.application_box_by_name.side_effect = [
            response1,
            response2,
            response3,
            response4,
            response5,
            response6,
            response7,
            response8,
            response9,
            response10,
            response11,
        ]
        address1, address2, address3, address4, address5 = (
            "OECZJTT5M2RTJMAWG7N3RBIJSU4M37O47DGHKLHLI6ZNHK5Q7ZDM2VMI6I",
            "KGTSKYBFYC4WHYQ5PLP7FAMGET7OUWPE6AZXJWQAKTMCI4BMZ6FGCPSHPQ",
            "VW55KZ3NF4GDOWI7IPWLGZDFWNXWKSRD5PETRLDABZVU5XPKRJJRK3CBSU",
            "LXJ3Q6RZ2TJ6VCJDFMSM4ZVNYYYE4KVSL3N2TYR23PLNCJCIXBM3NYTBYE",
            "VKENBO5W2DZAZFQR45SOQO6IMWS5UMVZCHLPEACNOII7BDJTGBZKSEL4Y4",
        )
        with mock.patch("network.datetime") as mocked_datetime:
            mocked_datetime.now.return_value.timestamp.side_effect = [
                1736000000,
                1736000000,
                1776000000,
                1736000000,
                1736512069,
                1736000000,
                1736000000,
                1736000000,
                1736000000,
                1756000000,
                1536000000,
            ]
            returned = fetch_subscriptions_from_boxes(client)
        assert returned == {
            address1: [(500000000000, 3236067977500)],
            address2: [(2500000000, 2329968943)],
            address3: [(18000000000, 23299689438)],
            address4: [(38000000000, 258885438200)],
            address5: [(500000000000, 3236067977500)],
        }
        calls = [mocker.call(app_id) for app_id in SUBSCRIPTION_PERMISSIONS]
        client.application_boxes.assert_has_calls(calls, any_order=True)
        assert client.application_boxes.call_count == len(SUBSCRIPTION_PERMISSIONS)
        calls = [
            mocker.call(
                SUBTOPIA_INTRO_APP_ID, base64.b64decode(boxes1["boxes"][0]["name"])
            ),
            mocker.call(
                SUBTOPIA_INTRO_APP_ID, base64.b64decode(boxes1["boxes"][1]["name"])
            ),
            mocker.call(
                SUBTOPIA_INTRO_APP_ID, base64.b64decode(boxes1["boxes"][2]["name"])
            ),
            mocker.call(
                SUBTOPIA_ASASTATSER_APP_ID, base64.b64decode(boxes2["boxes"][0]["name"])
            ),
            mocker.call(
                SUBTOPIA_ASASTATSER_APP_ID, base64.b64decode(boxes2["boxes"][1]["name"])
            ),
            mocker.call(
                SUBTOPIA_PROFESSIONAL_APP_ID,
                base64.b64decode(boxes3["boxes"][0]["name"]),
            ),
            mocker.call(
                SUBTOPIA_CLUSTER_APP_ID, base64.b64decode(boxes4["boxes"][0]["name"])
            ),
            mocker.call(
                SUBTOPIA_CLUSTER_APP_ID, base64.b64decode(boxes4["boxes"][1]["name"])
            ),
        ]
        client.application_box_by_name.assert_has_calls(calls, any_order=True)
        assert client.application_box_by_name.call_count == 8


# # STAKING
class TestNetworkStakingFunctions:
    """Testing class for :py:mod:`network` governance staking functions."""

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
        client.account_info.assert_called_once_with(address)

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
        client.account_info.assert_called_once_with(address)

    # # current_governance_staking_for_address
    def test_network_current_governance_staking_for_address_functionality_no_staking(
        self, mocker
    ):
        returned = current_governance_staking_for_address(
            mocker.MagicMock(), mocker.MagicMock()
        )
        assert returned == 0

    def test_network_current_governance_staking_for_address_for_no_state(self, mocker):
        client, address = mocker.MagicMock(), mocker.MagicMock()
        mocked_state = mocker.patch(
            "network._cometa_app_local_state_for_address", return_value=None
        )
        mocked_amount = mocker.patch("network._cometa_app_amount")
        returned = current_governance_staking_for_address(
            client, address, staking_key=STAKING_KEY
        )
        assert returned == 0
        mocked_state.assert_called_once_with(client, address)
        mocked_amount.assert_not_called()

    def test_network_current_governance_staking_for_address_functionality(self, mocker):
        client, address = mocker.MagicMock(), mocker.MagicMock()
        state = mocker.MagicMock()
        mocked_state = mocker.patch(
            "network._cometa_app_local_state_for_address", return_value=state
        )
        mocked_amount = mocker.patch("network._cometa_app_amount")
        staking_key = STAKING_KEY
        returned = current_governance_staking_for_address(
            client, address, staking_key=staking_key
        )
        assert returned == mocked_amount.return_value
        mocked_state.assert_called_once_with(client, address)
        mocked_amount.assert_called_once_with(staking_key, state)


class TestNetworkUpdateFunctions:
    """Testing class for :py:mod:`network` update functions."""

    # # check_and_update_changed_subscriptions_and_staking
    def test_network_check_and_update_changed_subscriptions_and_staking_for_no_changes(
        self, mocker
    ):
        permissions = {
            "address1": [1000, 500, 1000, 100, 5000, 200, 2000, 2],
            "address2": [5000, 800, 2000, 200, 8000, 400, 3000, 2],
        }
        subscriptions = {"address1": [(1000, 100)], "address2": [(2000, 200)]}
        stakings = {"address1": 5000, "address2": 8000}
        mocked_write = mocker.patch("network.write_box")
        check_and_update_changed_subscriptions_and_staking(
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            permissions,
            subscriptions,
            stakings,
        )
        mocked_write.assert_not_called()

    def test_network_check_and_update_changed_subscriptions_and_staking_functionality(
        self, mocker
    ):
        client, app_id, writing_parameters = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        address1, address2, address3, address4 = (
            "address1",
            "address2",
            "address3",
            "address4",
        )
        permissions = {
            address1: [1000, 500, 0, 0, 5000, 200, 2000, 2],
            address2: [5000, 800, 1000, 200, 8500, 400, 3000, 2],
            address3: [750, 7500, 18000, 1500, 0, 0],
            address4: [100, 200, 7000, 700, 3000, 600],
            "address5": [0, 500, 0, 0, 0, 0, 1000, 1],
        }
        amount1, permission1, amount2, permission2, amount3, permission3 = (
            1000,
            100,
            2000,
            200,
            8000,
            800,
        )
        amount4, amount5 = 4000, 3000
        subscriptions = {
            address2: [(amount1, permission1)],
            address4: [(amount2, permission2), (amount3, permission3)],
        }
        stakings = {address1: amount4, address4: amount5}
        permission4 = 100
        mocked_permission = mocker.patch(
            "network.permission_for_amount", return_value=permission4
        )
        mocked_write = mocker.patch("network.write_box")
        check_and_update_changed_subscriptions_and_staking(
            client, app_id, writing_parameters, permissions, subscriptions, stakings
        )
        mocked_permission.assert_called_once_with(amount4)
        calls = [
            mocker.call(
                client,
                app_id,
                writing_parameters,
                address1,
                "AAAAAAAAAAAAAAAAAAAINAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPoAAAAAAAAABkAAAAAAAAB9AC",
            ),
            mocker.call(
                client,
                app_id,
                writing_parameters,
                address3,
                "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            ),
            mocker.call(
                client,
                app_id,
                writing_parameters,
                address4,
                "AAAAAAAAAAAAAAAAAAAGQAAAAAAAACcQAAAAAAAAA+gAAAAAAAALuAAAAAAAAAJY",
            ),
        ]
        mocked_write.assert_has_calls(calls, any_order=True)
        assert mocked_write.call_count == 3

    # # check_and_update_new_stakers
    def test_network_check_and_update_new_stakers_for_no_new_stakers(self, mocker):
        permissions = {"address1": mocker.MagicMock(), "address2": mocker.MagicMock()}
        stakings = {
            "address1": [(mocker.MagicMock(), mocker.MagicMock())],
            "address2": [(mocker.MagicMock(), mocker.MagicMock())],
        }
        mocked_write = mocker.patch("network.write_box")
        check_and_update_new_stakers(
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            permissions,
            stakings,
        )
        mocked_write.assert_not_called()

    def test_network_check_and_update_new_stakers_functionality(self, mocker):
        client, app_id, writing_parameters = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        address1, address2, address3 = "address1", "address2", "address3"
        permissions = {"address4": mocker.MagicMock()}
        amount1, amount2, amount3 = 1000, 2000, 5000
        permission1, permission2, permission3 = 100, 0, 300
        stakings = {
            address1: amount1,
            address2: amount2,
            address3: amount3,
            "address4": mocker.MagicMock(),
        }
        mocked_permission = mocker.patch(
            "network.permission_for_amount",
            side_effect=[permission1, permission2, permission3],
        )
        mocked_write = mocker.patch("network.write_box")
        check_and_update_new_stakers(
            client, app_id, writing_parameters, permissions, stakings
        )
        calls = [mocker.call(amount1), mocker.call(amount2), mocker.call(amount3)]
        mocked_permission.assert_has_calls(calls, any_order=True)
        assert mocked_permission.call_count == 3
        calls = [
            mocker.call(
                client,
                app_id,
                writing_parameters,
                address1,
                "AAAAAAAAAAAAAAAAAAAAZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD6AAAAAAAAABk",
            ),
            mocker.call(
                client,
                app_id,
                writing_parameters,
                address3,
                "AAAAAAAAAAAAAAAAAAABLAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATiAAAAAAAAAEs",
            ),
        ]
        mocked_write.assert_has_calls(calls, any_order=True)
        assert mocked_write.call_count == 2

    # # check_and_update_new_subscribers
    def test_network_check_and_update_new_subscribers_for_no_new_subscibers(
        self, mocker
    ):
        permissions = {"address1": mocker.MagicMock(), "address2": mocker.MagicMock()}
        subscriptions = {
            "address1": [(mocker.MagicMock(), mocker.MagicMock())],
            "address2": [(mocker.MagicMock(), mocker.MagicMock())],
        }
        mocked_write = mocker.patch("network.write_box")
        check_and_update_new_subscribers(
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            permissions,
            subscriptions,
        )
        mocked_write.assert_not_called()

    def test_network_check_and_update_new_subscribers_functionality(self, mocker):
        client, app_id, writing_parameters = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        address2, address3 = "address2", "address3"
        permissions = {"address1": mocker.MagicMock(), "address4": mocker.MagicMock()}
        amount1, permission1, amount2, permission2, amount3, permission3 = (
            1000,
            100,
            2000,
            200,
            5000,
            500,
        )
        subscriptions = {
            "address1": [(mocker.MagicMock(), mocker.MagicMock())],
            address2: [(amount1, permission1)],
            address3: [(amount2, permission2), (amount3, permission3)],
            "address4": [(mocker.MagicMock(), mocker.MagicMock())],
        }
        mocked_write = mocker.patch("network.write_box")
        check_and_update_new_subscribers(
            client, app_id, writing_parameters, permissions, subscriptions
        )
        calls = [
            mocker.call(
                client,
                app_id,
                writing_parameters,
                address2,
                "AAAAAAAAAAAAAAAAAAAAZAAAAAAAAAPoAAAAAAAAAGQAAAAAAAAAAAAAAAAAAAAA",
            ),
            mocker.call(
                client,
                app_id,
                writing_parameters,
                address3,
                "AAAAAAAAAAAAAAAAAAACvAAAAAAAABtYAAAAAAAAArwAAAAAAAAAAAAAAAAAAAAA",
            ),
        ]
        mocked_write.assert_has_calls(calls, any_order=True)
        assert mocked_write.call_count == 2


class TestNetworkPermissionDappFunctions:
    """Testing class for :py:mod:`network` Permission dApp functions."""

    # # create_app
    def test_network_create_app_calls_wait_and_returns_app_id(self, mocker):
        client = mocker.MagicMock()
        private_key = mocker.MagicMock()
        approval_program = mocker.MagicMock()
        clear_program = mocker.MagicMock()
        contract_json = mocker.MagicMock()

        sender_address = mocker.MagicMock()
        mocker.patch("network.address_from_private_key", return_value=sender_address)

        mock_txn = mocker.MagicMock()
        mock_signed = mocker.MagicMock()
        mock_signed.transaction.get_txid.return_value = "txid123"
        mocker.patch("network.transaction.ApplicationCreateTxn", return_value=mock_txn)
        mock_txn.sign.return_value = mock_signed

        mocked_wait = mocker.patch("network.wait_for_confirmation")
        client.pending_transaction_info.return_value = {"application-index": 99}
        mock_params = mocker.MagicMock()
        mock_params.gh = b"genesis_hash_value"
        client.suggested_params.return_value = mock_params

        returned_app_id, returned_genesis_hash = create_app(
            client, private_key, approval_program, clear_program, contract_json
        )

        assert returned_app_id == 99
        assert returned_genesis_hash == b"genesis_hash_value"
        mock_txn.sign.assert_called_once_with(private_key)
        client.send_transactions.assert_called_once_with([mock_signed])
        mocked_wait.assert_called_once_with(client, "txid123")

    # # delete_app
    def test_network_delete_app_calls_wait(self, mocker):
        client = mocker.MagicMock()
        private_key = mocker.MagicMock()
        index = 2000

        sender_address = mocker.MagicMock()
        mocker.patch("network.address_from_private_key", return_value=sender_address)

        mock_txn = mocker.MagicMock()
        mock_signed = mocker.MagicMock()
        mock_signed.transaction.get_txid.return_value = "txid123"
        mocker.patch("network.transaction.ApplicationDeleteTxn", return_value=mock_txn)
        mock_txn.sign.return_value = mock_signed

        mocked_wait = mocker.patch("network.wait_for_confirmation")

        client.pending_transaction_info.return_value = {"txn": {"txn": {"apid": index}}}

        delete_app(client, private_key, index)

        mock_txn.sign.assert_called_once_with(private_key)
        client.send_transactions.assert_called_once_with([mock_signed])
        mocked_wait.assert_called_once_with(client, "txid123")

    # # delete_box
    def test_network_delete_box_functionality(self, mocker):
        client, app_id = mocker.MagicMock(), mocker.MagicMock()
        address = "2EVGZ4BGOSL3J64UYDE2BUGTNTBZZZLI54VUQQNZZLYCDODLY33UGXNSIU"
        box_name = (
            b"\xd1*l\xf0&t\x97\xb4\xfb\x94\xc0\xc9\xa0\xd0"
            b"\xd3l\xc3\x9c\xe5h\xef+HA\xb9\xca\xf0!\xb8k\xc6\xf7"
        )
        atc = mocker.MagicMock()
        mocked_composer = mocker.patch(
            "network.AtomicTransactionComposer", return_value=atc
        )
        sender, signer, contract = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        method = mocker.MagicMock()
        writing_parameters = {"sender": sender, "signer": signer, "contract": contract}
        contract.get_method_by_name.return_value = method
        delete_box(client, app_id, writing_parameters, address)
        mocked_composer.assert_called_once_with()
        client.suggested_params.assert_called_once_with()
        contract.get_method_by_name.assert_called_once_with("delete_box")
        atc.add_method_call.assert_called_once_with(
            app_id=app_id,
            method=contract.get_method_by_name.return_value,
            sender=sender,
            sp=client.suggested_params.return_value,
            signer=signer,
            method_args=[box_name],
            boxes=[(app_id, box_name)],
        )
        atc.execute.assert_called_once_with(client, 2)

    # # deserialized_permission_dapp_box_value
    def test_network_deserialized_permission_dapp_returns_none_for_no_box(self, mocker):
        client, app_id, box_name = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        mocked_deserialize = mocker.patch("network.deserialize_values_data")
        client.application_box_by_name.side_effect = AlgodHTTPError("box not found")
        returned = deserialized_permission_dapp_box_value(client, app_id, box_name)
        assert returned is None
        client.application_box_by_name.assert_called_once_with(app_id, box_name)
        mocked_deserialize.assert_not_called()

    def test_network_deserialized_permission_dapp_raises_for_other_errors(self, mocker):
        client, app_id, box_name = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        mocked_deserialize = mocker.patch("network.deserialize_values_data")
        client.application_box_by_name.side_effect = AlgodHTTPError("foo bar")
        with pytest.raises(AlgodHTTPError):
            deserialized_permission_dapp_box_value(client, app_id, box_name)
        client.application_box_by_name.assert_called_once_with(app_id, box_name)
        mocked_deserialize.assert_not_called()

    def test_network_deserialized_permission_dapp_box_value_functionality(self, mocker):
        client, app_id, box_name = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        value = (
            "QUFBQUFBQUhvU0FBQUFCMGFsS0lBQUFBQUFBQUFBQUFBQUFBQUFB"
            "QUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFkR3BTaUFBRQ=="
        )
        response = {"value": value}
        client.application_box_by_name.return_value = response
        returned = deserialized_permission_dapp_box_value(client, app_id, box_name)
        assert returned == [500000, 500000000000, 0, 0, 0, 0, 500000000000, 4]
        client.application_box_by_name.assert_called_once_with(app_id, box_name)

    # # permission_dapp_values_from_boxes
    def test_network_permission_dapp_values_from_boxes_raises_for_no_app_id(
        self, mocker
    ):
        with pytest.raises(ValueError) as exception:
            permission_dapp_values_from_boxes(mocker.MagicMock(), None)
            assert str(exception.value) == "Permission dApp ID isn't set!"

    def test_network_permission_dapp_values_from_boxes_functionality(self, mocker):
        client = mocker.MagicMock()
        app_id = 5050
        boxes = {
            "boxes": [
                {"name": "kh+jKvvPrg8LnAjH5OrWstXqJLucdZLRBUJCtsuFyBQ="},
                {"name": "wKicAOgLIKzPmAA0twVXMMBVwaVLVuoXHl9+Jf3wWAE="},
                {"name": "hBV+y5sLUru3xZ5GdkhVkl+dL5901V/Jxvh+YzNG3JE="},
                {"name": "DdECAhXvBtesYfyhYV8kFX/c5WBt/83UxUPS4O4/Avk="},
                {"name": "tdFRqNIIwrC1T95wS6adscJH4Wp0AWuHBTJ9UdcwBuw="},
            ]
        }
        client.application_boxes.return_value = boxes
        values1, values2, values3, values4 = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        mocked_deserialized = mocker.patch(
            "network.deserialized_permission_dapp_box_value",
            side_effect=[values1, values2, None, values3, values4],
        )
        address1, address2, address3, address4 = (
            "SIP2GKX3Z6XA6C44BDD6J2WWWLK6UJF3TR2ZFUIFIJBLNS4FZAKKTADUQU",
            "YCUJYAHIBMQKZT4YAA2LOBKXGDAFLQNFJNLOUFY6L57CL7PQLAAYCLLV2A",
            "BXIQEAQV54DNPLDB7SQWCXZECV75ZZLANX743VGFIPJOB3R7AL4TA7WYNY",
            "WXIVDKGSBDBLBNKP3ZYEXJU5WHBEPYLKOQAWXBYFGJ6VDVZQA3WCLSE4WA",
        )
        returned = permission_dapp_values_from_boxes(client, app_id)
        assert returned == {
            address1: values1,
            address2: values2,
            address3: values3,
            address4: values4,
        }
        client.application_boxes.assert_called_once_with(app_id)
        calls = [
            mocker.call(client, app_id, base64.b64decode(boxes["boxes"][i]["name"]))
            for i in range(len(boxes["boxes"]))
        ]
        mocked_deserialized.assert_has_calls(calls, any_order=True)
        assert mocked_deserialized.call_count == len(boxes["boxes"])

    # # write_box
    def test_network_write_box_functionality(self, mocker):
        client, app_id, writing_parameters, value = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        address = "2EVGZ4BGOSL3J64UYDE2BUGTNTBZZZLI54VUQQNZZLYCDODLY33UGXNSIU"
        box_name = (
            b"\xd1*l\xf0&t\x97\xb4\xfb\x94\xc0\xc9\xa0\xd0"
            b"\xd3l\xc3\x9c\xe5h\xef+HA\xb9\xca\xf0!\xb8k\xc6\xf7"
        )
        atc = mocker.MagicMock()
        mocked_composer = mocker.patch(
            "network.AtomicTransactionComposer", return_value=atc
        )
        sender, signer, contract = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        method = mocker.MagicMock()
        writing_parameters = {"sender": sender, "signer": signer, "contract": contract}
        method = mocker.MagicMock()
        contract.get_method_by_name.return_value = method
        write_box(client, app_id, writing_parameters, address, value)
        mocked_composer.assert_called_once_with()
        client.suggested_params.assert_called_once_with()
        contract.get_method_by_name.assert_called_once_with("write_box")
        atc.add_method_call.assert_called_once_with(
            app_id=app_id,
            method=contract.get_method_by_name.return_value,
            sender=sender,
            sp=client.suggested_params.return_value,
            signer=signer,
            method_args=[box_name, value],
            boxes=[(app_id, box_name)],
        )
        atc.execute.assert_called_once_with(client, 2)

    # # write_foundation_boxes
    def test_network_write_foundation_boxes_functionality(self, mocker):
        client, app_id, writing_parameters = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
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
        write_foundation_boxes(client, app_id, writing_parameters, data)
        calls = [mocker.call(values1), mocker.call(values2), mocker.call(values3)]
        mocked_serialize.assert_has_calls(calls, any_order=True)
        assert mocked_serialize.call_count == 3
        calls = [
            mocker.call(client, app_id, writing_parameters, address1, value1),
            mocker.call(client, app_id, writing_parameters, address2, value2),
            mocker.call(client, app_id, writing_parameters, address3, value3),
        ]
        mocked_write.assert_has_calls(calls, any_order=True)
        assert mocked_write.call_count == 3
