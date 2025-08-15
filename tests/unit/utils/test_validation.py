import pytest

from story_protocol_python_sdk.types.common import RevShareType
from story_protocol_python_sdk.utils.validation import (
    get_revenue_share,
    validate_address,
)


class TestValidateAddress:
    def test_valid_address(self):
        address = "0x1234567890123456789012345678901234567890"
        assert validate_address(address) == address

    def test_invalid_address(self):
        with pytest.raises(ValueError, match="Invalid address: invalid_address."):
            validate_address("invalid_address")


class TestGetRevenueShare:
    def test_valid_revenue_share_of_100(self):
        assert get_revenue_share(100) == 100 * 10**6

    def test_valid_revenue_share_of_0(self):
        assert get_revenue_share(0, RevShareType.COMMERCIAL_REVENUE_SHARE) == 0

    def test_valid_revenue_share_of_50(self):
        assert (
            get_revenue_share(50, RevShareType.MAX_ALLOWED_REWARD_SHARE) == 50 * 10**6
        )

    def test_valid_revenue_share_with_type_of_100(self):
        assert get_revenue_share(100) == 100 * 10**6

    def test_revenue_share_less_than_0_with_commercial_revenue_share(self):
        with pytest.raises(
            ValueError, match="The commercial_rev_share must be between 0 and 100."
        ):
            get_revenue_share(-1)

    def test_revenue_share_greater_than_100_with_max_allowed_reward_share(self):
        with pytest.raises(
            ValueError, match="The max_allowed_reward_share must be between 0 and 100."
        ):
            get_revenue_share(101, RevShareType.MAX_ALLOWED_REWARD_SHARE)

    def test_revenue_share_greater_than_100_with_commercial_revenue_share(self):
        with pytest.raises(
            ValueError, match="The commercial_rev_share must be between 0 and 100."
        ):
            get_revenue_share(101, RevShareType.COMMERCIAL_REVENUE_SHARE)

    def test_revenue_share_less_than_0_with_max_revenue_share(self):
        with pytest.raises(
            ValueError, match="The max_revenue_share must be between 0 and 100."
        ):
            get_revenue_share(-1, RevShareType.MAX_REVENUE_SHARE)

    def test_revenue_share_greater_than_100_with_expect_minimum_group_reward_share(
        self,
    ):
        with pytest.raises(
            ValueError,
            match="The expect_minimum_group_reward_share must be between 0 and 100.",
        ):
            get_revenue_share(101, RevShareType.EXPECT_MINIMUM_GROUP_REWARD_SHARE)
