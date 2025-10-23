from dataclasses import dataclass
from typing import TypedDict

from ens.ens import Address, HexStr

from story_protocol_python_sdk.types.resource.License import LicenseTermsInput
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
