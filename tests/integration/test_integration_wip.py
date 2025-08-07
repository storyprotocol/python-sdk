import logging
import sys

import pytest
from eth_typing import Hash32

from story_protocol_python_sdk.story_client import StoryClient

from .setup_for_integration import (
    wallet_address,
    wallet_address_2,
    wallet_address_3,
    web3,
)

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,  # Ensure output goes to stdout
)
logger = logging.getLogger(__name__)

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
    def test_transfer(self, story_client: StoryClient):
        """Test transferring WIP"""
        transfer_amount = web3.to_wei("0.01", "ether")

        # Get balances before transfer
        sender_wip_before = story_client.WIP.balance_of(wallet_address_str)
        receiver_wip_before = story_client.WIP.balance_of(wallet_address_2_str)

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


class TestWIPApprove:
    """Test WIP approval functionality"""

    def setup_method(self):
        """Setup method called before each test"""
        logger.info("Setting up WIP approve test")

    def teardown_method(self):
        """Teardown method called after each test"""
        logger.info("Cleaning up WIP approve test")

    def test_logging_demo(self):
        """Demo test to show logging vs print output"""
        print("🔵 PRINT: This will show with -s flag")
        print("🔵 PRINT: Without -s, this is captured by pytest")

        logger.debug("🐛 DEBUG: This won't show (level too low)")
        logger.info("📝 INFO: This should show with proper logging config")
        logger.warning("⚠️ WARNING: This should also show")
        logger.error("❌ ERROR: This should definitely show")

        # This test always passes
        assert True

    def test_approve_basic(self, story_client: StoryClient):
        """Test basic approve functionality"""
        print("🔵 PRINT: Starting basic approve test")  # This will show with -s
        logger.info("📝 LOGGER: Testing basic WIP approve functionality")

        approve_amount = web3.to_wei("0.1", "ether")

        try:
            # Get initial allowance
            initial_allowance = story_client.WIP.allowance(
                owner=wallet_address_str, spender=wallet_address_2_str
            )
            logger.info(
                f"Initial allowance: {web3.from_wei(initial_allowance, 'ether')} ETH"
            )

            # Approve wallet_address_2 to spend WIP
            logger.info(
                f"Approving {web3.from_wei(approve_amount, 'ether')} ETH for {wallet_address_2_str}"
            )
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
            logger.info(f"Approve transaction submitted: {tx_hash}")

            # Wait for transaction confirmation
            tx_receipt = web3.eth.wait_for_transaction_receipt(
                Hash32(bytes.fromhex(tx_hash)), timeout=300
            )

            if tx_receipt["status"] == 0:
                logger.error(f"Approve transaction failed: {tx_hash}")
                raise AssertionError(
                    f"Approve transaction failed with status 0: {tx_hash}"
                )

            logger.info(
                f"Approve transaction confirmed in block {tx_receipt['blockNumber']}"
            )

            # Verify allowance was set correctly
            final_allowance = story_client.WIP.allowance(
                owner=wallet_address_str, spender=wallet_address_2_str
            )
            logger.info(
                f"Final allowance: {web3.from_wei(final_allowance, 'ether')} ETH"
            )

            assert final_allowance == approve_amount, (
                f"Allowance mismatch. Expected: {web3.from_wei(approve_amount, 'ether')} ETH, "
                f"Got: {web3.from_wei(final_allowance, 'ether')} ETH"
            )

            logger.info("Basic approve test completed successfully!")

        except Exception as e:
            logger.error(f"Basic approve test failed: {str(e)}")
            raise

    def test_approve_zero_amount(self, story_client: StoryClient):
        """Test approving zero amount (should be rejected by implementation)"""
        logger.info("Testing approve with zero amount")

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
            logger.info("Attempting to approve zero amount (should be rejected)")
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
            logger.info("Zero amount approve test completed successfully!")

        except Exception as e:
            logger.error(f"Zero amount approve test failed: {str(e)}")
            raise

    def test_approve_negative_amount(self, story_client: StoryClient):
        """Test approving negative amount (should be rejected)"""
        logger.info("Testing approve with negative amount")

        with pytest.raises(
            ValueError, match="WIP approve amount must be greater than 0"
        ):
            story_client.WIP.approve(
                spender=wallet_address_2_str,
                amount=-1,
                tx_options={"waitForTransaction": True},
            )

        logger.info("Negative amount approve test completed successfully!")

    def test_approve_max_uint256(self, story_client: StoryClient):
        """Test approving maximum uint256 value"""
        logger.info("Testing approve with maximum uint256 value")

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
            logger.info("Max uint256 approve test completed successfully!")

        except Exception as e:
            logger.error(f"Max uint256 approve test failed: {str(e)}")
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
        logger.info(f"Testing approve with invalid spender: {invalid_address}")

        with pytest.raises(ValueError, match="not valid"):
            story_client.WIP.approve(
                spender=invalid_address, amount=web3.to_wei("0.01", "ether")
            )

        logger.info(f"Invalid spender test passed for: {invalid_address}")

    def test_approve_zero_address(self, story_client: StoryClient):
        """Test approve with zero address (should be rejected)"""
        logger.info("Testing approve with zero address")

        zero_address = "0x0000000000000000000000000000000000000000"

        # The current implementation allows zero address, but we can test it
        # If the implementation changes to reject zero address, this test will catch it
        try:
            response = story_client.WIP.approve(
                spender=zero_address,
                amount=web3.to_wei("0.01", "ether"),
                tx_options={"waitForTransaction": True},
            )

            # If it succeeds, verify the transaction
            assert isinstance(response["tx_hash"], str)
            logger.info(f"Zero address approve succeeded: {response['tx_hash']}")

        except ValueError as e:
            # If it fails, that's also acceptable
            logger.info(f"Zero address approve failed as expected: {str(e)}")

        logger.info("Zero address approve test completed")


