from dataclasses import dataclass
from enum import IntEnum

from ens.ens import Address


class NativeRoyaltyPolicy(IntEnum):
    """
    Native royalty policy created by the Story team.

    For more information:
    - LAP: https://docs.story.foundation/concepts/royalty-module/liquid-absolute-percentage
    - LRP: https://docs.story.foundation/concepts/royalty-module/liquid-relative-percentage

    Attributes:
        LAP: Liquid Absolute Percentage - defines that each parent IP Asset can choose a minimum royalty percentage that all of its downstream IP Assets in a derivative chain will share from their monetary gains as defined in the license agreement.
        LRP: Liquid Relative Percentage - royalty policy defines that each parent IP Asset can choose a minimum royalty percentage that only the direct derivative IP Assets in a derivative chain will share from their monetary gains as defined in the license agreement.
    """

    LAP = 0
    LRP = 1


# Type alias for royalty policy input
# Allow custom royalty policy address or use a native royalty policy enum.
# For custom royalty policy, see https://docs.story.foundation/concepts/royalty-module/external-royalty-policies
RoyaltyPolicyInput = Address | NativeRoyaltyPolicy


@dataclass
class RoyaltyShareInput:
    """Input data structure for a single royalty share.

    Attributes:
        recipient: The address of the recipient.
        percentage: The percentage of the total royalty share. Supports up to 6 decimal places precision. For example, a value of 10 represents 10% of max royalty shares, which is 10,000,000.
    """

    recipient: Address
    percentage: float | int
