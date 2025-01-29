import logging
import pytest
from unittest.mock import patch, MagicMock
from web3 import Web3
import os
import sys

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from src.story_protocol_python_sdk.resources.License import License

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()
private_key = os.getenv('WALLET_PRIVATE_KEY')
rpc_url = os.getenv('RPC_PROVIDER_URL')

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(rpc_url))

# Check if connected
if not web3.is_connected():
    raise Exception("Failed to connect to Web3 provider")

# Set up the account with the private key
account = web3.eth.account.from_key(private_key)

@pytest.fixture
def license_client():
    chain_id = 1315  # Devnet chain ID
    return License(web3, account, chain_id)

# Tests for registerPILTerms
def test_registerPILTerms_license_terms_id_registered(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=1, autospec=True), \
         patch.object(license_client.license_terms_util.royalty_module_client, 'isWhitelistedRoyaltyPolicy', return_value=True, autospec=True), \
         patch.object(license_client.license_terms_util.royalty_module_client, 'isWhitelistedRoyaltyToken', return_value=True, autospec=True):
        license_terms = {
            'defaultMintingFee': 1513,
            'currency': '0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c',
            'royaltyPolicy': '0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c',
            'transferable': False,
            'expiration': 0,
            'commercialUse': True,
            'commercialAttribution': False,
            'commercializerChecker': '0x0000000000000000000000000000000000000000',
            'commercializerCheckerData': '0x',
            'commercialRevShare': 0,
            'commercialRevCeiling': 0,
            'derivativesAllowed': False,
            'derivativesAttribution': False,
            'derivativesApproval': False,
            'derivativesReciprocal': False,
            'derivativeRevCeiling': 0,
            'uri': ''
        }
        
        response = license_client.registerPILTerms(
            transferable=license_terms['transferable'],
            royalty_policy=license_terms['royaltyPolicy'],
            default_minting_fee=license_terms['defaultMintingFee'],
            expiration=license_terms['expiration'],
            commercial_use=license_terms['commercialUse'],
            commercial_attribution=license_terms['commercialAttribution'],
            commercializer_checker=license_terms['commercializerChecker'],
            commercializer_checker_data=license_terms['commercializerCheckerData'],
            commercial_rev_share=license_terms['commercialRevShare'],
            commercial_rev_ceiling=license_terms['commercialRevCeiling'],
            derivatives_allowed=license_terms['derivativesAllowed'],
            derivatives_attribution=license_terms['derivativesAttribution'],
            derivatives_approval=license_terms['derivativesApproval'],
            derivatives_reciprocal=license_terms['derivativesReciprocal'],
            derivative_rev_ceiling=license_terms['derivativeRevCeiling'],
            currency=license_terms['currency'],
            uri=license_terms['uri']
        )
        
        assert response['licenseTermsId'] == 1
        assert 'txHash' not in response

def test_registerPILTerms_success(license_client):
    tx_hash = "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=0, autospec=True), \
         patch.object(license_client.license_terms_util.royalty_module_client, 'isWhitelistedRoyaltyPolicy', return_value=True, autospec=True), \
         patch.object(license_client.license_terms_util.royalty_module_client, 'isWhitelistedRoyaltyToken', return_value=True, autospec=True), \
         patch.object(license_client.license_template_client, 'build_registerLicenseTerms_transaction', return_value={'from': account.address, 'nonce': 1, 'gas': 2000000, 'gasPrice': web3.to_wei('100', 'gwei')}, autospec=True), \
         patch.object(account, 'sign_transaction', return_value=MagicMock(rawTransaction=b'signed_tx'), autospec=True), \
         patch.object(web3.eth, 'send_raw_transaction', return_value=bytes.fromhex(tx_hash[2:]), autospec=True), \
         patch.object(web3.eth, 'get_transaction_count', return_value=1, autospec=True), \
         patch.object(web3.eth, 'wait_for_transaction_receipt', return_value=MagicMock(), autospec=True):

        response = license_client.registerPILTerms(
            transferable=False,
            royalty_policy='0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c',
            default_minting_fee=1513,
            expiration=0,
            commercial_use=True,
            commercial_attribution=False,
            commercializer_checker='0x0000000000000000000000000000000000000000',
            commercializer_checker_data='0x',
            commercial_rev_share=90,
            commercial_rev_ceiling=0,
            derivatives_allowed=False,
            derivatives_attribution=False,
            derivatives_approval=False,
            derivatives_reciprocal=False,
            derivative_rev_ceiling=0,
            currency='0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c',
            uri=''
        )
        
        assert 'txHash' in response
        assert response['txHash'] == tx_hash[2:]
        assert isinstance(response['txHash'], str)

