"""Testing module for :py:mod:`helpers` module."""

import base64
import json
from pathlib import Path
from unittest import mock

import pytest

import helpers
from config import INDEXER_ADDRESS, INDEXER_TOKEN, STAKING_APP_ID, STAKING_APP_MIN_ROUND
from helpers import (
    _docs_positions_offset_and_length_pairs,
    _extract_uint,
    _indexer_instance,
    _starting_positions_offset_and_length_pairs,
    _value_length_from_values_position,
    _values_offset_and_length_pairs,
    app_schemas,
    box_name_from_address,
    compile_program,
    deserialize_values_data,
    environment_variables,
    governance_staking_addresses,
    load_contract,
    permission_for_amount,
    private_key_from_mnemonic,
    read_json,
    serialize_values,
)


def _valid_boxes_values_and_data():
    return [
        (
            [1, 2, 3, 4, 5, 6],
            "AAAAAAAAAAEAAAAAAAAAAgAAAAAAAAADAAAAAAAAAAQAAAAAAAAABQAAAAAAAAAG",
        ),
        (
            [100, 200, 300, 400, 500, 600],
            "AAAAAAAAAGQAAAAAAAAAyAAAAAAAAAEsAAAAAAAAAZAAAAAAAAAB9AAAAAAAAAJY",
        ),
        (
            [
                10000000000,
                1000000000000,
                0,
                0,
                0,
                0,
                1000000000000,
                1,
            ],
            (
                "AAAAAlQL5AAAAADo1KUQAAAAAAAAAAAAAAAAAA"
                "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA6NSlEAAB"
            ),
        ),
        (
            [100, 200, 300, 400, 500, 600, 700, 5, 800, 6, 900, 7, 1000, 8],
            "AAAAAAAAAGQAAAAAAAAAyAAAAAAAAAEsAAAAAAAAAZAAAAAAAAAB9"
            "AAAAAAAAAJYAAAAAAAAArwFAAAAAAAAAyAGAAAAAAAAA4QHAAAAAAAAA+gI",
        ),
        (
            [
                10000000,
                200000000,
                0,
                0,
                2000500,
                2055200,
                1000,
                1,
                1100,
                2,
                1200,
                3,
                1300,
                4,
                1400,
                5,
                1500,
                6,
                1600,
                7,
                1700,
                8,
                1800,
                9,
                1900,
                10,
                2000,
                11,
                2010,
                12,
            ],
            "AAAAAACYloAAAAAAC+vCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB6GdAAAAAAAH1wgAAAAAAA"
            "AA+gBAAAAAAAABEwCAAAAAAAABLADAAAAAAAABRQEAAAAAAAABXgFAAAAAAAABdwGAAAAAA"
            "AABkAHAAAAAAAABqQIAAAAAAAABwgJAAAAAAAAB2wKAAAAAAAAB9ALAAAAAAAAB9oM",
        ),
    ]


