# tests/integration/test_integration_dispute.py

import pytest
from web3 import Web3

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
            ip_metadata=metadata_a,
            tx_options={ "wait_for_transaction": True}
        )

        return response['ip_id']

    def test_raise_dispute(self, story_client, target_ip_id):
        """Test raising a dispute"""
        cid = generate_cid()
        bond_amount = 1000000000000000000  # 1 ETH in wei

        # Add approval before raising dispute
        # approve(
        #     erc20_contract_address="0x1514000000000000000000000000000000000000",
        #     web3=web3,
        #     account=account,
        #     spender_address="0xfFD98c3877B8789124f02C7E8239A4b0Ef11E936",
        #     amount=2**256 - 1  # maximum uint256 value
        # )
        
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
