# src/story_protcol_python_sdk/resources/Permission.py

from web3 import Web3
import os, json

from story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client import IPAccountImplClient
from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import IPAssetRegistryClient
from story_protocol_python_sdk.resources.IPAccount import IPAccount

from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction

class Permission:
    """
    A class to manage permissions for IP accounts.

    :param web3 Web3: An instance of Web3.
    :param account: The account to use for transactions.
    :param chain_id int: The ID of the blockchain network.
    """
    def __init__(self, web3: Web3, account, chain_id: int):
        self.web3 = web3
        self.account = account
        self.chain_id = chain_id

        self.ip_asset_registry_client = IPAssetRegistryClient(web3)
        self.ip_account = IPAccount(web3, account, chain_id)

    # def setPermission(self, ip_asset: str, signer: str, to: str, permission: int, func: str = "0x00000000", tx_options: dict = None) -> dict:
    #     """
    #     Sets the permission for a specific function call.

    #     :param ip_asset str: The address of the IP account that grants the permission for `signer`.
    #     :param signer str: The address that can call `to` on behalf of the `ip_asset`.
    #     :param to str: The address that can be called by the `signer`.
    #     :param permission int: The new permission level.
    #     :param func str: [Optional] The function selector string of `to` that can be called by the `signer` on behalf of the `ipAccount`.
    #     :param tx_options dict: [Optional] The transaction options.
    #     :return dict: A dictionary with the transaction hash.
    #     """
    #     try:
    #         if not self.web3.is_address(signer):
    #             raise ValueError(f"The address {signer} that can call 'to' on behalf of the 'ip_asset' is not a valid address.")

    #         if not self.web3.is_address(to):
    #             raise ValueError(f"The recipient of the transaction {to} is not a valid address.")
            
    #         if not self._is_registered(ip_asset):
    #             raise ValueError(f"The IP account with id {ip_asset} is not registered.")

    #         config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'config.json'))
    #         with open(config_path, 'r') as config_file:
    #             config = json.load(config_file)
    #         contract_address = None
    #         for contract in config['contracts']:
    #             if contract['contract_name'] == 'AccessController':
    #                 contract_address = contract['contract_address']
    #                 break
    #         if not contract_address:
    #             raise ValueError(f"Contract address for AccessController not found in config.json")
    #         abi_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'abi', 'AccessController', 'AccessController.json'))
    #         with open(abi_path, 'r') as abi_file:
    #             abi = json.load(abi_file)

    #         contract = self.web3.eth.contract(address=contract_address, abi=abi)
            
    #         data = contract.encode_abi(
    #             fn_name="setPermission",
    #             args=[
    #                 ip_asset,
    #                 signer,
    #                 to,
    #                 func,
    #                 permission
    #             ]
    #         )

    #         response = self.ip_account.execute(
    #             to=contract_address,
    #             value=0,
    #             account_address=ip_asset,
    #             data=data
    #         )

    #         return {
    #             'txHash': response['txHash']
    #         }

    #     except Exception as e:
    #         raise e

    # def _is_registered(self, ip_id: str) -> bool:
    #     """
    #     Check if an IP is registered.

    #     :param ip_id str: The IP ID to check.
    #     :return bool: True if registered, False otherwise.
    #     """        
    #     return self.ip_asset_registry_client.isRegistered(ip_id)