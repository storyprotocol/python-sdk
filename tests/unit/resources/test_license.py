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

from src.resources.License import License

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
    chain_id = 11155111  # Sepolia chain ID
    return License(web3, account, chain_id)

def test_registerNonComSocialRemixingPIL_license_terms_id_registered(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=1, autospec=True), \
         patch.object(license_client.license_template_client, 'build_registerLicenseTerms_transaction', return_value=None, autospec=True), \
         patch.object(account, 'sign_transaction', return_value=MagicMock(rawTransaction=b'signed_tx'), autospec=True), \
         patch.object(web3.eth, 'send_raw_transaction', return_value=b'\x12\x9f\x7d\xd8\x02\x20\x0f\x09\x62\x21\xdd\x89\xd5\xb0\x86\xe4\xbd\x3a\xd6\xea\xfb\x37\x8a\x0c\x75\xe3\xb0\x4f\xc3\x75\xf9\x97', autospec=True), \
         patch.object(web3.eth, 'get_transaction_count', return_value=1, autospec=True):

        response = license_client.registerNonComSocialRemixingPIL()
        
        assert response['licenseTermsId'] == 1
        assert 'txHash' not in response

def test_registerNonComSocialRemixingPIL_error(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=0, autospec=True), \
         patch.object(license_client.license_template_client, 'build_registerLicenseTerms_transaction', side_effect=Exception("request fail."), autospec=True):

        with pytest.raises(Exception) as excinfo:
            license_client.registerNonComSocialRemixingPIL()
        
        assert 'request fail.' in str(excinfo.value)

def test_registerNonComSocialRemixingPIL_license_terms_id_not_registered(license_client):
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

def test_registerCommercialUsePIL_license_terms_id_registered(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=1, autospec=True), \
         patch.object(license_client.license_template_client, 'build_registerLicenseTerms_transaction', return_value=None, autospec=True), \
         patch.object(account, 'sign_transaction', return_value=MagicMock(rawTransaction=b'signed_tx'), autospec=True), \
         patch.object(web3.eth, 'send_raw_transaction', return_value=b'\x12\x9f\x7d\xd8\x02\x20\x0f\x09\x62\x21\xdd\x89\xd5\xb0\x86\xe4\xbd\x3a\xd6\xea\xfb\x37\x8a\x0c\x75\xe3\xb0\x4f\xc3\x75\xf9\x97', autospec=True), \
         patch.object(web3.eth, 'get_transaction_count', return_value=1, autospec=True):

        response = license_client.registerCommercialUsePIL(
            minting_fee=1,
            currency='0x0000000000000000000000000000000000000000',
            royalty_policy='0x0000000000000000000000000000000000000000'
        )
        
        assert response['licenseTermsId'] == 1
        assert 'txHash' not in response

def test_registerCommercialUsePIL_error(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=0, autospec=True), \
         patch.object(license_client.license_template_client, 'build_registerLicenseTerms_transaction', side_effect=Exception("request fail."), autospec=True):

        with pytest.raises(Exception) as excinfo:
            license_client.registerCommercialUsePIL(
                minting_fee=1,
                currency='0x0000000000000000000000000000000000000000',
                royalty_policy='0x0000000000000000000000000000000000000000'
            )

        assert 'request fail.' in str(excinfo.value)

def test_registerCommercialUsePIL_license_terms_id_not_registered(license_client):
    tx_hash = "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=0, autospec=True), \
         patch.object(license_client.license_template_client, 'build_registerLicenseTerms_transaction', return_value={'from': account.address, 'nonce': 1, 'gas': 2000000, 'gasPrice': web3.to_wei('100', 'gwei')}, autospec=True), \
         patch.object(account, 'sign_transaction', return_value=MagicMock(rawTransaction=b'signed_tx'), autospec=True), \
         patch.object(web3.eth, 'send_raw_transaction', return_value=bytes.fromhex(tx_hash[2:]), autospec=True), \
         patch.object(web3.eth, 'get_transaction_count', return_value=1, autospec=True), \
         patch.object(web3.eth, 'wait_for_transaction_receipt', return_value=MagicMock(), autospec=True):

        response = license_client.registerCommercialUsePIL(
            minting_fee=1,
            currency='0x0000000000000000000000000000000000000000',
            royalty_policy='0x0000000000000000000000000000000000000000'
        )
        
        assert 'txHash' in response
        assert response['txHash'] == tx_hash[2:]
        assert isinstance(response['txHash'], str)

def test_registerCommercialRemixPIL_license_terms_id_registered(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=1, autospec=True), \
         patch.object(license_client.license_template_client, 'build_registerLicenseTerms_transaction', return_value=None, autospec=True), \
         patch.object(account, 'sign_transaction', return_value=MagicMock(rawTransaction=b'signed_tx'), autospec=True), \
         patch.object(web3.eth, 'send_raw_transaction', return_value=b'\x12\x9f\x7d\xd8\x02\x20\x0f\x09\x62\x21\xdd\x89\xd5\xb0\x86\xe4\xbd\x3a\xd6\xea\xfb\x37\x8a\x0c\x75\xe3\xb0\x4f\xc3\x75\xf9\x97', autospec=True), \
         patch.object(web3.eth, 'get_transaction_count', return_value=1, autospec=True):

        response = license_client.registerCommercialRemixPIL(
            minting_fee=1,
            currency='0x0000000000000000000000000000000000000000',
            commercial_rev_share=100,
            royalty_policy='0x0000000000000000000000000000000000000000'
        )
        
        assert response['licenseTermsId'] == 1
        assert 'txHash' not in response

