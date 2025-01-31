import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from web3 import Web3
from web3.exceptions import InvalidAddress
from eth_utils import is_address, to_checksum_address

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from src.story_protocol_python_sdk.resources.IPAccount import IPAccount

# Constants
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
VALID_IP_ID = "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"
TX_HASH = "0xe87b172eee35872179ced53ea4f3f314b12cd0f5d0034e7f0ae3c4efce9ba6f1"

# Web3 mock
class MockWeb3:
    def __init__(self):
        self.eth = MagicMock()
        
    @staticmethod
    def to_checksum_address(address):
        if not is_address(address):
            raise ValueError(f"The recipient of the transaction {address} is not a valid address")
        return to_checksum_address(address)
    
    @staticmethod
    def to_bytes(hexstr=None, **kwargs):
        return Web3.to_bytes(hexstr=hexstr, **kwargs)
    
    @staticmethod
    def to_wei(number, unit):
        return Web3.to_wei(number, unit)
    
    @staticmethod
    def is_address(address):
        return is_address(address)
        
    def is_connected(self):
        return True
    
@pytest.fixture
def mock_web3():
    return MockWeb3()

@pytest.fixture
def mock_account():
    account = MagicMock()
    account.address = "0xF60cBF0Ea1A61567F1dDaf79A6219D20d189155c"
    return account

@pytest.fixture
def ip_account(mock_web3, mock_account):
    chain_id = 11155111  # Sepolia chain ID
    return IPAccount(mock_web3, mock_account, chain_id)

@pytest.mark.unit
@pytest.mark.unit
@pytest.mark.unit
class TestExecute:
    def test_invalid_recipient_address(self, ip_account):
        with pytest.raises(ValueError) as exc_info:
            ip_account.execute("0xInvalidAddress", 1, VALID_IP_ID, "0x11111111111111111111111111111")
        assert "The recipient of the transaction 0xInvalidAddress is not a valid address" in str(exc_info.value)

    def test_unregistered_ip_account(self, ip_account):
        with patch.object(ip_account, '_is_registered', return_value=False):
            with pytest.raises(ValueError) as exc_info:
                ip_account.execute(ZERO_ADDRESS, 1, VALID_IP_ID, "0x11111111111111111111111111111")
            assert f"The IP id {VALID_IP_ID} is not registered" in str(exc_info.value)

    def test_successful_transaction(self, ip_account):
        to_address = "0xF9936a224b3Deb6f9A4645ccAfa66f7ECe83CF0A"
        data = "0x11111111111111111111111111111"
        value = 2

        # Mock signed transaction
        mock_signed_txn = MagicMock()
        mock_signed_txn.raw_transaction = b'raw_transaction_bytes'

        # Mock transaction hash with hex method that returns hash WITHOUT '0x' prefix
        class MockTxHash:
            def hex(self):
                return TX_HASH[2:]  # Remove '0x' prefix when returning the hash

        mock_tx_hash = MockTxHash()

        
        ip_account.account.sign_transaction = MagicMock(return_value=mock_signed_txn)

        with patch.object(ip_account, '_is_registered', return_value=True), \
            patch.object(ip_account.web3.eth, 'get_transaction_count', return_value=0), \
            patch.object(ip_account.web3.eth, 'send_raw_transaction', return_value=mock_tx_hash), \
            patch.object(ip_account.web3.eth, 'wait_for_transaction_receipt', return_value={'status': 1}):

            response = ip_account.execute(to_address, value, VALID_IP_ID, data)
            assert response['txHash'] == TX_HASH[2:]

    def test_wait_for_transaction(self, ip_account):
        to_address = "0xF9936a224b3Deb6f9A4645ccAfa66f7ECe83CF0A"
        data = "0x11111111111111111111111111111"
        value = 2
        tx_options = {'waitForTransaction': True}

        mock_signed_txn = MagicMock()
        mock_signed_txn.raw_transaction = b'raw_transaction_bytes'

        class MockTxHash:
            def hex(self):
                return TX_HASH[2:]  # Remove '0x' prefix when returning the hash

        mock_tx_hash = MockTxHash()

        ip_account.account.sign_transaction = MagicMock(return_value=mock_signed_txn)

        with patch.object(ip_account, '_is_registered', return_value=True), \
             patch.object(ip_account.web3.eth, 'get_transaction_count', return_value=0), \
             patch.object(ip_account.web3.eth, 'send_raw_transaction', return_value=mock_tx_hash), \
             patch.object(ip_account.web3.eth, 'wait_for_transaction_receipt', return_value={'status': 1}):

            response = ip_account.execute(to_address, value, VALID_IP_ID, data, tx_options=tx_options)
            assert response['txHash'] == TX_HASH[2:]

    def test_encoded_tx_data_only(self, ip_account):
        to_address = "0xF9936a224b3Deb6f9A4645ccAfa66f7ECe83CF0A"
        data = "0x11111111111111111111111111111"
        value = 2
        tx_options = {'encodedTxDataOnly': True}
        encoded_data = "0x123456789"

        mock_tx = {
            'to': to_address,
            'value': value,
            'data': encoded_data,
            'gas': 2000000,
            'gasPrice': Web3.to_wei('50', 'gwei'),
            'nonce': 0,
            'chainId': 11155111
        }

        with patch.object(ip_account, '_is_registered', return_value=True), \
            patch('story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client.IPAccountImplClient.build_execute_transaction',
                return_value=mock_tx), \
            patch('web3.eth.Eth.get_transaction_count',
                return_value=0):

            response = ip_account.execute(to_address, value, VALID_IP_ID, data, tx_options=tx_options)
            assert 'encodedTxData' in response
            assert response['encodedTxData'] == mock_tx

