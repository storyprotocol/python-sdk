# tests/integration/test_integration_wip.py

import pytest
from eth_typing import Hash32

from story_protocol_python_sdk.story_client import StoryClient

from .setup_for_integration import (
    wallet_address,
    wallet_address_2,
    wallet_address_3,
    web3,
)

# Type assertions to ensure wallet addresses are strings
assert wallet_address is not None, "wallet_address is required"
assert wallet_address_2 is not None, "wallet_address_2 is required"
assert wallet_address_3 is not None, "wallet_address_3 is required"

# Type cast to satisfy mypy
wallet_address_str: str = wallet_address
wallet_address_2_str: str = wallet_address_2
wallet_address_3_str: str = wallet_address_3


class TestWIPDeposit:
    def test_deposit(self, story_client: StoryClient):
        """Test depositing IP to WIP"""
        ip_amt = web3.to_wei(0.000001, "ether")

        # Get balances before deposit
        balance_before = story_client.get_wallet_balance()
        wip_before = story_client.WIP.balance_of(wallet_address_str)

        # Deposit IP to WIP
        response = story_client.WIP.deposit(amount=ip_amt)

        # Verify transaction hash
        assert isinstance(response["tx_hash"], str)

        # Get balances after deposit
        balance_after = story_client.get_wallet_balance()
        wip_after = story_client.WIP.balance_of(wallet_address_str)

        # Verify WIP balance increased by deposit amount
        assert wip_after == wip_before + ip_amt

        # Calculate gas cost
        tx_receipt = web3.eth.wait_for_transaction_receipt(
            Hash32(bytes.fromhex(response["tx_hash"])), timeout=300
        )
        gas_cost = tx_receipt["gasUsed"] * tx_receipt["effectiveGasPrice"]

        # Verify wallet balance decreased by deposit amount plus gas cost
        assert balance_after == balance_before - ip_amt - gas_cost


class TestWIPTransfer:
    """Test WIP transfer functionality"""

    def test_transfer(self, story_client: StoryClient):
        """Test transferring WIP"""
        transfer_amount = web3.to_wei("0.01", "ether")

        # Get balances before transfer
        sender_wip_before = story_client.WIP.balance_of(wallet_address_str)
        receiver_wip_before = story_client.WIP.balance_of(wallet_address_2_str)

        # Ensure sender has enough WIP balance
        if sender_wip_before < transfer_amount:
            story_client.WIP.deposit(
                amount=transfer_amount - sender_wip_before,
                tx_options={"waitForTransaction": True},
            )

        sender_wip_before = story_client.WIP.balance_of(wallet_address_str)

        # Transfer WIP to wallet_address_2
        response = story_client.WIP.transfer(
            to=wallet_address_2_str,
            amount=transfer_amount,
            tx_options={"waitForTransaction": True},
        )

        # Verify transaction hash
        assert isinstance(response["tx_hash"], str)

        # Get balances after transfer
        sender_wip_after = story_client.WIP.balance_of(wallet_address_str)
        receiver_wip_after = story_client.WIP.balance_of(wallet_address_2_str)

        # Verify sender's WIP balance decreased by transfer amount
        assert sender_wip_after == sender_wip_before - transfer_amount

        # Verify receiver's WIP balance increased by transfer amount
        assert receiver_wip_after == receiver_wip_before + transfer_amount
        # Note: We're not testing transferFrom here as it requires approval
        # and the TypeScript test also skips this test for the same reason

    def test_transfer_zero_address(self, story_client: StoryClient):
        """Test transfer with zero address (should be rejected by contract with custom error)"""
        zero_address = "0x0000000000000000000000000000000000000000"

        # The contract should reject this with a custom error ERC20InvalidReceiver
        with pytest.raises(Exception) as exc_info:
            story_client.WIP.transfer(
                to=zero_address,
                amount=web3.to_wei("0.01", "ether"),
                tx_options={"waitForTransaction": True},
            )

        # Verify the transaction failed due to contract validation
        # The SDK should provide the direct contract error message
        assert "0xec442f05" in str(exc_info.value)

    def test_transfer_to_contract_address(self, story_client: StoryClient):
        """Test transfer to WIP contract address (should be rejected by contract with custom error)"""
        # Get the WIP contract address
        contract_address = story_client.WIP.wip_client.contract.address

        # The contract should reject this with a custom error ERC20InvalidReceiver
        with pytest.raises(Exception) as exc_info:
            story_client.WIP.transfer(
                to=contract_address,
                amount=web3.to_wei("0.01", "ether"),
                tx_options={"waitForTransaction": True},
            )

        # Verify the transaction failed due to contract validation
        # The SDK should provide the direct contract error message
        assert "0xec442f05" in str(exc_info.value)


