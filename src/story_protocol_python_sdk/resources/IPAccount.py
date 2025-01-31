"""Module for handling IP Account operations and transactions."""

from web3 import Web3
from web3.exceptions import InvalidAddress 

from story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client import IPAccountImplClient
from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import IPAssetRegistryClient
from story_protocol_python_sdk.abi.AccessController.AccessController_client import AccessControllerClient

from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction

class IPAccount:
    """A class to execute a transaction from the IP Account.

    :param web3: An instance of Web3.
    :type web3: Web3
    :param account: The Web3 account used to sign and send transactions.
    :type account: Any
    :param chain_id: The ID of the blockchain network.
    :type chain_id: int
    """

    def __init__(self, web3: Web3, account, chain_id: int):
        self.web3 = web3
        self.account = account
        self.chain_id = chain_id

        self.ip_asset_registry_client = IPAssetRegistryClient(web3)
        self.access_controller_client = AccessControllerClient(web3)
        self.ip_account_client = IPAccountImplClient(web3)

    def getToken(self, ip_id: str) -> dict:
        """Retrieve token information associated with an IP account.

        :param ip_id: The IP ID to query.
        :type ip_id: str
        :returns: Dictionary containing chainId, tokenContract, and tokenId.
        :rtype: dict
        :raises ValueError: If the IP ID is invalid.
        """
        try:
            checksum_address = Web3.to_checksum_address(ip_id)
            ip_account_client = IPAccountImplClient(self.web3, contract_address=checksum_address)
            chain_id, token_contract, token_id = ip_account_client.token()
            return {
                'chainId': chain_id,
                'tokenContract': token_contract,
                'tokenId': token_id
            }
        except ValueError:  # Catch ValueError from to_checksum_address
            raise ValueError(f"Invalid IP id address: {ip_id}")

    def _execute_transaction(self, ip_id: str, to: str, build_transaction_method, *args, tx_options: dict = None) -> dict:
        """Execute a transaction from the IP Account.

        Internal helper method that handles transaction execution and validation.

        :param ip_id: The IP ID to get IP account.
        :type ip_id: str
        :param to: The recipient of the transaction.
        :type to: str
        :param build_transaction_method: Method to build the transaction.
        :type build_transaction_method: Callable
        :param args: Arguments to pass to the build method.
        :type args: tuple
        :param tx_options: Optional transaction options.
        :type tx_options: dict, optional
        :returns: Dictionary containing transaction details.
        :rtype: dict
        :raises ValueError: If recipient address is invalid or IP is not registered.
        :raises Exception: For other transaction-related errors.
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

            return response

        except Exception as e:
            raise e

    def execute(self, to: str, value: int, ip_id: str, data: str, tx_options: dict = None) -> dict:
        """Execute a transaction from the IP Account.

        :param to: The recipient of the transaction.
        :type to: str
        :param value: The amount of Ether to send.
        :type value: int
        :param ip_id: The IP ID to get IP account.
        :type ip_id: str
        :param data: The data to send with the transaction.
        :type data: str
        :param tx_options: Optional transaction options.
        :type tx_options: dict, optional
        :returns: Dictionary containing the transaction hash.
        :rtype: dict
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
        """Execute a signed transaction from the IP Account.

        :param ip_id: The IP ID to get IP account.
        :type ip_id: str
        :param to: The recipient of the transaction.
        :type to: str
        :param data: The data to send with the transaction.
        :type data: str
        :param signer: The signer of the transaction.
        :type signer: str
        :param deadline: The deadline of the transaction signature.
        :type deadline: int
        :param signature: The EIP-712 encoded transaction signature.
        :type signature: str
        :param value: Optional amount of Ether to send.
        :type value: int, optional
        :param tx_options: Optional transaction options.
        :type tx_options: dict, optional
        :returns: Dictionary containing the transaction hash.
        :rtype: dict
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
        """Get the IP Account's internal nonce for transaction ordering.

        :param ip_id: The IP ID to query.
        :type ip_id: str
        :returns: The IP Account's internal nonce for transaction ordering.
        :rtype: bytes
        :raises ValueError: If the IP ID is invalid.
        """
        try:
            checksum_address = Web3.to_checksum_address(ip_id)
            ip_account_client = IPAccountImplClient(self.web3, contract_address=checksum_address)
            return ip_account_client.state()
        except ValueError:  # Catch ValueError from to_checksum_address
            raise ValueError(f"Invalid IP id address: {ip_id}")

    def _is_registered(self, ip_id: str) -> bool:
        """Check if an IP is registered.

        :param ip_id: The IP ID to check.
        :type ip_id: str
        :returns: True if registered, False otherwise.
        :rtype: bool
        """        
        return self.ip_asset_registry_client.isRegistered(ip_id)