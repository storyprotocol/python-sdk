# tests/integration/test_integration_ip_account.py

import os, json, sys
import pytest
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_typed_data

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from utils import get_token_id, get_story_client_in_sepolia, MockERC721, getBlockTimestamp

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

def test_execute(story_client):
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'story_protocol_python_sdk', 'scripts', 'config.json'))
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    contract_address = None
    for contract in config['contracts']:
        if contract['contract_name'] == 'AccessController':
            contract_address = contract['contract_address']
            break
    if not contract_address:
        raise ValueError(f"Contract address for AccessController not found in config.json")
    abi_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'story_protocol_python_sdk', 'abi', 'AccessController', 'AccessController.json'))
    with open(abi_path, 'r') as abi_file:
        abi = json.load(abi_file)

    contract = web3.eth.contract(address=contract_address, abi=abi)

    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)

    response = story_client.IPAsset.register(
        token_contract=MockERC721,
        token_id=token_id
    )

    data = contract.encode_abi(
        fn_name="setPermission", 
        args=[response['ipId'], 
              account.address, 
              "0x2ac240293f12032E103458451dE8A8096c5A72E8", 
              "0x00000000", 
              1]
    )

    response = story_client.IPAccount.execute(
        to=contract_address,
        value=0,
        account_address=response['ipId'],
        data=data
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'txHash' in response, "Response does not contain 'txHash'."
    assert response['txHash'] is not None, "'txHash' is None."
    assert isinstance(response['txHash'], str), "'txHash' is not a string."
    assert len(response['txHash']) > 0, "'txHash' is empty."

def test_executeWithSig(story_client):
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'story_protocol_python_sdk', 'scripts', 'config.json'))
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    contract_address = None
    for contract in config['contracts']:
        if contract['contract_name'] == 'AccessController':
            contract_address = contract['contract_address']
            break
    if not contract_address:
        raise ValueError(f"Contract address for AccessController not found in config.json")
    abi_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'story_protocol_python_sdk', 'abi', 'AccessController', 'AccessController.json'))
    with open(abi_path, 'r') as abi_file:
        abi = json.load(abi_file)

    contract = web3.eth.contract(address=contract_address, abi=abi)

    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)

    response = story_client.IPAsset.register(
        token_contract=MockERC721,
        token_id=token_id
    )
    # response={'ipId': "0x33633A1C01E30618244e5877A4F3E1c85dFa4CCa"}
    ipId = response['ipId']

    data = contract.encode_abi(
        fn_name="setPermission", 
        args=[ipId, 
              account.address, 
              "0x2ac240293f12032E103458451dE8A8096c5A72E8", 
              "0x00000000", 
              1]
    )
    deadline = getBlockTimestamp(web3) + 100
    state = story_client.IPAccount.getIpAccountNonce(ipId)
    expectedState = state + 1
    print("State is: ", state)
    print("Expected state is: ", expectedState)
    
    # Define the domain data
    domain_data = {
        "name": "Story Protocol IP Account",
        "version": "1",
        "chainId": 11155111,
        "verifyingContract": ipId,
    }

    # Define the custom types
    message_types = {
        "Execute": [
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "data", "type": "bytes"},
            {"name": "nonce", "type": "uint256"},
            {"name": "deadline", "type": "uint256"},
        ],
    }

    # Define the message data
    message_data = {
        "to": contract_address,
        "value": 0,
        "data": data,  # Replace with the actual data
        "nonce": expectedState,  # Replace with the actual nonce
        "deadline": deadline,  # Replace with the actual deadline
    }

    # Encode the typed data
    signable_message = encode_typed_data(domain_data, message_types, message_data)
    signed_message = Account.sign_message(signable_message, private_key)

    print("Signed message: ", signed_message)
    print("Signature: ", signed_message.signature)

    response = story_client.IPAccount.executeWithSig(
        to=contract_address,
        value=0,
        account_address=ipId,
        data=data,
        signer=account.address,
        deadline=deadline,
        signature=signed_message.signature
    )

    assert response is not None, "Response is None, indicating the contract interaction failed."
    assert 'txHash' in response, "Response does not contain 'txHash'."
    assert response['txHash'] is not None, "'txHash' is None."
    assert isinstance(response['txHash'], str), "'txHash' is not a string."
    assert len(response['txHash']) > 0, "'txHash' is empty."

