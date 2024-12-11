"""Testing module for :py:mod:`network` module."""

import base64
from unittest import mock

import pytest
from algosdk.error import AlgodHTTPError

from config import (
    STAKING_KEY,
    SUBSCRIPTION_PERMISSIONS,
    SUBTOPIA_INTRO_APP_ID,
    SUBTOPIA_ASASTATSER_APP_ID,
    SUBTOPIA_PROFESSIONAL_APP_ID,
    SUBTOPIA_CLUSTER_APP_ID,
    SUBTOPIA_DAO_APP_ID,
)
from network import (
    _cometa_app_amount,
    _cometa_app_local_state_for_address,
    current_governance_staking_for_address,
    fetch_subscriptions_from_boxes,
    delete_box,
    deserialized_permission_dapp_box_value,
    permission_dapp_values_from_boxes,
    write_box,
    write_foundation_boxes,
)


# # SUBSCRIPTIONS
class TestNetworkSubscriptionsFunctions:
    """Testing class for :py:mod:`network` subscriptions functions."""

    # # fetch_subscriptions_from_boxes
    def test_network_fetch_subscriptions_from_boxes_functionality(self, mocker):
        algod_token, algod_address = mocker.MagicMock(), mocker.MagicMock()
        env = {"algod_token": algod_token, "algod_address": algod_address}
        mocked_env = mocker.patch("network.environment_variables", return_value=env)
        client = mocker.MagicMock()
        mocked_client = mocker.patch("network.AlgodClient", return_value=client)
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
        address1, address2, address3, address4, address5, address6 = (
            "OECZJTT5M2RTJMAWG7N3RBIJSU4M37O47DGHKLHLI6ZNHK5Q7ZDM2VMI6I",
            "KGTSKYBFYC4WHYQ5PLP7FAMGET7OUWPE6AZXJWQAKTMCI4BMZ6FGCPSHPQ",
            "2EVGZ4BGOSL3J64UYDE2BUGTNTBZZZLI54VUQQNZZLYCDODLY33UGXNSIU",
            "VW55KZ3NF4GDOWI7IPWLGZDFWNXWKSRD5PETRLDABZVU5XPKRJJRK3CBSU",
            "LXJ3Q6RZ2TJ6VCJDFMSM4ZVNYYYE4KVSL3N2TYR23PLNCJCIXBM3NYTBYE",
            "VKENBO5W2DZAZFQR45SOQO6IMWS5UMVZCHLPEACNOII7BDJTGBZKSEL4Y4",
        )
        with mock.patch("network.datetime") as mocked_datetime:
            mocked_datetime.now.return_value.timestamp.return_value = 1736000000
            returned = fetch_subscriptions_from_boxes()
        assert returned == {
            address1: [(500000000000, 3236067977500), (0, 0)],
            address2: [(2500000000, 2329968943), (18000000000, 23299689438)],
            address3: [(2500000000, 2329968943)],
            address4: [(18000000000, 23299689438), (0, 0)],
            address5: [(38000000000, 258885438200)],
            address6: [(500000000000, 3236067977500), (0, 0)],
        }
        mocked_env.assert_called_once()
        mocked_env.assert_called_with()
        mocked_client.assert_called_once()
        mocked_client.assert_called_with(algod_token, algod_address)
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
            mocker.call(
                SUBTOPIA_DAO_APP_ID, base64.b64decode(boxes5["boxes"][0]["name"])
            ),
            mocker.call(
                SUBTOPIA_DAO_APP_ID, base64.b64decode(boxes5["boxes"][1]["name"])
            ),
            mocker.call(
                SUBTOPIA_DAO_APP_ID, base64.b64decode(boxes5["boxes"][2]["name"])
            ),
        ]
        client.application_box_by_name.assert_has_calls(calls, any_order=True)
        assert client.application_box_by_name.call_count == 11


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

    # # current_governance_staking_for_address
    def test_network_current_governance_staking_for_address_for_no_state(self, mocker):
        client, address = mocker.MagicMock(), mocker.MagicMock()
        mocked_state = mocker.patch(
            "network._cometa_app_local_state_for_address", return_value=None
        )
        mocked_amount = mocker.patch("network._cometa_app_amount")
        returned = current_governance_staking_for_address(client, address)
        assert returned == 0
        mocked_state.assert_called_once()
        mocked_state.assert_called_with(client, address)
        mocked_amount.assert_not_called()

    def test_network_current_governance_staking_for_address_functionality(self, mocker):
        client, address = mocker.MagicMock(), mocker.MagicMock()
        state = mocker.MagicMock()
        mocked_state = mocker.patch(
            "network._cometa_app_local_state_for_address", return_value=state
        )
        mocked_amount = mocker.patch("network._cometa_app_amount")
        returned = current_governance_staking_for_address(client, address)
        assert returned == mocked_amount.return_value
        mocked_state.assert_called_once()
        mocked_state.assert_called_with(client, address)
        mocked_amount.assert_called_once()
        mocked_amount.assert_called_with(STAKING_KEY, state)


