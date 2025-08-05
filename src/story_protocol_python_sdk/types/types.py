"""
Common type definitions for Story Protocol Python SDK.

This module contains type aliases and dataclasses used throughout the SDK
to provide semantic clarity and type safety.
"""

from enum import Enum
from typing import Literal, NewType

Address = NewType("Address", str)  # Ethereum address
Hash = NewType("Hash", str)  # Transaction hash or state hash
Hex = NewType("Hex", str)  # Hex string
ChainIds = Literal[1315, 1514]  # Chain IDs 1315: aeneid, 1514: mainnet


# The type of revenue share.
# It is used to determine the type of revenue share to be used in the revenue share calculation and throw error when the revenue share is not valid.
class RevShareType(Enum):
    COMMERCIAL_REVENUE_SHARE = "CommercialRevShare"
    MAX_REVENUE_SHARE = "MaxRevenueShare"
    MAX_ALLOWED_REWARD_SHARE = "MaxAllowedRewardShare"