def test_registerPILTerms_commercial_rev_share_error_more_than_100(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=0, autospec=True), \
         patch.object(license_client.license_terms_util.royalty_module_client, 'isWhitelistedRoyaltyPolicy', return_value=True, autospec=True), \
         patch.object(license_client.license_terms_util.royalty_module_client, 'isWhitelistedRoyaltyToken', return_value=True, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.registerPILTerms(
                transferable=False,
                royalty_policy='0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c',
                default_minting_fee=1,
                expiration=0,
                commercial_use=True,
                commercial_attribution=False,
                commercializer_checker='0x0000000000000000000000000000000000000000',
                commercializer_checker_data='0x',
                commercial_rev_share=101,
                commercial_rev_ceiling=0,
                derivatives_allowed=False,
                derivatives_attribution=False,
                derivatives_approval=False,
                derivatives_reciprocal=False,
                derivative_rev_ceiling=0,
                currency='0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c',
                uri=''
            )
        assert str(excinfo.value) == 'CommercialRevShare should be between 0 and 100.'

def test_registerPILTerms_commercial_rev_share_error_less_than_0(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=0, autospec=True), \
         patch.object(license_client.license_terms_util.royalty_module_client, 'isWhitelistedRoyaltyPolicy', return_value=True, autospec=True), \
         patch.object(license_client.license_terms_util.royalty_module_client, 'isWhitelistedRoyaltyToken', return_value=True, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.registerPILTerms(
                transferable=False,
                royalty_policy='0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c',
                default_minting_fee=1,
                expiration=0,
                commercial_use=True,
                commercial_attribution=False,
                commercializer_checker='0x0000000000000000000000000000000000000000',
                commercializer_checker_data='0x',
                commercial_rev_share=-1,
                commercial_rev_ceiling=0,
                derivatives_allowed=False,
                derivatives_attribution=False,
                derivatives_approval=False,
                derivatives_reciprocal=False,
                derivative_rev_ceiling=0,
                currency='0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c',
                uri=''
            )
        assert str(excinfo.value) == 'CommercialRevShare should be between 0 and 100.'

# Tests for registerNonComSocialRemixingPIL
def test_registerNonComSocialRemixingPIL_license_terms_id_registered(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=1, autospec=True):
        response = license_client.registerNonComSocialRemixingPIL()
        assert response['licenseTermsId'] == 1
        assert 'txHash' not in response

def test_registerNonComSocialRemixingPIL_success(license_client):
    tx_hash = "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=0, autospec=True), \
         patch.object(license_client.license_template_client, 'build_registerLicenseTerms_transaction', return_value={'from': account.address, 'nonce': 1, 'gas': 2000000, 'gasPrice': web3.to_wei('100', 'gwei')}, autospec=True), \
         patch.object(account, 'sign_transaction', return_value=MagicMock(rawTransaction=b'signed_tx'), autospec=True), \
         patch.object(web3.eth, 'send_raw_transaction', return_value=bytes.fromhex(tx_hash[2:]), autospec=True), \
         patch.object(web3.eth, 'get_transaction_count', return_value=1, autospec=True), \
         patch.object(web3.eth, 'wait_for_transaction_receipt', return_value=MagicMock(), autospec=True):

        response = license_client.registerNonComSocialRemixingPIL()
        
        assert 'txHash' in response
        assert response['txHash'] == tx_hash[2:]
        assert isinstance(response['txHash'], str)

def test_registerNonComSocialRemixingPIL_error(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=0, autospec=True), \
         patch.object(license_client.license_terms_util.royalty_module_client, 'isWhitelistedRoyaltyPolicy', return_value=True, autospec=True), \
         patch.object(license_client.license_template_client, 'build_registerLicenseTerms_transaction', side_effect=Exception("request fail."), autospec=True):

        with pytest.raises(Exception) as excinfo:
            license_client.registerNonComSocialRemixingPIL()
        assert str(excinfo.value) == "request fail."

# Tests for registerCommercialUsePIL
def test_registerCommercialUsePIL_license_terms_id_registered(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=1, autospec=True):
        response = license_client.registerCommercialUsePIL(
            default_minting_fee=1,
            currency='0x0000000000000000000000000000000000000000'
        )
        assert response['licenseTermsId'] == 1
        assert 'txHash' not in response

def test_registerCommercialUsePIL_success(license_client):
    tx_hash = "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=0, autospec=True), \
         patch.object(license_client.license_terms_util.royalty_module_client, 'isWhitelistedRoyaltyPolicy', return_value=True, autospec=True), \
         patch.object(license_client.license_template_client, 'build_registerLicenseTerms_transaction', return_value={'from': account.address, 'nonce': 1, 'gas': 2000000, 'gasPrice': web3.to_wei('100', 'gwei')}, autospec=True), \
         patch.object(account, 'sign_transaction', return_value=MagicMock(rawTransaction=b'signed_tx'), autospec=True), \
         patch.object(web3.eth, 'send_raw_transaction', return_value=bytes.fromhex(tx_hash[2:]), autospec=True), \
         patch.object(web3.eth, 'get_transaction_count', return_value=1, autospec=True), \
         patch.object(web3.eth, 'wait_for_transaction_receipt', return_value=MagicMock(), autospec=True):

        response = license_client.registerCommercialUsePIL(
            default_minting_fee=1,
            currency='0x0000000000000000000000000000000000000000'
        )
        
        assert 'txHash' in response
        assert response['txHash'] == tx_hash[2:]
        assert isinstance(response['txHash'], str)

def test_registerCommercialUsePIL_error(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=0, autospec=True), \
         patch.object(license_client.license_terms_util.royalty_module_client, 'isWhitelistedRoyaltyPolicy', return_value=True, autospec=True), \
         patch.object(license_client.license_template_client, 'build_registerLicenseTerms_transaction', side_effect=Exception("request fail."), autospec=True):
        with pytest.raises(Exception) as excinfo:
            license_client.registerCommercialUsePIL(
                default_minting_fee=1,
                currency='0x0000000000000000000000000000000000000000'
            )
        assert str(excinfo.value) == "request fail."

# Tests for registerCommercialRemixPIL
def test_registerCommercialRemixPIL_license_terms_id_registered(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=1, autospec=True), \
         patch.object(license_client.license_terms_util.royalty_module_client, 'isWhitelistedRoyaltyPolicy', return_value=True, autospec=True):
        response = license_client.registerCommercialRemixPIL(
            default_minting_fee=1,
            commercial_rev_share=100,
            currency='0x0000000000000000000000000000000000000000',
            royalty_policy='0x0000000000000000000000000000000000000000'
        )
        assert response['licenseTermsId'] == 1
        assert 'txHash' not in response

def test_registerCommercialRemixPIL_success(license_client):
    tx_hash = "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=0, autospec=True), \
         patch.object(license_client.license_terms_util.royalty_module_client, 'isWhitelistedRoyaltyPolicy', return_value=True, autospec=True), \
         patch.object(license_client.license_template_client, 'build_registerLicenseTerms_transaction', return_value={'from': account.address, 'nonce': 1, 'gas': 2000000, 'gasPrice': web3.to_wei('100', 'gwei')}, autospec=True), \
         patch.object(account, 'sign_transaction', return_value=MagicMock(rawTransaction=b'signed_tx'), autospec=True), \
         patch.object(web3.eth, 'send_raw_transaction', return_value=bytes.fromhex(tx_hash[2:]), autospec=True), \
         patch.object(web3.eth, 'get_transaction_count', return_value=1, autospec=True), \
         patch.object(web3.eth, 'wait_for_transaction_receipt', return_value=MagicMock(), autospec=True):

        response = license_client.registerCommercialRemixPIL(
            default_minting_fee=1,
            commercial_rev_share=100,
            currency='0x0000000000000000000000000000000000000000',
            royalty_policy='0x0000000000000000000000000000000000000000'
        )
        
        assert 'txHash' in response
        assert response['txHash'] == tx_hash[2:]
        assert isinstance(response['txHash'], str)

def test_registerCommercialRemixPIL_error(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=0, autospec=True), \
         patch.object(license_client.license_terms_util.royalty_module_client, 'isWhitelistedRoyaltyPolicy', return_value=True, autospec=True), \
         patch.object(license_client.license_template_client, 'build_registerLicenseTerms_transaction', side_effect=Exception("request fail."), autospec=True):
        with pytest.raises(Exception) as excinfo:
            license_client.registerCommercialRemixPIL(
                default_minting_fee=1,
                commercial_rev_share=100,
                currency='0x0000000000000000000000000000000000000000',
                royalty_policy='0x0000000000000000000000000000000000000000'
            )
        assert str(excinfo.value) == "request fail."

# Tests for attachLicenseTerms
def test_attachLicenseTerms_ip_not_registered(license_client):
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=False, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.attachLicenseTerms(
                ip_id='0x0000000000000000000000000000000000000000',
                license_template='0x0000000000000000000000000000000000000000',
                license_terms_id=1
            )
        assert str(excinfo.value) == 'The IP with id 0x0000000000000000000000000000000000000000 is not registered.'

def test_attachLicenseTerms_license_terms_not_exist(license_client):
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True), \
         patch.object(license_client.license_registry_client, 'exists', return_value=False, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.attachLicenseTerms(
                ip_id='0x0000000000000000000000000000000000000000',
                license_template='0x0000000000000000000000000000000000000000',
                license_terms_id=1
            )
        assert str(excinfo.value) == 'License terms id 1 do not exist.'

def test_attachLicenseTerms_already_attached(license_client):
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True), \
         patch.object(license_client.license_registry_client, 'exists', return_value=True, autospec=True), \
         patch.object(license_client.license_registry_client, 'hasIpAttachedLicenseTerms', return_value=True, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.attachLicenseTerms(
                ip_id='0x0000000000000000000000000000000000000000',
                license_template='0x0000000000000000000000000000000000000000',
                license_terms_id=1
            )
        assert str(excinfo.value) == 'License terms id 1 is already attached to the IP with id 0x0000000000000000000000000000000000000000.'

def test_attachLicenseTerms_invalid_license_template(license_client):
    ip_id = '0x0000000000000000000000000000000000000000'
    invalid_license_template = 'invalid address'
    license_terms_id = 1

    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True), \
         patch.object(license_client.license_registry_client, 'exists', return_value=True, autospec=True), \
         patch.object(license_client.license_registry_client, 'hasIpAttachedLicenseTerms', return_value=False, autospec=True):
        
        with pytest.raises(ValueError) as excinfo:
            license_client.attachLicenseTerms(
                ip_id=ip_id,
                license_template=invalid_license_template,
                license_terms_id=license_terms_id
            )
        assert 'Address "invalid address" is invalid' in str(excinfo.value)

def test_attachLicenseTerms_success(license_client):
    tx_hash = "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True), \
         patch.object(license_client.license_registry_client, 'exists', return_value=True, autospec=True), \
         patch.object(license_client.license_registry_client, 'hasIpAttachedLicenseTerms', return_value=False, autospec=True), \
         patch.object(license_client.licensing_module_client, 'build_attachLicenseTerms_transaction', return_value={'from': account.address, 'nonce': 1, 'gas': 2000000, 'gasPrice': web3.to_wei('100', 'gwei')}, autospec=True), \
         patch.object(account, 'sign_transaction', return_value=MagicMock(rawTransaction=b'signed_tx'), autospec=True), \
         patch.object(web3.eth, 'send_raw_transaction', return_value=bytes.fromhex(tx_hash[2:]), autospec=True), \
         patch.object(web3.eth, 'get_transaction_count', return_value=1, autospec=True), \
         patch.object(web3.eth, 'wait_for_transaction_receipt', return_value=MagicMock(), autospec=True):

        response = license_client.attachLicenseTerms(
            ip_id='0x0000000000000000000000000000000000000000',
            license_template='0x0000000000000000000000000000000000000000',
            license_terms_id=1
        )
        
        assert 'txHash' in response
        assert response['txHash'] == tx_hash[2:]
        assert isinstance(response['txHash'], str)

# Tests for mintLicenseTokens
def test_mintLicenseTokens_invalid_license_template(license_client):
    licensor_ip_id = '0x0000000000000000000000000000000000000000'
    invalid_license_template = 'invalid address'
    receiver = '0x0000000000000000000000000000000000000000'
    license_terms_id = 1
    amount = 1

    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True), \
         patch.object(license_client.license_template_client, 'exists', return_value=True, autospec=True), \
         patch.object(license_client.license_registry_client, 'hasIpAttachedLicenseTerms', return_value=True, autospec=True):
        
        with pytest.raises(ValueError) as excinfo:
            license_client.mintLicenseTokens(
                licensor_ip_id=licensor_ip_id,
                license_template=invalid_license_template,
                license_terms_id=license_terms_id,
                amount=amount,
                receiver=receiver
            )
        assert 'Address "invalid address" is invalid' in str(excinfo.value)

