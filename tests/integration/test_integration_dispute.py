import pytest
import time
from web3 import Web3

from setup_for_integration import (
    web3,
    account, 
    account_2,
    story_client,
    story_client_2,
    generate_cid
)

class TestDispute:
    @pytest.fixture(scope="module")
    def target_ip_id(self, story_client, story_client_2):
        """Create an IP to be disputed"""
        txData = story_client.NFTClient.createNFTCollection(
            name="test-collection",
            symbol="TEST",
            max_supply=100,
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=account.address,
            tx_options={ "wait_for_transaction": True}
        )
        
        nft_contract = txData['nftContract']

        metadata_a = {
            'ip_metadata_uri': "test-uri-a",
            'ip_metadata_hash': web3.to_hex(web3.keccak(text="test-metadata-hash-a")),
            'nft_metadata_uri': "test-nft-uri-a",
            'nft_metadata_hash': web3.to_hex(web3.keccak(text="test-nft-metadata-hash-a"))
        }
        
        response = story_client_2.IPAsset.mintAndRegisterIp(
            spg_nft_contract=nft_contract,
            ip_metadata=metadata_a,
            tx_options={ "wait_for_transaction": True}
        )

        return response['ipId']

    def test_raise_dispute(self, story_client, target_ip_id):
        """Test raising a dispute"""
        cid = generate_cid()

        is_registered = story_client.IPAsset._is_registered(target_ip_id)

        print("test - check")
        print("cid:", cid)
        print("target_ip_id:", target_ip_id)
        print("is the target registered?", is_registered)
        
        response = story_client.Dispute.raise_dispute(
            target_ip_id=target_ip_id,
            target_tag="IMPROPER_REGISTRATION",
            cid=cid,
            liveness=0x278d,  # 30 days in seconds
            bond=1000000000000000000
        )
        
        assert 'txHash' in response
        assert isinstance(response['txHash'], str)
        assert len(response['txHash']) > 0
        assert 'disputeId' in response
        assert isinstance(response['disputeId'], int)
        assert response['disputeId'] > 0

    