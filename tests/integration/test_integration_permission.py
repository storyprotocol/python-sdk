# tests/integration/test_integration_permission.py

import pytest
from web3 import Web3

from setup_for_integration import (
    web3,
    account, 
    story_client,
    get_token_id,
    MockERC721,
    MockERC20,
    ZERO_ADDRESS,
    ROYALTY_POLICY,
    PIL_LICENSE_TEMPLATE,
    CORE_METADATA_MODULE
)

class TestPermissions:
    @pytest.fixture(scope="class")
    def ip_id(self, story_client):
        """Fixture to create an IP for testing permissions."""
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id,
            tx_options={"wait_for_transaction": True}
        )
        assert 'ip_id' in response, "Failed to register IP"
        return response['ip_id']

    def test_set_permission(self, story_client, ip_id):
        """Test setting permission successfully."""
        response = story_client.Permission.set_permission(
            ip_id=ip_id,
            signer=account.address,
            to=CORE_METADATA_MODULE,
            permission=1,  # ALLOW
            func="function setAll(address,string,bytes32,bytes32)",
            tx_options={"wait_for_transaction": True}
        )

        assert response is not None
        assert 'tx_hash' in response
        assert isinstance(response['tx_hash'], str)
        assert len(response['tx_hash']) > 0

    def test_set_all_permissions(self, story_client, ip_id):
        """Test setting all permissions successfully."""
        response = story_client.Permission.set_all_permissions(
            ip_id=ip_id,
            signer=account.address,
            permission=1,  # ALLOW
        )

        assert response is not None
        assert 'tx_hash' in response
        assert isinstance(response['tx_hash'], str)
        assert len(response['tx_hash']) > 0

    def test_create_set_permission_signature(self, story_client, ip_id):
        """Test creating set permission signature."""
        deadline = web3.eth.get_block('latest')['timestamp'] + 60000
        
        response = story_client.Permission.create_set_permission_signature(
            ip_id=ip_id,
            signer=account.address,
            to=CORE_METADATA_MODULE,
            func="setAll(address,string,bytes32,bytes32)",
            permission=1,  # ALLOW
            deadline=deadline,
        )

        assert response is not None
        assert 'tx_hash' in response
        assert isinstance(response['tx_hash'], str)
        assert len(response['tx_hash']) > 0

    def test_set_permission_invalid_ip(self, story_client):
        """Test setting permission for an unregistered IP."""
        unregistered_ip = "0x1234567890123456789012345678901234567890"
        
        with pytest.raises(Exception) as exc_info:
            story_client.Permission.set_permission(
                ip_id=unregistered_ip,
                signer=account.address,
                to=CORE_METADATA_MODULE,
                permission=1,
            )
        
        assert f"IP id with {unregistered_ip} is not registered" in str(exc_info.value)
