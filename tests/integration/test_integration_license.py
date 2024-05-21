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

from utils import get_story_client_in_sepolia, MockERC20

load_dotenv()
private_key = os.getenv('WALLET_PRIVATE_KEY')
rpc_url = os.getenv('RPC_PROVIDER_URL')

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(rpc_url))
if not web3.is_connected():
    raise Exception("Failed to connect to Web3 provider")

# Set up the account with the private key
account = web3.eth.account.from_key(private_key)

@pytest.fixture
def story_client():
    return get_story_client_in_sepolia(web3, account)

def test_registerNonComSocialRemixingPIL(story_client):
    response = story_client.License.registerNonComSocialRemixingPIL()

    assert response is not None
    assert 'licenseTermsId' in response
    assert response['licenseTermsId'] is not None
    assert isinstance(response['licenseTermsId'], int)
    print(response['licenseTermsId'])
    
def test_registerCommercialUsePIL(story_client):
    response = story_client.License.registerCommercialUsePIL(
        minting_fee=1,
        currency=MockERC20,
        royalty_policy="0xAAbaf349C7a2A84564F9CC4Ac130B3f19A718E86"
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'licenseTermsId' in response, "Response does not contain 'licenseTermsId'."
    assert response['licenseTermsId'] is not None, "'licenseTermsId' is None."
    assert isinstance(response['licenseTermsId'], int), "'licenseTermsId' is not an integer."

def test_registerCommercialRemixPIL(story_client):
    response = story_client.License.registerCommercialRemixPIL(
        minting_fee=1,
        currency=MockERC20,
        commercial_rev_share=10,
        royalty_policy="0xAAbaf349C7a2A84564F9CC4Ac130B3f19A718E86"
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'licenseTermsId' in response, "Response does not contain 'licenseTermsId'."
    assert response['licenseTermsId'] is not None, "'licenseTermsId' is None."
    # print("ye", response['licenseTermsId'])
    assert isinstance(response['licenseTermsId'], int), "'licenseTermsId' is not an integer."

def test_attachLicenseTerms(story_client):
    ip_id = "0x431A7Cc86381F9bA437b575D3F9E931652fFbbdd"
    license_template = "0x260B6CB6284c89dbE660c0004233f7bB99B5edE7"
    license_terms_id = 3 

    response = story_client.License.attachLicenseTerms(ip_id, license_template, license_terms_id)
    
    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'txHash' in response, "Response does not contain 'txHash'."
    assert response['txHash'] is not None, "'txHash' is None."
    assert isinstance(response['txHash'], str), "'txHash' is not a string."
    assert len(response['txHash']) > 0, "'txHash' is empty."

def test_mintLicenseTokens(story_client):
    licensor_ip_id = "0x431A7Cc86381F9bA437b575D3F9E931652fFbbdd"  # Replace with actual Licensor IP ID
    license_template = "0x260B6CB6284c89dbE660c0004233f7bB99B5edE7"  # Replace with actual License Template address
    license_terms_id = 2  # Replace with actual License Terms ID
    amount = 2  # Replace with the amount of license tokens to mint
    receiver = "0x14dC79964da2C08b23698B3D3cc7Ca32193d9955"  # Replace with the address of the receiver

    response = story_client.License.mintLicenseTokens(licensor_ip_id, license_template, license_terms_id, amount, receiver)
    
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
    selectedLicenseTermsId = 2  # Use license terms ID 2 for the test

    response = story_client.License.getLicenseTerms(selectedLicenseTermsId)
    # print(response)

    assert response is not None, "Response is None, indicating the call failed."
