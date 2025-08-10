from unittest.mock import Mock

import pytest
from web3 import Web3

from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction


class TestBuildAndSendTransaction:
    """Test suite for build_and_send_transaction function."""

    @pytest.fixture
    def mock_web3(self):
        """Create a mock Web3 instance."""
        web3 = Mock(spec=Web3)
        web3.eth = Mock()
        web3.to_wei = Mock(side_effect=lambda value, unit: value * 1000000000)
        return web3

    @pytest.fixture
    def mock_account(self):
        """Create a mock account."""
        account = Mock()
        account.address = "0x1234567890123456789012345678901234567890"
        account.sign_transaction = Mock()
        return account

    @pytest.fixture
    def mock_client_function(self):
        """Create a mock client function."""
        return Mock(return_value={"to": "0xabc", "data": "0x123"})

    def test_custom_nonce_is_used(self, mock_web3, mock_account, mock_client_function):
        """Test that custom nonce from tx_options is used when provided."""
        custom_nonce = 42
        tx_options = {"nonce": custom_nonce}
        mock_web3.eth.get_transaction_count.return_value = 10  # Should not be used
        mock_web3.eth.send_raw_transaction.return_value = Mock(
            hex=Mock(return_value="0xhash")
        )
        mock_web3.eth.wait_for_transaction_receipt.return_value = {"status": 1}
        mock_account.sign_transaction.return_value = Mock(raw_transaction=b"signed_tx")

        build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options=tx_options,
        )
        # Verify the client function was called with correct nonce
        mock_client_function.assert_called_once()
        call_args = mock_client_function.call_args[0][-1]
        assert call_args["nonce"] == custom_nonce
        # When custom nonce is provided, get_transaction_count should not be called
        mock_web3.eth.get_transaction_count.assert_not_called()

    def test_automatic_nonce_fetch_when_not_provided(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that nonce is fetched from chain when not provided in tx_options."""
        chain_nonce = 25
        mock_web3.eth.get_transaction_count.return_value = chain_nonce
        mock_web3.eth.send_raw_transaction.return_value = Mock(
            hex=Mock(return_value="0xhash")
        )
        mock_web3.eth.wait_for_transaction_receipt.return_value = {"status": 1}
        mock_account.sign_transaction.return_value = Mock(raw_transaction=b"signed_tx")

        build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options={},
        )

        mock_web3.eth.get_transaction_count.assert_called_once_with(
            mock_account.address
        )
        mock_client_function.assert_called_once()
        call_args = mock_client_function.call_args[0][-1]
        assert call_args["nonce"] == chain_nonce

    def test_nonce_validation_negative_value_raises_error(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that negative nonce values raise ValueError."""
        tx_options = {"nonce": -1}

        with pytest.raises(ValueError) as exc_info:
            build_and_send_transaction(
                mock_web3,
                mock_account,
                mock_client_function,
                tx_options=tx_options,
            )

        assert "Invalid nonce value: -1" in str(exc_info.value)
        assert "must be a non-negative integer" in str(exc_info.value)

    def test_nonce_validation_string_value_raises_error(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that string nonce values raise ValueError."""
        tx_options = {"nonce": "123"}

        with pytest.raises(ValueError) as exc_info:
            build_and_send_transaction(
                mock_web3,
                mock_account,
                mock_client_function,
                tx_options=tx_options,
            )

        assert "Invalid nonce value: 123" in str(exc_info.value)
        assert "must be a non-negative integer" in str(exc_info.value)

    def test_nonce_validation_float_value_raises_error(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that float nonce values raise ValueError."""
        tx_options = {"nonce": 42.5}

        with pytest.raises(ValueError) as exc_info:
            build_and_send_transaction(
                mock_web3,
                mock_account,
                mock_client_function,
                tx_options=tx_options,
            )

        assert "Invalid nonce value: 42.5" in str(exc_info.value)
        assert "must be a non-negative integer" in str(exc_info.value)

    def test_nonce_validation_none_value_raises_error(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that None nonce values raise ValueError."""
        tx_options = {"nonce": None}

        with pytest.raises(ValueError) as exc_info:
            build_and_send_transaction(
                mock_web3,
                mock_account,
                mock_client_function,
                tx_options=tx_options,
            )

        assert "Invalid nonce value: None" in str(exc_info.value)
        assert "must be a non-negative integer" in str(exc_info.value)

    def test_zero_nonce_is_valid(self, mock_web3, mock_account, mock_client_function):
        """Test that zero nonce is accepted as valid."""
        custom_nonce = 0
        tx_options = {"nonce": custom_nonce}
        mock_web3.eth.send_raw_transaction.return_value = Mock(
            hex=Mock(return_value="0xhash")
        )
        mock_web3.eth.wait_for_transaction_receipt.return_value = {"status": 1}
        mock_account.sign_transaction.return_value = Mock(raw_transaction=b"signed_tx")

        build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options=tx_options,
        )

        mock_client_function.assert_called_once()
        call_args = mock_client_function.call_args[0][-1]
        assert call_args["nonce"] == 0

    def test_large_nonce_is_valid(self, mock_web3, mock_account, mock_client_function):
        """Test that large nonce values are accepted."""
        custom_nonce = 999999999
        tx_options = {"nonce": custom_nonce}
        mock_web3.eth.send_raw_transaction.return_value = Mock(
            hex=Mock(return_value="0xhash")
        )
        mock_web3.eth.wait_for_transaction_receipt.return_value = {"status": 1}
        mock_account.sign_transaction.return_value = Mock(raw_transaction=b"signed_tx")

        build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options=tx_options,
        )

        mock_client_function.assert_called_once()
        call_args = mock_client_function.call_args[0][-1]
        assert call_args["nonce"] == custom_nonce

    def test_nonce_with_other_tx_options(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that nonce works correctly alongside other transaction options."""
        tx_options = {
            "nonce": 42,
            "value": 1000,
            "gasPrice": 20,
        }
        mock_web3.eth.send_raw_transaction.return_value = Mock(
            hex=Mock(return_value="0xhash")
        )
        mock_web3.eth.wait_for_transaction_receipt.return_value = {"status": 1}
        mock_account.sign_transaction.return_value = Mock(raw_transaction=b"signed_tx")

        build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options=tx_options,
        )

        mock_client_function.assert_called_once()
        call_args = mock_client_function.call_args[0][-1]
        assert call_args["nonce"] == 42
        assert call_args["value"] == 1000
        assert call_args["gasPrice"] == 20000000000  # 20 gwei in wei

    def test_encoded_tx_data_only_with_custom_nonce(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that custom nonce works with encodedTxDataOnly option."""
        custom_nonce = 42
        tx_options = {
            "nonce": custom_nonce,
            "encodedTxDataOnly": True,
        }
        expected_tx = {"to": "0xabc", "data": "0x123", "nonce": custom_nonce}
        mock_client_function.return_value = expected_tx

        result = build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options=tx_options,
        )

        assert result == {"encodedTxData": expected_tx}
        mock_client_function.assert_called_once()
        call_args = mock_client_function.call_args[0][-1]
        assert call_args["nonce"] == custom_nonce
        # Verify transaction was not sent
        mock_account.sign_transaction.assert_not_called()
        mock_web3.eth.send_raw_transaction.assert_not_called()

    def test_no_tx_options_uses_default_nonce(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that when tx_options is None, nonce is fetched from chain."""
        chain_nonce = 15
        mock_web3.eth.get_transaction_count.return_value = chain_nonce
        mock_web3.eth.send_raw_transaction.return_value = Mock(
            hex=Mock(return_value="0xhash")
        )
        mock_web3.eth.wait_for_transaction_receipt.return_value = {"status": 1}
        mock_account.sign_transaction.return_value = Mock(raw_transaction=b"signed_tx")

        build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options=None,  # Explicitly passing None
        )

        mock_web3.eth.get_transaction_count.assert_called_once_with(
            mock_account.address
        )
        mock_client_function.assert_called_once()
        call_args = mock_client_function.call_args[0][-1]
        assert call_args["nonce"] == chain_nonce
