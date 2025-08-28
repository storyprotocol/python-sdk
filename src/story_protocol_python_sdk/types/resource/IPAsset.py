from typing import Optional, TypedDict

from ens.ens import Address, HexStr


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
    token_id: Optional[int]


class RegisterPILTermsAndAttachResponse(TypedDict):
    """
    Response structure for Programmable IP License Terms registration and attachment operations.

    Attributes:
        tx_hash: The transaction hash of the registration transaction
        license_terms_ids: The IDs of the registered license terms
    """

    tx_hash: HexStr
    license_terms_ids: list[int]
