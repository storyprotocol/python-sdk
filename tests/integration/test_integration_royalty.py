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
    
from utils import get_story_client_in_sepolia, mint_tokens, approve, MockERC721, get_token_id, MockERC20

load_dotenv()
private_key = os.getenv('WALLET_PRIVATE_KEY')
rpc_url = os.getenv('RPC_PROVIDER_URL')

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(rpc_url))
if not web3.is_connected():
    raise Exception("Failed to connect to Web3 provider")

# Set up the account with the private key
account = web3.eth.account.from_key(private_key)

@pytest.fixture(scope="module")
def story_client():
    return get_story_client_in_sepolia(web3, account)

@pytest.fixture(scope="module")
def parent_ip_id(story_client):
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)

    parent_ip_response = story_client.IPAsset.register(
        token_contract=MockERC721,
        token_id=token_id
    )

    parent_ip_id = parent_ip_response['ipId']

    return parent_ip_id

@pytest.fixture(scope="module")
def child_ip_id(story_client):
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)

    response = story_client.IPAsset.register(
        token_contract=MockERC721,
        token_id=token_id
    )

    return response['ipId']

@pytest.fixture(scope="module")
def attach_and_register(story_client, parent_ip_id, child_ip_id):
    license_terms_response = story_client.License.registerCommercialRemixPIL(
        minting_fee=1,
        currency=MockERC20,
        commercial_rev_share=10,
        royalty_policy="0x1E1cBd300d351354EB17360a3769F23B18bbB77D"
    )

    attach_license_response = story_client.License.attachLicenseTerms(
        ip_id=parent_ip_id,
        license_template="0xB9bfC97d3b0b1333e079fb392F786a743d14Be56",
        license_terms_id=license_terms_response['licenseTermsId']
    )

    derivative_response = story_client.IPAsset.registerDerivative(
        child_ip_id=child_ip_id,
        parent_ip_ids=[parent_ip_id],
        license_terms_ids=[license_terms_response['licenseTermsId']],
        license_template="0xB9bfC97d3b0b1333e079fb392F786a743d14Be56"
    )

def test_collectRoyaltyTokens(story_client, parent_ip_id, child_ip_id, attach_and_register):
    response = story_client.Royalty.collectRoyaltyTokens(
        parent_ip_id=parent_ip_id,
        child_ip_id=child_ip_id
    )
    
    assert response is not None

    assert 'txHash' in response
    assert response['txHash'] is not None
    assert isinstance(response['txHash'], str)
    assert len(response['txHash']) > 0

    assert 'royaltyTokensCollected' in response
    assert response['royaltyTokensCollected'] is not None
    assert isinstance(response['royaltyTokensCollected'], int)

@pytest.fixture(scope="module")
def snapshot_id(story_client, child_ip_id):
    response = story_client.Royalty.snapshot(
        child_ip_id=child_ip_id
    )

    assert response is not None
    assert 'txHash' in response
    assert response['txHash'] is not None
    assert isinstance(response['txHash'], str)
    assert len(response['txHash']) > 0

    assert 'snapshotId' in response
    assert response['snapshotId'] is not None
    assert isinstance(response['snapshotId'], int)
    assert response['snapshotId'] >= 0

    return response['snapshotId']

def test_snapshot(story_client, snapshot_id):
    assert snapshot_id is not None

# def test_claimableRevenue(story_client, child_ip_id, snapshot_id):
#     response = story_client.Royalty.claimableRevenue(
#         child_ip_id=child_ip_id,
#         account_address=account.address,
#         snapshot_id=snapshot_id,
#         token=MockERC20
#     )

#     assert response is not None
#     assert isinstance(response, int)
#     assert response >= 0

# def test_payRoyaltyOnBehalf(story_client, parent_ip_id, child_ip_id):
#     token_ids = mint_tokens(
#         erc20_contract_address=MockERC20, 
#         web3=web3, 
#         account=account, 
#         to_address=account.address, 
#         amount=100000 * 10 ** 6
#     )
    
#     receipt = approve(
#         erc20_contract_address=MockERC20, 
#         web3=web3, 
#         account=account, 
#         spender_address="0x1E1cBd300d351354EB17360a3769F23B18bbB77D", 
#         amount=100000 * 10 ** 6)

#     response = story_client.Royalty.payRoyaltyOnBehalf(
#         receiver_ip_id=parent_ip_id,
#         payer_ip_id=child_ip_id,
#         token=MockERC20,
#         amount=10
#     )

#     assert response is not None
#     assert 'txHash' in response
#     assert response['txHash'] is not None
#     assert isinstance(response['txHash'], str)
#     assert len(response['txHash']) > 0

# def test_claimRevenue(story_client, child_ip_id, snapshot_id):
#     response = story_client.Royalty.claimRevenue(
#         snapshot_ids=[snapshot_id],
#         child_ip_id=child_ip_id,
#         token=MockERC20,
#     )

#     assert response is not None
#     assert 'txHash' in response
#     assert response['txHash'] is not None
#     assert isinstance(response['txHash'], str)
#     assert len(response['txHash']) > 0

#     assert 'claimableToken' in response
#     assert response['claimableToken'] is not None
#     assert isinstance(response['claimableToken'], int)
#     assert response['claimableToken'] >= 0