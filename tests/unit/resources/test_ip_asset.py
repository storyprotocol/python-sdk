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
ZERO_HASH = "0x0000000000000000000000000000000000000000000000000000000000000000"

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
    tx_hash = "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"

    # Mocking the expected behavior of the functions
    with patch.object(ip_asset.ip_asset_registry_client, 'ipId', return_value=ip_id), \
         patch.object(ip_asset.ip_asset_registry_client, 'isRegistered', return_value=False), \
         patch('story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client.IPAssetRegistryClient.build_register_transaction', return_value={
             'data': '0x',
             'nonce': 0,
             'gas': 2000000,
             'gasPrice': Web3.to_wei('100', 'gwei')
         }), \
         patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr=tx_hash)), \
         patch('web3.eth.Eth.wait_for_transaction_receipt', return_value={'status': 1, 'logs': []}):

        # Call the function being tested
        result = ip_asset.register(token_contract, token_id)
        
        assert result['txHash'] == tx_hash[2:]
        assert result['ipId'] == ip_id

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

    # Mocking the expected behavior of the functions
    with patch.object(ip_asset.ip_asset_registry_client, 'isRegistered', return_value=True), \
         patch.object(ip_asset.license_registry_client, 'hasIpAttachedLicenseTerms', return_value=True), \
         patch('story_protocol_python_sdk.abi.LicensingModule.LicensingModule_client.LicensingModuleClient.build_registerDerivative_transaction', return_value={
             'data': '0x',
             'nonce': 1,
             'gas': 2000000,
             'gasPrice': Web3.to_wei('300', 'gwei')
         }), \
         patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr=tx_hash)), \
         patch('web3.eth.Eth.wait_for_transaction_receipt', return_value={'status': 1, 'logs': []}):

        # Call the function being tested
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
    child_ip_id = "0xd142822Dc1674154EaF4DDF38bbF7EF8f0D8ECe4"
    license_token_ids = ["1"]
    tx_hash = "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"

    # Mocking the expected behavior of the functions
    with patch.object(ip_asset.ip_asset_registry_client, 'isRegistered', return_value=True), \
         patch.object(ip_asset.license_token_client, 'ownerOf', return_value=ip_asset.account.address), \
         patch('story_protocol_python_sdk.abi.LicensingModule.LicensingModule_client.LicensingModuleClient.build_registerDerivativeWithLicenseTokens_transaction', return_value={
             'data': '0x',
             'nonce': 1,
             'gas': 2000000,
             'gasPrice': Web3.to_wei('300', 'gwei')
         }), \
         patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr=tx_hash)), \
         patch('web3.eth.Eth.wait_for_transaction_receipt', return_value={'status': 1, 'logs': []}):

        # Call the function being tested
        res = ip_asset.registerDerivativeWithLicenseTokens(child_ip_id, license_token_ids)

        assert res['txHash'] == tx_hash[2:]

def test_mint_register_pil_type_error(ip_asset):
    with pytest.raises(ValueError, match="PIL type is required and must be one of the predefined PIL types."):
        ip_asset.mintAndRegisterIpAssetWithPilTerms(
            nft_contract="0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c",
            pil_type="incorrect_type"
        )

def test_mint_register_invalid_address(ip_asset):
    with pytest.raises(ValueError, match="The NFT contract address 0x is not valid."):
        ip_asset.mintAndRegisterIpAssetWithPilTerms(
            nft_contract="0x",
            pil_type='non_commercial_remix'
        )
        
def test_mint_register_successful_transaction(ip_asset):
    tx_receipt_mock = {
        'status': 1,
        'logs': [
            {
                'topics': [
                    Web3.keccak(text="IPRegistered(address,uint256,address,uint256,string,string,uint256)").hex(),
                    Web3.to_hex(Web3.keccak(text="1")),
                    Web3.to_hex(Web3.keccak(text="0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c")),
                    Web3.to_hex(Web3.keccak(text="1"))
                ],
                'data': '0x000000000000000000000000BD78ec0d5B1320f8A6C6225A73BF4FeBdb95233F0000000000000000000000000000000000000000000000000000000000000000'
            }
        ]
    }

    with patch.object(ip_asset.spg_client, 'build_mintAndRegisterIpAndAttachPILTerms_transaction', return_value={
                'to': "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c",
                'value': 0,
                'data': "0x",
                'gas': 2000000,
                'gasPrice': Web3.to_wei('50', 'gwei'),
                'nonce': 0
            }), \
         patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr="0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997")), \
         patch('web3.eth.Eth.wait_for_transaction_receipt', return_value=tx_receipt_mock), \
         patch.object(ip_asset, '_parse_tx_ip_registered_event', return_value={
             'ipId': '0xBD78ec0d5B1320f8A6C6225A73BF4FeBdb95233F',
             'tokenId': 1
         }), \
         patch.object(ip_asset, '_parse_tx_license_terms_attached_event', return_value=1):

        response = ip_asset.mintAndRegisterIpAssetWithPilTerms(
            nft_contract="0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c",
            pil_type='commercial_remix',
            metadata={
                'nftMetadataHash': Web3.to_hex(Web3.keccak(text="test-nft-metadata-hash")),
            }
        )

        assert response['txHash'] == "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"[2:]
        assert response['ipId'] == "0xBD78ec0d5B1320f8A6C6225A73BF4FeBdb95233F"
        assert response['licenseTermsId'] == 1
        assert response['tokenId'] == 1

