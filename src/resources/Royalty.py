#src/resources/Royalty.py

import logging
from web3 import Web3
from src.abi.IPAssetRegistry.IPAssetRegistry_client import IPAssetRegistryClient
from src.abi.IpRoyaltyVaultImpl.IpRoyaltyVaultImpl_client import IpRoyaltyVaultImplClient
from src.abi.RoyaltyPolicyLAP.RoyaltyPolicyLAP_client import RoyaltyPolicyLAPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Royalty:
    def __init__(self, web3: Web3, account, chain_id):
        self.web3 = web3
        self.account = account
        self.chain_id = chain_id

        self.ip_asset_registry_client = IPAssetRegistryClient(web3)
        self.royalty_policy_lap_client = RoyaltyPolicyLAPClient(web3)

    def collectRoyaltyTokens(self, parent_ip_id, child_ip_id, tx_options=None):
        try:
            # Check if the parent IP is registered
            is_registered = self.ip_asset_registry_client.isRegistered(parent_ip_id)
            if not is_registered:
                raise ValueError(f"The parent IP with id {parent_ip_id} is not registered.")

            # Get the royalty vault address
            # print("gonna check for royalty vault addy")
            proxy_address = self._getRoyaltyVaultAddress(child_ip_id)
            # print("The proxy address: ", proxy_address)

            # Initialize the IP Royalty Vault client with the proxy address
            ip_royalty_vault_client = IpRoyaltyVaultImplClient(self.web3, contract_address=proxy_address)

            # Build the transaction
            transaction = ip_royalty_vault_client.build_collectRoyaltyTokens_transaction(parent_ip_id, {
                'from': self.account.address,
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'gas': 2000000,
                'gasPrice': self.web3.to_wei('300', 'gwei')
            })

            # Sign the transaction using the account object
            signed_txn = self.account.sign_transaction(transaction)
            logger.info(f"Signed transaction: {signed_txn}")

            # Send the transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.info(f"Transaction hash: {tx_hash.hex()}")

            # Wait for transaction receipt with a longer timeout
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)  # 10 minutes timeout
            logger.info(f"Transaction receipt: {tx_receipt}")
    
            royaltyTokensCollected = self._parseTxRoyaltyTokensCollectedEvent(tx_receipt)
            # print("Number of royalty tokens collected: ", royaltyTokensCollected)

            return {
                'txHash': tx_hash.hex(),
                'royaltyTokensCollected': royaltyTokensCollected
            }
        
        except Exception as e:
            logger.error(f"Failed to collect royalty tokens: {e}")
            raise e

    def _getRoyaltyVaultAddress(self, royalty_vault_ip_id):
        # Check if the royalty vault IP is registered
        is_registered = self.ip_asset_registry_client.isRegistered(royalty_vault_ip_id)
        if not is_registered:
            raise ValueError(f"The royalty vault IP with id {royalty_vault_ip_id} is not registered.")

        # Fetch the royalty vault address
        data = self.royalty_policy_lap_client.getRoyaltyData(royalty_vault_ip_id)
        # print("The get royalty data looks like: ")
        if not data or not data[1] or data[1] == "0x":
            raise ValueError(f"The royalty vault IP with id {royalty_vault_ip_id} address is not set.")
        
        return data[1]

    def _parseTxRoyaltyTokensCollectedEvent(self, tx_receipt):
        event_signature = self.web3.keccak(text="RoyaltyTokensCollected(address,uint256)").hex()
        
        for log in tx_receipt['logs']:
            if log['topics'][0].hex() == event_signature:
                data = log['data']

                # Convert the last 32 bytes to an integer
                royalty_tokens_collected = int.from_bytes(data[-32:], byteorder='big')
                return royalty_tokens_collected

        return None
    
    def snapshot(self, child_ip_id, tx_options=None):
        try:
            # Get the royalty vault address
            proxy_address = self._getRoyaltyVaultAddress(child_ip_id)
            logger.info(f"The proxy address: {proxy_address}")
            #print("Thne proxy addres: ", proxy_address)

            # Initialize the IP Royalty Vault client with the proxy address
            ip_royalty_vault_client = IpRoyaltyVaultImplClient(self.web3, contract_address=proxy_address)

            # Build the transaction
            transaction = ip_royalty_vault_client.build_snapshot_transaction({
                'from': self.account.address,
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'gas': 2000000,
                'gasPrice': self.web3.to_wei('300', 'gwei')
            })

            # Sign the transaction using the account object
            signed_txn = self.account.sign_transaction(transaction)
            logger.info(f"Signed transaction: {signed_txn}")

            # Send the transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.info(f"Transaction hash: {tx_hash.hex()}")


            # Wait for transaction receipt with a longer timeout
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)  # 10 minutes timeout
            logger.info(f"Transaction receipt: {tx_receipt}")

            snapshotId =  self._parseTxSnapshotCompletedEvent(tx_receipt)

            return {
                'txHash': tx_hash.hex(),
                'snapshotId': snapshotId
            }
        except Exception as e:
            logger.error(f"Failed to snapshot: {e}")
            raise e

    def _parseTxSnapshotCompletedEvent(self, tx_receipt):
        event_signature = self.web3.keccak(text="SnapshotCompleted(uint256,uint256,uint32)").hex()
        
        for log in tx_receipt['logs']:
            if log['topics'][0].hex() == event_signature:
                data = log['data']
                
                # Convert the last 32 bytes to an integer
                snapshotId = int.from_bytes(data[:32], byteorder='big')

                return snapshotId

        return None

    def claimableRevenue(self, child_ip_id, account_address, snapshot_id, token, tx_options=None):
        try:
            # Get the royalty vault address
            proxy_address = self._getRoyaltyVaultAddress(child_ip_id)
            logger.info(f"The proxy address: {proxy_address}")
            print("Thne proxy addres: ", proxy_address)

            # Initialize the IP Royalty Vault client with the proxy address
            ip_royalty_vault_client = IpRoyaltyVaultImplClient(self.web3, contract_address=proxy_address)

            # Get the claimable revenue
            claimable_revenue = ip_royalty_vault_client.claimableRevenue(
                account=account_address,
                snapshotId=snapshot_id,
                token=token
            )

            return claimable_revenue

        except Exception as e:
            logger.error(f"Failed to calculate claimable revenue: {e}")
            raise e