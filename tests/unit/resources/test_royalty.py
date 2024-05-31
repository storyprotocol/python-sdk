import pytest, os, sys
from unittest.mock import patch, MagicMock
from web3 import Web3

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from src.story_protocol_python_sdk.resources.Royalty import Royalty

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
        assert str(excinfo.value) == f"The IP with id {child_ip_id} is not registered."

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
    checksum_address = "0x344A37c7086Ee79E51894949119878112487eaD7"
    royalty_tokens_collected = 10

    # Mocking the expected behavior of the functions
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=True), \
         patch.object(royalty_client, '_getRoyaltyVaultAddress', return_value=checksum_address), \
         patch.object(royalty_client, '_parseTxRoyaltyTokensCollectedEvent', return_value=royalty_tokens_collected), \
         patch('story_protocol_python_sdk.abi.IpRoyaltyVaultImpl.IpRoyaltyVaultImpl_client.IpRoyaltyVaultImplClient.build_collectRoyaltyTokens_transaction', return_value={
            'data': '0x',
            'nonce': 0,
            'gas': 2000000,
            'gasPrice': Web3.to_wei('300', 'gwei')
         }), \
         patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr=tx_hash)), \
         patch('web3.eth.Eth.wait_for_transaction_receipt', return_value={'status': 1, 'logs': [{'topics': [Web3.keccak(text="RoyaltyTokensCollected(address,uint256)").hex()], 'data': bytes.fromhex('000000000000000000000000000000000000000000000000000000000000000a')}]}):
        
        # Call the function being tested
        result = royalty_client.collectRoyaltyTokens(parent_ip_id, child_ip_id)
        
        assert result['txHash'] == tx_hash[2:]
        assert result['royaltyTokensCollected'] == royalty_tokens_collected
        
def test_snapshot_royaltyVaultIpId_error(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=False):
        parent_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
        
        with pytest.raises(ValueError, match=f"The IP with id {parent_ip_id} is not registered."):
            royalty_client.snapshot(parent_ip_id)

def test_snapshot_royaltyVaultAddress_error(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=True):
        with patch.object(royalty_client.royalty_policy_lap_client, 'getRoyaltyData', return_value=[True, "0x", 1, ["0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"], [1]]):
            parent_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"

            with pytest.raises(ValueError, match=f"The royalty vault IP with id {parent_ip_id} address is not set."):
                royalty_client.snapshot(parent_ip_id)

def test_snapshot_success(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=True):
        with patch.object(royalty_client.royalty_policy_lap_client, 'getRoyaltyData', return_value=[True, "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c", 1, ["0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"], [1]]):
            with patch.object(royalty_client, '_parseTxSnapshotCompletedEvent', return_value=2):
                with patch('story_protocol_python_sdk.abi.IpRoyaltyVaultImpl.IpRoyaltyVaultImpl_client.IpRoyaltyVaultImplClient.build_snapshot_transaction', return_value={
                    'data': '0x',
                    'nonce': 0,
                    'gas': 2000000,
                    'gasPrice': Web3.to_wei('300', 'gwei')
                }):
                    with patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr='0x471343c1ad3b358843b2079d8c5c1a0a5a86fe88382cdc67604b0209bbedf523')):
                        with patch('web3.eth.Eth.wait_for_transaction_receipt', return_value={'status': 1, 'logs': []}):
                            parent_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"

                            response = royalty_client.snapshot(parent_ip_id)
                            assert response is not None
                            assert 'txHash' in response
                            assert response['txHash'] == '471343c1ad3b358843b2079d8c5c1a0a5a86fe88382cdc67604b0209bbedf523'
                            assert 'snapshotId' in response
                            assert response['snapshotId'] == 2

def test_claimableRevenue_royaltyVaultIpId_error(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=False):
        parent_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
        account_address = account.address
        snapshot_id = 1
        token = "0xB132A6B7AE652c974EE1557A3521D53d18F6739f"

        with pytest.raises(ValueError, match=f"The IP with id {parent_ip_id} is not registered."):
            royalty_client.claimableRevenue(parent_ip_id, account_address, snapshot_id, token)

def test_claimableRevenue_royaltyVaultAddress_error(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=True):
        with patch.object(royalty_client.royalty_policy_lap_client, 'getRoyaltyData', return_value=[True, "0x", 1, ["0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"], [1]]):
            parent_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
            account_address = account.address
            snapshot_id = 1
            token = "0xB132A6B7AE652c974EE1557A3521D53d18F6739f"

            with pytest.raises(ValueError, match=f"The royalty vault IP with id {parent_ip_id} address is not set."):
                royalty_client.claimableRevenue(parent_ip_id, account_address, snapshot_id, token)

def test_claimableRevenue_success(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=True):
        with patch.object(royalty_client.royalty_policy_lap_client, 'getRoyaltyData', return_value=[True, "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c", 1, ["0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"], [1]]):
            with patch('story_protocol_python_sdk.abi.IpRoyaltyVaultImpl.IpRoyaltyVaultImpl_client.IpRoyaltyVaultImplClient.claimableRevenue', return_value=0):
                parent_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
                account_address = account.address
                snapshot_id = 1
                token = "0xB132A6B7AE652c974EE1557A3521D53d18F6739f"

                response = royalty_client.claimableRevenue(parent_ip_id, account_address, snapshot_id, token)
                assert response == 0