class TestExecuteWithSig:
    def test_invalid_recipient_address(self, ip_account):
        with pytest.raises(ValueError) as exc_info:
            ip_account.executeWithSig(
                VALID_IP_ID, 
                "0xInvalidAddress", 
                "0x11111111111111111111111111111",
                ZERO_ADDRESS,
                20,
                ZERO_ADDRESS
            )
        assert "The recipient of the transaction 0xInvalidAddress is not a valid address" in str(exc_info.value)

    def test_successful_transaction_with_sig(self, ip_account):
        to_address = "0xF9936a224b3Deb6f9A4645ccAfa66f7ECe83CF0A"
        data = "0x11111111111111111111111111111"
        value = 2
        signer = "0xF60cBF0Ea1A61567F1dDaf79A6219D20d189155c"
        deadline = 20
        signature = "0x11111111111111111111111111111"

        mock_signed_txn = MagicMock()
        mock_signed_txn.raw_transaction = b'raw_transaction_bytes'

        class MockTxHash:
            def hex(self):
                return TX_HASH[2:] 

        mock_tx_hash = MockTxHash()
        
        ip_account.account.sign_transaction = MagicMock(return_value=mock_signed_txn)

        with patch.object(ip_account, '_is_registered', return_value=True), \
             patch.object(ip_account.web3.eth, 'get_transaction_count', return_value=0), \
             patch.object(ip_account.web3.eth, 'send_raw_transaction', return_value=mock_tx_hash), \
             patch.object(ip_account.web3.eth, 'wait_for_transaction_receipt', return_value={'status': 1}):

            response = ip_account.executeWithSig(VALID_IP_ID, to_address, data, signer, deadline, signature, value)
            assert response['txHash'] == TX_HASH[2:]

    def test_wait_for_transaction_with_sig(self, ip_account):
        to_address = "0xF9936a224b3Deb6f9A4645ccAfa66f7ECe83CF0A"
        data = "0x11111111111111111111111111111"
        signer = ZERO_ADDRESS
        deadline = 20
        signature = ZERO_ADDRESS
        tx_options = {'waitForTransaction': True}

        mock_signed_txn = MagicMock()
        mock_signed_txn.raw_transaction = b'raw_transaction_bytes'
        
        class MockTxHash:
            def hex(self):
                return TX_HASH[2:]  # Remove '0x' prefix when returning the hash

        mock_tx_hash = MockTxHash()
        
        ip_account.account.sign_transaction = MagicMock(return_value=mock_signed_txn)

        with patch.object(ip_account, '_is_registered', return_value=True), \
             patch.object(ip_account.web3.eth, 'get_transaction_count', return_value=0), \
             patch.object(ip_account.web3.eth, 'send_raw_transaction', return_value=mock_tx_hash), \
             patch.object(ip_account.web3.eth, 'wait_for_transaction_receipt', return_value={'status': 1}):

            response = ip_account.executeWithSig(
                VALID_IP_ID, to_address, data, signer, deadline, signature,
                tx_options=tx_options
            )
            assert response['txHash'] == TX_HASH[2:]

class TestGetIpAccountNonce:
    def test_invalid_ip_id(self, ip_account):
        with pytest.raises(ValueError) as exc_info:
            ip_account.getIpAccountNonce("0x123")  # invalid address
        assert "Invalid IP id address" in str(exc_info.value)

    def test_successful_nonce_retrieval(self, ip_account):
        ip_id = Web3.to_checksum_address("0x73fcb515cee99e4991465ef586cfe2b072ebb512")
        expected_nonce = 1

        with patch('story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client.IPAccountImplClient.state', 
                return_value=expected_nonce), \
            patch('web3.eth.Eth.contract', return_value=MagicMock()):
            nonce = ip_account.getIpAccountNonce(ip_id)
            assert nonce == expected_nonce

class TestGetToken:
    def test_invalid_ip_id(self, ip_account):
        with pytest.raises(ValueError) as exc_info:
            ip_account.getToken("0x123")  # invalid address
        assert "Invalid IP id address" in str(exc_info.value)

    def test_successful_token_retrieval(self, ip_account):
        ip_id = Web3.to_checksum_address("0x73fcb515cee99e4991465ef586cfe2b072ebb512")
        expected_token = {
            'chainId': 1513,
            'tokenContract': ZERO_ADDRESS,
            'tokenId': 1
        }

        with patch('story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client.IPAccountImplClient.token',
                  return_value=[1513, ZERO_ADDRESS, 1]), \
             patch('web3.eth.Eth.contract', return_value=MagicMock()):
            token = ip_account.getToken(ip_id)
            assert token == expected_token