def test_registerCommercialRemixPIL_error(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=0, autospec=True), \
         patch.object(license_client.license_template_client, 'build_registerLicenseTerms_transaction', side_effect=Exception("request fail."), autospec=True):

        with pytest.raises(Exception) as excinfo:
            license_client.registerCommercialRemixPIL(
                minting_fee=1,
                currency='0x0000000000000000000000000000000000000000',
                commercial_rev_share=100,
                royalty_policy='0x0000000000000000000000000000000000000000'
            )

        assert 'request fail.' in str(excinfo.value)

def test_registerCommercialRemixPIL_license_terms_id_not_registered(license_client):
    tx_hash = "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"
    with patch.object(license_client.license_template_client, 'getLicenseTermsId', return_value=0, autospec=True), \
         patch.object(license_client.license_template_client, 'build_registerLicenseTerms_transaction', return_value={'from': account.address, 'nonce': 1, 'gas': 2000000, 'gasPrice': web3.to_wei('100', 'gwei')}, autospec=True), \
         patch.object(account, 'sign_transaction', return_value=MagicMock(rawTransaction=b'signed_tx'), autospec=True), \
         patch.object(web3.eth, 'send_raw_transaction', return_value=bytes.fromhex(tx_hash[2:]), autospec=True), \
         patch.object(web3.eth, 'get_transaction_count', return_value=1, autospec=True), \
         patch.object(web3.eth, 'wait_for_transaction_receipt', return_value=MagicMock(), autospec=True):

        response = license_client.registerCommercialRemixPIL(
            minting_fee=1,
            currency='0x0000000000000000000000000000000000000000',
            commercial_rev_share=100,
            royalty_policy='0x0000000000000000000000000000000000000000'
        )
        
        assert 'txHash' in response
        assert response['txHash'] == tx_hash[2:]
        assert isinstance(response['txHash'], str)

def test_attachLicenseTerms_ip_not_registered(license_client):
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=False, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.attachLicenseTerms(ip_id='0x0000000000000000000000000000000000000000', license_template='0x0000000000000000000000000000000000000000', license_terms_id=1)
        assert str(excinfo.value) == 'The IP with id 0x0000000000000000000000000000000000000000 is not registered.'

def test_attachLicenseTerms_license_terms_not_exist(license_client):
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True), \
         patch.object(license_client.license_registry_client, 'exists', return_value=False, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.attachLicenseTerms(ip_id='0x0000000000000000000000000000000000000000', license_template='0x0000000000000000000000000000000000000000', license_terms_id=1)
        assert str(excinfo.value) == 'License terms id 1 do not exist.'

def test_attachLicenseTerms_already_attached(license_client):
    with patch.object(license_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True), \
         patch.object(license_client.license_registry_client, 'exists', return_value=True, autospec=True), \
         patch.object(license_client.license_registry_client, 'hasIpAttachedLicenseTerms', return_value=True, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.attachLicenseTerms(ip_id='0x0000000000000000000000000000000000000000', license_template='0x0000000000000000000000000000000000000000', license_terms_id=1)
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

        response = license_client.attachLicenseTerms(ip_id='0x0000000000000000000000000000000000000000', license_template='0x0000000000000000000000000000000000000000', license_terms_id=1)
        
        assert 'txHash' in response
        assert response['txHash'] == tx_hash[2:]
        assert isinstance(response['txHash'], str)

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
                license_terms_id=1, amount=1,
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
                license_terms_id=1, amount=1,
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
                license_terms_id=1, amount=1,
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
            license_terms_id=1, amount=1,
            receiver='0x0000000000000000000000000000000000000000'
        )
        
        assert 'txHash' in response
        assert response['txHash'] == tx_hash[2:]
        assert isinstance(response['txHash'], str)

def test_getLicenseTerms_success(license_client):
    mock_license_terms_response = {
        'terms': {
            'transferable': True,
            'royaltyPolicy': '0x0000000000000000000000000000000000000000',
            'mintingFee': 1,
            'expiration': 1,
            'commercialUse': True,
            'commercialAttribution': True,
            'commercializerChecker': '0x0000000000000000000000000000000000000000',
            'commercializerCheckerData': '0x0000000000000000000000000000000000000000',
            'commercialRevShare': 100,
            'commercialRevCelling': 1,
            'derivativesAllowed': True,
            'derivativesAttribution': True,
            'derivativesApproval': True,
            'derivativesReciprocal': True,
            'derivativeRevCelling': 1,
            'currency': '0x0000000000000000000000000000000000000000',
            'uri': 'string',
        },
    }

    with patch.object(license_client.license_template_client, 'getLicenseTerms', return_value=mock_license_terms_response, autospec=True):
        result = license_client.getLicenseTerms(1)
        assert result == mock_license_terms_response

def test_getLicenseTerms_error(license_client):
    with patch.object(license_client.license_template_client, 'getLicenseTerms', side_effect=Exception("Given licenseTermsId does not exist."), autospec=True):
        with pytest.raises(ValueError) as excinfo:
            license_client.getLicenseTerms(1)
        assert str(excinfo.value) == 'Failed to get license terms: Given licenseTermsId does not exist.'

