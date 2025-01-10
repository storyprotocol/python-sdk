# tests/integration/test_integration_permission.py

import os, json, sys
import pytest
from dotenv import load_dotenv
from web3 import Web3

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from utils import get_token_id, get_story_client_in_sepolia, MockERC721, check_event_in_tx

load_dotenv()
private_key = os.getenv('WALLET_PRIVATE_KEY')
rpc_url = os.getenv('RPC_PROVIDER_URL')

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(rpc_url))
if not web3.is_connected():
    raise Exception("Failed to connect to Web3 provider")

# Set up the account with the private key
account = web3.eth.account.from_key(private_key)

CORE_METADATA_MODULE = "0x2ac240293f12032E103458451dE8A8096c5A72E8"

class TestPermission:
    """Tests for Permission management"""

    @pytest.fixture(scope="class")
    def story_client(self):
        """Fixture for story client instance"""
        return get_story_client_in_sepolia(web3, account)

    @pytest.fixture(scope="class")
    def ip_id(self, story_client):
        """Fixture to create an IP for testing permissions"""
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        response = story_client.IPAsset.register(
            token_contract=MockERC721,
            token_id=token_id
        )
        return response['ipId']

    def test_set_permission(self, story_client, ip_id):
        """Test setting a single permission"""
        response = story_client.Permission.setPermission(
            ip_asset=ip_id,
            signer=account.address,
            to=CORE_METADATA_MODULE,
            permission=1,
            func="0x00000000"
        )

        assert response is not None, "Response should not be None"
        assert 'txHash' in response, "Response should contain txHash"
        assert isinstance(response['txHash'], str), "txHash should be string"
        assert len(response['txHash']) > 0, "txHash should not be empty"
        # Check for PermissionSet event
        assert check_event_in_tx(
            web3, 
            response['txHash'],
            "PermissionSet(address,address,address,address,bytes4,uint8)"
        ), "PermissionSet event should be emitted"

    def test_set_all_permissions(self, story_client, ip_id):
        """Test setting all permissions"""
        response = story_client.Permission.setAllPermissions(
            ip_asset=ip_id,
            signer=account.address,
            permission=1  # AccessPermission.ALLOW
        )

        assert response is not None, "Response should not be None"
        assert 'txHash' in response, "Response should contain txHash"
        assert 'success' in response, "Response should contain success flag"
        assert response['success'] is True, "Operation should be successful"

    def test_create_set_permission_signature(self, story_client, ip_id):
        """Test creating a set permission signature"""
        response = story_client.Permission.createSetPermissionSignature(
            ip_asset=ip_id,
            signer=account.address,
            to=CORE_METADATA_MODULE,
            func="function setAll(address,string,bytes32,bytes32)",
            permission=1,  # AccessPermission.ALLOW
            deadline=60000
        )

        assert response is not None, "Response should not be None"
        assert 'signature' in response, "Response should contain signature"
        assert isinstance(response['signature'], str), "Signature should be string"

    def test_set_batch_permissions(self, story_client, ip_id):
        """Test setting batch permissions"""
        permissions = [
            {
                'ip_asset': ip_id,
                'signer': account.address,
                'to': CORE_METADATA_MODULE,
                'permission': 0,  # AccessPermission.DENY
                'func': "function setAll(address,string,bytes32,bytes32)"
            },
            {
                'ip_asset': ip_id,
                'signer': account.address,
                'to': CORE_METADATA_MODULE,
                'permission': 0,  # AccessPermission.DENY
                'func': "function freezeMetadata(address)"
            }
        ]

        response = story_client.Permission.setBatchPermissions(permissions=permissions)

        assert response is not None, "Response should not be None"
        assert 'txHash' in response, "Response should contain txHash"
        assert 'success' in response, "Response should contain success flag"
        assert response['success'] is True, "Operation should be successful"

    def test_create_batch_permission_signature(self, story_client, ip_id):
        """Test creating batch permission signature"""
        permissions = [
            {
                'ip_asset': ip_id,
                'signer': account.address,
                'to': CORE_METADATA_MODULE,
                'permission': 0,  # AccessPermission.DENY
                'func': "function setAll(address,string,bytes32,bytes32)"
            },
            {
                'ip_asset': ip_id,
                'signer': account.address,
                'to': CORE_METADATA_MODULE,
                'permission': 0,  # AccessPermission.DENY
                'func': "function freezeMetadata(address)"
            }
        ]

        response = story_client.Permission.createBatchPermissionSignature(
            ip_asset=ip_id,
            permissions=permissions,
            deadline=60000
        )

        assert response is not None, "Response should not be None"
        assert 'signatures' in response, "Response should contain signatures"
        assert isinstance(response['signatures'], list), "Signatures should be a list"

    def test_set_permission_invalid_address(self, story_client, ip_id):
        """Test setting permission with invalid address"""
        with pytest.raises(ValueError) as exc_info:
            story_client.Permission.setPermission(
                ip_asset=ip_id,
                signer="invalid_address",
                to=CORE_METADATA_MODULE,
                permission=1
            )
        assert "not a valid address" in str(exc_info.value)

    def test_set_permission_unregistered_ip(self, story_client):
        """Test setting permission for unregistered IP"""
        unregistered_ip = "0x1234567890123456789012345678901234567890"
        with pytest.raises(ValueError) as exc_info:
            story_client.Permission.setPermission(
                ip_asset=unregistered_ip,
                signer=account.address,
                to=CORE_METADATA_MODULE,
                permission=1
            )
        assert "not registered" in str(exc_info.value)