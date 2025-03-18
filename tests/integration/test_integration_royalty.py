import pytest
from web3 import Web3
import copy

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
    PIL_LICENSE_TEMPLATE,
    setup_royalty_vault
)

class TestRoyalty:
    @pytest.fixture(scope="module")
    def parent_ip_id(self, story_client):
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)

        parent_ip_response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )

        parent_ip_id = parent_ip_response['ipId']

        return parent_ip_id

    @pytest.fixture(scope="module")
    def child_ip_id(self, story_client):
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)

        response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )

        return response['ipId']

    @pytest.fixture(scope="module")
    def attach_and_register(self, story_client, parent_ip_id, child_ip_id):
        license_terms_response = story_client.License.registerCommercialRemixPIL(
            default_minting_fee=1,
            currency=MockERC20,
            commercial_rev_share=10,
            royalty_policy=ROYALTY_POLICY
        )

        attach_license_response = story_client.License.attachLicenseTerms(
            ip_id=parent_ip_id,
            license_template=PIL_LICENSE_TEMPLATE,
            license_terms_id=license_terms_response['licenseTermsId']
        )

        derivative_response = story_client.IPAsset.registerDerivative(
            child_ip_id=child_ip_id,
            parent_ip_ids=[parent_ip_id],
            license_terms_ids=[license_terms_response['licenseTermsId']],
            max_minting_fee=0,
            max_rts=0,
            max_revenue_share=0,
        )

        setup_royalty_vault(story_client, parent_ip_id, account)

    def test_pay_royalty_on_behalf(self, story_client, parent_ip_id, child_ip_id, attach_and_register):
        response = story_client.Royalty.payRoyaltyOnBehalf(
            receiver_ip_id=parent_ip_id,
            payer_ip_id=child_ip_id,
            token=MockERC20,
            amount=1000
        )

        assert response is not None
        assert response['txHash'] is not None

    def test_claimable_revenue(self, story_client, parent_ip_id, child_ip_id, attach_and_register):
        response = story_client.Royalty.claimableRevenue(
            royalty_vault_ip_id=parent_ip_id,
            claimer=account.address,
            token=MockERC20
        )

        assert response is not None
        assert type(response) == int
        assert response > 0

