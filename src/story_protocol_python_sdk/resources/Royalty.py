#src/story_protcol_python_sdk/resources/Royalty.py

from web3 import Web3

from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import IPAssetRegistryClient
from story_protocol_python_sdk.abi.IpRoyaltyVaultImpl.IpRoyaltyVaultImpl_client import IpRoyaltyVaultImplClient
from story_protocol_python_sdk.abi.RoyaltyPolicyLAP.RoyaltyPolicyLAP_client import RoyaltyPolicyLAPClient
from story_protocol_python_sdk.abi.RoyaltyModule.RoyaltyModule_client import RoyaltyModuleClient

from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction

class Royalty:
    def __init__(self, web3: Web3, account, chain_id):
        self.web3 = web3
        self.account = account
        self.chain_id = chain_id

        self.ip_asset_registry_client = IPAssetRegistryClient(web3)
        self.royalty_policy_lap_client = RoyaltyPolicyLAPClient(web3)
        self.royalty_module_client = RoyaltyModuleClient(web3)

    def collectRoyaltyTokens(self, parent_ip_id, child_ip_id, tx_options=None):
        try:
            # Check if the parent IP is registered
            is_registered = self.ip_asset_registry_client.isRegistered(parent_ip_id)
            if not is_registered:
                raise ValueError(f"The parent IP with id {parent_ip_id} is not registered.")

            # Get the royalty vault address
            proxy_address = self._getRoyaltyVaultAddress(child_ip_id)

            # Initialize the IP Royalty Vault client with the proxy address
            ip_royalty_vault_client = IpRoyaltyVaultImplClient(self.web3, contract_address=proxy_address)

            # Build and send the transaction
            response = build_and_send_transaction(
                self.web3,
                self.account,
                ip_royalty_vault_client.build_collectRoyaltyTokens_transaction,
                parent_ip_id,
                tx_options=tx_options
            )
    
            royaltyTokensCollected = self._parseTxRoyaltyTokensCollectedEvent(response['txReceipt'])

            return {
                'txHash': response['txHash'],
                'royaltyTokensCollected': royaltyTokensCollected
            }
        
        except Exception as e:
            raise e

    def _getRoyaltyVaultAddress(self, royalty_vault_ip_id):
        # Check if the royalty vault IP is registered
        is_registered = self.ip_asset_registry_client.isRegistered(royalty_vault_ip_id)
        if not is_registered:
            raise ValueError(f"The royalty vault IP with id {royalty_vault_ip_id} is not registered.")

        # Fetch the royalty vault address
        data = self.royalty_policy_lap_client.getRoyaltyData(royalty_vault_ip_id)

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

            # Initialize the IP Royalty Vault client with the proxy address
            ip_royalty_vault_client = IpRoyaltyVaultImplClient(self.web3, contract_address=proxy_address)

            # Build and send the transaction
            response = build_and_send_transaction(
                self.web3,
                self.account,
                ip_royalty_vault_client.build_snapshot_transaction,
                tx_options=tx_options
            )

            snapshotId =  self._parseTxSnapshotCompletedEvent(response['txReceipt'])

            return {
                'txHash': response['txHash'],
                'snapshotId': snapshotId
            }
        except Exception as e:
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

    def claimableRevenue(self, child_ip_id, account_address, snapshot_id, token):
        try:
            # Get the royalty vault address
            proxy_address = self._getRoyaltyVaultAddress(child_ip_id)

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
            raise e
        
    def payRoyaltyOnBehalf(self, receiver_ip_id, payer_ip_id, token, amount, tx_options=None):
        try:
            # Check if the receiver IP is registered
            is_receiver_registered = self.ip_asset_registry_client.isRegistered(receiver_ip_id)
            if not is_receiver_registered:
                raise ValueError(f"The receiver IP with id {receiver_ip_id} is not registered.")

            # Check if the payer IP is registered
            is_payer_registered = self.ip_asset_registry_client.isRegistered(payer_ip_id)
            if not is_payer_registered:
                raise ValueError(f"The payer IP with id {payer_ip_id} is not registered.")
                
            # Build and send the transaction
            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.royalty_module_client.build_payRoyaltyOnBehalf_transaction,
                receiver_ip_id,
                payer_ip_id,
                token,
                amount,
                tx_options=tx_options
            )

            return {'txHash': response['txHash']}
        
        except Exception as e:
            raise e
    
    def claimRevenue(self, snapshot_ids, child_ip_id, token, tx_options=None):
        try:
            # Get the royalty vault address
            proxy_address = self._getRoyaltyVaultAddress(child_ip_id)

            # Initialize the IP Royalty Vault client with the proxy address
            ip_royalty_vault_client = IpRoyaltyVaultImplClient(self.web3, contract_address=proxy_address)

            # Build and send the transaction
            response = build_and_send_transaction(
                self.web3,
                self.account,
                ip_royalty_vault_client.build_claimRevenueBySnapshotBatch_transaction,
                snapshot_ids,
                token,
                tx_options=tx_options
            )

            revenue_tokens_claimed = self._parseTxRevenueTokenClaimedEvent(response['txReceipt'])

            return {
                'txHash': response['txHash'],
                'claimableToken': revenue_tokens_claimed
            }
    
        except Exception as e:
            raise e
        
    def _parseTxRevenueTokenClaimedEvent(self, tx_receipt):
        event_signature = self.web3.keccak(text="RevenueTokenClaimed(address,address,uint256)").hex()
        
        for log in tx_receipt['logs']:
            if log['topics'][0].hex() == event_signature:
                data = log['data']

                # Convert the last 32 bytes to an integer
                revenue_tokens_claimed = int.from_bytes(data[-32:], byteorder='big')
                return revenue_tokens_claimed

        return None
