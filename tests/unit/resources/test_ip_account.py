import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from web3 import Web3
from dotenv import load_dotenv
from web3.exceptions import InvalidAddress


# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from src.story_protocol_python_sdk.resources.IPAccount import IPAccount

# Load environment variables from .env file
load_dotenv()
private_key = os.getenv('WALLET_PRIVATE_KEY')
rpc_url = os.getenv('RPC_PROVIDER_URL')

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(rpc_url))

# Check if connected
if not web3.is_connected():
    raise Exception("Failed to connect to Web3 provider")

# Set up the account with the private key
account = web3.eth.account.from_key(private_key)
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
VALID_IP_ID = "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"
TX_HASH = "0xe87b172eee35872179ced53ea4f3f314b12cd0f5d0034e7f0ae3c4efce9ba6f1"

@pytest.fixture
def ip_account():
    chain_id = 11155111  # Sepolia chain ID
    return IPAccount(web3, account, chain_id)

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

        with patch.object(ip_account, '_is_registered', return_value=True), \
             patch('story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client.IPAccountImplClient.build_execute_transaction', return_value={
                 'to': to_address,
                 'value': value,
                 'data': data,
                 'gas': 2000000,
                 'gasPrice': Web3.to_wei('50', 'gwei'),
                 'nonce': 0
             }), \
             patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr=TX_HASH)), \
             patch('web3.eth.Eth.wait_for_transaction_receipt', return_value={'status': 1, 'logs': []}):

            response = ip_account.execute(to_address, value, VALID_IP_ID, data)
            assert response['txHash'] == TX_HASH[2:]

    def test_wait_for_transaction(self, ip_account):
        to_address = "0xF9936a224b3Deb6f9A4645ccAfa66f7ECe83CF0A"
        data = "0x11111111111111111111111111111"
        value = 2
        tx_options = {'waitForTransaction': True}

        mock_transaction = {
            'to': to_address,
            'value': value,
            'data': data,
            'gas': 2000000,
            'gasPrice': Web3.to_wei('50', 'gwei'),
            'nonce': 0,
            'chainId': 11155111  # Sepolia chain ID
        }

        with patch.object(ip_account, '_is_registered', return_value=True), \
            patch('story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client.IPAccountImplClient.build_execute_transaction',
                return_value=mock_transaction), \
            patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr=TX_HASH)), \
            patch('web3.eth.Eth.wait_for_transaction_receipt', return_value={'status': 1}):

            response = ip_account.execute(to_address, value, VALID_IP_ID, data, tx_options=tx_options)
            assert response['txHash'] == TX_HASH[2:]

    def test_encoded_tx_data_only(self, ip_account):
        print("Starting test_encoded_tx_data_only")
        to_address = "0xF9936a224b3Deb6f9A4645ccAfa66f7ECe83CF0A"
        data = "0x11111111111111111111111111111"
        value = 2
        tx_options = {'encodedTxDataOnly': True}
        encoded_data = "0x123456789"

        print("Setting up mock transaction")
        mock_tx = {
            'to': to_address,
            'value': value,
            'data': encoded_data,
            'gas': 2000000,
            'gasPrice': Web3.to_wei('50', 'gwei'),
            'nonce': 0,
            'chainId': 11155111
        }

        print("Setting up patches")
        with patch.object(ip_account, '_is_registered', return_value=True), \
            patch('story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client.IPAccountImplClient.build_execute_transaction',
                return_value=mock_tx), \
            patch('web3.eth.Eth.get_transaction_count',
                return_value=0):

            print("Executing ip_account.execute")
            response = ip_account.execute(to_address, value, VALID_IP_ID, data, tx_options=tx_options)
            print("Got response")
            
            # We expect just the encodedTxData in the response
            assert 'encodedTxData' in response
            assert response['encodedTxData'] == mock_tx

        print("Test completed")

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

        # Create a mock transaction dictionary
        mock_tx = {
            'to': to_address,
            'value': value,
            'data': data,
            'gas': 2000000,
            'gasPrice': Web3.to_wei('50', 'gwei'),
            'nonce': 0,
            'chainId': 11155111  # Sepolia chain ID
        }

        with patch.object(ip_account, '_is_registered', return_value=True), \
            patch('story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client.IPAccountImplClient.build_executeWithSig_transaction',
                return_value=mock_tx), \
            patch('web3.eth.Eth.send_raw_transaction', 
                return_value=Web3.to_bytes(hexstr=TX_HASH)), \
            patch('web3.eth.Eth.wait_for_transaction_receipt', 
                return_value={'status': 1}), \
            patch('web3.eth.Eth.get_transaction_count',
                return_value=0):

            response = ip_account.executeWithSig(VALID_IP_ID, to_address, data, signer, deadline, signature, value)
            assert response['txHash'] == TX_HASH[2:]

    def test_wait_for_transaction_with_sig(self, ip_account):
        to_address = "0xF9936a224b3Deb6f9A4645ccAfa66f7ECe83CF0A"
        data = "0x11111111111111111111111111111"
        signer = ZERO_ADDRESS
        deadline = 20
        signature = ZERO_ADDRESS
        tx_options = {'waitForTransaction': True}

        mock_tx = {
            'to': to_address,
            'value': 0,
            'data': data,
            'gas': 2000000,
            'gasPrice': Web3.to_wei('50', 'gwei'),
            'nonce': 0,
            'chainId': 11155111 
        }

        with patch.object(ip_account, '_is_registered', return_value=True), \
            patch('story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client.IPAccountImplClient.build_executeWithSig_transaction',
                return_value=mock_tx), \
            patch('web3.eth.Eth.send_raw_transaction', 
                return_value=Web3.to_bytes(hexstr=TX_HASH)), \
            patch('web3.eth.Eth.wait_for_transaction_receipt', 
                return_value={'status': 1}), \
            patch('web3.eth.Eth.get_transaction_count',
                return_value=0):

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