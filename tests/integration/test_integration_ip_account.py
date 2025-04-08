# tests/integration/test_integration_ip_account.py

import pytest
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_abi.abi import encode

from setup_for_integration import (
    web3,
    account, 
    story_client,
    get_token_id,
    mint_tokens,
    getBlockTimestamp,
    MockERC721,
    MockERC20,
    private_key
)

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

class TestSetIpMetadata:
    """Tests for setting IP metadata"""
    
    def test_set_ip_metadata(self, story_client):
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )

        response = story_client.IPAccount.setIpMetadata(
            ip_id=response['ipId'],
            metadata_uri="https://example.com",
            metadata_hash=web3.to_hex(web3.keccak(text="test-metadata-hash"))
        )

        assert response is not None, "Response is None, indicating the contract interaction failed."
        assert 'txHash' in response, "Response does not contain 'txHash'."
        assert response['txHash'] is not None, "'txHash' is None."
        assert isinstance(response['txHash'], str), "'txHash' is not a string."
        assert len(response['txHash']) > 0, "'txHash' is empty."

    def test_execute_with_sig_wrong_signer(self, story_client):
        """Test executeWithSig with a valid signature but wrong signer address."""
        # Register a new IP
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        register_response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )
        ip_id = register_response['ipId']
        
        # Set a valid deadline
        deadline = getBlockTimestamp(web3) + 100
        
        # Get the current state/nonce
        state = story_client.IPAccount.getIpAccountNonce(ip_id)
        
        # Prepare data for a simple operation
        data = "0x"
        
        # Prepare the expected state for signing
        execute_data = story_client.IPAccount.ip_account_client.contract.encode_abi(
            abi_element_identifier="execute",
            args=[
                story_client.IPAccount.access_controller_client.contract.address,
                0,
                data
            ]
        )
        
        expected_state = Web3.keccak(
            encode(
                ["bytes32", "bytes"],
                [state, Web3.to_bytes(hexstr=execute_data)]
            )
        )
        
        # Prepare the signature data
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
            "data": data,
            "nonce": expected_state,
            "deadline": deadline,
        }
        
        # Sign the message
        signable_message = encode_typed_data(domain_data, message_types, message_data)
        signed_message = Account.sign_message(signable_message, private_key)
        
        # Use a wrong signer address
        wrong_signer = "0x1234567890123456789012345678901234567890"
        
        # Execute with wrong signer
        with pytest.raises(Exception) as exc_info:
            story_client.IPAccount.executeWithSig(
                ip_id=ip_id,
                to=story_client.IPAccount.access_controller_client.contract.address,
                value=0,
                data=data,
                signer=wrong_signer,  # Wrong signer address
                deadline=deadline,
                signature=signed_message.signature
            )
        
        print(f"Exception type: {type(exc_info.value)}")
        print(f"Exception value: {exc_info.value}")
        print(f"Exception args: {exc_info.value.args if hasattr(exc_info.value, 'args') else 'No args'}")

        error_hex = '0x3fd60002'
        assert error_hex in str(exc_info.value), f"Expected error code {error_hex} for wrong signer"
    
    @pytest.mark.skip(reason="contract allows empty calls")
    def test_transfer_erc20_empty_tokens(self, story_client):
        """Test transferERC20 with empty tokens list."""
        # Register a new IP
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        register_response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )
        ip_id = register_response['ipId']
        
        # Try to transfer with empty tokens list
        with pytest.raises(Exception) as exc_info:
            story_client.IPAccount.transferERC20(
                ip_id=ip_id,
                tokens=[]  # Empty tokens list
       )
    
    def test_transfer_erc20_invalid_token_params(self, story_client):
        """Test transferERC20 with invalid token parameters."""
        # Register a new IP
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        register_response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )
        ip_id = register_response['ipId']
        
        # Test with missing address
        with pytest.raises(ValueError) as exc_info:
            story_client.IPAccount.transferERC20(
                ip_id=ip_id,
                tokens=[
                    {
                        # Missing 'address'
                        "target": story_client.account.address,
                        "amount": 1000000
                    }
                ]
            )
        assert "must include" in str(exc_info.value), "Error should mention missing parameter"
        
        # Test with missing target
        # with pytest.raises(ValueError) as exc_info:
        #     story_client.IPAccount
    

class TestTransferERC20:
    """Tests for transferring ERC20 tokens"""

    def test_transfer_erc20(self, story_client):
        """Test transferring ERC20 tokens"""
        token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
        response = story_client.IPAsset.register(
            nft_contract=MockERC721,
            token_id=token_id
        )
        ip_id = response['ipId']

        # 1. Query token balance of ipId and wallet before
        initial_erc20_balance_of_ip_id = story_client.Royalty.mock_erc20_client.balanceOf(
            account=ip_id
        )
        initial_erc20_balance_of_wallet = story_client.Royalty.mock_erc20_client.balanceOf(
            account=story_client.account.address
        )
        initial_wip_balance_of_ip_id = story_client.WIP.balanceOf(
            address=ip_id
        )
        initial_wip_balance_of_wallet = story_client.WIP.balanceOf(
            address=story_client.account.address
        )

        # 2. Transfer ERC20 tokens to the IP account
        amount_to_mint = 2000000  # Equivalent to 0.002 ether in wei
        mint_receipt = mint_tokens(
            erc20_contract_address=MockERC20,
            web3=story_client.web3,
            account=story_client.account,
            to_address=ip_id,
            amount=amount_to_mint
        )
        
        # 3. Transfer WIP to the IP account
        # First deposit (wrap) IP to WIP
        deposit_response = story_client.WIP.deposit(
            amount=1
        )
        
        # Then transfer WIP to the IP account
        response = story_client.WIP.transfer(
            to=ip_id,
            amount=1
        )

        # 4. Transfer tokens from IP account to wallet address
        response = story_client.IPAccount.transferERC20(
            ip_id=ip_id,
            tokens=[
                {
                    "address": story_client.WIP.wip_client.contract.address,
                    "target": story_client.account.address,
                    "amount": 1
                },
                {
                    "address": MockERC20,
                    "target": story_client.account.address,
                    "amount": 1000000  # Equivalent to 0.001 ether
                },
                {
                    "address": MockERC20,
                    "target": story_client.account.address,
                    "amount": 1000000  # Equivalent to 0.001 ether
                }
            ]
        )
        
        # 5. Query token balance of ipId and wallet address after transfer
        final_erc20_balance_of_ip_id = story_client.Royalty.mock_erc20_client.balanceOf(
            account=ip_id
        )
        final_wip_balance_of_ip_id = story_client.WIP.balanceOf(
            address=ip_id
        )
        final_erc20_balance_of_wallet = story_client.Royalty.mock_erc20_client.balanceOf(
            account=story_client.account.address
        )
        final_wip_balance_of_wallet = story_client.WIP.balanceOf(
            address=story_client.account.address
        )

        assert isinstance(response['txHash'], str) and response['txHash'] != ""
        assert final_erc20_balance_of_ip_id == initial_erc20_balance_of_ip_id
        assert final_wip_balance_of_ip_id == initial_wip_balance_of_ip_id
        assert final_erc20_balance_of_wallet == initial_erc20_balance_of_wallet + 2000000
        assert final_wip_balance_of_wallet == initial_wip_balance_of_wallet + 1
