#src/story_protcol_python_sdk/resources/Royalty.py

from web3 import Web3

from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import IPAssetRegistryClient
from story_protocol_python_sdk.abi.IpRoyaltyVaultImpl.IpRoyaltyVaultImpl_client import IpRoyaltyVaultImplClient
from story_protocol_python_sdk.abi.RoyaltyPolicyLAP.RoyaltyPolicyLAP_client import RoyaltyPolicyLAPClient
from story_protocol_python_sdk.abi.RoyaltyModule.RoyaltyModule_client import RoyaltyModuleClient

from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction

class Royalty:
    """
    A class to claim and pay royalties on Story Protocol.

    :param web3 Web3: An instance of Web3.
    :param account: The account to use for transactions.
    :param chain_id int: The ID of the blockchain network.
    """
    def __init__(self, web3: Web3, account, chain_id: int):
        self.web3 = web3
        self.account = account
        self.chain_id = chain_id

        self.ip_asset_registry_client = IPAssetRegistryClient(web3)
        self.royalty_policy_lap_client = RoyaltyPolicyLAPClient(web3)
        self.royalty_module_client = RoyaltyModuleClient(web3)

    # def collectRoyaltyTokens(self, parent_ip_id: str, child_ip_id: str, tx_options: dict = None) -> dict:
    #     """
    #     Allows ancestors to claim the royalty tokens and any accrued revenue tokens.

    #     :param parent_ip_id str: The IP ID of the ancestor to whom the royalty tokens belong.
    #     :param child_ip_id str: The derivative IP ID.
    #     :param tx_options dict: [Optional] The transaction options.
    #     :return dict: A dictionary with the transaction hash and the number of royalty tokens collected.
    #     """
    #     try:
    #         is_registered = self.ip_asset_registry_client.isRegistered(parent_ip_id)
    #         if not is_registered:
    #             raise ValueError(f"The parent IP with id {parent_ip_id} is not registered.")

    #         proxy_address = self._getRoyaltyVaultAddress(child_ip_id)
    #         ip_royalty_vault_client = IpRoyaltyVaultImplClient(self.web3, contract_address=proxy_address)

    #         response = build_and_send_transaction(
    #             self.web3,
    #             self.account,
    #             ip_royalty_vault_client.build_collectRoyaltyTokens_transaction,
    #             parent_ip_id,
    #             tx_options=tx_options
    #         )
    
    #         royaltyTokensCollected = self._parseTxRoyaltyTokensCollectedEvent(response['txReceipt'])

    #         return {
    #             'txHash': response['txHash'],
    #             'royaltyTokensCollected': royaltyTokensCollected
    #         }
        
    #     except Exception as e:
    #         raise e

    # def _getRoyaltyVaultAddress(self, ip_id: str) -> str:
    #     """
    #     Get the royalty vault address for a given IP ID.

    #     :param ip_id str: The IP ID.
    #     :return str: The respective royalty vault address.
    #     """
    #     is_registered = self.ip_asset_registry_client.isRegistered(ip_id)
    #     if not is_registered:
    #         raise ValueError(f"The IP with id {ip_id} is not registered.")

    #     data = self.royalty_policy_lap_client.getRoyaltyData(ip_id)

    #     if not data or not data[1] or data[1] == "0x":
    #         raise ValueError(f"The royalty vault IP with id {ip_id} address is not set.")
        
    #     return data[1]

    # def _parseTxRoyaltyTokensCollectedEvent(self, tx_receipt: dict) -> int:
    #     """
    #     Parse the RoyaltyTokensCollected event from a transaction receipt.

    #     :param tx_receipt dict: The transaction receipt.
    #     :return int: The number of royalty tokens collected.
    #     """
    #     event_signature = self.web3.keccak(text="RoyaltyTokensCollected(address,uint256)").hex()
        
    #     for log in tx_receipt['logs']:
    #         if log['topics'][0].hex() == event_signature:
    #             data = log['data']

    #             royalty_tokens_collected = int.from_bytes(data[-32:], byteorder='big')
    #             return royalty_tokens_collected

    #     return None
    
    # def snapshot(self, child_ip_id: str, tx_options: dict = None) -> dict:
    #     """
    #     Snapshots the claimable revenue and royalty token amounts.

    #     :param child_ip_id str: The child IP ID.
    #     :param tx_options dict: [Optional] The transaction options.
    #     :return dict: A dictionary with the transaction hash and the snapshot ID.
    #     """
    #     try:
    #         proxy_address = self._getRoyaltyVaultAddress(child_ip_id)
    #         ip_royalty_vault_client = IpRoyaltyVaultImplClient(self.web3, contract_address=proxy_address)

    #         response = build_and_send_transaction(
    #             self.web3,
    #             self.account,
    #             ip_royalty_vault_client.build_snapshot_transaction,
    #             tx_options=tx_options
    #         )

    #         snapshotId =  self._parseTxSnapshotCompletedEvent(response['txReceipt'])

    #         return {
    #             'txHash': response['txHash'],
    #             'snapshotId': snapshotId
    #         }
    #     except Exception as e:
    #         raise e

    # def _parseTxSnapshotCompletedEvent(self, tx_receipt: dict) -> int:
    #     """
    #     Parse the SnapshotCompleted event from a transaction receipt.

    #     :param tx_receipt dict: The transaction receipt.
    #     :return int: The snapshot ID.
    #     """
    #     event_signature = self.web3.keccak(text="SnapshotCompleted(uint256,uint256,uint32)").hex()
        
    #     for log in tx_receipt['logs']:
    #         if log['topics'][0].hex() == event_signature:
    #             data = log['data']
                
    #             snapshotId = int.from_bytes(data[:32], byteorder='big')

    #             return snapshotId

    #     return None

    # def claimableRevenue(self, child_ip_id: str, account_address: str, snapshot_id: int, token: str) -> int:
    #     """
    #     Calculates the amount of revenue token claimable by a token holder at certain snapshot.

    #     :param child_ip_id str: The child IP ID.
    #     :param account_address str: The address of the token holder.
    #     :param snapshot_id int: The snapshot ID.
    #     :param token str: The revenue token to claim.
    #     :return int: The claimable revenue amount.
    #     """
    #     try:
    #         proxy_address = self._getRoyaltyVaultAddress(child_ip_id)
    #         ip_royalty_vault_client = IpRoyaltyVaultImplClient(self.web3, contract_address=proxy_address)

    #         claimable_revenue = ip_royalty_vault_client.claimableRevenue(
    #             account=account_address,
    #             snapshotId=snapshot_id,
    #             token=token
    #         )

    #         return claimable_revenue

    #     except Exception as e:
    #         raise e
        
    # def payRoyaltyOnBehalf(self, receiver_ip_id: str, payer_ip_id: str, token: str, amount: int, tx_options: dict = None) -> dict:
    #     """
    #     Allows the function caller to pay royalties to the receiver IP asset on behalf of the payer IP asset.

    #     :param receiver_ip_id str: The IP ID that receives the royalties.
    #     :param payer_ip_id str: The ID of the IP asset that pays the royalties.
    #     :param token str: The token to use to pay the royalties.
    #     :param amount int: The amount to pay.
    #     :param tx_options dict: [Optional] The transaction options.
    #     :return dict: A dictionary with the transaction hash.
    #     """
    #     try:
    #         is_receiver_registered = self.ip_asset_registry_client.isRegistered(receiver_ip_id)
    #         if not is_receiver_registered:
    #             raise ValueError(f"The receiver IP with id {receiver_ip_id} is not registered.")

    #         is_payer_registered = self.ip_asset_registry_client.isRegistered(payer_ip_id)
    #         if not is_payer_registered:
    #             raise ValueError(f"The payer IP with id {payer_ip_id} is not registered.")
                
    #         response = build_and_send_transaction(
    #             self.web3,
    #             self.account,
    #             self.royalty_module_client.build_payRoyaltyOnBehalf_transaction,
    #             receiver_ip_id,
    #             payer_ip_id,
    #             token,
    #             amount,
    #             tx_options=tx_options
    #         )

    #         return {'txHash': response['txHash']}
        
    #     except Exception as e:
    #         raise e
    
    # def claimRevenue(self, snapshot_ids: list, child_ip_id: str, token: str, tx_options: dict = None) -> dict:
    #     """
    #     Allows token holders to claim by a list of snapshot IDs based on the token balance at certain snapshot.

    #     :param snapshot_ids list: The list of snapshot IDs.
    #     :param child_ip_id str: The child IP ID.
    #     :param token str: The revenue token to claim.
    #     :param tx_options dict: [Optional] The transaction options.
    #     :return dict: A dictionary with the transaction hash and the number of claimable tokens.
    #     """
    #     try:
    #         proxy_address = self._getRoyaltyVaultAddress(child_ip_id)
    #         ip_royalty_vault_client = IpRoyaltyVaultImplClient(self.web3, contract_address=proxy_address)

    #         response = build_and_send_transaction(
    #             self.web3,
    #             self.account,
    #             ip_royalty_vault_client.build_claimRevenueBySnapshotBatch_transaction,
    #             snapshot_ids,
    #             token,
    #             tx_options=tx_options
    #         )

    #         revenue_tokens_claimed = self._parseTxRevenueTokenClaimedEvent(response['txReceipt'])

    #         return {
    #             'txHash': response['txHash'],
    #             'claimableToken': revenue_tokens_claimed
    #         }
    
    #     except Exception as e:
    #         raise e
        
    # def _parseTxRevenueTokenClaimedEvent(self, tx_receipt: dict) -> int:
    #     """
    #     Parse the RevenueTokenClaimed event from a transaction receipt.

    #     :param tx_receipt dict: The transaction receipt.
    #     :return int: The number of revenue tokens claimed.
    #     """
    #     event_signature = self.web3.keccak(text="RevenueTokenClaimed(address,address,uint256)").hex()
        
    #     for log in tx_receipt['logs']:
    #         if log['topics'][0].hex() == event_signature:
    #             data = log['data']

    #             revenue_tokens_claimed = int.from_bytes(data[-32:], byteorder='big')
    #             return revenue_tokens_claimed

    #     return None
