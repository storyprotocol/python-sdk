from web3 import Web3

from story_protocol_python_sdk.types.common import RevShareType
from story_protocol_python_sdk.utils.constants import MAX_ROYALTY_TOKEN


def validate_address(address: str) -> str:
    """
    Validates if the provided string is a valid Ethereum address.

    :param address str: The address to validate.
    :return str: The validated address.
    :raises ValueError: If the address is not valid.
    """
    if not Web3.is_address(address):
        raise ValueError(f"Invalid address: {address}.")
    return address


def get_revenue_share(
    revShare: int | float,
    type: RevShareType = RevShareType.COMMERCIAL_REVENUE_SHARE,
) -> int | float:
    """
    Convert revenue share percentage to token amount.

    :param revShare int: Revenue share percentage between 0-100
    :param type RevShareType: Type of revenue share
    :return int: Revenue share token amount
    """
    if revShare < 0 or revShare > 100:
        raise ValueError(f"The {type.value} must be between 0 and 100.")

    return (revShare * MAX_ROYALTY_TOKEN) / 100