def test_mintLicenseTokens_invalid_receiver(license_client):
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True), \
         patch.object(license_client.license_template_client, 'exists', return_value=True, autospec=True), \
         patch.object(license_client.license_registry_client, 'hasIpAttachedLicenseTerms', return_value=True, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.mintLicenseTokens(
                licensor_ip_id='0x0000000000000000000000000000000000000000',
                license_template='0x0000000000000000000000000000000000000000',
                license_terms_id=1,
                amount=1,
                receiver='invalid address'
            )
        assert 'Address "invalid address" is invalid' in str(excinfo.value)

def test_mintLicenseTokens_licensor_ip_not_registered(license_client):
    licensor_ip_id = '0x0000000000000000000000000000000000000000'
    license_template = '0x0000000000000000000000000000000000000000'
    receiver = '0x0000000000000000000000000000000000000000'
    license_terms_id = 1
    amount = 1

    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=False, autospec=True), \
         patch.object(license_client.license_template_client, 'exists', return_value=True, autospec=True), \
         patch.object(license_client.license_registry_client, 'hasIpAttachedLicenseTerms', return_value=True, autospec=True):
        
        with pytest.raises(ValueError) as excinfo:
            license_client.mintLicenseTokens(
                licensor_ip_id=licensor_ip_id,
                license_template=license_template,
                license_terms_id=license_terms_id,
                amount=amount,
                receiver=receiver
            )
        assert str(excinfo.value) == f"The licensor IP with id {licensor_ip_id} is not registered."

