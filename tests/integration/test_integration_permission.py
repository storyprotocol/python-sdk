# tests/integration/test_integration_permission.py

import os, json, sys
import pytest
from dotenv import load_dotenv
from web3 import Web3

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from utils import get_token_id, get_story_client_in_devnet, MockERC721, check_event_in_tx

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
    return get_story_client_in_devnet(web3, account)

def test_setPermission(story_client):
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)

    response = story_client.IPAsset.register(
        token_contract=MockERC721,
        token_id=token_id
    )

    response = story_client.Permission.setPermission(
        ip_asset=response['ipId'],
        signer=account.address,
        to="0x2ac240293f12032E103458451dE8A8096c5A72E8",
        permission=1,
        func="0x00000000"
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'txHash' in response, "Response does not contain 'txHash'."
    assert response['txHash'] is not None, "'txHash' is None."
    assert isinstance(response['txHash'], str), "'txHash' is not a string."
    assert len(response['txHash']) > 0, "'txHash' is empty."

    assert check_event_in_tx(web3, response['txHash'], "PermissionSet(address,address,address,address,bytes4,uint8)") is True

@pytest.fixture
def registered_ip(story_client):
    """Fixture to create an IP for testing permissions."""
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
    response = story_client.IPAsset.register(
        nft_contract=MockERC721,
        token_id=token_id
    )
    return response['ipId']

def test_set_permission_with_specific_function(story_client, registered_ip):
    """Test setting permission for a specific function."""
    module_address = "0x2ac240293f12032E103458451dE8A8096c5A72E8"
    function_selector = Web3.keccak(text="transfer(address,uint256)")[:4].hex()
    
    response = story_client.Permission.setPermission(
        ip_asset=registered_ip,
        signer=account.address,
        to=module_address,
        permission=1,  # ALLOW
        func=function_selector
    )

    assert response is not None
    assert 'txHash' in response
    assert isinstance(response['txHash'], str)
    assert len(response['txHash']) > 0
    assert check_event_in_tx(web3, response['txHash'], "PermissionSet(address,address,address,address,bytes4,uint8)")

def test_set_all_permissions(story_client, registered_ip):
    """Test setting all permissions for a signer."""
    response = story_client.Permission.setAllPermissions(
        ip_asset=registered_ip,
        signer=account.address,
        permission=1  # ALLOW
    )

    assert response is not None
    assert 'txHash' in response
    assert isinstance(response['txHash'], str)
    assert len(response['txHash']) > 0
    assert check_event_in_tx(web3, response['txHash'], "PermissionSet(address,address,address,address,bytes4,uint8)")

def test_set_batch_permissions(story_client, registered_ip):
    """Test setting multiple permissions in a single transaction."""
    module_address = "0x2ac240293f12032E103458451dE8A8096c5A72E8"
    permissions = [
        {
            'ip_asset': registered_ip,
            'signer': account.address,
            'to': module_address,
            'permission': 1,
            'func': "0x00000000"
        },
        {
            'ip_asset': registered_ip,
            'signer': account.address,
            'to': module_address,
            'permission': 2,  # DENY
            'func': Web3.keccak(text="transfer(address,uint256)")[:4].hex()
        }
    ]
    
    response = story_client.Permission.setBatchPermissions(permissions)

    assert response is not None
    assert 'txHash' in response
    assert isinstance(response['txHash'], str)
    assert len(response['txHash']) > 0
    assert check_event_in_tx(web3, response['txHash'], "PermissionSet(address,address,address,address,bytes4,uint8)")

def test_set_permission_invalid_ip(story_client):
    """Test setting permission for an unregistered IP."""
    unregistered_ip = "0x1234567890123456789012345678901234567890"
    
    with pytest.raises(ValueError) as exc_info:
        story_client.Permission.setPermission(
            ip_asset=unregistered_ip,
            signer=account.address,
            to="0x2ac240293f12032E103458451dE8A8096c5A72E8",
            permission=1
        )
    
    assert "is not registered" in str(exc_info.value)

def test_set_permission_invalid_signer(story_client, registered_ip):
    """Test setting permission with invalid signer address."""
    with pytest.raises(ValueError) as exc_info:
        story_client.Permission.setPermission(
            ip_asset=registered_ip,
            signer="0xinvalid",
            to="0x2ac240293f12032E103458451dE8A8096c5A72E8",
            permission=1
        )
    
    assert "is not a valid address" in str(exc_info.value)

def test_create_permission_signature(story_client, registered_ip):
    """Test creating and executing a permission signature."""
    module_address = "0x2ac240293f12032E103458451dE8A8096c5A72E8"
    deadline = web3.eth.get_block('latest')['timestamp'] + 1000
    
    response = story_client.Permission.createSetPermissionSignature(
        ip_asset=registered_ip,
        signer=account.address,
        to=module_address,
        permission=1,
        func="0x00000000",
        deadline=deadline
    )

    assert response is not None
    assert 'txHash' in response
    assert isinstance(response['txHash'], str)
    assert len(response['txHash']) > 0
    assert check_event_in_tx(web3, response['txHash'], "PermissionSet(address,address,address,address,bytes4,uint8)")