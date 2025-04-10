# tests/integration/test_integration_ip_asset.py

import pytest
from web3 import Web3

from setup_for_integration import (
    web3,
    account, 
    story_client,
    get_token_id,
    MockERC721,
    MockERC20,
    ZERO_ADDRESS,
    ROYALTY_POLICY,
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

        assert 'tx_hash' in response
        assert isinstance(response['tx_hash'], str)

        assert response is not None
        assert 'ip_id' in response
        assert response['ip_id'] is not None
        return response['ip_id']

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

        assert 'tx_hash' in response
        assert isinstance(response['tx_hash'], str)

        assert response is not None
        assert 'ip_id' in response
        assert response['ip_id'] is not None
        assert isinstance(response['ip_id'], str)

class TestIPAssetDerivatives:
    @pytest.fixture(scope="module")
    def child_ip_id(self, story_client):
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)

        response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )

        assert 'tx_hash' in response
        assert isinstance(response['tx_hash'], str)

        assert response is not None
        assert 'ip_id' in response
        assert response['ip_id'] is not None
        return response['ip_id']
    
    @pytest.fixture(scope="module")
    def non_commercial_license(self, story_client):
        license_register_response = story_client.License.register_non_com_social_remixing_pil()
        no_commercial_license_terms_id = license_register_response['license_terms_id']
        return no_commercial_license_terms_id

    @pytest.fixture(scope="module")
    def parent_ip_id(self, story_client, non_commercial_license):
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )

        attach_license_response = story_client.License.attach_license_terms(response['ip_id'], PIL_LICENSE_TEMPLATE, non_commercial_license)

        return response['ip_id']

    def test_register_derivative(self, story_client, child_ip_id, parent_ip_id, non_commercial_license):
        response = story_client.IPAsset.register_derivative(
            child_ip_id=child_ip_id,
            parent_ip_ids=[parent_ip_id],
            license_terms_ids=[non_commercial_license],
            max_minting_fee=0,
            max_rts=5 * 10 ** 6,
            max_revenue_share=0,
        )
        
        assert response is not None
        assert 'tx_hash' in response
        assert response['tx_hash'] is not None
        assert isinstance(response['tx_hash'], str)
        assert len(response['tx_hash']) > 0

    def test_register_derivative_with_license_tokens(self, story_client, parent_ip_id, non_commercial_license):
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        child_response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )
        child_ip_id = child_response['ip_id']

        license_token_response = story_client.License.mint_license_tokens(
            licensor_ip_id=parent_ip_id, 
            license_template=PIL_LICENSE_TEMPLATE, 
            license_terms_id=non_commercial_license, 
            amount=1,
            receiver=account.address,
            max_minting_fee=0,
            max_revenue_share=1
        )
        license_token_ids = license_token_response['license_token_ids']

        response = story_client.IPAsset.register_derivative_with_license_tokens(
            child_ip_id=child_ip_id,
            license_token_ids=license_token_ids,
            max_rts=5 * 10 ** 6
        )
        
        assert response is not None
        assert 'tx_hash' in response
        assert response['tx_hash'] is not None
        assert isinstance(response['tx_hash'], str)
        assert len(response['tx_hash']) > 0

class TestIPAssetMinting:
    @pytest.fixture(scope="module")
    def nft_collection(self, story_client):
        tx_data = story_client.NFTClient.create_nft_collection(
            name="test-collection",
            symbol="TEST",
            max_supply=100,
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=account.address,
        )
        return tx_data['nft_contract']

    def test_mint_register_attach_terms(self, story_client, nft_collection):
        metadata = {
            'ip_metadata_uri': "test-uri",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
            'nft_metadata_uri': "test-nft-uri",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
        }

        response = story_client.IPAsset.mint_and_register_ip_asset_with_pil_terms(
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

        assert 'tx_hash' in response
        assert isinstance(response['tx_hash'], str)

        assert 'ip_id' in response
        assert isinstance(response['ip_id'], str)
        assert response['ip_id'].startswith("0x")

        assert 'token_id' in response
        assert isinstance(response['token_id'], int)

        assert 'license_terms_ids' in response
        assert isinstance(response['license_terms_ids'], list)
        assert all(isinstance(id, int) for id in response['license_terms_ids'])

    def test_mint_register_ip(self, story_client, nft_collection):
        metadata = {
            'ip_metadata_uri': "test-uri",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
            'nft_metadata_uri': "test-nft-uri",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
        }
        
        response = story_client.IPAsset.mint_and_register_ip(
            spg_nft_contract=nft_collection,
            ip_metadata=metadata
        )
