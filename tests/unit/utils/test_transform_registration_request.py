from dataclasses import asdict, replace
from unittest.mock import MagicMock, patch

import pytest
from typing_extensions import cast
from web3 import Account

from story_protocol_python_sdk import (
    DerivativeDataInput,
    MintAndRegisterRequest,
    RegisterRegistrationRequest,
    RoyaltyShareInput,
)
from story_protocol_python_sdk.abi.DerivativeWorkflows.DerivativeWorkflows_client import (
    DerivativeWorkflowsClient,
)
from story_protocol_python_sdk.abi.LicenseAttachmentWorkflows.LicenseAttachmentWorkflows_client import (
    LicenseAttachmentWorkflowsClient,
)
from story_protocol_python_sdk.abi.RoyaltyTokenDistributionWorkflows.RoyaltyTokenDistributionWorkflows_client import (
    RoyaltyTokenDistributionWorkflowsClient,
)
from story_protocol_python_sdk.utils.ip_metadata import IPMetadata
from story_protocol_python_sdk.utils.registration.transform_registration_request import (
    get_allow_duplicates,
    get_public_minting,
    transform_distribute_royalty_tokens_request,
    transform_request,
    validate_license_terms_data,
)
from tests.unit.fixtures.data import (
    ADDRESS,
    CHAIN_ID,
    IP_ID,
    IP_METADATA,
    LICENSE_TERMS_DATA,
    LICENSE_TERMS_DATA_CAMEL_CASE,
)


@pytest.fixture
def mock_get_public_minting():
    """Mock get_public_minting function."""

    def _mock(public_minting: bool = True):
        return patch(
            "story_protocol_python_sdk.utils.registration.transform_registration_request.SPGNFTImplClient",
            return_value=MagicMock(
                publicMinting=MagicMock(return_value=public_minting)
            ),
        )

    return _mock


@pytest.fixture
def mock_royalty_module_client():
    """Mock RoyaltyModuleClient for validate_license_terms_data."""

    def _mock(is_whitelisted_policy: bool = True, is_whitelisted_token: bool = True):
        return patch(
            "story_protocol_python_sdk.utils.registration.transform_registration_request.RoyaltyModuleClient",
            return_value=MagicMock(
                isWhitelistedRoyaltyPolicy=MagicMock(
                    return_value=is_whitelisted_policy
                ),
                isWhitelistedRoyaltyToken=MagicMock(return_value=is_whitelisted_token),
            ),
        )

    return _mock


@pytest.fixture
def mock_module_registry_client():
    """Mock ModuleRegistryClient for validate_license_terms_data."""
    return patch(
        "story_protocol_python_sdk.utils.registration.transform_registration_request.ModuleRegistryClient",
        return_value=MagicMock(),
    )


@pytest.fixture
def mock_pi_license_template_client():
    """Mock PILicenseTemplateClient for DerivativeData."""

    def _mock():
        mock_instance = MagicMock()
        mock_instance.contract = MagicMock()
        mock_instance.contract.address = ADDRESS
        return patch(
            "story_protocol_python_sdk.utils.derivative_data.PILicenseTemplateClient",
            return_value=mock_instance,
        )

    return _mock


@pytest.fixture
def mock_derivative_ip_asset_registry_client():
    """Mock IPAssetRegistryClient for DerivativeData."""

    def _mock(is_registered: bool = True):
        return patch(
            "story_protocol_python_sdk.utils.derivative_data.IPAssetRegistryClient",
            return_value=MagicMock(isRegistered=MagicMock(return_value=is_registered)),
        )

    return _mock


@pytest.fixture
def mock_license_registry_client():
    """Mock LicenseRegistryClient for DerivativeData."""

    def _mock(has_attached_license_terms: bool = True, royalty_percent: int = 1000000):
        return patch(
            "story_protocol_python_sdk.utils.derivative_data.LicenseRegistryClient",
            return_value=MagicMock(
                hasIpAttachedLicenseTerms=MagicMock(
                    return_value=has_attached_license_terms
                ),
                getRoyaltyPercent=MagicMock(return_value=royalty_percent),
            ),
        )

    return _mock


