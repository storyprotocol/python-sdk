# tests/integration/test_integration_nft_client.py

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

from utils import get_story_client_in_devnet

# Load environment variables at module level
load_dotenv(override=True)

def get_web3_instance():
    """Get Web3 instance with proper error handling"""
    rpc_url = os.getenv('RPC_PROVIDER_URL')
    if not rpc_url:
        pytest.skip("RPC_PROVIDER_URL not found in environment")
    
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    if not web3.is_connected():
        pytest.skip("Failed to connect to Web3 provider")
    
    return web3

@pytest.fixture(scope="session")
def web3():
    return get_web3_instance()

@pytest.fixture(scope="session")
def account(web3):
    private_key = os.getenv('WALLET_PRIVATE_KEY')
    if not private_key:
        pytest.skip("WALLET_PRIVATE_KEY not found in environment")
    return web3.eth.account.from_key(private_key)

@pytest.fixture(scope="function")
def story_client(web3, account):
    return get_story_client_in_devnet(web3, account)

class TestNFTCollectionOperations:
    """Tests for NFT collection creation and management"""

    def test_create_basic_collection(self, story_client):
        """Test creating a basic NFT collection with minimum parameters"""
        response = story_client.NFTClient.createNFTCollection(
            name="test-collection",
            symbol="TEST",
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=story_client.account.address
        )

        assert response is not None
        assert 'txHash' in response
        assert isinstance(response['txHash'], str)
        assert len(response['txHash']) > 0
        assert 'nftContract' in response
        assert Web3.is_address(response['nftContract'])

    def test_create_collection_with_supply(self, story_client):
        """Test creating collection with max supply"""
        response = story_client.NFTClient.createNFTCollection(
            name="test-collection",
            symbol="TEST",
            max_supply=100,
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=story_client.account.address
        )

        assert response is not None
        assert 'nftContract' in response
        assert Web3.is_address(response['nftContract'])

    def test_create_collection_with_mint_fee(self, story_client):
        """Test creating collection with mint fee configuration"""
        response = story_client.NFTClient.createNFTCollection(
            name="test-collection",
            symbol="TEST",
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=story_client.account.address,
            mint_fee=1000,
            mint_fee_token=story_client.account.address  # Using account address as mock token
        )

        assert response is not None
        assert 'nftContract' in response
        assert Web3.is_address(response['nftContract'])

    def test_create_collection_with_base_uri(self, story_client):
        """Test creating collection with base URI"""
        response = story_client.NFTClient.createNFTCollection(
            name="test-collection",
            symbol="TEST",
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=story_client.account.address,
            base_uri="https://api.example.com/nft/"
        )

        assert response is not None
        assert 'nftContract' in response
        assert Web3.is_address(response['nftContract'])

class TestErrorCases:
    """Tests for error handling in NFT collection creation"""

    def test_invalid_mint_fee_configuration(self, story_client):
        """Test error when mint fee is set but token address is invalid"""
        with pytest.raises(ValueError) as exc_info:
            story_client.NFTClient.createNFTCollection(
                name="test-collection",
                symbol="TEST",
                is_public_minting=True,
                mint_open=True,
                contract_uri="test-uri",
                mint_fee_recipient=story_client.account.address,
                mint_fee=1000,
                mint_fee_token="0xinvalid"
            )
        assert "Invalid mint fee token address" in str(exc_info.value)

    def test_invalid_recipient_address(self, story_client):
        """Test error when mint fee recipient address is invalid"""
        with pytest.raises(ValueError) as exc_info:
            story_client.NFTClient.createNFTCollection(
                name="test-collection",
                symbol="TEST",
                is_public_minting=True,
                mint_open=True,
                contract_uri="test-uri",
                mint_fee_recipient="0xinvalid"
            )
        assert "when sending a str, it must be a hex string. got: '0xinvalid'" in str(exc_info.value).lower()