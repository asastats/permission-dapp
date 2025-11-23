"""Module with integration tests for the Permission dApp smart contract."""

import base64
import json
import time
from pathlib import Path

import pytest
from algokit_utils import (
    AlgoAmount,
    AlgorandClient,
    AppClientMethodCallParams,
    Arc56Contract,
    LogicError,
    PaymentParams,
    SigningAccount,
)
from algokit_utils.applications import AppClient, AppClientParams
from algosdk.account import generate_account
from algosdk.error import AlgodHTTPError
from algosdk.transaction import ApplicationDeleteTxn, ApplicationUpdateTxn
from dotenv import load_dotenv

from contract import PermissionDApp
from helpers import compile_program, wait_for_confirmation
from network import box_name_from_address, create_app

load_dotenv(Path(__file__).parent.parent / ".env")

# Assume tests are run from the project root
CONTRACT_PATH = Path(__file__).parent.parent / "artifacts"
APP_SPEC_PATH = CONTRACT_PATH / f"{PermissionDApp._name}.arc56.json"

TEST_ADDRESS = "2EVGZ4BGOSL3J64UYDE2BUGTNTBZZZLI54VUQQNZZLYCDODLY33UGXNSIU"


@pytest.fixture(scope="session")
def app_spec() -> Arc56Contract:
    """Get the application specification from the compiled artifact."""
    spec = json.loads(APP_SPEC_PATH.read_text())
    for network in spec["networks"].values():
        if "appID" in network:
            network["appId"] = network.pop("appID")
    return Arc56Contract.from_dict(spec)


class BaseTestContract:
    """Base testing class for :class:`contract.contract.PermissionDApp`."""

    name = "permission_dapp"

    @pytest.fixture(autouse=True)
    def _setup_contract(
        self,
        algorand_client: AlgorandClient,
        app_spec: Arc56Contract,
        creator_account: SigningAccount,
    ):
        """
        Deploy app using app_spec + your own TEAL compile logic.
        """

        algod = algorand_client.client.algod

        # --------------------------------------------------------------------
        # ✅ Extract name from app_spec (this matches *.approval.teal filenames)
        # --------------------------------------------------------------------
        dapp_name = app_spec.name

        artifacts_path = Path(__file__).resolve().parent.parent / "artifacts"

        approval_teal_path = artifacts_path / f"{dapp_name}.approval.teal"
        clear_teal_path = artifacts_path / f"{dapp_name}.clear.teal"

        # --------------------------------------------------------------------
        # ✅ Load TEAL source from artifacts (using your logic)
        # --------------------------------------------------------------------
        approval_program_source = approval_teal_path.read_bytes()
        clear_program_source = clear_teal_path.read_bytes()

        # --------------------------------------------------------------------
        # ✅ Compile using your compile_program()
        # --------------------------------------------------------------------
        approval_program = compile_program(algod, approval_program_source)
        clear_program = compile_program(algod, clear_program_source)

        # --------------------------------------------------------------------
        # ✅ app_spec → ARC56 JSON (your create_app expects dict)
        # --------------------------------------------------------------------
        contract_json = json.loads(app_spec.to_json())

        # --------------------------------------------------------------------
        # ✅ Create the app using your create_app() function
        #    This triggers @baremethod(create="require")
        # --------------------------------------------------------------------
        app_id, _gh = create_app(
            client=algod,
            private_key=creator_account.private_key,
            approval_program=approval_program,
            clear_program=clear_program,
            contract_json=contract_json,
        )

        # --------------------------------------------------------------------
        # ✅ Wrap in AppClient for ABI calls
        # --------------------------------------------------------------------
        permission_client = AppClient(
            AppClientParams(
                algorand=algorand_client,
                app_spec=app_spec,
                app_id=app_id,
            )
        )

        # --------------------------------------------------------------------
        # ✅ Fund the contract account for box operations
        # --------------------------------------------------------------------
        algorand_client.send.payment(
            PaymentParams(
                sender=creator_account.address,
                receiver=permission_client.app_address,
                amount=AlgoAmount(algo=2),  # More ALGO for box operations
                signer=creator_account.signer,
            )
        )

        # Expose for tests (test methods can now reference self.permission_client)
        self.permission_client = permission_client
        self.approval_program = approval_program
        self.clear_program = clear_program

    @pytest.fixture
    def algorand_client(self) -> AlgorandClient:
        return AlgorandClient.from_environment()

    @pytest.fixture
    def creator_account(self, algorand_client: AlgorandClient) -> SigningAccount:
        return algorand_client.account.from_environment(
            "CREATOR_ACCOUNT" + "_" + self.name.upper(), fund_with=AlgoAmount(algo=1000)
        )

    @pytest.fixture
    def user_account(self, algorand_client: AlgorandClient) -> SigningAccount:
        return algorand_client.account.from_environment(
            "USER_ACCOUNT" + "_" + self.name.upper(),
            fund_with=AlgoAmount(algo=10),
        )

    @pytest.fixture
    def other_account(self, algorand_client: AlgorandClient) -> SigningAccount:
        return algorand_client.account.from_environment(
            "OTHER_ACCOUNT" + "_" + self.name.upper(),
            fund_with=AlgoAmount(algo=10),
        )