# # VALUES
class TestHelpersValuesFunctions:
    """Testing class for :py:mod:`helpers` values functions."""

    # # _docs_positions_offset_and_length_pairs
    @pytest.mark.parametrize(
        "size,result",
        [
            (0, []),
            (9, [(48, 8), (56, 1)]),
            (18, [(48, 8), (56, 1), (57, 8), (65, 1)]),
            (27, [(48, 8), (56, 1), (57, 8), (65, 1), (66, 8), (74, 1)]),
            (
                36,
                [
                    (48, 8),
                    (56, 1),
                    (57, 8),
                    (65, 1),
                    (66, 8),
                    (74, 1),
                    (75, 8),
                    (83, 1),
                ],
            ),
            (
                108,
                [
                    (48, 8),
                    (56, 1),
                    (57, 8),
                    (65, 1),
                    (66, 8),
                    (74, 1),
                    (75, 8),
                    (83, 1),
                    (84, 8),
                    (92, 1),
                    (93, 8),
                    (101, 1),
                    (102, 8),
                    (110, 1),
                    (111, 8),
                    (119, 1),
                    (120, 8),
                    (128, 1),
                    (129, 8),
                    (137, 1),
                    (138, 8),
                    (146, 1),
                    (147, 8),
                    (155, 1),
                ],
            ),
        ],
    )
    def test_helpers_docs_positions_offset_and_length_pairs_functionality(
        self, size, result
    ):
        returned = _docs_positions_offset_and_length_pairs(size)
        assert returned == result

    # # _extract_uint
    @pytest.mark.parametrize(
        "index,length,result",
        [
            (0, 8, 10000000),
            (8, 8, 200000000),
            (16, 8, 0),
            (24, 8, 0),
            (32, 8, 2000500),
            (40, 8, 2055200),
            (48, 8, 1000),
            (56, 1, 1),
            (57, 8, 1100),
            (65, 1, 2),
            (66, 8, 1200),
            (74, 1, 3),
            (75, 8, 1300),
            (83, 1, 4),
            (84, 8, 1400),
            (92, 1, 5),
            (93, 8, 1500),
            (101, 1, 6),
            (102, 8, 1600),
            (110, 1, 7),
            (111, 8, 1700),
            (119, 1, 8),
            (120, 8, 1800),
            (128, 1, 9),
            (129, 8, 1900),
            (137, 1, 10),
            (138, 8, 2000),
            (146, 1, 11),
            (147, 8, 2010),
            (155, 1, 12),
        ],
    )
    def test_helpers_extract_uint_functionality(self, index, length, result):
        data = (
            "AAAAAACYloAAAAAAC+vCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB6GdAAAAAAAH1wgAAAAAAA"
            "AA+gBAAAAAAAABEwCAAAAAAAABLADAAAAAAAABRQEAAAAAAAABXgFAAAAAAAABdwGAAAAAA"
            "AABkAHAAAAAAAABqQIAAAAAAAABwgJAAAAAAAAB2wKAAAAAAAAB9ALAAAAAAAAB9oM"
        )
        returned = _extract_uint(base64.b64decode(data), index, length)
        assert returned == result

    # # _starting_positions_offset_and_length_pairs
    def test_helpers_starting_positions_offset_and_length_pairs_functionality(self):
        returned = _starting_positions_offset_and_length_pairs()
        assert returned == [
            (0, 8),
            (8, 8),
            (16, 8),
            (24, 8),
            (32, 8),
            (40, 8),
        ]

    # # _value_length_from_values_position
    @pytest.mark.parametrize(
        "position,length",
        [
            (0, 8),
            (1, 8),
            (2, 8),
            (3, 8),
            (4, 8),
            (5, 8),
            (6, 8),
            (7, 1),
            (8, 8),
            (9, 1),
            (24, 8),
            (25, 1),
        ],
    )
    def test_helpers_value_length_from_values_position_functionality(
        self, position, length
    ):
        returned = _value_length_from_values_position(position)
        assert returned == length

    # # _values_offset_and_length_pairs
    def test_helpers_values_offset_and_length_pairs_functionality(self, mocker):
        docs_data_size = mocker.MagicMock()
        starting = [(0, 8), (8, 1)]
        docs = [(48, 8), (56, 1)]
        mocked_starting = mocker.patch(
            "helpers._starting_positions_offset_and_length_pairs",
            return_value=starting,
        )
        mocked_docs = mocker.patch(
            "helpers._docs_positions_offset_and_length_pairs",
            return_value=docs,
        )
        returned = _values_offset_and_length_pairs(docs_data_size)
        assert returned == starting + docs
        mocked_starting.assert_called_once()
        mocked_starting.assert_called_with()
        mocked_docs.assert_called_once()
        mocked_docs.assert_called_with(docs_data_size)

    # # serialize_values
    @pytest.mark.parametrize("values,data", _valid_boxes_values_and_data())
    def test_helpers_serialize_values_functionality(self, values, data):
        returned = serialize_values(values)
        assert returned == data

    # # deserialize_values_data
    @pytest.mark.parametrize("values,data", _valid_boxes_values_and_data())
    def test_helpers_deserialize_values_data_functionality(self, values, data):
        returned = deserialize_values_data(data)
        assert returned == values


