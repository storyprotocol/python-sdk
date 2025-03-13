#src/story_protcol_python_sdk/resources/Royalty.py

from web3 import Web3

from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import IPAssetRegistryClient
from story_protocol_python_sdk.abi.IpRoyaltyVaultImpl.IpRoyaltyVaultImpl_client import IpRoyaltyVaultImplClient
from story_protocol_python_sdk.abi.RoyaltyPolicyLAP.RoyaltyPolicyLAP_client import RoyaltyPolicyLAPClient
from story_protocol_python_sdk.abi.RoyaltyModule.RoyaltyModule_client import RoyaltyModuleClient
from story_protocol_python_sdk.abi.IpRoyaltyVaultImpl.IpRoyaltyVaultImpl_client import IpRoyaltyVaultImplClient
from story_protocol_python_sdk.abi.RoyaltyWorkflows.RoyaltyWorkflows_client import RoyaltyWorkflowsClient

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
        self.ip_royalty_vault_client = IpRoyaltyVaultImplClient(web3)
        self.royalty_workflows_client = RoyaltyWorkflowsClient(web3)

    def getRoyaltyVaultAddress(self, ip_id: str) -> str:
        """
        Get the royalty vault address for a given IP ID.

        :param ip_id str: The IP ID.
        :return str: The respective royalty vault address.
        """
        is_registered = self.ip_asset_registry_client.isRegistered(ip_id)
        if not is_registered:
            raise ValueError(f"The IP with id {ip_id} is not registered.")

        return self.royalty_module_client.ipRoyaltyVaults(ip_id)

    def claimableRevenue(self, royalty_vault_ip_id: str, claimer: str, token: str) -> int:
        """
        Calculates the amount of revenue token claimable by a token holder.

        :param royalty_vault_ip_id str: The id of the royalty vault.
        :param claimer str: The address of the royalty token holder.
        :param token str: The revenue token to claim.
        :return int: The claimable revenue amount.
        """
        try:
            proxy_address = self.getRoyaltyVaultAddress(royalty_vault_ip_id)
            ip_royalty_vault_client = IpRoyaltyVaultImplClient(self.web3, contract_address=proxy_address)

            claimable_revenue = ip_royalty_vault_client.claimableRevenue(
                claimer=claimer,
                token=token
            )

            return claimable_revenue

        except Exception as e:
            raise e
        
    def payRoyaltyOnBehalf(self, receiver_ip_id: str, payer_ip_id: str, token: str, amount: int, tx_options: dict = None) -> dict:
        """
        Allows the function caller to pay royalties to the receiver IP asset on behalf of the payer IP asset.

        :param receiver_ip_id str: The IP ID that receives the royalties.
        :param payer_ip_id str: The ID of the IP asset that pays the royalties.
        :param token str: The token to use to pay the royalties.
        :param amount int: The amount to pay.
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash.
        """
        try:
            is_receiver_registered = self.ip_asset_registry_client.isRegistered(receiver_ip_id)
            if not is_receiver_registered:
                raise ValueError(f"The receiver IP with id {receiver_ip_id} is not registered.")

            is_payer_registered = self.ip_asset_registry_client.isRegistered(payer_ip_id)
            if not is_payer_registered:
                raise ValueError(f"The payer IP with id {payer_ip_id} is not registered.")
                
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
    
    def claimAllRevenue(self, ancestor_ip_id: str, claimer: str, child_ip_ids: list, royalty_policies: list, currency_tokens: list, claim_options: dict = None, tx_options: dict = None) -> dict:
        """
        Claims all revenue from the child IPs of an ancestor IP, then optionally transfers and unwraps tokens.

        :param ancestor_ip_id str: The IP ID of the ancestor.
        :param claimer str: The address of the claimer.
        :param child_ip_ids list: List of child IP IDs.
        :param royalty_policies list: List of royalty policy addresses.
        :param currency_tokens list: List of currency token addresses.
        :param claim_options dict: [Optional] Options for auto-transfer and unwrapping.
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with transaction details and claimed tokens.
        """
        try:
            # Validate addresses
            if not self.web3.is_address(ancestor_ip_id):
                raise ValueError("Invalid ancestor IP ID address")
            if not self.web3.is_address(claimer):
                raise ValueError("Invalid claimer address") 
            if not all(self.web3.is_address(addr) for addr in child_ip_ids):
                raise ValueError("Invalid child IP ID address")
            if not all(self.web3.is_address(addr) for addr in royalty_policies):
                raise ValueError("Invalid royalty policy address")
            if not all(self.web3.is_address(addr) for addr in currency_tokens):
                raise ValueError("Invalid currency token address")

            # Claim revenue
            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.royalty_workflows_client.build_claimAllRevenue_transaction,
                ancestor_ip_id,
                claimer, 
                child_ip_ids,
                royalty_policies,
                currency_tokens,
                tx_options=tx_options
            )

            tx_hashes = [response['txHash']]
            
            # Determine if the claimer is an IP owned by the wallet.
            owns_claimer, is_claimer_ip, ip_account = self._get_claimer_info(claimer)

            # If wallet does not own the claimer then we cannot auto claim.
            # If ownsClaimer is false, it means the claimer is neither an IP owned by the wallet nor the wallet address itself.
            if not owns_claimer:
                return {
                    'receipt': response['txReceipt'],
                    'txHashes': tx_hashes
                }
            
            claimed_tokens = self._parseTxRevenueTokenClaimedEvent(response['txReceipt'])


            auto_transfer = claim_options['autoTransferAllClaimedTokensFromIp']
            # auto_unwrap = claim_options['autoUnwrapIpTokens']

            # transfer claimed tokens from IP to wallet if wallet owns IP
            if auto_transfer and is_claimer_ip and owns_claimer:
                hashes = self._transferClaimedTokensFromIpToWallet(
                    ip_account,
                    claimed_tokens
                )
            tx_hashes.extend(hashes)

            return {
                'receipt': response['txReceipt'],
                'claimedTokens': claimed_tokens,
                'txHashes': tx_hashes
            }

        except Exception as e:
            raise ValueError(f"Failed to claim all revenue: {str(e)}")
    
    def _get_claimer_info(self, claimer):
        """
        Get information about the claimer address.
        
        :param claimer str: The claimer address to check
        :return dict: Dictionary containing:
            - owns_claimer (bool): Whether the wallet owns the claimer
            - is_claimer_ip (bool): Whether the claimer is an IP
            - ip_account (IpAccountImplClient): IP account client if claimer is an IP
        """
        is_claimer_ip = self.ip_asset_registry_client.isRegistered(claimer)
        owns_claimer = claimer == self.account.address

        ip_account = None
        if is_claimer_ip:
            ip_account = self.ip_account_impl_client(claimer) 
            ip_owner = ip_account.owner()
            owns_claimer = ip_owner == self.account.address

        return {
            'owns_claimer': owns_claimer,
            'is_claimer_ip': is_claimer_ip, 
            'ip_account': ip_account
        }
    
    def _transferClaimedTokensFromIpToWallet(self, ip_account, claimed_tokens: list) -> list:
        """
        Transfer claimed tokens from an IP account to the wallet.

        :param ip_account IpAccountImplClient: The IP account to transfer from
        :param claimed_tokens list: List of claimed tokens, each containing token address and amount
        :return list: List of transaction hashes
        """
        tx_hashes = []

        for claimed_token in claimed_tokens:
            token = claimed_token['token'] 
            amount = claimed_token['amount']

            if amount <= 0:
                continue

            # Build ERC20 transfer function data
            transfer_data = self.web3.eth.contract(
                abi=[{
                    "inputs": [
                        {"name": "recipient", "type": "address"},
                        {"name": "amount", "type": "uint256"}
                    ],
                    "name": "transfer",
                    "outputs": [{"name": "", "type": "bool"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }]
            ).encodeABI(
                fn_name="transfer",
                args=[self.account.address, amount]
            )

            # Execute transfer through IP account
            tx_hash = ip_account.execute(
                token,
                0,
                0,  # CALL operation
                transfer_data
            )
            tx_hashes.append(tx_hash)

        return tx_hashes

    def _parseTxRevenueTokenClaimedEvent(self, tx_receipt: dict) -> int:
        """
        Parse the RevenueTokenClaimed event from a transaction receipt.

        :param tx_receipt dict: The transaction receipt.
        :return int: The number of revenue tokens claimed.
        """
        event_signature = self.web3.keccak(text="RevenueTokenClaimed(address,address,uint256)").hex()
        
        for log in tx_receipt['logs']:
            if log['topics'][0].hex() == event_signature:
                data = log['data']

                revenue_tokens_claimed = int.from_bytes(data[-32:], byteorder='big')
                return revenue_tokens_claimed

        return None
