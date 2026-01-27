from dataclasses import dataclass
from typing import Literal, TypedDict

from ens.ens import Address, HexStr

from story_protocol_python_sdk.types.resource.License import LicenseTermsInput
from story_protocol_python_sdk.types.resource.Royalty import RoyaltyShareInput
from story_protocol_python_sdk.utils.derivative_data import DerivativeDataInput
from story_protocol_python_sdk.utils.ip_metadata import IPMetadataInput
from story_protocol_python_sdk.utils.licensing_config_data import LicensingConfig


class RegisteredIP(TypedDict):
    """
    Data structure for IP and token ID.

    Attributes:
        ip_id: The IP ID of the registered IP asset.
        token_id: The token ID of the registered IP asset
    """

    ip_id: Address
    token_id: int


class RegistrationResponse(RegisteredIP):
    """
    Response structure for IP asset registration operations.
    Extends `RegisteredIP` with transaction hash.

    Attributes:
        tx_hash: The transaction hash of the registration transaction
    """

    tx_hash: HexStr


class RegistrationWithRoyaltyVaultResponse(RegistrationResponse):
    """
    Response structure for IP asset registration operations with royalty vault.

    Extends `RegistrationResponse` with royalty vault information.

    Attributes:
        royalty_vault: The royalty vault address of the registered IP asset
    """

    royalty_vault: Address


class RegistrationWithRoyaltyVaultAndLicenseTermsResponse(
    RegistrationWithRoyaltyVaultResponse
):
    """
    Response structure for IP asset registration operations with royalty vault and license terms.

    Extends `RegistrationWithRoyaltyVaultResponse` with license terms information.

    Attributes:
        license_terms_ids: The IDs of the license terms attached to the IP asset.
    """

    license_terms_ids: list[int]


class RegisterPILTermsAndAttachResponse(TypedDict):
    """
    Response structure for Programmable IP License Terms registration and attachment operations.

    Attributes:
        tx_hash: The transaction hash of the registration transaction
        license_terms_ids: The IDs of the registered license terms
    """

    tx_hash: HexStr
    license_terms_ids: list[int]


class RegisterAndAttachAndDistributeRoyaltyTokensResponse(
    RegistrationWithRoyaltyVaultAndLicenseTermsResponse
):
    """
    Response structure for IP asset registration operations with royalty vault, license terms and distribute royalty tokens.

    Extends `RegistrationWithRoyaltyVaultAndLicenseTermsResponse` with distribute royalty tokens transaction hash.

    Attributes:
        distribute_royalty_tokens_tx_hash: The transaction hash of the distribute royalty tokens transaction.
    """

    distribute_royalty_tokens_tx_hash: HexStr


class RegisterDerivativeIPAndAttachAndDistributeRoyaltyTokensResponse(
    RegistrationResponse
):
    """
    Response structure for derivative IP and attach PIL terms and distribute royalty tokens.

    Extends `RegistrationResponse` with distribute royalty tokens transaction hash.

    Attributes:
        distribute_royalty_tokens_tx_hash: The transaction hash of the distribute royalty tokens transaction.
        royalty_vault: The royalty vault address of the registered IP asset.
    """

    distribute_royalty_tokens_tx_hash: HexStr
    royalty_vault: Address


@dataclass
class LicenseTermsDataInput:
    """
    Data structure for license terms.

    Attributes:
        terms: The terms of the license.
        licensing_config: The licensing configuration of the license.
    """

    terms: LicenseTermsInput
    licensing_config: LicensingConfig


@dataclass
class BatchMintAndRegisterIPInput:
    """
    Data structure for batch mint and register IP.

    Attributes:
        spg_nft_contract: The address of the SPGNFT collection.
        recipient: [Optional] The address of the recipient of the minted NFT,
        ip_metadata: [Optional] The desired metadata for the newly minted NFT and newly registered IP.
        allow_duplicates: [Optional] Set to true to allow minting an NFT with a duplicate metadata hash. (default: True)
    """

    spg_nft_contract: Address
    ip_metadata: IPMetadataInput | None = None
    allow_duplicates: bool = True
    recipient: Address | None = None