class TestWIPApprove:
    """Test WIP approval functionality"""

    def setup_method(self):
        """Setup method called before each test"""
        pass

    def teardown_method(self):
        """Teardown method called after each test"""
        # Reset allowance to a reasonable value to avoid affecting other tests
        try:
            from tests.integration.config.test_config import account, web3
            from tests.integration.config.utils import get_story_client

            story_client = get_story_client(web3, account)

            # Check current allowance
            current_allowance = story_client.WIP.allowance(
                owner=wallet_address_str, spender=wallet_address_2_str
            )
            target_allowance = web3.to_wei("0.01", "ether")

            # Only reset if current allowance is not already 0.01 IP
            if current_allowance != target_allowance:
                story_client.WIP.approve(
                    spender=wallet_address_2_str,
                    amount=target_allowance,
                    tx_options={"waitForTransaction": True},
                )
            else:
                pass
        except Exception:
            raise

    def test_approve_basic(self, story_client: StoryClient):
        """Test basic approve functionality"""
        approve_amount = web3.to_wei("0.1", "ether")

        try:
            # Get initial allowance
            story_client.WIP.allowance(
                owner=wallet_address_str, spender=wallet_address_2_str
            )

            # Approve wallet_address_2 to spend WIP
            response = story_client.WIP.approve(
                spender=wallet_address_2_str,
                amount=approve_amount,
                tx_options={"waitForTransaction": True},
            )

            # Verify transaction hash
            assert isinstance(
                response, dict
            ), f"Expected dict response, got {type(response)}"
            assert "tx_hash" in response, f"Response missing tx_hash: {response}"
            assert isinstance(
                response["tx_hash"], str
            ), f"Invalid tx_hash type: {type(response['tx_hash'])}"

            tx_hash = response["tx_hash"]

            # Wait for transaction confirmation
            tx_receipt = web3.eth.wait_for_transaction_receipt(
                Hash32(bytes.fromhex(tx_hash)), timeout=300
            )

            if tx_receipt["status"] == 0:
                raise AssertionError(
                    f"Approve transaction failed with status 0: {tx_hash}"
                )

            # Verify allowance was set correctly
            final_allowance = story_client.WIP.allowance(
                owner=wallet_address_str, spender=wallet_address_2_str
            )

            assert final_allowance == approve_amount, (
                f"Allowance mismatch. Expected: {web3.from_wei(approve_amount, 'ether')} IP, "
                f"Got: {web3.from_wei(final_allowance, 'ether')} IP"
            )

        except Exception:
            raise

    def test_approve_zero_amount(self, story_client: StoryClient):
        """Test approving zero amount (should be rejected by implementation)"""
        try:
            # First approve some amount
            initial_approve = web3.to_wei("0.05", "ether")
            story_client.WIP.approve(
                spender=wallet_address_2_str,
                amount=initial_approve,
                tx_options={"waitForTransaction": True},
            )

            # Verify initial allowance
            initial_allowance = story_client.WIP.allowance(
                owner=wallet_address_str, spender=wallet_address_2_str
            )
            assert initial_allowance == initial_approve

            # Try to approve zero amount - should be rejected
            with pytest.raises(
                ValueError, match="WIP approve amount must be greater than 0"
            ):
                story_client.WIP.approve(
                    spender=wallet_address_2_str,
                    amount=0,
                    tx_options={"waitForTransaction": True},
                )

            # Verify allowance remains unchanged
            final_allowance = story_client.WIP.allowance(
                owner=wallet_address_str, spender=wallet_address_2_str
            )

            assert (
                final_allowance == initial_allowance
            ), f"Allowance should remain unchanged, got: {final_allowance}"

        except Exception:
            raise

    def test_approve_negative_amount(self, story_client: StoryClient):
        """Test approving negative amount (should be rejected)"""
        with pytest.raises(
            ValueError, match="WIP approve amount must be greater than 0"
        ):
            story_client.WIP.approve(
                spender=wallet_address_2_str,
                amount=-1,
                tx_options={"waitForTransaction": True},
            )

    def test_approve_max_uint256(self, story_client: StoryClient):
        """Test approving maximum uint256 value"""
        max_uint256 = 2**256 - 1

        try:
            response = story_client.WIP.approve(
                spender=wallet_address_2_str,
                amount=max_uint256,
                tx_options={"waitForTransaction": True},
            )

            # Verify transaction
            assert isinstance(response["tx_hash"], str)

            # Wait for confirmation
            web3.eth.wait_for_transaction_receipt(
                Hash32(bytes.fromhex(response["tx_hash"])), timeout=300
            )

            # Verify allowance is set to max uint256
            final_allowance = story_client.WIP.allowance(
                owner=wallet_address_str, spender=wallet_address_2_str
            )

            assert (
                final_allowance == max_uint256
            ), f"Allowance should be max uint256, got: {final_allowance}"

        except Exception:
            raise

    @pytest.mark.parametrize(
        "invalid_address",
        [
            "0x123",  # Too short
            "invalid_address",  # Invalid format
            "",  # Empty string
        ],
    )
    def test_approve_invalid_spender(
        self, story_client: StoryClient, invalid_address: str
    ):
        """Test approve with invalid spender addresses"""
        with pytest.raises(ValueError, match="not valid"):
            story_client.WIP.approve(
                spender=invalid_address, amount=web3.to_wei("0.01", "ether")
            )

    def test_approve_zero_address(self, story_client: StoryClient):
        """Test approve with zero address (current implementation accepts it)"""
        zero_address = "0x0000000000000000000000000000000000000000"

        # The current implementation accepts zero address, so we test that it works
        response = story_client.WIP.approve(
            spender=zero_address,
            amount=web3.to_wei("0.01", "ether"),
            tx_options={"waitForTransaction": True},
        )

        # Verify the transaction succeeded
        assert isinstance(response["tx_hash"], str)

        # Verify the allowance was set
        allowance = story_client.WIP.allowance(
            owner=wallet_address_str, spender=zero_address
        )
        assert allowance == web3.to_wei("0.01", "ether")

    def test_approve_self(self, story_client: StoryClient):
        """Test approve with self as spender (should be rejected by contract with custom error)"""
        with pytest.raises(Exception) as exc_info:
            story_client.WIP.approve(
                spender=wallet_address_str,
                amount=web3.to_wei("0.01", "ether"),
                tx_options={"waitForTransaction": True},
            )

        # Verify the transaction failed due to contract validation
        # The SDK should provide the direct contract error message
        assert "0x94280d62" in str(exc_info.value)


