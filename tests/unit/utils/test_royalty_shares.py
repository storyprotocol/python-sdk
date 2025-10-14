"""Tests for royalty_shares module."""

import pytest

from story_protocol_python_sdk.utils.royalty_shares import (
    RoyaltyShare,
    RoyaltyShareInput,
)


class TestRoyaltyShareGetRoyaltyShares:
    """Test RoyaltyShare.get_royalty_shares method."""

    def test_get_royalty_shares_success(self):
        """Test successful processing of valid royalty shares."""
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890", percentage=50.0
            ),
            RoyaltyShareInput(
                recipient="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd", percentage=30.0
            ),
        ]

        result = RoyaltyShare.get_royalty_shares(shares)

        expected_shares = [
            {
                "recipient": "0x1234567890123456789012345678901234567890",
                "percentage": 50_000_000,  # 50.0 * 10^6
            },
            {
                "recipient": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                "percentage": 30_000_000,  # 30.0 * 10^6
            },
        ]

        assert result["royalty_shares"] == expected_shares
        assert result["total_amount"] == 80_000_000

    def test_get_royalty_shares_with_integer_percentages(self):
        """Test processing royalty shares with integer percentages."""
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890", percentage=25
            ),
            RoyaltyShareInput(
                recipient="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd", percentage=75
            ),
        ]

        result = RoyaltyShare.get_royalty_shares(shares)
        expected_shares = [
            {
                "recipient": "0x1234567890123456789012345678901234567890",
                "percentage": 25_000_000,  # 25 * 10^6
            },
            {
                "recipient": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                "percentage": 75_000_000,  # 75 * 10^6
            },
        ]
        assert result["total_amount"] == 100_000_000
        assert result["royalty_shares"] == expected_shares

    def test_get_royalty_shares_precision_handling_6_decimals(self):
        """Test precision handling with exactly 6 decimal places."""
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890",
                percentage=33.333333,  # Exactly 6 decimal places
            ),
            RoyaltyShareInput(
                recipient="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                percentage=66.666667,  # Exactly 6 decimal places
            ),
        ]

        result = RoyaltyShare.get_royalty_shares(shares)

        # 33.333333 * 10^6 = 33333333
        # 66.666667 * 10^6 = 66666667
        expected_shares = [
            {
                "recipient": "0x1234567890123456789012345678901234567890",
                "percentage": 33_333_333,
            },
            {
                "recipient": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                "percentage": 66_666_667,
            },
        ]

        assert result["royalty_shares"] == expected_shares
        assert result["total_amount"] == 100_000_000

    def test_get_royalty_shares_precision_loss_more_than_6_decimals(self):
        """Test precision loss with more than 6 decimal places."""
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890",
                percentage=33.3333333333,  # More than 6 decimal places
            ),
            RoyaltyShareInput(
                recipient="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                percentage=66.6666666667,  # More than 6 decimal places
            ),
        ]

        result = RoyaltyShare.get_royalty_shares(shares)

        # Due to floating point precision and int() truncation:
        # 33.3333333333 * 10^6 = 33333333.3333, int() = 33333333
        # 66.6666666667 * 10^6 = 66666666.6667, int() = 66666666
        # Total would be 99999999, not 100000000 (precision loss)

        assert result["royalty_shares"][0]["percentage"] == 33_333_333
        assert result["royalty_shares"][1]["percentage"] == 66_666_666
        assert result["total_amount"] == 99_999_999  # Precision loss evident

    def test_get_royalty_shares_floating_point_accumulation_issue(self):
        """Test floating point accumulation precision issues."""
        # This tests the classic 0.1 + 0.2 != 0.3 floating point issue
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890", percentage=0.1
            ),
            RoyaltyShareInput(
                recipient="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd", percentage=0.2
            ),
            RoyaltyShareInput(
                recipient="0x9876543210987654321098765432109876543210", percentage=99.7
            ),
        ]

        result = RoyaltyShare.get_royalty_shares(shares)

        # Even though 0.1 + 0.2 + 99.7 = 100.0 mathematically,
        # floating point arithmetic might introduce small errors
        # The method should still work correctly
        assert result["total_amount"] == 100_000_000

    def test_get_royalty_shares_very_small_percentages(self):
        """Test handling of very small percentages that might lose precision."""
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890",
                percentage=0.000001,  # 1 part per million
            ),
            RoyaltyShareInput(
                recipient="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                percentage=99.999999,  # Rest
            ),
        ]

        result = RoyaltyShare.get_royalty_shares(shares)

        # 0.000001 * 10^6 = 1
        # 99.999999 * 10^6 = 99999999
        assert result["royalty_shares"][0]["percentage"] == 1
        assert result["royalty_shares"][1]["percentage"] == 99_999_999
        assert result["total_amount"] == 100_000_000

    def test_get_royalty_shares_boundary_case_exactly_100_percent(self):
        """Test boundary case with exactly 100% total."""
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890", percentage=100.0
            )
        ]

        result = RoyaltyShare.get_royalty_shares(shares)

        assert result["royalty_shares"][0]["percentage"] == 100_000_000
        assert result["total_amount"] == 100_000_000

    def test_get_royalty_shares_boundary_case_minimum_percentage(self):
        """Test boundary case with minimum valid percentage."""
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890",
                percentage=0.000001,  # Minimum that results in 1 after conversion
            )
        ]

        result = RoyaltyShare.get_royalty_shares(shares)

        assert result["royalty_shares"][0]["percentage"] == 1
        assert result["total_amount"] == 1

    def test_get_royalty_shares_empty_list_error(self):
        """Test error when providing empty royalty shares list."""
        with pytest.raises(ValueError, match="Royalty shares must be provided."):
            RoyaltyShare.get_royalty_shares([])

    def test_get_royalty_shares_zero_percentage(self):
        """Test error when percentage is zero."""
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890", percentage=0
            )
        ]

        result = RoyaltyShare.get_royalty_shares(shares)

        assert result["royalty_shares"][0]["percentage"] == 0
        assert result["total_amount"] == 0

    def test_get_royalty_shares_negative_percentage_error(self):
        """Test error when percentage is negative."""
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890", percentage=-10
            )
        ]

        with pytest.raises(
            ValueError,
            match="he percentage of the royalty shares must be greater than or equal to 0.",
        ):
            RoyaltyShare.get_royalty_shares(shares)

    def test_get_royalty_shares_percentage_100(self):
        """Test when percentage is 100."""
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890", percentage=100
            )
        ]

        result = RoyaltyShare.get_royalty_shares(shares)

        assert result["royalty_shares"][0]["percentage"] == 100_000_000
        assert result["total_amount"] == 100_000_000

    def test_get_royalty_shares_percentage_over_100(self):
        """Test error when single percentage exceeds 100."""
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890", percentage=101
            )
        ]

        with pytest.raises(
            ValueError,
            match="The percentage of the royalty shares must be less than or equal to 100.",
        ):
            RoyaltyShare.get_royalty_shares(shares)

    def test_get_royalty_shares_invalid_address_error(self):
        """Test error when address is invalid."""
        shares = [RoyaltyShareInput(recipient="invalid_address", percentage=50)]

        with pytest.raises(ValueError, match="Invalid address"):
            RoyaltyShare.get_royalty_shares(shares)

    def test_get_royalty_shares_cumulative_precision_boundary(self):
        """Test cumulative precision at the boundary of 100%."""
        # This tests a scenario where individual percentages are valid
        # but cumulative floating point errors might cause issues
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890",
                percentage=33.333333,
            ),
            RoyaltyShareInput(
                recipient="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                percentage=33.333333,
            ),
            RoyaltyShareInput(
                recipient="0x9876543210987654321098765432109876543210",
                percentage=33.333334,
            ),
        ]

        # This should work because 33.333333 + 33.333333 + 33.333334 = 100.0
        result = RoyaltyShare.get_royalty_shares(shares)

        assert len(result["royalty_shares"]) == 3
        assert result["total_amount"] == 100_000_000

    def test_get_royalty_shares_precision_edge_case_just_over_100(self):
        """Test precision edge case where floating point arithmetic results in just over 100%."""
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890",
                percentage=50.0000001,
            ),
            RoyaltyShareInput(
                recipient="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                percentage=50.0000001,
            ),
        ]

        # 50.000001 + 50.000001 = 100.000002, which is > 100
        with pytest.raises(
            ValueError, match="The sum of the royalty shares cannot exceeds 100."
        ):
            RoyaltyShare.get_royalty_shares(shares)

    def test_get_royalty_shares_single_recipient_multiple_entries(self):
        """Test multiple entries for the same recipient."""
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890", percentage=25.5
            ),
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890", percentage=24.5
            ),
            RoyaltyShareInput(
                recipient="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd", percentage=50.0
            ),
        ]

        result = RoyaltyShare.get_royalty_shares(shares)

        # Should treat each entry separately, not merge them
        assert len(result["royalty_shares"]) == 3
        assert result["royalty_shares"][0]["percentage"] == 25_500_000
        assert result["royalty_shares"][1]["percentage"] == 24_500_000
        assert result["royalty_shares"][2]["percentage"] == 50_000_000
        assert result["total_amount"] == 100_000_000

    def test_get_royalty_shares_mixed_data_types(self):
        """Test mixing int and float percentages."""
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890", percentage=25
            ),  # int
            RoyaltyShareInput(
                recipient="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd", percentage=75.0
            ),  # float
        ]

        result = RoyaltyShare.get_royalty_shares(shares)

        assert result["royalty_shares"][0]["percentage"] == 25_000_000
        assert result["royalty_shares"][1]["percentage"] == 75_000_000
        assert result["total_amount"] == 100_000_000

    def test_get_royalty_shares_extremely_small_percentage(self):
        """Test extremely small percentage that rounds to 0."""
        shares = [
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890",
                percentage=0.0000001,  # 0.1 parts per million, will be 0 after int conversion
            ),
            RoyaltyShareInput(
                recipient="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                percentage=99.9999999,
            ),
        ]

        result = RoyaltyShare.get_royalty_shares(shares)

        # 0.0000001 * 10^6 = 0.1, int(0.1) = 0
        assert result["royalty_shares"][0]["percentage"] == 0
        assert result["royalty_shares"][1]["percentage"] == 99_999_999
        assert result["total_amount"] == 99_999_999

    def test_get_royalty_shares_address_validation_order(self):
        """Test that address validation happens before percentage processing."""
        shares = [
            RoyaltyShareInput(recipient="invalid_address", percentage=50.0),
            RoyaltyShareInput(
                recipient="0x1234567890123456789012345678901234567890", percentage=150.0
            ),
        ]

        # Should fail on address validation first, not percentage validation
        with pytest.raises(ValueError, match="Invalid address"):
            RoyaltyShare.get_royalty_shares(shares)
