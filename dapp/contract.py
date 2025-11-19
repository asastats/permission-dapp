"""Permission dApp smart contract implemented with Algorand Python (puyapy)."""

from algopy import Global, Txn, Bytes, Box, arc4, subroutine


@subroutine
def assert_sender_is_creator() -> None:
    assert Txn.sender == Global.creator_address, "Sender must be creator"


class PermissionDapp(arc4.ARC4Contract):
    """
    Permissioned box storage:
      - Only the creator may write or delete boxes.
      - Box name = Algorand address (32 raw bytes).
      - Box contents = arbitrary string.
    """

    @arc4.baremethod(create="require", allow_actions=["NoOp"])
    def create_application(self) -> None:
        return

    @arc4.baremethod(allow_actions=["UpdateApplication"])
    def update_application(self) -> None:
        assert_sender_is_creator()

    @arc4.baremethod(allow_actions=["DeleteApplication"])
    def delete_application(self) -> None:
        assert_sender_is_creator()

    # ----------------------------------------------------------------------
    #  writeBox
    # ----------------------------------------------------------------------
    @arc4.abimethod(name="writeBox")
    def write_box(self, box_name: arc4.StaticBytes[arc4.Literal[32]], value: arc4.DynamicBytes) -> None:
        assert_sender_is_creator()

        key: Bytes = box_name.bytes
        assert len(key) == 32

        raw_value: Bytes = value.bytes  # already raw UTF-8 bytes

        box = Box(Bytes, key=key)
        box.value = raw_value

    # ----------------------------------------------------------------------
    #  deleteBox
    # ----------------------------------------------------------------------
    @arc4.abimethod(name="deleteBox")
    def delete_box(self, box_name: arc4.Address) -> None:
        """
        Deletes a box keyed by the raw 32-byte address.
        """
        assert_sender_is_creator()

        key: Bytes = box_name.bytes

        assert len(key) == 32, "Box name must be 32 bytes"

        box = Box(Bytes, key=key)
        _, exists = box.maybe()
        assert exists, "Box does not exist"

        del box.value
