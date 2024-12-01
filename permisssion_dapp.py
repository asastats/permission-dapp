# from pyteal import *

from pyteal import (
    App,
    Approve,
    Assert,
    BareCallActions,
    CallConfig,
    Expr,
    Global,
    Int,
    OnCompleteAction,
    Router,
    Seq,
    Subroutine,
    Txn,
    abi,
)
from pyteal.types import TealType

ACCOUNT_STATE_SIZE = 32

# # convert 64 bit integer i to byte string
# def intToBytes(i):
#     return i.to_bytes(8, "big")


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


## CREATE
@router.method
def createBox(box_name: abi.String):
    return Seq(
        assert_sender_is_creator(),
        Assert(App.box_create(box_name.get(), Int(ACCOUNT_STATE_SIZE))),
    )


@router.method
def createBoxWithPut(box_name: abi.String, box_value: abi.String):
    return Seq(
        assert_sender_is_creator(),
        App.box_put(box_name.get(), box_value.get()),
    )


## WRITE
@router.method
def replaceBox(box_name: abi.String, new_name: abi.String):
    return Seq(
        assert_sender_is_creator(),
        App.box_replace(box_name.get(), Int(0), new_name.get()),
    )


@router.method
def writeBox(box_name: abi.String, new_name: abi.String):
    return Seq(
        assert_sender_is_creator(),
        App.box_put(box_name.get(), new_name.get()),
    )


## READ
@router.method
def extractBox(
    box_name: abi.String, start: abi.Uint8, end: abi.Uint8, *, output: abi.String
):
    return output.set(App.box_extract(box_name.get(), start.get(), end.get()))


@router.method
def getBox(box_name: abi.String, *, output: abi.String):
    return Seq(
        contents := App.box_get(box_name.get()),
        Assert(contents.hasValue()),
        output.set(contents.value()),
    )


## DELETE
@router.method
def deleteBox(box_name: abi.String):
    return Seq(
        assert_sender_is_creator(),
        Assert(App.box_delete(box_name.get())),
    )


## BOX SIZE
@router.method
def getBoxSize(box_name: abi.String, *, output: abi.Uint64):
    return Seq(
        length := App.box_length(box_name.get()),
        Assert(length.hasValue()),
        output.set(length.value()),
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
