# tests/integration/test_integration_wip.py

from eth_typing import Hash32

from story_protocol_python_sdk.story_client import StoryClient

from .setup_for_integration import wallet_address, wallet_address_2, web3

# Type assertions to ensure wallet addresses are strings
assert wallet_address is not None, "wallet_address is required"
assert wallet_address_2 is not None, "wallet_address_2 is required"

# Type cast to satisfy mypy
wallet_address_str: str = wallet_address
wallet_address_2_str: str = wallet_address_2


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


class TestWIPApprove:
    """Test WIP approval functionality"""

    def test_approve(self, story_client: StoryClient):
        """Test basic approve functionality"""
        approve_amount = web3.to_wei(1, "wei")

        response = story_client.WIP.approve(
            spender=wallet_address_2_str,
            amount=approve_amount,
        )

        assert response is not None
        assert "tx_hash" in response
        assert isinstance(response["tx_hash"], str)

        # Verify allowance was set correctly
        final_allowance = story_client.WIP.allowance(
            owner=wallet_address_str, spender=wallet_address_2_str
        )
        assert final_allowance == approve_amount


class TestWIPTransferFrom:
    """Test WIP transferFrom functionality"""

    def test_transfer_from(
        self, story_client: StoryClient, story_client_2: StoryClient
    ):
        """Test basic transferFrom functionality"""
        transfer_amount = web3.to_wei("1", "wei")

        # Ensure wallet_address has enough WIP balance
        owner_balance = story_client.WIP.balance_of(wallet_address_str)
        if owner_balance < transfer_amount:
            deposit_amount = transfer_amount - owner_balance + web3.to_wei("1", "wei")
            story_client.WIP.deposit(amount=deposit_amount)

        # Get initial balances
        owner_wip_before = story_client.WIP.balance_of(wallet_address_str)
        spender_wip_before = story_client.WIP.balance_of(wallet_address_2_str)

        # Approve spender to transfer from owner
        story_client.WIP.approve(
            spender=wallet_address_2_str,
            amount=transfer_amount,
        )

        # Execute transferFrom using spender's account
        response = story_client_2.WIP.transfer_from(
            from_address=wallet_address_str,
            to=wallet_address_2_str,
            amount=transfer_amount,
        )

        assert response is not None
        assert "tx_hash" in response
        assert isinstance(response["tx_hash"], str)

        # Get final balances
        owner_wip_after = story_client.WIP.balance_of(wallet_address_str)
        spender_wip_after = story_client.WIP.balance_of(wallet_address_2_str)

        # Verify balances
        assert owner_wip_after == owner_wip_before - transfer_amount
        assert spender_wip_after == spender_wip_before + transfer_amount


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
