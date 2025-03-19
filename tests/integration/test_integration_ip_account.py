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

class TestBasicIPAccountOperations:
    """Basic IP Account operations like execute and nonce retrieval"""
    
    def test_execute(self, story_client):
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )

        data = story_client.IPAccount.access_controller_client.contract.encode_abi(
            abi_element_identifier="setTransientPermission", 
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

    def test_get_ip_account_nonce(self, story_client):
        """Test getting IP Account nonce."""
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        register_response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )
        ip_id = register_response['ipId']
        
        state = story_client.IPAccount.getIpAccountNonce(ip_id)
        
        assert state is not None
        assert isinstance(state, bytes)

    def test_execute_with_encoded_data(self, story_client):
        """Test execute with pre-encoded function data."""
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        register_response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )
        ip_id = register_response['ipId']

        data = story_client.IPAccount.access_controller_client.contract.encode_abi(
            abi_element_identifier="setTransientPermission", 
            args=[
                ip_id,
                account.address, 
                "0x89630Ccf23277417FBdfd3076C702F5248267e78",
                Web3.keccak(text="function execute(address,uint256,bytes,uint8)")[:4],
                1
            ]
        )

        response = story_client.IPAccount.execute(
            to=story_client.IPAccount.access_controller_client.contract.address,
            value=0,
            ip_id=ip_id,
            data=data
        )

        assert response is not None
        assert 'txHash' in response
        assert isinstance(response['txHash'], str)
        assert len(response['txHash']) > 0

class TestSignatureOperations:
    """Tests for operations involving signatures"""
    
    def test_executeWithSig(self, story_client):
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )

        ipId = response['ipId']
        deadline = getBlockTimestamp(web3) + 100
        state = story_client.IPAccount.getIpAccountNonce(ipId)

        core_data = story_client.IPAccount.access_controller_client.contract.encode_abi(
            abi_element_identifier="setTransientPermission",
            args=[
                ipId,
                account.address,
                "0x6E81a25C99C6e8430aeC7353325EB138aFE5DC16",
                Web3.keccak(text="function setAll(address,string,bytes32,bytes32)")[:4],
                1
            ]
        )

        execute_data = story_client.IPAccount.ip_account_client.contract.encode_abi(
            abi_element_identifier="execute",
            args=[
                story_client.IPAccount.access_controller_client.contract.address,
                0,
                core_data
            ]
        )

        expected_state = Web3.keccak(
            encode(
                ["bytes32", "bytes"],
                [state, Web3.to_bytes(hexstr=execute_data)]
            )
        )

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
            "data": core_data,
            "nonce": expected_state,
            "deadline": deadline,
        }

        signable_message = encode_typed_data(domain_data, message_types, message_data)
        signed_message = Account.sign_message(signable_message, private_key)

        response = story_client.IPAccount.executeWithSig(
            to=story_client.IPAccount.access_controller_client.contract.address,
            value=0,
            ip_id=ipId,
            data=core_data,
            signer=account.address,
            deadline=deadline,
            signature=signed_message.signature
        )

        assert response is not None
        assert 'txHash' in response
        assert isinstance(response['txHash'], str)
        assert len(response['txHash']) > 0

    def test_execute_with_sig_multiple_permissions(self, story_client):
        """Test executeWithSig setting multiple permissions."""
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        register_response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )
        ip_id = register_response['ipId']

        deadline = getBlockTimestamp(web3) + 100
        state = story_client.IPAccount.getIpAccountNonce(ip_id)

        # Prepare all function signatures for permissions
        function_signatures = [
            "function setAll(address,string,bytes32,bytes32)",
            "function execute(address,uint256,bytes,uint8)",
            "function registerDerivative(address,address[],uint256[],address,bytes)"
        ]
        
        # Create individual permission data and combine them
        calls_data = []
        for func_sig in function_signatures:
            data = story_client.IPAccount.access_controller_client.contract.encode_abi(
                abi_element_identifier="setTransientPermission",
                args=[
                    ip_id,
                    account.address,
                    "0x6E81a25C99C6e8430aeC7353325EB138aFE5DC16",
                    Web3.keccak(text=func_sig)[:4],
                    1
                ]
            )
            if data.startswith('0x'):
                data = data[2:]
            calls_data.append(data)

        # Combine all encoded data
        combined_data = '0x' + ''.join(calls_data)

        # Create the execute data that would be signed
        execute_data = story_client.IPAccount.ip_account_client.contract.encode_abi(
            abi_element_identifier="execute",
            args=[
                story_client.IPAccount.access_controller_client.contract.address,
                0,
                combined_data
            ]
        )

        # Calculate the expected state
        expected_state = Web3.keccak(
            encode(
                ["bytes32", "bytes"],
                [state, Web3.to_bytes(hexstr=execute_data)]
            )
        )

        # Prepare signature data
        domain_data = {
            "name": "Story Protocol IP Account",
            "version": "1",
            "chainId": 1315,
            "verifyingContract": ip_id,
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
            "data": combined_data,
            "nonce": expected_state,
            "deadline": deadline,
        }

        signable_message = encode_typed_data(domain_data, message_types, message_data)
        signed_message = Account.sign_message(signable_message, private_key)

        response = story_client.IPAccount.executeWithSig(
            ip_id=ip_id,
            to=story_client.IPAccount.access_controller_client.contract.address,
            value=0,
            data=combined_data,
            signer=account.address,
            deadline=deadline,
            signature=signed_message.signature
        )

        assert response is not None
        assert 'txHash' in response
        assert isinstance(response['txHash'], str)
        assert len(response['txHash']) > 0

class TestErrorCases:
    """Tests for error cases and validation"""
    
    def test_execute_invalid_address(self, story_client):
        """Test execute with invalid address should raise error."""
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        register_response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )
        ip_id = register_response['ipId']

        data = "0x"
        invalid_address = "0xinvalid"
        
        with pytest.raises(ValueError) as exc_info:
            story_client.IPAccount.execute(
                to=invalid_address,
                value=0,
                ip_id=ip_id,
                data=data
            )
        
        assert "is not a valid address" in str(exc_info.value)

    def test_execute_unregistered_ip(self, story_client):
        """Test execute with unregistered IP should raise error."""
        unregistered_ip = "0x1234567890123456789012345678901234567890"
        data = "0x"
        
        with pytest.raises(ValueError) as exc_info:
            story_client.IPAccount.execute(
                to=story_client.IPAccount.access_controller_client.contract.address,
                value=0,
                ip_id=unregistered_ip,
                data=data
            )
        
        assert "is not registered" in str(exc_info.value)