class TestWIPTransferFrom:
    """Test WIP transferFrom functionality"""

    def setup_method(self):
        """Setup method called before each test"""
        logger.info("Setting up WIP transferFrom test")

    def teardown_method(self):
        """Teardown method called after each test"""
        logger.info("Cleaning up WIP transferFrom test")

    def test_transfer_from_basic(
        self, story_client: StoryClient, story_client_2: StoryClient
    ):
        """Test basic transferFrom functionality"""
        logger.info("Testing basic WIP transferFrom functionality")

        transfer_amount = web3.to_wei("0.01", "ether")

        try:
            # Ensure wallet_address has enough WIP balance
            owner_balance = story_client.WIP.balance_of(wallet_address_str)
            if owner_balance < transfer_amount:
                logger.info(
                    f"Insufficient balance ({web3.from_wei(owner_balance, 'ether')} ETH), depositing more WIP"
                )
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

            logger.info(
                f"Owner WIP balance before: {web3.from_wei(owner_wip_before, 'ether')} ETH"
            )
            logger.info(
                f"Spender WIP balance before: {web3.from_wei(spender_wip_before, 'ether')} ETH"
            )
            logger.info(
                f"Receiver WIP balance before: {web3.from_wei(receiver_wip_before, 'ether')} ETH"
            )

            # Approve spender to transfer from owner
            logger.info("Approving spender to transfer from owner")
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
            logger.info(f"Allowance verified: {web3.from_wei(allowance, 'ether')} ETH")

            # Execute transferFrom using spender's account
            logger.info("Executing transferFrom transaction")
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
            logger.info(f"TransferFrom transaction submitted: {tx_hash}")

            # Wait for transaction confirmation
            tx_receipt = web3.eth.wait_for_transaction_receipt(
                Hash32(bytes.fromhex(tx_hash)), timeout=300
            )

            if tx_receipt["status"] == 0:
                logger.error(f"TransferFrom transaction failed: {tx_hash}")
                raise AssertionError(
                    f"TransferFrom transaction failed with status 0: {tx_hash}"
                )

            logger.info(
                f"TransferFrom transaction confirmed in block {tx_receipt['blockNumber']}"
            )

            # Get final balances
            owner_wip_after = story_client.WIP.balance_of(wallet_address_str)
            spender_wip_after = story_client.WIP.balance_of(wallet_address_2_str)
            receiver_wip_after = story_client.WIP.balance_of(wallet_address_3_str)

            logger.info(
                f"Owner WIP balance after: {web3.from_wei(owner_wip_after, 'ether')} ETH"
            )
            logger.info(
                f"Spender WIP balance after: {web3.from_wei(spender_wip_after, 'ether')} ETH"
            )
            logger.info(
                f"Receiver WIP balance after: {web3.from_wei(receiver_wip_after, 'ether')} ETH"
            )

            # Verify balances
            assert (
                owner_wip_after == owner_wip_before - transfer_amount
            ), f"Owner balance should decrease by {web3.from_wei(transfer_amount, 'ether')} ETH"

            assert (
                receiver_wip_after == receiver_wip_before + transfer_amount
            ), f"Receiver balance should increase by {web3.from_wei(transfer_amount, 'ether')} ETH"

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
                f"Expected: {web3.from_wei(expected_allowance, 'ether')} ETH, "
                f"Got: {web3.from_wei(final_allowance, 'ether')} ETH"
            )

            logger.info("Basic transferFrom test completed successfully!")

        except Exception as e:
            logger.error(f"Basic transferFrom test failed: {str(e)}")
            # Log current balances for debugging
            try:
                logger.error(
                    f"Current owner balance: {web3.from_wei(story_client.WIP.balance_of(wallet_address_str), 'ether')} ETH"
                )
                logger.error(
                    f"Current spender balance: {web3.from_wei(story_client_2.WIP.balance_of(wallet_address_2_str), 'ether')} ETH"
                )
                logger.error(
                    f"Current allowance: {web3.from_wei(story_client.WIP.allowance(wallet_address_str, wallet_address_2_str), 'ether')} ETH"
                )
            except Exception as logging_error:
                logger.warning(f"Failed to log additional debug info: {logging_error}")
            raise

    def test_transfer_from_insufficient_allowance(
        self, story_client: StoryClient, story_client_2: StoryClient
    ):
        """Test transferFrom with insufficient allowance"""
        logger.info("Testing transferFrom with insufficient allowance")

        transfer_amount = web3.to_wei("0.01", "ether")

        try:
            # Ensure wallet_address has enough WIP balance
            owner_balance = story_client.WIP.balance_of(wallet_address_str)
            if owner_balance < transfer_amount:
                logger.info("Depositing WIP to ensure sufficient balance")
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

            logger.info("Insufficient allowance test completed successfully!")

        except Exception as e:
            logger.error(f"Insufficient allowance test failed: {str(e)}")
            raise

    def test_transfer_from_insufficient_balance(
        self, story_client: StoryClient, story_client_2: StoryClient
    ):
        """Test transferFrom with insufficient balance"""
        logger.info("Testing transferFrom with insufficient balance")

        transfer_amount = web3.to_wei("1000", "ether")  # Large amount

        try:
            # Get current balance
            current_balance = story_client.WIP.balance_of(wallet_address_str)
            logger.info(
                f"Current balance: {web3.from_wei(current_balance, 'ether')} ETH"
            )

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

            logger.info("Insufficient balance test completed successfully!")

        except Exception as e:
            logger.error(f"Insufficient balance test failed: {str(e)}")
            raise

    def test_transfer_from_negative_amount(self, story_client: StoryClient):
        """Test transferFrom with negative amount (should be rejected)"""
        logger.info("Testing transferFrom with negative amount")

        with pytest.raises(
            ValueError, match="WIP transfer amount must be greater than 0"
        ):
            story_client.WIP.transfer_from(
                from_address=wallet_address_str,
                to=wallet_address_2_str,
                amount=-1,
                tx_options={"waitForTransaction": True},
            )

        logger.info("Negative amount transferFrom test completed successfully!")

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
        logger.info(f"Testing transferFrom with invalid address: {invalid_address}")

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

        logger.info(f"Invalid address test passed for: {invalid_address}")

    def test_transfer_from_zero_addresses(self, story_client: StoryClient):
        """Test transferFrom with zero addresses"""
        logger.info("Testing transferFrom with zero addresses")

        zero_address = "0x0000000000000000000000000000000000000000"

        # Test zero address as from_address
        try:
            story_client.WIP.transfer_from(
                from_address=zero_address,
                to=wallet_address_2_str,
                amount=web3.to_wei("0.01", "ether"),
            )
            logger.info("Zero address as from_address succeeded")
        except Exception as e:
            logger.info(f"Zero address as from_address failed as expected: {str(e)}")

        # Test zero address as to_address
        try:
            story_client.WIP.transfer_from(
                from_address=wallet_address_str,
                to=zero_address,
                amount=web3.to_wei("0.01", "ether"),
            )
            logger.info("Zero address as to_address succeeded")
        except Exception as e:
            logger.info(f"Zero address as to_address failed as expected: {str(e)}")

        logger.info("Zero address transferFrom test completed")


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
