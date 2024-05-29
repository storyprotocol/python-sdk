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
    with patch.object(permission, '_is_registered', return_value=False):
        with pytest.raises(ValueError, match="The IP account with id 0x0000000000000000000000000000000000000000 is not registered."):
            permission.setPermission(ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS, 1)

def test_invalid_signer_address(permission):
    with pytest.raises(ValueError, match="The address 0xInvalidAddress that can call 'to' on behalf of the 'ip_asset' is not a valid address."):
        permission.setPermission(ZERO_ADDRESS, "0xInvalidAddress", ZERO_ADDRESS, "0x11111111111111111111111111111")

def test_invalid_to_address(permission):
    with pytest.raises(ValueError, match="The recipient of the transaction 0xInvalidAddress is not a valid address."):
        permission.setPermission(ZERO_ADDRESS, ZERO_ADDRESS, "0xInvalidAddress", "0x11111111111111111111111111111")

def test_successful_transaction(permission):
    ip_asset = "0x587AE719cACC8cC34188D9648d67CF885bE10558"
    signer = "0x8059F63663576bE3605B3CcD30aaEb858C345640"
    to = "0x2ac240293f12032E103458451dE8A8096c5A72E8"
    func = "0x00000000"
    permission_level = 1
    tx_hash = "0x0c0cce07beb64ccfbdd59da111f23084ab7c9e96a951f7381af49e792d014c04"
    
    with patch.object(permission, '_is_registered', return_value=True), \
         patch('story_protocol_python_sdk.resources.IPAccount.IPAccount.execute', return_value={'txHash': tx_hash}):
        response = permission.setPermission(ip_asset, signer, to, permission_level, func)
        assert response['txHash'] == tx_hash

def test_transaction_request_fails(permission):
    ip_asset = "0x587AE719cACC8cC34188D9648d67CF885bE10558"
    signer = "0x8059F63663576bE3605B3CcD30aaEb858C345640"
    to = "0x2ac240293f12032E103458451dE8A8096c5A72E8"
    func = "0x00000000"
    permission_level = 1
    
    with patch.object(permission, '_is_registered', return_value=True), \
         patch('story_protocol_python_sdk.resources.IPAccount.IPAccount.execute', side_effect=Exception("Transaction failed")):
        with pytest.raises(Exception) as excinfo:
            permission.setPermission(ip_asset, signer, to, permission_level, func)
        assert str(excinfo.value) == "Transaction failed"