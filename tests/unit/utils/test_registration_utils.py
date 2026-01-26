from unittest.mock import MagicMock, patch

import pytest
from ens.ens import HexStr

from story_protocol_python_sdk import RoyaltyShareInput
from story_protocol_python_sdk.types.resource.IPAsset import (
    ExtraData,
    IPRoyaltyVault,
    TransformedRegistrationRequest,
)
from story_protocol_python_sdk.utils.registration.registration_utils import (
    aggregate_multicall_requests,
    prepare_distribute_royalty_tokens_requests,
)
from tests.unit.fixtures.data import ADDRESS, LICENSE_TERMS_DATA_CAMEL_CASE


@pytest.fixture
def mock_multicall3_client():
    """Mock Multicall3Client."""

    def _mock():
        return patch(
            "story_protocol_python_sdk.utils.registration.registration_utils.Multicall3Client",
            return_value=MagicMock(
                contract=MagicMock(
                    address="multicall3",
                ),
            ),
        )

    return _mock


class TestAggregateMulticallRequests:
    def test_aggregates_single_request(self, mock_web3, mock_multicall3_client):
        """Test aggregating a single request."""
        with mock_multicall3_client():
            encoded_data = b"encoded_data_1"
            contract_call = MagicMock(return_value=HexStr("0x123"))
            request = TransformedRegistrationRequest(
                encoded_tx_data=encoded_data,
                is_use_multicall3=False,
                workflow_address=ADDRESS,
                validated_request=[],
                original_method_reference=contract_call,
            )
            result = aggregate_multicall_requests(
                requests=[request],
                is_use_multicall3=False,
                web3=mock_web3,
            )
            assert len(result) == 1
            assert ADDRESS in result
            aggregated_request_data = result[ADDRESS]
            assert aggregated_request_data["call_data"] == [encoded_data]
            assert aggregated_request_data["license_terms_data"] == [[]]
            assert aggregated_request_data["method_reference"] == contract_call

    def test_aggregates_multiple_requests_same_address(
        self, mock_web3, mock_multicall3_client
    ):
        """Test aggregating multiple requests to the same address."""
        with mock_multicall3_client():
            encoded_data_1 = b"encoded_data_1"
            encoded_data_2 = b"encoded_data_2"
            contract_call = MagicMock(return_value=HexStr("0x111"))

            request_1 = TransformedRegistrationRequest(
                encoded_tx_data=encoded_data_1,
                is_use_multicall3=False,
                workflow_address=ADDRESS,
                validated_request=[],
                original_method_reference=contract_call,
            )
            request_2 = TransformedRegistrationRequest(
                encoded_tx_data=encoded_data_2,
                is_use_multicall3=False,
                workflow_address=ADDRESS,
                validated_request=[],
                original_method_reference=contract_call,
                extra_data=ExtraData(
                    license_terms_data=[LICENSE_TERMS_DATA_CAMEL_CASE],
                ),
            )

            result = aggregate_multicall_requests(
                requests=[request_1, request_2],
                is_use_multicall3=False,
                web3=mock_web3,
            )

            assert len(result) == 1
            assert ADDRESS in result
            aggregated_request_data = result[ADDRESS]
            assert aggregated_request_data["call_data"] == [
                encoded_data_1,
                encoded_data_2,
            ]
            assert aggregated_request_data["license_terms_data"] == [
                [],
                [LICENSE_TERMS_DATA_CAMEL_CASE],
            ]
            assert aggregated_request_data["method_reference"] == contract_call

    def test_aggregates_multiple_requests_different_addresses(
        self, mock_web3, mock_multicall3_client
    ):
        """Test aggregating multiple requests to different addresses."""
        with mock_multicall3_client():
            workflow_address_1 = ADDRESS
            workflow_address_2 = "0xDifferentAddress"
            encoded_data_1 = b"encoded_data_1"
            encoded_data_2 = b"encoded_data_2"
            encoded_data_3 = b"encoded_data_3"
            contract_call_1 = MagicMock(return_value=HexStr("0x111"))
            contract_call_2 = MagicMock(return_value=HexStr("0x222"))
            royalty_shares = [RoyaltyShareInput(recipient=ADDRESS, percentage=50)]

            request_1 = TransformedRegistrationRequest(
                encoded_tx_data=encoded_data_1,
                is_use_multicall3=False,
                workflow_address=workflow_address_1,
                validated_request=[],
                original_method_reference=contract_call_1,
            )
            request_2 = TransformedRegistrationRequest(
                encoded_tx_data=encoded_data_2,
                is_use_multicall3=False,
                workflow_address=workflow_address_2,
                validated_request=[],
                original_method_reference=contract_call_2,
                extra_data=ExtraData(
                    license_terms_data=[LICENSE_TERMS_DATA_CAMEL_CASE],
                ),
            )
            request_3 = TransformedRegistrationRequest(
                encoded_tx_data=encoded_data_3,
                is_use_multicall3=False,
                workflow_address=workflow_address_2,
                validated_request=[],
                original_method_reference=contract_call_2,
                extra_data=ExtraData(
                    royalty_shares=royalty_shares,
                ),
            )

            result = aggregate_multicall_requests(
                requests=[request_1, request_2, request_3],
                is_use_multicall3=False,
                web3=mock_web3,
            )

            assert len(result) == 2
            assert workflow_address_1 in result
            assert workflow_address_2 in result

            aggregated_request_data = result[workflow_address_1]
            assert aggregated_request_data["call_data"] == [encoded_data_1]
            assert aggregated_request_data["license_terms_data"] == [[]]
            assert aggregated_request_data["method_reference"] == contract_call_1

            aggregated_request_data = result[workflow_address_2]
            assert aggregated_request_data["call_data"] == [
                encoded_data_2,
                encoded_data_3,
            ]
            assert aggregated_request_data["license_terms_data"] == [
                [LICENSE_TERMS_DATA_CAMEL_CASE],
                [],
            ]
            assert aggregated_request_data["method_reference"] == contract_call_2

    def test_uses_multicall3_address_when_enabled(
        self, mock_web3, mock_multicall3_client
    ):
        """Test using multicall3 address when is_use_multicall3 is True."""
        with mock_multicall3_client() as mock_patch:
            multicall3_instance = mock_patch.return_value
            encoded_data_1 = b"encoded_data1"
            encoded_data_2 = b"encoded_data2"
            contract_call1 = MagicMock(return_value=HexStr("0x111"))
            contract_call2 = MagicMock(return_value=HexStr("0x222"))

            request1 = TransformedRegistrationRequest(
                encoded_tx_data=encoded_data_1,
                is_use_multicall3=True,
                workflow_address="workflow1",
                validated_request=[],
                original_method_reference=contract_call1,
            )
            request2 = TransformedRegistrationRequest(
                encoded_tx_data=encoded_data_2,
                is_use_multicall3=True,
                workflow_address="workflow2",
                validated_request=[],
                original_method_reference=contract_call2,
                extra_data=ExtraData(
                    license_terms_data=[LICENSE_TERMS_DATA_CAMEL_CASE],
                ),
            )

            result = aggregate_multicall_requests(
                requests=[request1, request2],
                is_use_multicall3=True,
                web3=mock_web3,
            )

            assert len(result) == 1
            assert "multicall3" in result
            assert "workflow1" not in result
            assert "workflow2" not in result

            aggregated_request_data = result["multicall3"]
            # When using multicall3, call_data should be Multicall3Call structure
            expected_call_data = [
                {
                    "target": "workflow1",
                    "allowFailure": False,
                    "value": 0,
                    "callData": encoded_data_1,
                },
                {
                    "target": "workflow2",
                    "allowFailure": False,
                    "value": 0,
                    "callData": encoded_data_2,
                },
            ]
            assert aggregated_request_data["call_data"] == expected_call_data
            assert aggregated_request_data["license_terms_data"] == [
                [],
                [LICENSE_TERMS_DATA_CAMEL_CASE],
            ]
            # Method reference should be multicall3's method
            assert (
                aggregated_request_data["method_reference"]
                == multicall3_instance.build_aggregate3_transaction
            )

    def test_uses_workflow_address_when_multicall3_disabled(
        self, mock_web3, mock_multicall3_client
    ):
        """Test using workflow address when is_use_multicall3 is False."""
        with mock_multicall3_client() as mock_patch:
            multicall3_instance = mock_patch.return_value
            multicall3_address = multicall3_instance.contract.address

            encoded_data_1 = b"encoded_data1"
            encoded_data_2 = b"encoded_data2"
            contract_call1 = MagicMock(return_value=HexStr("0x111"))
            contract_call2 = MagicMock(return_value=HexStr("0x222"))

            request1 = TransformedRegistrationRequest(
                encoded_tx_data=encoded_data_1,
                is_use_multicall3=True,  # Request wants to use multicall3
                workflow_address="workflow1",
                validated_request=[],
                original_method_reference=contract_call1,
                extra_data=ExtraData(
                    license_terms_data=[LICENSE_TERMS_DATA_CAMEL_CASE],
                ),
            )
            request2 = TransformedRegistrationRequest(
                encoded_tx_data=encoded_data_2,
                is_use_multicall3=True,
                workflow_address="workflow2",
                validated_request=[],
                original_method_reference=contract_call2,
            )
            result = aggregate_multicall_requests(
                requests=[request1, request2],
                is_use_multicall3=False,
                web3=mock_web3,
            )

            assert len(result) == 2
            assert "workflow1" in result
            assert "workflow2" in result
            assert multicall3_address not in result

            aggregated_request_data = result["workflow1"]
            assert aggregated_request_data["call_data"] == [encoded_data_1]
            assert aggregated_request_data["license_terms_data"] == [
                [LICENSE_TERMS_DATA_CAMEL_CASE]
            ]
            assert aggregated_request_data["method_reference"] == contract_call1

            aggregated_request_data = result["workflow2"]
            assert aggregated_request_data["call_data"] == [encoded_data_2]
            assert aggregated_request_data["license_terms_data"] == [[]]
            assert aggregated_request_data["method_reference"] == contract_call2

    def test_aggregates_mixed_requests_with_multicall3(
        self, mock_web3, mock_multicall3_client
    ):
        """Test aggregating mixed requests where some use multicall3 and some don't."""
        with mock_multicall3_client() as mock_patch:
            multicall3_instance = mock_patch.return_value
            multicall3_address = multicall3_instance.contract.address

            workflow_address_1 = ADDRESS
            workflow_address_2 = "0xDifferentWorkflow"

            encoded_data_1 = b"encoded_data_1"
            encoded_data_2 = b"encoded_data_2"
            encoded_data_3 = b"encoded_data_3"
            contract_call_1 = MagicMock(return_value=HexStr("0x111"))
            contract_call_2 = MagicMock(return_value=HexStr("0x222"))
            contract_call_3 = MagicMock(return_value=HexStr("0x333"))

            # Request 1: uses multicall3
            request_1 = TransformedRegistrationRequest(
                encoded_tx_data=encoded_data_1,
                is_use_multicall3=True,
                workflow_address=workflow_address_1,
                validated_request=[],
                original_method_reference=contract_call_1,
                extra_data=ExtraData(
                    license_terms_data=[LICENSE_TERMS_DATA_CAMEL_CASE],
                ),
            )
            # Request 2: uses multicall3
            request_2 = TransformedRegistrationRequest(
                encoded_tx_data=encoded_data_2,
                is_use_multicall3=True,
                workflow_address=workflow_address_2,
                validated_request=[],
                original_method_reference=contract_call_2,
            )
            # Request 3: doesn't use multicall3
            request_3 = TransformedRegistrationRequest(
                encoded_tx_data=encoded_data_3,
                is_use_multicall3=False,
                workflow_address=workflow_address_1,
                validated_request=[],
                original_method_reference=contract_call_3,
            )

            result = aggregate_multicall_requests(
                requests=[request_1, request_2, request_3],
                is_use_multicall3=True,
                web3=mock_web3,
            )

            # Request 1 and 2 should be aggregated to multicall3_address
            # Request 3 should use its workflow_address
            assert len(result) == 2
            assert multicall3_address in result
            assert workflow_address_1 in result

            # Check multicall3 aggregation (request_1 and request_2)
            multicall_data = result[multicall3_address]["call_data"]
            assert len(multicall_data) == 2
            # Check that multicall structures are correct
            assert multicall_data == [
                {
                    "target": workflow_address_1,
                    "allowFailure": False,
                    "value": 0,
                    "callData": encoded_data_1,
                },
                {
                    "target": workflow_address_2,
                    "allowFailure": False,
                    "value": 0,
                    "callData": encoded_data_2,
                },
            ]
            assert result[multicall3_address]["license_terms_data"] == [
                [LICENSE_TERMS_DATA_CAMEL_CASE],
                [],
            ]
            assert (
                result[multicall3_address]["method_reference"]
                == multicall3_instance.build_aggregate3_transaction
            )

            # Check workflow address (request_3)
            aggregated_request_data = result[workflow_address_1]
            assert aggregated_request_data["call_data"] == [encoded_data_3]
            assert aggregated_request_data["license_terms_data"] == [[]]
            assert aggregated_request_data["method_reference"] == contract_call_3

    def test_aggregates_empty_requests_list(self, mock_web3, mock_multicall3_client):
        """Test aggregating an empty list of requests."""
        with mock_multicall3_client():
            result = aggregate_multicall_requests(
                requests=[],
                is_use_multicall3=False,
                web3=mock_web3,
            )

            assert len(result) == 0
            assert isinstance(result, dict)


