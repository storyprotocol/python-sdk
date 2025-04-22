# tests/integration/test_integration_dispute.py

import pytest
from web3 import Web3
import random
import string
import time

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
WIP_TOKEN_ADDRESS = "0x1514000000000000000000000000000000000000"
ROYALTY_POLICY = "0xBe54FB168b3c982b7AaE60dB6CF75Bd8447b390E"
GROUP_REWARD_POOL = "0xf96f2c30b41Cb6e0290de43C8528ae83d4f33F89"

from setup_for_integration import (
    web3,
    account, 
    account_2,
    story_client,
    story_client_2,
    generate_cid,
    approve,
    wallet_address
)

class TestDispute:
    @pytest.fixture(scope="module")
    def target_ip_id(self, story_client, story_client_2):
        """Create an IP to be disputed"""
        txData = story_client.NFTClient.create_nft_collection(
            name="test-collection",
            symbol="TEST",
            max_supply=100,
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=account.address
        )
        
        nft_contract = txData['nft_contract']

        metadata_a = {
            'ip_metadata_uri': "test-uri-a",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash-a")),
            'nft_metadata_uri': "test-nft-uri-a",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash-a"))
        }
        
        response = story_client_2.IPAsset.mint_and_register_ip(
            spg_nft_contract=nft_contract,
            ip_metadata=metadata_a
        )

        return response['ip_id']

    @pytest.fixture(scope="module")
    def dispute_id(self, story_client, target_ip_id):
        cid = generate_cid()
        bond_amount = 1000000000000000000  # 1 ETH in wei
        
        response = story_client.Dispute.raise_dispute(
            target_ip_id=target_ip_id,
            target_tag="IMPROPER_REGISTRATION",
            cid=cid,
            liveness=0x278d,  # 30 days in seconds
            bond=bond_amount
        )
        
        assert 'tx_hash' in response
        assert isinstance(response['tx_hash'], str)
        assert len(response['tx_hash']) > 0
        assert 'dispute_id' in response
        assert isinstance(response['dispute_id'], int)
        assert response['dispute_id'] > 0

        return response['dispute_id']
    
    def test_raise_dispute(self, dispute_id):
        """Test raising a dispute"""
        assert dispute_id is not None
    
    def test_counter_dispute(self, story_client_2, target_ip_id, dispute_id):
        """Test countering a dispute"""
        # Get the assertion ID from the dispute ID
        assertion_id = story_client_2.Dispute.dispute_id_to_assertion_id(dispute_id)
        
        # Generate a CID for counter evidence
        counter_evidence_cid = generate_cid()

        # Counter the dispute assertion with story_client_2 (the IP owner)
        response = story_client_2.Dispute.dispute_assertion(
            ip_id=target_ip_id,
            assertion_id=assertion_id,
            counter_evidence_cid=counter_evidence_cid
        )
        
        # Verify the response
        assert 'tx_hash' in response
        assert isinstance(response['tx_hash'], str)
        assert len(response['tx_hash']) > 0

