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

from utils import get_token_id, get_story_client_in_sepolia, MockERC721, check_event_in_tx

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
    return get_story_client_in_sepolia(web3, account)

def test_setPermission(story_client):
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'story_protocol_python_sdk', 'scripts', 'config.json'))
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    contract_address = None
    for contract in config['contracts']:
        if contract['contract_name'] == 'AccessController':
            contract_address = contract['contract_address']
            break
    if not contract_address:
        raise ValueError(f"Contract address for AccessController not found in config.json")
    abi_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'story_protocol_python_sdk', 'abi', 'AccessController', 'AccessController.json'))
    with open(abi_path, 'r') as abi_file:
        abi = json.load(abi_file)

    contract = web3.eth.contract(address=contract_address, abi=abi)

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