class TestClaimAllRevenue:
    @pytest.fixture(scope="module")
    def setup_claim_all_revenue(self, story_client):
        # Create NFT collection
        collection_response = story_client.NFTClient.createNFTCollection(
            name="free-collection",
            symbol="FREE", 
            max_supply=100,
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=ZERO_ADDRESS
        )
        spg_nft_contract = collection_response['nftContract']

        # Define license terms data template
        license_terms_template = [{
            'terms': {
                'transferable': True,
                'royalty_policy': ROYALTY_POLICY,
                'default_minting_fee': 100,
                'expiration': 0,
                'commercial_use': True,
                'commercial_attribution': False,
                'commercializer_checker': ZERO_ADDRESS,
                'commercializer_checker_data': ZERO_ADDRESS,
                'commercial_rev_share': 10,
                'commercial_rev_ceiling': 0,
                'derivatives_allowed': True,
                'derivatives_attribution': True,
                'derivatives_approval': False,
                'derivatives_reciprocal': True,
                'derivative_rev_ceiling': 0,
                'currency': MockERC20,
                'uri': ''
            },
            'licensing_config': {
                'is_set': True,
                'minting_fee': 100,
                'hook_data': ZERO_ADDRESS,
                'licensing_hook': ZERO_ADDRESS,
                'commercial_rev_share': 0,
                'disabled': False,
                'expect_minimum_group_reward_share': 0,
                'expect_group_reward_pool': ZERO_ADDRESS
            }
        }]

        # Create unique metadata for each IP
        metadata_a = {
            'ip_metadata_uri': "test-uri-a",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash-a")),
            'nft_metadata_uri': "test-nft-uri-a",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash-a"))
        }
        
        metadata_b = {
            'ip_metadata_uri': "test-uri-b",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash-b")),
            'nft_metadata_uri': "test-nft-uri-b",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash-b"))
        }
        
        metadata_c = {
            'ip_metadata_uri': "test-uri-c",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash-c")),
            'nft_metadata_uri': "test-nft-uri-c",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash-c"))
        }
        
        metadata_d = {
            'ip_metadata_uri': "test-uri-d",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash-d")),
            'nft_metadata_uri': "test-nft-uri-d",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash-d"))
        }

        # Register IP A with PIL terms
        ip_a_response = story_client.IPAsset.mintAndRegisterIpAssetWithPilTerms(
            spg_nft_contract=spg_nft_contract,
            terms=copy.deepcopy(license_terms_template),
            ip_metadata=metadata_a
        )
        ip_a = ip_a_response['ipId']
        license_terms_id = ip_a_response['licenseTermsIds'][0]

        # Register IP B as derivative of A
        ip_b_response = story_client.IPAsset.mintAndRegisterIp(
            spg_nft_contract=spg_nft_contract,
            ip_metadata=metadata_b
        )
        ip_b = ip_b_response['ipId']
        ip_b_derivative_response = story_client.IPAsset.registerDerivative(
            child_ip_id=ip_b,
            parent_ip_ids=[ip_a],
            license_terms_ids=[license_terms_id]
        )

        # Register IP C as derivative of B
        ip_c_response = story_client.IPAsset.mintAndRegisterIp(
            spg_nft_contract=spg_nft_contract,
            ip_metadata=metadata_c
        )
        ip_c = ip_c_response['ipId']
        ip_c_derivative_response = story_client.IPAsset.registerDerivative( 
            child_ip_id=ip_c,
            parent_ip_ids=[ip_b],
            license_terms_ids=[license_terms_id]
        )

        # Register IP D as derivative of C
        ip_d_response = story_client.IPAsset.mintAndRegisterIp(
            spg_nft_contract=spg_nft_contract,
            ip_metadata=metadata_d
        )
        ip_d = ip_d_response['ipId']
        ip_d_derivative_response = story_client.IPAsset.registerDerivative(
            child_ip_id=ip_d,
            parent_ip_ids=[ip_c],
            license_terms_ids=[license_terms_id]
        )
    
        return {
            'ip_a': ip_a,
            'ip_b': ip_b,
            'ip_c': ip_c,
            'ip_d': ip_d
        }

    def test_claim_all_revenue(self, setup_claim_all_revenue, story_client):
        response = story_client.Royalty.claimAllRevenue(
            ancestor_ip_id=setup_claim_all_revenue['ip_a'],
            claimer=setup_claim_all_revenue['ip_a'],
            child_ip_ids=[setup_claim_all_revenue['ip_b'], setup_claim_all_revenue['ip_c']],
            royalty_policies=[ROYALTY_POLICY, ROYALTY_POLICY],
            currency_tokens=[MockERC20, MockERC20]
        ) 

        assert response is not None
        assert 'txHashes' in response
        assert isinstance(response['txHashes'], list)
        assert len(response['txHashes']) > 0
        assert response['claimedTokens'][0]['amount'] == 120

    @pytest.fixture(scope="module")
    def setup_claim_all_revenue_claim_options(self, story_client):
        # Create NFT collection
        collection_response = story_client.NFTClient.createNFTCollection(
            name="free-collection",
            symbol="FREE", 
            max_supply=100,
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=ZERO_ADDRESS
        )
        spg_nft_contract = collection_response['nftContract']

        # Define license terms data template
        license_terms_template = [{
            'terms': {
                'transferable': True,
                'royalty_policy': ROYALTY_POLICY,
                'default_minting_fee': 100,
                'expiration': 0,
                'commercial_use': True,
                'commercial_attribution': False,
                'commercializer_checker': ZERO_ADDRESS,
                'commercializer_checker_data': ZERO_ADDRESS,
                'commercial_rev_share': 10,
                'commercial_rev_ceiling': 0,
                'derivatives_allowed': True,
                'derivatives_attribution': True,
                'derivatives_approval': False,
                'derivatives_reciprocal': True,
                'derivative_rev_ceiling': 0,
                'currency': MockERC20,
                'uri': ''
            },
            'licensing_config': {
                'is_set': True,
                'minting_fee': 100,
                'hook_data': ZERO_ADDRESS,
                'licensing_hook': ZERO_ADDRESS,
                'commercial_rev_share': 0,
                'disabled': False,
                'expect_minimum_group_reward_share': 0,
                'expect_group_reward_pool': ZERO_ADDRESS
            }
        }]

        # Create unique metadata for each IP
        metadata_a = {
            'ip_metadata_uri': "test-uri-a",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash-a")),
            'nft_metadata_uri': "test-nft-uri-a",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash-a"))
        }
        
        metadata_b = {
            'ip_metadata_uri': "test-uri-b",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash-b")),
            'nft_metadata_uri': "test-nft-uri-b",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash-b"))
        }
        
        metadata_c = {
            'ip_metadata_uri': "test-uri-c",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash-c")),
            'nft_metadata_uri': "test-nft-uri-c",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash-c"))
        }
        
        metadata_d = {
            'ip_metadata_uri': "test-uri-d",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash-d")),
            'nft_metadata_uri': "test-nft-uri-d",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash-d"))
        }

        # Register IP A with PIL terms
        ip_a_response = story_client.IPAsset.mintAndRegisterIpAssetWithPilTerms(
            spg_nft_contract=spg_nft_contract,
            terms=copy.deepcopy(license_terms_template),
            ip_metadata=metadata_a
        )
        ip_a = ip_a_response['ipId']
        license_terms_id = ip_a_response['licenseTermsIds'][0]

        # Register IP B as derivative of A
        ip_b_response = story_client.IPAsset.mintAndRegisterIp(
            spg_nft_contract=spg_nft_contract,
            ip_metadata=metadata_b
        )
        ip_b = ip_b_response['ipId']
        ip_b_derivative_response = story_client.IPAsset.registerDerivative(
            child_ip_id=ip_b,
            parent_ip_ids=[ip_a],
            license_terms_ids=[license_terms_id]
        )

        # Register IP C as derivative of B
        ip_c_response = story_client.IPAsset.mintAndRegisterIp(
            spg_nft_contract=spg_nft_contract,
            ip_metadata=metadata_c
        )
        ip_c = ip_c_response['ipId']
        ip_c_derivative_response = story_client.IPAsset.registerDerivative( 
            child_ip_id=ip_c,
            parent_ip_ids=[ip_b],
            license_terms_ids=[license_terms_id]
        )

        # Register IP D as derivative of C
        ip_d_response = story_client.IPAsset.mintAndRegisterIp(
            spg_nft_contract=spg_nft_contract,
            ip_metadata=metadata_d
        )
        ip_d = ip_d_response['ipId']
        ip_d_derivative_response = story_client.IPAsset.registerDerivative(
            child_ip_id=ip_d,
            parent_ip_ids=[ip_c],
            license_terms_ids=[license_terms_id]
        )

        return {
            'ip_a': ip_a,
            'ip_b': ip_b,
            'ip_c': ip_c,
            'ip_d': ip_d
        }

    def test_claim_all_revenue_claim_options(self, setup_claim_all_revenue_claim_options, story_client):
        response = story_client.Royalty.claimAllRevenue(
            ancestor_ip_id=setup_claim_all_revenue_claim_options['ip_a'],
            claimer=setup_claim_all_revenue_claim_options['ip_a'],
            child_ip_ids=[setup_claim_all_revenue_claim_options['ip_b'], setup_claim_all_revenue_claim_options['ip_c']],
            royalty_policies=[ROYALTY_POLICY, ROYALTY_POLICY],
            currency_tokens=[MockERC20, MockERC20],
            claim_options={
                'autoTransferAllClaimedTokensFromIp': False
            }
        )

        assert response is not None
        assert 'txHashes' in response
        assert isinstance(response['txHashes'], list)
        assert len(response['txHashes']) > 0
        assert response['claimedTokens'][0]['amount'] == 120