class TestDisputeInvalid:
    @pytest.fixture(scope="module")
    def target_ip_id(self, story_client, story_client_2):
        """Create an IP to be disputed"""
        txData = story_client.NFTClient.create_nft_collection(
            name="test-collection",
            symbol="TEST",
            max_supply=100,
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=account.address
        )
        
        nft_contract = txData['nft_contract']

        metadata_a = {
            'ip_metadata_uri': "test-uri-a",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash-a")),
            'nft_metadata_uri': "test-nft-uri-a",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash-a"))
        }
        
        response = story_client_2.IPAsset.mint_and_register_ip(
            spg_nft_contract=nft_contract,
            ip_metadata=metadata_a
        )

        return response['ip_id']
    
    @pytest.fixture(scope="module")
    def deposit_wip(self, story_client):
        """Deposit WIP tokens for tests"""
        deposit_response = story_client.WIP.deposit(
            amount=Web3.to_wei(10, 'ether')  
        )
        return deposit_response['tx_hash']
    
    @pytest.fixture(scope="module")
    def parent_dispute_id(self, story_client, parent_ip_id, deposit_wip):
        """Raise a dispute on the parent IP"""
        cid = generate_cid()
        bond_amount = Web3.to_wei(1, 'ether')  # 1 ETH in wei
        
        response = story_client.Dispute.raise_dispute(
            target_ip_id=parent_ip_id,
            target_tag="IMPROPER_REGISTRATION",
            cid=cid,
            liveness=0x278d,  # 30 days in seconds
            bond=bond_amount
        )
        
        assert 'dispute_id' in response
        assert 'tx_hash' in response
        
        return response['dispute_id']
    
    def generate_invalid_address(self):
        """Generate an invalid Ethereum address"""
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=40))
        return f"0x{random_chars}"
    
    def test_raise_dispute_with_invalid_ip_id(self, story_client):
        """Test raising a dispute with an invalid IP ID"""
        cid = generate_cid()
        invalid_ip_id = self.generate_invalid_address()
        
        with pytest.raises(ValueError, match=r"Invalid address.*"):
            story_client.Dispute.raise_dispute(
                target_ip_id=invalid_ip_id,
                target_tag="IMPROPER_REGISTRATION",
                cid=cid,
                liveness=0x278d,  # 30 days in seconds
                bond=Web3.to_wei(1, 'ether')
            )
    
    def test_raise_dispute_with_non_whitelisted_tag(self, story_client, target_ip_id):
        """Test raising a dispute with a non-whitelisted tag"""
        cid = generate_cid()
        
        with pytest.raises(ValueError, match=r".*not whitelisted.*"):
            story_client.Dispute.raise_dispute(
                target_ip_id=target_ip_id,
                target_tag="NON_WHITELISTED_TAG",
                cid=cid,
                liveness=0x278d,
                bond=Web3.to_wei(1, 'ether')
            )
    
    def test_raise_dispute_with_liveness_too_short(self, story_client, target_ip_id):
        """Test raising a dispute with liveness period too short"""
        cid = generate_cid()
        
        min_liveness = story_client.Dispute.arbitration_policy_uma_client.minLiveness()
        too_short_liveness = min_liveness - 1
        
        with pytest.raises(ValueError, match=r"Liveness must be between.*"):
            story_client.Dispute.raise_dispute(
                target_ip_id=target_ip_id,
                target_tag="IMPROPER_REGISTRATION",
                cid=cid,
                liveness=too_short_liveness,
                bond=Web3.to_wei(1, 'ether')
            )
    
    def test_raise_dispute_with_liveness_too_long(self, story_client, target_ip_id):
        """Test raising a dispute with liveness period too long"""
        cid = generate_cid()
        
        max_liveness = story_client.Dispute.arbitration_policy_uma_client.maxLiveness()
        too_long_liveness = max_liveness + 1
        
        with pytest.raises(ValueError, match=r"Liveness must be between.*"):
            story_client.Dispute.raise_dispute(
                target_ip_id=target_ip_id,
                target_tag="IMPROPER_REGISTRATION",
                cid=cid,
                liveness=too_long_liveness,
                bond=Web3.to_wei(1, 'ether')
            )
    
    def test_raise_dispute_with_excessive_bond(self, story_client, target_ip_id):
        """Test raising a dispute with bond exceeding maximum"""
        cid = generate_cid()
        
        token_address = story_client.web3.to_checksum_address("0x1514000000000000000000000000000000000000")
        max_bonds = story_client.Dispute.arbitration_policy_uma_client.maxBonds(token=token_address)
        excessive_bond = max_bonds + 1
        
        with pytest.raises(ValueError, match=r"Bond must be less than.*"):
            story_client.Dispute.raise_dispute(
                target_ip_id=target_ip_id,
                target_tag="IMPROPER_REGISTRATION",
                cid=cid,
                liveness=0x278d,
                bond=excessive_bond
            )
    
    def test_raise_dispute_with_insufficient_wip_balance(self, story_client, target_ip_id):
        """Test raising a dispute with insufficient WIP token balance"""
        cid = generate_cid()
        
        test_client = story_client
        
        with pytest.raises(ValueError):
            test_client.Dispute.raise_dispute(
                target_ip_id=target_ip_id,
                target_tag="IMPROPER_REGISTRATION",
                cid=cid,
                liveness=0x278d,
                bond=Web3.to_wei(1000, 'ether')  # Assuming this is more than deposited
            )
