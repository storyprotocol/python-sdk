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

from utils import get_story_client_in_devnet, MockERC20, MockERC721, get_token_id, approve, mint_tokens

load_dotenv()
private_key = os.getenv('WALLET_PRIVATE_KEY')
rpc_url = os.getenv('RPC_PROVIDER_URL')

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(rpc_url))
if not web3.is_connected():
    raise Exception("Failed to connect to Web3 provider")

# Set up the account with the private key
account = web3.eth.account.from_key(private_key)

royalty_policy="0xBe54FB168b3c982b7AaE60dB6CF75Bd8447b390E"
royalty_module="0xD2f60c40fEbccf6311f8B47c4f2Ec6b040400086"
license_template="0x2E896b0b2Fdb7457499B56AAaA4AE55BCB4Cd316"

@pytest.fixture(scope="module")
def story_client():
    return get_story_client_in_devnet(web3, account)

def test_registerPILTerms(story_client):
    response = story_client.License.registerPILTerms(
        transferable=False,
        royalty_policy=story_client.web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
        default_minting_fee=92,
        expiration=0,
        commercial_use=False,
        commercial_attribution=False,
        commercializer_checker=story_client.web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
        commercializer_checker_data="0x",
        commercial_rev_share=0,
        commercial_rev_ceiling=0,
        derivatives_allowed=False,
        derivatives_attribution=False,
        derivatives_approval=False,
        derivatives_reciprocal=False,
        derivative_rev_ceiling=0,
        currency=MockERC20,
        uri="",
    )

    assert response is not None
    assert 'licenseTermsId' in response
    assert response['licenseTermsId'] is not None
    assert isinstance(response['licenseTermsId'], int)

def test_registerNonComSocialRemixingPIL(story_client):
    response = story_client.License.registerNonComSocialRemixingPIL()

    assert response is not None
    assert 'licenseTermsId' in response
    assert response['licenseTermsId'] is not None
    assert isinstance(response['licenseTermsId'], int)
    
def test_registerCommercialUsePIL(story_client):
    response = story_client.License.registerCommercialUsePIL(
        default_minting_fee=11,
        currency=MockERC20,
        royalty_policy=royalty_policy
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'licenseTermsId' in response, "Response does not contain 'licenseTermsId'."
    assert response['licenseTermsId'] is not None, "'licenseTermsId' is None."
    assert isinstance(response['licenseTermsId'], int), "'licenseTermsId' is not an integer."

def test_registerCommercialRemixPIL(story_client):
    response = story_client.License.registerCommercialRemixPIL(
        default_minting_fee=1,
        currency=MockERC20,
        commercial_rev_share=100,
        royalty_policy=royalty_policy
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'licenseTermsId' in response, "Response does not contain 'licenseTermsId'."
    assert response['licenseTermsId'] is not None, "'licenseTermsId' is None."
    assert isinstance(response['licenseTermsId'], int), "'licenseTermsId' is not an integer."

@pytest.fixture(scope="module")
def ip_id(story_client):
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)

    response = story_client.IPAsset.register(
        nft_contract=MockERC721,
        token_id=token_id
    )

    token_ids = mint_tokens(
        erc20_contract_address=MockERC20, 
        web3=web3, 
        account=account, 
        to_address=account.address, 
        amount=100000 * 10 ** 6
    )
    
    receipt = approve(
        erc20_contract_address=MockERC20, 
        web3=web3, 
        account=account, 
        spender_address=royalty_module, 
        amount=100000 * 10 ** 6)

    assert response is not None
    assert 'ipId' in response
    assert response['ipId'] is not None

    return response['ipId']

def test_attachLicenseTerms(story_client, ip_id):
    license_terms_id = 5

    response = story_client.License.attachLicenseTerms(ip_id, license_template, license_terms_id)
    
    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'txHash' in response, "Response does not contain 'txHash'."
    assert response['txHash'] is not None, "'txHash' is None."
    assert isinstance(response['txHash'], str), "'txHash' is not a string."
    assert len(response['txHash']) > 0, "'txHash' is empty."

def test_mintLicenseTokens(story_client, ip_id):
    response = story_client.License.mintLicenseTokens(
        licensor_ip_id=ip_id, 
        license_template=license_template, 
        license_terms_id=5, 
        amount=1, 
        receiver=account.address
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'txHash' in response, "Response does not contain 'txHash'."
    assert response['txHash'] is not None, "'txHash' is None."
    assert isinstance(response['txHash'], str), "'txHash' is not a string."
    assert len(response['txHash']) > 0, "'txHash' is empty."
    assert 'licenseTokenIds' in response, "Response does not contain 'licenseTokenId'."
    assert response['licenseTokenIds'] is not None, "'licenseTokenId' is None."
    assert isinstance(response['licenseTokenIds'], list), "'licenseTokenIds' is not a list."
    assert all(isinstance(i, int) for i in response['licenseTokenIds']), "Not all elements in 'licenseTokenIds' are integers."

def test_getLicenseTerms(story_client):
    selectedLicenseTermsId = 3

    response = story_client.License.getLicenseTerms(selectedLicenseTermsId)

    assert response is not None, "Response is None, indicating the call failed."

def test_predictMintingLicenseFee(story_client, ip_id):
    response = story_client.License.predictMintingLicenseFee(
        licensor_ip_id=ip_id, 
        license_terms_id=5, 
        amount=1
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'currency' in response, "Response does not contain 'currency'."
    assert response['currency'] is not None, "'currency' is None."
    assert isinstance(response['currency'], str), "'currency' is not a string."
    assert len(response['currency']) > 0, "'currency' is empty."
    assert 'amount' in response, "Response does not contain 'amount'."
    assert response['amount'] is not None, "'amount' is None."
    assert isinstance(response['amount'], int), "'amount' is not an integer."

def test_setLicensingConfig(story_client, ip_id):
    licensing_config = {
        'mintingFee': 1,
        'isSet': True,
        'licensingHook': "0x0000000000000000000000000000000000000000",
        'hookData': "0xFcd3243590d29B131a26B1554B0b21a5B43e622e",
        'commercialRevShare': 0,
        'disabled': False,
        'expectMinimumGroupRewardShare': 1,
        'expectGroupRewardPool': "0x0000000000000000000000000000000000000000"
    }

    response = story_client.License.setLicensingConfig(
        ip_id=ip_id,
        license_terms_id=0,
        licensing_config=licensing_config,
        license_template=None  # Will default to zero address
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'txHash' in response, "Response does not contain 'txHash'"
    assert response['txHash'] is not None, "'txHash' is None"
    assert isinstance(response['txHash'], str), "'txHash' is not a string"
    assert len(response['txHash']) > 0, "'txHash' is empty"
    assert 'success' in response, "Response does not contain 'success'"
    assert response['success'] is True, "'success' is not True"
