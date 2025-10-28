from web3 import Web3

from story_protocol_python_sdk.types.common import RevShareType


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


def validate_addresses(addresses: list[str]) -> list[str]:
    """
    Validates if the provided list of strings are valid Ethereum addresses.

    :param addresses list[str]: The list of addresses to validate.
    :return list[str]: The validated list of addresses.
    :raises ValueError: If any address is not valid.
    """
    if not all(Web3.is_address(address) for address in addresses):
        raise ValueError(f"Invalid addresses: {addresses}.")
    return addresses


def get_revenue_share(
    revShare: int,
    type: RevShareType = RevShareType.COMMERCIAL_REVENUE_SHARE,
) -> int:
    """
    Convert revenue share percentage to token amount.

    :param revShare int: Revenue share percentage between 0-100
    :param type RevShareType: Type of revenue share, default is commercial revenue share
    :return int: Revenue share token amount
    """
    if revShare < 0 or revShare > 100:
        raise ValueError(f"The {type.value} must be between 0 and 100.")

    return revShare * 10**6


def validate_max_rts(max_rts: int):
    """
    Validates the maximum number of royalty tokens.

    :param max_rts int: The maximum number of royalty tokens
    :raises ValueError: If max_rts is invalid
    """
    if max_rts < 0 or max_rts > 100_000_000:
        raise ValueError("The maxRts must be greater than 0 and less than 100,000,000.")
