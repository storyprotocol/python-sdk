"""Module for handling IP Account operations and transactions."""

from dataclasses import asdict, is_dataclass

from ens.ens import Address, HexStr
from web3 import Web3

from story_protocol_python_sdk.abi.AccessController.AccessController_client import (
    AccessControllerClient,
)
from story_protocol_python_sdk.abi.CoreMetadataModule.CoreMetadataModule_client import (
    CoreMetadataModuleClient,
)
from story_protocol_python_sdk.abi.DerivativeWorkflows.DerivativeWorkflows_client import (
    DerivativeWorkflowsClient,
)
from story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client import (
    IPAccountImplClient,
)
from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import (
    IPAssetRegistryClient,
)
from story_protocol_python_sdk.abi.IpRoyaltyVaultImpl.IpRoyaltyVaultImpl_client import (
    IpRoyaltyVaultImplClient,
)
from story_protocol_python_sdk.abi.LicenseAttachmentWorkflows.LicenseAttachmentWorkflows_client import (
    LicenseAttachmentWorkflowsClient,
)
from story_protocol_python_sdk.abi.LicenseRegistry.LicenseRegistry_client import (
    LicenseRegistryClient,
)
from story_protocol_python_sdk.abi.LicenseToken.LicenseToken_client import (
    LicenseTokenClient,
)
from story_protocol_python_sdk.abi.LicensingModule.LicensingModule_client import (
    LicensingModuleClient,
)
from story_protocol_python_sdk.abi.Multicall3.Multicall3_client import Multicall3Client
from story_protocol_python_sdk.abi.PILicenseTemplate.PILicenseTemplate_client import (
    PILicenseTemplateClient,
)
from story_protocol_python_sdk.abi.RegistrationWorkflows.RegistrationWorkflows_client import (
    RegistrationWorkflowsClient,
)
from story_protocol_python_sdk.abi.RoyaltyModule.RoyaltyModule_client import (
    RoyaltyModuleClient,
)
from story_protocol_python_sdk.abi.RoyaltyTokenDistributionWorkflows.RoyaltyTokenDistributionWorkflows_client import (
    RoyaltyTokenDistributionWorkflowsClient,
)
from story_protocol_python_sdk.abi.SPGNFTImpl.SPGNFTImpl_client import SPGNFTImplClient
from story_protocol_python_sdk.types.common import AccessPermission
from story_protocol_python_sdk.types.resource.IPAsset import (
    BatchMintAndRegisterIPInput,
    BatchMintAndRegisterIPResponse,
    LicenseTermsDataInput,
    RegisterAndAttachAndDistributeRoyaltyTokensResponse,
    RegisterDerivativeIPAndAttachAndDistributeRoyaltyTokensResponse,
    RegisteredIP,
    RegisterPILTermsAndAttachResponse,
    RegistrationResponse,
    RegistrationWithRoyaltyVaultAndLicenseTermsResponse,
    RegistrationWithRoyaltyVaultResponse,
)
from story_protocol_python_sdk.types.resource.Royalty import RoyaltyShareInput
from story_protocol_python_sdk.utils.constants import (
    MAX_ROYALTY_TOKEN,
    ZERO_ADDRESS,
    ZERO_HASH,
)
from story_protocol_python_sdk.utils.derivative_data import (
    DerivativeData,
    DerivativeDataInput,
)
from story_protocol_python_sdk.utils.function_signature import get_function_signature
from story_protocol_python_sdk.utils.ip_metadata import IPMetadata, IPMetadataInput
from story_protocol_python_sdk.utils.license_terms import LicenseTerms
from story_protocol_python_sdk.utils.royalty import get_royalty_shares
from story_protocol_python_sdk.utils.sign import Sign
from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction
from story_protocol_python_sdk.utils.validation import (
    validate_address,
    validate_max_rts,
)


