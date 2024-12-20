#src/story_protcol_python_sdk/resources/IPAsset.py

from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_typed_data
from datetime import datetime

from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import IPAssetRegistryClient
from story_protocol_python_sdk.abi.LicensingModule.LicensingModule_client import LicensingModuleClient
from story_protocol_python_sdk.abi.LicenseToken.LicenseToken_client import LicenseTokenClient
from story_protocol_python_sdk.abi.LicenseRegistry.LicenseRegistry_client import LicenseRegistryClient
from story_protocol_python_sdk.abi.RegistrationWorkflows.RegistrationWorkflows_client import RegistrationWorkflowsClient
from story_protocol_python_sdk.abi.LicenseAttachmentWorkflows.LicenseAttachmentWorkflows_client import LicenseAttachmentWorkflowsClient
from story_protocol_python_sdk.abi.DerivativeWorkflows.DerivativeWorkflows_client import DerivativeWorkflowsClient
from story_protocol_python_sdk.abi.CoreMetadataModule.CoreMetadataModule_client import CoreMetadataModuleClient
from story_protocol_python_sdk.abi.AccessController.AccessController_client import AccessControllerClient
from story_protocol_python_sdk.abi.PILicenseTemplate.PILicenseTemplate_client import PILicenseTemplateClient

from story_protocol_python_sdk.utils.license_terms import LicenseTerms
from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ZERO_HASH = "0x0000000000000000000000000000000000000000000000000000000000000000"




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
        self.registration_workflows_client = RegistrationWorkflowsClient(web3)
        self.license_attachment_workflows_client = LicenseAttachmentWorkflowsClient(web3)
        self.derivative_workflows_client = DerivativeWorkflowsClient(web3)
        self.core_metadata_module_client = CoreMetadataModuleClient(web3)
        self.access_controller_client = AccessControllerClient(web3)
        self.pi_license_template_client = PILicenseTemplateClient(web3)

        # Instantiate LicenseTerms
        self.license_terms_util = LicenseTerms(web3)

    # def register(self, nft_contract: str, token_id: int, ip_metadata: dict = None, deadline: int = None, tx_options: dict = None) -> dict:
    #     """
    #     Registers an NFT as IP, creating a corresponding IP record.

    #     :param nft_contract str: The address of the NFT.
    #     :param token_id int: The token identifier of the NFT.
    #     :param ip_metadata dict: [Optional] The metadata for the IP.
    #         :param ip_metadata_URI str: [Optional] The URI of the metadata for the IP.
    #         :param ip_metadata_hash str: [Optional] The metadata hash for the IP.
    #         :param nft_metadata_URI str: [Optional] The URI of the metadata for the NFT.
    #         :param nft_metadata_hash str: [Optional] The metadata hash for the NFT.
    #     :param deadline int: [Optional] The deadline for the signature in milliseconds.
    #     :param tx_options dict: [Optional] The transaction options.
    #     :return dict: A dictionary with the transaction hash and IP ID.
    #     """
    #     try:
    #         ip_id = self._get_ip_id(nft_contract, token_id)
    #         if self._is_registered(ip_id):
    #             return {
    #                 'txHash': None,
    #                 'ipId': ip_id
    #             }

    #         req_object = {
    #             'tokenId': token_id,
    #             'nftContract': self.web3.to_checksum_address(nft_contract),
    #             'ipMetadata': {
    #                 'ipMetadataURI': "",
    #                 'ipMetadataHash': ZERO_HASH,
    #                 'nftMetadataURI': "",
    #                 'nftMetadataHash': ZERO_HASH,
    #             },
    #             'sigMetadata': {
    #                 'signer': ZERO_ADDRESS,
    #                 'deadline': 0,
    #                 'signature': ZERO_HASH,
    #             },
    #         }

    #         if ip_metadata:
    #             req_object['ipMetadata'].update({
    #                 'ipMetadataURI': ip_metadata.get('ipMetadataURI', ""),
    #                 'ipMetadataHash': ip_metadata.get('ipMetadataHash', ZERO_HASH),
    #                 'nftMetadataURI': ip_metadata.get('nftMetadataURI', ""),
    #                 'nftMetadataHash': ip_metadata.get('nftMetadataHash', ZERO_HASH),
    #             })

    #             calculated_deadline = self._get_deadline(deadline=deadline)
    #             signature = self._get_permission_signature(
    #                 ip_id=ip_id,
    #                 deadline=calculated_deadline,
    #                 state=self.web3.to_hex(0).rjust(66, '0'),
    #                 permissions=[{
    #                     'ipId': ip_id,
    #                     'signer': self.web3.to_checksum_address(self.account.address),
    #                     'to': self.core_metadata_module_client.contract.address,
    #                     'func': "setAll(address,string,bytes32,bytes32)",
    #                     'permission': 1
    #                 }],
    #                 permission_func="setAll"
    #             )
    #             req_object['sigMetadata'] = {
    #                 'signer': self.web3.to_checksum_address(self.account.address),
    #                 'deadline': calculated_deadline,
    #                 'signature': signature,
    #             }

    #         if ip_metadata:
    #             response = build_and_send_transaction(
    #                 self.web3,
    #                 self.account,
    #                 self.registration_workflows_client.build_registerIp_transaction,
    #                 req_object['nftContract'],
    #                 req_object['tokenId'],
    #                 req_object['metadata'],
    #                 req_object['sigMetadata'],
    #                 tx_options=tx_options
    #             )
    #         else:
    #             response = build_and_send_transaction(
    #                 self.web3,
    #                 self.account,
    #                 self.ip_asset_registry_client.build_register_transaction,
    #                 self.chain_id,
    #                 nft_contract,
    #                 token_id,
    #                 tx_options=tx_options
    #             )

    #         ip_registered = self._parse_tx_ip_registered_event(response['txReceipt'])

    #         return {
    #             'txHash': response['txHash'],
    #             'ipId': ip_registered['ipId']
    #         }

    #     except Exception as e:
    #         raise e

    # def registerDerivative(self, child_ip_id: str, parent_ip_ids: list, license_terms_ids: list, license_template: str, tx_options: dict = None) -> dict:
    #     """
    #     Registers an IP Asset as a derivative of another IP Asset without needing License Tokens.

    #     The License Terms must be attached to the parent IP before calling this function. Remember that all IPAs have default license terms attached by default.

    #     The derivative IP owner must be the caller or an authorized operator.

    #     :param child_ip_id str: The derivative IP ID.
    #     :param parent_ip_ids list: The parent IP IDs.
    #     :param license_terms_ids list: The IDs of the license terms that the parent IP supports.
    #     :param license_template str: The address of the license template.
    #     :param tx_options dict: [Optional] The transaction options.
    #     :return dict: A dictionary with the transaction hash.
    #     """
    #     try:
    #         if not self._is_registered(child_ip_id):
    #             raise ValueError(f"The child IP with id {child_ip_id} is not registered.")

    #         for parent_id in parent_ip_ids:
    #             if not self._is_registered(parent_id):
    #                 raise ValueError(f"The parent IP with id {parent_id} is not registered.")

    #         if len(parent_ip_ids) != len(license_terms_ids):
    #             raise ValueError("Parent IP IDs and license terms IDs must match in quantity.")
    #         # if len(parent_ip_ids) not in [1, 2]:
    #         #     raise ValueError("There can only be 1 or 2 parent IP IDs.")

    #         for parent_id, terms_id in zip(parent_ip_ids, license_terms_ids):
    #             if not self.license_registry_client.hasIpAttachedLicenseTerms(parent_id, license_template, terms_id):
    #                 raise ValueError(f"License terms id {terms_id} must be attached to the parent ipId {parent_id} before registering derivative.")

    #         response = build_and_send_transaction(
    #             self.web3,
    #             self.account,
    #             self.licensing_module_client.build_registerDerivative_transaction,
    #             child_ip_id,
    #             parent_ip_ids,
    #             license_terms_ids,
    #             license_template,
    #             ZERO_ADDRESS,
    #             tx_options=tx_options
    #         )

    #         return {
    #             'txHash': response['txHash']
    #         }

    #     except Exception as e:
    #         raise e
        
    # def registerDerivativeWithLicenseTokens(self, child_ip_id: str, license_token_ids: list, tx_options: dict = None) -> dict:
    #     """
    #     Uses a pre-minted License Token to register an IP Asset as a derivative of another IP Asset. The derivative IPA will inherit the License Terms in the License Token.

    #     The derivative IP owner must be the caller or an authorized operator.

    #     :param child_ip_id str: The derivative IP ID.
    #     :param license_token_ids list: The IDs of the license tokens.
    #     :param tx_options dict: [Optional] The transaction options.
    #     :return dict: A dictionary with the transaction hash.
    #     """
    #     try:
    #         if not self._is_registered(child_ip_id):
    #             raise ValueError(f"The child IP with id {child_ip_id} is not registered.")

    #         for token_id in license_token_ids:
    #             token_owner = self.license_token_client.ownerOf(token_id)
    #             if token_owner.lower() != self.account.address.lower():
    #                 raise ValueError(f"License token id {token_id} must be owned by the caller.")

    #         response = build_and_send_transaction(
    #             self.web3,
    #             self.account,
    #             self.licensing_module_client.build_registerDerivativeWithLicenseTokens_transaction,
    #             child_ip_id,
    #             license_token_ids,
    #             ZERO_ADDRESS,
    #             tx_options=tx_options
    #         )

    #         return {
    #             'txHash': response['txHash']
    #         }

    #     except Exception as e:
    #         raise e

    def mintAndRegisterIpAssetWithPilTerms(
        self,
        spg_nft_contract: str,
        terms: list,
        ip_metadata: dict = None,
        recipient: str = None,
        tx_options: dict = None
    ) -> dict:
        """
        Mint an NFT from a collection and register it as an IP.

        :param spg_nft_contract str: The address of the NFT collection
        :param terms list: The array of license terms to be attached
            :param transferable bool: Whether the license is transferable
            :param royalty_policy str: Address of the royalty policy contract registered with StoryProtocol
            :param default_minting_fee int: Fee to be paid when minting a license
            :param expiration int: Expiration period of the license
            :param commercial_use bool: Whether work can be used commercially
            :param commercial_attribution bool: Whether attribution required for commercial reproduction
            :param commercializer_checker str: Allowed commercializers (zero address for no restrictions)
            :param commercializer_checker_data str: Data for commercializer checker contract
            :param commercial_rev_share int: Percentage of revenue shared with licensor
            :param commercial_rev_ceiling int: Maximum revenue from commercial use
            :param derivatives_allowed bool: Whether derivatives can be created
            :param derivatives_attribution bool: Whether attribution required for derivatives
            :param derivatives_approval bool: Whether licensor must approve derivatives
            :param derivatives_reciprocal bool: Whether derivatives must use same license terms
            :param derivative_rev_ceiling int: Maximum revenue from derivative use
            :param currency str: ERC20 token for minting fee (must be registered)
            :param uri str: URI for offchain license terms
        :param ip_metadata dict: [Optional] Metadata for NFT and IP
            :param ip_metadata_uri str: [Optional] URI of IP metadata
            :param ip_metadata_hash str: [Optional] Hash of IP metadata
            :param nft_metadata_uri str: [Optional] URI of NFT metadata
            :param nft_metadata_hash str: [Optional] Hash of NFT metadata
        :param recipient str: [Optional] Address of NFT recipient (defaults to caller)
        :param tx_options dict: [Optional] Transaction options
        :return dict: Dictionary with transaction hash and optionally IP ID, Token ID, License Terms IDs
        """
        try:
            if not self.web3.is_address(spg_nft_contract):
                raise ValueError(f"The NFT contract address {spg_nft_contract} is not valid.")

            license_terms = []
            for term in terms:
                validated_term = self.license_terms_util.validate_license_terms(term)
                # Convert snake_case keys to camelCase while keeping the original values
                camelcase_term = {
                    'transferable': term['transferable'],
                    'royaltyPolicy': term['royalty_policy'],
                    'defaultMintingFee': term['default_minting_fee'],
                    'expiration': term['expiration'],
                    'commercialUse': term['commercial_use'],
                    'commercialAttribution': term['commercial_attribution'],
                    'commercializerChecker': term['commercializer_checker'],
                    'commercializerCheckerData': term['commercializer_checker_data'],
                    'commercialRevShare': term['commercial_rev_share'],
                    'commercialRevCeiling': term['commercial_rev_ceiling'],
                    'derivativesAllowed': term['derivatives_allowed'],
                    'derivativesAttribution': term['derivatives_attribution'],
                    'derivativesApproval': term['derivatives_approval'],
                    'derivativesReciprocal': term['derivatives_reciprocal'],
                    'derivativeRevCeiling': term['derivative_rev_ceiling'],
                    'currency': term['currency'],
                    'uri': term['uri']
                }
                license_terms.append(camelcase_term)

            metadata = {
                'ipMetadataURI': "",
                'ipMetadataHash': ZERO_HASH,
                'nftMetadataURI': "",
                'nftMetadataHash': ZERO_HASH,
            }

            if ip_metadata:
                metadata.update({
                    'ipMetadataURI': ip_metadata.get('ip_metadata_uri', ""),
                    'ipMetadataHash': ip_metadata.get('ip_metadata_hash', ZERO_HASH),
                    'nftMetadataURI': ip_metadata.get('nft_metadata_uri', ""),
                    'nftMetadataHash': ip_metadata.get('nft_metadata_hash', ZERO_HASH),
                })

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.license_attachment_workflows_client.build_mintAndRegisterIpAndAttachPILTerms_transaction,
                spg_nft_contract,
                recipient if recipient else self.account.address,
                metadata,
                license_terms,
                tx_options=tx_options
            )

            ip_registered = self._parse_tx_ip_registered_event(response['txReceipt'])
            license_terms_ids = self._parse_tx_license_terms_attached_event(response['txReceipt'])

            return {
                'txHash': response['txHash'],
                'ipId': ip_registered['ipId'],
                'licenseTermsIds': license_terms_ids,
                'tokenId': ip_registered['tokenId']
            }

        except Exception as e:
            raise e
        
    # def registerIpAndAttachPilTerms(self, nft_contract: str, token_id: int, pil_type: str, metadata: dict = None, deadline: int = None, minting_fee: int = None, commercial_rev_share: int = None, currency: str = None, tx_options: dict = None) -> dict:
    #     """
    #     Register a given NFT as an IP and attach Programmable IP License Terms.

    #     :param nft_contract str: The address of the NFT collection.
    #     :param token_id int: The ID of the NFT.
    #     :param pil_type str: The type of the PIL.
    #     :param metadata dict: [Optional] The metadata for the IP.
    #         :param metadataURI str: [Optional] The metadata URI for the IP.
    #         :param metadataHash str: [Optional] The metadata hash for the IP.
    #         :param nftMetadataHash str: [Optional] The metadata hash for the IP NFT.
    #     :param deadline int: [Optional] The deadline for the signature in milliseconds.
    #     :param minting_fee int: [Optional] The fee to be paid when minting a license.
    #     :param commercial_rev_share int: [Optional] Percentage of revenue that must be shared with the licensor.
    #     :param currency str: [Optional] The ERC20 token to be used to pay the minting fee. The token must be registered in Story Protocol.
    #     :param tx_options dict: [Optional] The transaction options.
    #     :return dict: A dictionary with the transaction hash, license terms ID, and IP ID.
    #     """
    #     try:
    #         if pil_type is None or pil_type not in self.license_terms_util.PIL_TYPE.values():
    #             raise ValueError("PIL type is required and must be one of the predefined PIL types.")
            
    #         ip_id = self._get_ip_id(nft_contract, token_id)
    #         if self._is_registered(ip_id):
    #             raise ValueError(f"The NFT with id {token_id} is already registered as IP.")

    #         license_term = self.license_terms_util.get_license_term_by_type(pil_type, {
    #             'mintingFee': minting_fee,
    #             'currency': currency,
    #             'royaltyPolicy': "0xAAbaf349C7a2A84564F9CC4Ac130B3f19A718E86", #default royalty policy
    #             'commercialRevShare': commercial_rev_share,
    #         })

    #         calculated_deadline = self._get_deadline(deadline=deadline)
    #         sig_attach_signature = self._get_signature(ip_id, self.licensing_module_client.contract.address, calculated_deadline, "attachLicenseTerms(address,address,uint256)", 2)

    #         req_object = {
    #             'nftContract': nft_contract,
    #             'tokenId': token_id,
    #             'terms': license_term,
    #             'metadata': {
    #                 'metadataURI': "",
    #                 'metadataHash': ZERO_HASH,
    #                 'nftMetadataHash': ZERO_HASH,
    #             },
    #             'sigMetadata': {
    #                 'signer': ZERO_ADDRESS,
    #                 'deadline': 0,
    #                 'signature': ZERO_HASH,
    #             },
    #             'sigAttach': {
    #                 'signer': self.web3.to_checksum_address(self.account.address),
    #                 'deadline': calculated_deadline,
    #                 'signature': sig_attach_signature,
    #             },
    #         }

    #         if metadata:
    #             req_object['metadata'].update({
    #                 'metadataURI': metadata.get('metadataURI', ""),
    #                 'metadataHash': metadata.get('metadataHash', ZERO_HASH),
    #                 'nftMetadataHash': metadata.get('nftMetadataHash', ZERO_HASH),
    #             })

    #         signature = self._get_signature(
    #             ip_id, 
    #             self.core_metadata_module_client.contract.address, 
    #             calculated_deadline, 
    #             "setAll(address,string,bytes32,bytes32)", 
    #             1
    #         )
    #         req_object['sigMetadata'] = {
    #             'signer': self.web3.to_checksum_address(self.account.address),
    #             'deadline': calculated_deadline,
    #             'signature': signature,
    #         }

    #         response = build_and_send_transaction(
    #             self.web3,
    #             self.account,
    #             self.license_attachment_workflows_client.build_registerIpAndAttachPILTerms_transaction,
    #             req_object['nftContract'],
    #             req_object['tokenId'],
    #             req_object['metadata'],
    #             req_object['terms'],
    #             req_object['sigMetadata'],
    #             req_object['sigAttach'],
    #             tx_options=tx_options
    #         )

    #         license_terms_id = self._parse_tx_license_terms_attached_event(response['txReceipt'])

    #         return {
    #             'txHash': response['txHash'],
    #             'licenseTermsId': license_terms_id,
    #             'ipId': ip_id
    #         }

    #     except Exception as e:
    #         raise e

    # def registerDerivativeIp(self, nft_contract: str, token_id: int, deriv_data: dict, metadata: dict = None, deadline: int = None, tx_options: dict = None) -> dict:
    #     """
    #     Register the given NFT as a derivative IP with metadata without using license tokens.

    #     :param nft_contract str: The address of the NFT collection.
    #     :param token_id int: The ID of the NFT.
    #     :param deriv_data dict: The derivative data to be used for registerDerivative.
    #         :param parentIpIds list: The IDs of the parent IPs to link the registered derivative IP.
    #         :param licenseTemplate str: [Optional] The address of the license template to be used for the linking.
    #         :param licenseTermsIds list: The IDs of the license terms to be used for the linking.
    #     :param metadata dict: [Optional] The desired metadata for the newly registered IP.
    #         :param metadataURI str: [Optional] The URI of the metadata for the IP.
    #         :param metadataHash str: [Optional] The metadata hash for the IP.
    #         :param nftMetadataHash str: [Optional] The metadata hash for the IP NFT.
    #     :param deadline int: [Optional] The deadline for the signature in milliseconds.
    #     :param tx_options dict: [Optional] The transaction options.
    #     :return dict: A dictionary with the transaction hash and IP ID.
    #     """
    #     try:
    #         ip_id = self._get_ip_id(nft_contract, token_id)
    #         if self._is_registered(ip_id):
    #             raise ValueError(f"The NFT with id {token_id} is already registered as IP.")

    #         if len(deriv_data['parentIpIds']) != len(deriv_data['licenseTermsIds']):
    #             raise ValueError("Parent IP IDs and license terms IDs must match in quantity.")
    #         if len(deriv_data['parentIpIds']) not in [1, 2]:
    #             raise ValueError("There can only be 1 or 2 parent IP IDs.")

    #         for parent_ip_id, license_terms_id in zip(deriv_data['parentIpIds'], deriv_data['licenseTermsIds']):
    #            if not self.license_registry_client.hasIpAttachedLicenseTerms(parent_ip_id, self.pi_license_template_client.contract.address, license_terms_id):
    #                 raise ValueError(f"License terms id {license_terms_id} must be attached to the parent ipId {parent_ip_id} before registering derivative.")

    #         calculated_deadline = self._get_deadline(deadline=deadline)
    #         sig_register_signature = self._get_signature(
    #             ip_id,
    #             self.licensing_module_client.contract.address,
    #             calculated_deadline,
    #             "registerDerivative(address,address[],uint256[],address,bytes)",
    #             2
    #         )

    #         req_object = {
    #             'nftContract': nft_contract,
    #             'tokenId': token_id,
    #             'derivData': {
    #                 'parentIpIds': [self.web3.to_checksum_address(id) for id in deriv_data['parentIpIds']],
    #                 'licenseTermsIds': deriv_data['licenseTermsIds'],
    #                 'licenseTemplate': self.pi_license_template_client.contract.address,
    #                 'royaltyContext': ZERO_ADDRESS,
    #             },
    #             'sigRegister': {
    #                 'signer': self.web3.to_checksum_address(self.account.address),
    #                 'deadline': calculated_deadline,
    #                 'signature': sig_register_signature,
    #             },
    #             'metadata': {
    #                 'metadataURI': "",
    #                 'metadataHash': ZERO_HASH,
    #                 'nftMetadataHash': ZERO_HASH,
    #             },
    #             'sigMetadata': {
    #                 'signer': ZERO_ADDRESS,
    #                 'deadline': 0,
    #                 'signature': ZERO_HASH,
    #             },
    #         }

    #         if metadata:
    #             req_object['metadata'].update({
    #                 'metadataURI': metadata.get('metadataURI', ""),
    #                 'metadataHash': metadata.get('metadataHash', ZERO_HASH),
    #                 'nftMetadataHash': metadata.get('nftMetadataHash', ZERO_HASH),
    #             })

    #         signature = self._get_signature(
    #             ip_id,
    #             self.core_metadata_module_client.contract.address,
    #             calculated_deadline,
    #             "setAll(address,string,bytes32,bytes32)",
    #             1
    #         )
    #         req_object['sigMetadata'] = {
    #             'signer': self.web3.to_checksum_address(self.account.address),
    #             'deadline': calculated_deadline,
    #             'signature': signature,
    #         }

    #         response = build_and_send_transaction(
    #             self.web3,
    #             self.account,
    #             self.derivative_workflows_client.build_registerIpAndMakeDerivative_transaction,
    #             req_object['nftContract'],
    #             req_object['tokenId'],
    #             req_object['derivData'],
    #             req_object['metadata'],
    #             req_object['sigMetadata'],
    #             req_object['sigRegister'],
    #             tx_options=tx_options
    #         )

    #         ip_registered = self._parse_tx_ip_registered_event(response['txReceipt'])

    #         return {
    #             'txHash': response['txHash'],
    #             'ipId': ip_registered['ipId']
    #         }

    #     except Exception as e:
    #         raise e

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

    def _parse_tx_ip_registered_event(self, tx_receipt: dict) -> int:
        """
        Parse the IPRegistered event from a transaction receipt.

        :param tx_receipt dict: The transaction receipt.
        :return int: The ID of the license terms.
        """
        event_signature = self.web3.keccak(text="IPRegistered(address,uint256,address,uint256,string,string,uint256)").hex()

        for log in tx_receipt['logs']:
            if log['topics'][0].hex() == event_signature:
                ip_id = '0x' + log['data'].hex()[26:66]
                token_id = int(log['topics'][3].hex(), 16)

                return {
                    'ipId': self.web3.to_checksum_address(ip_id),
                    'tokenId': token_id
                }
            
        return None
    
    def _parse_tx_license_term_attached_event(self, tx_receipt: dict) -> int:
        """
        Parse the LicenseTermsAttached event from a transaction receipt.

        :param tx_receipt dict: The transaction receipt.
        :return int: The ID of the license terms.
        """
        event_signature = self.web3.keccak(text="LicenseTermsAttached(address,address,address,uint256)").hex()

        for log in tx_receipt['logs']:
            if log['topics'][0].hex() == event_signature:
                data = log['data']

                license_terms_id  = int.from_bytes(data[-32:], byteorder='big')
                return license_terms_id 
        return None
    
    def _parse_tx_license_terms_attached_event(self, tx_receipt: dict) -> list:
        """
        Parse the LicenseTermsAttached events from a transaction receipt.

        :param tx_receipt dict: The transaction receipt.
        :return list: A list of license terms IDs.
        """
        event_signature = self.web3.keccak(text="LicenseTermsAttached(address,address,address,uint256)").hex()
        license_terms_ids = []

        for log in tx_receipt['logs']:
            if log['topics'][0].hex() == event_signature:
                data = log['data']
                license_terms_id = int.from_bytes(data[-32:], byteorder='big')
                license_terms_ids.append(license_terms_id)

        return license_terms_ids if license_terms_ids else None
    
    # def _get_signature(self, state: str, to: str, encode_data: bytes, verifying_contract: str, deadline: int) -> dict:
    #     """
    #     Get the signature.

    #     :param state str: The IP Account's state.
    #     :param to str: The recipient address.
    #     :param encode_data bytes: The encoded data.
    #     :param verifying_contract str: The verifying contract address.
    #     :param deadline int: The deadline for the signature in milliseconds.
    #     :return dict: A dictionary containing the signature and nonce.
    #     """
    #     try:
    #         # Calculate nonce by hashing state and encoded execute function data
    #         execute_data = self.ip_account_impl_client.contract.encode_abi(
    #             fn_name="execute",
    #             args=[to, 0, encode_data]
    #         )
            
    #         nonce = Web3.keccak(
    #             Web3.keccak(text=state) +
    #             execute_data
    #         )

    #         domain_data = {
    #             "name": "Story Protocol IP Account",
    #             "version": "1",
    #             "chainId": self.chain_id,
    #             "verifyingContract": verifying_contract,
    #         }

    #         message_types = {
    #             "Execute": [
    #                 {"name": "to", "type": "address"},
    #                 {"name": "value", "type": "uint256"},
    #                 {"name": "data", "type": "bytes"},
    #                 {"name": "nonce", "type": "bytes32"},
    #                 {"name": "deadline", "type": "uint256"},
    #             ],
    #         }

    #         message_data = {
    #             "to": to,
    #             "value": 0,
    #             "data": encode_data,
    #             "nonce": nonce.hex(),
    #             "deadline": deadline,
    #         }

    #         signable_message = encode_typed_data(domain_data, message_types, message_data)
    #         signed_message = Account.sign_message(signable_message, self.account.key)

    #         return {
    #             "signature": signed_message.signature.hex(),
    #             "nonce": nonce.hex()
    #         }

    #     except Exception as e:
    #         raise e
        
    # def _get_deadline(self, deadline: int = None) -> int:
    #     """
    #     Calculate the deadline for a transaction.

    #     :param deadline int: [Optional] The deadline value in milliseconds.
    #     :return int: The calculated deadline in milliseconds.
    #     """
    #     current_timestamp = int(datetime.now().timestamp() * 1000)
        
    #     if deadline is not None:
    #         if not isinstance(deadline, int) or deadline < 0:
    #             raise ValueError("Invalid deadline value.")
    #         return current_timestamp + deadline
    #     else:
    #         return current_timestamp + 1000
    # def _get_permission_signature(self, ip_id: str, deadline: int, nonce: str, wallet, chain_id: int, permissions: list, permission_func: str = "setPermission", state: str = None) -> dict:
    #     """
    #     Get the signature for setting permissions.

    #     :param ip_id str: The IP ID
    #     :param deadline int: The deadline
    #     :param nonce str: The nonce
    #     :param wallet: The wallet client
    #     :param chain_id int: The chain ID
    #     :param permissions list: The permissions
    #     :param permission_func str: The permission function (defaults to "setPermission")
    #     :param state str: The state
    #     :return dict: The signature response
    #     """
    #     try:
    #         # Get permission function name
    #         permission_function = permission_func if permission_func else "setPermission"

    #         # Get access controller address for chain
    #         access_address = self.access_controller_client.contract.address

    #         if permission_function == "setPermission":
    #             # Encode single permission
    #             encode_data = self.access_controller_client.contract.encode_abi(
    #                 fn_name=permission_function,
    #                 args=[
    #                     self.web3.to_checksum_address(permissions[0]['ipId']),
    #                     self.web3.to_checksum_address(permissions[0]['signer']),
    #                     self.web3.to_checksum_address(permissions[0]['to']),
    #                     permissions[0].get('func', "0x00000000"),
    #                     permissions[0]['permission']
    #                 ]
    #             )
    #         else:
    #             # Encode multiple permissions
    #             formatted_permissions = [{
    #                 'ipAccount': self.web3.to_checksum_address(p['ipId']),
    #                 'signer': self.web3.to_checksum_address(p['signer']),
    #                 'to': self.web3.to_checksum_address(p['to']),
    #                 'func': p.get('func', "0x00000000"),
    #                 'permission': p['permission']
    #             } for p in permissions]

    #             encode_data = self.access_controller_client.contract.encode_abi(
    #                 fn_name=permission_function,
    #                 args=[formatted_permissions]
    #             )

    #         return self._get_signature(
    #             state=state,
    #             to=access_address,
    #             encode_data=encode_data,
    #             wallet=wallet,
    #             verifying_contract=ip_id,
    #             deadline=deadline,
    #             chain_id=chain_id
    #         )

    #     except Exception as e:
    #         raise e
