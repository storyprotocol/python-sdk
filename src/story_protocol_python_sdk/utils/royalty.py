"""Module for handling royalty-related utilities including shares and policy conversions."""

from typing import List

from ens.ens import Address

from story_protocol_python_sdk.types.resource.Royalty import (
    NativeRoyaltyPolicy,
    RoyaltyShareInput,
)
from story_protocol_python_sdk.utils.constants import (
    ROYALTY_POLICY_LAP_ADDRESS,
    ROYALTY_POLICY_LRP_ADDRESS,
)
from story_protocol_python_sdk.utils.validation import validate_address


def get_royalty_shares(royalty_shares: list[RoyaltyShareInput]) -> dict:
    """
    Validate and convert royalty shares.

    :param royalty_shares: List of `RoyaltyShareInput`.
    :return: Dictionary with validated royalty_shares and total_amount.
    """
    if len(royalty_shares) == 0:
        raise ValueError("Royalty shares must be provided.")

    actual_total = 0
    sum_percentage = 0.0
    converted_shares: List[dict] = []

    for share_dict in royalty_shares:
        recipient = validate_address(share_dict.recipient)
        percentage = share_dict.percentage

        if percentage < 0:
            raise ValueError(
                "The percentage of the royalty shares must be greater than or equal to 0."
            )

        if percentage > 100:
            raise ValueError(
                "The percentage of the royalty shares must be less than or equal to 100."
            )

        sum_percentage += percentage
        if sum_percentage > 100:
            raise ValueError("The sum of the royalty shares cannot exceeds 100.")

        value = int(percentage * 10**6)
        actual_total += value

        converted_shares.append(
            {
                "recipient": recipient,
                "percentage": value,
            }
        )

    return {"royalty_shares": converted_shares, "total_amount": actual_total}


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
        ValueError: If the custom address is invalid.
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