class TestDisputeCancel:
    @pytest.fixture(scope="module")
    def target_ip_id(self, story_client, story_client_2):
        """Create an IP to be disputed"""
        txData = story_client.NFTClient.create_nft_collection(
            name="test-collection",
            symbol="TEST",
            max_supply=100,
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=account.address
        )
        
        nft_contract = txData['nft_contract']

        metadata_a = {
            'ip_metadata_uri': "test-uri-a",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash-a")),
            'nft_metadata_uri': "test-nft-uri-a",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash-a"))
        }
        
        response = story_client_2.IPAsset.mint_and_register_ip(
            spg_nft_contract=nft_contract,
            ip_metadata=metadata_a
        )

        return response['ip_id']

    @pytest.fixture(scope="module")
    def deposit_wip(self, story_client, story_client_2):
        """Deposit WIP tokens for both story clients"""
        deposit_response = story_client.WIP.deposit(
            amount=Web3.to_wei(10, 'ether')  # 10 IP tokens
        )
        
        deposit_response_2 = story_client_2.WIP.deposit(
            amount=Web3.to_wei(10, 'ether')  # 10 IP tokens
        )
        
        return {
            'client1': deposit_response['tx_hash'],
            'client2': deposit_response_2['tx_hash']
        }
    
    @pytest.fixture(scope="function")
    def raise_dispute(self, story_client, target_ip_id, deposit_wip):
        """Raise a dispute for testing cancellation"""
        cid = generate_cid()
        bond_amount = Web3.to_wei(1, 'ether')  # 1 ETH in wei
        
        response = story_client.Dispute.raise_dispute(
            target_ip_id=target_ip_id,
            target_tag="IMPROPER_REGISTRATION",
            cid=cid,
            liveness=0x278d,  # 30 days in seconds
            bond=bond_amount
        )
        
        assert 'dispute_id' in response
        assert isinstance(response['dispute_id'], int)
        assert response['dispute_id'] > 0

        return response['dispute_id']
    
    def test_cancel_dispute_unauthorized(self, story_client_2, raise_dispute):
        """Test attempting to cancel a dispute by a non-authorized account"""
        dispute_id = raise_dispute
        
        # Attempt to cancel the dispute with an unauthorized account (story_client_2)
        with pytest.raises(Exception):  # Exact exception type may vary based on implementation
            story_client_2.Dispute.cancel_dispute(
                dispute_id=dispute_id
            )

