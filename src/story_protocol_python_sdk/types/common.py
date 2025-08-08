from enum import Enum


class RevShareType(Enum):
    COMMERCIAL_REVENUE_SHARE = "commercialRevShare"
    MAX_REVENUE_SHARE = "maxRevenueShare"
    MAX_ALLOWED_REWARD_SHARE = "maxAllowedRewardShare"


class AccessPermission(Enum):
    """
    Permission level
    """

    # ABSTAIN means having not enough information to make decision at
    # current level, deferred decision to up.
    ABSTAIN = 0
    # ALLOW means the permission is granted to transaction signer to call the function.
    ALLOW = 1
    # DENY means the permission is denied to transaction signer to call the function.
    DENY = 2
