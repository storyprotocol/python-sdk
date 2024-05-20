# tests/integration/test_integration_royalty.py

import os
import sys
import pytest
from dotenv import load_dotenv
from web3 import Web3

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from utils import get_story_client_in_sepolia

load_dotenv()
private_key = os.getenv('WALLET_PRIVATE_KEY')
rpc_url = os.getenv('RPC_PROVIDER_URL')

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(rpc_url))
if not web3.is_connected():
    raise Exception("Failed to connect to Web3 provider")

# Set up the account with the private key
account = web3.eth.account.from_key(private_key)

@pytest.fixture
def story_client():
    return get_story_client_in_sepolia(web3, account)

#Ip id 1: 0xB24cB00a5d9cf2AdB2f6D5B22D479C90F5204c45
#Ip id 2: 0x99da6cc55f15Fa6dAe239C868877CB5D8Fc6Be05

#ip id with royalty policy: 0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c
# ip id royalty vault: 0x2626D54671c366e29682c94a2125452Ef3F401D2

#license term: 2
#attached done
# register derivative done


# def test_collectRoyaltyTokens(story_client): #can only run each child ip id once
#     # Register derivative IP
#     response = story_client.Royalty.collectRoyaltyTokens(
#         parent_ip_id="0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c",
#         child_ip_id="0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"
#     )
    
#     assert response is not None

#     assert 'txHash' in response
#     assert response['txHash'] is not None
#     assert isinstance(response['txHash'], str)
#     assert len(response['txHash']) > 0

#     assert 'royaltyTokensCollected' in response
#     assert response['royaltyTokensCollected'] is not None
#     assert isinstance(response['royaltyTokensCollected'], int)

def test_snapshot(story_client):
    # Define the parameters for the snapshot method
    child_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"  # Example child IP ID

    # Call the snapshot method
    response = story_client.Royalty.snapshot(
        child_ip_id=child_ip_id
    )

    # Verify the response
    assert response is not None
    assert 'txHash' in response
    assert response['txHash'] is not None
    assert isinstance(response['txHash'], str)
    assert len(response['txHash']) > 0

    assert 'snapshotId' in response
    assert response['snapshotId'] is not None
    assert isinstance(response['snapshotId'], int)
    assert response['snapshotId'] >= 0  # Assuming snapshotId is a non-negative integer

def test_claimableRevenue(story_client):
    # Define the parameters for the claimableRevenue method
    child_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"  # Example royalty vault IP ID
    account_address = account.address  # Use the test account address
    snapshot_id = 1  # Example snapshot ID
    token = "0xB132A6B7AE652c974EE1557A3521D53d18F6739f"  # Replace with the actual token address

    # Call the claimableRevenue method
    response = story_client.Royalty.claimableRevenue(
        child_ip_id=child_ip_id,
        account_address=account_address,
        snapshot_id=snapshot_id,
        token=token
    )
    print("It came out to,", response)
    # Verify the response
    assert response is not None
    assert isinstance(response, int)
    assert response >= 0  # Assuming the claimable revenue can be zero or positive