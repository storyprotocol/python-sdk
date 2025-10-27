from unittest.mock import patch

import pytest
from web3 import Web3

from story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client import (
    IPAccountImplClient,
)
from story_protocol_python_sdk.resources.Royalty import Royalty
from story_protocol_python_sdk.utils.constants import WIP_TOKEN_ADDRESS
from tests.unit.fixtures.data import ACCOUNT_ADDRESS, ADDRESS, CHAIN_ID, TX_HASH


@pytest.fixture(scope="class")
def royalty_client(mock_web3, mock_account):
    return Royalty(mock_web3, mock_account, CHAIN_ID)


@pytest.fixture(scope="class")
def mock_is_registered(royalty_client: Royalty):
    def _mock(is_registered: bool = False):
        return patch.object(
            royalty_client.ip_asset_registry_client,
            "isRegistered",
            return_value=is_registered,
        )

    return _mock


def test_claimable_revenue_royalty_vault_ip_id_error(royalty_client):
    with patch.object(
        royalty_client.ip_asset_registry_client, "isRegistered", return_value=False
    ):
        child_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"

        with pytest.raises(
            ValueError, match=f"The IP with id {child_ip_id} is not registered."
        ):
            royalty_client.claimable_revenue(
                child_ip_id,
                ACCOUNT_ADDRESS,
                "0xB132A6B7AE652c974EE1557A3521D53d18F6739f",
            )


def test_claimable_revenue_success(royalty_client):
    with patch.object(
        royalty_client.ip_asset_registry_client, "isRegistered", return_value=True
    ):
        with patch.object(
            royalty_client,
            "get_royalty_vault_address",
            return_value="0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c",
        ):
            with patch(
                "story_protocol_python_sdk.abi.IpRoyaltyVaultImpl.IpRoyaltyVaultImpl_client.IpRoyaltyVaultImplClient.claimableRevenue",
                return_value=0,
            ):

                response = royalty_client.claimable_revenue(
                    "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c",
                    ACCOUNT_ADDRESS,
                    "0xB132A6B7AE652c974EE1557A3521D53d18F6739f",
                )
                assert response == 0


def test_pay_royalty_on_behalf_receiver_ip_id_error(royalty_client):
    with patch.object(
        royalty_client.ip_asset_registry_client, "isRegistered", return_value=False
    ):
        receiver_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
        with pytest.raises(
            ValueError,
            match=f"The receiver IP with id {receiver_ip_id} is not registered.",
        ):
            royalty_client.pay_royalty_on_behalf(
                receiver_ip_id,
                "0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7",
                "0xB132A6B7AE652c974EE1557A3521D53d18F6739f",
                1,
            )


def test_pay_royalty_on_behalf_payer_ip_id_error(royalty_client):
    with patch.object(
        royalty_client.ip_asset_registry_client,
        "isRegistered",
        side_effect=[True, False],
    ):
        receiver_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
        payer_ip_id = "0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"
        ERC20 = "0xB132A6B7AE652c974EE1557A3521D53d18F6739f"
        amount = 1

        with pytest.raises(
            ValueError, match=f"The payer IP with id {payer_ip_id} is not registered."
        ):
            royalty_client.pay_royalty_on_behalf(
                receiver_ip_id, payer_ip_id, ERC20, amount
            )


def test_pay_royalty_on_behalf_success(royalty_client):
    with patch.object(
        royalty_client.ip_asset_registry_client, "isRegistered", return_value=True
    ):
        with patch(
            "story_protocol_python_sdk.abi.RoyaltyModule.RoyaltyModule_client.RoyaltyModuleClient.build_payRoyaltyOnBehalf_transaction",
            return_value={
                "data": "0x",
                "nonce": 0,
                "gas": 2000000,
                "gasPrice": Web3.to_wei("300", "gwei"),
            },
        ):

            response = royalty_client.pay_royalty_on_behalf(
                "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c",
                "0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7",
                "0xB132A6B7AE652c974EE1557A3521D53d18F6739f",
                1,
            )
            assert response is not None
            assert "tx_hash" in response
            assert response["tx_hash"] == TX_HASH.hex()


