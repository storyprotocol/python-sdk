# tests/integration/test_integration_nft_client.py

import os, sys
import pytest
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from utils import get_story_client_in_odyssey

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

def test_create_nft_collection(story_client):
    response = story_client.NFTClient.createNFTCollection(
        name="test-collection",
        symbol="TEST",
        max_supply=100,
        is_public_minting=True,
        mint_open=True,
        contract_uri="test-uri",
        mint_fee_recipient=account.address,
    )

    assert response is not None
    assert 'txHash' in response
    assert 'nftContract' in response
    assert isinstance(response['nftContract'], str)
    assert len(response['nftContract']) > 0
    assert response['nftContract'].startswith('0x')