@pytest.fixture
def mock_workflow_clients(mock_web3):
    """Mock workflow clients (RoyaltyTokenDistributionWorkflowsClient, LicenseAttachmentWorkflowsClient, DerivativeWorkflowsClient).

    Returns real client instances so encode_abi can produce real encoding results.
    """

    def _mock():

        # Create real client instances with mock_web3
        royalty_token_distribution_client = RoyaltyTokenDistributionWorkflowsClient(
            mock_web3
        )
        license_attachment_client = LicenseAttachmentWorkflowsClient(mock_web3)
        derivative_workflows_client = DerivativeWorkflowsClient(mock_web3)
        royalty_token_distribution_client.contract.address = (
            "royalty_token_distribution_client_address"
        )
        license_attachment_client.contract.address = "license_attachment_client_address"
        derivative_workflows_client.contract.address = (
            "derivative_workflows_client_address"
        )
        return {
            "royalty_token_distribution_patch": patch(
                "story_protocol_python_sdk.utils.registration.transform_registration_request.RoyaltyTokenDistributionWorkflowsClient",
                return_value=royalty_token_distribution_client,
            ),
            "license_attachment_patch": patch(
                "story_protocol_python_sdk.utils.registration.transform_registration_request.LicenseAttachmentWorkflowsClient",
                return_value=license_attachment_client,
            ),
            "derivative_workflows_patch": patch(
                "story_protocol_python_sdk.utils.registration.transform_registration_request.DerivativeWorkflowsClient",
                return_value=derivative_workflows_client,
            ),
            "royalty_token_distribution_client": royalty_token_distribution_client,
            "license_attachment_client": license_attachment_client,
            "derivative_workflows_client": derivative_workflows_client,
            "get_function_signature": patch(
                "story_protocol_python_sdk.utils.registration.transform_registration_request.get_function_signature",
                return_value="",
            ),
            "royalty_token_distribution_workflows_client": patch(
                "story_protocol_python_sdk.utils.registration.transform_registration_request.RoyaltyTokenDistributionWorkflowsClient",
                return_value=royalty_token_distribution_client,
            ),
        }

    return _mock


@pytest.fixture
def mock_ip_asset_registry_client():
    """Mock IPAssetRegistryClient."""

    def _mock(is_registered: bool = False, ip_id: str = IP_ID):
        mock_client = MagicMock()
        mock_client.ipId = MagicMock(return_value=ip_id)
        mock_client.isRegistered = MagicMock(return_value=is_registered)
        return patch(
            "story_protocol_python_sdk.utils.registration.transform_registration_request.IPAssetRegistryClient",
            return_value=mock_client,
        )

    return _mock


@pytest.fixture
def mock_sign_util():
    """Mock Sign utility."""

    def _mock(deadline: int = 1000, signature: bytes = b"signature"):
        mock_sign = MagicMock()
        mock_sign.get_deadline = MagicMock(return_value=deadline)
        mock_sign.get_permission_signature = MagicMock(
            return_value={"signature": signature}
        )
        mock_sign.get_signature = MagicMock(return_value={"signature": signature})
        return patch(
            "story_protocol_python_sdk.utils.registration.transform_registration_request.Sign",
            return_value=mock_sign,
        )

    return _mock


@pytest.fixture
def mock_module_clients():
    """Mock CoreMetadataModuleClient and LicensingModuleClient."""

    def _mock():
        mock_core_metadata_contract = MagicMock()
        mock_core_metadata_contract.address = ADDRESS
        mock_core_metadata_client = MagicMock()
        mock_core_metadata_client.contract = mock_core_metadata_contract

        mock_licensing_contract = MagicMock()
        mock_licensing_contract.address = ADDRESS
        mock_licensing_client = MagicMock()
        mock_licensing_client.contract = mock_licensing_contract

        return {
            "core_metadata_module_patch": patch(
                "story_protocol_python_sdk.utils.registration.transform_registration_request.CoreMetadataModuleClient",
                return_value=mock_core_metadata_client,
            ),
            "licensing_module_patch": patch(
                "story_protocol_python_sdk.utils.registration.transform_registration_request.LicensingModuleClient",
                return_value=mock_licensing_client,
            ),
        }

    return _mock


@pytest.fixture
def mock_spg_nft_client():
    """Mock SPGNFTImplClient."""

    def _mock(public_minting: bool = True):
        return patch(
            "story_protocol_python_sdk.utils.registration.transform_registration_request.SPGNFTImplClient",
            return_value=MagicMock(
                publicMinting=MagicMock(return_value=public_minting)
            ),
        )

    return _mock


account = Account.from_key(
    "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
)
ACCOUNT_ADDRESS = account.address


