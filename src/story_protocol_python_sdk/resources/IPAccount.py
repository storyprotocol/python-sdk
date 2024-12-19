#src/story_protcol_python_sdk/resources/IPAccount.py

from web3 import Web3

from story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client import IPAccountImplClient
from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import IPAssetRegistryClient
from story_protocol_python_sdk.abi.AccessController.AccessController_client import AccessControllerClient

from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction

class IPAccount:
    """
    A class to execute a transaction from the IP Account.

    :param web3 Web3: An instance of Web3.
    :param account: The account to use for transactions.
    :param chain_id int: The ID of the blockchain network.
    """
    def __init__(self, web3: Web3, account, chain_id: int):
        self.web3 = web3
        self.account = account
        self.chain_id = chain_id

        self.ip_asset_registry_client = IPAssetRegistryClient(web3)
        self.access_controller_client = AccessControllerClient(web3)

    # def execute(self, to: str, value: int, account_address: str, data: str) -> dict:
    #     """
    #     Executes a transaction from the IP Account.

    #     :param to str: The recipient of the transaction.
    #     :param value int: The amount of Ether to send.
    #     :param account_address str: The ipId to send.
    #     :param data str: The data to send along with the transaction.
    #     :return dict: A dictionary with the transaction hash.
    #     """
    #     try:
    #         if not self.web3.is_address(to):
    #             raise ValueError(f"The recipient of the transaction {to} is not a valid address.")
            
    #         if not self._is_registered(account_address):
    #             raise ValueError(f"The IP account with id {account_address} is not registered.")

    #         ip_account_client = IPAccountImplClient(self.web3, contract_address=account_address)

    #         response = build_and_send_transaction(
    #             self.web3,
    #             self.account,
    #             ip_account_client.build_execute_transaction,
    #             to,
    #             value,
    #             data
    #         )
    
    #         return {
    #             'txHash': response['txHash']
    #         }
        
    #     except Exception as e:
    #         raise e

    # def executeWithSig(self, to: str, value: int, account_address: str, data: str, signer: str, deadline: int, signature: str) -> dict:
    #     """
    #     Executes a transaction from the IP Account.

    #     :param to str: The recipient of the transaction.
    #     :param value int: The amount of Ether to send.
    #     :param account_address str: The ipId to send.
    #     :param data str: The data to send along with the transaction.
    #     :param signer str: The signer of the transaction.
    #     :param deadline int: The deadline of the transaction signature.
    #     :param signature str: The signature of the transaction, EIP-712 encoded.
    #     :return dict: A dictionary with the transaction hash.
    #     """
    #     try:
    #         if not self.web3.is_address(to):
    #             raise ValueError(f"The recipient of the transaction {to} is not a valid address.")
            
    #         if not self._is_registered(account_address):
    #             raise ValueError(f"The IP account with id {account_address} is not registered.")

    #         ip_account_client = IPAccountImplClient(self.web3, contract_address=account_address)

    #         response = build_and_send_transaction(
    #             self.web3,
    #             self.account,
    #             ip_account_client.build_executeWithSig_transaction,
    #             to,
    #             value,
    #             data,
    #             signer,
    #             deadline,
    #             signature
    #         )
    
    #         return {
    #             'txHash': response['txHash']
    #         }
        
    #     except Exception as e:
    #         raise e
        
    # def getIpAccountNonce(self, ip_id: str) -> int:
    #     """
    #     Returns the IPAccount's internal nonce for transaction ordering.

    #     :param ip_id str: The derivative IP ID
    #     :return int: The IPAccount's internal nonce for transaction ordering.
    #     """
    #     ip_account_client = IPAccountImplClient(self.web3, contract_address=ip_id)
    #     return ip_account_client.state()

    # def _is_registered(self, ip_id: str) -> bool:
    #     """
    #     Check if an IP is registered.

    #     :param ip_id str: The IP ID to check.
    #     :return bool: True if registered, False otherwise.
    #     """        
    #     return self.ip_asset_registry_client.isRegistered(ip_id)
