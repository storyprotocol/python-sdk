# tests/integration/test_integration_license.py

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

from utils import get_story_client_in_odyssey, MockERC20, MockERC721, get_token_id, approve, mint_tokens

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

@pytest.fixture(scope="module")
def story_client():
    return get_story_client_in_odyssey(web3, account)

class TestLicenseRegistration:
    """Tests for registering different types of licenses"""
    
    def test_register_basic_pil_terms(self, story_client):
        """Test registering basic PIL terms"""
        response = story_client.License.registerPILTerms(
            transferable=False,
            royalty_policy=ZERO_ADDRESS,
            default_minting_fee=1,
            expiration=0,
            commercial_use=False,
            commercial_attribution=False,
            commercializer_checker=ZERO_ADDRESS,
            commercializer_checker_data="0x",
            commercial_rev_share=0,
            commercial_rev_ceiling=0,
            derivatives_allowed=False,
            derivatives_attribution=False,
            derivatives_approval=False,
            derivatives_reciprocal=False,
            derivative_rev_ceiling=0,
            currency=MockERC20,
            uri=""
        )

        assert 'licenseTermsId' in response
        assert isinstance(response['licenseTermsId'], int)
        assert response['licenseTermsId'] > 0

    def test_register_non_commercial_social_remixing(self, story_client):
        """Test registering non-commercial social remixing PIL"""
        response = story_client.License.registerNonComSocialRemixingPIL()

        assert 'licenseTermsId' in response
        assert isinstance(response['licenseTermsId'], int)
        assert response['licenseTermsId'] > 0

    def test_register_commercial_use_pil(self, story_client):
        """Test registering commercial use PIL"""
        response = story_client.License.registerCommercialUsePIL(
            default_minting_fee=1,
            currency=MockERC20,
        )

        assert 'licenseTermsId' in response
        assert isinstance(response['licenseTermsId'], int)
        assert response['licenseTermsId'] > 0

    def test_register_commercial_remix_pil(self, story_client):
        """Test registering commercial remix PIL"""
        response = story_client.License.registerCommercialRemixPIL(
            default_minting_fee=1,
            commercial_rev_share=100,
            currency=MockERC20,
            royalty_policy="0x28b4F70ffE5ba7A26aEF979226f77Eb57fb9Fdb6"
        )

        assert 'licenseTermsId' in response
        assert isinstance(response['licenseTermsId'], int)
        assert response['licenseTermsId'] > 0

class TestLicenseOperations:
    """Tests for license operations like attaching and minting"""

    @pytest.fixture(scope="class")
    def setup_license_data(self, story_client):
        """Setup fixture for license operations tests"""
        # Register an IP
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        register_response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )
        ip_id = register_response['ipId']

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
            spender_address="0xEa6eD700b11DfF703665CCAF55887ca56134Ae3B",
            amount=100000 * 10 ** 6
        )

        # Register license terms
        license_response = story_client.License.registerCommercialRemixPIL(
            default_minting_fee=1,
            commercial_rev_share=100,
            currency=MockERC20,
            royalty_policy="0x28b4F70ffE5ba7A26aEF979226f77Eb57fb9Fdb6"
        )
        
        return {
            'ip_id': ip_id,
            'license_id': license_response['licenseTermsId']
        }

    def test_attach_license_terms(self, story_client, setup_license_data):
        """Test attaching license terms to an IP"""
        response = story_client.License.attachLicenseTerms(
            ip_id=setup_license_data['ip_id'],
            license_terms_id=setup_license_data['license_id'],
            license_template="0x58E2c909D557Cd23EF90D14f8fd21667A5Ae7a93"
        )

        assert 'txHash' in response
        assert isinstance(response['txHash'], str)
        assert response['txHash'].startswith("0x")

    def test_mint_license_tokens(self, story_client, setup_license_data):
        """Test minting license tokens"""
        response = story_client.License.mintLicenseTokens(
            licensor_ip_id=setup_license_data['ip_id'],
            license_template="0x58E2c909D557Cd23EF90D14f8fd21667A5Ae7a93",
            license_terms_id=setup_license_data['license_id'],
            amount=1,
            receiver=account.address
        )

        assert 'txHash' in response
        assert isinstance(response['txHash'], str)
        assert response['txHash'].startswith("0x")
        assert 'licenseTokenIds' in response
        assert isinstance(response['licenseTokenIds'], list)
        assert all(isinstance(id, int) for id in response['licenseTokenIds'])

    def test_get_license_terms(self, story_client, setup_license_data):
        """Test getting license terms"""
        response = story_client.License.getLicenseTerms(setup_license_data['license_id'])
        
        assert response is not None
        assert 'transferable' in response
        assert 'commercialUse' in response
        assert 'derivativesAllowed' in response