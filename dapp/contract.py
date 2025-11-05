"""Permission dApp smart contract module."""

from typing import Literal

from pyteal import (
    App,
    Approve,
    Assert,
    BareCallActions,
    CallConfig,
    Expr,
    Global,
    OnCompleteAction,
    Router,
    Seq,
    Subroutine,
    Txn,
    abi,
)
from pyteal.types import TealType


@Subroutine(TealType.none)
def assert_sender_is_creator() -> Expr:
    return Assert(Txn.sender() == Global.creator_address())


router = Router(
    "Permission dApp",
    BareCallActions(
        no_op=OnCompleteAction.create_only(Approve()),
        update_application=OnCompleteAction(
            action=assert_sender_is_creator, call_config=CallConfig.CALL
        ),
        delete_application=OnCompleteAction(
            action=assert_sender_is_creator, call_config=CallConfig.CALL
        ),
    ),
)


## WRITE
@router.method
def writeBox(box_name: abi.StaticBytes[Literal[32]], value: abi.String):
    return Seq(
        assert_sender_is_creator(),
        App.box_put(box_name.get(), value.get()),
    )


## DELETE
@router.method
def deleteBox(box_name: abi.StaticBytes[Literal[32]]):
    return Seq(
        assert_sender_is_creator(),
        Assert(App.box_delete(box_name.get())),
    )


if __name__ == "__main__":
    import os
    import json

    path = os.path.dirname(os.path.abspath(__file__))
    approval, clear, contract = router.compile_program(version=8)

    # Dump out the contract as json that can be read in by any of the SDKs
    with open(os.path.join(path, "artifacts/contract.json"), "w") as f:
        f.write(json.dumps(contract.dictify(), indent=2))

    # Write out the approval and clear programs
    with open(os.path.join(path, "artifacts/approval.teal"), "w") as f:
        f.write(approval)

    with open(os.path.join(path, "artifacts/clear.teal"), "w") as f:
        f.write(clear)
