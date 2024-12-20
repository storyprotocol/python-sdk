#src/story_protcol_python_sdk/resources/License.py

from web3 import Web3

from story_protocol_python_sdk.abi.PILicenseTemplate.PILicenseTemplate_client import PILicenseTemplateClient
from story_protocol_python_sdk.abi.LicenseRegistry.LicenseRegistry_client import LicenseRegistryClient
from story_protocol_python_sdk.abi.LicensingModule.LicensingModule_client import LicensingModuleClient
from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import IPAssetRegistryClient

from story_protocol_python_sdk.utils.license_terms import LicenseTerms
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

        self.license_terms_util = LicenseTerms(web3)

    def _get_license_terms_id(self, license_terms: dict) -> int:
        """
        Get the ID of the license terms.

        :param license_terms dict: The license terms.
        :return int: The ID of the license terms.
        """
        return self.license_template_client.getLicenseTermsId(license_terms)

    def registerPILTerms(self, 
                        transferable: bool,
                        royalty_policy: str,
                        default_minting_fee: int,
                        expiration: int,
                        commercial_use: bool,
                        commercial_attribution: bool,
                        commercializer_checker: str,
                        commercializer_checker_data: str,
                        commercial_rev_share: int,
                        commercial_rev_ceiling: int,
                        derivatives_allowed: bool,
                        derivatives_attribution: bool,
                        derivatives_approval: bool,
                        derivatives_reciprocal: bool,
                        derivative_rev_ceiling: int,
                        currency: str,
                        uri: str,
                        tx_options: dict = None) -> dict:
        """
        Registers new license terms and returns the ID of the newly registered license terms.

        :param transferable bool: Indicates whether the license is transferable or not.
        :param royalty_policy str: The address of the royalty policy contract which required to StoryProtocol in advance.
        :param default_minting_fee int: The fee to be paid when minting a license.
        :param expiration int: The expiration period of the license.
        :param commercial_use bool: Indicates whether the work can be used commercially or not.
        :param commercial_attribution bool: Whether attribution is required when reproducing the work commercially or not.
        :param commercializer_checker str: Commercializers that are allowed to commercially exploit the work. If zero address, then no restrictions is enforced.
        :param commercializer_checker_data str: The data to be passed to the commercializer checker contract.
        :param commercial_rev_share int: Percentage of revenue that must be shared with the licensor.
        :param commercial_rev_ceiling int: The maximum revenue that can be generated from the commercial use of the work.
        :param derivatives_allowed bool: Indicates whether the licensee can create derivatives of his work or not.
        :param derivatives_attribution bool: Indicates whether attribution is required for derivatives of the work or not.
        :param derivatives_approval bool: Indicates whether the licensor must approve derivatives of the work before they can be linked to the licensor IP ID or not.
        :param derivatives_reciprocal bool: Indicates whether the licensee must license derivatives of the work under the same terms or not.
        :param derivative_rev_ceiling int: The maximum revenue that can be generated from the derivative use of the work.
        :param currency str: The ERC20 token to be used to pay the minting fee. The token must be registered in story protocol.
        :param uri str: The URI of the license terms, which can be used to fetch the offchain license terms.
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash and license terms ID.
        """
        try:
            license_terms = {
                'transferable': transferable,
                'royaltyPolicy': royalty_policy,
                'defaultMintingFee': default_minting_fee,
                'expiration': expiration,
                'commercialUse': commercial_use,
                'commercialAttribution': commercial_attribution,
                'commercializerChecker': commercializer_checker,
                'commercializerCheckerData': commercializer_checker_data,
                'commercialRevShare': commercial_rev_share,
                'commercialRevCeiling': commercial_rev_ceiling,
                'derivativesAllowed': derivatives_allowed,
                'derivativesAttribution': derivatives_attribution,
                'derivativesApproval': derivatives_approval,
                'derivativesReciprocal': derivatives_reciprocal,
                'derivativeRevCeiling': derivative_rev_ceiling,
                'currency': currency,
                'uri': uri
            }

            license_terms_snake = {
                'transferable': transferable,
                'royalty_policy': royalty_policy,
                'default_minting_fee': default_minting_fee,
                'expiration': expiration,
                'commercial_use': commercial_use,
                'commercial_attribution': commercial_attribution,
                'commercializer_checker': commercializer_checker,
                'commercializer_checker_data': commercializer_checker_data,
                'commercial_rev_share': commercial_rev_share,
                'commercial_rev_ceiling': commercial_rev_ceiling,
                'derivatives_allowed': derivatives_allowed,
                'derivatives_attribution': derivatives_attribution,
                'derivatives_approval': derivatives_approval,
                'derivatives_reciprocal': derivatives_reciprocal,
                'derivative_rev_ceiling': derivative_rev_ceiling,
                'currency': currency,
                'uri': uri
            }

            # Validate the license terms
            self.license_terms_util.validate_license_terms(license_terms_snake)

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

    def registerNonComSocialRemixingPIL(self, tx_options: dict = None) -> dict:
        """
        Convenient function to register a PIL non-commercial social remix license to the registry.

        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash and the license terms ID.
        """
        try:
            license_terms = self.license_terms_util.get_license_term_by_type(self.license_terms_util.PIL_TYPE['NON_COMMERCIAL_REMIX'])

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
        
    def registerCommercialUsePIL(self, default_minting_fee: int, currency: str, royalty_policy: str = None, tx_options: dict = None) -> dict:
        """
        Convenient function to register a PIL commercial use license to the registry.

        :param default_minting_fee int: The fee to be paid when minting a license.
        :param currency str: The ERC20 token to be used to pay the minting fee.
        :param royalty_policy str: [Optional] The address of the royalty policy contract.
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash and the license terms ID.
        """
        try:
            complete_license_terms = self.license_terms_util.get_license_term_by_type(self.license_terms_util.PIL_TYPE['COMMERCIAL_USE'], {
                'defaultMintingFee': default_minting_fee,
                'currency': currency,
                'royaltyPolicyAddress': royalty_policy,
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

    def registerCommercialRemixPIL(self, default_minting_fee: int, currency: str, commercial_rev_share: int, royalty_policy: str, tx_options: dict = None) -> dict:
        """
        Convenient function to register a PIL commercial remix license to the registry.

        :param default_minting_fee int: The fee to be paid when minting a license.
        :param currency str: The ERC20 token to be used to pay the minting fee.
        :param commercial_rev_share int: Percentage of revenue that must be shared with the licensor.
        :param royalty_policy str: The address of the royalty policy contract.
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash and the license terms ID.
        """
        try:
            complete_license_terms = self.license_terms_util.get_license_term_by_type(self.license_terms_util.PIL_TYPE['COMMERCIAL_REMIX'], {
                'defaultMintingFee': default_minting_fee,
                'currency': currency,
                'commercialRevShare': commercial_rev_share,
                'royaltyPolicyAddress': royalty_policy,
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
        