@pytest.fixture
def mock_transform_distribute_royalty_tokens_request():
    """Mock dependencies needed by transform_distribute_royalty_tokens_request."""

    def _mock():
        return patch(
            "story_protocol_python_sdk.utils.registration.registration_utils.transform_distribute_royalty_tokens_request",
            return_value=TransformedRegistrationRequest(
                encoded_tx_data=b"mock_encoded_data",
                is_use_multicall3=False,
                workflow_address=ADDRESS,
                validated_request=[],
                original_method_reference=MagicMock(),
            ),
        )

    return _mock


class TestPrepareDistributeRoyaltyTokensRequests:
    def test_returns_empty_lists_when_extra_data_list_is_empty(
        self, mock_web3, mock_account
    ):
        """Test that empty lists are returned when extra_data_list is empty."""
        result = prepare_distribute_royalty_tokens_requests(
            extra_data_list=[],
            web3=mock_web3,
            ip_registered=[],
            royalty_vault=[],
            account=mock_account,
            chain_id=1,
        )

        transformed_requests, matching_vaults = result
        assert transformed_requests == []
        assert matching_vaults == []

    def test_filters_and_matches_ip_and_vault_data(
        self, mock_web3, mock_account, mock_transform_distribute_royalty_tokens_request
    ):
        """Test successful filtering and matching of IP and vault data."""
        with mock_transform_distribute_royalty_tokens_request():
            nft_contract = "0xNFTContract"
            token_id = 123
            ip_id = "ip_id"
            ip_registered = [
                {
                    "tokenContract": nft_contract,
                    "tokenId": token_id,
                    "ipId": ip_id,
                }
            ]
            ip_royalty_vault = "ip_royalty_vault"
            royalty_vault = [
                {
                    "ipId": ip_id,
                    "ipRoyaltyVault": ip_royalty_vault,
                }
            ]
            result = prepare_distribute_royalty_tokens_requests(
                extra_data_list=[
                    ExtraData(
                        nft_contract=nft_contract,
                        token_id=token_id,
                        deadline=1000,
                        royalty_total_amount=5000,
                        royalty_shares=[
                            RoyaltyShareInput(recipient="0xRecipient", percentage=50)
                        ],
                    )
                ],
                web3=mock_web3,
                ip_registered=ip_registered,
                royalty_vault=royalty_vault,
                account=mock_account,
                chain_id=1,
            )
            transformed_requests, matching_vaults = result
            assert len(transformed_requests) == 1
            assert len(matching_vaults) == 1
            assert matching_vaults == [
                IPRoyaltyVault(ip_id=ip_id, royalty_vault=ip_royalty_vault)
            ]

    def test_skips_when_no_matching_ip_registered(
        self, mock_web3, mock_account, mock_transform_distribute_royalty_tokens_request
    ):
        """Test that items are skipped when no matching IP is registered."""
        with mock_transform_distribute_royalty_tokens_request() as mock_transform:
            nft_contract = "0xNonExistentContract"
            token_id = 999
            ip_registered = [
                {
                    "tokenContract": "0xDifferentContract",
                    "tokenId": 123,
                    "ipId": "0xIPID",
                }
            ]
            royalty_vault = [
                {
                    "ipId": "0xIPID",
                    "ipRoyaltyVault": "0xRoyaltyVault",
                }
            ]
            result = prepare_distribute_royalty_tokens_requests(
                extra_data_list=[
                    ExtraData(
                        nft_contract=nft_contract,
                        token_id=token_id,
                        deadline=1000,
                        royalty_total_amount=5000,
                        royalty_shares=[
                            RoyaltyShareInput(recipient="0xRecipient", percentage=50)
                        ],
                    )
                ],
                web3=mock_web3,
                ip_registered=ip_registered,
                royalty_vault=royalty_vault,
                account=mock_account,
                chain_id=1,
            )
            transformed_requests, matching_vaults = result
            assert transformed_requests == []
            assert matching_vaults == []
            # Verify transform was not called since no IP matched
            mock_transform.assert_not_called()

    def test_skips_when_no_matching_vault(
        self, mock_web3, mock_account, mock_transform_distribute_royalty_tokens_request
    ):
        """Test that items are skipped when no matching vault is found."""
        with mock_transform_distribute_royalty_tokens_request() as mock_transform:
            nft_contract = "0xNFTContract"
            token_id = 123
            ip_id = "0xIPID"
            ip_registered = [
                {
                    "tokenContract": nft_contract,
                    "tokenId": token_id,
                    "ipId": ip_id,
                }
            ]
            # Vault for different IP ID
            royalty_vault = [
                {
                    "ipId": "0xDifferentIPID",
                    "ipRoyaltyVault": "0xRoyaltyVault",
                }
            ]
            result = prepare_distribute_royalty_tokens_requests(
                extra_data_list=[
                    ExtraData(
                        nft_contract=nft_contract,
                        token_id=token_id,
                        deadline=1000,
                        royalty_total_amount=5000,
                        royalty_shares=[
                            RoyaltyShareInput(recipient="0xRecipient", percentage=50)
                        ],
                    )
                ],
                web3=mock_web3,
                ip_registered=ip_registered,
                royalty_vault=royalty_vault,
                account=mock_account,
                chain_id=1,
            )
            transformed_requests, matching_vaults = result
            assert transformed_requests == []
            assert matching_vaults == []
            # Verify transform was not called since no vault matched
            mock_transform.assert_not_called()

    def test_processes_multiple_extra_data_items(
        self, mock_web3, mock_account, mock_transform_distribute_royalty_tokens_request
    ):
        """Test processing multiple extra_data items with mixed matching results."""
        with mock_transform_distribute_royalty_tokens_request() as mock_transform:
            # Test data - 3 items: 2 should match, 1 should not
            ip_registered = [
                {"tokenContract": "0xContract1", "tokenId": 1, "ipId": "0xIPID1"},
                {"tokenContract": "0xContract2", "tokenId": 2, "ipId": "0xIPID2"},
                {"tokenContract": "0xContract3", "tokenId": 3, "ipId": "0xIPID3"},
            ]
            # Only vaults for first two items
            royalty_vault = [
                {"ipId": "0xIPID1", "ipRoyaltyVault": "0xVault1"},
                {"ipId": "0xIPID2", "ipRoyaltyVault": "0xVault2"},
                # No vault for 0xIPID3
            ]
            result = prepare_distribute_royalty_tokens_requests(
                extra_data_list=[
                    # Item 1: Should match
                    ExtraData(
                        nft_contract="0xContract1",
                        token_id=1,
                        deadline=1000,
                        royalty_total_amount=5000,
                        royalty_shares=[
                            RoyaltyShareInput(recipient="0xRecipient1", percentage=30)
                        ],
                    ),
                    # Item 2: Should match
                    ExtraData(
                        nft_contract="0xContract2",
                        token_id=2,
                        deadline=2000,
                        royalty_total_amount=6000,
                        royalty_shares=[
                            RoyaltyShareInput(recipient="0xRecipient2", percentage=40)
                        ],
                    ),
                    # Item 3: Should not match (no vault)
                    ExtraData(
                        nft_contract="0xContract3",
                        token_id=3,
                        deadline=3000,
                        royalty_total_amount=7000,
                        royalty_shares=[
                            RoyaltyShareInput(recipient="0xRecipient3", percentage=50)
                        ],
                    ),
                ],
                web3=mock_web3,
                ip_registered=ip_registered,
                royalty_vault=royalty_vault,
                account=mock_account,
                chain_id=1,
            )
            transformed_requests, matching_vaults = result
            # Should have 2 results (first two items matched)
            assert len(transformed_requests) == 2
            assert len(matching_vaults) == 2
            assert matching_vaults == [
                IPRoyaltyVault(ip_id="0xIPID1", royalty_vault="0xVault1"),
                IPRoyaltyVault(ip_id="0xIPID2", royalty_vault="0xVault2"),
            ]
            # Verify transform was called twice (once for each matched item)
            assert mock_transform.call_count == 2
