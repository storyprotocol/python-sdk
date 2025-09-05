from unittest.mock import MagicMock, Mock, patch

import pytest
from eth_account import Account
from web3 import Web3

from tests.unit.fixtures.data import ACCOUNT_ADDRESS, ADDRESS, TX_HASH


@pytest.fixture(scope="package")
def mock_account():
    account = MagicMock()
    account.address = ACCOUNT_ADDRESS  # Create a mock signed transaction object with raw_transaction attribute
    mock_signed_txn = MagicMock()
    mock_signed_txn.raw_transaction = b"raw_transaction_bytes"

    account.sign_transaction = MagicMock(return_value=mock_signed_txn)
    account.sign_message = MagicMock(return_value=b"mock_signature")
    return account


@pytest.fixture(scope="package")
def mock_web3():
    mock_web3 = Mock(spec=Web3)
    mock_web3.to_checksum_address = MagicMock(return_value=ADDRESS)
    mock_web3.to_bytes = MagicMock(return_value=b"mock_bytes")

    # Add eth attribute with contract method
    mock_eth = Mock()

    # Create a function that returns a new mock contract each time
    def create_mock_contract(*args, **kwargs):
        """Create a new mock contract instance with address"""
        mock_contract = Mock()
        mock_contract.address = ADDRESS
        mock_contract.encode_abi = MagicMock(return_value="0x00")
        return mock_contract

    # Set up the contract method to return new mock contracts
    mock_eth.contract = create_mock_contract
    mock_web3.eth = mock_eth
    mock_web3.eth.get_transaction_count = MagicMock(return_value=0)
    mock_web3.eth.send_raw_transaction = MagicMock(return_value=TX_HASH)
    mock_web3.eth.wait_for_transaction_receipt = MagicMock(
        return_value={"status": 1, "logs": []}
    )
    mock_web3.to_wei = MagicMock(return_value=1)
    return mock_web3


@pytest.fixture(scope="package")
def mock_is_checksum_address():
    def _mock(is_checksum_address: bool = True):
        return patch.object(
            Web3, "is_checksum_address", return_value=is_checksum_address
        )

    return _mock


@pytest.fixture(scope="package")
def mock_signature_related_methods():
    class SignatureMockContext:
        def __init__(self):
            self.patches = []

        def __enter__(self):
            # Mock the IPAccountImplClient constructor and its contract.encode_abi method
            mock_client = MagicMock()
            mock_contract = MagicMock()
            mock_contract.encode_abi = MagicMock(return_value=b"encoded_data")
            mock_client.contract = mock_contract

            # Create all the patches
            mock_web3_to_bytes = patch.object(
                Web3, "to_bytes", return_value=b"mock_bytes"
            )
            mock_account_sign_message = patch.object(
                Account,
                "sign_message",
                return_value=MagicMock(signature=b"mock_signature"),
            )

            # Create a mock class that behaves like IPAccountImplClient
            class MockIPAccountImplClient:
                def __init__(self, web3, contract_address=None):
                    self.web3 = web3
                    self.contract_address = contract_address
                    self.contract = mock_contract

            # Patch the class to return our mock instance
            mock_ip_account_client = patch(
                "story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client.IPAccountImplClient",
                MockIPAccountImplClient,
            )

            # Apply all patches at once
            mock_web3_to_bytes.start()
            mock_account_sign_message.start()
            mock_ip_account_client.start()

            # Store patches for cleanup
            self.patches = [
                mock_web3_to_bytes,
                mock_account_sign_message,
                mock_ip_account_client,
            ]

        def __exit__(self, exc_type, exc_val, exc_tb):
            # Stop all patches in reverse order
            for patch_obj in reversed(self.patches):
                patch_obj.stop()

    return SignatureMockContext


@pytest.fixture(scope="package")
def mock_license_registry_client():
    """Fixture to mock LicenseRegistryClient for derivative data validation"""

    def _mock():
        # Create a mock that returns a proper value for getRoyaltyPercent
        mock_client = MagicMock()
        mock_client.hasIpAttachedLicenseTerms = MagicMock(return_value=True)
        mock_client.getRoyaltyPercent = MagicMock(return_value=10)

        # Patch both IPAsset and derivative_data modules
        patch1 = patch(
            "story_protocol_python_sdk.resources.IPAsset.LicenseRegistryClient",
            return_value=mock_client,
        )
        patch2 = patch(
            "story_protocol_python_sdk.utils.derivative_data.LicenseRegistryClient",
            return_value=mock_client,
        )

        # Start both patches
        patch1.start()
        patch2.start()

        # Return a context manager that stops both patches
        class MockContext:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                patch1.stop()
                patch2.stop()

        return MockContext()

    return _mock


@pytest.fixture(scope="module")
def mock_web3_is_address(mock_web3):
    def _mock(is_address: bool = True):
        return patch.object(mock_web3, "is_address", return_value=is_address)

    return _mock