class TestContractLifecycle(BaseTestContract):
    """Testing class for :class:`contract.contract.PermissionDApp` lifecycle methods."""

    name = "lifecycle"

    def test_contract_permission_dapp_create_application(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test that application creation succeeds."""
        # Application creation happens in fixture setup
        # If we reach this point without errors, creation was successful
        assert self.permission_client.app_id > 0

    def test_contract_permission_dapp_update_application_by_creator(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test that creator can update the application."""
        # Update by creator should succeed
        algod = self.permission_client.algorand.client.algod
        params = algod.suggested_params()

        update_txn = ApplicationUpdateTxn(
            sender=creator_account.address,
            sp=params,
            index=self.permission_client.app_id,
            approval_program=self.approval_program,
            clear_program=self.clear_program,
        )

        signed_txn = update_txn.sign(creator_account.private_key)
        tx_id = algod.send_transaction(signed_txn)

        # Wait for confirmation
        wait_for_confirmation(algod, tx_id)

        # If no exception was raised, update succeeded

    def test_contract_permission_dapp_update_application_fails_for_non_creator(
        self,
        user_account: SigningAccount,
    ) -> None:
        """Test that non-creator cannot update the application."""
        algod = self.permission_client.algorand.client.algod
        params = algod.suggested_params()

        update_txn = ApplicationUpdateTxn(
            sender=user_account.address,
            sp=params,
            index=self.permission_client.app_id,
            approval_program=self.approval_program,
            clear_program=self.clear_program,
        )

        signed_txn = update_txn.sign(user_account.private_key)

        with pytest.raises(Exception):  # Could be various error types
            tx_id = algod.send_transaction(signed_txn)
            wait_for_confirmation(algod, tx_id)

    def test_contract_permission_dapp_delete_application_by_creator(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test that creator can delete the application."""
        algod = self.permission_client.algorand.client.algod
        params = algod.suggested_params()

        delete_txn = ApplicationDeleteTxn(
            sender=creator_account.address,
            sp=params,
            index=self.permission_client.app_id,
        )

        signed_txn = delete_txn.sign(creator_account.private_key)
        tx_id = algod.send_transaction(signed_txn)

        # Wait for confirmation
        wait_for_confirmation(algod, tx_id)

        # Verify app is deleted
        with pytest.raises(AlgodHTTPError, match="application does not exist"):
            algod.application_info(self.permission_client.app_id)

    def test_contract_permission_dapp_delete_application_fails_for_non_creator(
        self,
        user_account: SigningAccount,
    ) -> None:
        """Test that non-creator cannot delete the application."""
        algod = self.permission_client.algorand.client.algod
        params = algod.suggested_params()

        delete_txn = ApplicationDeleteTxn(
            sender=user_account.address,
            sp=params,
            index=self.permission_client.app_id,
        )

        signed_txn = delete_txn.sign(user_account.private_key)

        with pytest.raises(Exception):  # Could be various error types
            tx_id = algod.send_transaction(signed_txn)
            wait_for_confirmation(algod, tx_id)


class TestContractWriteBox(BaseTestContract):
    """Testing class for :class:`contract.contract.PermissionDApp` write_box method."""

    name = "write_box"

    def test_contract_permission_dapp_write_box_by_creator(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test that creator can write to a box."""

        box_name = box_name_from_address(TEST_ADDRESS)
        value = "test_value"

        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="write_box",
                args=[box_name, value],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box_name],
            )
        )

        # Verify box was written
        box_info = self.permission_client.algorand.client.algod.application_box_by_name(
            self.permission_client.app_id, box_name
        )
        assert base64.b64decode(box_info["name"]) == box_name
        assert base64.b64decode(box_info["value"]) == value.encode("utf-8")

    def test_contract_permission_dapp_write_box_fails_for_non_creator(
        self,
        user_account: SigningAccount,
    ) -> None:
        box_name = box_name_from_address(TEST_ADDRESS)
        value = "test_value"

        with pytest.raises(LogicError, match="Only creator can write to boxes"):
            self.permission_client.send.call(
                AppClientMethodCallParams(
                    method="write_box",
                    args=[box_name, value],
                    sender=user_account.address,
                    signer=user_account.signer,
                    box_references=[box_name],
                    )
            )

    def test_contract_permission_dapp_write_box_fails_for_wrong_box_size(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test that box name must be exactly 32 bytes."""

        box_name = box_name_from_address(TEST_ADDRESS)[:9]
        value = "test_value"

        with pytest.raises(LogicError, match="Box name must be exactly 32 bytes"):
            self.permission_client.send.call(
                AppClientMethodCallParams(
                    method="write_box",
                    args=[box_name, value],
                    sender=creator_account.address,
                    signer=creator_account.signer,
                    box_references=[box_name],
                    )
            )

    def test_contract_permission_dapp_write_box_overwrites_existing(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test that writing to existing box overwrites content."""
        box_name = box_name_from_address(TEST_ADDRESS)
        value1 = "first_value"
        value2 = "second_value"

        # Write first value
        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="write_box",
                args=[box_name, value1],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box_name],
            )
        )

        # Verify first value
        box_info = self.permission_client.algorand.client.algod.application_box_by_name(
            self.permission_client.app_id, box_name
        )
        assert base64.b64decode(box_info["value"]) == value1.encode("utf-8")

        # Write second value (overwrite)
        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="write_box",
                args=[box_name, value2],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box_name],
            )
        )

        # Verify second value overwrote the first
        box_info = self.permission_client.algorand.client.algod.application_box_by_name(
            self.permission_client.app_id, box_name
        )
        assert base64.b64decode(box_info["value"]) == value2.encode("utf-8")

    def test_contract_permission_dapp_write_box_with_empty_string(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test writing empty string to a box."""
        _, address = generate_account()
        box_name = box_name_from_address(address)
        value = ""

        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="write_box",
                args=[box_name, value],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box_name],
            )
        )

        # Verify box was written with empty content
        box_info = self.permission_client.algorand.client.algod.application_box_by_name(
            self.permission_client.app_id, box_name
        )
        assert base64.b64decode(box_info["value"]) == b""

    def test_contract_permission_dapp_write_box_with_unicode_string(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test writing unicode string to a box."""
        _, address = generate_account()
        box_name = box_name_from_address(address)
        value = "Hello 世界 🌍"

        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="write_box",
                args=[box_name, value],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box_name],
            )
        )

        # Verify box was written with correct content
        box_info = self.permission_client.algorand.client.algod.application_box_by_name(
            self.permission_client.app_id, box_name
        )
        assert base64.b64decode(box_info["value"]) == value.encode("utf-8")


