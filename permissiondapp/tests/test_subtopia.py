"""Testing module for :py:mod:`subtopia` module."""

import base64
from unittest import mock

from config import (
    SUBSCRIPTION_PERMISSIONS,
    SUBTOPIA_INTRO_APP_ID,
    SUBTOPIA_ASASTATSER_APP_ID,
    SUBTOPIA_PROFESSIONAL_APP_ID,
    SUBTOPIA_CLUSTER_APP_ID,
    SUBTOPIA_DAO_APP_ID,
)
from subtopia import fetch_subscriptions_from_boxes


# # HELPERS
class TestSubtopiaFunctions:
    """Testing class for :py:mod:`subtopia` helpers functions."""

    # # fetch_subscriptions_from_boxes
    def test_subtopia_fetch_subscriptions_from_boxes_functionality(self, mocker):
        algod_token, algod_address = mocker.MagicMock(), mocker.MagicMock()
        env = {"algod_token": algod_token, "algod_address": algod_address}
        mocked_env = mocker.patch("subtopia.environment_variables", return_value=env)
        client = mocker.MagicMock()
        mocked_client = mocker.patch("subtopia.AlgodClient", return_value=client)
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
        with mock.patch("subtopia.datetime") as mocked_datetime:
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
