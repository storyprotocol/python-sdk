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
    :param account: The Web3 account used to sign and send transactions.
    :param chain_id int: The ID of the blockchain network.
    """
    def __init__(self, web3: Web3, account, chain_id: int):
        self.web3 = web3
        self.account = account
        self.chain_id = chain_id

        self.ip_asset_registry_client = IPAssetRegistryClient(web3)
        self.access_controller_client = AccessControllerClient(web3)
        self.ip_account_client = IPAccountImplClient(web3)

    def _execute_transaction(self, ip_id: str, to: str, build_transaction_method, *args, tx_options: dict = None) -> dict:
        """
        Internal helper to execute a transaction from the IP Account.

        :param ip_id str: The IP id to get IP account
        :param to str: The recipient of the transaction
        :param build_transaction_method: Method to build the transaction
        :param args: Arguments to pass to the build method
        :param tx_options dict: [Optional] The transaction options
        :return dict: A dictionary with the transaction hash
        """
        try:
            if not self.web3.is_address(to):
                raise ValueError(f"The recipient of the transaction {to} is not a valid address.")
            
            if not self._is_registered(ip_id):
                raise ValueError(f"The IP id {ip_id} is not registered.")

            ip_account_client = IPAccountImplClient(self.web3, contract_address=ip_id)

            response = build_and_send_transaction(
                self.web3,
                self.account,
                build_transaction_method,
                *args,
                tx_options=tx_options
            )

            return {
                'txHash': response['txHash']
            }

        except Exception as e:
            raise e

    def execute(self, to: str, value: int, ip_id: str, data: str, tx_options: dict = None) -> dict:
        """
        Executes a transaction from the IP Account.

        :param to str: The recipient of the transaction.
        :param value int: The amount of Ether to send.
        :param ip_id str: The IP id to get IP account
        :param data str: The data to send along with the transaction.
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash.
        """
        ip_account_client = IPAccountImplClient(self.web3, contract_address=ip_id)
        return self._execute_transaction(
            ip_id,
            to,
            ip_account_client.build_execute_transaction,
            to,
            value,
            data,
            0,
            tx_options=tx_options
        )

    def executeWithSig(self, ip_id: str, to: str, data: str, signer: str, deadline: int, signature: str, value: int = 0, tx_options: dict = None) -> dict:
        """
        Executes a transaction from the IP Account.

        :param ip_id str: The Ip Id to get ip account.
        :param to str: The recipient of the transaction.
        :param data str: The data to send along with the transaction.
        :param signer str: The signer of the transaction.
        :param deadline int: The deadline of the transaction signature.
        :param signature str: The signature of the transaction, EIP-712 encoded.
        :param value int: [Optional] The amount of Ether to send.
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash.
        """
        ip_account_client = IPAccountImplClient(self.web3, contract_address=ip_id)
        return self._execute_transaction(
            ip_id,
            to,
            ip_account_client.build_executeWithSig_transaction,
            to,
            value,
            data,
            signer,
            deadline,
            signature,
            tx_options=tx_options
        )
        
    def getIpAccountNonce(self, ip_id: str) -> bytes:
        """
        Returns the IPAccount's internal nonce for transaction ordering.

        :param ip_id str: The IP ID
        :return bytes: The IPAccount's internal nonce for transaction ordering.
        """
        ip_account_client = IPAccountImplClient(self.web3, contract_address=ip_id)
        return ip_account_client.state()

    def _is_registered(self, ip_id: str) -> bool:
        """
        Check if an IP is registered.

        :param ip_id str: The IP ID to check.
        :return bool: True if registered, False otherwise.
        """        
        return self.ip_asset_registry_client.isRegistered(ip_id)
