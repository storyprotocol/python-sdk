from unittest.mock import Mock

import pytest
from web3.exceptions import TimeExhausted

from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction


class TestBuildAndSendTransaction:
    """Test suite for build_and_send_transaction function."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self, mock_web3, mock_account):
        """Configure and reset the mocks from conftest for our specific needs."""
        mock_web3.reset_mock()
        mock_web3.eth.reset_mock()
        mock_account.reset_mock()
        mock_web3.to_wei = Mock(side_effect=lambda value, unit: value * 1000000000)

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
        mock_client_function.assert_called_once()
        call_args = mock_client_function.call_args[0][-1]
        assert call_args["nonce"] == custom_nonce
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

    def test_wait_for_receipt_default_true(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that wait_for_receipt defaults to True for backward compatibility."""
        mock_web3.eth.get_transaction_count.return_value = 10
        mock_web3.eth.send_raw_transaction.return_value = Mock(
            hex=Mock(return_value="0xhash123")
        )
        mock_web3.eth.wait_for_transaction_receipt.return_value = {"status": 1}
        mock_account.sign_transaction.return_value = Mock(raw_transaction=b"signed_tx")

        result = build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options={},
        )

        mock_web3.eth.wait_for_transaction_receipt.assert_called_once()
        assert "tx_hash" in result
        assert "tx_receipt" in result
        assert result["tx_receipt"] == {"status": 1}

    def test_wait_for_receipt_false_returns_immediately(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that wait_for_receipt=False returns immediately without waiting."""
        mock_web3.eth.get_transaction_count.return_value = 10
        mock_web3.eth.send_raw_transaction.return_value = Mock(
            hex=Mock(return_value="0xhash456")
        )
        mock_account.sign_transaction.return_value = Mock(raw_transaction=b"signed_tx")

        result = build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options={"wait_for_receipt": False},
        )

        mock_web3.eth.wait_for_transaction_receipt.assert_not_called()
        assert "tx_hash" in result
        assert result["tx_hash"] == "0xhash456"
        assert "tx_receipt" not in result

    def test_custom_timeout_is_used(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that custom timeout from tx_options is used when provided."""
        custom_timeout = 60
        mock_web3.eth.get_transaction_count.return_value = 10
        mock_web3.eth.send_raw_transaction.return_value = Mock(
            hex=Mock(return_value="0xhash789")
        )
        mock_web3.eth.wait_for_transaction_receipt.return_value = {"status": 1}
        mock_account.sign_transaction.return_value = Mock(raw_transaction=b"signed_tx")

        result = build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options={"timeout": custom_timeout},
        )

        mock_web3.eth.wait_for_transaction_receipt.assert_called_once_with(
            mock_web3.eth.send_raw_transaction.return_value, timeout=custom_timeout
        )
        assert "tx_hash" in result
        assert "tx_receipt" in result

    def test_timeout_ignored_when_not_waiting_for_receipt(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that timeout is ignored when wait_for_receipt is False."""
        mock_web3.eth.get_transaction_count.return_value = 10
        mock_web3.eth.send_raw_transaction.return_value = Mock(
            hex=Mock(return_value="0xhashabc")
        )
        mock_account.sign_transaction.return_value = Mock(raw_transaction=b"signed_tx")

        result = build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options={"wait_for_receipt": False, "timeout": 60},
        )

        mock_web3.eth.wait_for_transaction_receipt.assert_not_called()
        assert "tx_hash" in result
        assert "tx_receipt" not in result

    def test_wait_for_receipt_with_custom_nonce_and_timeout(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that wait_for_receipt works correctly with other options."""
        tx_options = {
            "nonce": 42,
            "wait_for_receipt": True,
            "timeout": 120,
            "value": 1000,
        }
        mock_web3.eth.send_raw_transaction.return_value = Mock(
            hex=Mock(return_value="0xhashdef")
        )
        mock_web3.eth.wait_for_transaction_receipt.return_value = {"status": 1}
        mock_account.sign_transaction.return_value = Mock(raw_transaction=b"signed_tx")

        result = build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options=tx_options,
        )

        mock_client_function.assert_called_once()
        call_args = mock_client_function.call_args[0][-1]
        assert call_args["nonce"] == 42
        assert call_args["value"] == 1000

        mock_web3.eth.wait_for_transaction_receipt.assert_called_once_with(
            mock_web3.eth.send_raw_transaction.return_value, timeout=120
        )
        assert "tx_hash" in result
        assert "tx_receipt" in result

    def test_default_timeout_used_when_not_specified(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that default TRANSACTION_TIMEOUT is used when timeout not specified."""
        from story_protocol_python_sdk.utils.transaction_utils import (
            TRANSACTION_TIMEOUT,
        )

        mock_web3.eth.get_transaction_count.return_value = 10
        mock_web3.eth.send_raw_transaction.return_value = Mock(
            hex=Mock(return_value="0xhash999")
        )
        mock_web3.eth.wait_for_transaction_receipt.return_value = {"status": 1}
        mock_account.sign_transaction.return_value = Mock(raw_transaction=b"signed_tx")

        result = build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options={"wait_for_receipt": True},  # No timeout specified
        )

        mock_web3.eth.wait_for_transaction_receipt.assert_called_once_with(
            mock_web3.eth.send_raw_transaction.return_value, timeout=TRANSACTION_TIMEOUT
        )
        assert "tx_hash" in result
        assert "tx_receipt" in result

    def test_wait_for_receipt_false_with_encoded_tx_data(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that encodedTxDataOnly takes precedence over wait_for_receipt."""
        tx_options = {
            "wait_for_receipt": False,
            "encodedTxDataOnly": True,
        }
        expected_tx = {"to": "0xabc", "data": "0x123"}
        mock_client_function.return_value = expected_tx

        result = build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options=tx_options,
        )

        assert result == {"encodedTxData": expected_tx}
        mock_account.sign_transaction.assert_not_called()
        mock_web3.eth.send_raw_transaction.assert_not_called()
        mock_web3.eth.wait_for_transaction_receipt.assert_not_called()

    def test_very_short_timeout_value(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that very short timeout values are accepted."""
        mock_web3.eth.get_transaction_count.return_value = 10
        mock_web3.eth.send_raw_transaction.return_value = Mock(
            hex=Mock(return_value="0xhashxyz")
        )
        mock_web3.eth.wait_for_transaction_receipt.return_value = {"status": 1}
        mock_account.sign_transaction.return_value = Mock(raw_transaction=b"signed_tx")

        result = build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options={"timeout": 1},  # 1 second timeout
        )

        mock_web3.eth.wait_for_transaction_receipt.assert_called_once_with(
            mock_web3.eth.send_raw_transaction.return_value, timeout=1
        )
        assert "tx_hash" in result
        assert "tx_receipt" in result

    def test_float_timeout_value(self, mock_web3, mock_account, mock_client_function):
        """Test that float timeout values are accepted."""
        mock_web3.eth.get_transaction_count.return_value = 10
        mock_web3.eth.send_raw_transaction.return_value = Mock(
            hex=Mock(return_value="0xhashfloat")
        )
        mock_web3.eth.wait_for_transaction_receipt.return_value = {"status": 1}
        mock_account.sign_transaction.return_value = Mock(raw_transaction=b"signed_tx")

        result = build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options={"timeout": 45.5},  # Float timeout
        )

        mock_web3.eth.wait_for_transaction_receipt.assert_called_once_with(
            mock_web3.eth.send_raw_transaction.return_value, timeout=45.5
        )
        assert "tx_hash" in result
        assert "tx_receipt" in result

    def test_wait_for_receipt_explicitly_true(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test explicitly setting wait_for_receipt to True."""
        mock_web3.eth.get_transaction_count.return_value = 10
        mock_web3.eth.send_raw_transaction.return_value = Mock(
            hex=Mock(return_value="0xhashexplicit")
        )
        mock_web3.eth.wait_for_transaction_receipt.return_value = {
            "status": 1,
            "blockNumber": 12345,
        }
        mock_account.sign_transaction.return_value = Mock(raw_transaction=b"signed_tx")

        result = build_and_send_transaction(
            mock_web3,
            mock_account,
            mock_client_function,
            tx_options={"wait_for_receipt": True},
        )

        mock_web3.eth.wait_for_transaction_receipt.assert_called_once()
        assert result["tx_hash"] == "0xhashexplicit"
        assert result["tx_receipt"]["status"] == 1
        assert result["tx_receipt"]["blockNumber"] == 12345

    def test_timeout_exception_is_propagated(
        self, mock_web3, mock_account, mock_client_function
    ):
        """Test that TimeExhausted exception is properly propagated when timeout occurs."""
        mock_web3.eth.get_transaction_count.return_value = 10
        mock_web3.eth.send_raw_transaction.return_value = Mock(
            hex=Mock(return_value="0xhashtimeout")
        )
        mock_web3.eth.wait_for_transaction_receipt.side_effect = TimeExhausted(
            "Transaction receipt not found after 0.5 seconds"
        )
        mock_account.sign_transaction.return_value = Mock(raw_transaction=b"signed_tx")

        with pytest.raises(TimeExhausted):
            build_and_send_transaction(
                mock_web3,
                mock_account,
                mock_client_function,
                tx_options={"wait_for_receipt": True, "timeout": 0.5},
            )
        mock_web3.eth.wait_for_transaction_receipt.assert_called_once_with(
            mock_web3.eth.send_raw_transaction.return_value, timeout=0.5
        )
