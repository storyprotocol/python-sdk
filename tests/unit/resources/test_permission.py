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

from src.story_protocol_python_sdk.resources.Permission import Permission

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
def permission():
    chain_id = 11155111  # Sepolia chain ID
    return Permission(web3, account, chain_id)


def test_unregistered_ip_account(permission):
    with patch.object(permission.ip_asset_registry_client, 'isRegistered', return_value=False):
        with pytest.raises(Exception, match="IP id with 0x0000000000000000000000000000000000000000 is not registered."):
            permission.set_permission(ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS, 1)

def test_invalid_signer_address(permission):
    with pytest.raises(Exception, match=" Invalid address: 0xInvalidAddress"):
        permission.set_permission(ZERO_ADDRESS, "0xInvalidAddress", ZERO_ADDRESS, "0x11111111111111111111111111111")

def test_invalid_to_address(permission):
    with pytest.raises(Exception, match="Invalid address: 0xInvalidAddress."):
        permission.set_permission(ZERO_ADDRESS, ZERO_ADDRESS, "0xInvalidAddress", "0x11111111111111111111111111111")

def test_successful_transaction(permission):
    ip_asset = "0x587AE719cACC8cC34188D9648d67CF885bE10558"
    signer = "0x8059F63663576bE3605B3CcD30aaEb858C345640"
    to = "0x2ac240293f12032E103458451dE8A8096c5A72E8"
    func = "0x00000000"
    permission_level = 1
    tx_hash = "0x0c0cce07beb64ccfbdd59da111f23084ab7c9e96a951f7381af49e792d014c04"
    
    with patch.object(permission.ip_asset_registry_client, 'isRegistered', return_value=True), \
         patch.object(permission.ip_account, 'execute', return_value={'tx_hash': tx_hash}):
        response = permission.set_permission(ip_asset, signer, to, permission_level, func)
        assert response['tx_hash'] == tx_hash

def test_transaction_request_fails(permission):
    ip_asset = "0x587AE719cACC8cC34188D9648d67CF885bE10558"
    signer = "0x8059F63663576bE3605B3CcD30aaEb858C345640"
    to = "0x2ac240293f12032E103458451dE8A8096c5A72E8"
    func = "0x00000000"
    permission_level = 1
    
    with patch.object(permission.ip_asset_registry_client, 'isRegistered', return_value=True), \
         patch.object(permission.ip_account, 'execute', side_effect=Exception("Transaction failed")):
        with pytest.raises(Exception, match="Transaction failed"):
            permission.set_permission(ip_asset, signer, to, permission_level, func)