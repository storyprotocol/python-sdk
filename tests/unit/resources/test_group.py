from unittest.mock import MagicMock, patch

import pytest

from story_protocol_python_sdk.resources.Group import Group
from tests.unit.fixtures.data import ADDRESS, CHAIN_ID, IP_ID, TX_HASH


@pytest.fixture(scope="class")
def group(mock_web3, mock_account):
    return Group(mock_web3, mock_account, CHAIN_ID)


@pytest.fixture(scope="class")
def mock_grouping_module_client(group):
    def _mock():
        return patch.object(
            group.grouping_module_client,
            "build_claimReward_transaction",
            return_value=MagicMock(),
        )

    return _mock


@pytest.fixture(scope="class")
def mock_build_and_send_transaction():
    def _mock():
        return patch(
            "story_protocol_python_sdk.resources.Group.build_and_send_transaction",
            return_value={
                "tx_hash": TX_HASH,
                "tx_receipt": {"status": 1, "logs": []},
            },
        )

    return _mock


@pytest.fixture(scope="class")
def mock_parse_tx_claimed_reward_event(group):
    def _mock():
        return patch.object(
            group,
            "_parse_tx_claimed_reward_event",
            return_value=[{"amount": 100, "token": ADDRESS}],
        )

    return _mock


class TestGroupClaimRewards:
    """Test class for Group.claim_rewards method"""

    def test_claim_rewards_invalid_group_ip_id(
        self, group: Group, mock_web3_is_address
    ):
        """Test claim_rewards with invalid group IP ID."""
        invalid_group_ip_id = "invalid_group_ip_id"
        with mock_web3_is_address(False):
            with pytest.raises(
                ValueError,
                match=f"Failed to claim rewards: Invalid group IP ID: {invalid_group_ip_id}",
            ):
                group.claim_rewards(
                    group_ip_id=invalid_group_ip_id,
                    currency_token=ADDRESS,
                    member_ip_ids=[IP_ID],
                )

    def test_claim_rewards_invalid_currency_token(self, group: Group, mock_web3):
        """Test claim_rewards with invalid currency token."""
        invalid_currency_token = "invalid_currency_token"
        with patch.object(mock_web3, "is_address") as mock_is_address:
            # group_ip_id=True, currency_token=False
            mock_is_address.side_effect = [True, False]
            with pytest.raises(
                ValueError,
                match=f"Failed to claim rewards: Invalid currency token: {invalid_currency_token}",
            ):
                group.claim_rewards(
                    group_ip_id=IP_ID,
                    currency_token=invalid_currency_token,
                    member_ip_ids=[ADDRESS],
                )

    def test_claim_rewards_invalid_member_ip_ids(self, group: Group, mock_web3):
        """Test claim_rewards with invalid member IP IDs."""
        invalid_member_ip_id = "invalid_member_ip"
        with patch.object(mock_web3, "is_address") as mock_is_address:
            # group_ip_id=True, currency_token=True, first member_ip_id=False
            mock_is_address.side_effect = [True, True, False]
            with pytest.raises(
                ValueError,
                match=f"Failed to claim rewards: Invalid member IP ID: {invalid_member_ip_id}",
            ):
                group.claim_rewards(
                    group_ip_id=IP_ID,
                    currency_token=ADDRESS,
                    member_ip_ids=[invalid_member_ip_id],
                )

    def test_claim_rewards_mixed_valid_invalid_members(self, group: Group, mock_web3):
        """Test claim_rewards with mix of valid and invalid member IP IDs."""
        invalid_member_ip_id = "invalid_member_ip"
        with patch.object(mock_web3, "is_address") as mock_is_address:
            # group_ip_id=True, currency_token=True, first_member=True, second_member=False
            mock_is_address.side_effect = [True, True, True, False]
            with pytest.raises(
                ValueError,
                match=f"Failed to claim rewards: Invalid member IP ID: {invalid_member_ip_id}",
            ):
                group.claim_rewards(
                    group_ip_id=IP_ID,
                    currency_token=ADDRESS,
                    member_ip_ids=[ADDRESS, invalid_member_ip_id],
                )

    def test_claim_rewards_success(
        self,
        group: Group,
        mock_grouping_module_client,
        mock_build_and_send_transaction,
        mock_parse_tx_claimed_reward_event,
        mock_web3_is_address,
    ):
        """Test successful claim_rewards operation."""

        with (
            mock_grouping_module_client(),
            mock_build_and_send_transaction(),
            mock_parse_tx_claimed_reward_event(),
            mock_web3_is_address(),
        ):
            result = group.claim_rewards(
                group_ip_id=IP_ID,
                currency_token=ADDRESS,
                member_ip_ids=[IP_ID, ADDRESS],
            )

            # Verify response structure
            assert "tx_hash" in result
            assert result["tx_hash"] == TX_HASH
            assert "claimed_rewards" in result
            assert result["claimed_rewards"] == [{"amount": 100, "token": ADDRESS}]

    def test_claim_rewards_transaction_build_failure(
        self, group: Group, mock_web3_is_address
    ):
        """Test claim_rewards when transaction building fails."""
        with mock_web3_is_address(True):
            with patch(
                "story_protocol_python_sdk.resources.Group.build_and_send_transaction",
                side_effect=Exception("Transaction build failed"),
            ):
                with pytest.raises(
                    ValueError,
                    match="Failed to claim rewards: Transaction build failed",
                ):
                    group.claim_rewards(
                        group_ip_id=IP_ID,
                        currency_token=ADDRESS,
                        member_ip_ids=[IP_ID],
                    )
