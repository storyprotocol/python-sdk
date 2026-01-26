from dataclasses import asdict, replace
from unittest.mock import MagicMock, patch

import pytest
from ens.ens import HexStr

from story_protocol_python_sdk.types.resource.IPAsset import (
    TransformedRegistrationRequest,
)
from story_protocol_python_sdk.utils.registration.registration_utils import (
    aggregate_multicall_requests,
    get_public_minting,
    validate_license_terms_data,
)
from tests.unit.fixtures.data import (
    ADDRESS,
    LICENSE_TERMS_DATA,
    LICENSE_TERMS_DATA_CAMEL_CASE,
)


@pytest.fixture
def mock_module_registry_client():
    """Mock ModuleRegistryClient."""
    return patch(
        "story_protocol_python_sdk.utils.registration.registration_utils.ModuleRegistryClient",
        return_value=MagicMock(),
    )


class TestGetPublicMinting:
    def test_returns_true_when_public_minting_enabled(
        self, mock_web3, mock_spg_nft_client
    ):
        with mock_spg_nft_client(public_minting=True):
            result = get_public_minting(ADDRESS, mock_web3)
            assert result is True

    def test_returns_false_when_public_minting_disabled(
        self, mock_web3, mock_spg_nft_client
    ):
        with mock_spg_nft_client(public_minting=False):
            result = get_public_minting(ADDRESS, mock_web3)
            assert result is False

    def test_throws_error_when_spg_nft_contract_invalid(self, mock_web3):
        with pytest.raises(Exception):
            get_public_minting("invalid_address", mock_web3)


class TestValidateLicenseTermsData:
    def test_validates_license_terms_with_dataclass_input(
        self,
        mock_web3,
        mock_royalty_module_client,
        mock_module_registry_client,
    ):
        with (
            mock_royalty_module_client(),
            mock_module_registry_client,
        ):
            result = validate_license_terms_data(LICENSE_TERMS_DATA, mock_web3)
            assert isinstance(result, list)
            assert len(result) == len(LICENSE_TERMS_DATA)
            assert result[0] == LICENSE_TERMS_DATA_CAMEL_CASE

    def test_validates_license_terms_with_dict_input(
        self,
        mock_web3,
        mock_royalty_module_client,
        mock_module_registry_client,
    ):
        with (
            mock_royalty_module_client(),
            mock_module_registry_client,
        ):
            result = validate_license_terms_data(
                [
                    {
                        "terms": asdict(LICENSE_TERMS_DATA[0].terms),
                        "licensing_config": LICENSE_TERMS_DATA[0].licensing_config,
                    }
                ],
                mock_web3,
            )
            assert result[0] == LICENSE_TERMS_DATA_CAMEL_CASE

    def test_throws_error_when_royalty_policy_not_whitelisted(
        self,
        mock_web3,
        mock_royalty_module_client,
        mock_module_registry_client,
    ):
        with (
            mock_royalty_module_client(is_whitelisted_policy=False),
            mock_module_registry_client,
            pytest.raises(ValueError, match="The royalty_policy is not whitelisted."),
        ):
            validate_license_terms_data(LICENSE_TERMS_DATA, mock_web3)

    def test_throws_error_when_currency_not_whitelisted(
        self,
        mock_web3,
        mock_royalty_module_client,
        mock_module_registry_client,
    ):
        with (
            mock_royalty_module_client(is_whitelisted_token=False),
            mock_module_registry_client,
            pytest.raises(ValueError, match="The currency is not whitelisted."),
        ):
            validate_license_terms_data(LICENSE_TERMS_DATA, mock_web3)

    def test_validates_multiple_license_terms(
        self,
        mock_web3,
        mock_royalty_module_client,
        mock_module_registry_client,
    ):
        # Use LICENSE_TERMS_DATA twice to test multiple terms
        license_terms_data = LICENSE_TERMS_DATA + [
            replace(
                LICENSE_TERMS_DATA[0],
                terms=replace(LICENSE_TERMS_DATA[0].terms, commercial_rev_share=20),
            )
        ]

        with (
            mock_royalty_module_client(),
            mock_module_registry_client,
        ):
            result = validate_license_terms_data(license_terms_data, mock_web3)
            assert result[0] == LICENSE_TERMS_DATA_CAMEL_CASE
            assert result[1] == {
                "terms": {
                    **LICENSE_TERMS_DATA_CAMEL_CASE["terms"],
                    "commercialRevShare": 20 * 10**6,
                },
                "licensingConfig": LICENSE_TERMS_DATA_CAMEL_CASE["licensingConfig"],
            }


