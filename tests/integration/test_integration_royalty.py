# 1
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
    MockERC721,
    MockERC20,
    ZERO_ADDRESS,
    ROYALTY_POLICY,
    ROYALTY_MODULE,
    PIL_LICENSE_TEMPLATE,
    WIP_TOKEN_ADDRESS,
    setup_royalty_vault
)

class TestRoyalty:
    """
    Tests for Royalty functionality, mirroring the TypeScript implementation tests.
    """
    @pytest.fixture(scope="module")
    def parent_ip_id(self, story_client):
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)

        parent_ip_response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )
        spg_nft_contract = collection_response['nftContract']

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
        """Test paying royalty on behalf of a payer IP to a receiver IP"""
        response = story_client.Royalty.payRoyaltyOnBehalf(
            receiver_ip_id=parent_ip_id,
            payer_ip_id=child_ip_id,
            token=MockERC20,
            amount=1
        )

        assert response is not None
        assert response['txHash'] is not None and isinstance(response['txHash'], str)

    def test_claimable_revenue(self, story_client, setup_ips_and_licenses):
        """Test checking claimable revenue"""
        parent_ip_id = setup_ips_and_licenses['parent_ip_id']
        
        response = story_client.Royalty.claimableRevenue(
            royalty_vault_ip_id=parent_ip_id,
            claimer=account.address,
            token=MockERC20
        )

        assert isinstance(response, int)
    
    def test_pay_royalty_unregistered_receiver(self, story_client, setup_ips_and_licenses):
        """Test that paying royalty to unregistered IP fails appropriately"""
        child_ip_id = setup_ips_and_licenses['child_ip_id']
        unregistered_ip_id = "0x1234567890123456789012345678901234567890"
        
        with pytest.raises(ValueError, match=f"The receiver IP with id {unregistered_ip_id} is not registered"):
            story_client.Royalty.payRoyaltyOnBehalf(
                receiver_ip_id=unregistered_ip_id,
                payer_ip_id=child_ip_id,
                token=MockERC20,
                amount=1000
            )

    def test_pay_royalty_invalid_amount(self, story_client, setup_ips_and_licenses):
        """Test that paying with invalid amount fails appropriately"""
        parent_ip_id = setup_ips_and_licenses['parent_ip_id']
        child_ip_id = setup_ips_and_licenses['child_ip_id']
        
        with pytest.raises(Exception):  
            story_client.Royalty.payRoyaltyOnBehalf(
                receiver_ip_id=parent_ip_id,
                payer_ip_id=child_ip_id,
                token=MockERC20,
                amount=-1
            )

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
            mint_fee_recipient="0x0000000000000000000000000000000000000000",
            tx_options={"waitForTransaction": True},
        )
        spg_nft_contract = tx_data['nftContract']

        ret_a = story_client.IPAsset.mintAndRegisterIpAssetWithPilTerms(
            spg_nft_contract=spg_nft_contract,
            terms=[{
                "terms": {
                    "transferable": True,
                    "royalty_policy": ROYALTY_POLICY,
                    "default_minting_fee": 100,
                    "expiration": 0,
                    "commercial_use": True,
                    "commercial_attribution": False,
                    "commercializer_checker": ZERO_ADDRESS,
                    "commercializer_checker_data": ZERO_ADDRESS,
                    "commercial_rev_share": 10,
                    "commercial_rev_ceiling": 0,
                    "derivatives_allowed": True,
                    "derivatives_attribution": True,
                    "derivatives_approval": False,
                    "derivatives_reciprocal": True,
                    "derivative_rev_ceiling": 0,
                    "currency": WIP_TOKEN_ADDRESS,
                    "uri": "",
                },
                "licensing_config": {
                    "is_set": False,
                    "minting_fee": 100,
                    "hook_data": ZERO_ADDRESS,
                    "licensing_hook": ZERO_ADDRESS,                    
                    "commercial_rev_share": 0,
                    "disabled": False,
                    "expect_minimum_group_reward_share": 0,
                    "expect_group_reward_pool": ZERO_ADDRESS,
                },
            }],
        )
        ip_a = ret_a["ipId"]
        license_terms_id = ret_a["licenseTermsIds"][0]

        ret_b = story_client.IPAsset.mintAndRegisterIpAndMakeDerivative(
            spgNftContract=spg_nft_contract,
            derivData={
                "parentIpIds": [ip_a],
                "licenseTermsIds": [license_terms_id],
                "maxMintingFee": 0,
                "maxRts": 100000000,
                "maxRevenueShare": 100,
            },
            txOptions={"waitForTransaction": True},
        )
        ip_b = ret_b["ipId"]

        ret_c = story_client.ipAsset.mintAndRegisterIpAndMakeDerivative(
            spgNftContract=spg_nft_contract,
            derivData={
                "parentIpIds": [ip_b],
                "licenseTermsIds": [license_terms_id],
                "maxMintingFee": 0,
                "maxRts": 100000000,
                "maxRevenueShare": 100,
            },
            txOptions={"waitForTransaction": True},
        )
        ip_c = ret_c["ipId"]

        return {
            "ip_a": ip_a,
            "ip_b": ip_b,
            "ip_c": ip_c,
            "spg_nft_contract": spg_nft_contract,
            "license_terms_id": license_terms_id,
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

        assert isinstance(response['txHashes'], list)
        assert len(response['txHashes']) > 0
        assert response['claimedTokens'][0]['amount'] == 120