class IPAsset:
    """
    IPAssetClient allows you to create, get, and list IP Assets with Story
    Protocol.

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
        self.license_attachment_workflows_client = LicenseAttachmentWorkflowsClient(
            web3
        )
        self.derivative_workflows_client = DerivativeWorkflowsClient(web3)
        self.core_metadata_module_client = CoreMetadataModuleClient(web3)
        self.access_controller_client = AccessControllerClient(web3)
        self.pi_license_template_client = PILicenseTemplateClient(web3)
        self.royalty_token_distribution_workflows_client = (
            RoyaltyTokenDistributionWorkflowsClient(web3)
        )
        self.royalty_module_client = RoyaltyModuleClient(web3)
        self.multicall3_client = Multicall3Client(web3)
        self.license_terms_util = LicenseTerms(web3)
        self.sign_util = Sign(web3, self.chain_id, self.account)

    def mint(
        self,
        nft_contract: str,
        to_address: str,
        metadata_uri: str,
        metadata_hash: bytes,
        allow_duplicates: bool = False,
        tx_options: dict | None = None,
    ):
        spg_nft_client = SPGNFTImplClient(self.web3, contract_address=nft_contract)

        def build_mint_transaction(
            to, metadata_uri, metadata_hash, allow_duplicates, transaction_options
        ):
            return spg_nft_client.contract.functions.mint(
                to, metadata_uri, metadata_hash, allow_duplicates
            ).build_transaction(transaction_options)

        response = build_and_send_transaction(
            self.web3,
            self.account,
            build_mint_transaction,
            to_address,
            metadata_uri,
            metadata_hash,
            allow_duplicates,
            tx_options=tx_options,
        )

        tx_hash = response["tx_hash"]
        # Ensure the transaction hash starts with "0x"
        if isinstance(tx_hash, str) and not tx_hash.startswith("0x"):
            tx_hash = "0x" + tx_hash

        return tx_hash

    def register(
        self,
        nft_contract: str,
        token_id: int,
        ip_metadata: dict | None = None,
        deadline: int | None = None,
        tx_options: dict | None = None,
    ) -> dict:
        """
        Register an NFT as IP, creating a corresponding IP record.
        :param nft_contract str: The address of the NFT.
        :param token_id int: The token identifier of the NFT.
        :param ip_metadata dict: [Optional] Metadata for the IP.
            :param ip_metadata_uri str: [Optional] Metadata URI for the IP.
            :param ip_metadata_hash str: [Optional] Metadata hash for the IP.
            :param nft_metadata_uri str: [Optional] Metadata URI for the NFT.
            :param nft_metadata_hash str: [Optional] Metadata hash for the NFT.
        :param deadline int: [Optional] Signature deadline in seconds. (default: 1000 seconds)
        :param tx_options dict: [Optional] Transaction options.
        :return dict: Dictionary with the transaction hash and IP ID.
        """
        try:
            ip_id = self._get_ip_id(nft_contract, token_id)
            if self._is_registered(ip_id):
                return {"tx_hash": None, "ip_id": ip_id}

            req_object: dict = {
                "tokenId": token_id,
                "nftContract": self.web3.to_checksum_address(nft_contract),
                "ipMetadata": {
                    "ipMetadataURI": "",
                    "ipMetadataHash": ZERO_HASH,
                    "nftMetadataURI": "",
                    "nftMetadataHash": ZERO_HASH,
                },
                "sigMetadata": {
                    "signer": ZERO_ADDRESS,
                    "deadline": 0,
                    "signature": ZERO_HASH,
                },
            }

            if ip_metadata:
                req_object["ipMetadata"].update(
                    {
                        "ipMetadataURI": ip_metadata.get("ip_metadata_uri", ""),
                        "ipMetadataHash": ip_metadata.get(
                            "ip_metadata_hash", ZERO_HASH
                        ),
                        "nftMetadataURI": ip_metadata.get("nft_metadata_uri", ""),
                        "nftMetadataHash": ip_metadata.get(
                            "nft_metadata_hash", ZERO_HASH
                        ),
                    }
                )

                calculated_deadline = self.sign_util.get_deadline(deadline=deadline)
                signature_response = self.sign_util.get_permission_signature(
                    ip_id=ip_id,
                    deadline=calculated_deadline,
                    state=self.web3.to_bytes(hexstr=HexStr(ZERO_HASH)),
                    permissions=[
                        {
                            "ipId": ip_id,
                            "signer": self.registration_workflows_client.contract.address,
                            "to": self.core_metadata_module_client.contract.address,
                            "func": "setAll(address,string,bytes32,bytes32)",
                            "permission": AccessPermission.ALLOW,
                        }
                    ],
                )

                req_object["sigMetadata"] = {
                    "signer": self.web3.to_checksum_address(self.account.address),
                    "deadline": calculated_deadline,
                    "signature": signature_response["signature"],
                }

                response = build_and_send_transaction(
                    self.web3,
                    self.account,
                    self.registration_workflows_client.build_registerIp_transaction,
                    req_object["nftContract"],
                    req_object["tokenId"],
                    req_object["ipMetadata"],
                    req_object["sigMetadata"],
                    tx_options=tx_options,
                )
            else:
                response = build_and_send_transaction(
                    self.web3,
                    self.account,
                    self.ip_asset_registry_client.build_register_transaction,
                    self.chain_id,
                    nft_contract,
                    token_id,
                    tx_options=tx_options,
                )

            ip_registered = self._parse_tx_ip_registered_event(response["tx_receipt"])[
                0
            ]

            return {"tx_hash": response["tx_hash"], "ip_id": ip_registered["ip_id"]}

        except Exception as e:
            raise e

    def register_derivative(
        self,
        child_ip_id: str,
        parent_ip_ids: list,
        license_terms_ids: list,
        max_minting_fee: int = 0,
        max_rts: int = MAX_ROYALTY_TOKEN,
        max_revenue_share: int = 100,
        license_template: str | None = None,
        tx_options: dict | None = None,
    ) -> dict:
        """
        Registers a derivative directly with parent IP's license terms, without needing license tokens,
        and attaches the license terms of the parent IPs to the derivative IP.
        The license terms must be attached to the parent IP before calling this function.
        All IPs attached default license terms by default.
        The derivative IP owner must be the caller or an authorized operator.

        :param child_ip_id str: The derivative IP ID
        :param parent_ip_ids list: The parent IP IDs
        :param license_terms_ids list: The IDs of the license terms that the parent IP supports
        :param max_minting_fee int: The maximum minting fee that the caller is willing to pay.
            if set to 0 then no limit. (default: 0)
        :param max_rts int: The maximum number of royalty tokens that can be distributed
            (max: 100,000,000) (default: 100,000,000)
        :param max_revenue_share int: The maximum revenue share percentage allowed. Must be between 0 and 100 (where 100% represents 100,000,000). (default: 100)
        :param license_template str: [Optional] The license template address. Defaults to [License Template](https://docs.story.foundation/docs/programmable-ip-license) address if not provided.
        :param tx_options dict: [Optional] Transaction options
        :return dict: A dictionary with the transaction hash
        """
        try:
            if not self._is_registered(child_ip_id):
                raise ValueError(
                    f"The child IP with id {child_ip_id} is not registered."
                )
            derivative_data = DerivativeData.from_input(
                web3=self.web3,
                input_data=DerivativeDataInput(
                    parent_ip_ids=parent_ip_ids,
                    license_terms_ids=license_terms_ids,
                    max_minting_fee=max_minting_fee,
                    max_rts=max_rts,
                    max_revenue_share=max_revenue_share,
                    license_template=license_template,
                ),
            ).get_validated_data()

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.licensing_module_client.build_registerDerivative_transaction,
                child_ip_id,
                derivative_data["parentIpIds"],
                derivative_data["licenseTermsIds"],
                derivative_data["licenseTemplate"],
                derivative_data["royaltyContext"],
                derivative_data["maxMintingFee"],
                derivative_data["maxRts"],
                derivative_data["maxRevenueShare"],
                tx_options=tx_options,
            )

            return {"tx_hash": response["tx_hash"]}

        except Exception as e:
            raise ValueError(f"Failed to register derivative: {str(e)}") from e

    def register_derivative_with_license_tokens(
        self,
        child_ip_id: str,
        license_token_ids: list,
        max_rts: int = 0,
        tx_options: dict | None = None,
    ) -> dict:
        """
        Registers a derivative with license tokens. The derivative IP is registered with license tokens
        minted from the parent IP's license terms.
        The license terms of the parent IPs issued with license tokens are attached to the derivative IP.
        The caller must be the derivative IP owner or an authorized operator.

        :param child_ip_id str: The derivative IP ID.
        :param license_token_ids list: The IDs of the license tokens.
        :param max_rts int: The maximum number of royalty tokens that can be distributed to the
            external royalty policies (max: 100,000,000).
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash.
        """
        try:
            # Validate max_rts
            validate_max_rts(max_rts)

            # Validate child IP registration
            if not self._is_registered(child_ip_id):
                raise ValueError(
                    f"The child IP with id {child_ip_id} is not registered."
                )

            # Validate license token IDs and ownership
            validated_token_ids = self._validate_license_token_ids(license_token_ids)

            # Build and send transaction
            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.licensing_module_client.build_registerDerivativeWithLicenseTokens_transaction,
                child_ip_id,
                validated_token_ids,
                ZERO_ADDRESS,
                max_rts,
                tx_options=tx_options,
            )

            return {"tx_hash": response["tx_hash"]}

        except Exception as e:
            raise ValueError(
                f"Failed to register derivative with license tokens: {str(e)}"
            )

    def mint_and_register_ip_asset_with_pil_terms(
        self,
        spg_nft_contract: str,
        terms: list,
        ip_metadata: dict | None = None,
        recipient: str | None = None,
        allow_duplicates: bool = False,
        tx_options: dict | None = None,
    ) -> dict:
        """
        Mint an NFT from a collection and register it as an IP.

        :param spg_nft_contract str: The address of the NFT collection.
        :param terms list: An array of license terms to attach.
            :param terms dict: The license terms configuration.
                :param transferable bool: Transferability of the license.
                :param royalty_policy str: Address of the royalty policy contract.
                :param default_minting_fee int: Fee for minting a license.
                :param expiration int: License expiration.
                :param commercial_use bool: Whether commercial use is allowed.
                :param commercial_attribution bool: Whether attribution is needed
                    for commercial use.
                :param commercializer_checker str: Allowed commercializers or zero
                    address for none.
                :param commercializer_checker_data str: Data for checker contract.
                :param commercial_rev_share int: Percentage of revenue that must be shared with the licensor. Must be between 0 and 100 (where 100% represents 100,000,000).
                :param commercial_rev_ceiling int: Maximum commercial revenue.
                :param derivatives_allowed bool: Whether derivatives are allowed.
                :param derivatives_attribution bool: Whether attribution is needed
                    for derivatives.
                :param derivatives_approval bool: Whether licensor approval is
                    required for derivatives.
                :param derivatives_reciprocal bool: Whether derivatives must use
                    the same license terms.
                :param derivative_rev_ceiling int: Max derivative revenue.
                :param currency str: ERC20 token for the minting fee.
                :param uri str: URI for offchain license terms.
            :param licensing_config dict: The configuration for the license.
                :param is_set bool: Whether the configuration is set or not.
                :param minting_fee int: The fee to be paid when minting tokens.
                :param hook_data str: The data used by the licensing hook.
                :param licensing_hook str: The licensing hook contract address or
                    address(0) if none.
                :param commercial_rev_share int: Percentage of revenue that must be shared with the licensor. Must be between 0 and 100 (where 100% represents 100,000,000).
                :param disabled bool: Whether the license is disabled.
                :param expect_minimum_group_reward_share int: Minimum group reward share percentage. Must be between 0 and 100 (where 100% represents 100,000,000).
                :param expect_group_reward_pool str: Address of the expected group reward pool.
        :param ip_metadata dict: [Optional] NFT and IP metadata.
            :param ip_metadata_uri str: [Optional] IP metadata URI.
            :param ip_metadata_hash str: [Optional] IP metadata hash.
            :param nft_metadata_uri str: [Optional] NFT metadata URI.
            :param nft_metadata_hash str: [Optional] NFT metadata hash.
        :param recipient str: [Optional] Recipient address (defaults to caller).
        :param allow_duplicates bool: [Optional] Whether to allow duplicates.
        :param tx_options dict: [Optional] Transaction options.
        :return dict: Dictionary with tx hash, IP ID, token ID, and license term IDs.
        """
        try:
            if not self.web3.is_address(spg_nft_contract):
                raise ValueError(
                    f"The NFT contract address {spg_nft_contract} is not valid."
                )
            license_terms = self._validate_license_terms_data(terms)

            metadata = {
                "ipMetadataURI": "",
                "ipMetadataHash": ZERO_HASH,
                "nftMetadataURI": "",
                "nftMetadataHash": ZERO_HASH,
            }

            if ip_metadata:
                metadata.update(
                    {
                        "ipMetadataURI": ip_metadata.get("ip_metadata_uri", ""),
                        "ipMetadataHash": ip_metadata.get(
                            "ip_metadata_hash", ZERO_HASH
                        ),
                        "nftMetadataURI": ip_metadata.get("nft_metadata_uri", ""),
                        "nftMetadataHash": ip_metadata.get(
                            "nft_metadata_hash", ZERO_HASH
                        ),
                    }
                )

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.license_attachment_workflows_client.build_mintAndRegisterIpAndAttachPILTerms_transaction,
                spg_nft_contract,
                self._validate_recipient(recipient),
                metadata,
                license_terms,
                allow_duplicates,
                tx_options=tx_options,
            )

            ip_registered = self._parse_tx_ip_registered_event(response["tx_receipt"])[
                0
            ]
            license_terms_ids = self._parse_tx_license_terms_attached_event(
                response["tx_receipt"]
            )

            return {
                "tx_hash": response["tx_hash"],
                "ip_id": ip_registered["ip_id"],
                "license_terms_ids": license_terms_ids,
                "token_id": ip_registered["token_id"],
            }

        except Exception as e:
            raise e

    def mint_and_register_ip(
        self,
        spg_nft_contract: str,
        recipient: str | None = None,
        ip_metadata: dict | None = None,
        allow_duplicates: bool = True,
        tx_options: dict | None = None,
    ) -> dict:
        """
        Mint an NFT from a SPGNFT collection and register it with metadata as an IP.

        :param spg_nft_contract str: The address of the SPGNFT collection.
        :param recipient str: [Optional] The address of the recipient of the minted NFT,
            default value is your wallet address.
        :param ip_metadata dict: [Optional] The desired metadata for the newly minted NFT
            and newly registered IP.
            :param ip_metadata_uri str: [Optional] The URI of the metadata for the IP.
            :param ip_metadata_hash str: [Optional] The hash of the metadata for the IP.
            :param nft_metadata_uri str: [Optional] The URI of the metadata for the NFT.
            :param nft_metadata_hash str: [Optional] The hash of the metadata for the IP NFT.
        :param allow_duplicates bool: Set to true to allow minting an NFT with a duplicate
            metadata hash.
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash, IP ID and token ID.
        """
        try:
            metadata = {
                "ipMetadataURI": "",
                "ipMetadataHash": ZERO_HASH,
                "nftMetadataURI": "",
                "nftMetadataHash": ZERO_HASH,
            }

            if ip_metadata:
                metadata.update(
                    {
                        "ipMetadataURI": ip_metadata.get("ip_metadata_uri", ""),
                        "ipMetadataHash": ip_metadata.get(
                            "ip_metadata_hash", ZERO_HASH
                        ),
                        "nftMetadataURI": ip_metadata.get("nft_metadata_uri", ""),
                        "nftMetadataHash": ip_metadata.get(
                            "nft_metadata_hash", ZERO_HASH
                        ),
                    }
                )

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.registration_workflows_client.build_mintAndRegisterIp_transaction,
                spg_nft_contract,
                self._validate_recipient(recipient),
                metadata,
                allow_duplicates,
                tx_options=tx_options,
            )

            ip_registered = self._parse_tx_ip_registered_event(response["tx_receipt"])[
                0
            ]

            return {
                "tx_hash": response["tx_hash"],
                "ip_id": ip_registered["ip_id"],
                "token_id": ip_registered["token_id"],
            }

        except Exception as e:
            raise ValueError(f"Failed to mint and register IP: {str(e)}")

    def batch_mint_and_register_ip(
        self,
        requests: list[BatchMintAndRegisterIPInput],
        tx_options: dict | None = None,
    ) -> BatchMintAndRegisterIPResponse:
        """
        Batch mints NFTs from SPGNFT collections and registers them as IP assets.
        Optimizes transaction processing by grouping requests and  Uses `RegistrationWorkflows's multicall` for minting contracts.

          :param requests list[BatchMintAndRegisterIPInput]: The list of batch mint and register IP requests.
          :param tx_options: [Optional] The transaction options.
          :return `BatchMintAndRegisterIPResponse`: A response with transaction hash and list of `RegisteredIP` which includes IP ID and token ID.
        """
        try:
            encoded_data = []
            for request in requests:
                encoded_data.append(
                    self.registration_workflows_client.contract.encode_abi(
                        abi_element_identifier="mintAndRegisterIp",
                        args=[
                            validate_address(request.spg_nft_contract),
                            self._validate_recipient(request.recipient),
                            IPMetadata.from_input(
                                request.ip_metadata
                            ).get_validated_data(),
                            request.allow_duplicates,
                        ],
                    )
                )
            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.registration_workflows_client.build_multicall_transaction,
                encoded_data,
                tx_options=tx_options,
            )
            registered_ips = self._parse_tx_ip_registered_event(response["tx_receipt"])
            return BatchMintAndRegisterIPResponse(
                tx_hash=response["tx_hash"],
                registered_ips=registered_ips,
            )

        except Exception as e:
            raise ValueError(f"Failed to batch mint and register IP: {str(e)}")

    def register_ip_and_attach_pil_terms(
        self,
        nft_contract: str,
        token_id: int,
        license_terms_data: list,
        ip_metadata: dict | None = None,
        deadline: int | None = None,
        tx_options: dict | None = None,
    ) -> dict:
        """
        Register a given NFT as an IP and attach Programmable IP License Terms.

        :param nft_contract str: The address of the NFT collection.
        :param token_id int: The ID of the NFT.
        :param license_terms_data list: The PIL terms and licensing configuration data to be attached to the IP.
            :param terms dict: The PIL terms to be used for the licensing.
                :param transferable bool: Indicates whether the license is transferable or not.
                :param royalty_policy str: The address of the royalty policy contract which required to StoryProtocol in advance.
                :param minting_fee int: The fee to be paid when minting a license.
                :param expiration int: The expiration period of the license.
                :param commercial_use bool: Indicates whether the work can be used commercially or not.
                :param commercial_attribution bool: Whether attribution is required when reproducing the work commercially or not.
                :param commercializer_checker str: Commercializers that are allowed to commercially exploit the work.
                :param commercializer_checker_data str: The data to be passed to the commercializer checker contract.
                :param commercial_rev_share int: Percentage of revenue that must be shared with the licensor. Must be between 0 and 100 (where 100% represents 100,000,000).
                :param commercial_rev_ceiling int: The maximum revenue that can be generated from the commercial use of the work.
                :param derivatives_allowed bool: Indicates whether the licensee can create derivatives of his work or not.
                :param derivatives_attribution bool: Indicates whether attribution is required for derivatives of the work or not.
                :param derivatives_approval bool: Indicates whether the licensor must approve derivatives of the work before they can be linked.
                :param derivatives_reciprocal bool: Indicates whether the licensee must license derivatives under the same terms.
                :param derivative_rev_ceiling int: The maximum revenue that can be generated from the derivative use of the work.
                :param currency str: The ERC20 token to be used to pay the minting fee.
                :param uri str: The URI of the license terms.
            :param licensing_config dict: The PIL terms and licensing configuration data to attach to the IP.
                :param is_set bool: Whether the configuration is set or not.
                :param minting_fee int: The minting fee to be paid when minting license tokens.
                :param licensing_hook str: The hook contract address for the licensing module.
                :param hook_data str: The data to be used by the licensing hook.
                :param commercial_rev_share int: Percentage of revenue that must be shared with the licensor. Must be between 0 and 100 (where 100% represents 100,000,000).
                :param disabled bool: Whether the licensing is disabled or not.
                :param expect_minimum_group_reward_share int: The minimum percentage of the group's reward share. Must be between 0 and 100 (where 100% represents 100,000,000).
                :param expect_group_reward_pool str: The address of the expected group reward pool.
        :param ip_metadata dict: [Optional] The metadata for the newly registered IP.
            :param ip_metadata_uri str: [Optional] The URI of the metadata for the IP.
            :param ip_metadata_hash str: [Optional] The hash of the metadata for the IP.
            :param nft_metadata_uri str: [Optional] The URI of the metadata for the NFT.
            :param nft_metadata_hash str: [Optional] The hash of the metadata for the IP NFT.
        :param deadline int: [Optional] The deadline for the signature in seconds. (default: 1000 seconds)
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash, license terms ID, and IP ID.
        """
        try:
            ip_id = self._get_ip_id(nft_contract, token_id)
            if self._is_registered(ip_id):
                raise ValueError(
                    f"The NFT with id {token_id} is already registered as IP."
                )
            license_terms = self._validate_license_terms_data(license_terms_data)

            calculated_deadline = self.sign_util.get_deadline(deadline=deadline)

            # Get permission signature for all required permissions
            signature_response = self.sign_util.get_permission_signature(
                ip_id=ip_id,
                deadline=calculated_deadline,
                state=self.web3.to_bytes(hexstr=HexStr(ZERO_HASH)),
                permissions=[
                    {
                        "ipId": ip_id,
                        "signer": self.license_attachment_workflows_client.contract.address,
                        "to": self.core_metadata_module_client.contract.address,
                        "permission": AccessPermission.ALLOW,
                        "func": "setAll(address,string,bytes32,bytes32)",
                    },
                    {
                        "ipId": ip_id,
                        "signer": self.license_attachment_workflows_client.contract.address,
                        "to": self.licensing_module_client.contract.address,
                        "permission": AccessPermission.ALLOW,
                        "func": "attachLicenseTerms(address,address,uint256)",
                    },
                    {
                        "ipId": ip_id,
                        "signer": self.license_attachment_workflows_client.contract.address,
                        "to": self.licensing_module_client.contract.address,
                        "permission": AccessPermission.ALLOW,
                        "func": "setLicensingConfig(address,address,uint256,(bool,uint256,address,bytes,uint32,bool,uint32,address))",
                    },
                ],
            )

            metadata = {
                "ipMetadataURI": "",
                "ipMetadataHash": ZERO_HASH,
                "nftMetadataURI": "",
                "nftMetadataHash": ZERO_HASH,
            }

            if ip_metadata:
                metadata.update(
                    {
                        "ipMetadataURI": ip_metadata.get("ip_metadata_uri", ""),
                        "ipMetadataHash": ip_metadata.get(
                            "ip_metadata_hash", ZERO_HASH
                        ),
                        "nftMetadataURI": ip_metadata.get("nft_metadata_uri", ""),
                        "nftMetadataHash": ip_metadata.get(
                            "nft_metadata_hash", ZERO_HASH
                        ),
                    }
                )

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.license_attachment_workflows_client.build_registerIpAndAttachPILTerms_transaction,
                nft_contract,
                token_id,
                metadata,
                license_terms,
                {
                    "signer": self.web3.to_checksum_address(self.account.address),
                    "deadline": calculated_deadline,
                    "signature": signature_response["signature"],
                },
                tx_options=tx_options,
            )

            ip_registered = self._parse_tx_ip_registered_event(response["tx_receipt"])[
                0
            ]
            license_terms_ids = self._parse_tx_license_terms_attached_event(
                response["tx_receipt"]
            )

            return {
                "tx_hash": response["tx_hash"],
                "ip_id": ip_registered["ip_id"],
                "license_terms_ids": license_terms_ids,
                "token_id": ip_registered["token_id"],
            }

        except Exception as e:
            raise e

    def register_derivative_ip(
        self,
        nft_contract: str,
        token_id: int,
        deriv_data: DerivativeDataInput,
        metadata: IPMetadataInput | None = None,
        deadline: int | None = None,
        tx_options: dict | None = None,
    ) -> dict:
        """
        Register the given NFT as a derivative IP with metadata without using
        license tokens.

        :param nft_contract str: The address of the NFT collection.
        :param token_id int: The ID of the NFT.
        :param deriv_data `DerivativeDataInput`: The derivative data for registerDerivative.
        :param metadata `IPMetadataInput`: [Optional] Desired IP metadata.
        :param deadline int: [Optional] Signature deadline in seconds. (default: 1000 seconds)
        :param tx_options dict: [Optional] Transaction options.
        :return dict: Dictionary with the tx hash and IP ID.
        """
        try:
            ip_id = self._get_ip_id(nft_contract, token_id)
            if self._is_registered(ip_id):
                raise ValueError(
                    f"The NFT with id {token_id} is already registered as IP."
                )
            validated_deriv_data = DerivativeData.from_input(
                web3=self.web3, input_data=deriv_data
            ).get_validated_data()
            calculated_deadline = self.sign_util.get_deadline(deadline=deadline)
            sig_register_signature = self.sign_util.get_permission_signature(
                ip_id=ip_id,
                deadline=calculated_deadline,
                state=Web3.to_bytes(0),
                permissions=[
                    {
                        "ipId": ip_id,
                        "signer": self.derivative_workflows_client.contract.address,
                        "to": self.core_metadata_module_client.contract.address,
                        "permission": AccessPermission.ALLOW,
                        "func": get_function_signature(
                            self.core_metadata_module_client.contract.abi,
                            "setAll",
                        ),
                    },
                    {
                        "ipId": ip_id,
                        "signer": self.derivative_workflows_client.contract.address,
                        "to": self.licensing_module_client.contract.address,
                        "permission": AccessPermission.ALLOW,
                        "func": get_function_signature(
                            self.licensing_module_client.contract.abi,
                            "registerDerivative",
                        ),
                    },
                ],
            )
            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.derivative_workflows_client.build_registerIpAndMakeDerivative_transaction,
                nft_contract,
                token_id,
                validated_deriv_data,
                IPMetadata.from_input(metadata).get_validated_data(),
                {
                    "signer": self.account.address,
                    "deadline": calculated_deadline,
                    "signature": sig_register_signature["signature"],
                },
                tx_options=tx_options,
            )

            ip_registered = self._parse_tx_ip_registered_event(response["tx_receipt"])[
                0
            ]

            return {"tx_hash": response["tx_hash"], "ip_id": ip_registered["ip_id"]}

        except Exception as e:
            raise e

    def mint_and_register_ip_and_make_derivative(
        self,
        spg_nft_contract: str,
        deriv_data: DerivativeDataInput,
        ip_metadata: IPMetadataInput | None = None,
        recipient: Address | None = None,
        allow_duplicates: bool = True,
        tx_options: dict | None = None,
    ) -> RegistrationResponse:
        """
        Mint an NFT from a collection and register it as a derivative IP without license tokens.

        :param spg_nft_contract str: The address of the SPGNFT collection.
        :param deriv_data `DerivativeDataInput`: The derivative data to be used for register derivative.
        :param ip_metadata `IPMetadataInput`: [Optional] The desired metadata for the newly minted NFT and newly registered IP.
        :param recipient str: [Optional] The address to receive the minted NFT. If not provided, the client's own wallet address will be used.
        :param allow_duplicates bool: [Optional] Set to true to allow minting an NFT with a duplicate metadata hash. (default: True)
        :param tx_options dict: [Optional] Transaction options.
        :return RegistrationResponse: Dictionary with the tx hash, IP ID and token ID.
        """

        try:
            validated_deriv_data = DerivativeData.from_input(
                web3=self.web3, input_data=deriv_data
            ).get_validated_data()
            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.derivative_workflows_client.build_mintAndRegisterIpAndMakeDerivative_transaction,
                validate_address(spg_nft_contract),
                validated_deriv_data,
                IPMetadata.from_input(ip_metadata).get_validated_data(),
                self._validate_recipient(recipient),
                allow_duplicates,
                tx_options=tx_options,
            )
            ip_registered = self._parse_tx_ip_registered_event(response["tx_receipt"])[
                0
            ]
            return RegistrationResponse(
                tx_hash=response["tx_hash"],
                ip_id=ip_registered["ip_id"],
                token_id=ip_registered["token_id"],
            )
        except Exception as e:
            raise e

    def mint_and_register_ip_and_make_derivative_with_license_tokens(
        self,
        spg_nft_contract: Address,
        license_token_ids: list[int],
        max_rts: int,
        recipient: Address | None = None,
        allow_duplicates: bool = True,
        ip_metadata: IPMetadataInput | None = None,
        tx_options: dict | None = None,
    ) -> RegistrationResponse:
        """
        Mint an NFT from a collection and register it as a derivative IP with license tokens.

        :param spg_nft_contract Address: The address of the `SPGNFT` collection.
        :param license_token_ids list[int]: The IDs of the license tokens to be burned for linking the IP to parent IPs.
        :param max_rts int: The maximum number of royalty tokens that can be distributed to the external royalty policies (max: 100,000,000).
        :param recipient Address: [Optional] The address to receive the minted NFT. If not provided, the client's own wallet address will be used.
        :param allow_duplicates bool: [Optional] Set to true to allow minting an NFT with a duplicate metadata hash. (default: True)
        :param ip_metadata IPMetadataInput: [Optional] The desired metadata for the newly minted NFT and newly registered IP.
        :param tx_options dict: [Optional] Transaction options.
        :return RegistrationResponse: Dictionary with the tx hash, IP ID and token ID.
        """
        try:
            validated_license_token_ids = self._validate_license_token_ids(
                license_token_ids
            )
            validate_max_rts(max_rts)
            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.derivative_workflows_client.build_mintAndRegisterIpAndMakeDerivativeWithLicenseTokens_transaction,
                validate_address(spg_nft_contract),
                validated_license_token_ids,
                ZERO_ADDRESS,
                max_rts,
                IPMetadata.from_input(ip_metadata).get_validated_data(),
                self._validate_recipient(recipient),
                allow_duplicates,
                tx_options=tx_options,
            )
            ip_registered = self._parse_tx_ip_registered_event(response["tx_receipt"])[
                0
            ]
            return RegistrationResponse(
                tx_hash=response["tx_hash"],
                ip_id=ip_registered["ip_id"],
                token_id=ip_registered["token_id"],
            )
        except Exception as e:
            raise e

    def register_ip_and_make_derivative_with_license_tokens(
        self,
        nft_contract: str,
        token_id: int,
        license_token_ids: list[int],
        max_rts: int = 100_000_000,
        deadline: int = 1000,
        ip_metadata: IPMetadataInput | None = None,
        tx_options: dict | None = None,
    ) -> RegistrationResponse:
        """
        Register the given NFT as a derivative IP using license tokens.

        :param nft_contract str: The address of the NFT collection.
        :param token_id int: The ID of the NFT.
        :param license_token_ids list[int]: The IDs of the license tokens to be burned for linking the IP to parent IPs.
        :param max_rts int: [Optional] The maximum number of royalty tokens that can be distributed to the external royalty policies (max: 100,000,000). (default: 100,000,000)
        :param deadline int: [Optional] Signature deadline in seconds. (default: 1000 seconds)
        :param ip_metadata IPMetadataInput: [Optional] The desired metadata for the newly registered IP.
        :param tx_options dict: [Optional] Transaction options.
        :return RegistrationResponse: Dictionary with the tx hash, IP ID and token ID.
        """
        try:
            ip_id = self._get_ip_id(nft_contract, token_id)
            if self._is_registered(ip_id):
                raise ValueError(
                    f"The NFT with id {token_id} is already registered as IP."
                )

            # Validate license token IDs and ownership
            validated_license_token_ids = self._validate_license_token_ids(
                license_token_ids
            )

            # Validate max_rts
            validate_max_rts(max_rts)

            calculated_deadline = self.sign_util.get_deadline(deadline=deadline)

            # Get permission signature for registration and derivative
            signature_response = self.sign_util.get_permission_signature(
                ip_id=ip_id,
                deadline=calculated_deadline,
                state=Web3.to_bytes(0),
                permissions=[
                    {
                        "ipId": ip_id,
                        "signer": self.derivative_workflows_client.contract.address,
                        "to": self.core_metadata_module_client.contract.address,
                        "permission": AccessPermission.ALLOW,
                        "func": get_function_signature(
                            self.core_metadata_module_client.contract.abi,
                            "setAll",
                        ),
                    },
                    {
                        "ipId": ip_id,
                        "signer": self.derivative_workflows_client.contract.address,
                        "to": self.licensing_module_client.contract.address,
                        "permission": AccessPermission.ALLOW,
                        "func": get_function_signature(
                            self.licensing_module_client.contract.abi,
                            "registerDerivativeWithLicenseTokens",
                        ),
                    },
                ],
            )

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.derivative_workflows_client.build_registerIpAndMakeDerivativeWithLicenseTokens_transaction,
                validate_address(nft_contract),
                token_id,
                validated_license_token_ids,
                ZERO_ADDRESS,  # royaltyContext
                max_rts,
                IPMetadata.from_input(ip_metadata).get_validated_data(),
                {
                    "signer": self.web3.to_checksum_address(self.account.address),
                    "deadline": calculated_deadline,
                    "signature": signature_response["signature"],
                },
                tx_options=tx_options,
            )

            ip_registered = self._parse_tx_ip_registered_event(response["tx_receipt"])[
                0
            ]

            return RegistrationResponse(
                tx_hash=response["tx_hash"],
                ip_id=ip_registered["ip_id"],
                token_id=ip_registered["token_id"],
            )

        except Exception as e:
            raise ValueError(
                f"Failed to register IP and make derivative with license tokens: {str(e)}"
            ) from e

    def mint_and_register_ip_and_attach_pil_terms_and_distribute_royalty_tokens(
        self,
        spg_nft_contract: Address,
        license_terms_data: list[LicenseTermsDataInput],
        royalty_shares: list[RoyaltyShareInput],
        ip_metadata: IPMetadataInput | None = None,
        recipient: Address | None = None,
        allow_duplicates: bool = True,
        tx_options: dict | None = None,
    ) -> RegistrationWithRoyaltyVaultAndLicenseTermsResponse:
        """
        Mint an NFT and register the IP, attach PIL terms, and distribute royalty tokens.

        :param spg_nft_contract Address: The address of the SPGNFT collection.
        :param license_terms_data `list[LicenseTermsDataInput]`: The PIL terms and licensing configuration data to be attached to the IP.
        :param royalty_shares `list[RoyaltyShareInput]`: The royalty shares to be distributed.
        :param ip_metadata `IPMetadataInput`: [Optional] The desired metadata for the newly minted NFT and newly registered IP.
        :param recipient Address: [Optional] The address to receive the minted NFT. If not provided, the client's own wallet address will be used.
        :param allow_duplicates bool: [Optional] Set to false to prevent minting an NFT with a duplicate metadata hash. (default: True)
        :param tx_options dict: [Optional] Transaction options.
        :return `RegistrationWithRoyaltyVaultAndLicenseTermsResponse`: Response with tx hash, IP ID, token ID, license terms IDs, and royalty vault address.
        """
        try:
            validated_royalty_shares = get_royalty_shares(royalty_shares)[
                "royalty_shares"
            ]
            license_terms = self._validate_license_terms_data(license_terms_data)

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.royalty_token_distribution_workflows_client.build_mintAndRegisterIpAndAttachPILTermsAndDistributeRoyaltyTokens_transaction,
                validate_address(spg_nft_contract),
                self._validate_recipient(recipient),
                IPMetadata.from_input(ip_metadata).get_validated_data(),
                license_terms,
                validated_royalty_shares,
                allow_duplicates,
                tx_options=tx_options,
            )

            ip_registered = self._parse_tx_ip_registered_event(response["tx_receipt"])[
                0
            ]
            license_terms_ids = self._parse_tx_license_terms_attached_event(
                response["tx_receipt"]
            )
            royalty_vault = self.get_royalty_vault_address_by_ip_id(
                response["tx_receipt"],
                ip_registered["ip_id"],
            )

            return RegistrationWithRoyaltyVaultAndLicenseTermsResponse(
                tx_hash=response["tx_hash"],
                ip_id=ip_registered["ip_id"],
                token_id=ip_registered["token_id"],
                license_terms_ids=license_terms_ids,
                royalty_vault=royalty_vault,
            )
        except Exception as e:
            raise ValueError(
                f"Failed to mint, register IP, attach PIL terms and distribute royalty tokens: {str(e)}"
            ) from e

    def mint_and_register_ip_and_make_derivative_and_distribute_royalty_tokens(
        self,
        spg_nft_contract: Address,
        deriv_data: DerivativeDataInput,
        royalty_shares: list[RoyaltyShareInput],
        ip_metadata: IPMetadataInput | None = None,
        recipient: Address | None = None,
        allow_duplicates: bool = True,
        tx_options: dict | None = None,
    ) -> RegistrationWithRoyaltyVaultResponse:
        """
        Mint an NFT and register the IP, make a derivative, and distribute royalty tokens.

         :param spg_nft_contract Address: The address of the SPGNFT collection.
         :param deriv_data `DerivativeDataInput`: The derivative data to be used for register derivative.
         :param royalty_shares `list[RoyaltyShareInput]`: The royalty shares to be distributed.
         :param ip_metadata `IPMetadataInput`: [Optional] The desired metadata for the newly minted NFT and newly registered IP.
         :param recipient Address: [Optional] The address to receive the minted NFT. If not provided, the client's own wallet address will be used.
         :param allow_duplicates bool: [Optional] Set to true to allow minting an NFT with a duplicate metadata hash. (default: True)
         :param tx_options dict: [Optional] Transaction options.
         :return `RegistrationWithRoyaltyVaultResponse`: Dictionary with the tx hash, IP ID and token ID, royalty vault.
        """
        try:
            validated_royalty_shares_obj = get_royalty_shares(royalty_shares)
            validated_deriv_data = DerivativeData.from_input(
                web3=self.web3, input_data=deriv_data
            ).get_validated_data()

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.royalty_token_distribution_workflows_client.build_mintAndRegisterIpAndMakeDerivativeAndDistributeRoyaltyTokens_transaction,
                validate_address(spg_nft_contract),
                self._validate_recipient(recipient),
                IPMetadata.from_input(ip_metadata).get_validated_data(),
                validated_deriv_data,
                validated_royalty_shares_obj["royalty_shares"],
                allow_duplicates,
                tx_options=tx_options,
            )

            ip_registered = self._parse_tx_ip_registered_event(response["tx_receipt"])[
                0
            ]
            royalty_vault = self.get_royalty_vault_address_by_ip_id(
                response["tx_receipt"],
                ip_registered["ip_id"],
            )

            return RegistrationWithRoyaltyVaultResponse(
                tx_hash=response["tx_hash"],
                ip_id=ip_registered["ip_id"],
                token_id=ip_registered["token_id"],
                royalty_vault=royalty_vault,
            )
        except Exception as e:
            raise ValueError(
                f"Failed to mint, register IP, make derivative and distribute royalty tokens: {str(e)}"
            ) from e

    def register_derivative_ip_and_attach_pil_terms_and_distribute_royalty_tokens(
        self,
        nft_contract: Address,
        token_id: int,
        deriv_data: DerivativeDataInput,
        royalty_shares: list[RoyaltyShareInput],
        ip_metadata: IPMetadataInput | None = None,
        deadline: int = 1000,
        tx_options: dict | None = None,
    ) -> RegisterDerivativeIPAndAttachAndDistributeRoyaltyTokensResponse:
        """
        Register the given NFT as a derivative IP, attach license terms from parent IPs, and distribute royalty tokens.
        In order to successfully distribute royalty tokens, the first license terms attached to the IP must be a commercial license.

         :param nft_contract Address: The address of the NFT collection.
         :param token_id int: The ID of the NFT.
         :param deriv_data `DerivativeDataInput`: The derivative data to be used for register derivative.
         :param royalty_shares `list[RoyaltyShareInput]`: Authors of the IP and their shares of the royalty tokens.
         :param ip_metadata `IPMetadataInput`: [Optional] The metadata for the newly registered IP.
         :param deadline int: [Optional] The deadline for the signature in seconds. (default: 1000 seconds)
         :param tx_options dict: [Optional] Transaction options.
         :return `RegisterDerivativeIPAndAttachAndDistributeRoyaltyTokensResponse`: Response with tx hash, IP ID, token ID, royalty vault address, and distribute royalty tokens transaction hash.
        """
        try:
            nft_contract = validate_address(nft_contract)
            ip_id = self._get_ip_id(nft_contract, token_id)
            if self._is_registered(ip_id):
                raise ValueError(
                    f"The NFT with id {token_id} is already registered as IP."
                )

            validated_deriv_data = DerivativeData.from_input(
                web3=self.web3, input_data=deriv_data
            ).get_validated_data()
            calculated_deadline = self.sign_util.get_deadline(deadline=deadline)
            royalty_shares_obj = get_royalty_shares(royalty_shares)

            signature_response = self.sign_util.get_permission_signature(
                ip_id=ip_id,
                deadline=calculated_deadline,
                state=self.web3.to_bytes(hexstr=HexStr(ZERO_HASH)),
                permissions=[
                    {
                        "ipId": ip_id,
                        "signer": self.royalty_token_distribution_workflows_client.contract.address,
                        "to": self.core_metadata_module_client.contract.address,
                        "permission": AccessPermission.ALLOW,
                        "func": "setAll(address,string,bytes32,bytes32)",
                    },
                    {
                        "ipId": ip_id,
                        "signer": self.royalty_token_distribution_workflows_client.contract.address,
                        "to": self.licensing_module_client.contract.address,
                        "permission": AccessPermission.ALLOW,
                        "func": "registerDerivative(address,address[],uint256[],address,bytes,uint256,uint32,uint32)",
                    },
                ],
            )

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.royalty_token_distribution_workflows_client.build_registerIpAndMakeDerivativeAndDeployRoyaltyVault_transaction,
                nft_contract,
                token_id,
                IPMetadata.from_input(ip_metadata).get_validated_data(),
                validated_deriv_data,
                {
                    "signer": self.web3.to_checksum_address(self.account.address),
                    "deadline": calculated_deadline,
                    "signature": signature_response["signature"],
                },
                tx_options=tx_options,
            )

            ip_registered = self._parse_tx_ip_registered_event(response["tx_receipt"])[
                0
            ]
            royalty_vault = self.get_royalty_vault_address_by_ip_id(
                response["tx_receipt"],
                ip_registered["ip_id"],
            )

            # Distribute royalty tokens
            distribute_tx_hash = self._distribute_royalty_tokens(
                ip_id=ip_registered["ip_id"],
                royalty_shares=royalty_shares_obj["royalty_shares"],
                royalty_vault=royalty_vault,
                total_amount=royalty_shares_obj["total_amount"],
                tx_options=tx_options,
                deadline=calculated_deadline,
            )

            return RegisterDerivativeIPAndAttachAndDistributeRoyaltyTokensResponse(
                tx_hash=response["tx_hash"],
                ip_id=ip_registered["ip_id"],
                token_id=ip_registered["token_id"],
                royalty_vault=royalty_vault,
                distribute_royalty_tokens_tx_hash=distribute_tx_hash,
            )
        except Exception as e:
            raise ValueError(
                f"Failed to register derivative IP and distribute royalty tokens: {str(e)}"
            ) from e

    def register_ip_and_attach_pil_terms_and_distribute_royalty_tokens(
        self,
        nft_contract: Address,
        token_id: int,
        license_terms_data: list[LicenseTermsDataInput],
        royalty_shares: list[RoyaltyShareInput],
        ip_metadata: IPMetadataInput | None = None,
        deadline: int | None = None,
        tx_options: dict | None = None,
    ) -> RegisterAndAttachAndDistributeRoyaltyTokensResponse:
        """
        Register the given NFT and attach license terms and distribute royalty
        tokens. In order to successfully distribute royalty tokens, the first license terms
        attached to the IP must be a commercial license.

         :param nft_contract Address: The address of the NFT collection.
         :param token_id int: The ID of the NFT.
         :param license_terms_data `list[LicenseTermsDataInput]`: The data of the license and its configuration to be attached to the new group IP.
         :param royalty_shares `list[RoyaltyShareInput]`: Authors of the IP and their shares of the royalty tokens.
         :param ip_metadata `IPMetadataInput`: [Optional] The metadata for the newly registered IP.
         :param deadline int: [Optional] The deadline for the signature in seconds. (default: 1000 seconds)
         :param tx_options dict: [Optional] Transaction options.
         :return `RegisterAndAttachAndDistributeRoyaltyTokensResponse`: Response with tx hash, license terms IDs, royalty vault address, and distribute royalty tokens transaction hash.
        """
        try:
            nft_contract = validate_address(nft_contract)
            ip_id = self._get_ip_id(nft_contract, token_id)
            if self._is_registered(ip_id):
                raise ValueError(
                    f"The NFT with id {token_id} is already registered as IP."
                )

            license_terms = self._validate_license_terms_data(license_terms_data)
            calculated_deadline = self.sign_util.get_deadline(deadline=deadline)
            royalty_shares_obj = get_royalty_shares(royalty_shares)

            signature_response = self.sign_util.get_permission_signature(
                ip_id=ip_id,
                deadline=calculated_deadline,
                state=self.web3.to_bytes(hexstr=HexStr(ZERO_HASH)),
                permissions=[
                    {
                        "ipId": ip_id,
                        "signer": self.royalty_token_distribution_workflows_client.contract.address,
                        "to": self.core_metadata_module_client.contract.address,
                        "permission": AccessPermission.ALLOW,
                        "func": "setAll(address,string,bytes32,bytes32)",
                    },
                    {
                        "ipId": ip_id,
                        "signer": self.royalty_token_distribution_workflows_client.contract.address,
                        "to": self.licensing_module_client.contract.address,
                        "permission": AccessPermission.ALLOW,
                        "func": "attachLicenseTerms(address,address,uint256)",
                    },
                    {
                        "ipId": ip_id,
                        "signer": self.royalty_token_distribution_workflows_client.contract.address,
                        "to": self.licensing_module_client.contract.address,
                        "permission": AccessPermission.ALLOW,
                        "func": "setLicensingConfig(address,address,uint256,(bool,uint256,address,bytes,uint32,bool,uint32,address))",
                    },
                ],
            )

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.royalty_token_distribution_workflows_client.build_registerIpAndAttachPILTermsAndDeployRoyaltyVault_transaction,
                nft_contract,
                token_id,
                IPMetadata.from_input(ip_metadata).get_validated_data(),
                license_terms,
                {
                    "signer": self.web3.to_checksum_address(self.account.address),
                    "deadline": calculated_deadline,
                    "signature": signature_response["signature"],
                },
                tx_options=tx_options,
            )
            ip_registered = self._parse_tx_ip_registered_event(response["tx_receipt"])[
                0
            ]
            license_terms_ids = self._parse_tx_license_terms_attached_event(
                response["tx_receipt"]
            )
            royalty_vault = self.get_royalty_vault_address_by_ip_id(
                response["tx_receipt"],
                ip_registered["ip_id"],
            )

            # Distribute royalty tokens
            distribute_tx_hash = self._distribute_royalty_tokens(
                ip_id=ip_registered["ip_id"],
                royalty_shares=royalty_shares_obj["royalty_shares"],
                royalty_vault=royalty_vault,
                total_amount=royalty_shares_obj["total_amount"],
                tx_options=tx_options,
                deadline=calculated_deadline,
            )

            return RegisterAndAttachAndDistributeRoyaltyTokensResponse(
                tx_hash=response["tx_hash"],
                license_terms_ids=license_terms_ids,
                royalty_vault=royalty_vault,
                distribute_royalty_tokens_tx_hash=distribute_tx_hash,
                ip_id=ip_registered["ip_id"],
                token_id=ip_registered["token_id"],
            )
        except Exception as e:
            raise ValueError(
                f"Failed to register IP, attach PIL terms and distribute royalty tokens: {str(e)}"
            ) from e

    def register_pil_terms_and_attach(
        self,
        ip_id: Address,
        license_terms_data: list,
        deadline: int | None = None,
        tx_options: dict | None = None,
    ) -> RegisterPILTermsAndAttachResponse:
        """
        Register Programmable IP License Terms (if unregistered) and attach it to IP.

         :param ip_id Address: The IP ID.
         :param license_terms_data list: The data of the license and its configuration to be attached to the IP.
         :param deadline int: [Optional] Signature deadline in seconds. (default: 1000 seconds)
         :param tx_options dict: [Optional] Transaction options.
         :return RegisterPILTermsAndAttachResponse: Dictionary with the tx hash and license terms IDs.
        """
        try:
            if not self._is_registered(ip_id):
                raise ValueError(f"The IP with id {ip_id} is not registered.")
            calculated_deadline = self.sign_util.get_deadline(deadline=deadline)
            ip_account_impl_client = IPAccountImplClient(self.web3, ip_id)
            state = ip_account_impl_client.state()
            license_terms = self._validate_license_terms_data(license_terms_data)
            signature_response = self.sign_util.get_permission_signature(
                ip_id=ip_id,
                deadline=calculated_deadline,
                state=state,
                permissions=[
                    {
                        "ipId": ip_id,
                        "signer": self.license_attachment_workflows_client.contract.address,
                        "to": self.licensing_module_client.contract.address,
                        "permission": AccessPermission.ALLOW,
                        "func": get_function_signature(
                            self.licensing_module_client.contract.abi,
                            "attachLicenseTerms",
                        ),
                    },
                    {
                        "ipId": ip_id,
                        "signer": self.license_attachment_workflows_client.contract.address,
                        "to": self.licensing_module_client.contract.address,
                        "permission": AccessPermission.ALLOW,
                        "func": get_function_signature(
                            self.licensing_module_client.contract.abi,
                            "setLicensingConfig",
                        ),
                    },
                ],
            )
            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.license_attachment_workflows_client.build_registerPILTermsAndAttach_transaction,
                ip_id,
                license_terms,
                {
                    "signer": self.web3.to_checksum_address(self.account.address),
                    "deadline": calculated_deadline,
                    "signature": signature_response["signature"],
                },
                tx_options=tx_options,
            )
            license_terms_ids = self._parse_tx_license_terms_attached_event(
                response["tx_receipt"]
            )
            return RegisterPILTermsAndAttachResponse(
                tx_hash=response["tx_hash"],
                license_terms_ids=license_terms_ids,
            )
        except Exception as e:
            raise e

    def _validate_derivative_data(self, derivative_data: dict) -> dict:
        """
        Validates the derivative data and returns processed internal data.

        :param derivative_data dict: The derivative data to validate
        :return dict: The processed internal derivative data
        :raises ValueError: If validation fails
        """
        internal_data = {
            "childIpId": derivative_data["childIpId"],
            "parentIpIds": derivative_data["parentIpIds"],
            "licenseTermsIds": [int(id) for id in derivative_data["licenseTermsIds"]],
            "licenseTemplate": (
                derivative_data.get("licenseTemplate")
                if derivative_data.get("licenseTemplate") is not None
                else self.pi_license_template_client.contract.address
            ),
            "royaltyContext": ZERO_ADDRESS,
            "maxMintingFee": int(derivative_data.get("maxMintingFee", 0)),
            "maxRts": int(derivative_data.get("maxRts", 0)),
            "maxRevenueShare": int(derivative_data.get("maxRevenueShare", 0)),
        }

        if not internal_data["parentIpIds"]:
            raise ValueError("The parent IP IDs must be provided.")

        if not internal_data["licenseTermsIds"]:
            raise ValueError("The license terms IDs must be provided.")

        if len(internal_data["parentIpIds"]) != len(internal_data["licenseTermsIds"]):
            raise ValueError(
                "The number of parent IP IDs must match the number of license terms IDs."
            )

        if internal_data["maxMintingFee"] < 0:
            raise ValueError("The maxMintingFee must be greater than 0.")

        validate_max_rts(internal_data["maxRts"])

        for parent_id, terms_id in zip(
            internal_data["parentIpIds"], internal_data["licenseTermsIds"]
        ):
            if not self._is_registered(parent_id):
                raise ValueError(
                    f"The parent IP with id {parent_id} is not registered."
                )

            if not self.license_registry_client.hasIpAttachedLicenseTerms(
                parent_id, internal_data["licenseTemplate"], terms_id
            ):
                raise ValueError(
                    f"License terms id {terms_id} must be attached to the parent ipId "
                    f"{parent_id} before registering derivative."
                )

            royalty_percent = self.license_registry_client.getRoyaltyPercent(
                parent_id, internal_data["licenseTemplate"], terms_id
            )
            if (
                internal_data["maxRevenueShare"] != 0
                and royalty_percent > internal_data["maxRevenueShare"]
            ):
                raise ValueError(
                    f"The royalty percent for the parent IP with id {parent_id} is greater "
                    f"than the maximum revenue share {internal_data['maxRevenueShare']}."
                )

        return internal_data

    def _validate_license_token_ids(self, license_token_ids: list) -> list:
        """
        Validates the license token IDs and checks ownership.

        :param license_token_ids list: The IDs of the license tokens to validate
        :return list: The validated and converted license token IDs
        :raises ValueError: If validation fails
        """
        if not license_token_ids:
            raise ValueError("License token IDs must be provided.")

        # Convert all IDs to integers
        license_token_ids = [int(id) for id in license_token_ids]

        # Validate ownership of each token
        for token_id in license_token_ids:
            token_owner = self.license_token_client.ownerOf(token_id)
            if not token_owner or token_owner.lower() != self.account.address.lower():
                raise ValueError(
                    f"License token id {token_id} must be owned by the caller."
                )

        return license_token_ids

    def _distribute_royalty_tokens(
        self,
        ip_id: Address,
        royalty_shares: list[RoyaltyShareInput],
        deadline: int,
        royalty_vault: Address,
        total_amount: int,
        tx_options: dict | None = None,
    ) -> HexStr:
        """
        Distribute royalty tokens to specified recipients.

        This is an internal method that handles the distribution of royalty tokens
        from an IP's royalty vault to the specified recipients.

        :param ip_id Address: The IP ID.
        :param royalty_shares list[RoyaltyShareInput]: The validated royalty shares with recipient and percentage.
        :param deadline int: The deadline for the signature.
        :param royalty_vault Address: The address of the royalty vault.
        :param total_amount int: The total amount of royalty tokens to distribute.
        :param tx_options dict: [Optional] Transaction options.
        :return HexStr: The transaction hash.
        """
        try:
            ip_account_impl_client = IPAccountImplClient(self.web3, ip_id)
            state = ip_account_impl_client.state()

            ip_royalty_vault_client = IpRoyaltyVaultImplClient(self.web3, royalty_vault)

            signature_response = self.sign_util.get_signature(
                state=state,
                to=royalty_vault,
                encode_data=ip_royalty_vault_client.contract.encode_abi(
                    abi_element_identifier="approve",
                    args=[
                        self.royalty_token_distribution_workflows_client.contract.address,
                        total_amount,
                    ],
                ),
                verifying_contract=ip_id,
                deadline=deadline,
            )

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.royalty_token_distribution_workflows_client.build_distributeRoyaltyTokens_transaction,
                ip_id,
                royalty_shares,
                {
                    "signer": self.web3.to_checksum_address(self.account.address),
                    "deadline": deadline,
                    "signature": signature_response["signature"],
                },
                tx_options=tx_options,
            )

            return response["tx_hash"]

        except Exception as e:
            raise ValueError(f"Failed to distribute royalty tokens: {str(e)}") from e

    def _get_ip_id(self, token_contract: str, token_id: int) -> str:
        """
        Get the IP ID for a given token.

        :param token_contract str: The NFT contract address.
        :param token_id int: The token identifier.
        :return str: The IP ID.
        """
        return self.ip_asset_registry_client.ipId(
            self.chain_id, token_contract, token_id
        )

    def _is_registered(self, ip_id: str) -> bool:
        """
        Check if an IP is registered.

        :param ip_id str: The IP ID to check.
        :return bool: True if registered, False otherwise.
        """
        return self.ip_asset_registry_client.isRegistered(ip_id)

    def _parse_tx_ip_registered_event(self, tx_receipt: dict) -> list[RegisteredIP]:
        """
        Parse the IPRegistered event from a transaction receipt.

        :param tx_receipt dict: The transaction receipt.
        :return int: The IP ID and token ID from the event, or None.
        """
        event_signature = self.web3.keccak(
            text="IPRegistered(address,uint256,address,uint256,string,string,uint256)"
        ).hex()
        registered_ips: list[RegisteredIP] = []
        for log in tx_receipt["logs"]:
            if log["topics"][0].hex() == event_signature:
                event_result = self.ip_asset_registry_client.contract.events.IPRegistered.process_log(
                    log
                )
                registered_ips.append(
                    RegisteredIP(
                        ip_id=event_result["args"]["ipId"],
                        token_id=event_result["args"]["tokenId"],
                    )
                )
        return registered_ips

    def _parse_tx_license_term_attached_event(self, tx_receipt: dict) -> int | None:
        """
        Parse the LicenseTermsAttached event from a transaction receipt.

        :param tx_receipt dict: The transaction receipt.
        :return int: The license terms ID or None if not found.
        """
        event_signature = self.web3.keccak(
            text="LicenseTermsAttached(address,address,address,uint256)"
        ).hex()

        for log in tx_receipt["logs"]:
            if log["topics"][0].hex() == event_signature:
                data = log["data"]
                license_terms_id = int.from_bytes(data[-32:], byteorder="big")
                return license_terms_id
        return None

    def _parse_tx_license_terms_attached_event(self, tx_receipt: dict) -> list[int]:
        """
        Parse the LicenseTermsAttached events from a transaction receipt.

        :param tx_receipt dict: The transaction receipt.
        :return list: A list of license terms IDs or None if none found.
        """
        event_signature = self.web3.keccak(
            text="LicenseTermsAttached(address,address,address,uint256)"
        ).hex()
        license_terms_ids = []

        for log in tx_receipt["logs"]:
            if log["topics"][0].hex() == event_signature:
                data = log["data"]
                license_terms_id = int.from_bytes(data[-32:], byteorder="big")
                license_terms_ids.append(license_terms_id)

        return license_terms_ids

    def get_royalty_vault_address_by_ip_id(
        self, tx_receipt: dict, ipId: Address
    ) -> Address:
        """
        Parse the IpRoyaltyVaultDeployed event from a transaction receipt and return the royalty vault address for a given IP ID.

        :param tx_receipt dict: The transaction receipt.
        :param ipId Address: The IP ID.
        :return Address: The royalty vault address.
        """
        event_signature = Web3.keccak(
            text="IpRoyaltyVaultDeployed(address,address)"
        ).hex()
        for log in tx_receipt["logs"]:
            if log["topics"][0].hex() == event_signature:
                event_result = self.royalty_module_client.contract.events.IpRoyaltyVaultDeployed.process_log(
                    log
                )
                if event_result["args"]["ipId"] == ipId:
                    return event_result["args"]["ipRoyaltyVault"]

    def _validate_recipient(self, recipient: Address | None) -> Address:
        """
        Validate the recipient address.

        :param recipient Address: The recipient address to validate.
        :return Address: The validated recipient address.
        """
        if recipient is None:
            return self.account.address
        return validate_address(recipient)

    def _validate_license_terms_data(
        self, license_terms_data: list[LicenseTermsDataInput] | list[dict]
    ) -> list:
        """
        Validate the license terms data.

        :param license_terms_data `list[LicenseTermsDataInput]` or `list[dict]`: The license terms data to validate.
        :return list: The validated license terms data.
        """

        validated_license_terms_data = []
        for term in license_terms_data:
            if is_dataclass(term):
                terms_dict = asdict(term.terms)
                licensing_config_dict = term.licensing_config
            else:
                terms_dict = term["terms"]
                licensing_config_dict = term["licensing_config"]

            validated_license_terms_data.append(
                {
                    "terms": self.license_terms_util.validate_license_terms(terms_dict),
                    "licensingConfig": self.license_terms_util.validate_licensing_config(
                        licensing_config_dict
                    ),
                }
            )
        return validated_license_terms_data