def test_mintLicenseTokens_license_terms_not_exist(license_client):
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True), \
         patch.object(license_client.license_template_client, 'exists', return_value=False, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.mintLicenseTokens(
                licensor_ip_id='0x0000000000000000000000000000000000000000',
                license_template='0x0000000000000000000000000000000000000000',
                license_terms_id=1,
                amount=1,
                receiver='0x0000000000000000000000000000000000000000'
            )
        assert str(excinfo.value) == 'License terms id 1 do not exist.'

def test_mintLicenseTokens_not_attached(license_client):
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True), \
         patch.object(license_client.license_template_client, 'exists', return_value=True, autospec=True), \
         patch.object(license_client.license_registry_client, 'hasIpAttachedLicenseTerms', return_value=False, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.mintLicenseTokens(
                licensor_ip_id='0x0000000000000000000000000000000000000000',
                license_template='0x0000000000000000000000000000000000000000',
                license_terms_id=1,
                amount=1,
                receiver='0x0000000000000000000000000000000000000000'
            )
        assert str(excinfo.value) == 'License terms id 1 is not attached to the IP with id 0x0000000000000000000000000000000000000000.'

def test_mintLicenseTokens_success(license_client):
    tx_hash = "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True), \
         patch.object(license_client.license_template_client, 'exists', return_value=True, autospec=True), \
         patch.object(license_client.license_registry_client, 'hasIpAttachedLicenseTerms', return_value=True, autospec=True), \
         patch.object(license_client.licensing_module_client, 'build_mintLicenseTokens_transaction', return_value={
             'from': account.address, 'nonce': 1, 'gas': 2000000, 'gasPrice': web3.to_wei('100', 'gwei')
         }, autospec=True), \
         patch.object(account, 'sign_transaction', return_value=MagicMock(rawTransaction=b'signed_tx'), autospec=True), \
         patch.object(web3.eth, 'send_raw_transaction', return_value=bytes.fromhex(tx_hash[2:]), autospec=True), \
         patch.object(web3.eth, 'get_transaction_count', return_value=1, autospec=True), \
         patch.object(web3.eth, 'wait_for_transaction_receipt', return_value=MagicMock(), autospec=True):

        response = license_client.mintLicenseTokens(
            licensor_ip_id='0x0000000000000000000000000000000000000000',
            license_template='0x0000000000000000000000000000000000000000',
            license_terms_id=1,
            amount=1,
            receiver='0x0000000000000000000000000000000000000000'
        )
        
        assert 'txHash' in response
        assert response['txHash'] == tx_hash[2:]
        assert isinstance(response['txHash'], str)