# # BOXES
class TestHelpersBoxesFunctions:
    """Testing class for :py:mod:`helpers` boxes functions."""

    # # box_name_from_address
    @pytest.mark.parametrize(
        "address,box_name",
        [
            (
                "2EVGZ4BGOSL3J64UYDE2BUGTNTBZZZLI54VUQQNZZLYCDODLY33UGXNSIU",
                "0Sps8CZ0l7T7lMDJoNDTbMOc5WjvK0hBucrwIbhrxvc=",
            ),
            (
                "VW55KZ3NF4GDOWI7IPWLGZDFWNXWKSRD5PETRLDABZVU5XPKRJJRK3CBSU",
                "rbvVZ20vDDdZH0Pss2Rls29lSiPryTisYA5rTt3qilM=",
            ),
            (
                "LXJ3Q6RZ2TJ6VCJDFMSM4ZVNYYYE4KVSL3N2TYR23PLNCJCIXBM3NYTBYE",
                "XdO4ejnU0+qJIyskzmatxjBOKrJe26niOtvW0SRIuFk=",
            ),
            (
                "VKENBO5W2DZAZFQR45SOQO6IMWS5UMVZCHLPEACNOII7BDJTGBZKSEL4Y4",
                "qojQu7bQ8gyWEedk6DvIZaXaMrkR1vIATXIR8I0zMHI=",
            ),
        ],
    )
    def test_helpers_box_name_from_address_functionality(self, address, box_name):
        returned = box_name_from_address(address)
        assert returned == box_name


# # CONTRACT
class TestHelpersContractFunctions:
    """Testing class for :py:mod:`helpers` smart contract functions."""

    # # app_schemas
    def test_helpers_app_schemas_functionality(self, mocker):
        schema1, schema2 = mocker.MagicMock(), mocker.MagicMock()
        mocked_schema = mocker.patch(
            "helpers.StateSchema", side_effect=[schema1, schema2]
        )
        returned = app_schemas()
        assert returned == (schema1, schema2)
        calls = [mocker.call(0, 0), mocker.call(0, 0)]
        mocked_schema.assert_has_calls(calls, any_order=True)
        assert mocked_schema.call_count == 2

    # # compile_program
    def test_helpers_compile_program_functionality(self, mocker):
        client = mocker.MagicMock()
        source_code = b"source_code"
        result = base64.b64encode(b"result")
        compile_response = {"result": result}
        client.compile.return_value = compile_response
        returned = compile_program(client, source_code)
        assert returned == b"result"

    # # load_contract
    def test_helpers_load_contract_functionality(self, mocker):
        contract_json = mocker.MagicMock()
        mocked_read = mocker.patch("helpers.read_json", return_value=contract_json)
        mocked_undictify = mocker.patch("helpers.Contract.undictify")
        returned = load_contract()
        assert returned == mocked_undictify.return_value
        mocked_read.assert_called_once()
        mocked_read.assert_called_with(
            Path(helpers.__file__).resolve().parent / "artifacts" / "contract.json"
        )
        mocked_undictify.assert_called_once()
        mocked_undictify.assert_called_with(contract_json)


# # STAKING
class TestHelpersStakingFunctions:
    """Testing class for :py:mod:`helpers` staking functions."""

    # # _indexer_instance
    def test_helpers_indexer_instance_functionality(self, mocker):
        mocked_indexer = mocker.patch("helpers.IndexerClient")
        returned = _indexer_instance()
        assert returned == mocked_indexer.return_value
        mocked_indexer.assert_called_once()
        mocked_indexer.assert_called_with(
            INDEXER_TOKEN, INDEXER_ADDRESS, headers={"User-Agent": "algosdk"}
        )

    # # governance_staking_addresses
    def test_helpers_governance_staking_addresses_functionality(self, mocker):
        mocked_indexer = mocker.patch("helpers._indexer_instance")
        address1, address2, address3, address4, address5 = (
            "address1",
            "address2",
            "address3",
            "address4",
            "address5",
        )
        txns = [
            {"sender": address4},
            {"sender": address2},
            {"sender": address3},
            {"sender": address4},
            {"sender": address1},
            {"sender": address2},
            {"sender": address5},
        ]
        mocked_transaction = mocker.patch(
            "helpers._application_transaction", return_value=txns
        )
        params = {
            "application_id": STAKING_APP_ID,
            "limit": 1000,
            "min_round": STAKING_APP_MIN_ROUND,
        }
        returned = governance_staking_addresses()
        assert isinstance(returned, set)
        assert sorted(list(returned)) == [
            address1,
            address2,
            address3,
            address4,
            address5,
        ]
        mocked_indexer.assert_called_once()
        mocked_indexer.assert_called_with()
        mocked_transaction.assert_called_once()
        mocked_transaction.assert_called_with(params, mocked_indexer.return_value)


