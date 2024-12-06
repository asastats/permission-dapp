"""Testing module for :py:mod:`permission_dapp` module."""

from pyteal import ABIReturnSubroutine, CallConfig, Router, SubroutineFnWrapper, abi

from permission_dapp import assert_sender_is_creator, deleteBox, router, writeBox


class TestPermissionDappFunctions:
    """Testing class for :py:mod:`permission_dapp` functions."""

    # # assert_sender_is_creator
    def test_permission_dapp_assert_sender_is_creator_is_subroutine_wrapper(self):
        assert isinstance(assert_sender_is_creator, SubroutineFnWrapper)

    # # router
    def test_permission_dapp_router_is_router_instance(self):
        assert isinstance(router, Router)

    def test_permission_dapp_router_name(self):
        assert router.name == "Permission dApp"

    def test_permission_dapp_router_no_op_is_create_only(self):
        assert int(router.bare_call_actions.no_op.call_config) == int(CallConfig.CREATE)

    def test_permission_dapp_router_update_application_requires_creator(self):
        assert (
            router.bare_call_actions.update_application.action.subroutine._SubroutineDefinition__name
            == "assert_sender_is_creator"
        )

    def test_permission_dapp_router_delete_requires_creator(self):
        assert (
            router.bare_call_actions.delete_application.action.subroutine._SubroutineDefinition__name
            == "assert_sender_is_creator"
        )

    def test_permission_dapp_router_methods(self):
        assert len(router.methods) == 2
        assert router.methods[0].name == "writeBox"
        assert router.methods[1].name == "deleteBox"

    # # writeBox
    def test_permission_dapp_writebox_is_subroutine(self):
        assert isinstance(writeBox, ABIReturnSubroutine)

    def test_permission_dapp_writebox_arguments(self):
        assert len(writeBox.subroutine.abi_args) == 2
        assert isinstance(writeBox.subroutine.abi_args["box_name"], abi.StringTypeSpec)
        assert isinstance(writeBox.subroutine.abi_args["value"], abi.StringTypeSpec)

    # # deleteBox
    def test_permission_dapp_deletebox_is_subroutine(self):
        assert isinstance(deleteBox, ABIReturnSubroutine)

    def test_permission_dapp_deletebox_arguments(self):
        assert len(deleteBox.subroutine.abi_args) == 1
        assert isinstance(deleteBox.subroutine.abi_args["box_name"], abi.StringTypeSpec)
