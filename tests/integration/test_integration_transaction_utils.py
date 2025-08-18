import time

import pytest
from web3.exceptions import TimeExhausted

from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction

from .setup_for_integration import MockERC20, account, web3


class TestTransactionUtils:
    """Integration tests for transaction utilities with custom nonce support."""

    def test_custom_nonce_with_sequential_transactions(self):
        """Test custom nonce works correctly with sequential transactions."""
        current_nonce = web3.eth.get_transaction_count(account.address, "pending")

        def create_transfer_tx(to_address, value):
            def build_tx(tx_options):
                return {
                    "to": to_address,
                    "value": value,
                    "data": "0x",
                    "gas": 21000,
                    "gasPrice": web3.eth.gas_price,
                    "chainId": 1315,
                    **tx_options,
                }

            return build_tx

        tx_func = create_transfer_tx(account.address, 0)
        result = build_and_send_transaction(
            web3, account, tx_func, tx_options={"nonce": current_nonce}
        )

        assert result["tx_receipt"]["status"] == 1
        tx = web3.eth.get_transaction(result["tx_hash"])
        assert tx["nonce"] == current_nonce

    def test_automatic_nonce_fallback(self):
        """Test backward compatibility - automatic nonce when not specified."""

        def create_transfer_tx(to_address, value):
            def build_tx(tx_options):
                return {
                    "to": to_address,
                    "value": value,
                    "data": "0x",
                    "gas": 21000,
                    "gasPrice": web3.eth.gas_price,
                    "chainId": 1315,
                    **tx_options,
                }

            return build_tx

        tx_func = create_transfer_tx(account.address, 0)
        result = build_and_send_transaction(web3, account, tx_func, tx_options={})

        assert result["tx_receipt"]["status"] == 1
        tx = web3.eth.get_transaction(result["tx_hash"])
        assert tx["nonce"] >= 0

    def test_invalid_nonce_validation(self):
        """Test that invalid nonce values are properly rejected."""

        def dummy_func(tx_options):
            return {
                "to": account.address,
                "value": 0,
                "data": "0x",
                "gas": 21000,
                "gasPrice": web3.eth.gas_price,
                "chainId": 1315,
                **tx_options,
            }

        invalid_nonces = [
            (-1, "negative"),
            ("10", "string"),
            (10.5, "float"),
            (None, "None"),
        ]

        for nonce_value, nonce_type in invalid_nonces:
            with pytest.raises(ValueError) as exc_info:
                build_and_send_transaction(
                    web3, account, dummy_func, tx_options={"nonce": nonce_value}
                )
            assert "Invalid nonce value" in str(exc_info.value)
            assert "must be a non-negative integer" in str(exc_info.value)

    def test_nonce_with_contract_interaction(self):
        """Test custom nonce works with actual contract calls."""
        erc20_contract = web3.eth.contract(
            address=MockERC20,
            abi=[
                {
                    "inputs": [
                        {"name": "spender", "type": "address"},
                        {"name": "amount", "type": "uint256"},
                    ],
                    "name": "approve",
                    "outputs": [{"name": "", "type": "bool"}],
                    "stateMutability": "nonpayable",
                    "type": "function",
                }
            ],
        )

        current_nonce = web3.eth.get_transaction_count(account.address)

        def approve_func(tx_options):
            return erc20_contract.functions.approve(
                account.address, 100
            ).build_transaction(tx_options)

        result = build_and_send_transaction(
            web3, account, approve_func, tx_options={"nonce": current_nonce}
        )

        assert result["tx_receipt"]["status"] == 1
        tx = web3.eth.get_transaction(result["tx_hash"])
        assert tx["nonce"] == current_nonce

    def test_wait_for_receipt_false_returns_only_tx_hash(self):
        """Test that wait_for_receipt=False returns immediately with only tx_hash."""

        def create_transfer_tx(to_address, value):
            def build_tx(tx_options):
                return {
                    "to": to_address,
                    "value": value,
                    "data": "0x",
                    "gas": 21000,
                    "gasPrice": web3.eth.gas_price,
                    "chainId": 1315,
                    **tx_options,
                }

            return build_tx

        tx_func = create_transfer_tx(account.address, 0)
        result = build_and_send_transaction(
            web3, account, tx_func, tx_options={"wait_for_receipt": False}
        )
        assert "tx_hash" in result
        assert "tx_receipt" not in result
        assert len(result["tx_hash"]) == 64

        tx_receipt = web3.eth.wait_for_transaction_receipt(result["tx_hash"])
        assert tx_receipt["status"] == 1

    def test_wait_for_receipt_true_returns_receipt(self):
        """Test that wait_for_receipt=True (default) returns both tx_hash and receipt."""

        def create_transfer_tx(to_address, value):
            def build_tx(tx_options):
                return {
                    "to": to_address,
                    "value": value,
                    "data": "0x",
                    "gas": 21000,
                    "gasPrice": web3.eth.gas_price,
                    "chainId": 1315,
                    **tx_options,
                }

            return build_tx

        tx_func = create_transfer_tx(account.address, 0)
        result = build_and_send_transaction(
            web3, account, tx_func, tx_options={"wait_for_receipt": True}
        )

        assert "tx_hash" in result
        assert "tx_receipt" in result
        assert result["tx_receipt"]["status"] == 1
        assert "blockNumber" in result["tx_receipt"]
        assert "gasUsed" in result["tx_receipt"]

    def test_custom_timeout_with_transaction(self):
        """Test that custom timeout is used when specified."""

        def create_transfer_tx(to_address, value):
            def build_tx(tx_options):
                return {
                    "to": to_address,
                    "value": value,
                    "data": "0x",
                    "gas": 21000,
                    "gasPrice": web3.eth.gas_price,
                    "chainId": 1315,
                    **tx_options,
                }

            return build_tx

        tx_func = create_transfer_tx(account.address, 0)
        result = build_and_send_transaction(
            web3,
            account,
            tx_func,
            tx_options={"wait_for_receipt": True, "timeout": 120},
        )

        assert "tx_hash" in result
        assert "tx_receipt" in result
        assert result["tx_receipt"]["status"] == 1

    def test_combined_options_nonce_wait_timeout(self):
        """Test that all new options work correctly together."""
        current_nonce = web3.eth.get_transaction_count(account.address)

        def create_transfer_tx(to_address, value):
            def build_tx(tx_options):
                return {
                    "to": to_address,
                    "value": value,
                    "data": "0x",
                    "gas": 21000,
                    "gasPrice": web3.eth.gas_price,
                    "chainId": 1315,
                    **tx_options,
                }

            return build_tx

        tx_func = create_transfer_tx(account.address, 0)
        result = build_and_send_transaction(
            web3,
            account,
            tx_func,
            tx_options={
                "nonce": current_nonce,
                "wait_for_receipt": True,
                "timeout": 120,
            },
        )

        assert "tx_hash" in result
        assert "tx_receipt" in result
        assert result["tx_receipt"]["status"] == 1

        tx = web3.eth.get_transaction(result["tx_hash"])
        assert tx["nonce"] == current_nonce

    def test_wait_for_receipt_false_with_contract_call(self):
        """Test wait_for_receipt=False with actual contract interaction."""
        erc20_contract = web3.eth.contract(
            address=MockERC20,
            abi=[
                {
                    "inputs": [
                        {"name": "spender", "type": "address"},
                        {"name": "amount", "type": "uint256"},
                    ],
                    "name": "approve",
                    "outputs": [{"name": "", "type": "bool"}],
                    "stateMutability": "nonpayable",
                    "type": "function",
                }
            ],
        )

        def approve_func(tx_options):
            return erc20_contract.functions.approve(
                account.address, 200
            ).build_transaction(tx_options)

        time.time()
        result = build_and_send_transaction(
            web3, account, approve_func, tx_options={"wait_for_receipt": False}
        )

        assert "tx_hash" in result
        assert "tx_receipt" not in result

        tx_receipt = web3.eth.wait_for_transaction_receipt(result["tx_hash"])
        assert tx_receipt["status"] == 1

    def test_timeout_too_short_raises_exception(self):
        """Test that very short timeout raises TimeExhausted exception."""

        def build_tx(tx_options):
            return {
                "to": account.address,
                "value": 0,
                "data": "0x",
                "gas": 21000,
                "gasPrice": web3.eth.gas_price,
                "chainId": 1315,
                **tx_options,
            }

        with pytest.raises(TimeExhausted):
            build_and_send_transaction(
                web3,
                account,
                build_tx,
                tx_options={"wait_for_receipt": True, "timeout": 0.001},
            )
