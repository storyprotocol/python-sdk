# tests/integration/test_integration_ip_account.py

import os, json, sys
import pytest
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_typed_data

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from utils import get_token_id, get_story_client_in_odyssey, MockERC721, getBlockTimestamp

load_dotenv()
private_key = os.getenv('WALLET_PRIVATE_KEY')
rpc_url = os.getenv('RPC_PROVIDER_URL')

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(rpc_url))
if not web3.is_connected():
    raise Exception("Failed to connect to Web3 provider")

# Set up the account with the private key
account = web3.eth.account.from_key(private_key)

@pytest.fixture
def story_client():
    return get_story_client_in_odyssey(web3, account)

@pytest.fixture
def registered_ip_id(story_client):
    """Fixture to create a registered IP ID for testing"""
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
    response = story_client.IPAsset.register(
        token_contract=MockERC721,
        token_id=token_id
    )
    return response['ipId']

def test_execute(story_client, registered_ip_id):
    data = story_client.IPAccount.access_controller_client.contract.encode_abi(
        fn_name="setPermission", 
        args=[registered_ip_id, 
              account.address, 
              "0x2ac240293f12032E103458451dE8A8096c5A72E8", 
              "0x00000000", 
              1]
    )

    response = story_client.IPAccount.execute(
        to=story_client.IPAccount.access_controller_client.contract.address,
        value=0,
        account_address=registered_ip_id,
        data=data
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'txHash' in response, "Response does not contain 'txHash'."
    assert response['txHash'] is not None, "'txHash' is None."
    assert isinstance(response['txHash'], str), "'txHash' is not a string."
    assert len(response['txHash']) > 0, "'txHash' is empty."

def test_executeWithSig(story_client, registered_ip_id):
    data = story_client.IPAccount.access_controller_client.contract.encode_abi(
        fn_name="setPermission", 
        args=[registered_ip_id, 
              account.address, 
              "0x2ac240293f12032E103458451dE8A8096c5A72E8", 
              "0x00000000", 
              1]
    )
    deadline = getBlockTimestamp(web3) + 100
    state = story_client.IPAccount.getIpAccountNonce(registered_ip_id)
    expectedState = state + 1

    domain_data = {
        "name": "Story Protocol IP Account",
        "version": "1",
        "chainId": 11155111,
        "verifyingContract": registered_ip_id,
    }

    message_types = {
        "Execute": [
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "data", "type": "bytes"},
            {"name": "nonce", "type": "uint256"},
            {"name": "deadline", "type": "uint256"},
        ],
    }

    message_data = {
        "to": story_client.IPAccount.access_controller_client.contract.address,
        "value": 0,
        "data": data,
        "nonce": expectedState,
        "deadline": deadline,
    }

    signable_message = encode_typed_data(domain_data, message_types, message_data)
    signed_message = Account.sign_message(signable_message, private_key)

    response = story_client.IPAccount.executeWithSig(
        to=story_client.IPAccount.access_controller_client.contract.address,
        value=0,
        account_address=registered_ip_id,
        data=data,
        signer=account.address,
        deadline=deadline,
        signature=signed_message.signature
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'txHash' in response, "Response does not contain 'txHash'."
    assert response['txHash'] is not None, "'txHash' is None."
    assert isinstance(response['txHash'], str), "'txHash' is not a string."
    assert len(response['txHash']) > 0, "'txHash' is empty."

def test_getIpAccountNonce(story_client, registered_ip_id):
    """Test getting the IP Account's nonce"""
    nonce = story_client.IPAccount.getIpAccountNonce(registered_ip_id)
    
    assert isinstance(nonce, int), "Nonce should be an integer"
    assert nonce >= 0, "Nonce should be non-negative"

def test_getToken(story_client, registered_ip_id):
    """Test getting the token information for an IP Account"""
    response = story_client.IPAccount.getToken(registered_ip_id)
    
    assert response is not None, "Response should not be None"
    assert 'chainId' in response, "Response should contain chainId"
    assert 'tokenContract' in response, "Response should contain tokenContract"
    assert 'tokenId' in response, "Response should contain tokenId"
    assert isinstance(response['chainId'], int), "chainId should be an integer"
    assert Web3.is_address(response['tokenContract']), "tokenContract should be a valid address"
    assert isinstance(response['tokenId'], int), "tokenId should be an integer"

def test_execute_with_invalid_address(story_client, registered_ip_id):
    """Test executing with invalid address should raise ValueError"""
    data = "0x00"  # dummy data
    with pytest.raises(ValueError) as exc_info:
        story_client.IPAccount.execute(
            to="invalid_address",
            value=0,
            account_address=registered_ip_id,
            data=data
        )
    assert "not a valid address" in str(exc_info.value)

def test_execute_with_unregistered_ip_id(story_client):
    """Test executing with unregistered IP ID should raise ValueError"""
    unregistered_id = "0x1234567890123456789012345678901234567890"
    data = "0x00"  # dummy data
    with pytest.raises(ValueError) as exc_info:
        story_client.IPAccount.execute(
            to=story_client.IPAccount.access_controller_client.contract.address,
            value=0,
            account_address=unregistered_id,
            data=data
        )
    assert "not registered" in str(exc_info.value)