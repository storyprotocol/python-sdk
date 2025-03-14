import os
import sys
import pytest
from dotenv import load_dotenv
from web3 import Web3

from setup_for_integration import (
    web3,
    account, 
    story_client,
    get_token_id,
    mint_tokens,
    approve,
    getBlockTimestamp,
    check_event_in_tx,
    MockERC721,
    MockERC20,
    ZERO_ADDRESS,
    ROYALTY_POLICY,
    ROYALTY_MODULE,
    PIL_LICENSE_TEMPLATE
)

@pytest.fixture(scope="module")
def child_ip_id(story_client):
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)

    response = story_client.IPAsset.register(
        nft_contract=MockERC721,
        token_id=token_id
    )

    assert 'txHash' in response
    assert isinstance(response['txHash'], str)

    assert response is not None
    assert 'ipId' in response
    assert response['ipId'] is not None
    return response['ipId']

def test_register_ip_asset(story_client, child_ip_id):
    assert child_ip_id is not None

def test_register_ip_asset_with_metadata(story_client):
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
    metadata = {
        'ip_metadata_uri': "test-uri",
        'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
        'nft_metadata_uri': "test-nft-uri",
        'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
    }

    response = story_client.IPAsset.register(
        nft_contract=MockERC721,
        token_id=token_id,
        ip_metadata=metadata,
        deadline=1000
    )

    assert 'txHash' in response
    assert isinstance(response['txHash'], str)

    assert response is not None
    assert 'ipId' in response
    assert response['ipId'] is not None
    assert isinstance(response['ipId'], str)

@pytest.fixture(scope="module")
def non_commercial_license(story_client):
    license_register_response = story_client.License.registerNonComSocialRemixingPIL()
    no_commercial_license_terms_id = license_register_response['licenseTermsId']
    return no_commercial_license_terms_id

@pytest.fixture(scope="module")
def parent_ip_id(story_client, non_commercial_license):
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
    response = story_client.IPAsset.register(
        nft_contract=MockERC721,
        token_id=token_id
    )

    attach_license_response = story_client.License.attachLicenseTerms(response['ipId'], PIL_LICENSE_TEMPLATE, non_commercial_license)

    return response['ipId']

def test_register_derivative(story_client, child_ip_id, parent_ip_id, non_commercial_license):
    response = story_client.IPAsset.registerDerivative(
        child_ip_id=child_ip_id,
        parent_ip_ids=[parent_ip_id],
        license_terms_ids=[non_commercial_license],
        max_minting_fee=0,
        max_rts=5 * 10 ** 6,
        max_revenue_share=0,
    )
    
    assert response is not None
    assert 'txHash' in response
    assert response['txHash'] is not None
    assert isinstance(response['txHash'], str)
    assert len(response['txHash']) > 0

def test_registerDerivativeWithLicenseTokens(story_client, parent_ip_id, non_commercial_license):
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
    child_response = story_client.IPAsset.register(
        nft_contract=MockERC721,
        token_id=token_id
    )
    child_ip_id = child_response['ipId']

    license_token_response = story_client.License.mintLicenseTokens(
        licensor_ip_id=parent_ip_id, 
        license_template=PIL_LICENSE_TEMPLATE, 
        license_terms_id=non_commercial_license, 
        amount=1,
        receiver=account.address,
        max_minting_fee=0,
        max_revenue_share=1
    )
    licenseTokenIds = license_token_response['licenseTokenIds']

    response = story_client.IPAsset.registerDerivativeWithLicenseTokens(
        child_ip_id=child_ip_id,
        license_token_ids=licenseTokenIds,
        max_rts=5 * 10 ** 6
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
        max_supply=100,
        is_public_minting=True,
        mint_open=True,
        contract_uri="test-uri",
        mint_fee_recipient=account.address,
    )
    return txData['nftContract']

def test_mint_register_attach_terms(story_client, nft_collection):

    metadata = {
        'ip_metadata_uri': "test-uri",
        'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
        'nft_metadata_uri': "test-nft-uri",
        'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
    }

    response = story_client.IPAsset.mintAndRegisterIpAssetWithPilTerms(
        spg_nft_contract=nft_collection,
        terms=[{
            'terms': {
                'transferable': True,
                'royalty_policy': ROYALTY_POLICY,
                'default_minting_fee': 1,
                'expiration': 0,
                'commercial_use': True,
                'commercial_attribution': False,
                'commercializer_checker': ZERO_ADDRESS,
                'commercializer_checker_data': ZERO_ADDRESS,
                'commercial_rev_share': 90,
                'commercial_rev_ceiling': 0,
                'derivatives_allowed': True,
                'derivatives_attribution': True,
                'derivatives_approval': False,
                'derivatives_reciprocal': True,
                'derivative_rev_ceiling': 0,
                'currency': MockERC20,
                'uri': ""
            },
            'licensing_config': {
                'is_set': True,
                'minting_fee': 1,
                'hook_data': "",
                'licensing_hook': ZERO_ADDRESS,
                'commercial_rev_share': 90,
                'disabled': False,
                'expect_minimum_group_reward_share': 0,
                'expect_group_reward_pool': ZERO_ADDRESS
            }
        }],
        ip_metadata=metadata
    )

    assert 'txHash' in response
    assert isinstance(response['txHash'], str)

    assert 'ipId' in response
    assert isinstance(response['ipId'], str)
    assert response['ipId'].startswith("0x")

    assert 'tokenId' in response
    assert isinstance(response['tokenId'], int)

    assert 'licenseTermsIds' in response
    assert isinstance(response['licenseTermsIds'], list)
    assert all(isinstance(id, int) for id in response['licenseTermsIds'])

