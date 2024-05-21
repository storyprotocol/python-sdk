import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from web3 import Web3
from dotenv import load_dotenv

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from src.story_protocol_python_sdk.resources.IPAsset import IPAsset

# Load environment variables from .env file
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
def ip_asset():
    chain_id = 11155111  # Sepolia chain ID
    return IPAsset(web3, account, chain_id)

def test_ip_asset_register_token_already_registered(ip_asset):
    token_contract = "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"
    token_id = "3"
    ip_id = "0xd142822Dc1674154EaF4DDF38bbF7EF8f0D8ECe4"

    with patch.object(ip_asset.ip_asset_registry_client, 'ipId', return_value=ip_id), \
         patch.object(ip_asset.ip_asset_registry_client, 'isRegistered', return_value=True):

        response = ip_asset.register(token_contract, token_id)

        assert response['ipId'] == ip_id
        assert response['txHash'] is None

def test_ip_asset_register_token_not_registered(ip_asset):
    token_contract = "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"
    token_id = "3"
    ip_id = "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"

    with patch.object(ip_asset.ip_asset_registry_client, 'ipId', return_value=ip_id), \
         patch.object(ip_asset.ip_asset_registry_client, 'isRegistered', return_value=False), \
         patch.object(ip_asset.ip_asset_registry_client, 'build_register_transaction', return_value={
             'from': account.address,
             'nonce': web3.eth.get_transaction_count(account.address),
             'gas': 2000000,
             'gasPrice': web3.to_wei('100', 'gwei')
         }):

        # Mock signing and sending transaction
        with patch.object(account, 'sign_transaction', return_value=MagicMock(rawTransaction=b'signed_tx')), \
             patch.object(web3.eth, 'send_raw_transaction', return_value=b'\x12\x9f\x7d\xd8\x02\x20\x0f\x09\x62\x21\xdd\x89\xd5\xb0\x86\xe4\xbd\x3a\xd6\xea\xfb\x37\x8a\x0c\x75\xe3\xb0\x4f\xc3\x75\xf9\x97'):

            # Mock the return value for the send_raw_transaction to include the '0x' prefix
            with patch.object(web3.eth, 'send_raw_transaction', return_value=bytes.fromhex("0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"[2:])):
                res = ip_asset.register(token_contract, token_id)

                assert res['txHash'] == "129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"
                assert res['ipId'] == ip_id

def test_ip_asset_register_error(ip_asset):
    token_contract = "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"
    token_id = "3"
    ip_id = "0xd142822Dc1674154EaF4DDF38bbF7EF8f0D8ECe4"

    with patch.object(ip_asset.ip_asset_registry_client, 'ipId', return_value=ip_id), \
         patch.object(ip_asset.ip_asset_registry_client, 'isRegistered', return_value=False), \
         patch.object(ip_asset.ip_asset_registry_client, 'build_register_transaction', side_effect=Exception("revert error")):

        with pytest.raises(Exception) as excinfo:
            response = ip_asset.register(token_contract, token_id)
        assert str(excinfo.value) == "revert error"

def test_register_derivative_child_ip_not_registered(ip_asset):
    child_ip_id = "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"
    parent_ip_ids = ["0xd142822Dc1674154EaF4DDF38bbF7EF8f0D8ECe4"]
    license_terms_ids = ["1"]

    with patch.object(ip_asset.ip_asset_registry_client, 'isRegistered', return_value=False):
        with pytest.raises(ValueError) as excinfo:
            ip_asset.registerDerivative(child_ip_id, parent_ip_ids, license_terms_ids, "0x0000000000000000000000000000000000000000")
        assert str(excinfo.value) == f"The child IP with id {child_ip_id} is not registered."

def test_register_derivative_parent_ip_not_registered(ip_asset):
    child_ip_id = "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"
    parent_ip_ids = ["0xd142822Dc1674154EaF4DDF38bbF7EF8f0D8ECe4"]
    license_terms_ids = ["1"]

    with patch.object(ip_asset.ip_asset_registry_client, 'isRegistered') as mock_is_registered:
        mock_is_registered.side_effect = [True, False]
        with pytest.raises(ValueError) as excinfo:
            ip_asset.registerDerivative(child_ip_id, parent_ip_ids, license_terms_ids, "0x0000000000000000000000000000000000000000")
        assert str(excinfo.value) == f"The parent IP with id {parent_ip_ids[0]} is not registered."

