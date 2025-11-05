"""Testing module for :py:mod:`helpers` module."""

import base64
import json
from pathlib import Path
from unittest import mock

import pytest

import helpers
from config import INDEXER_ADDRESS, INDEXER_TOKEN, STAKING_APP_ID, STAKING_APP_MIN_ROUND
from helpers import (
    _application_transaction,
    _application_transactions,
    _docs_positions_offset_and_length_pairs,
    _extract_uint,
    _indexer_instance,
    _starting_positions_offset_and_length_pairs,
    _value_length_from_values_position,
    _values_offset_and_length_pairs,
    app_schemas,
    box_name_from_address,
    box_writing_parameters,
    calculate_votes_and_permission,
    compile_program,
    deserialize_values_data,
    environment_variables,
    governance_staking_addresses,
    load_contract,
    pause,
    permission_for_amount,
    private_key_from_mnemonic,
    read_json,
    serialize_values,
    wait_for_confirmation,
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
        mocked_starting.assert_called_once_with()
        mocked_docs.assert_called_once_with(docs_data_size)

    # # deserialize_values_data
    @pytest.mark.parametrize("values,data", _valid_boxes_values_and_data())
    def test_helpers_deserialize_values_data_functionality(self, values, data):
        returned = deserialize_values_data(data)
        assert returned == values

    # # serialize_values
    @pytest.mark.parametrize("values,data", _valid_boxes_values_and_data())
    def test_helpers_serialize_values_functionality(self, values, data):
        returned = serialize_values(values)
        assert returned == data


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
        mocked_read.assert_called_once_with(
            Path(helpers.__file__).resolve().parent / "artifacts" / "contract.json"
        )
        mocked_undictify.assert_called_once_with(contract_json)


# # STAKING
class TestHelpersStakingFunctions:
    """Testing class for :py:mod:`helpers` staking functions."""

    # # _application_transaction
    def test_helpers_application_transaction_functionality_for_no_transactions(
        self, mocker
    ):
        params, indexer_client = (
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        mocked_pause = mocker.patch("helpers.pause")
        mocked_transactions = mocker.patch(
            "helpers._application_transactions", return_value={"transactions": []}
        )
        yielded = list(_application_transaction(params, indexer_client))
        assert yielded == []
        mocked_transactions.assert_called_once_with(params, indexer_client, delay=1)
        mocked_pause.assert_not_called()

    def test_helpers_application_transaction_functionality(self, mocker):
        params, indexer_client = (
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        mocked_pause = mocker.patch("helpers.pause")
        txn1, txn2, txn3, txn4, txn5 = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        token1, token2 = (
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        mocked_transactions = mocker.patch(
            "helpers._application_transactions",
            side_effect=[
                {"transactions": [txn1, txn2, txn3], "next-token": token1},
                {"transactions": [txn4, txn5], "next-token": token2},
                {"transactions": [], "next-token": mocker.MagicMock()},
            ],
        )
        yielded = list(_application_transaction(params, indexer_client))
        assert yielded == [txn1, txn2, txn3, txn4, txn5]
        mocked_pause.assert_called_with(1)
        assert mocked_pause.call_count == 2
        calls = [
            mocker.call(params, indexer_client, delay=1),
            mocker.call(params, indexer_client, next_page=token1, delay=1),
            mocker.call(params, indexer_client, next_page=token2, delay=1),
        ]
        mocked_transactions.assert_has_calls(calls, any_order=True)
        assert mocked_transactions.call_count == 3

    # # _application_transactions
    def test_helpers_application_transactions_returns_transactions_for_default(
        self, mocker
    ):
        indexer_client, txns = mocker.MagicMock(), mocker.MagicMock()
        params = {"foo": "bar"}
        mocked_pause = mocker.patch("helpers.pause")
        indexer_client.search_transactions.return_value = txns
        returned = _application_transactions(params, indexer_client)
        assert returned == txns
        mocked_pause.assert_called_once_with(1)
        indexer_client.search_transactions.assert_called_once_with(**params)

    def test_helpers_application_transactions_returns_transactions_for_added_delay(
        self, mocker
    ):
        indexer_client, txns, next_page = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        params = {"foo": "bar"}
        mocked_pause = mocker.patch("helpers.pause")
        indexer_client.search_transactions.return_value = txns
        delay = 2
        returned = _application_transactions(
            params, indexer_client, next_page=next_page, delay=delay
        )
        assert returned == txns
        mocked_pause.assert_called_once_with(delay)
        indexer_client.search_transactions.assert_called_once_with(
            **params, next_page=next_page
        )

    def test_helpers_application_transactions_logs_error_for_exception_default_values(
        self, mocker
    ):
        indexer_client, txns = mocker.MagicMock(), mocker.MagicMock()
        params = {"foo": "bar"}
        mocked_pause = mocker.patch("helpers.pause")
        indexer_client.search_transactions.side_effect = [
            Exception("a"),
            Exception("b"),
            txns,
        ]
        with mock.patch("helpers.print") as mocked_print:
            returned = _application_transactions(params, indexer_client)
            assert returned == txns
            calls = [
                mocker.call(
                    "Exception a raised searching transactions: %s; Paused..."
                    % ({"foo": "bar"})
                ),
                mocker.call(
                    "Exception b raised searching transactions: %s; Paused..."
                    % ({"foo": "bar"})
                ),
            ]
            mocked_print.assert_has_calls(calls, any_order=True)
            assert mocked_print.call_count == 2
        calls = [mocker.call(1), mocker.call(5)]
        mocked_pause.assert_has_calls(calls, any_order=True)
        assert mocked_pause.call_count == 5

    def test_helpers_application_transactions_logs_error_for_exception_provided_values(
        self, mocker
    ):
        indexer_client, txns = mocker.MagicMock(), mocker.MagicMock()
        params = {"foo": "bar"}
        mocked_pause = mocker.patch("helpers.pause")
        delay = 0.5
        error_delay = 10
        indexer_client.search_transactions.side_effect = [
            Exception("a"),
            Exception("b"),
            txns,
        ]
        with mock.patch("helpers.print") as mocked_print:
            returned = _application_transactions(
                params,
                indexer_client,
                delay=delay,
                error_delay=error_delay,
            )
            assert returned == txns
            calls = [
                mocker.call(
                    "Exception a raised searching transactions: %s; Paused..."
                    % ({"foo": "bar"})
                ),
                mocker.call(
                    "Exception b raised searching transactions: %s; Paused..."
                    % ({"foo": "bar"})
                ),
            ]
            mocked_print.assert_has_calls(calls, any_order=True)
            assert mocked_print.call_count == 2
        calls = [mocker.call(delay), mocker.call(error_delay)]
        mocked_pause.assert_has_calls(calls, any_order=True)
        assert mocked_pause.call_count == 5

    def test_helpers_application_transactions_logs_and_exits_for_max_retries_default(
        self, mocker
    ):
        indexer_client = mocker.MagicMock()
        params = {"foo": "bar"}
        mocked_pause = mocker.patch("helpers.pause")
        indexer_client.search_transactions.side_effect = [Exception("")] * 20
        with mock.patch("helpers.print") as mocked_print:
            returned = _application_transactions(params, indexer_client)
            assert returned == {}
            calls = [
                mocker.call(
                    "Exception  raised searching transactions: %s; Paused..."
                    % ({"foo": "bar"})
                ),
                mocker.call("Maximum number of retries reached. Exiting..."),
            ]
            mocked_print.assert_has_calls(calls, any_order=True)
            assert mocked_print.call_count == 21
        calls = [mocker.call(1), mocker.call(5)]
        mocked_pause.assert_has_calls(calls, any_order=True)
        assert mocked_pause.call_count == 41

    def test_helpers_application_transactions_logs_and_exits_for_max_retries_provided(
        self, mocker
    ):
        indexer_client = mocker.MagicMock()
        params = {"foo": "bar"}
        mocked_pause = mocker.patch("helpers.pause")
        retries = 10
        indexer_client.search_transactions.side_effect = [Exception("")] * retries
        with mock.patch("helpers.print") as mocked_print:
            returned = _application_transactions(
                params, indexer_client, retries=retries
            )
            assert returned == {}
            calls = [
                mocker.call(
                    "Exception  raised searching transactions: %s; Paused..."
                    % ({"foo": "bar"})
                ),
                mocker.call("Maximum number of retries reached. Exiting..."),
            ]
            mocked_print.assert_has_calls(calls, any_order=True)
            assert mocked_print.call_count == retries + 1
        calls = [mocker.call(1), mocker.call(5)]
        mocked_pause.assert_has_calls(calls, any_order=True)
        assert mocked_pause.call_count == retries * 2 + 1

    # # _indexer_instance
    def test_helpers_indexer_instance_functionality(self, mocker):
        mocked_indexer = mocker.patch("helpers.IndexerClient")
        returned = _indexer_instance()
        assert returned == mocked_indexer.return_value
        mocked_indexer.assert_called_once_with(
            INDEXER_TOKEN, INDEXER_ADDRESS, headers={"User-Agent": "algosdk"}
        )

    # # governance_staking_addresses
    def test_helpers_governance_staking_addresses_functionality(self):
        returned = governance_staking_addresses()
        assert returned == set()

    def test_helpers_governance_staking_addresses_for_provided_staking_app(
        self, mocker
    ):
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
        staking_app_id, staking_min_round = STAKING_APP_ID, STAKING_APP_MIN_ROUND
        returned = governance_staking_addresses(
            staking_app_id=staking_app_id, staking_min_round=staking_min_round
        )
        assert isinstance(returned, set)
        assert sorted(list(returned)) == [
            address1,
            address2,
            address3,
            address4,
            address5,
        ]
        mocked_indexer.assert_called_once_with()
        mocked_transaction.assert_called_once_with(
            {
                "application_id": staking_app_id,
                "limit": 1000,
                "min_round": staking_min_round,
            },
            mocked_indexer.return_value,
        )


# # HELPERS
class TestHelpersHelpersFunctions:
    """Testing class for :py:mod:`helpers` helpers functions."""

    # # box_name_from_address
    @pytest.mark.parametrize(
        "address,box_name",
        [
            (
                "2EVGZ4BGOSL3J64UYDE2BUGTNTBZZZLI54VUQQNZZLYCDODLY33UGXNSIU",
                (
                    b"\xd1*l\xf0&t\x97\xb4\xfb\x94\xc0\xc9\xa0\xd0"
                    b"\xd3l\xc3\x9c\xe5h\xef+HA\xb9\xca\xf0!\xb8k\xc6\xf7"
                ),
            ),
            (
                "VW55KZ3NF4GDOWI7IPWLGZDFWNXWKSRD5PETRLDABZVU5XPKRJJRK3CBSU",
                (
                    b"\xad\xbb\xd5gm/\x0c7Y\x1fC\xec\xb3de\xb3oeJ#"
                    b"\xeb\xc98\xac`\x0ekN\xdd\xea\x8aS"
                ),
            ),
            (
                "LXJ3Q6RZ2TJ6VCJDFMSM4ZVNYYYE4KVSL3N2TYR23PLNCJCIXBM3NYTBYE",
                (
                    b"]\xd3\xb8z9\xd4\xd3\xea\x89#+$\xcef\xad\xc60N*"
                    b"\xb2^\xdb\xa9\xe2:\xdb\xd6\xd1$H\xb8Y"
                ),
            ),
            (
                "VKENBO5W2DZAZFQR45SOQO6IMWS5UMVZCHLPEACNOII7BDJTGBZKSEL4Y4",
                (
                    b"\xaa\x88\xd0\xbb\xb6\xd0\xf2\x0c\x96\x11\xe7d"
                    b"\xe8;\xc8e\xa5\xda2\xb9\x11\xd6\xf2\x00Mr\x11\xf0\x8d30r"
                ),
            ),
        ],
    )
    def test_helpers_box_name_from_address_functionality(self, address, box_name):
        returned = box_name_from_address(address)
        assert returned == box_name

    # # box_writing_parameters
    def test_helpers_box_writing_parameters_for_provided_network_suffix(self, mocker):
        mnemonic = "mnemonic1 mnemonic2"
        env = {"creator_mnemonic_testnet": mnemonic, "foo": "bar"}
        network_suffix = "_testnet"
        private_key, sender, signer, contract = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        mocked_private_key = mocker.patch(
            "helpers.private_key_from_mnemonic", return_value=private_key
        )
        mocked_address = mocker.patch(
            "helpers.address_from_private_key", return_value=sender
        )
        mocked_signer = mocker.patch(
            "helpers.AccountTransactionSigner", return_value=signer
        )
        mocked_contract = mocker.patch("helpers.load_contract", return_value=contract)
        returned = box_writing_parameters(env, network_suffix=network_suffix)
        assert returned == {"sender": sender, "signer": signer, "contract": contract}
        mocked_private_key.assert_called_once_with(mnemonic)
        mocked_address.assert_called_once_with(private_key)
        mocked_signer.assert_called_once_with(private_key)
        mocked_contract.assert_called_once_with()

    def test_helpers_box_writing_parameters_functionality(self, mocker):
        mnemonic = "mnemonic1 mnemonic2"
        env = {"creator_mnemonic": mnemonic, "foo": "bar"}
        private_key, sender, signer, contract = (
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )
        mocked_private_key = mocker.patch(
            "helpers.private_key_from_mnemonic", return_value=private_key
        )
        mocked_address = mocker.patch(
            "helpers.address_from_private_key", return_value=sender
        )
        mocked_signer = mocker.patch(
            "helpers.AccountTransactionSigner", return_value=signer
        )
        mocked_contract = mocker.patch("helpers.load_contract", return_value=contract)
        returned = box_writing_parameters(env)
        assert returned == {"sender": sender, "signer": signer, "contract": contract}
        mocked_private_key.assert_called_once_with(mnemonic)
        mocked_address.assert_called_once_with(private_key)
        mocked_signer.assert_called_once_with(private_key)
        mocked_contract.assert_called_once_with()

    # # calculate_votes_and_permission
    def test_helpers_calculate_votes_and_permission_functionality(self):
        values = [0, 0, 1300000, 1400000, 1500000, 1600000, 35000000, 6, 40000000, 202]
        returned = calculate_votes_and_permission(values)
        assert returned == (75, 78000000)

    # # environment_variables
    def test_helpers_environment_variables_functionality(self, mocker):
        (
            creator_mnemonic,
            user_mnemonic,
            algod_token,
            algod_address,
            algod_token_mainnet,
            algod_address_mainnet,
            algod_address_testnet,
            algod_token_testnet,
            creator_mnemonic_testnet,
        ) = (
            mocker.MagicMock(),
            mocker.MagicMock(),
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
                algod_token_mainnet,
                algod_address_mainnet,
                algod_token_testnet,
                algod_address_testnet,
                creator_mnemonic_testnet,
            ],
        ) as mocked_getenv:
            returned = environment_variables()
            assert returned == {
                "creator_mnemonic": creator_mnemonic,
                "user_mnemonic": user_mnemonic,
                "algod_token": algod_token,
                "algod_address": algod_address,
                "algod_token_mainnet": algod_token_mainnet,
                "algod_address_mainnet": algod_address_mainnet,
                "algod_token_testnet": algod_token_testnet,
                "algod_address_testnet": algod_address_testnet,
                "creator_mnemonic_testnet": creator_mnemonic_testnet,
            }
            calls = [
                mocker.call("CREATOR_MNEMONIC"),
                mocker.call("USER_MNEMONIC"),
                mocker.call("ALGOD_TOKEN"),
                mocker.call("ALGOD_ADDRESS"),
                mocker.call("ALGOD_TOKEN_MAINNET"),
                mocker.call("ALGOD_ADDRESS_MAINNET"),
                mocker.call("ALGOD_TOKEN_TESTNET"),
                mocker.call("ALGOD_ADDRESS_TESTNET"),
                mocker.call("CREATOR_MNEMONIC_TESTNET"),
            ]
            mocked_getenv.assert_has_calls(calls, any_order=True)
            assert mocked_getenv.call_count == 9
        mocked_load_dotenv.assert_called_once_with()

    # # pause
    def test_helpers_pause_functionality_for_provided_argument(self):
        seconds = 10
        with mock.patch("helpers.time.sleep") as mocked_sleep:
            pause(seconds)
            mocked_sleep.assert_called_once_with(seconds)

    def test_helpers_pause_default_functionality(self):
        with mock.patch("helpers.time.sleep") as mocked_sleep:
            pause()
            mocked_sleep.assert_called_once_with(1)

    # # permission_for_amount
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
        mocked_key.assert_called_once_with(passphrase)

    # # read_json
    def test_helpers_read_json_returns_empty_dict_for_no_file(self, mocker):
        path = mocker.MagicMock()
        with (
            mock.patch("helpers.os.path.exists", return_value=False) as mocked_exist,
            mock.patch("helpers.open") as mocked_open,
        ):
            assert read_json(path) == {}
            mocked_exist.assert_called_once_with(path)
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
            mocked_open.assert_called_once_with(path, "r")
            mocked_load.assert_called_once_with(
                mocked_open.return_value.__enter__.return_value
            )

    # # wait_for_confirmation
    def test_helpers_wait_for_confirmation_functionality(self, mocker):
        client = mocker.MagicMock()
        txid = "12345"

        # Simulate pending tx then confirmed tx
        client.status.return_value = {"last-round": 1}
        client.pending_transaction_info.side_effect = [
            {"confirmed-round": None},
            {"confirmed-round": 5},
        ]

        returned = wait_for_confirmation(client, txid)

        assert returned == {"confirmed-round": 5}
        client.status.assert_called_once_with()
        assert client.pending_transaction_info.call_count == 2
        client.status_after_block.assert_called_with(2)