def test_mintLicenseTokens_invalid_license_template(license_client):
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.mintLicenseTokens(
                licensor_ip_id=ZERO_ADDRESS,
                license_terms_id=1,
                license_template="invalid_address",
                amount=1,
                receiver=ZERO_ADDRESS,
                max_minting_fee=1,
                max_revenue_share=1
            )
        assert 'Address "invalid_address" is invalid' in str(excinfo.value)

def test_mintLicenseTokens_invalid_receiver(license_client):
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.mintLicenseTokens(
                licensor_ip_id=ZERO_ADDRESS,
                license_terms_id=1,
                license_template=ZERO_ADDRESS,  # Added missing parameter
                amount=1,
                receiver="invalid_address",
                max_minting_fee=1,
                max_revenue_share=1
            )
        assert 'Address "invalid_address" is invalid' in str(excinfo.value)

def test_mintLicenseTokens_avmount_five(license_client):
    tx_hash = "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True), \
         patch.object(license_client.license_template_client, 'exists', return_value=True, autospec=True), \
         patch.object(license_client.license_registry_client, 'hasIpAttachedLicenseTerms', return_value=True, autospec=True), \
         patch.object(license_client.licensing_module_client, 'build_mintLicenseTokens_transaction', return_value={'from': account.address, 'nonce': 1}, autospec=True), \
         patch.object(account, 'sign_transaction', return_value=MagicMock(rawTransaction=b'signed_tx'), autospec=True), \
         patch.object(web3.eth, 'send_raw_transaction', return_value=bytes.fromhex(tx_hash[2:]), autospec=True), \
         patch.object(web3.eth, 'wait_for_transaction_receipt', return_value=MagicMock(), autospec=True):
        
        response = license_client.mintLicenseTokens(
            licensor_ip_id=ZERO_ADDRESS,
            license_terms_id=1,
            license_template=ZERO_ADDRESS,  # Added missing parameter
            amount=5,
            receiver=ZERO_ADDRESS,
            max_minting_fee=1,
            max_revenue_share=1
        )
        
        assert response['txHash'] == tx_hash[2:]
        assert isinstance(response['txHash'], str)