class TestAggregateMulticallRequests:
    def test_aggregates_single_request(self):
        """Test aggregating a single request."""
        multicall3_address = "multicall3"
        encoded_data = b"encoded_data_1"
        contract_call = MagicMock(return_value=HexStr("0x123"))

        request = TransformedRegistrationRequest(
            encoded_tx_data=encoded_data,
            is_use_multicall3=False,
            workflow_address=ADDRESS,
            validated_request=[],
            contract_call=contract_call,
        )

        result = aggregate_multicall_requests(
            requests=[request],
            is_use_multicall3=False,
            multicall_address=multicall3_address,
        )

        assert len(result) == 1
        assert ADDRESS in result
        assert result[ADDRESS]["encoded_tx_data"] == [encoded_data]
        assert result[ADDRESS]["contract_calls"] == [contract_call]

    def test_aggregates_multiple_requests_same_address(self):
        """Test aggregating multiple requests to the same address."""
        encoded_data_1 = b"encoded_data_1"
        encoded_data_2 = b"encoded_data_2"
        contract_call_1 = MagicMock(return_value=HexStr("0x111"))
        contract_call_2 = MagicMock(return_value=HexStr("0x222"))

        request_1 = TransformedRegistrationRequest(
            encoded_tx_data=encoded_data_1,
            is_use_multicall3=False,
            workflow_address=ADDRESS,
            validated_request=[],
            contract_call=contract_call_1,
        )
        request_2 = TransformedRegistrationRequest(
            encoded_tx_data=encoded_data_2,
            is_use_multicall3=False,
            workflow_address=ADDRESS,
            validated_request=[],
            contract_call=contract_call_2,
        )

        multicall3_address = "multicall3"
        result = aggregate_multicall_requests(
            requests=[request_1, request_2],
            is_use_multicall3=False,
            multicall_address=multicall3_address,
        )

        assert len(result) == 1
        assert ADDRESS in result
        assert result[ADDRESS]["encoded_tx_data"] == [encoded_data_1, encoded_data_2]
        assert result[ADDRESS]["contract_calls"] == [contract_call_1, contract_call_2]

    def test_aggregates_multiple_requests_different_addresses(self):
        """Test aggregating multiple requests to different addresses."""
        workflow_address_1 = ADDRESS
        workflow_address_2 = "0x"
        encoded_data_1 = b"encoded_data_1"
        encoded_data_2 = b"encoded_data_2"
        contract_call_1 = MagicMock(return_value=HexStr("0x111"))
        contract_call_2 = MagicMock(return_value=HexStr("0x222"))

        request_1 = TransformedRegistrationRequest(
            encoded_tx_data=encoded_data_1,
            is_use_multicall3=False,
            workflow_address=workflow_address_1,
            validated_request=[],
            contract_call=contract_call_1,
        )
        request_2 = TransformedRegistrationRequest(
            encoded_tx_data=encoded_data_2,
            is_use_multicall3=False,
            workflow_address=workflow_address_2,
            validated_request=[],
            contract_call=contract_call_2,
        )

        result = aggregate_multicall_requests(
            requests=[request_1, request_2],
            is_use_multicall3=False,
            multicall_address="0xmulticall",
        )

        assert len(result) == 2
        assert workflow_address_1 in result
        assert workflow_address_2 in result
        assert result[workflow_address_1]["encoded_tx_data"] == [encoded_data_1]
        assert result[workflow_address_1]["contract_calls"] == [contract_call_1]
        assert result[workflow_address_2]["encoded_tx_data"] == [encoded_data_2]
        assert result[workflow_address_2]["contract_calls"] == [contract_call_2]

    def test_uses_multicall3_address_when_enabled(self):
        """Test using multicall3 address when is_use_multicall3 is True."""
        multicall3_address = "multicall3"
        encoded_data = b"encoded_data"
        contract_call = MagicMock(return_value=HexStr("0x123"))

        request = TransformedRegistrationRequest(
            encoded_tx_data=encoded_data,
            is_use_multicall3=True,
            workflow_address=ADDRESS,
            validated_request=[],
            contract_call=contract_call,
        )

        result = aggregate_multicall_requests(
            requests=[request],
            is_use_multicall3=True,
            multicall_address=multicall3_address,
        )

        assert len(result) == 1
        assert multicall3_address in result
        assert ADDRESS not in result
        assert result[multicall3_address]["encoded_tx_data"] == [encoded_data]
        assert result[multicall3_address]["contract_calls"] == [contract_call]

    def test_uses_workflow_address_when_multicall3_disabled(self):
        """Test using workflow address when is_use_multicall3 is False."""
        multicall3_address = "multicall3"
        encoded_data = b"encoded_data"
        contract_call = MagicMock(return_value=HexStr("0x123"))

        request = TransformedRegistrationRequest(
            encoded_tx_data=encoded_data,
            is_use_multicall3=True,
            workflow_address=ADDRESS,
            validated_request=[],
            contract_call=contract_call,
        )

        result = aggregate_multicall_requests(
            requests=[request],
            is_use_multicall3=False,
            multicall_address=multicall3_address,
        )

        assert len(result) == 1
        assert ADDRESS in result
        assert multicall3_address not in result
        assert result[ADDRESS]["encoded_tx_data"] == [encoded_data]
        assert result[ADDRESS]["contract_calls"] == [contract_call]

    def test_aggregates_mixed_requests_with_multicall3(self):
        """Test aggregating mixed requests where some use multicall3 and some don't."""
        multicall3_address = "multicall3"
        workflow_address_1 = ADDRESS
        workflow_address_2 = "0x"

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
            contract_call=contract_call_1,
        )
        # Request 2: uses multicall3
        request_2 = TransformedRegistrationRequest(
            encoded_tx_data=encoded_data_2,
            is_use_multicall3=True,
            workflow_address=workflow_address_2,
            validated_request=[],
            contract_call=contract_call_2,
        )
        # Request 3: doesn't use multicall3
        request_3 = TransformedRegistrationRequest(
            encoded_tx_data=encoded_data_3,
            is_use_multicall3=False,
            workflow_address=workflow_address_1,
            validated_request=[],
            contract_call=contract_call_3,
        )

        result = aggregate_multicall_requests(
            requests=[request_1, request_2, request_3],
            is_use_multicall3=True,
            multicall_address=multicall3_address,
        )

        # Request 1 and 2 should be aggregated to multicall3_address
        # Request 3 should use its workflow_address
        assert len(result) == 2
        assert multicall3_address in result
        assert workflow_address_1 in result

        # Check multicall3 aggregation (request_1 and request_2)
        assert len(result[multicall3_address]["encoded_tx_data"]) == 2
        assert encoded_data_1 in result[multicall3_address]["encoded_tx_data"]
        assert encoded_data_2 in result[multicall3_address]["encoded_tx_data"]
        assert contract_call_1 in result[multicall3_address]["contract_calls"]
        assert contract_call_2 in result[multicall3_address]["contract_calls"]

        # Check workflow address (request_3)
        assert result[workflow_address_1]["encoded_tx_data"] == [encoded_data_3]
        assert result[workflow_address_1]["contract_calls"] == [contract_call_3]

    def test_aggregates_empty_requests_list(self):
        """Test aggregating an empty list of requests."""
        multicall3_address = "multicall3"
        result = aggregate_multicall_requests(
            requests=[],
            is_use_multicall3=False,
            multicall_address=multicall3_address,
        )

        assert len(result) == 0
        assert isinstance(result, dict)

    def test_aggregates_multiple_requests_to_multicall3(self):
        """Test aggregating multiple requests that all use multicall3."""
        multicall3_address = "0xmulticall3"
        workflow_address_1 = "0x1"
        workflow_address_2 = "0x2"
        workflow_address_3 = "0x33333333"
        encoded_data_1 = b"encoded_data_1"
        encoded_data_2 = b"encoded_data_2"
        encoded_data_3 = b"encoded_data_3"
        contract_call_1 = MagicMock(return_value=HexStr("0x111"))
        contract_call_2 = MagicMock(return_value=HexStr("0x222"))
        contract_call_3 = MagicMock(return_value=HexStr("0x333"))

        request_1 = TransformedRegistrationRequest(
            encoded_tx_data=encoded_data_1,
            is_use_multicall3=True,
            workflow_address=workflow_address_1,
            validated_request=[],
            contract_call=contract_call_1,
        )
        request_2 = TransformedRegistrationRequest(
            encoded_tx_data=encoded_data_2,
            is_use_multicall3=True,
            workflow_address=workflow_address_2,
            validated_request=[],
            contract_call=contract_call_2,
        )
        request_3 = TransformedRegistrationRequest(
            encoded_tx_data=encoded_data_3,
            is_use_multicall3=True,
            workflow_address=workflow_address_3,
            validated_request=[],
            contract_call=contract_call_3,
        )

        result = aggregate_multicall_requests(
            requests=[request_1, request_2, request_3],
            is_use_multicall3=True,
            multicall_address=multicall3_address,
        )

        assert len(result) == 1
        assert multicall3_address in result
        assert len(result[multicall3_address]["encoded_tx_data"]) == 3
        assert len(result[multicall3_address]["contract_calls"]) == 3
        assert encoded_data_1 in result[multicall3_address]["encoded_tx_data"]
        assert encoded_data_2 in result[multicall3_address]["encoded_tx_data"]
        assert encoded_data_3 in result[multicall3_address]["encoded_tx_data"]
        assert contract_call_1 in result[multicall3_address]["contract_calls"]
        assert contract_call_2 in result[multicall3_address]["contract_calls"]
        assert contract_call_3 in result[multicall3_address]["contract_calls"]
