from ens.ens import Address

from story_protocol_python_sdk.types.resource.Royalty import NativeRoyaltyPolicy
from story_protocol_python_sdk.utils.constants import (
    ROYALTY_POLICY_LAP_ADDRESS,
    ROYALTY_POLICY_LRP_ADDRESS,
)
from story_protocol_python_sdk.utils.validation import validate_address


def royalty_policy_input_to_address(
    input: Address | NativeRoyaltyPolicy | None = None,
) -> Address:
    """
    Convert RoyaltyPolicyInput to an address.

    Args:
        input: The royalty policy input. Can be None, a NativeRoyaltyPolicy enum value, or a custom address.

    Returns:
        Address: The corresponding royalty policy address.
            - If None, returns the default LAP policy address
            - If a string address, validates and returns it (custom address)
            - If NativeRoyaltyPolicy.LAP (0), returns the LAP policy address
            - If NativeRoyaltyPolicy.LRP (1), returns the LRP policy address

    Raises:
        ValueError: If the custom address is invalid
    """
    if input is None:
        return ROYALTY_POLICY_LAP_ADDRESS

    if isinstance(input, str):
        return validate_address(input)

    if input == NativeRoyaltyPolicy.LAP:
        return ROYALTY_POLICY_LAP_ADDRESS
    elif input == NativeRoyaltyPolicy.LRP:
        return ROYALTY_POLICY_LRP_ADDRESS

    return ROYALTY_POLICY_LAP_ADDRESS