class TestGetAllowDuplicates:
    def test_returns_default_for_mint_and_register_ip_and_attach_pil_terms_and_distribute_royalty_tokens(
        self,
    ):
        result = get_allow_duplicates(
            None, "mintAndRegisterIpAndAttachPILTermsAndDistributeRoyaltyTokens"
        )
        assert result is True

    def test_returns_default_for_mint_and_register_ip_and_make_derivative_and_distribute_royalty_tokens(
        self,
    ):
        result = get_allow_duplicates(
            None, "mintAndRegisterIpAndMakeDerivativeAndDistributeRoyaltyTokens"
        )
        assert result is True

    def test_returns_default_for_mint_and_register_ip_and_attach_pil_terms(self):
        result = get_allow_duplicates(None, "mintAndRegisterIpAndAttachPILTerms")
        assert result is False

    def test_returns_default_for_mint_and_register_ip_and_make_derivative(self):
        result = get_allow_duplicates(None, "mintAndRegisterIpAndMakeDerivative")
        assert result is True

    def test_returns_provided_value_when_not_none(self):
        result = get_allow_duplicates(False, "mintAndRegisterIpAndAttachPILTerms")
        assert result is False

        result = get_allow_duplicates(True, "mintAndRegisterIpAndAttachPILTerms")
        assert result is True


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


class TestTransformRegistrationRequest:
    def test_routes_to_mint_and_register_attach_pil_terms_when_spg_nft_contract_present(
        self,
        mock_web3,
        mock_get_public_minting,
        mock_royalty_module_client,
        mock_module_registry_client,
        mock_workflow_clients,
    ):
        request = MintAndRegisterRequest(
            spg_nft_contract=ADDRESS,
            ip_metadata=IP_METADATA,
            license_terms_data=LICENSE_TERMS_DATA,
        )
        workflow_mocks = mock_workflow_clients()
        license_attachment_client = workflow_mocks["license_attachment_client"]
        with (
            mock_get_public_minting(),
            mock_royalty_module_client(),
            mock_module_registry_client,
            workflow_mocks["royalty_token_distribution_patch"],
            workflow_mocks["license_attachment_patch"],
            workflow_mocks["derivative_workflows_patch"],
        ):
            result = transform_request(request, mock_web3, account, CHAIN_ID)
            # Assert real encoding result (not mock value)
            license_attachment_client.contract.encode_abi.assert_called_once()
            call_args = license_attachment_client.contract.encode_abi.call_args
            assert call_args[1]["abi_element_identifier"] == (
                "mintAndRegisterIpAndAttachPILTerms"
            )
            # Verify args
            args = call_args[1]["args"]
            assert args[0] == ADDRESS  # spg_nft_contract
            assert args[1] == ACCOUNT_ADDRESS  # recipient
            assert (
                args[2] == IPMetadata.from_input(IP_METADATA).get_validated_data()
            )  # metadata
            assert args[3][0] == LICENSE_TERMS_DATA_CAMEL_CASE  # license_terms_data
            assert args[4] is False  # allow_duplicates (default for this method)
            assert result.workflow_address == "license_attachment_client_address"
            assert result.is_use_multicall3 is True
            assert result.extra_data is not None
            license_terms_data = result.extra_data.get("license_terms_data")
            assert license_terms_data is not None
            assert license_terms_data[0] == LICENSE_TERMS_DATA_CAMEL_CASE
            assert result.workflow_multicall_reference is not None

    def test_routes_to_register_ip_and_attach_pil_terms_when_nft_contract_and_token_id_present(
        self,
        mock_web3,
        mock_ip_asset_registry_client,
        mock_sign_util,
        mock_module_clients,
        mock_royalty_module_client,
        mock_module_registry_client,
        mock_workflow_clients,
    ):
        request = RegisterRegistrationRequest(
            nft_contract=ADDRESS,
            token_id=1,
            license_terms_data=LICENSE_TERMS_DATA,
        )
        workflow_mocks = mock_workflow_clients()
        module_patches = mock_module_clients()
        license_attachment_client = workflow_mocks["license_attachment_client"]
        with (
            mock_ip_asset_registry_client(),
            mock_sign_util(),
            mock_royalty_module_client(),
            mock_module_registry_client,
            workflow_mocks["royalty_token_distribution_patch"],
            workflow_mocks["license_attachment_patch"],
            workflow_mocks["derivative_workflows_patch"],
            workflow_mocks["get_function_signature"],
            module_patches["core_metadata_module_patch"],
            module_patches["licensing_module_patch"],
        ):
            result = transform_request(request, mock_web3, account, CHAIN_ID)
            # Assert real encoding result (not mock value)
            license_attachment_client.contract.encode_abi.assert_called_once()
            assert result.workflow_address == "license_attachment_client_address"
            assert result.is_use_multicall3 is False
            call_args = license_attachment_client.contract.encode_abi.call_args
            assert call_args[1]["abi_element_identifier"] == (
                "registerIpAndAttachPILTerms"
            )
            # Verify args
            args = call_args[1]["args"]
            assert args[0] == ADDRESS  # nft_contract
            assert args[1] == 1  # token_id
            assert args[2] == IPMetadata.from_input().get_validated_data()  # metadata
            assert args[3][0] == LICENSE_TERMS_DATA_CAMEL_CASE  # license_terms_data
            assert args[4]["signer"] == ACCOUNT_ADDRESS  # signature data
            assert args[4]["deadline"] == 1000
            assert args[4]["signature"] == b"signature"
            assert result.extra_data is not None
            license_terms_data = result.extra_data.get("license_terms_data")
            assert license_terms_data is not None
            assert license_terms_data[0] == LICENSE_TERMS_DATA_CAMEL_CASE
            assert result.is_use_multicall3 is False
            assert result.workflow_multicall_reference is not None

    def test_raises_error_for_invalid_request_type(
        self, mock_web3, mock_ip_asset_registry_client
    ):
        with mock_ip_asset_registry_client():
            with pytest.raises(ValueError, match="Invalid register request type"):
                transform_request(
                    RegisterRegistrationRequest(
                        nft_contract=ADDRESS,
                        token_id=1,
                    ),
                    mock_web3,
                    account,
                    CHAIN_ID,
                )

    def test_raises_error_for_invalid_registration_request_type(self, mock_web3):
        """Test that ValueError is raised when request doesn't match any known type."""
        with pytest.raises(ValueError, match="Invalid registration request type"):
            transform_request(
                None,  # type: ignore[arg-type]
                mock_web3,
                account,
                CHAIN_ID,
            )


