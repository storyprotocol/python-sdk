"""Module for handling IP Account operations and transactions."""

from web3 import Web3
from web3.exceptions import InvalidAddress 

from story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client import IPAccountImplClient
from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import IPAssetRegistryClient
from story_protocol_python_sdk.abi.AccessController.AccessController_client import AccessControllerClient

from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction

class IPAccount:
    """A class to execute a transaction from the IP Account.

    :param web3 Web3: An instance of Web3.
    :param account Any: The Web3 account used to sign and send transactions.
    :param chain_id int: The ID of the blockchain network.
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

        :param ip_id str: The IP ID to query.
        :returns dict: Dictionary containing chainId, tokenContract, and tokenId.
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

    def _validate_transaction_params(self, ip_id: str, to: str):
        """Validate transaction parameters.

        :param ip_id str: The IP ID to get IP account.
        :param to str: The recipient of the transaction.
        :raises ValueError: If recipient address is invalid or IP is not registered.
        """
        if not self.web3.is_address(to):
            raise ValueError(f"The recipient of the transaction {to} is not a valid address.")
        
        if not self._is_registered(ip_id):
            raise ValueError(f"The IP id {ip_id} is not registered.")

    def execute(self, to: str, value: int, ip_id: str, data: str, tx_options: dict = None) -> dict:
        """Execute a transaction from the IP Account.

        :param to str: The recipient of the transaction.
        :param value int: The amount of Ether to send.
        :param ip_id str: The IP ID to get IP account.
        :param data str: The data to send with the transaction.
        :param tx_options dict: Optional transaction options.
        :returns dict: Dictionary containing the transaction hash.
        """
        self._validate_transaction_params(ip_id, to)
        
        ip_account_client = IPAccountImplClient(self.web3, contract_address=ip_id)
        
        response = build_and_send_transaction(
            self.web3,
            self.account,
            ip_account_client.build_execute_transaction,
            to,
            value, 
            data,
            0,
            tx_options=tx_options
        )

        return response

    def executeWithSig(self, ip_id: str, to: str, data: str, signer: str, deadline: int, signature: str, value: int = 0, tx_options: dict = None) -> dict:
        """Execute a signed transaction from the IP Account.

        :param ip_id str: The IP ID to get IP account.
        :param to str: The recipient of the transaction.
        :param data str: The data to send with the transaction.
        :param signer str: The signer of the transaction.
        :param deadline int: The deadline of the transaction signature.
        :param signature str: The EIP-712 encoded transaction signature.
        :param value int: Optional amount of Ether to send.
        :param tx_options dict: Optional transaction options.
        :returns dict: Dictionary containing the transaction hash.
        """
        self._validate_transaction_params(ip_id, to)

        ip_account_client = IPAccountImplClient(self.web3, contract_address=ip_id)
        
        response = build_and_send_transaction(
            self.web3,
            self.account,
            ip_account_client.build_executeWithSig_transaction,
            to,
            value,
            data,
            signer,
            deadline,
            signature,
            tx_options=tx_options
        )

        return response
        
    def getIpAccountNonce(self, ip_id: str) -> bytes:
        """Get the IP Account's internal nonce for transaction ordering.

        :param ip_id str: The IP ID to query.
        :returns bytes: The IP Account's internal nonce for transaction ordering.
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

        :param ip_id str: The IP ID to check.
        :returns bool: True if registered, False otherwise.
        """        
        return self.ip_asset_registry_client.isRegistered(ip_id)
    
    def owner(self, ip_id: str) -> str:
        """Get the owner of the IP Account.

        :param ip_id str: The IP ID to get IP account.
        :returns str: The owner of the IP Account.
        :raises ValueError: If the IP ID is invalid.
        """
        try:
            checksum_address = Web3.to_checksum_address(ip_id)
            ip_account_client = IPAccountImplClient(self.web3, contract_address=checksum_address)
            return ip_account_client.owner()
        except ValueError:  # Catch ValueError from to_checksum_address
            raise ValueError(f"Invalid IP id address: {ip_id}")
        except Exception as e:
            raise e