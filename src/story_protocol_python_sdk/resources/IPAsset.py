#src/story_protcol_python_sdk/resources/IPAsset.py

from web3 import Web3

from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import IPAssetRegistryClient
from story_protocol_python_sdk.abi.LicensingModule.LicensingModule_client import LicensingModuleClient
from story_protocol_python_sdk.abi.LicenseToken.LicenseToken_client import LicenseTokenClient
from story_protocol_python_sdk.abi.LicenseRegistry.LicenseRegistry_client import LicenseRegistryClient

from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

class IPAsset:
    """
    IPAssetClient allows you to create, get, and list IP Assets with Story Protocol.

    :param web3 Web3: An instance of Web3.
    :param account: The account to use for transactions.
    :param chain_id int: The ID of the blockchain network.
    """    
    def __init__(self, web3: Web3, account, chain_id: int):
        self.web3 = web3
        self.account = account
        self.chain_id = chain_id

        self.ip_asset_registry_client = IPAssetRegistryClient(web3)
        self.licensing_module_client = LicensingModuleClient(web3)
        self.license_token_client = LicenseTokenClient(web3)
        self.license_registry_client = LicenseRegistryClient(web3)

    def _get_ip_id(self, token_contract: str, token_id: int) -> str:
        """
        Get the IP ID for a given token.

        :param token_contract str: The address of the NFT.
        :param token_id int: The token identifier of the NFT.
        :return str: The IP ID.
        """
        return self.ip_asset_registry_client.ipId(
            self.chain_id, 
            token_contract,
            token_id
        )

    def _is_registered(self, ip_id: str) -> bool:
        """
        Check if an IP is registered.

        :param ip_id str: The IP ID to check.
        :return bool: True if registered, False otherwise.
        """        
        return self.ip_asset_registry_client.isRegistered(ip_id)

    def register(self, token_contract: str, token_id: int, tx_options: dict = None) -> dict:
        """
        Registers an NFT as IP, creating a corresponding IP record.

        :param token_contract str: The address of the NFT.
        :param token_id int: The token identifier of the NFT.
        :param tx_options dict: [Optional] transaction options.
        :return dict: A dictionary with the transaction hash and IP ID.
        """
        try:
            ip_id = self._get_ip_id(token_contract, token_id)
            if self._is_registered(ip_id):
                return {
                    'txHash': None,
                    'ipId': ip_id
                }

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.ip_asset_registry_client.build_register_transaction,
                self.chain_id,
                token_contract,
                token_id,
                tx_options=tx_options
            )

            return {
                'txHash': response['txHash'],
                'ipId': ip_id
            }

        except Exception as e:
            raise e

    def registerDerivative(self, child_ip_id: str, parent_ip_ids: list, license_terms_ids: list, license_template: str, tx_options: dict = None) -> dict:
        """
        Registers an IP Asset as a derivative of another IP Asset without needing License Tokens.

        The License Terms must be attached to the parent IP before calling this function. Remember that all IPAs have default license terms attached by default.

        The derivative IP owner must be the caller or an authorized operator.

        :param child_ip_id str: The derivative IP ID.
        :param parent_ip_ids list: The parent IP IDs.
        :param license_terms_ids list: The IDs of the license terms that the parent IP supports.
        :param license_template str: The address of the license template.
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash.
        """
        try:
            if not self._is_registered(child_ip_id):
                raise ValueError(f"The child IP with id {child_ip_id} is not registered.")

            for parent_id in parent_ip_ids:
                if not self._is_registered(parent_id):
                    raise ValueError(f"The parent IP with id {parent_id} is not registered.")

            if len(parent_ip_ids) != len(license_terms_ids):
                raise ValueError("Parent IP IDs and license terms IDs must match in quantity.")
            if len(parent_ip_ids) not in [1, 2]:
                raise ValueError("There can only be 1 or 2 parent IP IDs.")

            for parent_id, terms_id in zip(parent_ip_ids, license_terms_ids):
                if not self.license_registry_client.hasIpAttachedLicenseTerms(parent_id, license_template, terms_id):
                    raise ValueError(f"License terms id {terms_id} must be attached to the parent ipId {parent_id} before registering derivative.")

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.licensing_module_client.build_registerDerivative_transaction,
                child_ip_id,
                parent_ip_ids,
                license_terms_ids,
                license_template,
                ZERO_ADDRESS,
                tx_options=tx_options
            )

            return {
                'txHash': response['txHash']
            }

        except Exception as e:
            raise e
        
    def registerDerivativeWithLicenseTokens(self, child_ip_id: str, license_token_ids: list, tx_options: dict = None) -> dict:
        """
        Uses a pre-minted License Token to register an IP Asset as a derivative of another IP Asset. The derivative IPA will inherit the License Terms in the License Token.

        The derivative IP owner must be the caller or an authorized operator.

        :param child_ip_id str: The derivative IP ID.
        :param license_token_ids list: The IDs of the license tokens.
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash.
        """
        try:
            if not self._is_registered(child_ip_id):
                raise ValueError(f"The child IP with id {child_ip_id} is not registered.")

            for token_id in license_token_ids:
                token_owner = self.license_token_client.ownerOf(token_id)
                if token_owner.lower() != self.account.address.lower():
                    raise ValueError(f"License token id {token_id} must be owned by the caller.")

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.licensing_module_client.build_registerDerivativeWithLicenseTokens_transaction,
                child_ip_id,
                license_token_ids,
                ZERO_ADDRESS,
                tx_options=tx_options
            )

            return {
                'txHash': response['txHash']
            }

        except Exception as e:
            raise e
