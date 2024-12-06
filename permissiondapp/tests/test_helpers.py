"""Testing module for :py:mod:`helpers` module."""

import pytest

from permissiondapp.helpers import (
    _value_length_from_values_position,
    deserialize_values_data,
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
                1400,
                4,
                1500,
                5,
                1600,
                6,
                1700,
                7,
                1800,
                8,
                1900,
                9,
                2000,
                10,
                2010,
                11,
                2020,
                12,
            ],
            "AAAAAACYloAAAAAAC+vCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB6GdAAAAAAAH1wgAAAAAAA"
            "AA+gBAAAAAAAABEwCAAAAAAAABLADAAAAAAAABXgEAAAAAAAABdwFAAAAAAAABkAGAAAAAA"
            "AABqQHAAAAAAAABwgIAAAAAAAAB2wJAAAAAAAAB9AKAAAAAAAAB9oLAAAAAAAAB+QM",
        ),
    ]


# # VALUES
class TestHelpersValuesFunctions:
    """Testing class for :py:mod:`helpers` values functions."""

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
