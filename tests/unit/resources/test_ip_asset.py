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
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

@pytest.fixture
def ip_asset():
    chain_id = 1516
    return IPAsset(web3, account, chain_id)

class TestIPAssetRegister:
    def test_register_invalid_deadline_type(self, ip_asset):
        with patch.object(ip_asset, '_get_ip_id', return_value="0xd142822Dc1674154EaF4DDF38bbF7EF8f0D8ECe4"), \
             patch.object(ip_asset, '_is_registered', return_value=False):
            with pytest.raises(ValueError, match="Invalid deadline value."):
                ip_asset.register(
                    nft_contract="0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c",
                    token_id=3,
                    deadline="error",
                    ip_metadata={
                        'ipMetadataURI': "1",
                        'ipMetadataHash': ZERO_HASH
                    }
                )

    def test_register_already_registered(self, ip_asset):
        token_contract = "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"
        token_id = 3
        ip_id = "0xd142822Dc1674154EaF4DDF38bbF7EF8f0D8ECe4"

        with patch.object(ip_asset.ip_asset_registry_client, 'ipId', return_value=ip_id), \
             patch.object(ip_asset.ip_asset_registry_client, 'isRegistered', return_value=True):
            response = ip_asset.register(token_contract, token_id)
            assert response['ipId'] == ip_id
            assert response['txHash'] is None

    def test_register_successful(self, ip_asset):
        token_contract = "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"
        token_id = 3
        ip_id = "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"
        tx_hash = "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"

        with patch.object(ip_asset, '_get_ip_id', return_value=ip_id), \
             patch.object(ip_asset, '_is_registered', return_value=False), \
             patch('story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client.IPAssetRegistryClient.build_register_transaction', return_value={
                 'data': '0x',
                 'nonce': 0,
                 'gas': 2000000,
                 'gasPrice': Web3.to_wei('100', 'gwei')
             }), \
             patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr=tx_hash)), \
             patch('web3.eth.Eth.wait_for_transaction_receipt', return_value={'status': 1, 'logs': []}), \
             patch.object(ip_asset, '_parse_tx_ip_registered_event', return_value={'ipId': ip_id}):

            result = ip_asset.register(token_contract, token_id)
            assert result['txHash'] == tx_hash[2:]
            assert result['ipId'] == ip_id

    def test_register_with_metadata(self, ip_asset):
        token_contract = "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"
        token_id = 3
        ip_id = "0x1daAE3197Bc469Cb97B917aa460a12dD95c6627c"
        tx_hash = "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"

        metadata = {
            'ipMetadataURI': "",
            'ipMetadataHash': ZERO_HASH,
            'nftMetadataURI': "",
            'nftMetadataHash': ZERO_HASH,
        }

        calculated_deadline = 1000

        with patch.object(ip_asset, '_get_ip_id', return_value=ip_id), \
             patch.object(ip_asset, '_is_registered', return_value=False), \
             patch.object(ip_asset.sign_util, 'get_deadline', return_value=calculated_deadline), \
             patch.object(ip_asset.sign_util, 'get_permission_signature', return_value={"signature": tx_hash}), \
             patch.object(ip_asset.registration_workflows_client, 'build_registerIp_transaction', return_value={
                 'data': '0x',
                 'nonce': 0,
                 'gas': 2000000,
                 'gasPrice': Web3.to_wei('100', 'gwei')
             }), \
             patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr=tx_hash)), \
             patch('web3.eth.Eth.wait_for_transaction_receipt', return_value={'status': 1, 'logs': []}), \
             patch.object(ip_asset, '_parse_tx_ip_registered_event', return_value={'ipId': ip_id}):

            result = ip_asset.register(
                nft_contract=token_contract,
                token_id=token_id,
                ip_metadata=metadata,
                deadline=1000
            )

            assert result['txHash'] == tx_hash[2:]
            assert result['ipId'] == ip_id