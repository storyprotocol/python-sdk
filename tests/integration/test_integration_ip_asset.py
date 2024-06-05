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

from utils import get_token_id, get_story_client_in_sepolia, MockERC721, MockERC20, getBlockTimestamp

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
    return get_story_client_in_sepolia(web3, account)

@pytest.fixture(scope="module")
def parent_ip_id(story_client):
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)

    response = story_client.IPAsset.register(
        token_contract=MockERC721,
        token_id=token_id
    )

    assert response is not None
    assert 'ipId' in response
    assert response['ipId'] is not None

    return response['ipId']

def test_register_ip_asset(story_client, parent_ip_id):
    assert parent_ip_id is not None

def test_register_ip_asset_with_metadata(story_client):
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
    metadata = {
        'metadataURI': "test-uri",
        'metadataHash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
        'nftMetadataHash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
    }

    response = story_client.IPAsset.register(
        token_contract=MockERC721,
        token_id=token_id,
        metadata=metadata,
        deadline=1000
    )

    assert response is not None
    assert 'ipId' in response
    assert response['ipId'] is not None
    assert isinstance(response['ipId'], str)

@pytest.fixture(scope="module")
def attach_non_commercial_license(story_client, parent_ip_id):
    license_template = "0x260B6CB6284c89dbE660c0004233f7bB99B5edE7"
    no_commercial_license_terms_id = 2

    attach_license_response = story_client.License.attachLicenseTerms(
        ip_id=parent_ip_id,
        license_template=license_template,
        license_terms_id=no_commercial_license_terms_id
    )

def test_register_derivative(story_client, parent_ip_id, attach_non_commercial_license):
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
    child_response = story_client.IPAsset.register(
        token_contract=MockERC721,
        token_id=token_id
    )
    child_ip_id = child_response['ipId']

    response = story_client.IPAsset.registerDerivative(
        child_ip_id=child_ip_id,
        parent_ip_ids=[parent_ip_id],
        license_terms_ids=[2],
        license_template="0x260B6CB6284c89dbE660c0004233f7bB99B5edE7"
    )
    
    assert response is not None
    assert 'txHash' in response
    assert response['txHash'] is not None
    assert isinstance(response['txHash'], str)
    assert len(response['txHash']) > 0

def test_registerDerivativeWithLicenseTokens(story_client, parent_ip_id, attach_non_commercial_license):
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
    child_response = story_client.IPAsset.register(
        token_contract=MockERC721,
        token_id=token_id
    )
    child_ip_id = child_response['ipId']

    license_token_response = story_client.License.mintLicenseTokens(
        licensor_ip_id=parent_ip_id, 
        license_template="0x260B6CB6284c89dbE660c0004233f7bB99B5edE7", 
        license_terms_id=2, 
        amount=1, 
        receiver=account.address
    )
    licenseTokenIds = license_token_response['licenseTokenIds']

    response = story_client.IPAsset.registerDerivativeWithLicenseTokens(
        child_ip_id=child_ip_id,
        license_token_ids=licenseTokenIds
    )
    
    assert response is not None
    assert 'txHash' in response
    assert response['txHash'] is not None
    assert isinstance(response['txHash'], str)
    assert len(response['txHash']) > 0

@pytest.fixture(scope="module")
def nft_collection(story_client):
    txData = story_client.NFTClient.createNFTCollection(
        name="test-collection",
        symbol="TEST",
        max_supply=25,
        mint_fee=0,
        mint_fee_token=ZERO_ADDRESS,
        owner=None
    )
    return txData['nftContract']

def test_mint_register_non_commercial(story_client, nft_collection):
    pil_type = 'non_commercial_remix'
    metadata = {
        'metadataURI': "test-uri",
        'metadataHash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
        'nftMetadataHash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
    }

    response = story_client.IPAsset.mintAndRegisterIpAssetWithPilTerms(
        nft_contract=nft_collection,
        pil_type=pil_type,
        metadata=metadata
    )

    assert 'txHash' in response
    assert isinstance(response['txHash'], str)
    assert response['txHash'].startswith("0x")

    assert 'ipId' in response
    assert isinstance(response['ipId'], str)
    assert response['ipId'].startswith("0x")

    assert 'tokenId' in response
    assert isinstance(response['tokenId'], int)

    assert 'licenseTermsId' in response
    assert isinstance(response['licenseTermsId'], int)

