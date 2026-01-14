from unittest.mock import MagicMock, patch

import pytest
from typing_extensions import cast

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
    transform_registration_request,
)
from tests.unit.fixtures.data import (
    ACCOUNT_ADDRESS,
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
            "story_protocol_python_sdk.utils.registration.registration_utils.SPGNFTImplClient",
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
            "story_protocol_python_sdk.utils.registration.registration_utils.RoyaltyModuleClient",
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
        "story_protocol_python_sdk.utils.registration.registration_utils.ModuleRegistryClient",
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
        patches = [
            patch(
                "story_protocol_python_sdk.utils.registration.transform_registration_request.RoyaltyTokenDistributionWorkflowsClient",
                return_value=royalty_token_distribution_client,
            ),
            patch(
                "story_protocol_python_sdk.utils.registration.transform_registration_request.LicenseAttachmentWorkflowsClient",
                return_value=license_attachment_client,
            ),
            patch(
                "story_protocol_python_sdk.utils.registration.transform_registration_request.DerivativeWorkflowsClient",
                return_value=derivative_workflows_client,
            ),
        ]
        return {
            "patches": patches,
            "royalty_token_distribution_client": royalty_token_distribution_client,
            "license_attachment_client": license_attachment_client,
            "derivative_workflows_client": derivative_workflows_client,
        }

    return _mock


@pytest.fixture
def mock_ip_asset_registry_client():
    """Mock IPAssetRegistryClient."""

    def _mock(is_registered: bool = True, ip_id: str = IP_ID):
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

        patches = [
            patch(
                "story_protocol_python_sdk.utils.registration.transform_registration_request.CoreMetadataModuleClient",
                return_value=mock_core_metadata_client,
            ),
            patch(
                "story_protocol_python_sdk.utils.registration.transform_registration_request.LicensingModuleClient",
                return_value=mock_licensing_client,
            ),
        ]
        return patches

    return _mock


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
        patches = workflow_mocks["patches"]
        license_attachment_client = workflow_mocks["license_attachment_client"]
        with (
            mock_get_public_minting(),
            mock_royalty_module_client(),
            mock_module_registry_client,
            patches[0],
            patches[1],
            patches[2],
        ):
            result = transform_registration_request(
                request, mock_web3, ACCOUNT_ADDRESS, CHAIN_ID
            )
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
            assert result.extra_data is None

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
        workflow_patches = workflow_mocks["patches"]
        module_patches = mock_module_clients()
        license_attachment_client = workflow_mocks["license_attachment_client"]
        with (
            mock_ip_asset_registry_client(),
            mock_sign_util(),
            mock_royalty_module_client(),
            mock_module_registry_client,
            workflow_patches[0],
            workflow_patches[1],
            workflow_patches[2],
            module_patches[0],
            module_patches[1],
        ):
            result = transform_registration_request(
                request, mock_web3, ACCOUNT_ADDRESS, CHAIN_ID
            )
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
            assert result.extra_data is None
            assert result.is_use_multicall3 is False

    def test_raises_error_for_invalid_request_type(
        self, mock_web3, mock_ip_asset_registry_client
    ):
        with mock_ip_asset_registry_client():
            with pytest.raises(
                ValueError, match="Invalid mint and register request type"
            ):
                transform_registration_request(
                    RegisterRegistrationRequest(
                        nft_contract=ADDRESS,
                        token_id=1,
                    ),
                    mock_web3,
                    ACCOUNT_ADDRESS,
                    CHAIN_ID,
                )

    def test_raises_error_for_invalid_registration_request_type(self, mock_web3):
        """Test that ValueError is raised when request doesn't match any known type."""
        with pytest.raises(ValueError, match="Invalid registration request type"):
            transform_registration_request(
                None,  # type: ignore[arg-type]
                mock_web3,
                ACCOUNT_ADDRESS,
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
        patches = workflow_mocks["patches"]
        royalty_token_distribution_client = workflow_mocks[
            "royalty_token_distribution_client"
        ]
        with (
            mock_get_public_minting(public_minting=True),
            mock_royalty_module_client(),
            mock_module_registry_client,
            patches[0],
            patches[1],
            patches[2],
        ):
            result = transform_registration_request(
                request, mock_web3, ACCOUNT_ADDRESS, CHAIN_ID
            )

            royalty_token_distribution_client.contract.encode_abi.assert_called_once()
            call_args = royalty_token_distribution_client.contract.encode_abi.call_args
            assert result.is_use_multicall3 is True
            assert (
                result.workflow_address == "royalty_token_distribution_client_address"
            )
            assert result.extra_data is None
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
        patches = workflow_mocks["patches"]
        royalty_token_distribution_client = workflow_mocks[
            "royalty_token_distribution_client"
        ]
        with (
            mock_get_public_minting(public_minting=False),
            mock_pi_license_template_client(),
            mock_derivative_ip_asset_registry_client(),
            mock_license_registry_client(),
            patches[0],
            patches[1],
            patches[2],
        ):
            result = transform_registration_request(
                request, mock_web3, ACCOUNT_ADDRESS, CHAIN_ID
            )

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
        patches = workflow_mocks["patches"]
        derivative_workflows_client = workflow_mocks["derivative_workflows_client"]
        with (
            mock_get_public_minting(public_minting=True),
            mock_pi_license_template_client(),
            mock_derivative_ip_asset_registry_client(),
            mock_license_registry_client(),
            patches[0],
            patches[1],
            patches[2],
        ):
            result = transform_registration_request(
                request, mock_web3, ACCOUNT_ADDRESS, CHAIN_ID
            )
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
        patches = workflow_mocks["patches"]
        with (
            mock_get_public_minting(),
            patches[0],
            patches[1],
            patches[2],
        ):
            with pytest.raises(
                ValueError, match="Invalid mint and register request type"
            ):
                transform_registration_request(
                    request, mock_web3, ACCOUNT_ADDRESS, CHAIN_ID
                )


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
        workflow_patches = workflow_mocks["patches"]
        royalty_token_distribution_client = workflow_mocks[
            "royalty_token_distribution_client"
        ]
        module_patches = mock_module_clients()
        with (
            mock_ip_asset_registry_client(),
            mock_sign_util(deadline=2000),
            mock_royalty_module_client(),
            mock_module_registry_client,
            workflow_patches[0],
            workflow_patches[1],
            workflow_patches[2],
            module_patches[0],
            module_patches[1],
        ):
            result = transform_registration_request(
                request, mock_web3, ACCOUNT_ADDRESS, CHAIN_ID
            )

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
            assert len(royalty_shares) == 1
            royalty_share_dict = cast(list[dict[str, str | int]], royalty_shares)[0]
            assert royalty_share_dict["recipient"] == ADDRESS
            assert royalty_share_dict["percentage"] == 50 * 10**6
            assert result.extra_data["deadline"] == 2000

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
        workflow_patches = workflow_mocks["patches"]
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
            workflow_patches[0],
            workflow_patches[1],
            workflow_patches[2],
            module_patches[0],
            module_patches[1],
        ):
            result = transform_registration_request(
                request, mock_web3, ACCOUNT_ADDRESS, CHAIN_ID
            )

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
        workflow_patches = workflow_mocks["patches"]
        license_attachment_client = workflow_mocks["license_attachment_client"]
        module_patches = mock_module_clients()
        with (
            mock_ip_asset_registry_client(),
            mock_sign_util(),
            mock_royalty_module_client(),
            mock_module_registry_client,
            workflow_patches[0],
            workflow_patches[1],
            workflow_patches[2],
            module_patches[0],
            module_patches[1],
        ):
            result = transform_registration_request(
                request, mock_web3, ACCOUNT_ADDRESS, CHAIN_ID
            )

            # Verify encode_abi was called with correct method and arguments
            license_attachment_client.contract.encode_abi.assert_called_once()
            call_args = license_attachment_client.contract.encode_abi.call_args
            assert result.is_use_multicall3 is False
            assert result.workflow_address == "license_attachment_client_address"
            assert result.extra_data is None
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
        workflow_patches = workflow_mocks["patches"]
        derivative_workflows_client = workflow_mocks["derivative_workflows_client"]
        module_patches = mock_module_clients()
        with (
            mock_ip_asset_registry_client(),
            mock_sign_util(),
            mock_pi_license_template_client(),
            mock_derivative_ip_asset_registry_client(),
            mock_license_registry_client(),
            workflow_patches[0],
            workflow_patches[1],
            workflow_patches[2],
            module_patches[0],
            module_patches[1],
        ):
            result = transform_registration_request(
                request, mock_web3, ACCOUNT_ADDRESS, CHAIN_ID
            )

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
            assert (
                args[2] == IPMetadata.from_input(IP_METADATA).get_validated_data()
            )  # metadata
            assert args[3] == ACCOUNT_ADDRESS  # wallet_address
            assert args[4]["signer"] == ACCOUNT_ADDRESS
            assert args[4]["deadline"] == 1000
            assert args[4]["signature"] == b"signature"

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
            mock_ip_asset_registry_client(is_registered=False),
            pytest.raises(
                ValueError, match="The NFT with id 1 is not registered as IP."
            ),
        ):
            transform_registration_request(
                request, mock_web3, ACCOUNT_ADDRESS, CHAIN_ID
            )
