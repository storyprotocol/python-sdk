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
    def setup_ips_and_licenses(self, story_client):
        """Setup parent and child IPs with proper license relationships"""
        
        parent_token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        parent_ip_response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=parent_token_id
        )
        parent_ip_id = parent_ip_response['ipId']
        
        child_token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        child_ip_response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=child_token_id
        )
        child_ip_id = child_ip_response['ipId']
        
        license_terms_response = story_client.License.registerCommercialRemixPIL(
            default_minting_fee=100000,
            currency=MockERC20,
            commercial_rev_share=10,
            royalty_policy=ROYALTY_POLICY
        )
        license_terms_id = license_terms_response['licenseTermsId']
        
        story_client.License.attachLicenseTerms(
            ip_id=parent_ip_id,
            license_template=PIL_LICENSE_TEMPLATE,
            license_terms_id=license_terms_id
        )
        
        story_client.IPAsset.registerDerivative(
            child_ip_id=child_ip_id,
            parent_ip_ids=[parent_ip_id],
            license_terms_ids=[license_terms_id],
            max_minting_fee=0,
            max_rts=0,
            max_revenue_share=0,
        )
        
        setup_royalty_vault(story_client, parent_ip_id, account)
        
        mint_tokens(
            erc20_contract_address=MockERC20, 
            web3=web3, 
            account=account, 
            to_address=account.address, 
            amount=100000 * 10 ** 6
        )
        
        approve(
            erc20_contract_address=MockERC20, 
            web3=web3, 
            account=account, 
            spender_address=ROYALTY_MODULE, 
            amount=100000 * 10 ** 6
        )
        
        return {
            'parent_ip_id': parent_ip_id,
            'child_ip_id': child_ip_id,
            'license_terms_id': license_terms_id
        }

    def test_pay_royalty_on_behalf(self, story_client, setup_ips_and_licenses):
        """Test paying royalty on behalf of a payer IP to a receiver IP"""
        parent_ip_id = setup_ips_and_licenses['parent_ip_id']
        child_ip_id = setup_ips_and_licenses['child_ip_id']
        
        response = story_client.Royalty.payRoyaltyOnBehalf(
            receiver_ip_id=parent_ip_id,
            payer_ip_id=child_ip_id,
            token=MockERC20,
            amount=1
        )

        assert response is not None
        assert response['txHash'] is not None and isinstance(response['txHash'], str)

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

    def test_claimable_revenue(self, story_client, setup_ips_and_licenses):
        """Test checking claimable revenue"""
        parent_ip_id = setup_ips_and_licenses['parent_ip_id']
        
        response = story_client.Royalty.claimableRevenue(
            royalty_vault_ip_id=parent_ip_id,
            claimer=account.address,
            token=MockERC20
        )

        assert isinstance(response, int)

    def test_get_royalty_vault_address_unregistered(self, story_client):
        """Test getting royalty vault address for an unregistered IP"""
        unregistered_ip_id = "0x1234567890123456789012345678901234567890"
        
        with pytest.raises(ValueError, match=f"The IP with id {unregistered_ip_id} is not registered"):
            story_client.Royalty.getRoyaltyVaultAddress(ip_id=unregistered_ip_id)

    # Check
    def test_royalty_vault_token_transfer(self, story_client, setup_ips_and_licenses):
        """Test that IP account can transfer royalty vault tokens to a wallet address"""
        parent_ip_id = setup_ips_and_licenses['parent_ip_id']
        
        royalty_vault_address = story_client.Royalty.getRoyaltyVaultAddress(ip_id=parent_ip_id)
        
        assert royalty_vault_address is not None
        assert Web3.is_address(royalty_vault_address)
        
        story_client.Royalty.payRoyaltyOnBehalf(
            receiver_ip_id=parent_ip_id,
            payer_ip_id=setup_ips_and_licenses['child_ip_id'],
            token=MockERC20,
            amount=10000000  # 10 million tokens
        )

@pytest.mark.skip(reason="mintAndRegisterIpAndMakeDerivative not implemented yet")
class TestClaimAllRevenue:
    """
    Tests for the claimAllRevenue functionality, mirroring the TypeScript implementation tests.
    """
    @pytest.fixture(scope="module")
    def setup_test(self, story_client):
        # set up
        tx_data = story_client.NFTClient.createNFTCollection(
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

        ret_d = story_client.ipAsset.mintAndRegisterIpAndMakeDerivative(
            spgNftContract=spg_nft_contract,
            derivData={
                "parentIpIds": [ip_c],
                "licenseTermsIds": [license_terms_id],
                "maxMintingFee": 0,
                "maxRts": 100000000,
                "maxRevenueShare": 100,
            },
            txOptions={"waitForTransaction": True},
        )
        ip_d = ret_d["ipId"]

        return {
            "ip_a": ip_a,
            "ip_b": ip_b,
            "ip_c": ip_c,
            "ip_d": ip_d,
            "spg_nft_contract": spg_nft_contract,
            "license_terms_id": license_terms_id,
        }

    def test_claim_all_revenue(self, story_client, setup_test):
        ip_a = setup_test["ip_a"]
        ip_b = setup_test["ip_b"]
        ip_c = setup_test["ip_c"]

        ret = story_client.royalty.claimAllRevenue(
            ancestor_ip_id=ip_a,
            claimer=ip_a,
            child_ip_ids=[ip_b, ip_c],
            royalty_policies=[
                ROYALTY_POLICY,
                ROYALTY_POLICY,
            ],
            currency_tokens=[WIP_TOKEN_ADDRESS, WIP_TOKEN_ADDRESS],
        )

        assert isinstance(ret.txHashes, list)
        assert len(ret.txHashes) > 0
        assert ret.claimedTokens[0].amount == 120