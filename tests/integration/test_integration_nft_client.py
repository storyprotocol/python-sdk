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

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

@pytest.fixture(scope="module")
def story_client():
    """Fixture for story client instance"""
    return get_story_client_in_odyssey(web3, account)

class TestNFTCollection:
    """Tests for NFT Collection creation and management"""

    def test_create_basic_nft_collection(self, story_client):
        """Test creating a basic NFT collection with minimal parameters"""
        response = story_client.NFTClient.createNFTCollection(
            name="test-collection",
            symbol="TEST",
            max_supply=100,
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=account.address,
        )

        assert response is not None, "Response should not be None"
        assert 'txHash' in response, "Response should contain txHash"
        assert 'nftContract' in response, "Response should contain nftContract address"
        assert isinstance(response['nftContract'], str), "NFT contract address should be string"
        assert response['nftContract'].startswith('0x'), "NFT contract address should start with 0x"
        assert len(response['nftContract']) == 42, "NFT contract address should be 42 characters long"

    def test_create_nft_collection_with_mint_fee(self, story_client):
        """Test creating NFT collection with mint fee configuration"""
        response = story_client.NFTClient.createNFTCollection(
            name="test-collection-fee",
            symbol="TESTFEE",
            max_supply=100,
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=account.address,
            mint_fee=100,
            mint_fee_token=ZERO_ADDRESS
        )

        assert response is not None, "Response should not be None"
        assert 'txHash' in response, "Response should contain txHash"
        assert 'nftContract' in response, "Response should contain nftContract address"
        assert isinstance(response['nftContract'], str), "NFT contract address should be string"

    def test_create_nft_collection_with_base_uri(self, story_client):
        """Test creating NFT collection with base URI"""
        response = story_client.NFTClient.createNFTCollection(
            name="test-collection-uri",
            symbol="TESTURI",
            max_supply=100,
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=account.address,
            base_uri="https://api.example.com/nft/"
        )

        assert response is not None, "Response should not be None"
        assert 'txHash' in response, "Response should contain txHash"
        assert 'nftContract' in response, "Response should contain nftContract address"
        assert isinstance(response['nftContract'], str), "NFT contract address should be string"

    def test_create_private_nft_collection(self, story_client):
        """Test creating private NFT collection (not public minting)"""
        response = story_client.NFTClient.createNFTCollection(
            name="test-collection-private",
            symbol="TESTPRIV",
            max_supply=100,
            is_public_minting=False,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=account.address
        )

        assert response is not None, "Response should not be None"
        assert 'txHash' in response, "Response should contain txHash"
        assert 'nftContract' in response, "Response should contain nftContract address"
        assert isinstance(response['nftContract'], str), "NFT contract address should be string"

    def test_create_nft_collection_with_custom_owner(self, story_client):
        """Test creating NFT collection with custom owner"""
        response = story_client.NFTClient.createNFTCollection(
            name="test-collection-owner",
            symbol="TESTOWN",
            max_supply=100,
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=account.address,
            owner=account.address
        )

        assert response is not None, "Response should not be None"
        assert 'txHash' in response, "Response should contain txHash"
        assert 'nftContract' in response, "Response should contain nftContract address"
        assert isinstance(response['nftContract'], str), "NFT contract address should be string"

    def test_create_nft_collection_invalid_mint_fee(self, story_client):
        """Test creating NFT collection with invalid mint fee configuration"""
        with pytest.raises(ValueError) as exc_info:
            story_client.NFTClient.createNFTCollection(
                name="test-collection-invalid",
                symbol="TESTINV",
                max_supply=100,
                is_public_minting=True,
                mint_open=True,
                contract_uri="test-uri",
                mint_fee_recipient=account.address,
                mint_fee=100,
                mint_fee_token="invalid_address"
            )
        assert "Invalid mint fee token address" in str(exc_info.value)