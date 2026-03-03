from unittest.mock import patch

import pytest

from story_protocol_python_sdk.resources.Royalty import Royalty
from story_protocol_python_sdk.utils.constants import WIP_TOKEN_ADDRESS
from tests.unit.fixtures.data import ACCOUNT_ADDRESS, ADDRESS, TX_HASH


@pytest.fixture(scope="class")
def royalty_client(mock_web3, mock_account):
    return Royalty(mock_web3, mock_account, 1)


class TestBatchClaimAllRevenue:
    def test_batch_claim_all_revenue_single_ancestor(self, royalty_client):
        """Test batch claim with single ancestor IP (should call claim_all_revenue)"""
        with patch.object(
            royalty_client,
            "claim_all_revenue",
            return_value={
                "tx_hashes": [TX_HASH.hex()],
                "receipt": {"logs": []},
                "claimed_tokens": [
                    {
                        "claimer": ADDRESS,
                        "token": WIP_TOKEN_ADDRESS,
                        "amount": 1000,
                    }
                ],
            },
        ):
            result = royalty_client.batch_claim_all_revenue(
                ancestor_ips=[
                    {
                        "ip_id": ADDRESS,
                        "claimer": ADDRESS,
                        "child_ip_ids": [],
                        "royalty_policies": [],
                        "currency_tokens": [WIP_TOKEN_ADDRESS],
                    }
                ],
            )
            assert len(result["tx_hashes"]) >= 1
            assert len(result["receipts"]) == 1
            assert len(result["claimed_tokens"]) == 1

    def test_batch_claim_all_revenue_multiple_ancestors_with_multicall(
        self, royalty_client
    ):
        """Test batch claim with multiple ancestors using multicall"""
        with patch.object(
            royalty_client.royalty_workflows_client.contract.functions,
            "claimAllRevenue",
            return_value=type(
                "MockFunction",
                (),
                {
                    "build_transaction": lambda self, opts: {"data": "0x1234"},
                    "_encode_transaction_data": lambda self: "0x1234",
                },
            )(),
        ):
            with patch.object(
                royalty_client,
                "_parse_tx_revenue_token_claimed_event",
                return_value=[
                    {
                        "claimer": ADDRESS,
                        "token": WIP_TOKEN_ADDRESS,
                        "amount": 1000,
                    },
                    {
                        "claimer": ACCOUNT_ADDRESS,
                        "token": WIP_TOKEN_ADDRESS,
                        "amount": 2000,
                    },
                ],
            ):
                with patch.object(
                    royalty_client,
                    "_get_claimer_info",
                    return_value=(False, False, None),
                ):
                    with patch(
                        "story_protocol_python_sdk.resources.Royalty.build_and_send_transaction",
                        return_value={
                            "tx_hash": TX_HASH.hex(),
                            "tx_receipt": {"logs": []},
                        },
                    ):
                        result = royalty_client.batch_claim_all_revenue(
                            ancestor_ips=[
                                {
                                    "ip_id": ADDRESS,
                                    "claimer": ADDRESS,
                                    "child_ip_ids": [],
                                    "royalty_policies": [],
                                    "currency_tokens": [WIP_TOKEN_ADDRESS],
                                },
                                {
                                    "ip_id": ACCOUNT_ADDRESS,
                                    "claimer": ACCOUNT_ADDRESS,
                                    "child_ip_ids": [],
                                    "royalty_policies": [],
                                    "currency_tokens": [WIP_TOKEN_ADDRESS],
                                },
                            ],
                        )
                    assert len(result["tx_hashes"]) == 1
                    assert len(result["receipts"]) == 1
                    assert len(result["claimed_tokens"]) == 2

    def test_batch_claim_all_revenue_without_multicall(self, royalty_client):
        """Test batch claim with multicall disabled"""
        with patch.object(
            royalty_client,
            "claim_all_revenue",
            return_value={
                "tx_hashes": [TX_HASH.hex()],
                "receipt": {"logs": []},
                "claimed_tokens": [
                    {
                        "claimer": ADDRESS,
                        "token": WIP_TOKEN_ADDRESS,
                        "amount": 1000,
                    }
                ],
            },
        ):
            result = royalty_client.batch_claim_all_revenue(
                ancestor_ips=[
                    {
                        "ip_id": ADDRESS,
                        "claimer": ADDRESS,
                        "child_ip_ids": [],
                        "royalty_policies": [],
                        "currency_tokens": [WIP_TOKEN_ADDRESS],
                    },
                    {
                        "ip_id": ACCOUNT_ADDRESS,
                        "claimer": ACCOUNT_ADDRESS,
                        "child_ip_ids": [],
                        "royalty_policies": [],
                        "currency_tokens": [WIP_TOKEN_ADDRESS],
                    },
                ],
                options={"use_multicall_when_possible": False},
            )
            assert len(result["tx_hashes"]) >= 2
            assert len(result["receipts"]) == 2

    def test_batch_claim_all_revenue_aggregates_tokens(self, royalty_client):
        """Test that claimed tokens are properly aggregated"""
        with patch.object(
            royalty_client,
            "claim_all_revenue",
            side_effect=[
                {
                    "tx_hashes": [TX_HASH.hex()],
                    "receipt": {"logs": []},
                    "claimed_tokens": [
                        {
                            "claimer": ADDRESS,
                            "token": WIP_TOKEN_ADDRESS,
                            "amount": 1000,
                        }
                    ],
                },
                {
                    "tx_hashes": [TX_HASH.hex()],
                    "receipt": {"logs": []},
                    "claimed_tokens": [
                        {
                            "claimer": ADDRESS,
                            "token": WIP_TOKEN_ADDRESS,
                            "amount": 500,
                        }
                    ],
                },
            ],
        ):
            result = royalty_client.batch_claim_all_revenue(
                ancestor_ips=[
                    {
                        "ip_id": ADDRESS,
                        "claimer": ADDRESS,
                        "child_ip_ids": [],
                        "royalty_policies": [],
                        "currency_tokens": [WIP_TOKEN_ADDRESS],
                    },
                    {
                        "ip_id": ACCOUNT_ADDRESS,
                        "claimer": ADDRESS,
                        "child_ip_ids": [],
                        "royalty_policies": [],
                        "currency_tokens": [WIP_TOKEN_ADDRESS],
                    },
                ],
                options={"use_multicall_when_possible": False},
            )
            # Should aggregate tokens for same claimer and token
            assert len(result["claimed_tokens"]) == 1
            assert result["claimed_tokens"][0]["amount"] == 1500
