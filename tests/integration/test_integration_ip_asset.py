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

class TestIPAssetRegistration:
    @pytest.fixture(scope="module")
    def child_ip_id(self, story_client):
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

    def test_register_ip_asset(self, story_client, child_ip_id):
        assert child_ip_id is not None

    def test_register_ip_asset_with_metadata(self, story_client):
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

class TestIPAssetDerivatives:
    @pytest.fixture(scope="module")
    def non_commercial_license(self, story_client):
        license_register_response = story_client.License.registerNonComSocialRemixingPIL()
        no_commercial_license_terms_id = license_register_response['licenseTermsId']
        return no_commercial_license_terms_id

    @pytest.fixture(scope="module")
    def parent_ip_id(self, story_client, non_commercial_license):
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )

        attach_license_response = story_client.License.attachLicenseTerms(response['ipId'], PIL_LICENSE_TEMPLATE, non_commercial_license)

        return response['ipId']

    def test_register_derivative(self, story_client, child_ip_id, parent_ip_id, non_commercial_license):
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

    def test_registerDerivativeWithLicenseTokens(self, story_client, parent_ip_id, non_commercial_license):
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

class TestIPAssetMinting:
    @pytest.fixture(scope="module")
    def nft_collection(self, story_client):
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

    def test_mint_register_attach_terms(self, story_client, nft_collection):
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

    def test_mint_register_ip(self, story_client, nft_collection):
        metadata = {
            'ip_metadata_uri': "test-uri",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
            'nft_metadata_uri': "test-nft-uri",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
        }
        
        response = story_client.IPAsset.mintAndRegisterIp(
            spg_nft_contract=nft_collection,
            ip_metadata=metadata
        )
