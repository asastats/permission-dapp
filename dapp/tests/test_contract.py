"""Testing module for :py:mod:`contract` module."""

import pytest
import algopy
from algopy import arc4
from algopy_testing import AlgopyTestContext, algopy_testing_context

from contract import PermissionDapp


def _app(context: AlgopyTestContext, contract: PermissionDapp):
    """Get the ledger's App instance for this deployed ARC4 contract."""
    return context.ledger.get_app(contract)


@pytest.fixture()
def context():
    with algopy_testing_context() as ctx:
        yield ctx


class TestPermissionDapp:
    # ----------------------------------------------------------------------
    #  create_application
    # ----------------------------------------------------------------------

    def test_create_application(self, context):
        creator = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDapp()
            contract.create_application()
            app = _app(context, contract)

        assert app.id > 0, "Application should be created"

    # ----------------------------------------------------------------------
    #  update_application
    # ----------------------------------------------------------------------

    def test_update_application_succeeds_for_creator(self, context):
        creator = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDapp()
            contract.create_application()
            _ = _app(context, contract)

        with context.txn.create_group(
            active_txn_overrides={
                "sender": creator,
                "on_completion": algopy.OnCompleteAction.UpdateApplication,
            }
        ):
            contract.update_application()

    def test_update_application_fails_for_non_creator(self, context):
        creator = context.any.account()
        non_creator = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDapp()
            contract.create_application()

        with pytest.raises(AssertionError, match="Sender must be creator"):
            with context.txn.create_group(
                active_txn_overrides={
                    "sender": non_creator,
                    "on_completion": algopy.OnCompleteAction.UpdateApplication,
                }
            ):
                contract.update_application()

    # ----------------------------------------------------------------------
    #  delete_application
    # ----------------------------------------------------------------------

    def test_delete_application_succeeds_for_creator(self, context):
        creator = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDapp()
            contract.create_application()
            _ = _app(context, contract)

        with context.txn.create_group(
            active_txn_overrides={
                "sender": creator,
                "on_completion": algopy.OnCompleteAction.DeleteApplication,
            }
        ):
            contract.delete_application()

    def test_delete_application_fails_for_non_creator(self, context):
        creator = context.any.account()
        non_creator = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDapp()
            contract.create_application()

        with pytest.raises(AssertionError, match="Sender must be creator"):
            with context.txn.create_group(
                active_txn_overrides={
                    "sender": non_creator,
                    "on_completion": algopy.OnCompleteAction.DeleteApplication,
                }
            ):
                contract.delete_application()

    # ----------------------------------------------------------------------
    #  writeBox
    # ----------------------------------------------------------------------

    def test_write_box_succeeds(self, context):
        creator = context.any.account()
        target = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDapp()
            contract.create_application()
            app = _app(context, contract)

        val = "hello world"

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.write_box(
                arc4.Address(target.bytes),
                arc4.String(val),
            )

        raw = context.ledger.get_box(app.id, target.bytes)
        assert raw == val.encode(), "Box should contain value"

    def test_write_box_fails_for_non_creator(self, context):
        creator = context.any.account()
        non_creator = context.any.account()
        target = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDapp()
            contract.create_application()

        with pytest.raises(AssertionError, match="Sender must be creator"):
            with context.txn.create_group(active_txn_overrides={"sender": non_creator}):
                contract.write_box(
                    arc4.Address(target.bytes),
                    arc4.String("value"),
                )

    def test_write_box_fails_for_invalid_key_type(self, context):
        creator = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDapp()
            contract.create_application()

        bad_key = b"too short"

        with pytest.raises(Exception):
            arc4.Address(bad_key)

    # ----------------------------------------------------------------------
    #  deleteBox
    # ----------------------------------------------------------------------

    def test_delete_box_succeeds(self, context):
        creator = context.any.account()
        target = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDapp()
            contract.create_application()
            app = _app(context, contract)

        # Create box
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.write_box(
                arc4.Address(target.bytes),
                arc4.String("to delete"),
            )

        assert context.ledger.get_box(app.id, target.bytes) is not None

        # Delete box
        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract.delete_box(arc4.Address(target.bytes))

        raw = context.ledger.get_box(app.id, target.bytes)
        assert raw in (None, b"", bytearray()), "Box should be deleted"

    def test_delete_box_fails_for_non_creator(self, context):
        creator = context.any.account()
        non_creator = context.any.account()
        target = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDapp()
            contract.create_application()

        with pytest.raises(AssertionError, match="Sender must be creator"):
            with context.txn.create_group(active_txn_overrides={"sender": non_creator}):
                contract.delete_box(arc4.Address(target.bytes))

    def test_delete_box_fails_when_missing(self, context):
        creator = context.any.account()
        target = context.any.account()

        with context.txn.create_group(active_txn_overrides={"sender": creator}):
            contract = PermissionDapp()
            contract.create_application()

        with pytest.raises(AssertionError, match="Box does not exist"):
            with context.txn.create_group(active_txn_overrides={"sender": creator}):
                contract.delete_box(arc4.Address(target.bytes))
