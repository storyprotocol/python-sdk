from typing import TypedDict

from ens.ens import Address, HexBytes


class ClaimReward(TypedDict):
    """
    Structure for a claimed reward.
    """

    ip_ids: list[Address]
    amounts: list[int]
    token: Address
    group_id: Address


class ClaimRewardsResponse(TypedDict):
    """
    Response structure for Group.claim_rewards method.
    """

    tx_hash: HexBytes
    claimed_rewards: ClaimReward


class CollectRoyaltiesResponse(TypedDict):
    """
    Response structure for Group.collect_royalties method.
    """

    tx_hash: HexBytes
    collected_royalties: int