class TestClaimAllRevenue:

    @pytest.fixture(scope="class")
    def mock_parse_tx_revenue_token_claimed_event(self, royalty_client: Royalty):
        return patch.object(
            royalty_client,
            "_parse_tx_revenue_token_claimed_event",
            return_value=[
                {
                    "claimer": ACCOUNT_ADDRESS,
                    "token": WIP_TOKEN_ADDRESS,
                    "amount": 120,
                }
            ],
        )

    @pytest.fixture(scope="class")
    def mock_ip_account_owner(self):
        def _mock(owner: str = ACCOUNT_ADDRESS):
            return patch.object(
                IPAccountImplClient,
                "owner",
                return_value=owner,
            )

        return _mock

    def test_claim_all_revenue_invalid_ancestor_ip_id(self, royalty_client: Royalty):
        ancestor_ip_id = "invalid_address"
        with pytest.raises(
            ValueError,
            match=f"Invalid address: {ancestor_ip_id}.",
        ):
            royalty_client.claim_all_revenue(
                ancestor_ip_id=ancestor_ip_id,
                claimer=ACCOUNT_ADDRESS,
                child_ip_ids=[],
                royalty_policies=[],
                currency_tokens=[],
            )

    def test_claim_all_revenue_invalid_claimer(self, royalty_client):
        ancestor_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
        claimer = "invalid_address"

        with pytest.raises(
            ValueError,
            match="Failed to claim all revenue: Invalid address: invalid_address.",
        ):
            royalty_client.claim_all_revenue(
                ancestor_ip_id=ancestor_ip_id,
                claimer=claimer,
                child_ip_ids=[],
                royalty_policies=[],
                currency_tokens=[],
            )

    def test_claim_all_revenue_invalid_child_ip_id(self, royalty_client):
        ancestor_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
        claimer = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
        child_ip_ids = ["invalid_address"]

        with pytest.raises(
            ValueError,
            match=r"Failed to claim all revenue: Invalid addresses: \['invalid_address'\]\.",
        ):
            royalty_client.claim_all_revenue(
                ancestor_ip_id=ancestor_ip_id,
                claimer=claimer,
                child_ip_ids=child_ip_ids,
                royalty_policies=[],
                currency_tokens=[],
            )

    def test_claim_all_revenue_invalid_royalty_policy(self, royalty_client):
        ancestor_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
        claimer = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
        child_ip_ids = ["0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"]
        royalty_policies = ["invalid_address"]

        with pytest.raises(
            ValueError,
            match=r"Failed to claim all revenue: Invalid addresses: \['invalid_address'\]\.",
        ):
            royalty_client.claim_all_revenue(
                ancestor_ip_id=ancestor_ip_id,
                claimer=claimer,
                child_ip_ids=child_ip_ids,
                royalty_policies=royalty_policies,
                currency_tokens=[],
            )

    def test_claim_all_revenue_invalid_currency_token(self, royalty_client):
        ancestor_ip_id = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
        claimer = "0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c"
        child_ip_ids = ["0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"]
        royalty_policies = ["0xBe54FB168b3c982b7AaE60dB6CF75Bd8447b390E"]
        currency_tokens = ["invalid_address"]

        with pytest.raises(
            ValueError,
            match=r"Failed to claim all revenue: Invalid addresses: \['invalid_address'\]\.",
        ):
            royalty_client.claim_all_revenue(
                ancestor_ip_id=ancestor_ip_id,
                claimer=claimer,
                child_ip_ids=child_ip_ids,
                royalty_policies=royalty_policies,
                currency_tokens=currency_tokens,
            )

    def test_claim_all_revenue_success_with_default_claim_options_and_is_claimer_ip_and_own_claimer(
        self,
        royalty_client: Royalty,
        mock_is_registered,
        mock_ip_account_owner,
        mock_parse_tx_revenue_token_claimed_event,
    ):
        """Test claim_all_revenue with default options (auto_transfer=True, auto_unwrap=True)"""
        TRANSFER_TX_HASH = b"transfer_tx_hash_bytes"
        WITHDRAW_TX_HASH = b"withdraw_tx_hash_bytes"
        with mock_is_registered(True), mock_ip_account_owner(
            ACCOUNT_ADDRESS
        ), mock_parse_tx_revenue_token_claimed_event:
            with patch(
                "story_protocol_python_sdk.resources.Royalty.build_and_send_transaction",
                side_effect=[
                    {"tx_hash": TX_HASH.hex(), "tx_receipt": {"status": 1}},
                    {"tx_hash": TRANSFER_TX_HASH.hex(), "tx_receipt": {"status": 1}},
                    {"tx_hash": WITHDRAW_TX_HASH.hex(), "tx_receipt": {"status": 1}},
                ],
            ) as mock_build_and_send:
                response = royalty_client.claim_all_revenue(
                    ancestor_ip_id="0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c",
                    claimer=ACCOUNT_ADDRESS,
                    child_ip_ids=["0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"],
                    royalty_policies=["0xBe54FB168b3c982b7AaE60dB6CF75Bd8447b390E"],
                    currency_tokens=["0xB132A6B7AE652c974EE1557A3521D53d18F6739f"],
                )
                assert mock_build_and_send.call_count == 3
                assert response is not None
                assert "tx_hashes" in response
                assert response["tx_hashes"] == [
                    TX_HASH.hex(),
                    TRANSFER_TX_HASH.hex(),
                    WITHDRAW_TX_HASH.hex(),
                ]
                assert "claimed_tokens" in response
                assert len(response["claimed_tokens"]) == 1
                assert response["claimed_tokens"][0]["amount"] == 120

    def test_claim_all_revenue_with_default_claim_options_and_claimer_is_ip_and_owns_claimer_and_token_is_not_wip(
        self,
        royalty_client: Royalty,
        mock_is_registered,
        mock_ip_account_owner,
    ):
        """Test claim_all_revenue with default options and claimer is ip and owns claimer and token is not wip"""
        TRANSFER_TX_HASH = b"transfer_tx_hash_bytes"
        with mock_is_registered(True), mock_ip_account_owner(ACCOUNT_ADDRESS):
            with patch.object(
                royalty_client,
                "_parse_tx_revenue_token_claimed_event",
                return_value=[
                    {
                        "claimer": ACCOUNT_ADDRESS,
                        "token": ADDRESS,
                        "amount": 120,
                    },
                ],
            ), patch(
                "story_protocol_python_sdk.resources.Royalty.build_and_send_transaction",
                side_effect=[
                    {"tx_hash": TX_HASH.hex(), "tx_receipt": {"status": 1}},
                    {"tx_hash": TRANSFER_TX_HASH.hex(), "tx_receipt": {"status": 1}},
                ],
            ) as mock_build_and_send:
                response = royalty_client.claim_all_revenue(
                    ancestor_ip_id="0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c",
                    claimer=ACCOUNT_ADDRESS,
                    child_ip_ids=["0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"],
                    royalty_policies=["0xBe54FB168b3c982b7AaE60dB6CF75Bd8447b390E"],
                    currency_tokens=["0xB132A6B7AE652c974EE1557A3521D53d18F6739f"],
                )
                assert mock_build_and_send.call_count == 2
                assert response is not None
                assert "tx_hashes" in response
                assert response["tx_hashes"] == [TX_HASH.hex(), TRANSFER_TX_HASH.hex()]
                assert "claimed_tokens" in response
                assert len(response["claimed_tokens"]) == 1
                assert response["claimed_tokens"][0]["amount"] == 120

    def test_claim_all_revenue_with_default_claim_options_and_claimer_is_ip_and_own_claimer_and_tokens_have_multiple_wip(
        self,
        royalty_client: Royalty,
        mock_is_registered,
        mock_ip_account_owner,
        mock_parse_tx_revenue_token_claimed_event,
    ):
        """Test claim_all_revenue with default options and claimer is ip and owns claimer and tokens have multiple wip"""
        TRANSFER_TX_HASH = b"transfer_tx_hash_bytes"
        with mock_is_registered(True), mock_ip_account_owner(
            ACCOUNT_ADDRESS
        ), mock_parse_tx_revenue_token_claimed_event:
            with patch(
                "story_protocol_python_sdk.resources.Royalty.build_and_send_transaction",
                side_effect=[
                    {"tx_hash": TX_HASH.hex(), "tx_receipt": {"status": 1}},
                    {"tx_hash": TRANSFER_TX_HASH.hex(), "tx_receipt": {"status": 1}},
                ],
            ), patch.object(
                royalty_client,
                "_parse_tx_revenue_token_claimed_event",
                return_value=[
                    {
                        "claimer": ACCOUNT_ADDRESS,
                        "token": WIP_TOKEN_ADDRESS,
                        "amount": 120,
                    },
                    {
                        "claimer": ACCOUNT_ADDRESS,
                        "token": WIP_TOKEN_ADDRESS,
                        "amount": 120,
                    },
                ],
            ):
                with pytest.raises(
                    ValueError,
                    match="Failed to claim all revenue: Multiple WIP tokens found in the claimed tokens.",
                ):
                    royalty_client.claim_all_revenue(
                        ancestor_ip_id="0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c",
                        claimer=ACCOUNT_ADDRESS,
                        child_ip_ids=["0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"],
                        royalty_policies=["0xBe54FB168b3c982b7AaE60dB6CF75Bd8447b390E"],
                        currency_tokens=["0xB132A6B7AE652c974EE1557A3521D53d18F6739f"],
                    )

    def test_claim_all_revenue_with_default_claim_options_and_claimer_is_ip_and_own_claimer_and_token_amount_is_zero(
        self,
        royalty_client: Royalty,
        mock_is_registered,
        mock_ip_account_owner,
    ):
        """Test claim_all_revenue with default options and claimer is ip and owns claimer and token amount is zero"""
        with mock_is_registered(True), mock_ip_account_owner(ACCOUNT_ADDRESS):
            with patch(
                "story_protocol_python_sdk.resources.Royalty.build_and_send_transaction",
                return_value={
                    "tx_hash": TX_HASH.hex(),
                    "tx_receipt": {
                        "logs": [
                            {
                                "topics": [
                                    Web3.keccak(
                                        text="RevenueTokenClaimed(address,address,uint256)"
                                    )
                                ],
                            },
                        ],
                    },
                },
            ) as mock_build_and_send, patch.object(
                royalty_client.ip_royalty_vault_client.contract.events.RevenueTokenClaimed,
                "process_log",
                return_value={
                    "args": {
                        "claimer": ACCOUNT_ADDRESS,
                        "token": WIP_TOKEN_ADDRESS,
                        "amount": 0,
                    },
                },
            ):
                response = royalty_client.claim_all_revenue(
                    ancestor_ip_id="0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c",
                    claimer=ACCOUNT_ADDRESS,
                    child_ip_ids=["0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"],
                    royalty_policies=["0xBe54FB168b3c982b7AaE60dB6CF75Bd8447b390E"],
                    currency_tokens=["0xB132A6B7AE652c974EE1557A3521D53d18F6739f"],
                )
                assert mock_build_and_send.call_count == 1
                assert response is not None
                assert "tx_hashes" in response
                assert response["tx_hashes"] == [TX_HASH.hex()]
                assert "claimed_tokens" in response
                assert len(response["claimed_tokens"]) == 1
                assert response["claimed_tokens"][0]["amount"] == 0

    def test_claim_all_revenue_with_default_claim_options_and_claimer_is_ip_and_not_own_claimer(
        self,
        royalty_client: Royalty,
        mock_is_registered,
        mock_ip_account_owner,
        mock_parse_tx_revenue_token_claimed_event,
    ):
        """Test claim_all_revenue with default options (auto_transfer=True, auto_unwrap=True)"""
        with mock_is_registered(True), mock_ip_account_owner(
            ADDRESS
        ), mock_parse_tx_revenue_token_claimed_event:
            with patch(
                "story_protocol_python_sdk.resources.Royalty.build_and_send_transaction",
                return_value={"tx_hash": TX_HASH.hex(), "tx_receipt": {"status": 1}},
            ) as mock_build_and_send:
                response = royalty_client.claim_all_revenue(
                    ancestor_ip_id="0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c",
                    claimer=ADDRESS,
                    child_ip_ids=["0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"],
                    royalty_policies=["0xBe54FB168b3c982b7AaE60dB6CF75Bd8447b390E"],
                    currency_tokens=["0xB132A6B7AE652c974EE1557A3521D53d18F6739f"],
                )
                assert mock_build_and_send.call_count == 1
                assert response is not None
                assert "tx_hashes" in response
                assert response["tx_hashes"] == [TX_HASH.hex()]
                assert "claimed_tokens" in response
                assert len(response["claimed_tokens"]) == 1
                assert response["claimed_tokens"][0]["amount"] == 120

    def test_claim_all_revenue_with_default_claim_options_and_not_claimer_ip_and_own_claimer(
        self,
        royalty_client: Royalty,
        mock_is_registered,
        mock_ip_account_owner,
        mock_parse_tx_revenue_token_claimed_event,
    ):
        """Test claim_all_revenue with default options (auto_transfer=True, auto_unwrap=True)"""
        WITHDRAW_TX_HASH = b"withdraw_tx_hash_bytes"
        with mock_is_registered(), mock_ip_account_owner(
            ACCOUNT_ADDRESS
        ), mock_parse_tx_revenue_token_claimed_event:
            with patch(
                "story_protocol_python_sdk.resources.Royalty.build_and_send_transaction",
                side_effect=[
                    {"tx_hash": TX_HASH.hex(), "tx_receipt": {"status": 1}},
                    {"tx_hash": WITHDRAW_TX_HASH.hex(), "tx_receipt": {"status": 1}},
                ],
            ) as mock_build_and_send:
                response = royalty_client.claim_all_revenue(
                    ancestor_ip_id="0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c",
                    claimer=ACCOUNT_ADDRESS,
                    child_ip_ids=["0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"],
                    royalty_policies=["0xBe54FB168b3c982b7AaE60dB6CF75Bd8447b390E"],
                    currency_tokens=["0xB132A6B7AE652c974EE1557A3521D53d18F6739f"],
                )
                assert (
                    mock_build_and_send.call_count == 2
                )  # claim_all_revenue and withdraw
                assert response is not None
                assert "tx_hashes" in response
                assert response["tx_hashes"] == [TX_HASH.hex(), WITHDRAW_TX_HASH.hex()]
                assert "claimed_tokens" in response
                assert len(response["claimed_tokens"]) == 1
                assert response["claimed_tokens"][0]["amount"] == 120

    def test_claim_all_revenue_with_auto_transfer_false_and_own_claimer(
        self,
        royalty_client: Royalty,
        mock_is_registered,
        mock_ip_account_owner,
        mock_parse_tx_revenue_token_claimed_event,
    ):
        """Test claim_all_revenue with auto_transfer_all_claimed_tokens_from_ip=False"""
        WITHDRAW_TX_HASH = b"withdraw_tx_hash_bytes"
        with mock_is_registered(True), mock_ip_account_owner(
            ACCOUNT_ADDRESS
        ), mock_parse_tx_revenue_token_claimed_event:
            with patch(
                "story_protocol_python_sdk.resources.Royalty.build_and_send_transaction",
                side_effect=[
                    {"tx_hash": TX_HASH.hex(), "tx_receipt": {"status": 1}},
                    {"tx_hash": WITHDRAW_TX_HASH.hex(), "tx_receipt": {"status": 1}},
                ],
            ) as mock_build_and_send:
                response = royalty_client.claim_all_revenue(
                    ancestor_ip_id="0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c",
                    claimer=ACCOUNT_ADDRESS,
                    child_ip_ids=["0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"],
                    royalty_policies=["0xBe54FB168b3c982b7AaE60dB6CF75Bd8447b390E"],
                    currency_tokens=["0xB132A6B7AE652c974EE1557A3521D53d18F6739f"],
                    claim_options={"auto_transfer_all_claimed_tokens_from_ip": False},
                )
                assert mock_build_and_send.call_count == 2
                assert response is not None
                assert "tx_hashes" in response
                assert response["tx_hashes"] == [TX_HASH.hex(), WITHDRAW_TX_HASH.hex()]
                assert "claimed_tokens" in response
                assert len(response["claimed_tokens"]) == 1

    def test_claim_all_revenue_with_auto_transfer_false_and_not_own_claimer(
        self,
        royalty_client: Royalty,
        mock_is_registered,
        mock_ip_account_owner,
        mock_parse_tx_revenue_token_claimed_event,
    ):
        """Test claim_all_revenue with auto_transfer_all_claimed_tokens_from_ip=False"""
        WITHDRAW_TX_HASH = b"withdraw_tx_hash_bytes"
        with mock_is_registered(), mock_ip_account_owner(
            ADDRESS
        ), mock_parse_tx_revenue_token_claimed_event:
            with patch(
                "story_protocol_python_sdk.resources.Royalty.build_and_send_transaction",
                side_effect=[
                    {"tx_hash": TX_HASH.hex(), "tx_receipt": {"status": 1}},
                    {"tx_hash": WITHDRAW_TX_HASH.hex(), "tx_receipt": {"status": 1}},
                ],
            ) as mock_build_and_send:
                response = royalty_client.claim_all_revenue(
                    ancestor_ip_id="0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c",
                    claimer=ADDRESS,
                    child_ip_ids=["0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"],
                    royalty_policies=["0xBe54FB168b3c982b7AaE60dB6CF75Bd8447b390E"],
                    currency_tokens=["0xB132A6B7AE652c974EE1557A3521D53d18F6739f"],
                    claim_options={"auto_transfer_all_claimed_tokens_from_ip": False},
                )
                assert mock_build_and_send.call_count == 1
                assert response is not None
                assert "tx_hashes" in response
                assert response["tx_hashes"] == [TX_HASH.hex()]
                assert "claimed_tokens" in response
                assert len(response["claimed_tokens"]) == 1
                assert response["claimed_tokens"][0]["amount"] == 120

    def test_claim_all_revenue_with_auto_unwrap_false_and_own_claimer_ip_and_owns_claimer(
        self,
        royalty_client: Royalty,
        mock_is_registered,
        mock_ip_account_owner,
        mock_parse_tx_revenue_token_claimed_event,
    ):
        """Test claim_all_revenue with auto_unwrap_ip_tokens=False"""
        TRANSFER_TX_HASH = b"transfer_tx_hash_bytes"
        with mock_is_registered(True), mock_ip_account_owner(
            ACCOUNT_ADDRESS
        ), mock_parse_tx_revenue_token_claimed_event:
            with patch(
                "story_protocol_python_sdk.resources.Royalty.build_and_send_transaction",
                side_effect=[
                    {"tx_hash": TX_HASH.hex(), "tx_receipt": {"status": 1}},
                    {"tx_hash": TRANSFER_TX_HASH.hex(), "tx_receipt": {"status": 1}},
                ],
            ) as mock_build_and_send:
                response = royalty_client.claim_all_revenue(
                    ancestor_ip_id="0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c",
                    claimer=ACCOUNT_ADDRESS,
                    child_ip_ids=["0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"],
                    royalty_policies=["0xBe54FB168b3c982b7AaE60dB6CF75Bd8447b390E"],
                    currency_tokens=["0xB132A6B7AE652c974EE1557A3521D53d18F6739f"],
                    claim_options={"auto_unwrap_ip_tokens": False},
                )
                assert mock_build_and_send.call_count == 2
                assert response is not None
                assert "tx_hashes" in response
                assert response["tx_hashes"] == [TX_HASH.hex(), TRANSFER_TX_HASH.hex()]
                assert "claimed_tokens" in response
                assert len(response["claimed_tokens"]) == 1
                assert response["claimed_tokens"][0]["amount"] == 120

    def test_claim_all_revenue_with_auto_unwrap_false_and_own_claimer_ip_and_not_owns_claimer(
        self,
        royalty_client: Royalty,
        mock_is_registered,
        mock_ip_account_owner,
        mock_parse_tx_revenue_token_claimed_event,
    ):
        """Test claim_all_revenue with auto_unwrap_ip_tokens=False"""
        TRANSFER_TX_HASH = b"transfer_tx_hash_bytes"
        with mock_is_registered(True), mock_ip_account_owner(
            ADDRESS
        ), mock_parse_tx_revenue_token_claimed_event:
            with patch(
                "story_protocol_python_sdk.resources.Royalty.build_and_send_transaction",
                side_effect=[
                    {"tx_hash": TX_HASH.hex(), "tx_receipt": {"status": 1}},
                    {"tx_hash": TRANSFER_TX_HASH.hex(), "tx_receipt": {"status": 1}},
                ],
            ) as mock_build_and_send:
                response = royalty_client.claim_all_revenue(
                    ancestor_ip_id="0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c",
                    claimer=ACCOUNT_ADDRESS,
                    child_ip_ids=["0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"],
                    royalty_policies=["0xBe54FB168b3c982b7AaE60dB6CF75Bd8447b390E"],
                    currency_tokens=["0xB132A6B7AE652c974EE1557A3521D53d18F6739f"],
                    claim_options={"auto_unwrap_ip_tokens": False},
                )
                assert mock_build_and_send.call_count == 1
                assert response is not None
                assert "tx_hashes" in response
                assert response["tx_hashes"] == [TX_HASH.hex()]
                assert "claimed_tokens" in response
                assert len(response["claimed_tokens"]) == 1
                assert response["claimed_tokens"][0]["amount"] == 120

    def test_claim_all_revenue_with_auto_unwrap_false_and_not_own_claimer_ip_and_owns_claimer(
        self,
        royalty_client: Royalty,
        mock_is_registered,
        mock_ip_account_owner,
        mock_parse_tx_revenue_token_claimed_event,
    ):
        """Test claim_all_revenue with auto_unwrap_ip_tokens=False"""
        TRANSFER_TX_HASH = b"transfer_tx_hash_bytes"
        with mock_is_registered(), mock_ip_account_owner(
            ACCOUNT_ADDRESS
        ), mock_parse_tx_revenue_token_claimed_event:
            with patch(
                "story_protocol_python_sdk.resources.Royalty.build_and_send_transaction",
                side_effect=[
                    {"tx_hash": TX_HASH.hex(), "tx_receipt": {"status": 1}},
                    {"tx_hash": TRANSFER_TX_HASH.hex(), "tx_receipt": {"status": 1}},
                ],
            ) as mock_build_and_send:
                response = royalty_client.claim_all_revenue(
                    ancestor_ip_id="0xA34611b0E11Bba2b11c69864f7D36aC83D862A9c",
                    claimer=ADDRESS,
                    child_ip_ids=["0x9C098DF37b2324aaC8792dDc7BcEF7Bb0057A9C7"],
                    royalty_policies=["0xBe54FB168b3c982b7AaE60dB6CF75Bd8447b390E"],
                    currency_tokens=["0xB132A6B7AE652c974EE1557A3521D53d18F6739f"],
                    claim_options={"auto_unwrap_ip_tokens": False},
                )
                assert mock_build_and_send.call_count == 1
                assert response is not None
                assert "tx_hashes" in response
                assert response["tx_hashes"] == [TX_HASH.hex()]
                assert "claimed_tokens" in response
                assert len(response["claimed_tokens"]) == 1