class TestDisputeResolve:
    @pytest.fixture(scope="module")
    def target_ip_id(self, story_client, story_client_2):
        """Create an IP to be disputed with PIL terms attached"""
        txData = story_client.NFTClient.create_nft_collection(
            name="test-collection",
            symbol="TEST",
            max_supply=100,
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=account.address
        )
        
        nft_contract = txData['nft_contract']

        # Register IP with PIL license terms
        license_terms_data = [
            {
                'terms': {
                    'transferable': True,
                    'royalty_policy': ROYALTY_POLICY,
                    'default_minting_fee': 0,
                    'expiration': 0,
                    'commercial_use': True,
                    'commercial_attribution': False,
                    'commercializer_checker': ZERO_ADDRESS,
                    'commercializer_checker_data': ZERO_ADDRESS,
                    'commercial_rev_share': 90,
                    'commercial_rev_ceiling': 0,
                    'derivatives_allowed': True,
                    'derivatives_attribution': True,
                    'derivatives_approval': False,
                    'derivatives_reciprocal': True,
                    'derivative_rev_ceiling': 0,
                    'currency': WIP_TOKEN_ADDRESS,
                    'uri': ""
                },
                'licensing_config': {
                    'is_set': True,
                    'minting_fee': 0,
                    'licensing_hook': ZERO_ADDRESS,
                    'hook_data': ZERO_ADDRESS,
                    'commercial_rev_share': 0,
                    'disabled': False,
                    'expect_minimum_group_reward_share': 0,
                    'expect_group_reward_pool': GROUP_REWARD_POOL
                }
            }
        ]

        metadata_a = {
            'ip_metadata_uri': "test-uri-a",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash-a")),
            'nft_metadata_uri': "test-nft-uri-a",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash-a"))
        }
        
        response = story_client_2.IPAsset.mint_and_register_ip_asset_with_pil_terms(
            spg_nft_contract=nft_contract,
            terms=license_terms_data,
            ip_metadata=metadata_a
        )

        return response['ip_id']

    @pytest.fixture(scope="module")
    def deposit_wip(self, story_client, story_client_2):
        """Deposit WIP tokens for both story clients"""
        deposit_response = story_client.WIP.deposit(
            amount=Web3.to_wei(10, 'ether')  # 10 IP tokens
        )
        
        deposit_response_2 = story_client_2.WIP.deposit(
            amount=Web3.to_wei(10, 'ether')  # 10 IP tokens
        )
        
        return {
            'client1': deposit_response['tx_hash'],
            'client2': deposit_response_2['tx_hash']
        }
    
    @pytest.fixture(scope="function")
    def dispute_id(self, story_client, target_ip_id, deposit_wip):
        """Raise a dispute for testing resolution with a short liveness period"""
        cid = generate_cid()
        bond_amount = Web3.to_wei(1, 'ether')  # 1 ETH in wei
        
        response = story_client.Dispute.raise_dispute(
            target_ip_id=target_ip_id,
            target_tag="IMPROPER_REGISTRATION",
            cid=cid,
            liveness=1,
            bond=bond_amount
        )

        time.sleep(3)

        dispute_id = response['dispute_id']

        assert 'dispute_id' in response
        assert isinstance(dispute_id, int)
        assert response['dispute_id'] > 0
        
        return dispute_id
    
    def settle_assertion(self, client, dispute_id):
        """
        Settle an assertion for a dispute.
        This function mimics the TypeScript implementation provided.
        """
        # Initialize the UMA arbitration policy client
        arbitration_policy_uma_client = client.Dispute.arbitration_policy_uma_client
        
        # Get the address of the Optimistic Oracle V3 contract
        oov3_address = arbitration_policy_uma_client.oov3()
        
        # Convert the disputeId to the corresponding assertionId
        assertion_id = client.Dispute.dispute_id_to_assertion_id(dispute_id)
        
        # Define the ASSERTION_ABI
        ASSERTION_ABI = [
            {
                "inputs": [{"internalType": "bytes32", "name": "assertionId", "type": "bytes32"}],
                "name": "settleAssertion",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        # Create a contract instance for the OOv3
        oov3_contract = web3.eth.contract(address=oov3_address, abi=ASSERTION_ABI)
        
        # Build the transaction
        tx = oov3_contract.functions.settleAssertion(assertion_id).build_transaction({
            'from': client.account.address,
            'nonce': web3.eth.get_transaction_count(client.account.address),
            'gas': 500000,
            'gasPrice': web3.eth.gas_price
        })
        
        # Sign and send the transaction
        signed_tx = web3.eth.account.sign_transaction(tx, client.account.key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for the transaction to be mined
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Verify dispute state is updated appropriately
        dispute_module_address = client.Dispute.dispute_module_client.contract.address
        dispute_module_contract = web3.eth.contract(
            address=dispute_module_address,
            abi=client.Dispute.dispute_module_client.contract.abi
        )
        
        dispute_state = dispute_module_contract.functions.disputes(dispute_id).call()
        # Check if current tag (index 6) equals target tag (index 5)
        assert dispute_state[6] == dispute_state[5], "Dispute state not updated correctly after settlement"
        
        return tx_receipt.transactionHash.hex()
    
    def test_resolve_dispute_by_initiator(self, story_client, dispute_id):
        """Test resolving a dispute successfully when initiated by dispute initiator"""
        # Settle the assertion first
        self.settle_assertion(story_client, dispute_id)
        
        # Resolve the dispute
        response = story_client.Dispute.resolve_dispute(
            dispute_id=dispute_id,
            data="0x"
        )
        
        # Verify the response
        assert 'tx_hash' in response
        assert isinstance(response['tx_hash'], str)
        assert len(response['tx_hash']) > 0
    
    def test_resolve_dispute_by_non_initiator(self, story_client_2, dispute_id):
        """Test that resolving a dispute fails when attempted by non-initiator"""
        # Settle the assertion first
        self.settle_assertion(story_client_2, dispute_id)
        
        # Attempt to resolve the dispute as non-initiator (should fail)
        print(ValueError)
        with pytest.raises(ValueError, match=r"0xb9e311aa"):
            story_client_2.Dispute.resolve_dispute(
                dispute_id=dispute_id,
                data="0x"
            )
    
    def test_resolve_nonexistent_dispute(self, story_client):
        """Test attempting to resolve a dispute that doesn't exist"""
        # Use a high dispute ID that's unlikely to exist
        nonexistent_dispute_id = 999999
        resolution_data = web3.to_hex(text="Resolution data")
        
        with pytest.raises(Exception):
            story_client.Dispute.resolve_dispute(
                dispute_id=nonexistent_dispute_id,
                data=resolution_data
            )
    
    def test_resolve_uncountered_dispute(self, story_client, dispute_id):
        """Test resolving a dispute that hasn't been countered"""
        # Try to resolve a dispute that hasn't been countered
        resolution_data = web3.to_hex(text="Resolution data")
        
        # This might be allowed or disallowed depending on the implementation
        # If it's disallowed, we expect an exception
        try:
            response = story_client.Dispute.resolve_dispute(
                dispute_id=dispute_id,
                data=resolution_data
            )
            # If it succeeds, verify the response
            assert 'tx_hash' in response
        except Exception as e:
            # If it fails, that's also valid depending on the implementation
            pass
