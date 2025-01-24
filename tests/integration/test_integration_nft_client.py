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

from utils import get_story_client_in_devnet

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

def test_create_nft_collection_with_base_uri(story_client):
    """Test creating NFT collection with base URI."""
    response = story_client.NFTClient.createNFTCollection(
        name="test-collection-base-uri",
        symbol="TESTURI",
        max_supply=100,
        is_public_minting=True,
        mint_open=True,
        contract_uri="test-uri",
        base_uri="https://api.example.com/tokens/",
        mint_fee_recipient=account.address
    )

    assert response is not None
    assert 'txHash' in response
    assert 'nftContract' in response
    assert isinstance(response['nftContract'], str)
    assert response['nftContract'].startswith('0x')

def test_create_nft_collection_with_mint_fee(story_client):
    """Test creating NFT collection with minting fee."""
    response = story_client.NFTClient.createNFTCollection(
        name="test-collection-fee",
        symbol="TESTFEE",
        max_supply=100,
        is_public_minting=True,
        mint_open=True,
        contract_uri="test-uri",
        mint_fee=1000000,  # Set a minting fee
        mint_fee_token="0x0000000000000000000000000000000000000000",  # Use zero address for native token
        mint_fee_recipient=account.address
    )

    assert response is not None
    assert 'txHash' in response
    assert 'nftContract' in response
    assert isinstance(response['nftContract'], str)
    assert response['nftContract'].startswith('0x')

def test_create_private_mint_collection(story_client):
    """Test creating NFT collection with private minting."""
    response = story_client.NFTClient.createNFTCollection(
        name="test-collection-private",
        symbol="TESTPRIV",
        max_supply=100,
        is_public_minting=False,  # Only allowed minters can mint
        mint_open=True,
        contract_uri="test-uri",
        mint_fee_recipient=account.address
    )

    assert response is not None
    assert 'txHash' in response
    assert 'nftContract' in response
    assert isinstance(response['nftContract'], str)
    assert response['nftContract'].startswith('0x')

def test_create_closed_mint_collection(story_client):
    """Test creating NFT collection with minting closed."""
    response = story_client.NFTClient.createNFTCollection(
        name="test-collection-closed",
        symbol="TESTCLOSED",
        max_supply=100,
        is_public_minting=True,
        mint_open=False,  # Minting starts closed
        contract_uri="test-uri",
        mint_fee_recipient=account.address
    )

    assert response is not None
    assert 'txHash' in response
    assert 'nftContract' in response
    assert isinstance(response['nftContract'], str)
    assert response['nftContract'].startswith('0x')

def test_create_collection_with_custom_owner(story_client):
    """Test creating NFT collection with a custom owner."""
    custom_owner = "0x1234567890123456789012345678901234567890"
    response = story_client.NFTClient.createNFTCollection(
        name="test-collection-owner",
        symbol="TESTOWNER",
        max_supply=100,
        is_public_minting=True,
        mint_open=True,
        contract_uri="test-uri",
        owner=custom_owner,
        mint_fee_recipient=account.address
    )

    assert response is not None
    assert 'txHash' in response
    assert 'nftContract' in response
    assert isinstance(response['nftContract'], str)
    assert response['nftContract'].startswith('0x')

def test_create_collection_invalid_mint_fee(story_client):
    """Test creating NFT collection with invalid mint fee configuration."""
    with pytest.raises(ValueError) as exc_info:
        story_client.NFTClient.createNFTCollection(
            name="test-collection-invalid",
            symbol="TESTINV",
            max_supply=100,
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee=-1,  # Invalid negative fee
            mint_fee_token="0x0000000000000000000000000000000000000000",
            mint_fee_recipient=account.address
        )
    
    assert "Invalid mint fee" in str(exc_info.value)
