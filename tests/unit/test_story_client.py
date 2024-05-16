import os
import sys
import pytest
from web3 import Web3
from dotenv import load_dotenv

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from src.story_client import StoryClient
from src.resources.IPAsset import IPAsset

# Load environment variables from .env file
load_dotenv()
private_key = os.getenv('WALLET_PRIVATE_KEY')
rpc_url = os.getenv('RPC_PROVIDER_URL')

# Ensure the environment variables are set
if not private_key or not rpc_url:
    raise ValueError("Please set WALLET_PRIVATE_KEY and RPC_PROVIDER_URL in the .env file")

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(rpc_url))

# Check if connected
if not web3.is_connected():
    raise Exception("Failed to connect to Web3 provider")

# Set up the account with the private key
account = web3.eth.account.from_key(private_key)

@pytest.fixture
def story_client():
    chain_id = 11155111  # Sepolia chain ID
    return StoryClient(web3, account, chain_id)

def test_story_client_constructor(story_client):
    assert story_client is not None
    assert isinstance(story_client, StoryClient)

def test_story_client_transport_error():
    with pytest.raises(ValueError):
        StoryClient(None, account, chain_id=11155111)

def test_story_client_account_missing():
    with pytest.raises(ValueError):
        StoryClient(web3, None, chain_id=11155111)

def test_story_client_wallet_initialization():
    client = StoryClient(web3, account, chain_id=11155111)
    assert client is not None
    assert isinstance(client, StoryClient)

def test_ip_asset_client_getter(story_client):
    ip_asset = story_client.IPAsset
    assert ip_asset is not None
    assert isinstance(ip_asset, IPAsset)
