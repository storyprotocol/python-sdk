# tests/integration/test_integration_license.py

import os
import sys
import pytest
from dotenv import load_dotenv
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
    ROYALTY_MODULE,
    PIL_LICENSE_TEMPLATE
)

def test_registerPILTerms(story_client):
    response = story_client.License.registerPILTerms(
        transferable=False,
        royalty_policy=story_client.web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
        default_minting_fee=0,
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

@pytest.fixture(scope="module")
def registerCommercialUsePIL(story_client):
    response = story_client.License.registerCommercialUsePIL(
        default_minting_fee=11,
        currency=MockERC20,
        royalty_policy=ROYALTY_POLICY
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'licenseTermsId' in response, "Response does not contain 'licenseTermsId'."
    assert response['licenseTermsId'] is not None, "'licenseTermsId' is None."
    assert isinstance(response['licenseTermsId'], int), "'licenseTermsId' is not an integer."

    return response['licenseTermsId']
    
def test_registerCommercialUsePIL(story_client, registerCommercialUsePIL):
    assert registerCommercialUsePIL is not None

@pytest.fixture(scope="module")
def registerCommercialRemixPIL(story_client):
    response = story_client.License.registerCommercialRemixPIL(
        default_minting_fee=1,
        currency=MockERC20,
        commercial_rev_share=100,
        royalty_policy=ROYALTY_POLICY
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'licenseTermsId' in response, "Response does not contain 'licenseTermsId'."
    assert response['licenseTermsId'] is not None, "'licenseTermsId' is None."
    assert isinstance(response['licenseTermsId'], int), "'licenseTermsId' is not an integer."

    return response['licenseTermsId']

def test_registerCommercialRemixPIL(story_client, registerCommercialRemixPIL):
    assert registerCommercialRemixPIL is not None

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
        spender_address=ROYALTY_MODULE, 
        amount=100000 * 10 ** 6)

    assert response is not None
    assert 'ipId' in response
    assert response['ipId'] is not None

    return response['ipId']

def test_attachLicenseTerms(story_client, ip_id, registerCommercialUsePIL):
    license_terms_id = registerCommercialUsePIL

    response = story_client.License.attachLicenseTerms(ip_id, PIL_LICENSE_TEMPLATE, license_terms_id)
    
    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'txHash' in response, "Response does not contain 'txHash'."
    assert response['txHash'] is not None, "'txHash' is None."
    assert isinstance(response['txHash'], str), "'txHash' is not a string."
    assert len(response['txHash']) > 0, "'txHash' is empty."

def test_mintLicenseTokens(story_client, ip_id, registerCommercialUsePIL):
    response = story_client.License.mintLicenseTokens(
        licensor_ip_id=ip_id, 
        license_template=PIL_LICENSE_TEMPLATE, 
        license_terms_id=registerCommercialUsePIL, 
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

def test_predictMintingLicenseFee(story_client, ip_id, registerCommercialUsePIL):
    response = story_client.License.predictMintingLicenseFee(
        licensor_ip_id=ip_id, 
        license_terms_id=registerCommercialUsePIL, 
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

def test_setLicensingConfig(story_client, ip_id, registerCommercialRemixPIL):
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
        license_terms_id=registerCommercialRemixPIL,
        licensing_config=licensing_config,
        license_template=PIL_LICENSE_TEMPLATE
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'txHash' in response, "Response does not contain 'txHash'"
    assert response['txHash'] is not None, "'txHash' is None"
    assert isinstance(response['txHash'], str), "'txHash' is not a string"
    assert len(response['txHash']) > 0, "'txHash' is empty"
    assert 'success' in response, "Response does not contain 'success'"
    assert response['success'] is True, "'success' is not True"

def test_register_pil_terms_with_no_minting_fee(story_client):
    """Test registering PIL terms with no minting fee."""
    response = story_client.License.registerPILTerms(
        transferable=False,
        royalty_policy=story_client.web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
        default_minting_fee=0,  # Minimal minting fee
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
        uri=""
    )

    assert response is not None
    assert 'licenseTermsId' in response
    assert response['licenseTermsId'] is not None
    assert isinstance(response['licenseTermsId'], int)

def test_register_commercial_use_pil_without_royalty_policy(story_client):
    """Test registering commercial use PIL without specifying royalty policy."""
    response = story_client.License.registerCommercialUsePIL(
        default_minting_fee=1,
        currency=MockERC20
    )

    assert response is not None
    assert 'licenseTermsId' in response
    assert response['licenseTermsId'] is not None
    assert isinstance(response['licenseTermsId'], int)

@pytest.fixture(scope="module")
def setup_license_terms(story_client, ip_id):
    """Fixture to set up license terms for testing."""
    response = story_client.License.registerCommercialRemixPIL(
        default_minting_fee=1,
        currency=MockERC20,
        commercial_rev_share=100,
        royalty_policy=ROYALTY_POLICY
    )
    license_id = response['licenseTermsId']

    # Attach the license terms
    story_client.License.attachLicenseTerms(
        ip_id=ip_id,
        license_template=PIL_LICENSE_TEMPLATE,
        license_terms_id=license_id
    )

    return license_id

def test_multi_token_minting(story_client, ip_id, setup_license_terms):
    """Test minting multiple license tokens at once."""
    response = story_client.License.mintLicenseTokens(
        licensor_ip_id=ip_id,
        license_template=PIL_LICENSE_TEMPLATE,
        license_terms_id=setup_license_terms,
        amount=3,  # Mint multiple tokens
        receiver=account.address
    )

    assert response is not None
    assert 'txHash' in response
    assert response['txHash'] is not None
    assert isinstance(response['txHash'], str)
    assert len(response['txHash']) > 0
    assert 'licenseTokenIds' in response
    assert isinstance(response['licenseTokenIds'], list)
    assert len(response['licenseTokenIds']) > 0

def test_set_licensing_config_with_hooks(story_client, ip_id, registerCommercialRemixPIL):
    """Test setting licensing configuration with hooks enabled."""
    licensing_config = {
        'mintingFee': 100,
        'isSet': True,
        'licensingHook': "0x0000000000000000000000000000000000000000",
        'hookData': "0x1234567890",  # Different hook data
        'commercialRevShare': 100,  # 50% revenue share
        'disabled': False,
        'expectMinimumGroupRewardShare': 10,  # 10% minimum group reward
        'expectGroupRewardPool': "0x0000000000000000000000000000000000000000"
    }

    response = story_client.License.setLicensingConfig(
        ip_id=ip_id,
        license_terms_id=registerCommercialRemixPIL,
        licensing_config=licensing_config,
        license_template=PIL_LICENSE_TEMPLATE
    )

    assert response is not None
    assert 'txHash' in response
    assert response['txHash'] is not None
    assert isinstance(response['txHash'], str)
    assert len(response['txHash']) > 0
    assert 'success' in response
    assert response['success'] is True

def test_predict_minting_fee_with_multiple_tokens(story_client, ip_id, setup_license_terms):
    """Test predicting minting fee for multiple tokens."""
    response = story_client.License.predictMintingLicenseFee(
        licensor_ip_id=ip_id,
        license_terms_id=setup_license_terms,
        amount=5  # Predict for 5 tokens
    )

    assert response is not None
    assert 'currency' in response
    assert response['currency'] is not None
    assert isinstance(response['currency'], str)
    assert len(response['currency']) > 0
    assert 'amount' in response
    assert response['amount'] is not None
    assert isinstance(response['amount'], int)
    assert response['amount'] > 0  # Amount should be positive for multiple tokens