# Tests for getLicenseTerms
def test_getLicenseTerms_success(license_client):
    mock_response = {
        'terms': {
            'transferable': True,
            'royaltyPolicy': ZERO_ADDRESS,
            'defaultMintingFee': 1,
            'expiration': 1,
            'commercialUse': True,
            'commercialAttribution': True,
            'commercializerChecker': ZERO_ADDRESS,
            'commercializerCheckerData': ZERO_ADDRESS,
            'commercialRevShare': 100,
            'commercialRevCeiling': 1,
            'derivativesAllowed': True,
            'derivativesAttribution': True,
            'derivativesApproval': True,
            'derivativesReciprocal': True,
            'derivativeRevCeiling': 1,
            'currency': ZERO_ADDRESS,
            'uri': "string"
        }
    }
    with patch.object(license_client.license_template_client, 'getLicenseTerms', return_value=mock_response, autospec=True):
        response = license_client.getLicenseTerms(1)
        assert response == mock_response

def test_getLicenseTerms_not_exist(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTerms', 
                     side_effect=Exception("Given licenseTermsId is not exist."), 
                     autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.getLicenseTerms(1)
        assert str(excinfo.value) == "Failed to get license terms: Given licenseTermsId is not exist."

# Tests for setLicensingConfig
def test_setLicensingConfig_missing_params(license_client):
    incomplete_config = {
        'isSet': True,
        'mintingFee': 0,
        # missing required params
    }
    with pytest.raises(ValueError) as excinfo:
        license_client.setLicensingConfig(
            ip_id=ZERO_ADDRESS,
            license_terms_id=1,
            licensing_config=incomplete_config
        )
    assert "Missing required licensing_config parameters:" in str(excinfo.value)

def test_setLicensingConfig_negative_minting_fee(license_client):
    config = {
        'isSet': True,
        'mintingFee': -1,
        'hookData': "0x",
        'licensingHook': ZERO_ADDRESS,
        'commercialRevShare': 0,
        'disabled': False,
        'expectMinimumGroupRewardShare': 0,
        'expectGroupRewardPool': ZERO_ADDRESS
    }
    with pytest.raises(ValueError) as excinfo:
        license_client.setLicensingConfig(
            ip_id=ZERO_ADDRESS,
            license_terms_id=1,
            licensing_config=config
        )
    assert str(excinfo.value) == "Failed to set licensing config: The minting fee must be greater than 0."

def test_setLicensingConfig_ip_not_registered(license_client):
    config = {
        'isSet': True,
        'mintingFee': 1,
        'hookData': "0x",
        'licensingHook': ZERO_ADDRESS,
        'commercialRevShare': 0,
        'disabled': False,
        'expectMinimumGroupRewardShare': 0,
        'expectGroupRewardPool': ZERO_ADDRESS
    }
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=False, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.setLicensingConfig(
                ip_id=ZERO_ADDRESS,
                license_terms_id=1,
                licensing_config=config
            )
        assert str(excinfo.value) == f"Failed to set licensing config: The licensor IP with id {ZERO_ADDRESS} is not registered."

def test_setLicensingConfig_unregistered_licensing_hook(license_client):
    config = {
        'isSet': True,
        'mintingFee': 1,
        'hookData': "0x",
        'licensingHook': "0x1234567890123456789012345678901234567890",
        'commercialRevShare': 0,
        'disabled': False,
        'expectMinimumGroupRewardShare': 0,
        'expectGroupRewardPool': ZERO_ADDRESS
    }
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True), \
         patch.object(license_client.module_registry_client, 'isRegistered', return_value=False, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.setLicensingConfig(
                ip_id=ZERO_ADDRESS,
                license_terms_id=1,
                licensing_config=config
            )
        assert str(excinfo.value) == "Failed to set licensing config: The licensing hook is not registered."

def test_setLicensingConfig_template_terms_mismatch(license_client):
    config = {
        'isSet': True,
        'mintingFee': 1,
        'hookData': "0x",
        'licensingHook': ZERO_ADDRESS,
        'commercialRevShare': 0,
        'disabled': False,
        'expectMinimumGroupRewardShare': 0,
        'expectGroupRewardPool': ZERO_ADDRESS
    }
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.setLicensingConfig(
                ip_id=ZERO_ADDRESS,
                license_terms_id=1,
                license_template=ZERO_ADDRESS,
                licensing_config=config
            )
        assert str(excinfo.value) == "Failed to set licensing config: The license template is zero address but license terms id is not zero."

def test_setLicensingConfig_zero_address_with_rev_share(license_client):
    config = {
        'isSet': True,
        'mintingFee': 1,
        'hookData': "0x",
        'licensingHook': ZERO_ADDRESS,
        'commercialRevShare': 10,  # Non-zero value
        'disabled': False,
        'expectMinimumGroupRewardShare': 0,
        'expectGroupRewardPool': ZERO_ADDRESS
    }
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.setLicensingConfig(
                ip_id=ZERO_ADDRESS,
                license_terms_id=0,
                license_template=ZERO_ADDRESS,
                licensing_config=config
            )
        assert str(excinfo.value) == "Failed to set licensing config: The license template cannot be zero address if commercial revenue share is not zero."
