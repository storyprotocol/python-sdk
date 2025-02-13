import os
import sys
import pytest
from web3 import Web3
from dotenv import load_dotenv

current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from utils import (
    get_token_id,
    mint_by_spg,
    get_story_client_in_devnet,
    MockERC721,
    MockERC20,
    getBlockTimestamp,
    ZERO_ADDRESS,
    ROYALTY_POLICY
)

load_dotenv(override=True)
private_key = os.getenv('WALLET_PRIVATE_KEY')
rpc_url = os.getenv('RPC_PROVIDER_URL')

web3 = Web3(Web3.HTTPProvider(rpc_url))
if not web3.is_connected():
    raise Exception("Failed to connect to Web3 provider")

account = web3.eth.account.from_key(private_key)

@pytest.fixture(scope="module")
def story_client():
    return get_story_client_in_devnet(web3, account)

@pytest.fixture(scope="module")
def non_commercial_license_terms_id(story_client):
    response = story_client.License.registerNonComSocialRemixingPIL()
    return response['licenseTermsId']

@pytest.fixture(scope="module")
def parent_ip_id(story_client):
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
    response = story_client.IPAsset.register(
        nft_contract=MockERC721,
        token_id=token_id
    )
    return response['ipId']

@pytest.fixture(scope="module")
def nft_collection(story_client):
    tx_data = story_client.NFTClient.createNFTCollection(
        name="test-collection",
        symbol="TEST",
        max_supply=100,
        is_public_minting=True,
        mint_open=True,
        contract_uri="test-uri",
        mint_fee_recipient=account.address,
    )
    return tx_data['nftContract']

class TestBasicIPAssetOperations:
    """Basic IP asset registration and validation tests"""
    
    def test_register_ip_asset(self, story_client):
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )
        assert 'ipId' in response
        assert isinstance(response['ipId'], str)
        assert len(response['ipId']) > 0

    def test_is_registered(self, story_client, parent_ip_id):
        is_registered = story_client.IPAsset._is_registered(parent_ip_id)
        assert is_registered is True

        unregistered_ip_id = "0x1234567890123456789012345678901234567890"
        is_registered = story_client.IPAsset._is_registered(unregistered_ip_id)
        assert is_registered is False

class TestSPGOperations:
    """Tests for Story Protocol Generated (SPG) NFT operations"""
    
    @pytest.fixture(scope="class")
    def setup(self, story_client, nft_collection):
        result = story_client.IPAsset.mintAndRegisterIpAssetWithPilTerms(
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
        )
        return {
            'parent_ip_id': result['ipId'],
            'license_terms_id': result['licenseTermsIds'][0],
            'nft_contract': nft_collection
        }

    def test_register_ip_with_metadata(self, story_client, setup):
        token_id = mint_by_spg(setup['nft_contract'], story_client.web3, story_client.account, "test-metadata")
        response = story_client.IPAsset.register(
            nft_contract=setup['nft_contract'],
            token_id=token_id,
            ip_metadata={
                'ipMetadataURI': "test-uri",
                'ipMetadataHash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
                'nftMetadataHash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
            },
            deadline=1000
        )
        assert 'txHash' in response
        assert isinstance(response['txHash'], str)
        assert 'ipId' in response
        assert isinstance(response['ipId'], str)

    @pytest.mark.skip(reason="registerDerivativeIp not implemented yet")
    def test_register_derivative_ip(self, story_client, setup):
        token_id = mint_by_spg(setup['nft_contract'], story_client.web3, story_client.account)
        
        response = story_client.IPAsset.registerDerivativeIp(
            nft_contract=setup['nft_contract'],
            token_id=token_id,
            deriv_data={
                'parentIpIds': [setup['parent_ip_id']],
                'licenseTermsIds': [setup['license_terms_id']]
            },
            metadata={
                'metadataURI': "test-uri",
                'metadataHash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
            },
            deadline=1000
        )

        assert 'txHash' in response
        assert isinstance(response['txHash'], str)
        assert 'ipId' in response
        assert isinstance(response['ipId'], str)

    @pytest.mark.skip(reason="registerIpAndAttachPilTerms not implemented yet")
    def test_register_ip_and_attach_pil_terms(self, story_client, setup):
        token_id = mint_by_spg(setup['nft_contract'], story_client.web3, story_client.account)
        
        result = story_client.IPAsset.registerIpAndAttachPilTerms(
            nft_contract=setup['nft_contract'],
            token_id=token_id,
            pil_type='non_commercial_remix',
            metadata={
                'metadataURI': "test-uri",
                'metadataHash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
                'nftMetadataHash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
            },
            deadline=1000,
            commercial_rev_share=10,
            currency=MockERC20
        )

        assert 'txHash' in result
        assert isinstance(result['txHash'], str)
        assert 'ipId' in result
        assert isinstance(result['ipId'], str)
        assert 'licenseTermsIds' in result
        assert isinstance(result['licenseTermsIds'], list)