class TestHandleMintAndRegisterRequest:
    def test_mint_and_register_ip_and_attach_pil_terms_and_distribute_royalty_tokens(
        self,
        mock_web3,
        mock_get_public_minting,
        mock_royalty_module_client,
        mock_module_registry_client,
        mock_workflow_clients,
    ):
        request = MintAndRegisterRequest(
            spg_nft_contract=ADDRESS,
            recipient=ADDRESS,
            ip_metadata=IP_METADATA,
            license_terms_data=LICENSE_TERMS_DATA,
            royalty_shares=[RoyaltyShareInput(recipient=ADDRESS, percentage=50.0)],
        )
        workflow_mocks = mock_workflow_clients()
        royalty_token_distribution_client = workflow_mocks[
            "royalty_token_distribution_client"
        ]
        with (
            mock_get_public_minting(public_minting=True),
            mock_royalty_module_client(),
            mock_module_registry_client,
            workflow_mocks["royalty_token_distribution_patch"],
            workflow_mocks["license_attachment_patch"],
            workflow_mocks["derivative_workflows_patch"],
        ):
            result = transform_request(request, mock_web3, account, CHAIN_ID)

            royalty_token_distribution_client.contract.encode_abi.assert_called_once()
            call_args = royalty_token_distribution_client.contract.encode_abi.call_args
            assert result.is_use_multicall3 is False
            assert (
                result.workflow_address == "royalty_token_distribution_client_address"
            )
            assert result.extra_data is not None
            license_terms_data = result.extra_data.get("license_terms_data")
            assert license_terms_data is not None
            assert license_terms_data[0] == LICENSE_TERMS_DATA_CAMEL_CASE
            # Verify encode_abi was called with correct method and arguments
            assert call_args[1]["abi_element_identifier"] == (
                "mintAndRegisterIpAndAttachPILTermsAndDistributeRoyaltyTokens"
            )
            # Verify args
            args = call_args[1]["args"]
            assert args[0] == ADDRESS  # spg_nft_contract
            assert args[1] == ADDRESS  # recipient
            assert (
                args[2] == IPMetadata.from_input(IP_METADATA).get_validated_data()
            )  # metadata
            # license_terms_data is validated, so we check it's not None
            assert args[3][0] == LICENSE_TERMS_DATA_CAMEL_CASE  # license_terms_data
            # royalty_shares is processed, so we check it's a list with correct structure
            assert args[4][0]["recipient"] == ADDRESS
            assert args[4][0]["percentage"] == 50 * 10**6
            assert args[5] is True  # allow_duplicates (default for this method)
            assert result.workflow_multicall_reference is not None

    def test_mint_and_register_ip_and_make_derivative_and_distribute_royalty_tokens(
        self,
        mock_web3,
        mock_get_public_minting,
        mock_pi_license_template_client,
        mock_derivative_ip_asset_registry_client,
        mock_license_registry_client,
        mock_workflow_clients,
    ):
        request = MintAndRegisterRequest(
            spg_nft_contract=ADDRESS,
            ip_metadata=IP_METADATA,
            deriv_data=DerivativeDataInput(
                parent_ip_ids=[IP_ID], license_terms_ids=[1]
            ),
            royalty_shares=[RoyaltyShareInput(recipient=ADDRESS, percentage=50.0)],
        )
        workflow_mocks = mock_workflow_clients()
        royalty_token_distribution_client = workflow_mocks[
            "royalty_token_distribution_client"
        ]
        with (
            mock_get_public_minting(public_minting=False),
            mock_pi_license_template_client(),
            mock_derivative_ip_asset_registry_client(),
            mock_license_registry_client(),
            workflow_mocks["royalty_token_distribution_patch"],
            workflow_mocks["license_attachment_patch"],
            workflow_mocks["derivative_workflows_patch"],
        ):
            result = transform_request(request, mock_web3, account, CHAIN_ID)

            royalty_token_distribution_client.contract.encode_abi.assert_called_once()
            call_args = royalty_token_distribution_client.contract.encode_abi.call_args
            assert result.is_use_multicall3 is False
            assert (
                result.workflow_address == "royalty_token_distribution_client_address"
            )
            assert result.extra_data is None
            # Verify encode_abi was called with correct method and arguments
            assert call_args[1]["abi_element_identifier"] == (
                "mintAndRegisterIpAndMakeDerivativeAndDistributeRoyaltyTokens"
            )
            # Verify args
            args = call_args[1]["args"]
            assert args[0] == ADDRESS  # spg_nft_contract
            assert args[1] == ACCOUNT_ADDRESS  # recipient
            assert (
                args[2] == IPMetadata.from_input(IP_METADATA).get_validated_data()
            )  # metadata
            assert args[4][0]["recipient"] == ADDRESS  # royalty_shares
            assert args[4][0]["percentage"] == 50 * 10**6  # royalty_shares
            assert args[5] is True  # allow_duplicates (default for this method)
            assert result.workflow_multicall_reference is not None

    def test_mint_and_register_ip_and_make_derivative(
        self,
        mock_web3,
        mock_get_public_minting,
        mock_pi_license_template_client,
        mock_derivative_ip_asset_registry_client,
        mock_license_registry_client,
        mock_workflow_clients,
    ):
        request = MintAndRegisterRequest(
            spg_nft_contract=ADDRESS,
            recipient=ACCOUNT_ADDRESS,
            ip_metadata=IP_METADATA,
            deriv_data=DerivativeDataInput(
                parent_ip_ids=[IP_ID], license_terms_ids=[1]
            ),
            allow_duplicates=False,
        )
        workflow_mocks = mock_workflow_clients()
        derivative_workflows_client = workflow_mocks["derivative_workflows_client"]
        with (
            mock_get_public_minting(public_minting=True),
            mock_pi_license_template_client(),
            mock_derivative_ip_asset_registry_client(),
            mock_license_registry_client(),
            workflow_mocks["royalty_token_distribution_patch"],
            workflow_mocks["license_attachment_patch"],
            workflow_mocks["derivative_workflows_patch"],
        ):
            result = transform_request(request, mock_web3, account, CHAIN_ID)
            # Assert real encoding result (not mock value)
            derivative_workflows_client.contract.encode_abi.assert_called_once()
            call_args = derivative_workflows_client.contract.encode_abi.call_args
            assert result.is_use_multicall3 is True
            assert result.workflow_address == "derivative_workflows_client_address"
            assert result.extra_data is None
            assert call_args[1]["abi_element_identifier"] == (
                "mintAndRegisterIpAndMakeDerivative"
            )
            assert call_args[1]["args"][0] == ADDRESS  # spg_nft_contract
            assert (
                call_args[1]["args"][2]
                == IPMetadata.from_input(IP_METADATA).get_validated_data()
            )  # metadata
            assert call_args[1]["args"][3] == ACCOUNT_ADDRESS  # recipient
            assert (
                call_args[1]["args"][4] is False
            )  # allow_duplicates (default for this method)
            assert result.workflow_multicall_reference is not None

    def test_raises_error_for_invalid_mint_and_register_request_type(
        self,
        mock_web3,
        mock_get_public_minting,
        mock_workflow_clients,
    ):
        request = MintAndRegisterRequest(
            spg_nft_contract=ADDRESS,
            ip_metadata=IP_METADATA,
        )
        workflow_mocks = mock_workflow_clients()
        with (
            mock_get_public_minting(),
            workflow_mocks["royalty_token_distribution_patch"],
            workflow_mocks["license_attachment_patch"],
            workflow_mocks["derivative_workflows_patch"],
        ):
            with pytest.raises(
                ValueError, match="Invalid mint and register request type"
            ):
                transform_request(request, mock_web3, account, CHAIN_ID)


