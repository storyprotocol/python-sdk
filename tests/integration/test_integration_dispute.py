import pytest
from web3 import Web3

from setup_for_integration import (
    web3,
    account,
    account_2,
    story_client,
    story_client_2,
    get_token_id,
    mint_tokens,
    approve,
    getBlockTimestamp,
    check_event_in_tx,
    MockERC721,
    MockERC20,
    ZERO_ADDRESS,
    ARBITRATION_POLICY_UMA,
    generate_cid
)

@pytest.fixture(scope="module")
def target_ip_id(story_client_2):
    """Create an IP to be disputed"""
    token_id = get_token_id(MockERC721, story_client_2.web3, story_client_2.account)
    
    response = story_client_2.IPAsset.register(
        nft_contract=MockERC721,
        token_id=token_id
    )

    return response['ipId']

@pytest.fixture(scope="module")
def dispute_id(story_client, target_ip_id):
    """Create a dispute and return its ID"""

    cid = generate_cid()

    response = story_client.Dispute.raise_dispute(
        target_ip_id=target_ip_id,
        target_tag="IMPROPER_REGISTRATION",
        cid=cid,
        liveness=2592000,  # 30 days in seconds
        bond=0,
        tx_options={"wait_for_transaction": True}
    )
    
    assert 'txHash' in response
    assert isinstance(response['txHash'], str)
    assert 'disputeId' in response
    assert isinstance(response['disputeId'], int)
    return response['disputeId']

def test_raise_dispute(story_client, dispute_id):
    """Test raising a dispute"""
    assert dispute_id is not None
    assert isinstance(dispute_id, int)
    assert dispute_id > 0

# def test_raise_dispute_with_bond(story_client, target_ip_id):
#     """Test raising a dispute with a bond amount"""
#     # Approve tokens first
#     approve(story_client.account, ARBITRATION_POLICY_UMA)
    
#     response = story_client.Dispute.raise_dispute(
#         target_ip_id=target_ip_id,
#         target_tag="IMPROPER_REGISTRATION",
#         cid="QmX4zdp8VpzqvtKuEqMo6gfZPdoUx9TeHXCgzKLcFfSUbk",
#         liveness=2592000,
#         bond=1000000,  # Use a valid bond amount
#         tx_options={"wait_for_transaction": True}
#     )
    
#     assert 'txHash' in response
#     assert isinstance(response['txHash'], str)
#     assert len(response['txHash']) > 0
#     assert 'disputeId' in response
#     assert isinstance(response['disputeId'], int)
