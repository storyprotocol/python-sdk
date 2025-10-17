from dataclasses import dataclass
from typing import TypedDict

from ens.ens import Address, HexStr

from story_protocol_python_sdk.types.resource.License import LicenseTermsInput
from story_protocol_python_sdk.utils.licensing_config_data import LicensingConfig


class RegistrationResponse(TypedDict):
    """
    Response structure for IP asset registration operations.

    Attributes:
        ip_id: The IP ID of the registered IP asset
        tx_hash: The transaction hash of the registration transaction
        token_id: [Optional] The token ID of the registered IP asset
    """

    ip_id: Address
    tx_hash: HexStr
    token_id: int


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
