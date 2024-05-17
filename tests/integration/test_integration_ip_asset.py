# tests/integration/test_integration_ip_asset.py

import os
import sys
import pytest
from dotenv import load_dotenv
from web3 import Web3

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from utils import get_token_id, get_story_client_in_sepolia, MockERC721

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

def test_register_ip_asset(story_client):
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
    wait_for_transaction = True

    response = story_client.IPAsset.register(
        token_contract=MockERC721,
        token_id=token_id
    )

    assert response is not None
    assert 'ipId' in response
    assert response['ipId'] is not None

    if wait_for_transaction:
        assert response['ipId'] is not None and response['ipId'] != ''