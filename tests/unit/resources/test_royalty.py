import pytest, os, sys
from unittest.mock import patch, MagicMock
from web3 import Web3

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from src.resources.Royalty import Royalty

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
def royalty_client():
    chain_id = 11155111  # Sepolia chain ID
    return Royalty(web3, account, chain_id)

def test_collectRoyaltyTokens_parent_ip_id_not_registered(royalty_client):
    parent_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
    child_ip_id = "0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"

    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=False, autospec=True):
        with pytest.raises(ValueError) as excinfo:
            royalty_client.collectRoyaltyTokens(parent_ip_id, child_ip_id)
        assert str(excinfo.value) == f"The parent IP with id {parent_ip_id} is not registered."

def test_collectRoyaltyTokens_royalty_vault_ip_id_not_registered(royalty_client):
    parent_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
    child_ip_id = "0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"

    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', side_effect=[True, False], autospec=True):
        with pytest.raises(ValueError) as excinfo:
            royalty_client.collectRoyaltyTokens(parent_ip_id, child_ip_id)
        assert str(excinfo.value) == f"The royalty vault IP with id {child_ip_id} is not registered."

def test_collectRoyaltyTokens_royalty_vault_address_empty(royalty_client):
    parent_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
    child_ip_id = "0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"

    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True), \
         patch.object(royalty_client.royalty_policy_lap_client, 'getRoyaltyData', return_value=[], autospec=True):
        with pytest.raises(ValueError) as excinfo:
            royalty_client.collectRoyaltyTokens(parent_ip_id, child_ip_id)
        assert str(excinfo.value) == f"The royalty vault IP with id {child_ip_id} address is not set."

def test_collectRoyaltyTokens_royalty_vault_address_zero(royalty_client):
    parent_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
    child_ip_id = "0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"

    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True), \
         patch.object(royalty_client.royalty_policy_lap_client, 'getRoyaltyData', return_value=[True, "0x", 1, [child_ip_id], [1]], autospec=True):
        with pytest.raises(ValueError) as excinfo:
            royalty_client.collectRoyaltyTokens(parent_ip_id, child_ip_id)
        assert str(excinfo.value) == f"The royalty vault IP with id {child_ip_id} address is not set."
        
def test_collectRoyaltyTokens_success(royalty_client):
    parent_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
    child_ip_id = "0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"
    tx_hash = "0x39f7ea8b04f383d7b60e1882f6bb7d94d3c9efa9251cef4543a1bb655faf21fb"

    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=True, autospec=True), \
         patch.object(royalty_client.royalty_policy_lap_client, 'getRoyaltyData', return_value=[True, "0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7", 1, [child_ip_id], [1]], autospec=True), \
         patch.object(web3.eth, 'send_raw_transaction', return_value=bytes.fromhex(tx_hash[2:]), autospec=True), \
         patch.object(web3.eth, 'wait_for_transaction_receipt', return_value=MagicMock(logs=[{'topics': [web3.keccak(text="RoyaltyTokensCollected(address,uint256)").hex()], 'data': bytes.fromhex('000000000000000000000000000000000000000000000000000000000000000a')}]), autospec=True), \
         patch.object(royalty_client, '_parseTxRoyaltyTokensCollectedEvent', return_value=10, autospec=True):

        result = royalty_client.collectRoyaltyTokens(parent_ip_id, child_ip_id)

        assert result['txHash'] == tx_hash[2:]
        assert result['royaltyTokensCollected'] == 10

def test_snapshot_royaltyVaultIpId_error(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=False):
        child_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
        
        with pytest.raises(ValueError, match=f"The royalty vault IP with id {child_ip_id} is not registered."):
            royalty_client.snapshot(child_ip_id)

def test_snapshot_royaltyVaultAddress_error(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=True):
        with patch.object(royalty_client.royalty_policy_lap_client, 'getRoyaltyData', return_value=[True, "0x", 1, ["0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"], [1]]):
            child_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"

            with pytest.raises(ValueError, match=f"The royalty vault IP with id {child_ip_id} address is not set."):
                royalty_client.snapshot(child_ip_id)

def test_snapshot_success(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=True):
        with patch.object(royalty_client.royalty_policy_lap_client, 'getRoyaltyData', return_value=[True, "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c", 1, ["0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"], [1]]):
            with patch.object(royalty_client, '_parseTxSnapshotCompletedEvent', return_value=2):
                with patch('src.abi.IpRoyaltyVaultImpl.IpRoyaltyVaultImpl_client.IpRoyaltyVaultImplClient.build_snapshot_transaction', return_value={
                    'data': '0x',
                    'nonce': 0,
                    'gas': 2000000,
                    'gasPrice': Web3.to_wei('300', 'gwei')
                }):
                    with patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr='0x471343c1ad3b358843b2079d8c5c1a0a5a86fe88382cdc67604b0209bbedf523')):
                        with patch('web3.eth.Eth.wait_for_transaction_receipt', return_value={'status': 1, 'logs': []}):
                            child_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"

                            response = royalty_client.snapshot(child_ip_id)
                            assert response is not None
                            assert 'txHash' in response
                            assert response['txHash'] == '471343c1ad3b358843b2079d8c5c1a0a5a86fe88382cdc67604b0209bbedf523'
                            assert 'snapshotId' in response
                            assert response['snapshotId'] == 2

def test_claimableRevenue_royaltyVaultIpId_error(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=False):
        child_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
        account_address = account.address
        snapshot_id = 1
        token = "0xB132A6B7AE652c974EE1557A3521D53d18F6739f"

        with pytest.raises(ValueError, match=f"The royalty vault IP with id {child_ip_id} is not registered."):
            royalty_client.claimableRevenue(child_ip_id, account_address, snapshot_id, token)

def test_claimableRevenue_royaltyVaultAddress_error(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=True):
        with patch.object(royalty_client.royalty_policy_lap_client, 'getRoyaltyData', return_value=[True, "0x", 1, ["0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"], [1]]):
            child_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
            account_address = account.address
            snapshot_id = 1
            token = "0xB132A6B7AE652c974EE1557A3521D53d18F6739f"

            with pytest.raises(ValueError, match=f"The royalty vault IP with id {child_ip_id} address is not set."):
                royalty_client.claimableRevenue(child_ip_id, account_address, snapshot_id, token)

def test_claimableRevenue_success(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=True):
        with patch.object(royalty_client.royalty_policy_lap_client, 'getRoyaltyData', return_value=[True, "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c", 1, ["0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"], [1]]):
            with patch('src.abi.IpRoyaltyVaultImpl.IpRoyaltyVaultImpl_client.IpRoyaltyVaultImplClient.claimableRevenue', return_value=0):
                child_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
                account_address = account.address
                snapshot_id = 1
                token = "0xB132A6B7AE652c974EE1557A3521D53d18F6739f"

                response = royalty_client.claimableRevenue(child_ip_id, account_address, snapshot_id, token)
                assert response == 0
