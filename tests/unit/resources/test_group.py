from unittest.mock import patch

import pytest

from story_protocol_python_sdk.resources.Group import Group
from story_protocol_python_sdk.types.resource.Group import (
    ClaimReward,
    ClaimRewardsResponse,
    CollectRoyaltiesResponse,
)
from tests.unit.fixtures.data import ADDRESS, CHAIN_ID, IP_ID, TX_HASH


@pytest.fixture(scope="class")
def group(mock_web3, mock_account):
    return Group(mock_web3, mock_account, CHAIN_ID)


class TestGroupCollectRoyalties:
    """Test class for Group.collect_royalties method"""

    def test_collect_royalties_invalid_group_ip_id(
        self, group: Group, mock_web3_is_address
    ):
        """Test collect_royalties with invalid group IP ID."""
        invalid_group_ip_id = "invalid_group_ip_id"
        with mock_web3_is_address(False):
            with pytest.raises(
                ValueError,
                match=f"Failed to collect royalties: Invalid group IP ID: {invalid_group_ip_id}",
            ):
                group.collect_royalties(
                    group_ip_id=invalid_group_ip_id,
                    currency_token=ADDRESS,
                )

    def test_collect_royalties_invalid_currency_token(self, group: Group, mock_web3):
        """Test collect_royalties with invalid currency token."""
        invalid_currency_token = "invalid_currency_token"
        with patch.object(mock_web3, "is_address") as mock_is_address:
            # group_ip_id=True, currency_token=False
            mock_is_address.side_effect = [True, False]
            with pytest.raises(
                ValueError,
                match=f"Failed to collect royalties: Invalid currency token: {invalid_currency_token}",
            ):
                group.collect_royalties(
                    group_ip_id=IP_ID,
                    currency_token=invalid_currency_token,
                )

    def test_collect_royalties_success(
        self,
        group: Group,
        mock_web3_is_address,
    ):
        """Test successful collect_royalties operation."""
        collected_amount = 100

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
                                        text="CollectedRoyaltiesToGroupPool(address,address,address,uint256)"
                                    )
                                ]
                            }
                        ]
                    },
                },
            ), patch.object(
                group.grouping_module_client.contract.events.CollectedRoyaltiesToGroupPool,
                "process_log",
                return_value={"args": {"amount": collected_amount}},
            ):
                result = group.collect_royalties(
                    group_ip_id=IP_ID,
                    currency_token=ADDRESS,
                )

                assert "tx_hash" in result
                assert result["tx_hash"] == TX_HASH
                assert "collected_royalties" in result
                assert result["collected_royalties"] == collected_amount
                assert result == CollectRoyaltiesResponse(
                    tx_hash=TX_HASH,
                    collected_royalties=collected_amount,
                )

    def test_collect_royalties_no_event_found(
        self,
        group: Group,
        mock_web3_is_address,
    ):
        """Test collect_royalties when no CollectedRoyaltiesToGroupPool event is found."""
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
                group.grouping_module_client.contract.events.CollectedRoyaltiesToGroupPool,
                "process_log",
                return_value={"args": {"amount": 0}},
            ):
                result = group.collect_royalties(
                    group_ip_id=IP_ID,
                    currency_token=ADDRESS,
                )

                # Should return 0 collected royalties when no event is found
                assert "tx_hash" in result
                assert result["tx_hash"] == TX_HASH
                assert "collected_royalties" in result
                assert result["collected_royalties"] == 0

    def test_collect_royalties_transaction_build_failure(
        self, group: Group, mock_web3_is_address
    ):
        """Test collect_royalties when transaction building fails."""
        with mock_web3_is_address(True):
            with patch(
                "story_protocol_python_sdk.resources.Group.build_and_send_transaction",
                side_effect=Exception("Transaction build failed"),
            ):
                with pytest.raises(
                    ValueError,
                    match="Failed to collect royalties: Transaction build failed",
                ):
                    group.collect_royalties(
                        group_ip_id=IP_ID,
                        currency_token=ADDRESS,
                    )


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
                result = group.claim_rewards(
                    group_ip_id=IP_ID,
                    currency_token=ADDRESS,
                    member_ip_ids=[IP_ID, ADDRESS],
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


class TestGroupAddIpsToGroup:
    """Test class for Group.add_ips_to_group method"""

    def test_add_ips_to_group_invalid_group_ip_id(
        self, group: Group, mock_web3_is_address
    ):
        """Test add_ips_to_group with invalid group IP ID."""
        invalid_group_ip_id = "invalid_group_ip_id"
        with mock_web3_is_address(False):
            with pytest.raises(
                ValueError,
                match="Failed to add IP to group:",
            ):
                group.add_ips_to_group(
                    group_ip_id=invalid_group_ip_id,
                    ip_ids=[IP_ID],
                )

    def test_add_ips_to_group_invalid_ip_id(self, group: Group, mock_web3):
        """Test add_ips_to_group with invalid IP ID."""
        invalid_ip_id = "invalid_ip_id"
        with patch.object(mock_web3, "is_address") as mock_is_address:
            mock_is_address.side_effect = [True, False]
            with pytest.raises(
                ValueError,
                match="Failed to add IP to group:",
            ):
                group.add_ips_to_group(
                    group_ip_id=IP_ID,
                    ip_ids=[invalid_ip_id],
                )

    def test_add_ips_to_group_max_reward_share_exceeds_100(
        self, group: Group, mock_web3_is_address
    ):
        """Test add_ips_to_group rejects max_allowed_reward_share_percentage > 100 (via get_revenue_share)."""
        with mock_web3_is_address():
            with patch.object(
                group.dispute_module_client, "isIpTagged", return_value=False
            ), patch.object(
                group.ip_asset_registry_client,
                "isRegisteredGroup",
                return_value=False,
            ):
                with pytest.raises(
                    ValueError,
                    match="must be between 0 and 100",
                ):
                    group.add_ips_to_group(
                        group_ip_id=IP_ID,
                        ip_ids=[IP_ID],
                        max_allowed_reward_share_percentage=101,
                    )

    def test_add_ips_to_group_disputed_group(self, group: Group, mock_web3_is_address):
        """Test add_ips_to_group rejects disputed group."""
        with mock_web3_is_address():
            with patch.object(
                group.dispute_module_client, "isIpTagged", return_value=True
            ):
                with pytest.raises(
                    ValueError,
                    match="Disputed group cannot add IP",
                ):
                    group.add_ips_to_group(
                        group_ip_id=IP_ID,
                        ip_ids=[IP_ID],
                    )

    def test_add_ips_to_group_disputed_ip(self, group: Group, mock_web3_is_address):
        """Test add_ips_to_group rejects disputed IP in ip_ids."""
        with mock_web3_is_address():
            with patch.object(
                group.dispute_module_client,
                "isIpTagged",
                side_effect=[False, True],  # group ok, first ip disputed
            ):
                with pytest.raises(
                    ValueError,
                    match="Cannot add disputed IP to group",
                ):
                    group.add_ips_to_group(
                        group_ip_id=IP_ID,
                        ip_ids=[IP_ID, ADDRESS],
                    )

    def test_add_ips_to_group_ip_is_registered_group(
        self, group: Group, mock_web3_is_address
    ):
        """Test add_ips_to_group rejects IP that is a registered group."""
        with mock_web3_is_address():
            with patch.object(
                group.dispute_module_client, "isIpTagged", return_value=False
            ), patch.object(
                group.ip_asset_registry_client,
                "isRegisteredGroup",
                side_effect=[False, True],  # first ip ok, second ip is group
            ):
                with pytest.raises(
                    ValueError,
                    match="Cannot add group to group",
                ):
                    group.add_ips_to_group(
                        group_ip_id=IP_ID,
                        ip_ids=[IP_ID, ADDRESS],
                    )

    def test_add_ips_to_group_success(
        self,
        group: Group,
        mock_web3_is_address,
    ):
        """Test successful add_ips_to_group operation."""
        with mock_web3_is_address():
            with patch.object(
                group.dispute_module_client, "isIpTagged", return_value=False
            ), patch.object(
                group.ip_asset_registry_client,
                "isRegisteredGroup",
                return_value=False,
            ), patch(
                "story_protocol_python_sdk.resources.Group.build_and_send_transaction",
                return_value={"tx_hash": TX_HASH, "tx_receipt": {}},
            ):
                result = group.add_ips_to_group(
                    group_ip_id=IP_ID,
                    ip_ids=[IP_ID, ADDRESS],
                )

                assert "tx_hash" in result
                assert result["tx_hash"] == TX_HASH

    def test_add_ips_to_group_default_max_allowed_reward_share_percentage(
        self,
        group: Group,
        mock_web3_is_address,
    ):
        """Test add_ips_to_group uses default max_allowed_reward_share_percentage 100."""
        with mock_web3_is_address():
            with patch.object(
                group.dispute_module_client, "isIpTagged", return_value=False
            ), patch.object(
                group.ip_asset_registry_client,
                "isRegisteredGroup",
                return_value=False,
            ), patch(
                "story_protocol_python_sdk.resources.Group.build_and_send_transaction",
                return_value={"tx_hash": TX_HASH, "tx_receipt": {}},
            ) as mock_build:
                group.add_ips_to_group(
                    group_ip_id=IP_ID,
                    ip_ids=[IP_ID],
                )
                # 100 -> 100 * 10**6
                call_args = mock_build.call_args[0]
                assert call_args[5] == 100 * 10**6

    def test_add_ips_to_group_max_allowed_reward_share_percentage_zero(
        self,
        group: Group,
        mock_web3_is_address,
    ):
        """Test add_ips_to_group with max_allowed_reward_share_percentage 0."""
        with mock_web3_is_address():
            with patch.object(
                group.dispute_module_client, "isIpTagged", return_value=False
            ), patch.object(
                group.ip_asset_registry_client,
                "isRegisteredGroup",
                return_value=False,
            ), patch(
                "story_protocol_python_sdk.resources.Group.build_and_send_transaction",
                return_value={"tx_hash": TX_HASH, "tx_receipt": {}},
            ) as mock_build:
                group.add_ips_to_group(
                    group_ip_id=IP_ID,
                    ip_ids=[IP_ID],
                    max_allowed_reward_share_percentage=0,
                )
                call_args = mock_build.call_args[0]
                assert call_args[5] == 0

    def test_add_ips_to_group_transaction_fails(
        self, group: Group, mock_web3_is_address
    ):
        """Test add_ips_to_group when transaction build/send fails."""
        with mock_web3_is_address():
            with patch.object(
                group.dispute_module_client, "isIpTagged", return_value=False
            ), patch.object(
                group.ip_asset_registry_client,
                "isRegisteredGroup",
                return_value=False,
            ), patch(
                "story_protocol_python_sdk.resources.Group.build_and_send_transaction",
                side_effect=Exception("Transaction build failed"),
            ):
                with pytest.raises(
                    ValueError,
                    match="Failed to add IP to group: Transaction build failed",
                ):
                    group.add_ips_to_group(
                        group_ip_id=IP_ID,
                        ip_ids=[IP_ID],
                    )


class TestGroupRemoveIpsFromGroup:
    """Test class for Group.remove_ips_from_group method"""

    def test_remove_ips_from_group_invalid_group_ip_id(
        self, group: Group, mock_web3_is_address
    ):
        """Test remove_ips_from_group with invalid group IP ID."""
        invalid_group_ip_id = "invalid_group_ip_id"
        with mock_web3_is_address(False):
            with pytest.raises(
                ValueError,
                match="Failed to remove IPs from group:",
            ):
                group.remove_ips_from_group(
                    group_ip_id=invalid_group_ip_id,
                    ip_ids=[IP_ID],
                )

    def test_remove_ips_from_group_group_has_derivative_ips(
        self, group: Group, mock_web3_is_address
    ):
        """Test remove_ips_from_group rejects when group has derivative IPs."""
        with mock_web3_is_address():
            with patch.object(
                group.license_registry_client,
                "hasDerivativeIps",
                return_value=True,
            ):
                with pytest.raises(
                    ValueError,
                    match="Group frozen:.*has derivative IPs",
                ):
                    group.remove_ips_from_group(
                        group_ip_id=IP_ID,
                        ip_ids=[IP_ID],
                    )

    def test_remove_ips_from_group_group_has_minted_license_tokens(
        self, group: Group, mock_web3_is_address
    ):
        """Test remove_ips_from_group rejects when group has minted license tokens."""
        with mock_web3_is_address():
            with patch.object(
                group.license_registry_client,
                "hasDerivativeIps",
                return_value=False,
            ), patch.object(
                group.license_token_client,
                "getTotalTokensByLicensor",
                return_value=10,
            ):
                with pytest.raises(
                    ValueError,
                    match="Group frozen:.*has already minted license tokens",
                ):
                    group.remove_ips_from_group(
                        group_ip_id=IP_ID,
                        ip_ids=[IP_ID],
                    )

    def test_remove_ips_from_group_invalid_ip_id(self, group: Group, mock_web3):
        """Test remove_ips_from_group with invalid IP ID."""
        invalid_ip_id = "invalid_ip_id"
        with patch.object(mock_web3, "is_address") as mock_is_address:
            mock_is_address.side_effect = [True, False]
            with pytest.raises(
                ValueError,
                match="Failed to remove IPs from group:",
            ):
                group.remove_ips_from_group(
                    group_ip_id=IP_ID,
                    ip_ids=[invalid_ip_id],
                )

    def test_remove_ips_from_group_success(
        self,
        group: Group,
        mock_web3_is_address,
    ):
        """Test successful remove_ips_from_group operation."""
        with mock_web3_is_address():
            with patch.object(
                group.license_registry_client,
                "hasDerivativeIps",
                return_value=False,
            ), patch.object(
                group.license_token_client,
                "getTotalTokensByLicensor",
                return_value=0,
            ), patch(
                "story_protocol_python_sdk.resources.Group.build_and_send_transaction",
                return_value={"tx_hash": TX_HASH, "tx_receipt": {}},
            ):
                result = group.remove_ips_from_group(
                    group_ip_id=IP_ID,
                    ip_ids=[IP_ID, ADDRESS],
                )

                assert "tx_hash" in result
                assert result["tx_hash"] == TX_HASH

    def test_remove_ips_from_group_transaction_fails(
        self, group: Group, mock_web3_is_address
    ):
        """Test remove_ips_from_group when transaction build/send fails."""
        with mock_web3_is_address():
            with patch.object(
                group.license_registry_client,
                "hasDerivativeIps",
                return_value=False,
            ), patch.object(
                group.license_token_client,
                "getTotalTokensByLicensor",
                return_value=0,
            ), patch(
                "story_protocol_python_sdk.resources.Group.build_and_send_transaction",
                side_effect=Exception("Transaction build failed"),
            ):
                with pytest.raises(
                    ValueError,
                    match="Failed to remove IPs from group: Transaction build failed",
                ):
                    group.remove_ips_from_group(
                        group_ip_id=IP_ID,
                        ip_ids=[IP_ID],
                    )


class TestGroupGetClaimableReward:
    """Test class for Group.get_claimable_reward method"""

    def test_get_claimable_reward_invalid_group_ip_id(
        self, group: Group, mock_web3_is_address
    ):
        """Test get_claimable_reward with invalid group IP ID."""
        invalid_group_ip_id = "invalid_group_ip_id"
        with mock_web3_is_address(False):
            with pytest.raises(
                ValueError,
                match=f"Failed to get claimable rewards: Invalid group IP ID: {invalid_group_ip_id}",
            ):
                group.get_claimable_reward(
                    group_ip_id=invalid_group_ip_id,
                    currency_token=ADDRESS,
                    member_ip_ids=[IP_ID],
                )

    def test_get_claimable_reward_invalid_currency_token(self, group: Group, mock_web3):
        """Test get_claimable_reward with invalid currency token."""
        invalid_currency_token = "invalid_currency_token"
        with patch.object(mock_web3, "is_address") as mock_is_address:
            # group_ip_id=True, currency_token=False, member_ip_ids=True
            mock_is_address.side_effect = [True, False]
            with pytest.raises(
                ValueError,
                match=f"Failed to get claimable rewards: Invalid currency token: {invalid_currency_token}",
            ):
                group.get_claimable_reward(
                    group_ip_id=IP_ID,
                    currency_token=invalid_currency_token,
                    member_ip_ids=[IP_ID],
                )

    def test_get_claimable_reward_invalid_member_ip_id(self, group: Group, mock_web3):
        """Test get_claimable_reward with invalid member IP ID."""
        invalid_member_ip_id = "invalid_member_ip_id"
        with patch.object(mock_web3, "is_address") as mock_is_address:
            # group_ip_id=True, currency_token=True, first_member=True, second_member=False
            mock_is_address.side_effect = [True, True, True, False]
            with pytest.raises(
                ValueError,
                match=f"Failed to get claimable rewards: Invalid member IP ID: {invalid_member_ip_id}",
            ):
                group.get_claimable_reward(
                    group_ip_id=IP_ID,
                    currency_token=ADDRESS,
                    member_ip_ids=[ADDRESS, invalid_member_ip_id],
                )

    def test_get_claimable_reward_success(
        self,
        group: Group,
        mock_web3_is_address,
    ):
        """Test successful get_claimable_reward operation."""
        expected_claimable_rewards = [100, 200, 300]
        member_ip_ids = [IP_ID, ADDRESS, ADDRESS]

        with mock_web3_is_address():
            with patch.object(
                group.grouping_module_client,
                "getClaimableReward",
                return_value=expected_claimable_rewards,
            ) as mock_get_claimable_reward:
                result = group.get_claimable_reward(
                    group_ip_id=IP_ID,
                    currency_token=ADDRESS,
                    member_ip_ids=member_ip_ids,
                )

                # Verify the result
                assert result == expected_claimable_rewards
                assert len(result) == len(member_ip_ids)
                mock_get_claimable_reward.assert_called_once_with(
                    groupId=IP_ID,
                    token=ADDRESS,
                    ipIds=member_ip_ids,
                )

    def test_get_claimable_reward_empty_member_ip_ids(
        self,
        group: Group,
        mock_web3_is_address,
    ):
        """Test get_claimable_reward with empty member IP IDs list."""
        expected_claimable_rewards: list[int] = []

        with mock_web3_is_address():
            with patch.object(
                group.grouping_module_client,
                "getClaimableReward",
                return_value=expected_claimable_rewards,
            ) as mock_get_claimable_reward:
                result = group.get_claimable_reward(
                    group_ip_id=IP_ID,
                    currency_token=ADDRESS,
                    member_ip_ids=[],
                )

                # Verify the result
                assert result == expected_claimable_rewards
                assert len(result) == 0

                # Verify the client method was called with correct parameters
                mock_get_claimable_reward.assert_called_once_with(
                    groupId=IP_ID,
                    token=ADDRESS,
                    ipIds=[],
                )

    def test_get_claimable_reward_client_call_failure(
        self, group: Group, mock_web3_is_address
    ):
        """Test get_claimable_reward when client call fails."""
        with mock_web3_is_address():
            with patch.object(
                group.grouping_module_client,
                "getClaimableReward",
                side_effect=Exception("Client call failed"),
            ):
                with pytest.raises(
                    ValueError,
                    match="Failed to get claimable rewards: Client call failed",
                ):
                    group.get_claimable_reward(
                        group_ip_id=IP_ID,
                        currency_token=ADDRESS,
                        member_ip_ids=[IP_ID],
                    )