def test_mint_register_commercial_use(story_client, nft_collection):
    pil_type = 'commercial_use'
    metadata = {
        'metadataURI': "test-uri",
        'metadataHash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
        'nftMetadataHash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
    }
    minting_fee = 100
    commercial_rev_share = 10
    currency = MockERC20

    response = story_client.IPAsset.mintAndRegisterIpAssetWithPilTerms(
        nft_contract=nft_collection,
        pil_type=pil_type,
        metadata=metadata,
        minting_fee=minting_fee,
        commercial_rev_share=commercial_rev_share,
        currency=currency
    )

    assert 'txHash' in response
    assert isinstance(response['txHash'], str)
    assert response['txHash'].startswith("0x")

    assert 'ipId' in response
    assert isinstance(response['ipId'], str)
    assert response['ipId'].startswith("0x")

    assert 'tokenId' in response
    assert isinstance(response['tokenId'], int)

    assert 'licenseTermsId' in response
    assert isinstance(response['licenseTermsId'], int)

def test_mint_register_commercial_remix(story_client, nft_collection):
    pil_type = 'commercial_remix'
    metadata = {
        'metadataURI': "test-uri",
        'metadataHash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
        'nftMetadataHash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
    }
    minting_fee = 100
    commercial_rev_share = 10
    currency = MockERC20

    response = story_client.IPAsset.mintAndRegisterIpAssetWithPilTerms(
        nft_contract=nft_collection,
        pil_type=pil_type,
        metadata=metadata,
        minting_fee=minting_fee,
        commercial_rev_share=commercial_rev_share,
        currency=currency
    )
    
    assert 'txHash' in response
    assert isinstance(response['txHash'], str)
    assert response['txHash'].startswith("0x")

    assert 'ipId' in response
    assert isinstance(response['ipId'], str)
    assert response['ipId'].startswith("0x")

    assert 'tokenId' in response
    assert isinstance(response['tokenId'], int)

    assert 'licenseTermsId' in response
    assert isinstance(response['licenseTermsId'], int)

def test_register_attach(story_client, nft_collection):
    token_id = get_token_id(nft_collection, story_client.web3, story_client.account)

    pil_type = 'non_commercial_remix'
    metadata = {
        'metadataURI': "test-uri",
        'metadataHash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
        'nftMetadataHash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
    }
    deadline = getBlockTimestamp(web3) + 1000

    response = story_client.IPAsset.registerIpAndAttachPilTerms(
        nft_contract=nft_collection,
        token_id=token_id,
        pil_type=pil_type,
        metadata=metadata,
        deadline=deadline,
    )

    assert 'txHash' in response
    assert isinstance(response['txHash'], str)
    assert response['txHash'].startswith("0x")

    assert 'ipId' in response
    assert isinstance(response['ipId'], str)
    assert response['ipId'].startswith("0x")

    assert 'licenseTermsId' in response
    assert isinstance(response['licenseTermsId'], int)

def test_register_ip_derivative(story_client, nft_collection):
    child_token_id = get_token_id(nft_collection, story_client.web3, story_client.account)

    pil_type = 'non_commercial_remix'
    mint_metadata = {
        'metadataHash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
        'nftMetadataHash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
    }

    mint_response = story_client.IPAsset.mintAndRegisterIpAssetWithPilTerms(
        nft_contract=nft_collection,
        pil_type=pil_type,
        metadata=mint_metadata,
        minting_fee=100,
        commercial_rev_share=10,
        currency=MockERC20
    )

    parent_ip_id = mint_response['ipId']
    license_terms_id = mint_response['licenseTermsId']

    metadata = {
        'metadataURI': "test-uri",
        'metadataHash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
    }
    derivData = {
        'parentIpIds': [parent_ip_id],
        'licenseTermsIds': [license_terms_id]
    }

    response = story_client.IPAsset.registerDerivativeIp(
        nft_contract=nft_collection,
        token_id=child_token_id,
        metadata=metadata,
        deadline=1000,
        deriv_data=derivData
    )

    assert 'txHash' in response
    assert isinstance(response['txHash'], str)
    assert response['txHash'].startswith("0x")

    assert 'ipId' in response
    assert isinstance(response['ipId'], str)
    assert response['ipId'].startswith("0x")
