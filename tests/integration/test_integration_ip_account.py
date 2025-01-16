# tests/integration/test_integration_ip_account.py

import os, json, sys
import pytest
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_abi.abi import encode

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from utils import get_token_id, get_story_client_in_devnet, MockERC721, getBlockTimestamp

load_dotenv(override=True)
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
    return get_story_client_in_devnet(web3, account)

def test_execute(story_client):
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)

    response = story_client.IPAsset.register(
        nft_contract=MockERC721,
        token_id=token_id
    )

    data = story_client.IPAccount.access_controller_client.contract.encode_abi(
        fn_name="setPermission", 
        args=[response['ipId'], 
              account.address, 
              "0x89630Ccf23277417FBdfd3076C702F5248267e78", 
              Web3.keccak(text="function setAll(address,string,bytes32,bytes32)")[:4], 
              1]
    )

    response = story_client.IPAccount.execute(
        to=story_client.IPAccount.access_controller_client.contract.address,
        value=0,
        ip_id=response['ipId'],
        data=data
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'txHash' in response, "Response does not contain 'txHash'."
    assert response['txHash'] is not None, "'txHash' is None."
    assert isinstance(response['txHash'], str), "'txHash' is not a string."
    assert len(response['txHash']) > 0, "'txHash' is empty."

def test_executeWithSig(story_client):
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)

    response = story_client.IPAsset.register(
        nft_contract=MockERC721,
        token_id=token_id
    )

    ipId = response['ipId']

    deadline = getBlockTimestamp(web3) + 100
    state = story_client.IPAccount.getIpAccountNonce(ipId)

    # Step 1: Encode the core data for `setPermission`
    core_data = story_client.IPAccount.access_controller_client.contract.encode_abi(
        fn_name="setPermission",
        args=[
            ipId,
            account.address,
            "0x6E81a25C99C6e8430aeC7353325EB138aFE5DC16",  # Module address
            Web3.keccak(text="function setAll(address,string,bytes32,bytes32)")[:4],  # Selector
            1  # ALLOW
        ]
    )

    # Step 2: Encode the `execute` function data
    execute_data = story_client.IPAccount.ip_account_client.contract.encode_abi(
        fn_name="execute",
        args=[
            story_client.IPAccount.access_controller_client.contract.address,  # `to`
            0,  # `value`
            core_data  # Encoded `setPermission` data
        ]
    )

    # Step 3: Compute the expected state (nonce)
    expected_state = Web3.keccak(
        encode(
            ["bytes32", "bytes"],
            [
                state,  # Current state (nonce)
                Web3.to_bytes(hexstr=execute_data)  # Convert hex string to bytes
            ]
        )
    )

    # Step 4: Define EIP-712 domain and message
    domain_data = {
        "name": "Story Protocol IP Account",
        "version": "1",
        "chainId": 1315,
        "verifyingContract": ipId,
    }

    message_types = {
        "Execute": [
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "data", "type": "bytes"},
            {"name": "nonce", "type": "bytes32"},
            {"name": "deadline", "type": "uint256"},
        ],
    }

    message_data = {
        "to": story_client.IPAccount.access_controller_client.contract.address,
        "value": 0,
        "data": core_data,  # Pass the raw `setPermission` encoded data
        "nonce": expected_state,
        "deadline": deadline,
    }

    # Step 5: Create and sign the EIP-712 message
    signable_message = encode_typed_data(domain_data, message_types, message_data)
    signed_message = Account.sign_message(signable_message, private_key)

    # Step 6: Call `executeWithSig`
    response = story_client.IPAccount.executeWithSig(
        to=story_client.IPAccount.access_controller_client.contract.address,
        value=0,
        ip_id=ipId,
        data=core_data,
        signer=account.address,
        deadline=deadline,
        signature=signed_message.signature
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'txHash' in response, "Response does not contain 'txHash'."
    assert response['txHash'] is not None, "'txHash' is None."
    assert isinstance(response['txHash'], str), "'txHash' is not a string."
    assert len(response['txHash']) > 0, "'txHash' is empty."
