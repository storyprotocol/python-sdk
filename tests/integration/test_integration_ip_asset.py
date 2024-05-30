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

from utils import get_token_id, get_story_client_in_sepolia, MockERC721, MockERC20

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

@pytest.fixture
def story_client():
    return get_story_client_in_sepolia(web3, account)

# def test_register_ip_asset(story_client):
#     token_id = get_token_id(MockERC721, story_client.web3, story_client.account)

#     response = story_client.IPAsset.register(
#         token_contract=MockERC721,
#         token_id=token_id
#     )

#     assert response is not None
#     assert 'ipId' in response
#     assert response['ipId'] is not None

# def test_registerDerivative(story_client): #can only run once since using preset variables
#     parent_ip_id = "0x567603411Fb957759Ac2090659B73cC5f099456D"
    
#     # Attach license terms to parent IP
#     license_template = "0x260B6CB6284c89dbE660c0004233f7bB99B5edE7"  # Replace with actual license template address
#     no_commercial_license_terms_id = 2  # Replace with actual license terms ID

#     attach_license_response = story_client.License.attachLicenseTerms(
#         ip_id=parent_ip_id,
#         license_template=license_template,
#         license_terms_id=no_commercial_license_terms_id
#     )
#     assert attach_license_response is not None
#     assert 'txHash' in attach_license_response
#     assert attach_license_response['txHash'] is not None

#     child_ip_id = "0xc478561B1A18331d92b2b6f6a863dbAA874729c3"
#     assert child_ip_id is not None

#     # Register derivative IP
#     response = story_client.IPAsset.registerDerivative(
#         child_ip_id=child_ip_id,
#         parent_ip_ids=[parent_ip_id],
#         license_terms_ids=[no_commercial_license_terms_id],
#         license_template=license_template
#     )
    
#     assert response is not None
#     assert 'txHash' in response
#     assert response['txHash'] is not None
#     assert isinstance(response['txHash'], str)
#     assert len(response['txHash']) > 0

# def test_registerDerivativeWithLicenseTokens(story_client): #can only run once since using preset variables

#     child_ip_id = "0xDd4330c5aeA6ab3a3E9620D2c74799bAb3BD117D"  #make sure the child ip has access to these token ids
#     assert child_ip_id is not None

#     licenseTokenIds = [1199]

#     # Register derivative IP
#     response = story_client.IPAsset.registerDerivativeWithLicenseTokens(
#         child_ip_id=child_ip_id,
#         license_token_ids=licenseTokenIds
#     )
    
#     assert response is not None
#     assert 'txHash' in response
#     assert response['txHash'] is not None
#     assert isinstance(response['txHash'], str)
#     assert len(response['txHash']) > 0

def test_mint_register_non_commercial(story_client):
    txData = story_client.NFTClient.createNFTCollection(
        name="test-collection",
        symbol="TEST",
        max_supply=25,
        mint_fee=0,
        mint_fee_token=ZERO_ADDRESS,
        owner=None
    )

    nft_contract = txData['nftContract']
    pil_type = 'non_commercial_remix'
    metadata = {
        'metadataURI': "test-uri",
        'metadataHash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
        'nftMetadataHash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
    }

    response = story_client.IPAsset.mintAndRegisterIpAssetWithPilTerms(
        nft_contract=nft_contract,
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

def test_mint_register_commercial_use(story_client):
    txData = story_client.NFTClient.createNFTCollection(
        name="test-collection",
        symbol="TEST",
        max_supply=25,
        mint_fee=0,
        mint_fee_token=ZERO_ADDRESS,
        owner=None
    )

    nft_contract = txData['nftContract']
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
        nft_contract=nft_contract,
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

def test_mint_register_commercial_remix(story_client):
    txData = story_client.NFTClient.createNFTCollection(
        name="test-collection",
        symbol="TEST",
        max_supply=25,
        mint_fee=0,
        mint_fee_token=ZERO_ADDRESS,
        owner=None
    )

    nft_contract = txData['nftContract']
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
        nft_contract=nft_contract,
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

def test_register_attach(story_client):
    txData = story_client.NFTClient.createNFTCollection(
        name="test-collection",
        symbol="TEST",
        max_supply=25,
        mint_fee=0,
        mint_fee_token=ZERO_ADDRESS,
        owner=None
    )

    nft_contract = txData['nftContract']

    token_id = get_token_id(nft_contract, story_client.web3, story_client.account)

    pil_type = 'non_commercial_remix'
    metadata = {
        'metadataURI': "test-uri",
        'metadataHash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
        'nftMetadataHash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
    }

    response = story_client.IPAsset.registerIpAndAttachPilTerms(
        nft_contract=nft_contract,
        token_id=token_id,
        pil_type=pil_type,
        metadata=metadata,
        deadline=1000,
    )

    assert 'txHash' in response
    assert isinstance(response['txHash'], str)
    assert response['txHash'].startswith("0x")

    assert 'ipId' in response
    assert isinstance(response['ipId'], str)
    assert response['ipId'].startswith("0x")

    assert 'licenseTermsId' in response
    assert isinstance(response['licenseTermsId'], int)