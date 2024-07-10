#src/story_protcol_python_sdk/resources/License.py

from web3 import Web3

from story_protocol_python_sdk.abi.PILicenseTemplate.PILicenseTemplate_client import PILicenseTemplateClient
from story_protocol_python_sdk.abi.LicenseRegistry.LicenseRegistry_client import LicenseRegistryClient
from story_protocol_python_sdk.abi.LicensingModule.LicensingModule_client import LicensingModuleClient
from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import IPAssetRegistryClient

from story_protocol_python_sdk.utils.license_terms import get_license_term_by_type, PIL_TYPE
from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

class License:
    """
    A class to manage licenses on Story Protocol.

    :param web3 Web3: An instance of Web3.
    :param account: The account to use for transactions.
    :param chain_id int: The ID of the blockchain network.
    """
    def __init__(self, web3: Web3, account, chain_id: int):
        self.web3 = web3
        self.account = account
        self.chain_id = chain_id

        self.license_template_client = PILicenseTemplateClient(web3)
        self.license_registry_client = LicenseRegistryClient(web3)
        self.licensing_module_client  = LicensingModuleClient(web3)
        self.ip_asset_registry_client = IPAssetRegistryClient(web3)

    def _get_license_terms_id(self, license_terms: dict) -> int:
        """
        Get the ID of the license terms.

        :param license_terms dict: The license terms.
        :return int: The ID of the license terms.
        """
        return self.license_template_client.getLicenseTermsId(license_terms)

    def registerNonComSocialRemixingPIL(self, tx_options: dict = None) -> dict:
        """
        Convenient function to register a PIL non-commercial social remix license to the registry.

        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash and the license terms ID.
        """
        try:
            license_terms = get_license_term_by_type(PIL_TYPE['NON_COMMERCIAL_REMIX'])

            license_terms_id = self._get_license_terms_id(license_terms)
            if (license_terms_id is not None) and (license_terms_id != 0):
                return {'licenseTermsId': license_terms_id}

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.license_template_client.build_registerLicenseTerms_transaction,
                license_terms,
                tx_options=tx_options
            )

            target_logs = self._parse_tx_license_terms_registered_event(response['txReceipt'])
            return {
                'txHash': response['txHash'],
                'licenseTermsId': target_logs
            }

        except Exception as e:
            raise e
        
    def registerCommercialUsePIL(self, minting_fee: int, currency: str, royalty_policy: str, tx_options: dict = None) -> dict:
        """
        Convenient function to register a PIL commercial use license to the registry.

        :param minting_fee int: The fee to be paid when minting a license.
        :param currency str: The ERC20 token to be used to pay the minting fee.
        :param royalty_policy str: The address of the royalty policy contract.
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash and the license terms ID.
        """
        try:
            complete_license_terms = get_license_term_by_type(PIL_TYPE['COMMERCIAL_USE'], {
                'mintingFee': minting_fee,
                'currency': currency,
                'royaltyPolicy': royalty_policy,
            })

            license_terms_id = self._get_license_terms_id(complete_license_terms)
            if (license_terms_id is not None) and (license_terms_id != 0):
                return {'licenseTermsId': license_terms_id}

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.license_template_client.build_registerLicenseTerms_transaction,
                complete_license_terms,
                tx_options=tx_options
            )

            if not response['txReceipt'].logs:
                return None

            target_logs = self._parse_tx_license_terms_registered_event(response['txReceipt'])
            return {
                'txHash': response['txHash'],
                'licenseTermsId': target_logs
            }

        except Exception as e:
            raise e

    def registerCommercialRemixPIL(self, minting_fee: int, currency: str, commercial_rev_share: int, royalty_policy: str, tx_options: dict = None) -> dict:
        """
        Convenient function to register a PIL commercial remix license to the registry.

        :param minting_fee int: The fee to be paid when minting a license.
        :param currency str: The ERC20 token to be used to pay the minting fee.
        :param commercial_rev_share int: Percentage of revenue that must be shared with the licensor.
        :param royalty_policy str: The address of the royalty policy contract.
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash and the license terms ID.
        """
        try:
            complete_license_terms = get_license_term_by_type(PIL_TYPE['COMMERCIAL_REMIX'], {
                'mintingFee': minting_fee,
                'currency': currency,
                'commercialRevShare': int((commercial_rev_share / 100) * 100000000),
                'royaltyPolicy': royalty_policy,
            })

            license_terms_id = self._get_license_terms_id(complete_license_terms)
            if license_terms_id and license_terms_id != 0:
                return {'licenseTermsId': license_terms_id}

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.license_template_client.build_registerLicenseTerms_transaction,
                complete_license_terms,
                tx_options=tx_options
            )

            if not response['txReceipt'].logs:
                return None

            target_logs = self._parse_tx_license_terms_registered_event(response['txReceipt'])
            return {
                'txHash': response['txHash'],
                'licenseTermsId': target_logs
            }

        except Exception as e:
            raise e

    def _parse_tx_license_terms_registered_event(self, tx_receipt: dict) -> int:
        """
        Parse the LicenseTermsRegistered event from a transaction receipt.

        :param tx_receipt dict: The transaction receipt.
        :return int: The ID of the license terms.
        """
        event_signature = self.web3.keccak(text="LicenseTermsRegistered(uint256,address,bytes)").hex()

        for log in tx_receipt['logs']:
            if log['topics'][0].hex() == event_signature:
                return int(log['topics'][1].hex(), 16)

        return None
    
    def attachLicenseTerms(self, ip_id: str, license_template: str, license_terms_id: int, tx_options: dict = None) -> dict:
        """
        Attaches license terms to an IP.

        :param ip_id str: The address of the IP to which the license terms are attached.
        :param license_template str: The address of the license template.
        :param license_terms_id int: The ID of the license terms.
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash.
        """
        try:
            if not Web3.is_address(license_template):
                raise ValueError(f'Address "{license_template}" is invalid.')

            is_registered = self.ip_asset_registry_client.isRegistered(ip_id)
            if not is_registered:
                raise ValueError(f"The IP with id {ip_id} is not registered.")

            is_existed = self.license_registry_client.exists(license_template, license_terms_id)
            if not is_existed:
                raise ValueError(f"License terms id {license_terms_id} do not exist.")

            is_attached_license_terms = self.license_registry_client.hasIpAttachedLicenseTerms(ip_id, license_template, license_terms_id)
            if is_attached_license_terms:
                raise ValueError(f"License terms id {license_terms_id} is already attached to the IP with id {ip_id}.")

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.licensing_module_client.build_attachLicenseTerms_transaction,
                ip_id,
                license_template,
                license_terms_id,
                tx_options=tx_options
            )

            return {'txHash': response['txHash']}
        
        except Exception as e:
            raise e
        
    def mintLicenseTokens(self, licensor_ip_id: str, license_template: str, license_terms_id: int, amount: int, receiver: str, tx_options: dict = None) -> dict:
        """
        Mints license tokens for the license terms attached to an IP.

        :param licensor_ip_id str: The licensor IP ID.
        :param license_template str: The address of the license template.
        :param license_terms_id int: The ID of the license terms within the license template.
        :param amount int: The amount of license tokens to mint.
        :param receiver str: The address of the receiver.
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash and the license token IDs.
        """
        try:
            if not Web3.is_address(license_template):
                raise ValueError(f'Address "{license_template}" is invalid.')
            
            if not Web3.is_address(receiver):
                raise ValueError(f'Address "{receiver}" is invalid.')

            is_registered = self.ip_asset_registry_client.isRegistered(licensor_ip_id)
            if not is_registered:
                raise ValueError(f"The licensor IP with id {licensor_ip_id} is not registered.")

            is_existed = self.license_template_client.exists(license_terms_id)
            if not is_existed:
                raise ValueError(f"License terms id {license_terms_id} do not exist.")

            is_attached_license_terms = self.license_registry_client.hasIpAttachedLicenseTerms(licensor_ip_id, license_template, license_terms_id)
            if not is_attached_license_terms:
                raise ValueError(f"License terms id {license_terms_id} is not attached to the IP with id {licensor_ip_id}.")

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.licensing_module_client.build_mintLicenseTokens_transaction,
                licensor_ip_id,
                license_template,
                license_terms_id,
                amount,
                receiver,
                ZERO_ADDRESS,
                tx_options=tx_options
            )

            target_logs = self._parse_tx_license_tokens_minted_event(response['txReceipt'])

            return {
                'txHash': response['txHash'],
                'licenseTokenIds': target_logs
            }

        except Exception as e:
            raise e

    def _parse_tx_license_tokens_minted_event(self, tx_receipt: dict) -> list:
        """
        Parse the LicenseTokenMinted event from a transaction receipt.

        :param tx_receipt dict: The transaction receipt.
        :return list: A list of license token IDs.
        """
        event_signature = self.web3.keccak(text="LicenseTokenMinted(address,address,uint256)").hex()
        token_ids = []

        for log in tx_receipt['logs']:
            if log['topics'][0].hex() == event_signature:
                start_license_token_id = int(log['topics'][3].hex(), 16)
                token_ids.append(start_license_token_id)

        return token_ids if token_ids else None
    
    def getLicenseTerms(self, selectedLicenseTermsId: int) -> dict:
        """
        Gets License Terms of the given ID.

        :param selectedLicenseTermsId int: The ID of the license terms to retrieve.
        :return dict: An object containing all of the selected license terms.
        """
        try:
            return self.license_template_client.getLicenseTerms(selectedLicenseTermsId)
        except Exception as e:
            raise ValueError(f"Failed to get license terms: {str(e)}")
        