from dataclasses import dataclass
from typing import Optional

from ens.ens import Address, HexStr

from story_protocol_python_sdk.types.resource.Royalty import RoyaltyPolicyInput


@dataclass
class LicenseTermsOverride:
    """
    Optional override parameters for license terms.
    All fields are optional and default to None.

    Attributes:
        transferable: Whether the license is transferable.
        royalty_policy: The type of royalty policy to be used.
        default_minting_fee: The fee to be paid when minting a license.
        expiration: The expiration period of the license.
        commercial_use: Whether commercial use is allowed.
        commercial_attribution: Whether commercial attribution is required.
        commercializer_checker: The address of the commercializer checker contract.
        commercializer_checker_data: The data to be passed to the commercializer checker contract.
        commercial_rev_share: Percentage of revenue that must be shared with the licensor. Must be between 0 and 100 (where 100% represents 100_000_000).
        commercial_rev_ceiling: The maximum revenue that can be collected from commercial use.
        derivatives_allowed: Whether derivatives are allowed.
        derivatives_attribution: Whether attribution is required for derivatives.
        derivatives_approval: Whether approval is required for derivatives.
        derivatives_reciprocal: Whether derivatives must have the same license terms.
        derivative_rev_ceiling: The maximum revenue that can be collected from derivatives.
        currency: The ERC20 token to be used to pay the minting fee.
        uri: The URI of the license terms.
    """

    transferable: Optional[bool] = None
    royalty_policy: Optional[RoyaltyPolicyInput] = None
    default_minting_fee: Optional[int] = None
    expiration: Optional[int] = None
    commercial_use: Optional[bool] = None
    commercial_attribution: Optional[bool] = None
    commercializer_checker: Optional[Address] = None
    commercializer_checker_data: Optional[Address | HexStr] = None
    commercial_rev_share: Optional[int] = None
    commercial_rev_ceiling: Optional[int] = None
    derivatives_allowed: Optional[bool] = None
    derivatives_attribution: Optional[bool] = None
    derivatives_approval: Optional[bool] = None
    derivatives_reciprocal: Optional[bool] = None
    derivative_rev_ceiling: Optional[int] = None
    currency: Optional[Address] = None
    uri: Optional[str] = None


@dataclass
class LicenseTermsInput:
    """
    This structure defines the terms for a Programmable IP License (PIL).
    These terms can be attached to IP Assets.

    For more information, see https://docs.story.foundation/concepts/programmable-ip-license/pil-terms

    Attributes:
        transferable: Indicates whether the license is transferable or not.
        royalty_policy: The address of the royalty policy contract which required to StoryProtocol in advance.
        default_minting_fee: The default minting fee to be paid when minting a license.
        expiration: The expiration period of the license.
        commercial_use: Indicates whether the work can be used commercially or not.
        commercial_attribution: Whether attribution is required when reproducing the work commercially or not.
        commercializer_checker: Commercializers that are allowed to commercially exploit the work. If zero address, then no restrictions is enforced.
        commercializer_checker_data: The data to be passed to the commercializer checker contract.
        commercial_rev_share: Percentage of revenue that must be shared with the licensor. Must be between 0 and 100 (where 100% represents 100_000_000).
        commercial_rev_ceiling: The maximum revenue that can be generated from the commercial use of the work.
        derivatives_allowed: Indicates whether the licensee can create derivatives of his work or not.
        derivatives_attribution: Indicates whether attribution is required for derivatives of the work or not.
        derivatives_approval: Indicates whether the licensor must approve derivatives of the work before they can be linked to the licensor IP ID or not.
        derivatives_reciprocal: Indicates whether the licensee must license derivatives of the work under the same terms or not.
        derivative_rev_ceiling: The maximum revenue that can be generated from the derivative use of the work.
        currency: The ERC20 token to be used to pay the minting fee. The token must be registered in story protocol.
        uri: The URI of the license terms, which can be used to fetch the offchain license terms.
    """

    transferable: bool
    royalty_policy: RoyaltyPolicyInput
    default_minting_fee: int
    expiration: int
    commercial_use: bool
    commercial_attribution: bool
    commercializer_checker: Address
    commercializer_checker_data: Address | HexStr
    commercial_rev_share: int
    commercial_rev_ceiling: int
    derivatives_allowed: bool
    derivatives_attribution: bool
    derivatives_approval: bool
    derivatives_reciprocal: bool
    derivative_rev_ceiling: int
    currency: Address
    uri: str