class TestContractDeleteBox(BaseTestContract):
    """Testing class for :class:`contract.contract.PermissionDApp` delete_box method."""

    name = "delete_box"

    def test_contract_permission_dapp_delete_box_by_creator(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test that creator can delete a box."""
        _, address = generate_account()
        box_name = box_name_from_address(address)
        value = "test_value"

        # First write a box
        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="write_box",
                args=[box_name, value],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box_name],
            )
        )

        # Verify box exists
        box_info = self.permission_client.algorand.client.algod.application_box_by_name(
            self.permission_client.app_id, box_name
        )
        assert base64.b64decode(box_info["name"]) == box_name

        # Delete the box
        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="delete_box",
                args=[box_name],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box_name],
            )
        )

        # Verify box was deleted
        with pytest.raises(AlgodHTTPError, match="box not found"):
            self.permission_client.algorand.client.algod.application_box_by_name(
                self.permission_client.app_id, box_name
            )

    def test_contract_permission_dapp_delete_box_fails_for_non_creator(
        self,
        creator_account: SigningAccount,
        user_account: SigningAccount,
    ) -> None:
        """Test that non-creator cannot delete boxes."""
        _, address = generate_account()
        box_name = box_name_from_address(address)
        value = "test_value"

        # First write a box (by creator)
        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="write_box",
                args=[box_name, value],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box_name],
            )
        )

        # Try to delete by non-creator
        with pytest.raises(LogicError, match="Only creator can delete boxes"):
            self.permission_client.send.call(
                AppClientMethodCallParams(
                    method="delete_box",
                    args=[box_name],
                    sender=user_account.address,
                    signer=user_account.signer,
                    box_references=[box_name],
                    )
            )

    def test_contract_permission_dapp_delete_box_fails_for_wrong_box_size(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test that box name must be exactly 32 bytes for deletion."""
        box_name = box_name_from_address(TEST_ADDRESS)[:9]

        with pytest.raises(LogicError, match="Box name must be exactly 32 bytes"):
            self.permission_client.send.call(
                AppClientMethodCallParams(
                    method="delete_box",
                    args=[box_name],
                    sender=creator_account.address,
                    signer=creator_account.signer,
                    box_references=[box_name],
                    )
            )

    def test_contract_permission_dapp_delete_nonexistent_box(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test deleting a box that doesn't exist."""
        _, address = generate_account()
        box_name = box_name_from_address(address)

        # This should succeed (box deletion is idempotent in Algorand)
        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="delete_box",
                args=[box_name],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box_name],
            )
        )


