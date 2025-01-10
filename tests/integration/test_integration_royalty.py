# tests/integration/test_integration_royalty.py

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
    
from utils import get_story_client_in_sepolia, mint_tokens, approve, MockERC721, get_token_id, MockERC20

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

class TestRoyalty:
    """Tests for Royalty functionality"""

    @pytest.fixture(scope="class")
    def story_client(self):
        """Setup story client"""
        return get_story_client_in_sepolia(web3, account)

    @pytest.fixture(scope="class")
    def setup_ip_and_license(self, story_client):
        """Setup IP assets and license terms"""
        # Register parent IP
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        parent_ip_response = story_client.IPAsset.register(
            token_contract=MockERC721,
            token_id=token_id
        )
        parent_ip_id = parent_ip_response['ipId']

        # Register child IP
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        child_ip_response = story_client.IPAsset.register(
            token_contract=MockERC721,
            token_id=token_id
        )
        child_ip_id = child_ip_response['ipId']

        # Register commercial remix PIL
        license_terms_response = story_client.License.registerCommercialRemixPIL(
            default_minting_fee=100000,
            currency=MockERC20,
            commercial_rev_share=10,
            royalty_policy="0xAAbaf349C7a2A84564F9CC4Ac130B3f19A718E86"
        )
        license_terms_id = license_terms_response['licenseTermsId']

        # Attach license terms
        story_client.License.attachLicenseTerms(
            ip_id=parent_ip_id,
            license_template="0x58E2c909D557Cd23EF90D14f8fd21667A5Ae7a93",
            license_terms_id=license_terms_id
        )

        # Setup ERC20 approval
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
            spender_address=story_client.Royalty.royalty_module_client.contract.address,
            amount=100000 * 10 ** 6
        )

        # Register derivative
        story_client.IPAsset.registerDerivative(
            child_ip_id=child_ip_id,
            parent_ip_ids=[parent_ip_id],
            license_terms_ids=[license_terms_id],
            license_template="0x58E2c909D557Cd23EF90D14f8fd21667A5Ae7a93"
        )

        return {
            'parent_ip_id': parent_ip_id,
            'child_ip_id': child_ip_id,
            'license_terms_id': license_terms_id
        }

    def test_pay_royalty_on_behalf(self, story_client, setup_ip_and_license):
        """Test paying royalty on behalf"""
        response = story_client.Royalty.payRoyaltyOnBehalf(
            receiver_ip_id=setup_ip_and_license['parent_ip_id'],
            payer_ip_id=setup_ip_and_license['child_ip_id'],
            token=MockERC20,
            amount=10 * 10 ** 2
        )

        assert 'txHash' in response
        assert isinstance(response['txHash'], str)
        assert response['txHash'].startswith("0x")

    def test_snapshot(self, story_client, setup_ip_and_license):
        """Test creating a snapshot"""
        response = story_client.Royalty.snapshot(
            child_ip_id=setup_ip_and_license['parent_ip_id']
        )

        assert 'txHash' in response
        assert isinstance(response['txHash'], str)
        assert 'snapshotId' in response
        assert isinstance(response['snapshotId'], int)
        return response['snapshotId']

    def test_claimable_revenue(self, story_client, setup_ip_and_license, snapshot_id):
        """Test checking claimable revenue"""
        response = story_client.Royalty.claimableRevenue(
            child_ip_id=setup_ip_and_license['parent_ip_id'],
            account_address=setup_ip_and_license['parent_ip_id'],
            snapshot_id=snapshot_id,
            token=MockERC20
        )

        assert isinstance(response, int)
        assert response >= 0

    def test_claim_revenue_by_ip_account(self, story_client, setup_ip_and_license, snapshot_id):
        """Test claiming revenue by IP account"""
        response = story_client.Royalty.claimRevenue(
            snapshot_ids=[snapshot_id],
            child_ip_id=setup_ip_and_license['parent_ip_id'],
            token=MockERC20
        )

        assert 'claimableToken' in response
        assert isinstance(response['claimableToken'], int)

    def test_claim_revenue_by_eoa(self, story_client, setup_ip_and_license):
        """Test claiming revenue by EOA"""
        # First pay royalty
        story_client.Royalty.payRoyaltyOnBehalf(
            receiver_ip_id=setup_ip_and_license['parent_ip_id'],
            payer_ip_id=setup_ip_and_license['child_ip_id'],
            token=MockERC20,
            amount=10 * 10 ** 2
        )

        # Create snapshot
        snapshot_response = story_client.Royalty.snapshot(
            child_ip_id=setup_ip_and_license['parent_ip_id']
        )
        
        # Claim revenue
        response = story_client.Royalty.claimRevenue(
            snapshot_ids=[snapshot_response['snapshotId']],
            child_ip_id=setup_ip_and_license['parent_ip_id'],
            token=MockERC20
        )

        assert 'claimableToken' in response
        assert isinstance(response['claimableToken'], int)

class TestRoyaltyWorkflow:
    """Tests for complex royalty workflows"""

    @pytest.fixture(scope="class")
    def story_client(self):
        return get_story_client_in_sepolia(web3, account)

    @pytest.fixture(scope="class")
    def setup_workflow(self, story_client):
        """Setup workflow test data"""
        # Similar setup to above, but with additional configurations
        # Implementation similar to setup_ip_and_license but with workflow-specific setup
        pass

    def test_snapshot_and_claim_by_token_batch(self, story_client, setup_workflow):
        """Test snapshotting and claiming by token batch"""
        # First pay royalty
        story_client.Royalty.payRoyaltyOnBehalf(
            receiver_ip_id=setup_workflow['parent_ip_id'],
            payer_ip_id=setup_workflow['child_ip_id'],
            token=MockERC20,
            amount=10
        )

        response = story_client.Royalty.snapshotAndClaimByTokenBatch(
            royalty_vault_ip_id=setup_workflow['parent_ip_id'],
            currency_tokens=[MockERC20]
        )

        assert 'txHash' in response
        assert isinstance(response['txHash'], str)
        assert 'snapshotId' in response
        assert isinstance(response['snapshotId'], int)
        assert 'amounts_claimed' in response
        assert isinstance(response['amounts_claimed'], int)

    def test_snapshot_and_claim_by_snapshot_batch(self, story_client, setup_workflow):
        """Test snapshotting and claiming by snapshot batch"""
        # Implementation
        pass

    def test_transfer_to_vault_and_snapshot_and_claim_by_snapshot_batch(self, story_client, setup_workflow):
        """Test transferring to vault with snapshot and claim by snapshot batch"""
        # Implementation
        pass

    def test_transfer_to_vault_and_snapshot_and_claim_by_token_batch(self, story_client, setup_workflow):
        """Test transferring to vault with snapshot and claim by token batch"""
        # Implementation
        pass