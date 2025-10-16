"""Module for handling royalty shares data structure and validation."""

from dataclasses import dataclass
from typing import List

from ens.ens import Address

from story_protocol_python_sdk.utils.validation import validate_address


@dataclass
class RoyaltyShareInput:
    """Input data structure for a single royalty share.

    Attributes:
        recipient: The address of the recipient.
        percentage: The percentage of the total royalty share. Supports up to 6 decimal places precision. For example, a value of 10 represents 10% of max royalty shares, which is 10,000,000.
    """

    recipient: Address
    percentage: float | int


@dataclass
class RoyaltyShare:
    """Validated royalty share data."""

    @classmethod
    def get_royalty_shares(cls, royalty_shares: List[RoyaltyShareInput]):
        """
        Validate and convert royalty shares.

        :param royalty_shares: List of `RoyaltyShareInput`
        :return: Dictionary with validated royalty_shares and total_amount
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