def test_register_derivative_mismatched_ids(ip_asset):
    child_ip_id = "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"
    parent_ip_ids = ["0xd142822Dc1674154EaF4DDF38bbF7EF8f0D8ECe4"]
    license_terms_ids = ["1", "2"]

    with patch.object(ip_asset.ip_asset_registry_client, 'isRegistered', return_value=True):
        with pytest.raises(ValueError) as excinfo:
            ip_asset.registerDerivative(child_ip_id, parent_ip_ids, license_terms_ids, "0x0000000000000000000000000000000000000000")
        assert str(excinfo.value) == "Parent IP IDs and license terms IDs must match in quantity."

def test_register_derivative_not_attached_license_terms(ip_asset):
    child_ip_id = "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"
    parent_ip_ids = ["0xd142822Dc1674154EaF4DDF38bbF7EF8f0D8ECe4"]
    license_terms_ids = ["1"]

    with patch.object(ip_asset.ip_asset_registry_client, 'isRegistered', return_value=True), \
         patch.object(ip_asset.license_registry_client, 'hasIpAttachedLicenseTerms', return_value=False):
        with pytest.raises(ValueError) as excinfo:
            ip_asset.registerDerivative(child_ip_id, parent_ip_ids, license_terms_ids, "0x0000000000000000000000000000000000000000")
        assert str(excinfo.value) == f"License terms id {license_terms_ids[0]} must be attached to the parent ipId {parent_ip_ids[0]} before registering derivative."

def test_register_derivative_success(ip_asset):
    child_ip_id = "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"
    parent_ip_ids = ["0xd142822Dc1674154EaF4DDF38bbF7EF8f0D8ECe4"]
    license_terms_ids = ["1"]
    tx_hash = "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"

    with patch.object(ip_asset.ip_asset_registry_client, 'isRegistered', return_value=True), \
         patch.object(ip_asset.license_registry_client, 'hasIpAttachedLicenseTerms', return_value=True), \
         patch.object(ip_asset.licensing_module_client, 'build_registerDerivative_transaction', return_value={'from': account.address, 'nonce': 1, 'gas': 2000000, 'gasPrice': 30000000000}), \
         patch.object(account, 'sign_transaction', return_value=MagicMock(rawTransaction=b'signed_tx')), \
         patch.object(web3.eth, 'send_raw_transaction', return_value=bytes.fromhex(tx_hash[2:])):
        res = ip_asset.registerDerivative(child_ip_id, parent_ip_ids, license_terms_ids, "0x0000000000000000000000000000000000000000")

        assert res['txHash'] == tx_hash[2:]

def test_register_derivative_with_license_tokens_child_ip_not_registered(ip_asset):
    with patch.object(ip_asset.ip_asset_registry_client, 'isRegistered', return_value=False):
        with pytest.raises(ValueError) as excinfo:
            ip_asset.registerDerivativeWithLicenseTokens("0xd142822Dc1674154EaF4DDF38bbF7EF8f0D8ECe4", ["1"])
        assert str(excinfo.value) == "The child IP with id 0xd142822Dc1674154EaF4DDF38bbF7EF8f0D8ECe4 is not registered."

def test_register_derivative_with_license_tokens_token_not_owned_by_caller(ip_asset):
    with patch.object(ip_asset.ip_asset_registry_client, 'isRegistered', side_effect=[True, True]), \
         patch.object(ip_asset.license_token_client, 'ownerOf', return_value="0xAnotherAddress"):
        with pytest.raises(ValueError) as excinfo:
            ip_asset.registerDerivativeWithLicenseTokens("0xd142822Dc1674154EaF4DDF38bbF7EF8f0D8ECe4", ["1"])
        assert str(excinfo.value) == "License token id 1 must be owned by the caller."

def test_register_derivative_with_license_tokens_success(ip_asset):
    with patch.object(ip_asset.ip_asset_registry_client, 'isRegistered', side_effect=[True, True]), \
         patch.object(ip_asset.license_token_client, 'ownerOf', return_value=account.address), \
         patch.object(ip_asset.licensing_module_client, 'build_registerDerivativeWithLicenseTokens_transaction', return_value={
             'from': account.address,
             'nonce': web3.eth.get_transaction_count(account.address),
             'gas': 2000000,
             'gasPrice': web3.to_wei('100', 'gwei')
         }), \
         patch.object(account, 'sign_transaction', return_value=MagicMock(rawTransaction=b'signed_tx')), \
         patch.object(web3.eth, 'send_raw_transaction', return_value=bytes.fromhex("0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"[2:])):

        res = ip_asset.registerDerivativeWithLicenseTokens("0xd142822Dc1674154EaF4DDF38bbF7EF8f0D8ECe4", ["1"])

        assert res['txHash'] == "129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"