class TestWIPTransferFrom:
    """Test WIP transferFrom functionality"""

    def setup_method(self):
        """Setup method called before each test"""
        pass

    def teardown_method(self):
        """Teardown method called after each test"""
        pass

    def test_transfer_from_basic(
        self, story_client: StoryClient, story_client_2: StoryClient
    ):
        """Test basic transferFrom functionality"""
        transfer_amount = web3.to_wei("0.01", "ether")

        try:
            # Ensure wallet_address has enough WIP balance
            owner_balance = story_client.WIP.balance_of(wallet_address_str)
            if owner_balance < transfer_amount:
                deposit_amount = (
                    transfer_amount - owner_balance + web3.to_wei("0.1", "ether")
                )
                story_client.WIP.deposit(
                    amount=deposit_amount, tx_options={"waitForTransaction": True}
                )

            # Get initial balances
            owner_wip_before = story_client.WIP.balance_of(wallet_address_str)
            spender_wip_before = story_client.WIP.balance_of(wallet_address_2_str)
            receiver_wip_before = story_client.WIP.balance_of(wallet_address_3_str)

            # Approve spender to transfer from owner
            approve_response = story_client.WIP.approve(
                spender=wallet_address_2_str,
                amount=transfer_amount,
                tx_options={"waitForTransaction": True},
            )

            # Wait for approve transaction
            web3.eth.wait_for_transaction_receipt(
                Hash32(bytes.fromhex(approve_response["tx_hash"])), timeout=300
            )

            # Verify allowance
            allowance = story_client.WIP.allowance(
                owner=wallet_address_str, spender=wallet_address_2_str
            )
            assert allowance >= transfer_amount, f"Insufficient allowance: {allowance}"

            # Execute transferFrom using spender's account
            transfer_response = story_client_2.WIP.transfer_from(
                from_address=wallet_address_str,
                to=wallet_address_3_str,
                amount=transfer_amount,
                tx_options={"waitForTransaction": True},
            )

            # Verify transaction hash
            assert isinstance(
                transfer_response, dict
            ), f"Expected dict response, got {type(transfer_response)}"
            assert (
                "tx_hash" in transfer_response
            ), f"Response missing tx_hash: {transfer_response}"
            assert isinstance(
                transfer_response["tx_hash"], str
            ), f"Invalid tx_hash type: {type(transfer_response['tx_hash'])}"

            tx_hash = transfer_response["tx_hash"]

            # Wait for transaction confirmation
            tx_receipt = web3.eth.wait_for_transaction_receipt(
                Hash32(bytes.fromhex(tx_hash)), timeout=300
            )

            if tx_receipt["status"] == 0:
                raise AssertionError(
                    f"TransferFrom transaction failed with status 0: {tx_hash}"
                )

            # Get final balances
            owner_wip_after = story_client.WIP.balance_of(wallet_address_str)
            spender_wip_after = story_client.WIP.balance_of(wallet_address_2_str)
            receiver_wip_after = story_client.WIP.balance_of(wallet_address_3_str)

            # Verify balances
            assert (
                owner_wip_after == owner_wip_before - transfer_amount
            ), f"Owner balance should decrease by {web3.from_wei(transfer_amount, 'ether')} IP"

            assert (
                receiver_wip_after == receiver_wip_before + transfer_amount
            ), f"Receiver balance should increase by {web3.from_wei(transfer_amount, 'ether')} IP"

            # Verify spender balance remains the same (they're just the intermediary)
            assert (
                spender_wip_after == spender_wip_before
            ), "Spender balance should remain unchanged"

            # Verify allowance was reduced
            final_allowance = story_client.WIP.allowance(
                owner=wallet_address_str, spender=wallet_address_2_str
            )
            expected_allowance = allowance - transfer_amount
            assert final_allowance == expected_allowance, (
                f"Allowance should be reduced by transfer amount. "
                f"Expected: {web3.from_wei(expected_allowance, 'ether')} IP, "
                f"Got: {web3.from_wei(final_allowance, 'ether')} IP"
            )

        except Exception:
            raise

    def test_transfer_from_insufficient_allowance(
        self, story_client: StoryClient, story_client_2: StoryClient
    ):
        """Test transferFrom with insufficient allowance"""
        transfer_amount = web3.to_wei("0.01", "ether")

        try:
            # Ensure wallet_address has enough WIP balance
            owner_balance = story_client.WIP.balance_of(wallet_address_str)
            if owner_balance < transfer_amount:
                story_client.WIP.deposit(
                    amount=transfer_amount, tx_options={"waitForTransaction": True}
                )

            # Approve less than transfer amount
            insufficient_allowance = transfer_amount - web3.to_wei("0.001", "ether")
            story_client.WIP.approve(
                spender=wallet_address_2_str,
                amount=insufficient_allowance,
                tx_options={"waitForTransaction": True},
            )

            # Try to transfer more than allowed
            with pytest.raises(Exception):  # Should raise an exception
                story_client_2.WIP.transfer_from(
                    from_address=wallet_address_str,
                    to=wallet_address_2_str,
                    amount=transfer_amount,
                    tx_options={"waitForTransaction": True},
                )

        except Exception:
            raise

    def test_transfer_from_insufficient_balance(
        self, story_client: StoryClient, story_client_2: StoryClient
    ):
        """Test transferFrom with insufficient balance"""
        transfer_amount = web3.to_wei("1000", "ether")  # Large amount

        try:
            # Get current balance
            story_client.WIP.balance_of(wallet_address_str)

            # Approve large amount
            story_client.WIP.approve(
                spender=wallet_address_2_str,
                amount=transfer_amount,
                tx_options={"waitForTransaction": True},
            )

            # Try to transfer more than available balance
            with pytest.raises(Exception):  # Should raise an exception
                story_client_2.WIP.transfer_from(
                    from_address=wallet_address_str,
                    to=wallet_address_2_str,
                    amount=transfer_amount,
                    tx_options={"waitForTransaction": True},
                )

        except Exception:
            raise

    def test_transfer_from_negative_amount(self, story_client: StoryClient):
        """Test transferFrom with negative amount (should be rejected)"""
        with pytest.raises(
            ValueError, match="WIP transfer amount must be greater than 0"
        ):
            story_client.WIP.transfer_from(
                from_address=wallet_address_str,
                to=wallet_address_2_str,
                amount=-1,
                tx_options={"waitForTransaction": True},
            )

    @pytest.mark.parametrize(
        "invalid_address",
        [
            "0x123",  # Too short
            "invalid_address",  # Invalid format
            "",  # Empty string
        ],
    )
    def test_transfer_from_invalid_addresses(
        self, story_client: StoryClient, invalid_address: str
    ):
        """Test transferFrom with invalid addresses"""
        with pytest.raises(ValueError, match="not valid"):
            story_client.WIP.transfer_from(
                from_address=invalid_address,
                to=wallet_address_2_str,
                amount=web3.to_wei("0.01", "ether"),
            )

        with pytest.raises(ValueError, match="not valid"):
            story_client.WIP.transfer_from(
                from_address=wallet_address_str,
                to=invalid_address,
                amount=web3.to_wei("0.01", "ether"),
            )

    def test_transfer_from_zero_addresses(self, story_client: StoryClient):
        """Test transferFrom with zero addresses (should be rejected by contract with custom error)"""
        zero_address = "0x0000000000000000000000000000000000000000"

        # Test zero address as to_address - should be rejected by contract validation
        # Note: We need to set up approval first for a valid from_address
        story_client.WIP.approve(
            spender=wallet_address_2_str,
            amount=web3.to_wei("0.1", "ether"),
            tx_options={"waitForTransaction": True},
        )

        with pytest.raises(Exception) as exc_info:
            story_client.WIP.transfer_from(
                from_address=wallet_address_str,
                to=zero_address,
                amount=web3.to_wei("0.01", "ether"),
                tx_options={"waitForTransaction": True},
            )

        # Verify the transaction failed due to contract validation
        # The SDK should provide the direct contract error message
        assert "0xec442f05" in str(exc_info.value)

    def test_transfer_from_to_contract_address(self, story_client: StoryClient):
        """Test transferFrom to WIP contract address (should be rejected by contract with custom error)"""
        # Get the WIP contract address
        contract_address = story_client.WIP.wip_client.contract.address

        # Set up approval first
        story_client.WIP.approve(
            spender=wallet_address_2_str,
            amount=web3.to_wei("0.1", "ether"),
            tx_options={"waitForTransaction": True},
        )

        with pytest.raises(Exception) as exc_info:
            story_client.WIP.transfer_from(
                from_address=wallet_address_str,
                to=contract_address,
                amount=web3.to_wei("0.01", "ether"),
                tx_options={"waitForTransaction": True},
            )

        # Verify the transaction failed due to contract validation
        # The SDK should provide the direct contract error message
        assert "0xec442f05" in str(exc_info.value)


class TestWIPWithdraw:
    def test_withdraw(self, story_client: StoryClient):
        """Test withdrawing WIP to IP"""
        # Get balances before withdrawal
        balance_before = story_client.get_wallet_balance()
        wip_before = story_client.WIP.balance_of(wallet_address_str)

        # Withdraw all WIP
        response = story_client.WIP.withdraw(
            amount=wip_before, tx_options={"waitForTransaction": True}
        )

        # Verify transaction hash
        assert isinstance(response["tx_hash"], str)

        # Get balances after withdrawal
        wip_after = story_client.WIP.balance_of(wallet_address_str)
        balance_after = story_client.get_wallet_balance()

        # Verify WIP balance is now zero
        assert wip_after == 0

        # Calculate gas cost
        tx_receipt = web3.eth.wait_for_transaction_receipt(
            Hash32(bytes.fromhex(response["tx_hash"])), timeout=300
        )
        gas_cost = tx_receipt["gasUsed"] * tx_receipt["effectiveGasPrice"]

        # Verify wallet balance increased by withdrawal amount minus gas cost
        assert balance_after == balance_before + wip_before - gas_cost
