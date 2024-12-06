"""Testing module for :py:mod:`helpers` module."""

import pytest

from permissiondapp.helpers import serialize_values

# # VALUES
class TestHelpersValuesFunctions:
    """Testing class for :py:mod:`helpers` values functions."""

    # # serialize_values
    @pytest.mark.parametrize(
        "values,result",
        [
            ([1,2,3,4,5,6,7,8,9,10], ""),
            # ([1,2,3,4,5,6,7,8,9,10], ""),
            # ([1,2,3,4,5,6,7,8,9,10], ""),
            # ([1,2,3,4,5,6,7,8,9,10], ""),
            # ([1,2,3,4,5,6,7,8,9,10], ""),
        ],
    )
    def test_helpers_serialize_values_functionality(self, values, result):
        returned = serialize_values(values)
        assert returned == result
