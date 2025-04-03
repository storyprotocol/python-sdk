# tests/integration/test_integration_nft_client.py

import pytest
from web3 import Web3

from setup_for_integration import (
    story_client,
    MockERC721,
    MockERC20,
)

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
            mint_fee_token=MockERC20
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

class TestMintFee:
    """Tests for mint fee functionality in NFT collections"""

    @pytest.fixture(scope="module")
    def nft_contract(self, story_client):
        response = story_client.NFTClient.createNFTCollection(
            name="paid-collection",
            symbol="PAID",
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            max_supply=100,
            mint_fee_recipient=story_client.account.address,
            mint_fee=1000,
            mint_fee_token=MockERC20,
        )        

        return response['nftContract']

    def test_get_mint_fee_token(self, story_client, nft_contract):
        """Test successfully getting mint fee token"""
        mint_fee_token = story_client.NFTClient.getMintFeeToken(nft_contract)
        assert mint_fee_token == MockERC20

    def test_get_mint_fee(self, story_client, nft_contract):
        """Test successfully getting mint fee"""
        mint_fee = story_client.NFTClient.getMintFee(nft_contract)
        assert mint_fee == 1000