class BatchMintAndRegisterIPResponse(TypedDict):
    """
    Response structure for batch mint and register IP.

    Attributes:
        tx_hash: The transaction hash of the batch mint and register IP transaction.
        registered_ips: The list of `RegisteredIP` which includes IP ID and token ID.
    """

    tx_hash: HexStr
    registered_ips: list[RegisteredIP]


@dataclass
class MintNFT:
    """
    Configuration for minting a new NFT from an SPG NFT contract.

    Attributes:
        type: Must be "mint" to indicate a new NFT will be minted.
        spg_nft_contract: The address of the SPG NFT contract.
            You can create one via `client.nft_client.create_nft_collection`.
        recipient: [Optional] The address to receive the NFT. Defaults to caller's wallet address.
        allow_duplicates: [Optional] Set to true to allow minting an NFT with a duplicate metadata hash. (default: True)
    """

    type: Literal["mint"]
    spg_nft_contract: Address
    recipient: Address | None = None
    allow_duplicates: bool = True


@dataclass
class MintedNFT:
    """
    Configuration for registering an already minted NFT as an IP asset.

    Attributes:
        type: Must be "minted" to indicate an existing NFT.
        nft_contract: The address of the NFT contract.
        token_id: The token ID of the NFT.
    """

    type: Literal["minted"]
    nft_contract: Address
    token_id: int


class RegisterIpAssetResponse(TypedDict, total=False):
    """
    Response structure for unified IP asset registration.
    Fields vary based on the registration method used.

    Attributes:
        tx_hash: The transaction hash of the registration transaction.
        ip_id: The IP ID of the registered IP asset.
        token_id: The token ID of the registered IP asset.
        license_terms_ids: [Optional] The IDs of the license terms attached to the IP asset.
        royalty_vault: [Optional] The royalty vault address of the registered IP asset.
        distribute_royalty_tokens_tx_hash: [Optional] The transaction hash of the distribute royalty tokens transaction.
    """

    tx_hash: HexStr
    ip_id: Address
    token_id: int
    license_terms_ids: list[int]
    royalty_vault: Address
    distribute_royalty_tokens_tx_hash: HexStr


class RegisterDerivativeIpAssetResponse(TypedDict, total=False):
    """
    Response structure for unified derivative IP asset registration.
    Fields vary based on the registration method used.

    Attributes:
        tx_hash: The transaction hash of the registration transaction.
        ip_id: The IP ID of the registered IP asset.
        token_id: The token ID of the registered IP asset.
        royalty_vault: [Optional] The royalty vault address of the registered IP asset.
        distribute_royalty_tokens_tx_hash: [Optional] The transaction hash of the distribute royalty tokens transaction.
    """

    tx_hash: HexStr
    ip_id: Address
    token_id: int
    royalty_vault: Address
    distribute_royalty_tokens_tx_hash: HexStr


class LinkDerivativeResponse(TypedDict):
    """
    Response structure for linking a derivative IP asset.

    Attributes:
        tx_hash: The transaction hash of the link derivative transaction.
    """

    tx_hash: HexStr


# =============================================================================
# Batch Registration Types for batch_register_ip_assets_with_optimized_workflows
# =============================================================================