class TestContractMultipleBoxes(BaseTestContract):
    """Testing multiple box operations."""

    name = "multiple_boxes"

    def test_contract_permission_dapp_multiple_boxes_operations(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test operations with multiple boxes."""

        _, address = generate_account()
        box1_name = box_name_from_address(address)
        box1_value = "value1"
        _, address = generate_account()
        box2_name = box_name_from_address(address)
        box2_value = "value2"

        # Write first box
        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="write_box",
                args=[box1_name, box1_value],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box1_name],
            )
        )

        # Write second box
        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="write_box",
                args=[box2_name, box2_value],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box2_name],
            )
        )

        # Verify both boxes exist with correct values
        box1_info = (
            self.permission_client.algorand.client.algod.application_box_by_name(
                self.permission_client.app_id, box1_name
            )
        )
        box2_info = (
            self.permission_client.algorand.client.algod.application_box_by_name(
                self.permission_client.app_id, box2_name
            )
        )

        assert base64.b64decode(box1_info["value"]) == box1_value.encode("utf-8")
        assert base64.b64decode(box2_info["value"]) == box2_value.encode("utf-8")

        # Delete first box
        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="delete_box",
                args=[box1_name],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box1_name],
            )
        )

        # Verify first box is gone, second box still exists
        with pytest.raises(AlgodHTTPError, match="box not found"):
            self.permission_client.algorand.client.algod.application_box_by_name(
                self.permission_client.app_id, box1_name
            )

        box2_info = (
            self.permission_client.algorand.client.algod.application_box_by_name(
                self.permission_client.app_id, box2_name
            )
        )
        assert base64.b64decode(box2_info["value"]) == box2_value.encode("utf-8")


class TestContractBoxManagement(BaseTestContract):
    """Testing box storage and memory management."""

    name = "box_management"

    def test_contract_permission_dapp_box_creation_and_deletion_lifecycle(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test complete box lifecycle: create → verify → delete → verify gone."""
        _, address = generate_account()
        box_name = box_name_from_address(address)
        value = "lifecycle_test_value"

        # Create box
        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="write_box",
                args=[box_name, value],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box_name],
            )
        )

        # Verify box exists and has correct content
        box_info = self.permission_client.algorand.client.algod.application_box_by_name(
            self.permission_client.app_id, box_name
        )
        assert base64.b64decode(box_info["name"]) == box_name
        assert base64.b64decode(box_info["value"]) == value.encode("utf-8")

        # Delete box
        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="delete_box",
                args=[box_name],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box_name],
            )
        )

        # Verify box is gone
        with pytest.raises(AlgodHTTPError, match="box not found"):
            self.permission_client.algorand.client.algod.application_box_by_name(
                self.permission_client.app_id, box_name
            )

    def test_contract_permission_dapp_consecutive_box_operations(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test multiple consecutive box operations on same box."""
        _, address = generate_account()
        box_name = box_name_from_address(address)

        # Write → Delete → Write → Delete
        values = ["first", "second", "third"]
        note_counter = 0

        for i, value in enumerate(values):
            # Write box
            note = f"write_{note_counter}".encode()
            note_counter += 1
            self.permission_client.send.call(
                AppClientMethodCallParams(
                    method="write_box",
                    args=[box_name, value],
                    sender=creator_account.address,
                    signer=creator_account.signer,
                    box_references=[box_name],
                    note=note,
                )
            )

            # Verify content
            box_info = (
                self.permission_client.algorand.client.algod.application_box_by_name(
                    self.permission_client.app_id, box_name
                )
            )
            assert base64.b64decode(box_info["value"]) == value.encode("utf-8")

            # Delete box (except for last iteration)
            if i < len(values) - 1:
                note = f"delete_{note_counter}".encode()
                note_counter += 1
                self.permission_client.send.call(
                    AppClientMethodCallParams(
                        method="delete_box",
                        args=[box_name],
                        sender=creator_account.address,
                        signer=creator_account.signer,
                        box_references=[box_name],
                        note=note,
                    )
                )

                # Verify deletion
                with pytest.raises(AlgodHTTPError, match="box not found"):
                    self.permission_client.algorand.client.algod.application_box_by_name(
                        self.permission_client.app_id, box_name
                    )


class TestContractAccessControl(BaseTestContract):
    """Testing access control scenarios."""

    name = "access_control"

    def test_contract_permission_dapp_only_creator_can_manage_boxes(
        self,
        creator_account: SigningAccount,
        user_account: SigningAccount,
        other_account: SigningAccount,
    ) -> None:
        """Test that only creator can perform box operations."""
        _, address = generate_account()
        box_name = box_name_from_address(address)
        value = "test_value"

        # Creator can write
        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="write_box",
                args=[box_name, value],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box_name],
            )
        )

        # User cannot write
        with pytest.raises(LogicError, match="Only creator can write to boxes"):
            self.permission_client.send.call(
                AppClientMethodCallParams(
                    method="write_box",
                    args=[box_name, "user_value"],
                    sender=user_account.address,
                    signer=user_account.signer,
                    box_references=[box_name],
                    )
            )

        # Other account cannot write
        with pytest.raises(LogicError, match="Only creator can write to boxes"):
            self.permission_client.send.call(
                AppClientMethodCallParams(
                    method="write_box",
                    args=[box_name, "other_value"],
                    sender=other_account.address,
                    signer=other_account.signer,
                    box_references=[box_name],
                    )
            )

        # User cannot delete
        with pytest.raises(LogicError, match="Only creator can delete boxes"):
            self.permission_client.send.call(
                AppClientMethodCallParams(
                    method="delete_box",
                    args=[box_name],
                    sender=user_account.address,
                    signer=user_account.signer,
                    box_references=[box_name],
                    )
            )

        # Only creator can delete
        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="delete_box",
                args=[box_name],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box_name],
            )
        )


class TestContractEdgeCases(BaseTestContract):
    """Testing edge cases and error scenarios."""

    name = "edge_cases"

    def test_contract_permission_dapp_large_box_content(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test writing large content to a box."""
        _, address = generate_account()
        box_name = box_name_from_address(address)
        # Create a string that's ~1KB
        value = "x" * 1000

        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="write_box",
                args=[box_name, value],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box_name],
            )
        )

        # Verify box content
        box_info = self.permission_client.algorand.client.algod.application_box_by_name(
            self.permission_client.app_id, box_name
        )
        assert base64.b64decode(box_info["value"]) == value.encode("utf-8")
        assert len(base64.b64decode(box_info["value"])) == 1000

    def test_contract_permission_dapp_special_characters_in_content(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test writing content with special characters."""
        _, address = generate_account()
        box_name = box_name_from_address(address)
        value = "Line1\nLine2\tTabbed\x00Null\rReturn"

        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="write_box",
                args=[box_name, value],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box_name],
            )
        )

        # Verify box content preserves special characters
        box_info = self.permission_client.algorand.client.algod.application_box_by_name(
            self.permission_client.app_id, box_name
        )
        assert base64.b64decode(box_info["value"]) == value.encode("utf-8")

    def test_contract_permission_dapp_rapid_sequential_operations(
        self,
        creator_account: SigningAccount,
    ) -> None:
        """Test rapid sequential box operations."""
        _, address = generate_account()
        box_name = box_name_from_address(address)

        # Perform multiple operations quickly
        for i in range(5):
            value = f"value_{i}"

            # Write
            self.permission_client.send.call(
                AppClientMethodCallParams(
                    method="write_box",
                    args=[box_name, value],
                    sender=creator_account.address,
                    signer=creator_account.signer,
                    box_references=[box_name],
                    )
            )

            # Verify
            box_info = (
                self.permission_client.algorand.client.algod.application_box_by_name(
                    self.permission_client.app_id, box_name
                )
            )
            assert base64.b64decode(box_info["value"]) == value.encode("utf-8")

        # Final delete
        self.permission_client.send.call(
            AppClientMethodCallParams(
                method="delete_box",
                args=[box_name],
                sender=creator_account.address,
                signer=creator_account.signer,
                box_references=[box_name],
            )
        )