@pytest.mark.skip(reason="Royalty operations not implemented yet")
class TestRoyaltyOperations:
    """Tests for royalty-related operations"""

    def test_register_ip_with_royalty_distribution(self, story_client, nft_collection):
        token_id = get_token_id(nft_collection, story_client.web3, story_client.account)
        
        response = story_client.IPAsset.registerIPAndAttachLicenseTermsAndDistributeRoyaltyTokens(
            nft_contract=nft_collection,
            token_id=token_id,
            terms=[{
                'terms': self._get_royalty_terms(),
                'licensing_config': self._get_royalty_licensing_config()
            }],
            ip_metadata=self._get_test_metadata(),
            royalty_shares=[{
                'author': story_client.account.address,
                'percentage': 1
            }]
        )

        self._assert_royalty_response(response)

    def test_mint_register_and_distribute_royalty(self, story_client, nft_collection):
        response = story_client.IPAsset.mintAndRegisterIpAndAttachPilTermsAndDistributeRoyaltyTokens(
            spg_nft_contract=nft_collection,
            terms=[{
                'terms': self._get_royalty_terms(),
                'licensing_config': self._get_royalty_licensing_config()
            }],
            ip_metadata=self._get_test_metadata(),
            royalty_shares=[{
                'author': story_client.account.address,
                'percentage': 10
            }]
        )

        assert 'txHash' in response
        assert isinstance(response['txHash'], str)
        assert 'ipId' in response
        assert isinstance(response['ipId'], str)
        assert 'licenseTermsIds' in response
        assert isinstance(response['licenseTermsIds'], list)
        assert 'tokenId' in response
        assert isinstance(response['tokenId'], int)

    @staticmethod
    def _get_royalty_terms():
        return {
            'transferable': True,
            'royalty_policy': ROYALTY_POLICY,
            'default_minting_fee': 10000,
            'expiration': 1000,
            'commercial_use': True,
            'commercial_attribution': False,
            'commercializer_checker': ZERO_ADDRESS,
            'commercializer_checker_data': ZERO_ADDRESS,
            'commercial_rev_share': 0,
            'commercial_rev_ceiling': 0,
            'derivatives_allowed': True,
            'derivatives_attribution': True,
            'derivatives_approval': False,
            'derivatives_reciprocal': True,
            'derivative_rev_ceiling': 0,
            'currency': MockERC20,
            'uri': "test case"
        }

    @staticmethod
    def _get_royalty_licensing_config():
        return {
            'is_set': True,
            'minting_fee': 10000,
            'hook_data': "",
            'licensing_hook': ZERO_ADDRESS,
            'commercial_rev_share': 0,
            'disabled': False,
            'expect_minimum_group_reward_share': 0,
            'expect_group_reward_pool': ZERO_ADDRESS
        }

    @staticmethod
    def _get_test_metadata():
        return {
            'ip_metadata_uri': "test-uri",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash")),
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash"))
        }

    @staticmethod
    def _assert_royalty_response(response):
        assert 'registerIpAndAttachPilTermsAndDeployRoyaltyVaultTxHash' in response
        assert isinstance(response['registerIpAndAttachPilTermsAndDeployRoyaltyVaultTxHash'], str)
        assert 'distributeRoyaltyTokensTxHash' in response
        assert isinstance(response['distributeRoyaltyTokensTxHash'], str)
        assert 'ipId' in response
        assert isinstance(response['ipId'], str)
        assert 'licenseTermsIds' in response
        assert isinstance(response['licenseTermsIds'], list)