@dataclass
class MintAndRegisterRequest:
    """
    Request for mint and register IP operations.

    Used for(contract method):
    - mintAndRegisterIpAssetWithPilTerms
    - mintAndRegisterIpAndMakeDerivative
    - mintAndRegisterIpAndAttachPilTermsAndDistributeRoyaltyTokens
    - mintAndRegisterIpAndMakeDerivativeAndDistributeRoyaltyTokens

    Attributes:
        spg_nft_contract: The address of the SPG NFT contract.
        recipient: [Optional] The address to receive the NFT. Defaults to caller's wallet address.
        allow_duplicates: [Optional] Set to true to allow minting an NFT with a duplicate metadata hash. (default: True)
        ip_metadata: [Optional] The metadata for the newly minted NFT and registered IP.
        license_terms_data: [Optional] The license terms data to attach. Required if not using deriv_data.
        deriv_data: [Optional] The derivative data for creating derivative IP. Required if not using license_terms_data.
        royalty_shares: [Optional] The royalty shares for distributing royalty tokens. Must be specified together with either `license_terms_data` or `deriv_data`.
    """

    spg_nft_contract: Address
    recipient: Address | None = None
    # TODO: need to consider how to handle new method and existing method
    allow_duplicates: bool | None = None
    ip_metadata: IPMetadataInput | None = None
    license_terms_data: list[LicenseTermsDataInput] | None = None
    deriv_data: DerivativeDataInput | None = None
    royalty_shares: list[RoyaltyShareInput] | None = None


@dataclass
class RegisterRegistrationRequest:
    """
    Request for register IP operations (already minted NFT).

    Used for(contract method):
    - registerIpAndAttachPilTerms
    - registerIpAndMakeDerivative
    - registerIpAndAttachPilTermsAndDeployRoyaltyVault
    - registerIpAndMakeDerivativeAndDeployRoyaltyVault

    Attributes:
        nft_contract: The address of the NFT contract.
        token_id: The token ID of the NFT.
        ip_metadata: [Optional] The metadata for the registered IP.
        deadline: [Optional] The deadline for the signature in seconds. (default: 1000)
        license_terms_data: [Optional] The license terms data to attach. Required if not using deriv_data.
        deriv_data: [Optional] The derivative data for creating derivative IP. Required if not using license_terms_data.
        royalty_shares: [Optional] The royalty shares for distributing royalty tokens. Must be specified together with either `license_terms_data` or `deriv_data`.
    """

    nft_contract: Address
    token_id: int
    ip_metadata: IPMetadataInput | None = None
    deadline: int | None = None
    license_terms_data: list[LicenseTermsDataInput] | None = None
    deriv_data: DerivativeDataInput | None = None
    royalty_shares: list[RoyaltyShareInput] | None = None


# Union type for all registration requests
IpRegistrationWorkflowRequest = MintAndRegisterRequest | RegisterRegistrationRequest


class IPRoyaltyVault(TypedDict):
    """
    IP royalty vault.

    Attributes:
        ip_id: The IP ID.
        royalty_vault: The royalty vault address.
    """

    ip_id: Address
    royalty_vault: Address


class RegisteredIPWithLicenseTermsIds(RegisteredIP):
    """
    Data structure for IP and token ID with license terms IDs.

    Attributes:
        license_terms_ids: The license terms IDs of the registered IP asset.
    """

    license_terms_ids: list[int]


class BatchRegistrationResult(TypedDict, total=False):
    """
    Result of a single batch registration transaction.

    Attributes:
        tx_hash: The transaction hash.
        registered_ips: List of registered IP assets (ip_id, token_id, license_terms_ids).
        ip_royalty_vaults: [Optional] List of IP royalty vaults for deployed royalty vaults.
    """

    tx_hash: HexStr
    registered_ips: list[RegisteredIPWithLicenseTermsIds]
    ip_royalty_vaults: list[IPRoyaltyVault]


class BatchRegisterIpAssetsWithOptimizedWorkflowsResponse(TypedDict, total=False):
    """
    Response for batch register IP assets with optimized workflows.

    Attributes:
        registration_results: List of batch registration results.
        distribute_royalty_tokens_tx_hashes: [Optional] Transaction hashes for royalty token distribution.
    """

    registration_results: list[BatchRegistrationResult]
    distribute_royalty_tokens_tx_hashes: list[HexStr]
