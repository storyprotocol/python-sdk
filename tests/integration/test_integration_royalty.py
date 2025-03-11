import pytest
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
            amount=69
        )

    
