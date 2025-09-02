from unittest.mock import patch

import pytest

from story_protocol_python_sdk.resources.Group import Group
from story_protocol_python_sdk.types.resource.Group import (
    ClaimReward,
    ClaimRewardsResponse,
)
from tests.unit.fixtures.data import ADDRESS, CHAIN_ID, IP_ID, TX_HASH


@pytest.fixture(scope="class")
def group(mock_web3, mock_account):
    return Group(mock_web3, mock_account, CHAIN_ID)


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
        mock_web3_is_address,
    ):
        """Test successful claim_rewards operation."""
        with mock_web3_is_address():
            with patch(
                "story_protocol_python_sdk.resources.Group.build_and_send_transaction",
                return_value={
                    "tx_hash": TX_HASH,
                    "tx_receipt": {
                        "logs": [
                            {
                                "topics": [
                                    group.web3.keccak(
                                        text="ClaimedReward(address,address,address[],uint256[])"
                                    )
                                ]
                            }
                        ]
                    },
                },
            ), patch.object(
                group.grouping_module_client.contract.events.ClaimedReward,
                "process_log",
                return_value={
                    "args": {
                        "ipId": [IP_ID, ADDRESS],
                        "amount": [100, 200],
                        "token": ADDRESS,
                        "groupId": IP_ID,
                    }
                },
            ):
                # Test without tx_options
                result = group.claim_rewards(
                    group_ip_id=IP_ID,
                    currency_token=ADDRESS,
                    member_ip_ids=[IP_ID, ADDRESS],
                )

                # Verify response structure
                assert "tx_hash" in result
                assert result["tx_hash"] == TX_HASH
                assert "claimed_rewards" in result
                assert result["claimed_rewards"] == ClaimReward(
                    ip_ids=[IP_ID, ADDRESS],
                    amounts=[100, 200],
                    token=ADDRESS,
                    group_id=IP_ID,
                )
                assert result == ClaimRewardsResponse(
                    tx_hash=TX_HASH,
                    claimed_rewards=ClaimReward(
                        ip_ids=[IP_ID, ADDRESS],
                        amounts=[100, 200],
                        token=ADDRESS,
                        group_id=IP_ID,
                    ),
                )

    def test_claim_rewards_with_tx_options(
        self,
        group: Group,
        mock_web3_is_address,
    ):
        """Test claim_rewards with transaction options."""
        with mock_web3_is_address():
            with patch(
                "story_protocol_python_sdk.resources.Group.build_and_send_transaction",
                return_value={
                    "tx_hash": TX_HASH,
                    "tx_receipt": {
                        "logs": [
                            {
                                "topics": [
                                    group.web3.keccak(
                                        text="ClaimedReward(address,address,address[],uint256[])"
                                    )
                                ]
                            }
                        ]
                    },
                },
            ) as mock_build_and_send, patch.object(
                group.grouping_module_client.contract.events.ClaimedReward,
                "process_log",
                return_value={
                    "args": {
                        "ipId": [IP_ID, ADDRESS],
                        "amount": [100, 200],
                        "token": ADDRESS,
                        "groupId": IP_ID,
                    }
                },
            ):
                tx_options = {"gas": 200000, "gasPrice": 20000000000}
                result = group.claim_rewards(
                    group_ip_id=IP_ID,
                    currency_token=ADDRESS,
                    member_ip_ids=[IP_ID, ADDRESS],
                    tx_options=tx_options,
                )

                # Verify tx_options were passed to build_and_send_transaction
                mock_build_and_send.assert_called_once()
                call_args = mock_build_and_send.call_args
                assert call_args[1]["tx_options"] == tx_options

                # Verify response with tx_options
                assert result["tx_hash"] == TX_HASH
                assert result["claimed_rewards"] == ClaimReward(
                    ip_ids=[IP_ID, ADDRESS],
                    amounts=[100, 200],
                    token=ADDRESS,
                    group_id=IP_ID,
                )

    def test_claim_rewards_no_event_found(
        self,
        group: Group,
        mock_web3_is_address,
    ):
        """Test claim_rewards when no ClaimedReward event is found."""
        with mock_web3_is_address():
            with patch(
                "story_protocol_python_sdk.resources.Group.build_and_send_transaction",
                return_value={
                    "tx_hash": TX_HASH,
                    "tx_receipt": {
                        "logs": [
                            {"topics": [group.web3.keccak(text="DifferentEvent()")]}
                        ]
                    },
                },
            ), patch.object(
                group.grouping_module_client.contract.events.ClaimedReward,
                "process_log",
                return_value={"args": {}},
            ):
                with pytest.raises(
                    ValueError,
                    match="Failed to claim rewards: Not found ClaimedReward event in transaction logs.",
                ):
                    group.claim_rewards(
                        group_ip_id=IP_ID,
                        currency_token=ADDRESS,
                        member_ip_ids=[IP_ID],
                    )

    def test_claim_rewards_empty_member_ip_ids(
        self,
        group: Group,
        mock_web3_is_address,
    ):
        """Test claim_rewards with empty member IP IDs list."""
        with mock_web3_is_address():
            with patch(
                "story_protocol_python_sdk.resources.Group.build_and_send_transaction",
                return_value={
                    "tx_hash": TX_HASH,
                    "tx_receipt": {
                        "logs": [
                            {
                                "topics": [
                                    group.web3.keccak(
                                        text="ClaimedReward(address,address,address[],uint256[])"
                                    )
                                ]
                            }
                        ]
                    },
                },
            ), patch.object(
                group.grouping_module_client.contract.events.ClaimedReward,
                "process_log",
                return_value={
                    "args": {
                        "ipId": [],
                        "amount": [],
                        "token": ADDRESS,
                        "groupId": IP_ID,
                    }
                },
            ):
                result = group.claim_rewards(
                    group_ip_id=IP_ID,
                    currency_token=ADDRESS,
                    member_ip_ids=[],
                )

                # Verify response structure
                assert "tx_hash" in result
                assert result["tx_hash"] == TX_HASH
                assert "claimed_rewards" in result
                assert result["claimed_rewards"] == ClaimReward(
                    ip_ids=[],
                    amounts=[],
                    token=ADDRESS,
                    group_id=IP_ID,
                )

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