def test_claimRevenue_royaltyVaultIpId_error(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=False):
        parent_ip_id = "0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"
        ERC20 = "0xB132A6B7AE652c974EE1557A3521D53d18F6739f"
        snapshot_ids = [1, 2]

        with pytest.raises(ValueError, match=f"The IP with id {parent_ip_id} is not registered."):
            royalty_client.claimRevenue(snapshot_ids, parent_ip_id, ERC20)

def test_claimRevenue_royaltyVaultAddress_error(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=True):
        with patch.object(royalty_client.royalty_policy_lap_client, 'getRoyaltyData', return_value=[True, "0x", 1, ["0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"], [1]]):
            parent_ip_id = "0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"
            ERC20 = "0xB132A6B7AE652c974EE1557A3521D53d18F6739f"
            snapshot_ids = [1, 2]

            with pytest.raises(ValueError, match=f"The royalty vault IP with id {parent_ip_id} address is not set."):
                royalty_client.claimRevenue(snapshot_ids, parent_ip_id, ERC20)

def test_claimRevenue_success(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=True):
        with patch.object(royalty_client.royalty_policy_lap_client, 'getRoyaltyData', return_value=[True, "0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7", 1, ["0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"], [1]]):
            with patch.object(royalty_client, '_parseTxRevenueTokenClaimedEvent', return_value=0):
                with patch('story_protocol_python_sdk.abi.IpRoyaltyVaultImpl.IpRoyaltyVaultImpl_client.IpRoyaltyVaultImplClient.build_claimRevenueBySnapshotBatch_transaction', return_value={
                    'data': '0x',
                    'nonce': 0,
                    'gas': 2000000,
                    'gasPrice': Web3.to_wei('300', 'gwei')
                }):
                    with patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr='0x7065317271b179a2b4d47ff23b9b12ea50cdf668b892c8912cd7df71797b6561')):
                        with patch('web3.eth.Eth.wait_for_transaction_receipt', return_value={'status': 1, 'logs': []}):
                            parent_ip_id = "0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"
                            ERC20 = "0xB132A6B7AE652c974EE1557A3521D53d18F6739f"
                            snapshot_ids = [1, 2]

                            response = royalty_client.claimRevenue(snapshot_ids, parent_ip_id, ERC20)
                            assert response is not None
                            assert 'txHash' in response
                            assert response['txHash'] == '7065317271b179a2b4d47ff23b9b12ea50cdf668b892c8912cd7df71797b6561'
                            assert 'claimableToken' in response
                            assert response['claimableToken'] == 0

def test_payRoyaltyOnBehalf_receiverIpId_error(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=False):
        receiver_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
        payer_ip_id = "0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"
        ERC20 = "0xB132A6B7AE652c974EE1557A3521D53d18F6739f"
        amount = 1

        with pytest.raises(ValueError, match=f"The receiver IP with id {receiver_ip_id} is not registered."):
            royalty_client.payRoyaltyOnBehalf(receiver_ip_id, payer_ip_id, ERC20, amount)

def test_payRoyaltyOnBehalf_payerIpId_error(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', side_effect=[True, False]):
        receiver_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
        payer_ip_id = "0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"
        ERC20 = "0xB132A6B7AE652c974EE1557A3521D53d18F6739f"
        amount = 1

        with pytest.raises(ValueError, match=f"The payer IP with id {payer_ip_id} is not registered."):
            royalty_client.payRoyaltyOnBehalf(receiver_ip_id, payer_ip_id, ERC20, amount)

def test_payRoyaltyOnBehalf_success(royalty_client):
    with patch.object(royalty_client.ip_asset_registry_client, 'isRegistered', return_value=True):
        with patch('story_protocol_python_sdk.abi.RoyaltyModule.RoyaltyModule_client.RoyaltyModuleClient.build_payRoyaltyOnBehalf_transaction', return_value={
            'data': '0x',
            'nonce': 0,
            'gas': 2000000,
            'gasPrice': Web3.to_wei('300', 'gwei')
        }):
            with patch('web3.eth.Eth.send_raw_transaction', return_value=Web3.to_bytes(hexstr='0xbadf64f2c220e27407c4d2ccbc772fb72c7dc590ac25000dc316e4dc519fbfa2')):
                with patch('web3.eth.Eth.wait_for_transaction_receipt', return_value={'status': 1, 'logs': []}):
                    receiver_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
                    payer_ip_id = "0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"
                    ERC20 = "0xB132A6B7AE652c974EE1557A3521D53d18F6739f"
                    amount = 1

                    response = royalty_client.payRoyaltyOnBehalf(receiver_ip_id, payer_ip_id, ERC20, amount, tx_options={'wait_for_transaction': True})
                    assert response is not None
                    assert 'txHash' in response
                    assert response['txHash'] == 'badf64f2c220e27407c4d2ccbc772fb72c7dc590ac25000dc316e4dc519fbfa2'