class TestNetworkPermissionDappFunctions:
    """Testing class for :py:mod:`network` Permission dApp functions."""

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
        client.application_box_by_name.assert_called_once()
        client.application_box_by_name.assert_called_with(app_id, box_name)
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
        client.application_box_by_name.assert_called_once()
        client.application_box_by_name.assert_called_with(app_id, box_name)
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
        client.application_box_by_name.assert_called_once()
        client.application_box_by_name.assert_called_with(app_id, box_name)

    # # permission_dapp_values_from_boxes
    def test_network_permission_dapp_values_from_boxes_raises_for_no_app_id(
        self, mocker
    ):
        algod_token, algod_address = mocker.MagicMock(), mocker.MagicMock()
        env = {"algod_token": algod_token, "algod_address": algod_address}
        mocked_env = mocker.patch("network.environment_variables", return_value=env)
        mocked_client = mocker.patch("network.AlgodClient")
        with pytest.raises(ValueError) as exception:
            permission_dapp_values_from_boxes()
            assert str(exception.value) == "Permission dApp ID isn't set!"
        mocked_env.assert_called_once()
        mocked_env.assert_called_with()
        mocked_client.assert_not_called()

    def test_network_permission_dapp_values_from_boxes_functionality(self, mocker):
        algod_token, algod_address = mocker.MagicMock(), mocker.MagicMock()
        app_id = 5050
        env = {
            "permission_app_id": app_id,
            "algod_token": algod_token,
            "algod_address": algod_address,
        }
        mocked_env = mocker.patch("network.environment_variables", return_value=env)
        client = mocker.MagicMock()
        mocked_client = mocker.patch("network.AlgodClient", return_value=client)
        boxes = {
            "boxes": [
                {"name": "0Sps8CZ0l7T7lMDJoNDTbMOc5WjvK0hBucrwIbhrxvc="},
                {"name": "8hpyzix6cqySfm/qF8VT/NZSNB2RRkQ8x3BhJggvgXY="},
                {"name": "PS0rYN5N7NcjOcyG2JAZtk2TdZSCylU93lnpdxrWCxU="},
                {"name": "kI7lz3JceNCB4gOOi/HM4PM+V3G5wHLi3LoX5IMf3SM="},
                {"name": "sApIj6tyyM7p4UNQ6Le9FvLDUrWkUnb0aCq262s0JcE="},
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
            "2EVGZ4BGOSL3J64UYDE2BUGTNTBZZZLI54VUQQNZZLYCDODLY33UGXNSIU",
            "6INHFTRMPJZKZET6N7VBPRKT7TLFENA5SFDEIPGHOBQSMCBPQF3BBH4RAY",
            "SCHOLT3SLR4NBAPCAOHIX4OM4DZT4V3RXHAHFYW4XIL6JAY73URXR5PONE",
            "WAFERD5LOLEM52PBINIORN55C3ZMGUVVURJHN5DIFK3OW2ZUEXAYBDEWCA",
        )
        returned = permission_dapp_values_from_boxes()
        assert returned == {
            address1: values1,
            address2: values2,
            address3: values3,
            address4: values4,
        }
        mocked_env.assert_called_once()
        mocked_env.assert_called_with()
        mocked_client.assert_called_once()
        mocked_client.assert_called_with(algod_token, algod_address)
        client.application_boxes.assert_called_once()
        client.application_boxes.assert_called_with(app_id)
        calls = [
            mocker.call(client, app_id, base64.b64decode(boxes["boxes"][i]["name"]))
            for i in range(len(boxes["boxes"]))
        ]
        mocked_deserialized.assert_has_calls(calls, any_order=True)
        assert mocked_deserialized.call_count == len(boxes["boxes"])

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