class TestHandleRegisterRequest:
    def test_register_ip_and_attach_pil_terms_and_deploy_royalty_vault(
        self,
        mock_web3,
        mock_ip_asset_registry_client,
        mock_sign_util,
        mock_module_clients,
        mock_royalty_module_client,
        mock_module_registry_client,
        mock_workflow_clients,
    ):
        request = RegisterRegistrationRequest(
            nft_contract=ADDRESS,
            token_id=1,
            ip_metadata=IP_METADATA,
            license_terms_data=LICENSE_TERMS_DATA,
            royalty_shares=[RoyaltyShareInput(recipient=ADDRESS, percentage=50.0)],
            deadline=2000,
        )
        workflow_mocks = mock_workflow_clients()
        royalty_token_distribution_client = workflow_mocks[
            "royalty_token_distribution_client"
        ]
        module_patches = mock_module_clients()
        with (
            mock_ip_asset_registry_client(),
            mock_sign_util(deadline=2000),
            mock_royalty_module_client(),
            mock_module_registry_client,
            workflow_mocks["royalty_token_distribution_patch"],
            workflow_mocks["license_attachment_patch"],
            workflow_mocks["derivative_workflows_patch"],
            workflow_mocks["get_function_signature"],
            module_patches["core_metadata_module_patch"],
            module_patches["licensing_module_patch"],
        ):
            result = transform_request(request, mock_web3, account, CHAIN_ID)

            royalty_token_distribution_client.contract.encode_abi.assert_called_once()
            call_args = royalty_token_distribution_client.contract.encode_abi.call_args
            assert call_args[1]["abi_element_identifier"] == (
                "registerIpAndAttachPILTermsAndDeployRoyaltyVault"
            )
            args = call_args[1]["args"]
            assert args[0] == ADDRESS  # nft_contract
            assert args[1] == 1  # token_id
            assert (
                args[2] == IPMetadata.from_input(IP_METADATA).get_validated_data()
            )  # metadata
            assert args[3][0] == LICENSE_TERMS_DATA_CAMEL_CASE  # license_terms_data
            assert args[4]["signer"] == ACCOUNT_ADDRESS  # signature data
            assert args[4]["deadline"] == 2000
            assert args[4]["signature"] == b"signature"
            assert result.is_use_multicall3 is False
            assert (
                result.workflow_address == "royalty_token_distribution_client_address"
            )
            assert result.extra_data is not None
            royalty_shares = result.extra_data["royalty_shares"]
            royalty_total_amount = cast(dict[str, int], result.extra_data)[
                "royalty_total_amount"
            ]
            assert royalty_total_amount == 50 * 10**6
            assert len(royalty_shares) == 1
            royalty_share_dict = cast(list[dict[str, str | int]], royalty_shares)[0]
            assert royalty_share_dict["recipient"] == ADDRESS
            assert royalty_share_dict["percentage"] == 50 * 10**6
            assert result.extra_data["deadline"] == 2000
            assert result.workflow_multicall_reference is not None

    def test_register_ip_and_make_derivative_and_deploy_royalty_vault(
        self,
        mock_web3,
        mock_ip_asset_registry_client,
        mock_sign_util,
        mock_module_clients,
        mock_pi_license_template_client,
        mock_derivative_ip_asset_registry_client,
        mock_license_registry_client,
        mock_workflow_clients,
    ):
        request = RegisterRegistrationRequest(
            nft_contract=ADDRESS,
            token_id=1,
            deriv_data=DerivativeDataInput(
                parent_ip_ids=[IP_ID], license_terms_ids=[1]
            ),
            royalty_shares=[RoyaltyShareInput(recipient=ADDRESS, percentage=50.0)],
        )
        workflow_mocks = mock_workflow_clients()
        royalty_token_distribution_client = workflow_mocks[
            "royalty_token_distribution_client"
        ]
        module_patches = mock_module_clients()
        with (
            mock_ip_asset_registry_client(),
            mock_sign_util(),
            mock_pi_license_template_client(),
            mock_derivative_ip_asset_registry_client(),
            mock_license_registry_client(),
            workflow_mocks["royalty_token_distribution_patch"],
            workflow_mocks["license_attachment_patch"],
            workflow_mocks["derivative_workflows_patch"],
            workflow_mocks["get_function_signature"],
            module_patches["core_metadata_module_patch"],
            module_patches["licensing_module_patch"],
        ):
            result = transform_request(request, mock_web3, account, CHAIN_ID)

            # Verify encode_abi was called with correct method and arguments
            royalty_token_distribution_client.contract.encode_abi.assert_called_once()
            call_args = royalty_token_distribution_client.contract.encode_abi.call_args
            assert result.is_use_multicall3 is False
            assert (
                result.workflow_address == "royalty_token_distribution_client_address"
            )
            assert result.extra_data is not None
            royalty_shares = result.extra_data["royalty_shares"]
            assert len(royalty_shares) == 1
            royalty_share_dict = cast(list[dict[str, str | int]], royalty_shares)[0]
            assert royalty_share_dict["recipient"] == ADDRESS
            assert royalty_share_dict["percentage"] == 50 * 10**6
            assert call_args[1]["abi_element_identifier"] == (
                "registerIpAndMakeDerivativeAndDeployRoyaltyVault"
            )
            # Verify args
            args = call_args[1]["args"]
            assert args[0] == ADDRESS  # nft_contract
            assert args[1] == 1  # token_id
            assert args[2] == IPMetadata.from_input().get_validated_data()  # metadata
            assert args[4]["signer"] == ACCOUNT_ADDRESS
            assert args[4]["deadline"] == 1000
            assert args[4]["signature"] == b"signature"
            assert result.workflow_multicall_reference is not None

    def test_register_ip_and_attach_pil_terms(
        self,
        mock_web3,
        mock_ip_asset_registry_client,
        mock_sign_util,
        mock_module_clients,
        mock_royalty_module_client,
        mock_module_registry_client,
        mock_workflow_clients,
    ):
        request = RegisterRegistrationRequest(
            nft_contract=ADDRESS,
            token_id=1,
            ip_metadata=IP_METADATA,
            license_terms_data=LICENSE_TERMS_DATA,
        )
        workflow_mocks = mock_workflow_clients()
        license_attachment_client = workflow_mocks["license_attachment_client"]
        module_patches = mock_module_clients()
        with (
            mock_ip_asset_registry_client(),
            mock_sign_util(),
            mock_royalty_module_client(),
            mock_module_registry_client,
            workflow_mocks["royalty_token_distribution_patch"],
            workflow_mocks["license_attachment_patch"],
            workflow_mocks["derivative_workflows_patch"],
            workflow_mocks["get_function_signature"],
            module_patches["core_metadata_module_patch"],
            module_patches["licensing_module_patch"],
        ):
            result = transform_request(request, mock_web3, account, CHAIN_ID)

            # Verify encode_abi was called with correct method and arguments
            license_attachment_client.contract.encode_abi.assert_called_once()
            call_args = license_attachment_client.contract.encode_abi.call_args
            assert result.is_use_multicall3 is False
            assert result.workflow_address == "license_attachment_client_address"
            assert result.extra_data is not None
            license_terms_data = result.extra_data.get("license_terms_data")
            assert license_terms_data is not None
            assert license_terms_data[0] == LICENSE_TERMS_DATA_CAMEL_CASE
            assert call_args[1]["abi_element_identifier"] == (
                "registerIpAndAttachPILTerms"
            )
            # Verify args
            args = call_args[1]["args"]
            assert args[0] == ADDRESS  # nft_contract
            assert args[1] == 1  # token_id
            assert (
                args[2] == IPMetadata.from_input(IP_METADATA).get_validated_data()
            )  # metadata
            assert args[3][0] == LICENSE_TERMS_DATA_CAMEL_CASE  # license_terms_data
            assert args[4]["signer"] == ACCOUNT_ADDRESS
            assert args[4]["deadline"] == 1000
            assert args[4]["signature"] == b"signature"
            assert result.workflow_multicall_reference is not None

    def test_register_ip_and_make_derivative(
        self,
        mock_web3,
        mock_ip_asset_registry_client,
        mock_sign_util,
        mock_module_clients,
        mock_pi_license_template_client,
        mock_derivative_ip_asset_registry_client,
        mock_license_registry_client,
        mock_workflow_clients,
    ):
        request = RegisterRegistrationRequest(
            nft_contract=ADDRESS,
            token_id=1,
            ip_metadata=IP_METADATA,
            deriv_data=DerivativeDataInput(
                parent_ip_ids=[IP_ID], license_terms_ids=[1]
            ),
        )
        workflow_mocks = mock_workflow_clients()
        derivative_workflows_client = workflow_mocks["derivative_workflows_client"]
        module_patches = mock_module_clients()
        with (
            mock_ip_asset_registry_client(),
            mock_sign_util(),
            mock_pi_license_template_client(),
            mock_derivative_ip_asset_registry_client(),
            mock_license_registry_client(),
            workflow_mocks["royalty_token_distribution_patch"],
            workflow_mocks["license_attachment_patch"],
            workflow_mocks["derivative_workflows_patch"],
            workflow_mocks["get_function_signature"],
            module_patches["core_metadata_module_patch"],
            module_patches["licensing_module_patch"],
        ):
            result = transform_request(request, mock_web3, account, CHAIN_ID)

            # Verify encode_abi was called with correct method and arguments
            derivative_workflows_client.contract.encode_abi.assert_called_once()
            call_args = derivative_workflows_client.contract.encode_abi.call_args
            assert result.is_use_multicall3 is False
            assert result.workflow_address == "derivative_workflows_client_address"
            assert result.extra_data is None
            assert call_args[1]["abi_element_identifier"] == (
                "registerIpAndMakeDerivative"
            )
            # Verify args
            args = call_args[1]["args"]
            assert args[0] == ADDRESS  # nft_contract
            assert args[1] == 1  # token_id
            assert (
                args[3] == IPMetadata.from_input(IP_METADATA).get_validated_data()
            )  # metadata
            assert args[4]["signer"] == ACCOUNT_ADDRESS
            assert args[4]["deadline"] == 1000
            assert args[4]["signature"] == b"signature"
            assert result.workflow_multicall_reference is not None

    def test_raises_error_when_ip_not_registered(
        self,
        mock_web3,
        mock_ip_asset_registry_client,
    ):
        request = RegisterRegistrationRequest(
            nft_contract=ADDRESS,
            token_id=1,
            ip_metadata=IP_METADATA,
            license_terms_data=LICENSE_TERMS_DATA,
        )
        with (
            mock_ip_asset_registry_client(is_registered=True),
            pytest.raises(
                ValueError, match="The NFT with id 1 is already registered as IP."
            ),
        ):
            transform_request(request, mock_web3, account, CHAIN_ID)


