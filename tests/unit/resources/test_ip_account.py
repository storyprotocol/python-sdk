import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from web3 import Web3
from dotenv import load_dotenv

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

@pytest.fixture
def ip_account():
    chain_id = 11155111  # Sepolia chain ID
    return IPAccount(web3, account, chain_id)

def test_invalid_recipient_address(ip_account):
    with pytest.raises(ValueError, match="The recipient of the transaction 0xInvalidAddress is not a valid address."):
        ip_account.execute("0xInvalidAddress", 1, ZERO_ADDRESS, "0x11111111111111111111111111111")

def test_unregistered_ip_account(ip_account):
    with patch.object(ip_account, '_is_registered', return_value=False):
        with pytest.raises(ValueError, match="The IP account with id 0x0000000000000000000000000000000000000000 is not registered."):
            ip_account.execute(ZERO_ADDRESS, 1, ZERO_ADDRESS, "0x11111111111111111111111111111")

def test_successful_transaction(ip_account):
    to_address = "0xF9936a224b3Deb6f9A4645ccAfa66f7ECe83CF0A"
    ip_address = "0xF60cBF0Ea1A61567F1dDaf79A6219D20d189155c"
    data = "0x11111111111111111111111111111"
    value = 2
    tx_hash = "0xe87b172eee35872179ced53ea4f3f314b12cd0f5d0034e7f0ae3c4efce9ba6f1"

    with patch.object(ip_account, '_is_registered', return_value=True), \
         patch('story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client.IPAccountImplClient.build_execute_transaction', return_value={
             'to': to_address,
             'value': value,
             'data': data,
             'gas': 2000000,
             'gasPrice': Web3.to_wei('50', 'gwei'),
             'nonce': 0
         }), \
         patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr=tx_hash)), \
         patch('web3.eth.Eth.wait_for_transaction_receipt', return_value={'status': 1, 'logs': []}):

        response = ip_account.execute(to_address, value, ip_address, data)
        assert response['txHash'] == tx_hash[2:]

def test_transaction_request_fails(ip_account):
    to_address = ZERO_ADDRESS
    ip_address = ZERO_ADDRESS
    data = "0x11111111111111111111111111111"
    value = 2

    with patch.object(ip_account, '_is_registered', return_value=True), \
         patch('story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client.IPAccountImplClient.build_execute_transaction', side_effect=Exception("Transaction failed")):

        with pytest.raises(Exception) as excinfo:
            response = ip_account.execute(to_address, value, ip_address, data)
        assert str(excinfo.value) == "Transaction failed"

def test_invalid_recipient_address_with_sig(ip_account):
    with pytest.raises(ValueError, match="The recipient of the transaction 0xInvalidAddress is not a valid address."):
        ip_account.executeWithSig("0xInvalidAddress", 1, ZERO_ADDRESS, "0x11111111111111111111111111111", ZERO_ADDRESS, 20, ZERO_ADDRESS)

def test_unregistered_ip_account_with_sig(ip_account):
    with patch.object(ip_account, '_is_registered', return_value=False):
        with pytest.raises(ValueError, match="The IP account with id 0x0000000000000000000000000000000000000000 is not registered."):
            ip_account.executeWithSig(ZERO_ADDRESS, 1, ZERO_ADDRESS, "0x11111111111111111111111111111", ZERO_ADDRESS, 20, ZERO_ADDRESS)

def test_successful_transaction_with_sig(ip_account):
    to_address = "0xF9936a224b3Deb6f9A4645ccAfa66f7ECe83CF0A"
    ip_address = "0xF60cBF0Ea1A61567F1dDaf79A6219D20d189155c"
    data = "0x11111111111111111111111111111"
    value = 2
    signer = "0xF60cBF0Ea1A61567F1dDaf79A6219D20d189155c"
    deadline = 20
    signature = "0x11111111111111111111111111111"
    tx_hash = "0xe87b172eee35872179ced53ea4f3f314b12cd0f5d0034e7f0ae3c4efce9ba6f1"

    with patch.object(ip_account, '_is_registered', return_value=True), \
         patch('story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client.IPAccountImplClient.build_executeWithSig_transaction', return_value={
             'to': to_address,
             'value': value,
             'data': data,
             'gas': 2000000,
             'gasPrice': Web3.to_wei('50', 'gwei'),
             'nonce': 0
         }), \
         patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr=tx_hash)), \
         patch('web3.eth.Eth.wait_for_transaction_receipt', return_value={'status': 1, 'logs': []}):

        response = ip_account.executeWithSig(to_address, value, ip_address, data, signer, deadline, signature)
        assert response['txHash'] == tx_hash[2:]

def test_transaction_request_fails_with_sig(ip_account):
    to_address = ZERO_ADDRESS
    ip_address = ZERO_ADDRESS
    data = "0x11111111111111111111111111111"
    value = 2
    signer = ZERO_ADDRESS
    deadline = 20
    signature = ZERO_ADDRESS

    with patch.object(ip_account, '_is_registered', return_value=True), \
         patch('story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client.IPAccountImplClient.build_executeWithSig_transaction', side_effect=Exception("Transaction failed")):

        with pytest.raises(Exception) as excinfo:
            response = ip_account.executeWithSig(to_address, value, ip_address, data, signer, deadline, signature)
        assert str(excinfo.value) == "Transaction failed"

def test_get_ip_account_nonce(ip_account):
    ip_id = "0x73fcb515cee99e4991465ef586cfe2b072ebb512"
    checksum_ip_id = Web3.to_checksum_address(ip_id)
    expected_nonce = 1

    with patch('story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client.IPAccountImplClient.state', return_value=expected_nonce):
        nonce = ip_account.getIpAccountNonce(checksum_ip_id)
        assert nonce == expected_nonce