# # HELPERS
class TestHelpersHelpersFunctions:
    """Testing class for :py:mod:`helpers` helpers functions."""

    # # environment_variables
    def test_helpers_environment_variables_functionality(self, mocker):
        (
            creator_mnemonic,
            user_mnemonic,
            algod_token,
            algod_address,
            mainnet_algod_address,
            mainnet_algod_token,
            permission_app_id,
        ) = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        mocked_load_dotenv = mocker.patch("helpers.load_dotenv")
        with mock.patch(
            "helpers.os.getenv",
            side_effect=[
                creator_mnemonic,
                user_mnemonic,
                algod_token,
                algod_address,
                mainnet_algod_token,
                mainnet_algod_address,
                permission_app_id,
            ],
        ) as mocked_getenv:
            returned = environment_variables()
            assert returned == {
                "creator_mnemonic": creator_mnemonic,
                "user_mnemonic": user_mnemonic,
                "algod_token": algod_token,
                "algod_address": algod_address,
                "mainnet_algod_token": mainnet_algod_token,
                "mainnet_algod_address": mainnet_algod_address,
                "permission_app_id": permission_app_id,
            }
            calls = [
                mocker.call("CREATOR_MNEMONIC"),
                mocker.call("USER_MNEMONIC"),
                mocker.call("ALGOD_TOKEN"),
                mocker.call("ALGOD_ADDRESS"),
                mocker.call("MAINNET_ALGOD_TOKEN"),
                mocker.call("MAINNET_ALGOD_ADDRESS"),
                mocker.call("PERMISSION_APP_ID"),
            ]
            mocked_getenv.assert_has_calls(calls, any_order=True)
            assert mocked_getenv.call_count == 7
        mocked_load_dotenv.assert_called_once()
        mocked_load_dotenv.assert_called_with()

    # # box_name_from_address
    @pytest.mark.parametrize(
        "amount,permission",
        [
            (
                50_000_000_000_001,
                3236067977500,
            ),
            (
                49_999_999_999_999,
                2588854381999,
            ),
            (
                5_000_000_000_001,
                258885438200,
            ),
            (
                4_999_999_999_999,
                232996894379,
            ),
            (
                500_000_000_001,
                23299689438,
            ),
            (
                1_500_000_000_001,
                69899068314,
            ),
            (
                25_000_000_000_001,
                1294427191000,
            ),
            (
                90_000_000_000_001,
                5824922359500,
            ),
        ],
    )
    def test_helpers_permission_for_amount_functionality(self, amount, permission):
        returned = permission_for_amount(amount)
        assert returned == permission

    @pytest.mark.parametrize(
        "amount",
        [
            0,
            1,
            10000000,
            1000000000,
            999999999,
            450252515252,
            499999999999,
            500000000000,
        ],
    )
    def test_helpers_permission_for_amount_returns_0_for_to_small_amount(self, amount):
        returned = permission_for_amount(amount)
        assert returned == 0

    # # private_key_from_mnemonic
    def test_helpers_private_key_from_mnemonic_functionality(self, mocker):
        passphrase = mocker.MagicMock()
        mocked_key = mocker.patch("helpers.to_private_key")
        returned = private_key_from_mnemonic(passphrase)
        assert returned == mocked_key.return_value
        mocked_key.assert_called_once()
        mocked_key.assert_called_with(passphrase)

    # # read_json
    def test_helpers_read_json_returns_empty_dict_for_no_file(self, mocker):
        path = mocker.MagicMock()
        with (
            mock.patch("helpers.os.path.exists", return_value=False) as mocked_exist,
            mock.patch("helpers.open") as mocked_open,
        ):
            assert read_json(path) == {}
            mocked_exist.assert_called_once()
            mocked_exist.assert_called_with(path)
            mocked_open.assert_not_called()

    def test_helpers_read_json_returns_empty_dict_for_exception(self, mocker):
        with (
            mock.patch("helpers.os.path.exists", return_value=True),
            mock.patch("helpers.open"),
            mock.patch(
                "helpers.json.load", side_effect=json.JSONDecodeError("", "", 0)
            ),
        ):
            assert read_json(mocker.MagicMock()) == {}

    def test_helpers_read_json_returns_json_file_content(self, mocker):
        path = mocker.MagicMock()
        with (
            mock.patch("helpers.os.path.exists", return_value=True),
            mock.patch("helpers.open") as mocked_open,
            mock.patch("helpers.json.load") as mocked_load,
        ):
            assert read_json(path) == mocked_load.return_value
            mocked_open.assert_called_once()
            mocked_open.assert_called_with(path, "r")
            mocked_load.assert_called_once()
            mocked_load.assert_called_with(
                mocked_open.return_value.__enter__.return_value
            )