def test_register_attach_pil_type_error(ip_asset):
    with pytest.raises(ValueError, match="PIL type is required and must be one of the predefined PIL types."):
        ip_asset.registerIpAndAttachPilTerms(
            nft_contract="0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c",
            token_id=3,
            pil_type="incorrect_type"
        )

def test_register_attach_already_registered(ip_asset):
    with patch.object(ip_asset, '_get_ip_id', return_value="0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"), \
         patch.object(ip_asset, '_is_registered', return_value=True):
        with pytest.raises(ValueError, match="The NFT with id 3 is already registered as IP."):
            ip_asset.registerIpAndAttachPilTerms(
                nft_contract="0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c",
                token_id=3,
                pil_type='non_commercial_remix'
            )

def test_register_attach_with_initial_metadata(ip_asset):
    with patch.object(ip_asset.spg_client, 'build_registerIpAndAttachPILTerms_transaction', return_value={
                'to': "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c",
                'value': 0,
                'data': "0x",
                'gas': 2000000,
                'gasPrice': Web3.to_wei('50', 'gwei'),
                'nonce': 0
            }), \
         patch.object(ip_asset, '_get_ip_id', return_value="0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"), \
         patch.object(ip_asset, '_is_registered', return_value=False), \
         patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr="0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997")), \
         patch('web3.eth.Eth.wait_for_transaction_receipt', return_value={'status': 1, 'logs': []}), \
         patch.object(ip_asset, '_get_permission_signature_for_spg', return_value="0xsignature"):

        ip_asset.registerIpAndAttachPilTerms(
            nft_contract="0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c",
            token_id=3,
            pil_type='non_commercial_remix',
            metadata={
                'metadataHash': Web3.to_hex(Web3.keccak(text="test-metadata-hash")),
                'metadataURI': ""
            }
        )

        expected_metadata = {
            'metadataURI': "",
            'metadataHash': Web3.to_hex(Web3.keccak(text="test-metadata-hash")),
            'nftMetadataHash': ZERO_HASH
        }

        args, kwargs = ip_asset.spg_client.build_registerIpAndAttachPILTerms_transaction.call_args
        assert args[2] == expected_metadata

def test_register_attach_successful_transaction(ip_asset):
    tx_receipt_mock = {
        'status': 1,
        'logs': [
            {
                'topics': [
                    Web3.keccak(text="LicenseTermsAttached(address,address,uint256)").hex(),
                    Web3.to_hex(Web3.keccak(text="1")),
                    Web3.to_hex(Web3.keccak(text="0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c")),
                    Web3.to_hex(Web3.keccak(text="1"))
                ],
                'data': '0x000000000000000000000000BD78ec0d5B1320f8A6C6225A73BF4FeBdb95233F0000000000000000000000000000000000000000000000000000000000000000'
            }
        ]
    }

    with patch.object(ip_asset.spg_client, 'build_registerIpAndAttachPILTerms_transaction', return_value={
                'to': "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c",
                'value': 0,
                'data': "0x",
                'gas': 2000000,
                'gasPrice': Web3.to_wei('50', 'gwei'),
                'nonce': 0
            }), \
         patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr="0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997")), \
         patch('web3.eth.Eth.wait_for_transaction_receipt', return_value=tx_receipt_mock), \
         patch.object(ip_asset, '_parse_tx_license_terms_attached_event', return_value=1), \
         patch.object(ip_asset, '_get_ip_id', return_value="0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"):

        response = ip_asset.registerIpAndAttachPilTerms(
            nft_contract="0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c",
            token_id=3,
            pil_type='commercial_remix',
            metadata={
                'nftMetadataHash': Web3.to_hex(Web3.keccak(text="test-nft-metadata-hash")),
            }
        )

        assert response['txHash'] == "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"[2:]
        assert response['ipId'] == "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"
        assert response['licenseTermsId'] == 1