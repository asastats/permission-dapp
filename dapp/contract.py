"""Permission dApp smart contract implemented with Algorand Python (puyapy)."""

from algopy import ARC4Contract, Global, Txn, arc4, op


class PermissionDApp(ARC4Contract):
    """
    A permission-based dApp that allows only the creator to manage boxes.
    """

    def __init__(self) -> None:
        """Initialize the contract state."""
        pass

    @arc4.baremethod(allow_actions=["NoOp"], create="require")
    def create_application(self) -> None:
        """
        Handles the application creation.
        This method is called only once, when the contract is deployed.
        """
        # No state initialization needed for this contract
        pass

    @arc4.baremethod(allow_actions=["UpdateApplication"])
    def update_application(self) -> None:
        """
        Allows only the creator to update the application.
        """
        assert (
            Txn.sender == Global.creator_address
        ), "Only creator can update application"

    @arc4.baremethod(allow_actions=["DeleteApplication"])
    def delete_application(self) -> None:
        """
        Allows only the creator to delete the application.
        """
        assert (
            Txn.sender == Global.creator_address
        ), "Only creator can delete application"

    @arc4.abimethod
    def write_box(self, box_name: arc4.DynamicBytes, value: arc4.String) -> None:
        """
        Write a value to a box. Only the creator can call this method.

        Args:
            box_name: The name of the box (should be 32 bytes)
            value: The string value to write to the box
        """
        assert Txn.sender == Global.creator_address, "Only creator can write to boxes"

        # Convert arc4 types to bytes for box operations
        box_name_bytes = box_name.bytes
        value_bytes = value.bytes

        # For DynamicBytes, the .bytes includes the length prefix, so we need to extract the actual content
        # The first 2 bytes are the length prefix in big-endian
        actual_box_name_length = op.extract_uint16(box_name_bytes, 0)
        actual_box_name = op.extract(box_name_bytes, 2, actual_box_name_length)

        # For String, the .bytes also includes the length prefix
        actual_value_length = op.extract_uint16(value_bytes, 0)
        actual_value = op.extract(value_bytes, 2, actual_value_length)

        assert actual_box_name_length == 32, "Box name must be exactly 32 bytes"

        # Simple approach: always delete the box first if it exists, then create it
        # This avoids the length comparison issue
        box_exists = op.Box.length(actual_box_name)
        if box_exists:
            op.Box.delete(actual_box_name)

        # Write to box (create new box)
        op.Box.put(actual_box_name, actual_value)

    @arc4.abimethod
    def delete_box(self, box_name: arc4.DynamicBytes) -> None:
        """
        Delete a box. Only the creator can call this method.

        Args:
            box_name: The name of the box to delete (should be 32 bytes)
        """
        assert Txn.sender == Global.creator_address, "Only creator can delete boxes"

        # Convert arc4 type to bytes for box operations
        box_name_bytes = box_name.bytes

        # Extract the actual box name from the ARC4 encoded bytes
        actual_box_name_length = op.extract_uint16(box_name_bytes, 0)
        actual_box_name = op.extract(box_name_bytes, 2, actual_box_name_length)

        assert actual_box_name_length == 32, "Box name must be exactly 32 bytes"

        # Delete the box
        op.Box.delete(actual_box_name)