class TestTransformDistributeRoyaltyTokensRequest:
    @pytest.fixture
    def mock_ip_account_impl_client(self):
        """Mock IPAccountImplClient."""

        def _mock():
            return patch(
                "story_protocol_python_sdk.utils.registration.transform_registration_request.IPAccountImplClient",
                return_value=MagicMock(state=MagicMock(return_value=123)),
            )

        return _mock

    @pytest.fixture
    def mock_ip_royalty_vault_client(self):
        """Mock IpRoyaltyVaultImplClient."""

        def _mock():
            mock_contract = MagicMock()
            mock_contract.encode_abi.return_value = b"encoded_approve"
            return patch(
                "story_protocol_python_sdk.utils.registration.transform_registration_request.IpRoyaltyVaultImplClient",
                return_value=MagicMock(contract=mock_contract),
            )

        return _mock

    @pytest.fixture
    def mock_royalty_token_distribution_workflows_client(self):
        """Mock RoyaltyTokenDistributionWorkflowsClient."""

        def _mock():
            mock_contract = MagicMock()
            mock_contract.address = (
                "royalty_token_distribution_workflows_client_address"
            )
            mock_contract.encode_abi.return_value = b"encoded_distribute"
            mock_build_multicall = MagicMock()
            return patch(
                "story_protocol_python_sdk.utils.registration.transform_registration_request.RoyaltyTokenDistributionWorkflowsClient",
                return_value=MagicMock(
                    contract=mock_contract,
                    build_multicall_transaction=mock_build_multicall,
                ),
            )

        return _mock

    def test_transforms_distribute_royalty_tokens_request_successfully(
        self,
        mock_web3,
        mock_ip_account_impl_client,
        mock_ip_royalty_vault_client,
        mock_royalty_token_distribution_workflows_client,
        mock_sign_util,
        mock_account,
    ):
        """Test successful transformation of distribute royalty tokens request."""
        ip_id = IP_ID
        royalty_vault = "0xRoyaltyVault"
        royalty_shares = [
            RoyaltyShareInput(recipient="0xRecipient1", percentage=50),
            RoyaltyShareInput(recipient="0xRecipient2", percentage=50),
        ]
        deadline = 1000
        total_amount = 100

        with (
            mock_ip_account_impl_client(),
            mock_ip_royalty_vault_client(),
            mock_royalty_token_distribution_workflows_client(),
            mock_sign_util(),
        ):
            result = transform_distribute_royalty_tokens_request(
                ip_id=ip_id,
                royalty_vault=royalty_vault,
                deadline=deadline,
                web3=mock_web3,
                account=mock_account,
                chain_id=CHAIN_ID,
                royalty_shares=royalty_shares,
                total_amount=total_amount,
            )

            # Verify result structure
            assert result.encoded_tx_data == b"encoded_distribute"
            assert result.is_use_multicall3 is False
            assert (
                result.workflow_address
                == "royalty_token_distribution_workflows_client_address"
            )
            assert result.extra_data is None
            assert result.workflow_multicall_reference is not None

            # Verify validated_request structure
            assert result.validated_request[0] == ip_id
            assert result.validated_request[1] == royalty_shares
            signature_data = cast(dict, result.validated_request[2])
            assert signature_data["signer"] == ADDRESS
            assert signature_data["deadline"] == deadline
            assert signature_data["signature"] == b"signature"