# def test_register_attach(story_client, nft_collection):
#     token_id = get_token_id_from_collection(nft_collection, story_client.web3, story_client.account)

#     pil_type = 'non_commercial_remix'
#     metadata = {
#         'metadataURI': "test-uri",
#         'metadataHash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
#         'nftMetadataHash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
#     }
#     deadline = getBlockTimestamp(web3) + 1000
#     response = story_client.IPAsset.registerIpAndAttachPilTerms(
#         nft_contract=nft_collection,
#         token_id=token_id,
#         license_terms_data=[
#             {
#                 'terms': {
#                     'transferable': True,
#                     'royalty_policy': ZERO_ADDRESS,
#                     'minting_fee': 0,
#                     'expiration': 0,
#                     'commercial_use': False,
#                     'commercial_attribution': False,
#                     'commercializer_checker': ZERO_ADDRESS,
#                     'commercializer_checker_data': ZERO_ADDRESS,
#                     'commercial_rev_share': 0,
#                     'commercial_rev_ceiling': 0,
#                     'derivatives_allowed': True,
#                     'derivatives_attribution': True,
#                     'derivatives_approval': False,
#                     'derivatives_reciprocal': True,
#                     'derivative_rev_ceiling': 0,
#                     'currency': MockERC20,
#                     'uri': ""
#                 },
#                 'licensing_config': {
#                     'is_set': True,
#                     'minting_fee': 0,
#                     'licensing_hook': ZERO_ADDRESS,
#                     'hook_data': ZERO_ADDRESS,
#                     'commercial_rev_share': 0,
#                     'disabled': False,
#                     'expect_minimum_group_reward_share': 0,
#                     'expect_group_reward_pool': ZERO_ADDRESS
#                 }
#             },
#             {
#                 'terms': {
#                     'transferable': True,
#                     'royalty_policy': ROYALTY_POLICY,
#                     'minting_fee': 10000,
#                     'expiration': 1000,
#                     'commercial_use': True,
#                     'commercial_attribution': False,
#                     'commercializer_checker': ZERO_ADDRESS,
#                     'commercializer_checker_data': ZERO_ADDRESS,
#                     'commercial_rev_share': 0,
#                     'commercial_rev_ceiling': 0,
#                     'derivatives_allowed': True,
#                     'derivatives_attribution': True,
#                     'derivatives_approval': False,
#                     'derivatives_reciprocal': True,
#                     'derivative_rev_ceiling': 0,
#                     'currency': MockERC20,
#                     'uri': "test case"
#                 },
#                 'licensing_config': {
#                     'is_set': True,
#                     'minting_fee': 10000,
#                     'licensing_hook': ZERO_ADDRESS,
#                     'hook_data': ZERO_ADDRESS,
#                     'commercial_rev_share': 0,
#                     'disabled': False,
#                     'expect_minimum_group_reward_share': 0,
#                     'expect_group_reward_pool': ZERO_ADDRESS
#                 }
#             }
#         ],
#         ip_metadata=metadata,
#         deadline=deadline
#     )

#     assert 'txHash' in response
#     assert isinstance(response['txHash'], str)
#     assert response['txHash'].startswith("0x")

#     assert 'ipId' in response
#     assert isinstance(response['ipId'], str)
#     assert response['ipId'].startswith("0x")

#     assert 'licenseTermsId' in response
#     assert isinstance(response['licenseTermsId'], int)

# def test_register_ip_derivative(story_client, nft_collection):
#     child_token_id = get_token_id(nft_collection, story_client.web3, story_client.account)

#     pil_type = 'non_commercial_remix'
#     mint_metadata = {
#         'metadataHash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
#         'nftMetadataHash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
#     }

#     mint_response = story_client.IPAsset.mintAndRegisterIpAssetWithPilTerms(
#         nft_contract=nft_collection,
#         pil_type=pil_type,
#         metadata=mint_metadata,
#         minting_fee=100,
#         commercial_rev_share=10,
#         currency=MockERC20
#     )

#     parent_ip_id = mint_response['ipId']
#     license_terms_id = mint_response['licenseTermsId']

#     metadata = {
#         'metadataURI': "test-uri",
#         'metadataHash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
#     }
#     derivData = {
#         'parentIpIds': [parent_ip_id],
#         'licenseTermsIds': [license_terms_id]
#     }

#     response = story_client.IPAsset.registerDerivativeIp(
#         nft_contract=nft_collection,
#         token_id=child_token_id,
#         metadata=metadata,
#         deadline=1000,
#         deriv_data=derivData
#     )

#     assert 'txHash' in response
#     assert isinstance(response['txHash'], str)
#     assert response['txHash'].startswith("0x")

#     assert 'ipId' in response
#     assert isinstance(response['ipId'], str)
#     assert response['ipId'].startswith("0x")
