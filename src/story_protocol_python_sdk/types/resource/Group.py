from typing import TypedDict

from ens.ens import Address, HexStr


class ClaimReward(TypedDict):
    """
    Structure for a claimed reward.
    """

    ip_id: Address
    amount: int
    token: Address


class ClaimRewardsResponse(TypedDict):
    """
    Response structure for Group.claim_rewards method.
    """

    tx_hash: HexStr
    claimed_rewards: list[ClaimReward]
