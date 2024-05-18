# tests/integration/test_integration_ip_asset.py

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

from utils import get_token_id, get_story_client_in_sepolia, MockERC721

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

# def test_register_ip_asset(story_client):
#     token_id = get_token_id(MockERC721, story_client.web3, story_client.account)

#     response = story_client.IPAsset.register(
#         token_contract=MockERC721,
#         token_id=token_id
#     )

#     assert response is not None
#     assert 'ipId' in response
#     assert response['ipId'] is not None

#     # print(response['ipId'])

def test_registerDerivative(story_client):
    parent_token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
    
    parent_ip_response = story_client.IPAsset.register(
        token_contract=MockERC721,
        token_id=parent_token_id
    )
    assert parent_ip_response is not None
    assert 'ipId' in parent_ip_response
    assert parent_ip_response['ipId'] is not None
    parent_ip_id = parent_ip_response['ipId']
    
    # Attach license terms to parent IP
    license_template = "0x260B6CB6284c89dbE660c0004233f7bB99B5edE7"  # Replace with actual license template address
    no_commercial_license_terms_id = 2  # Replace with actual license terms ID

    attach_license_response = story_client.License.attachLicenseTerms(
        ip_id=parent_ip_id,
        license_template=license_template,
        license_terms_id=no_commercial_license_terms_id
    )
    assert attach_license_response is not None
    assert 'txHash' in attach_license_response
    assert attach_license_response['txHash'] is not None

    child_token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
    
    child_ip_response = story_client.IPAsset.register(
        token_contract=MockERC721,
        token_id=child_token_id
    )
    child_ip_id = child_ip_response['ipId']  # Replace with actual child IP ID

    # Register derivative IP
    response = story_client.IPAsset.registerDerivative(
        child_ip_id=child_ip_id,
        parent_ip_ids=[parent_ip_id],
        license_terms_ids=[no_commercial_license_terms_id],
        license_template=license_template
    )
    
    assert response is not None
    assert 'txHash' in response
    assert response['txHash'] is not None
    assert isinstance(response['txHash'], str)
    assert len(response['txHash']) > 0
