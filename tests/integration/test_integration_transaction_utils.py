# tests/integration/test_integration_transaction_utils.py

import pytest

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
