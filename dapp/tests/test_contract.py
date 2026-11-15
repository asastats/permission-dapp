"""Testing module for :py:mod:`contract` module."""

from collections.abc import Generator

import algopy
import pytest
from algopy import arc4
from algopy_testing import AlgopyTestContext, algopy_testing_context

from contract import PermissionDApp
from helpers import serialize_values


def _app(context: AlgopyTestContext, contract: PermissionDApp):
    """Get the ledger app object for a contract."""
    return context.ledger.get_app(contract)


@pytest.fixture()
def context() -> Generator[AlgopyTestContext, None, None]:
    """Fixture to provide a testing context."""
    with algopy_testing_context() as ctx:
        yield ctx


class TestPermissionDApp:
    """Testing class for PermissionDApp contract."""

    # create_application
    def test_permission_dapp_create_application(
        self, context: AlgopyTestContext
    ) -> None:
        creator = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()
            app = _app(context, contract)

        # Sanity check: app object exists
        assert app.id > 0

    # update_application
    def test_permission_dapp_update_application_by_creator(
        self, context: AlgopyTestContext
    ) -> None:
        creator = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        # Update by creator should succeed
        with context.txn.create_group(
            active_txn_overrides={
                "on_completion": algopy.OnCompleteAction.UpdateApplication,
                "sender": creator,
            }
        ):
            contract.update_application()

        # If no exception was raised, the test passes

    def test_permission_dapp_update_application_fails_for_non_creator(
        self, context: AlgopyTestContext
    ) -> None:
        creator = context.any.account()
        non_creator = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        with pytest.raises(AssertionError, match="Only creator can update application"):
            with context.txn.create_group(
                active_txn_overrides={
                    "on_completion": algopy.OnCompleteAction.UpdateApplication,
                    "sender": non_creator,
                }
            ):
                contract.update_application()

    # delete_application
    def test_permission_dapp_delete_application_by_creator(
        self, context: AlgopyTestContext
    ) -> None:
        creator = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        # Delete by creator should succeed
        with context.txn.create_group(
            active_txn_overrides={
                "on_completion": algopy.OnCompleteAction.DeleteApplication,
                "sender": creator,
            }
        ):
            contract.delete_application()

        # If no exception was raised, the test passes

    def test_permission_dapp_delete_application_fails_for_non_creator(
        self, context: AlgopyTestContext
    ) -> None:
        creator = context.any.account()
        non_creator = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        with pytest.raises(AssertionError, match="Only creator can delete application"):
            with context.txn.create_group(
                active_txn_overrides={
                    "on_completion": algopy.OnCompleteAction.DeleteApplication,
                    "sender": non_creator,
                }
            ):
                contract.delete_application()

    # write_box
    def test_permission_dapp_write_box_by_creator(
        self, context: AlgopyTestContext
    ) -> None:
        creator = context.default_sender

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        app = _app(context, contract)
        box_name = context.any.bytes(32)  # 32 bytes for box name
        value = "test_value"  # Use a short string to avoid ARC4 encoding issues

        # Write box by creator should succeed
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.write_box(
                arc4.DynamicBytes(box_name),
                arc4.String(value),
            )

        # Verify the box was written
        box_content = context.ledger.get_box(app.id, box_name)
        assert box_content == value.encode("utf-8")

    def test_permission_dapp_write_box_fails_for_non_creator(
        self, context: AlgopyTestContext
    ) -> None:
        creator = context.any.account()
        non_creator = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        box_name = context.any.bytes(32)
        value = "test_value"

        with pytest.raises(AssertionError, match="Only creator can write to boxes"):
            with context.txn.create_group(active_txn_overrides={"sender": non_creator}):
                contract.write_box(
                    arc4.DynamicBytes(box_name),
                    arc4.String(value),
                )

    def test_permission_dapp_write_box_fails_for_wrong_box_size(
        self, context: AlgopyTestContext
    ) -> None:
        creator = context.default_sender

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        # Test with box name that's not 32 bytes
        box_name_wrong_size = context.any.bytes(16)  # 16 bytes instead of 32
        value = "test_value"

        with pytest.raises(AssertionError, match="Box name must be exactly 32 bytes"):
            with context.txn.create_group(active_txn_overrides={"sender": creator}):
                contract.write_box(
                    arc4.DynamicBytes(box_name_wrong_size),
                    arc4.String(value),
                )

    def test_permission_dapp_write_box_overwrites_existing(
        self, context: AlgopyTestContext
    ) -> None:
        creator = context.default_sender

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        app = _app(context, contract)
        box_name = context.any.bytes(32)
        value1 = "first_value"
        value2 = "second_value"

        # Write first value
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.write_box(
                arc4.DynamicBytes(box_name),
                arc4.String(value1),
            )

        # Verify first value was written
        box_content = context.ledger.get_box(app.id, box_name)
        assert box_content == value1.encode("utf-8")

        # Write second value (overwrite)
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.write_box(
                arc4.DynamicBytes(box_name),
                arc4.String(value2),
            )

        # Verify second value overwrote the first
        box_content = context.ledger.get_box(app.id, box_name)
        assert box_content == value2.encode("utf-8")

    def test_permission_dapp_write_box_creates_new_box(
        self, context: AlgopyTestContext
    ) -> None:
        """Test that write_box creates a new box if it doesn't exist."""
        creator = context.default_sender

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        app = _app(context, contract)
        box_name = context.any.bytes(32)
        value = "new_box_value"

        # Verify the box does not exist initially
        box_content = context.ledger.get_box(app.id, box_name)
        assert box_content in (None, b"", bytearray())

        # Write to the new box
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.write_box(
                arc4.DynamicBytes(box_name),
                arc4.String(value),
            )

        # Verify the box was created with the correct content
        box_content = context.ledger.get_box(app.id, box_name)
        assert box_content == value.encode("utf-8")

    # delete_box
    def test_permission_dapp_delete_box_by_creator(
        self, context: AlgopyTestContext
    ) -> None:
        creator = context.default_sender

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        app = _app(context, contract)
        box_name = context.any.bytes(32)
        value = "test_value"

        # First write a box
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.write_box(
                arc4.DynamicBytes(box_name),
                arc4.String(value),
            )

        # Verify the box exists
        box_content = context.ledger.get_box(app.id, box_name)
        assert box_content == value.encode("utf-8")

        # Delete the box
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.delete_box(arc4.DynamicBytes(box_name))

        # Verify the box was deleted
        box_content = context.ledger.get_box(app.id, box_name)
        assert box_content in (None, b"", bytearray())

    def test_permission_dapp_delete_box_fails_for_non_creator(
        self, context: AlgopyTestContext
    ) -> None:
        creator = context.any.account()
        non_creator = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        box_name = context.any.bytes(32)
        value = "test_value"

        # First write a box (by creator)
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.write_box(
                arc4.DynamicBytes(box_name),
                arc4.String(value),
            )

        # Try to delete by non-creator
        with pytest.raises(AssertionError, match="Only creator can delete boxes"):
            with context.txn.create_group(active_txn_overrides={"sender": non_creator}):
                contract.delete_box(arc4.DynamicBytes(box_name))

    def test_permission_dapp_delete_box_fails_for_wrong_box_size(
        self, context: AlgopyTestContext
    ) -> None:
        creator = context.default_sender

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        # Test with box name that's not 32 bytes
        box_name_wrong_size = context.any.bytes(16)

        with pytest.raises(AssertionError, match="Box name must be exactly 32 bytes"):
            with context.txn.create_group(active_txn_overrides={"sender": creator}):
                contract.delete_box(arc4.DynamicBytes(box_name_wrong_size))

    def test_permission_dapp_delete_nonexistent_box(
        self, context: AlgopyTestContext
    ) -> None:
        creator = context.default_sender

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        box_name = context.any.bytes(32)

        # Try to delete a box that doesn't exist
        # This should succeed (box deletion is idempotent in Algorand)
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.delete_box(arc4.DynamicBytes(box_name))

        # If no exception was raised, the test passes

    def test_permission_dapp_multiple_boxes_operations(
        self, context: AlgopyTestContext
    ) -> None:
        creator = context.default_sender

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        app = _app(context, contract)

        # Create multiple boxes
        box1_name = context.any.bytes(32)
        box1_value = "value1"
        box2_name = context.any.bytes(32)
        box2_value = "value2"

        # Write first box
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.write_box(
                arc4.DynamicBytes(box1_name),
                arc4.String(box1_value),
            )

        # Write second box
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.write_box(
                arc4.DynamicBytes(box2_name),
                arc4.String(box2_value),
            )

        # Verify both boxes exist with correct values
        box1_content = context.ledger.get_box(app.id, box1_name)
        box2_content = context.ledger.get_box(app.id, box2_name)

        assert box1_content == box1_value.encode("utf-8")
        assert box2_content == box2_value.encode("utf-8")

        # Delete first box
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.delete_box(arc4.DynamicBytes(box1_name))

        # Verify first box is gone, second box still exists
        box1_content = context.ledger.get_box(app.id, box1_name)
        box2_content = context.ledger.get_box(app.id, box2_name)

        assert box1_content in (None, b"", bytearray())
        assert box2_content == box2_value.encode("utf-8")

    def test_permission_dapp_write_box_with_empty_string(
        self, context: AlgopyTestContext
    ) -> None:
        """Test writing an empty string to a box."""
        creator = context.default_sender

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        app = _app(context, contract)
        box_name = context.any.bytes(32)
        value = ""  # Empty string

        # Write empty string to box
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.write_box(
                arc4.DynamicBytes(box_name),
                arc4.String(value),
            )

        # Verify the box was written with empty content
        box_content = context.ledger.get_box(app.id, box_name)
        assert box_content == b""

    def test_permission_dapp_write_box_with_unicode_string(
        self, context: AlgopyTestContext
    ) -> None:
        """Test writing a unicode string to a box."""
        creator = context.default_sender

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        app = _app(context, contract)
        box_name = context.any.bytes(32)
        value = "Hello 世界 🌍"  # Unicode string

        # Write unicode string to box
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.write_box(
                arc4.DynamicBytes(box_name),
                arc4.String(value),
            )

        # Verify the box was written with correct content
        box_content = context.ledger.get_box(app.id, box_name)
        assert box_content == value.encode("utf-8")

    def test_permission_dapp_write_box_overwrites_with_different_size(
        self, context: AlgopyTestContext
    ) -> None:
        """Test that write_box correctly overwrites an existing box with a value of a different size."""
        creator = context.default_sender

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        app = _app(context, contract)
        box_name = context.any.bytes(32)
        value1 = "short_value"  # Original value
        value2 = "a_much_longer_value_that_is_different_in_size"  # New value with different size

        # Write first value
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.write_box(
                arc4.DynamicBytes(box_name),
                arc4.String(value1),
            )

        # Verify first value was written
        box_content = context.ledger.get_box(app.id, box_name)
        assert box_content == value1.encode("utf-8")

        # Write second value (overwrite with different size)
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.write_box(
                arc4.DynamicBytes(box_name),
                arc4.String(value2),
            )

        # Verify second value overwrote the first and has the new size
        box_content = context.ledger.get_box(app.id, box_name)
        assert box_content == value2.encode("utf-8")

    # votes_of
    def _contract_with_box(self, context, box_name, value):
        creator = context.default_sender
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDApp()
            contract.create_application()

        if value is not None:
            with context.txn.create_group(active_txn_overrides={"sender": creator}):
                contract.write_box(arc4.DynamicBytes(box_name), arc4.String(value))

        return contract

    def test_permission_dapp_votes_of_returns_votes_from_box(
        self, context: AlgopyTestContext
    ) -> None:
        box_name = context.any.bytes(32)
        values = [1_234_567, 99, 0, 0, 0, 0, 5_000_000, 1]
        contract = self._contract_with_box(context, box_name, serialize_values(values))

        with context.txn.create_group(
            active_txn_overrides={"sender": context.any.account()}
        ):
            returned = contract.votes_of(arc4.Address(box_name))

        assert returned.native == 1_234_567

    def test_permission_dapp_votes_of_returns_zero_for_missing_box(
        self, context: AlgopyTestContext
    ) -> None:
        contract = self._contract_with_box(context, context.any.bytes(32), None)

        returned = contract.votes_of(arc4.Address(context.any.bytes(32)))

        assert returned.native == 0

    def test_permission_dapp_votes_of_fails_for_short_box(
        self, context: AlgopyTestContext
    ) -> None:
        box_name = context.any.bytes(32)
        contract = self._contract_with_box(context, box_name, "AAAAAAA=")

        with pytest.raises(Exception):
            contract.votes_of(arc4.Address(box_name))
