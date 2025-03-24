import pytest
import time
from web3 import Web3

from setup_for_integration import (
    web3,
    account, 
    account_2,
    story_client,
    story_client_2,
    get_token_id,
    mint_tokens,
    approve,
    getBlockTimestamp,
    check_event_in_tx,
    MockERC721,
    MockERC20,
    ZERO_ADDRESS,
    ARBITRATION_POLICY_UMA,
    PIL_LICENSE_TEMPLATE,
    ROYALTY_POLICY,
    generate_cid
)

class TestDispute:
    @pytest.fixture(scope="module")
    def target_ip_id(self, story_client, story_client_2):
        """Create an IP to be disputed"""
        txData = story_client.NFTClient.createNFTCollection(
            name="test-collection",
            symbol="TEST",
            max_supply=100,
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=account.address,
            tx_options={ "wait_for_transaction": True}
        )
        
        nft_contract = txData['nftContract']

        metadata_a = {
            'ip_metadata_uri': "test-uri-a",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash-a")),
            'nft_metadata_uri': "test-nft-uri-a",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash-a"))
        }
        
        response = story_client_2.IPAsset.mintAndRegisterIp(
            spg_nft_contract=nft_contract,
            ip_metadata=metadata_a,
            tx_options={ "wait_for_transaction": True}
        )
        return response['ipId']

    @pytest.fixture(scope="module")
    def dispute_id(self, story_client, target_ip_id):
        """Create a dispute and return its ID"""
        cid = generate_cid()

        response = story_client.Dispute.raise_dispute(
            target_ip_id=target_ip_id,
            target_tag="IMPROPER_REGISTRATION",
            cid=cid,
            liveness=2592000,  # 30 days in seconds
            bond=0,
            tx_options={"wait_for_transaction": True}
        )
        
        assert 'txHash' in response
        assert isinstance(response['txHash'], str)
        assert 'disputeId' in response
        assert isinstance(response['disputeId'], int)
        return response['disputeId']

    @pytest.fixture(scope="module")
    def parent_ip_with_license(self, story_client):
        """Create a parent IP with license terms using mintAndRegisterIpAssetWithPilTerms"""
        
        txData = story_client.NFTClient.createNFTCollection(
            name="parent-collection",
            symbol="PRNT",
            max_supply=100,
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=account.address,
        )
        nft_collection = txData['nftContract']
        
        response = story_client.IPAsset.mintAndRegisterIpAssetWithPilTerms(
            spg_nft_contract=nft_collection,
            terms=[{
                'terms': {
                    'transferable': True,
                    'royalty_policy': ROYALTY_POLICY,
                    'default_minting_fee': 0,
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
                    'minting_fee': 0,
                    'hook_data': "",
                    'licensing_hook': ZERO_ADDRESS,
                    'commercial_rev_share': 90,
                    'disabled': False,
                    'expect_minimum_group_reward_share': 0,
                    'expect_group_reward_pool': ZERO_ADDRESS
                }
            }]
        )
        
        return {
            'ip_id': response['ipId'],
            'license_terms_id': response['licenseTermsIds'][0],
            'nft_contract': nft_collection
        }

    @pytest.fixture(scope="module")
    def child_ip_id(self, story_client, parent_ip_with_license):
        """Create a derivative IP (child IP) from the parent IP"""
        derivative_response = story_client.IPAsset.mintAndRegisterIpAndMakeDerivative(
            spg_nft_contract=parent_ip_with_license['nft_contract'],
            deriv_data={
                'parent_ip_ids': [parent_ip_with_license['ip_id']],
                'license_terms_ids': [parent_ip_with_license['license_terms_id']],
                'max_minting_fee': 1,
                'max_rts': 5 * 10 ** 6,
                'max_revenue_share': 100
            },
            tx_options={"wait_for_transaction": True}
        )
        
        return derivative_response['ipId']

    def test_raise_dispute(self, story_client, target_ip_id):
        """Test raising a dispute"""
        cid = generate_cid()
        
        response = story_client.Dispute.raise_dispute(
            target_ip_id=target_ip_id,
            target_tag="IMPROPER_REGISTRATION",
            cid=cid,
            liveness=2592000,  # 30 days in seconds
            bond=0,
            tx_options={"wait_for_transaction": True}
        )
        
        assert 'txHash' in response
        assert isinstance(response['txHash'], str)
        assert len(response['txHash']) > 0
        assert 'disputeId' in response
        assert isinstance(response['disputeId'], int)
        assert response['disputeId'] > 0

    def test_cancel_dispute_unauthorized(self, story_client_2, dispute_id):
        """Test attempting to cancel a dispute by an unauthorized account"""
        with pytest.raises(ValueError) as excinfo:
            story_client_2.Dispute.cancel_dispute(
                dispute_id=dispute_id,
                tx_options={"wait_for_transaction": True}
            )
        
        assert "Failed to cancel dispute" in str(excinfo.value)

    def test_resolve_dispute_unauthorized(self, story_client_2, dispute_id):
        """Test attempting to resolve a dispute by an unauthorized account"""
        with pytest.raises(ValueError) as excinfo:
            story_client_2.Dispute.resolve_dispute(
                dispute_id=dispute_id,
                data="0x",
                tx_options={"wait_for_transaction": True}
            )
        
        assert "Failed to resolve dispute" in str(excinfo.value)

    def test_raise_dispute_invalid_tag(self, story_client, target_ip_id):
        """Test raising a dispute with an invalid tag"""
        cid = generate_cid()
        
        with pytest.raises(ValueError) as excinfo:
            story_client.Dispute.raise_dispute(
                target_ip_id=target_ip_id,
                target_tag="INVALID_TAG",
                cid=cid,
                liveness=2592000,
                bond=0,
                tx_options={"wait_for_transaction": True}
            )
        
        assert "not whitelisted" in str(excinfo.value)

    def test_raise_dispute_invalid_liveness(self, story_client, target_ip_id):
        """Test raising a dispute with invalid liveness period"""
        min_liveness = story_client.Dispute.arbitration_policy_uma_client.minLiveness()
        
        cid = generate_cid()
        
        with pytest.raises(ValueError) as excinfo:
            story_client.Dispute.raise_dispute(
                target_ip_id=target_ip_id,
                target_tag="IMPROPER_REGISTRATION",
                cid=cid,
                liveness=int(min_liveness) - 1,
                bond=0,
                tx_options={"wait_for_transaction": True}
            )
        
        assert "Liveness must be between" in str(excinfo.value)
        
        max_liveness = story_client.Dispute.arbitration_policy_uma_client.maxLiveness()
        
        with pytest.raises(ValueError) as excinfo:
            story_client.Dispute.raise_dispute(
                target_ip_id=target_ip_id,
                target_tag="IMPROPER_REGISTRATION",
                cid=cid,
                liveness=int(max_liveness) + 1,
                bond=0,
                tx_options={"wait_for_transaction": True}
            )
        
        assert "Liveness must be between" in str(excinfo.value)

    def test_raise_dispute_invalid_bond(self, story_client, target_ip_id):
        """Test raising a dispute with an excessive bond amount"""
        cid = generate_cid()
        
        max_bonds = story_client.Dispute.arbitration_policy_uma_client.maxBonds(
            token=web3.to_checksum_address("0x1514000000000000000000000000000000000000")
        )
        
        with pytest.raises(ValueError) as excinfo:
            story_client.Dispute.raise_dispute(
                target_ip_id=target_ip_id,
                target_tag="IMPROPER_REGISTRATION",
                cid=cid,
                liveness=2592000,
                bond=int(max_bonds) + 1,
                tx_options={"wait_for_transaction": True}
            )
        
        assert "Bond must be less than" in str(excinfo.value)

    def test_raise_dispute_invalid_address(self, story_client):
        """Test raising a dispute with an invalid IP address"""
        cid = generate_cid()
        
        with pytest.raises(ValueError) as excinfo:
            story_client.Dispute.raise_dispute(
                target_ip_id="not-an-address",
                target_tag="IMPROPER_REGISTRATION",
                cid=cid,
                liveness=2592000,
                bond=0,
                tx_options={"wait_for_transaction": True}
            )
        
        assert "Invalid address" in str(excinfo.value)

    