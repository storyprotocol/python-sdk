"""Transform registration request utilities."""

from ens.ens import Address, HexStr
from typing_extensions import cast
from web3 import Web3

from story_protocol_python_sdk.abi.CoreMetadataModule.CoreMetadataModule_client import (
    CoreMetadataModuleClient,
)
from story_protocol_python_sdk.abi.DerivativeWorkflows.DerivativeWorkflows_client import (
    DerivativeWorkflowsClient,
)
from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import (
    IPAssetRegistryClient,
)
from story_protocol_python_sdk.abi.LicenseAttachmentWorkflows.LicenseAttachmentWorkflows_client import (
    LicenseAttachmentWorkflowsClient,
)
from story_protocol_python_sdk.abi.LicensingModule.LicensingModule_client import (
    LicensingModuleClient,
)
from story_protocol_python_sdk.abi.RoyaltyTokenDistributionWorkflows.RoyaltyTokenDistributionWorkflows_client import (
    RoyaltyTokenDistributionWorkflowsClient,
)
from story_protocol_python_sdk.types.common import AccessPermission
from story_protocol_python_sdk.types.resource.IPAsset import (
    ExtraData,
    MintAndRegisterRequest,
    RegisterRegistrationRequest,
    TransformedRegistrationRequest,
)
from story_protocol_python_sdk.types.resource.Royalty import RoyaltyShareInput
from story_protocol_python_sdk.utils.constants import ZERO_HASH
from story_protocol_python_sdk.utils.derivative_data import DerivativeData
from story_protocol_python_sdk.utils.ip_metadata import IPMetadata
from story_protocol_python_sdk.utils.registration.registration_utils import (
    get_public_minting,
    validate_license_terms_data,
)
from story_protocol_python_sdk.utils.royalty import get_royalty_shares
from story_protocol_python_sdk.utils.sign import Sign
from story_protocol_python_sdk.utils.validation import validate_address


def get_allow_duplicates(allow_duplicates: bool | None, request_type: str) -> bool:
    """
    Get the allow duplicates value based on the request type.
    Due to history reasons, we need to use different allow duplicates values for different request types.
    In the future, we need to unified the allow duplicates logic for all request types, but it can cause breaking changes.
    Args:
        allow_duplicates: The allow duplicates value.
        request_type: The request type.
    Returns:
        The allow duplicates value.
    """
    ALLOW_DUPLICATES_MAP = {
        "mintAndRegisterIpAndAttachPILTermsAndDistributeRoyaltyTokens": True,
        "mintAndRegisterIpAndMakeDerivativeAndDistributeRoyaltyTokens": True,
        "mintAndRegisterIpAndAttachPILTerms": False,
        "mintAndRegisterIpAndMakeDerivative": True,
    }
    return (
        allow_duplicates
        if allow_duplicates is not None
        else ALLOW_DUPLICATES_MAP[request_type]
    )


def transform_registration_request(
    request: MintAndRegisterRequest | RegisterRegistrationRequest,
    web3: Web3,
    wallet_address: Address,
    chain_id: int,
) -> TransformedRegistrationRequest:
    """
    Transform a registration request into encoded transaction data with multicall info.

    This is the main entry point for processing registration requests. It:
    1. Validates all input parameters
    2. Generates required signatures (for register* methods)
    3. Encodes the transaction data
    4. Determines whether to use multicall3 or SPG's native multicall

    Args:
        request: The registration request (MintAndRegisterRequest or RegisterRegistrationRequest)
        web3: Web3 instance for contract interaction
        wallet_address: The wallet address for signing and recipient fallback
        chain_id: The chain ID for IP ID calculation

    Returns:
        TransformedRegistrationRequest with encoded data and multicall strategy

    Raises:
        ValueError: If the request is invalid
    """
    # Check request type by attribute presence (following TypeScript SDK pattern)
    if hasattr(request, "spg_nft_contract"):
        return _handle_mint_and_register_request(
            cast(MintAndRegisterRequest, request), web3, wallet_address
        )
    elif hasattr(request, "nft_contract") and hasattr(request, "token_id"):
        return _handle_register_request(request, web3, wallet_address, chain_id)
    else:
        raise ValueError("Invalid registration request type")


# =============================================================================
# Mint and Register Request Handlers
# =============================================================================


def _handle_mint_and_register_request(
    request: MintAndRegisterRequest,
    web3: Web3,
    wallet_address: Address,
) -> TransformedRegistrationRequest:
    """
    Handle mintAndRegister* workflow requests.

    Supports:
    - mintAndRegisterIpAndAttachPILTermsAndDistributeRoyaltyTokens
    - mintAndRegisterIpAndMakeDerivativeAndDistributeRoyaltyTokens
    - mintAndRegisterIpAndAttachPILTerms
    - mintAndRegisterIpAndMakeDerivative

    Multicall strategy:
    - Public minting enabled: Uses multicall3
    - Public minting disabled: Uses SPG's native multicall
    """
    spg_nft_contract = validate_address(request.spg_nft_contract)
    is_public_minting = get_public_minting(spg_nft_contract, web3)
    recipient = (
        validate_address(request.recipient) if request.recipient else wallet_address
    )
    license_terms_data = (
        validate_license_terms_data(request.license_terms_data, web3)
        if request.license_terms_data
        else None
    )
    deriv_data = (
        DerivativeData.from_input(
            web3=web3, input_data=request.deriv_data
        ).get_validated_data()
        if request.deriv_data
        else None
    )
    royalty_shares = (
        get_royalty_shares(request.royalty_shares)["royalty_shares"]
        if request.royalty_shares
        else None
    )

    metadata = IPMetadata.from_input(request.ip_metadata).get_validated_data()
    # Build encoded data based on request type
    if license_terms_data and royalty_shares:
        return _handle_mint_and_register_with_license_terms_and_royalty_tokens(
            web3=web3,
            spg_nft_contract=spg_nft_contract,
            recipient=recipient,
            metadata=metadata,
            license_terms_data=license_terms_data,
            royalty_shares=royalty_shares,
            allow_duplicates=request.allow_duplicates,
            is_public_minting=is_public_minting,
        )

    elif deriv_data and royalty_shares:
        return _handle_mint_and_register_with_derivative_and_royalty_tokens(
            web3=web3,
            spg_nft_contract=spg_nft_contract,
            recipient=recipient,
            metadata=metadata,
            deriv_data=deriv_data,
            royalty_shares=royalty_shares,
            allow_duplicates=request.allow_duplicates,
            is_public_minting=is_public_minting,
        )

    elif license_terms_data:
        return _handle_mint_and_register_with_license_terms(
            web3=web3,
            spg_nft_contract=spg_nft_contract,
            recipient=recipient,
            metadata=metadata,
            license_terms_data=license_terms_data,
            allow_duplicates=request.allow_duplicates,
            is_public_minting=is_public_minting,
        )

    elif deriv_data:
        return _handle_mint_and_register_with_derivative(
            web3=web3,
            spg_nft_contract=spg_nft_contract,
            recipient=recipient,
            metadata=metadata,
            deriv_data=deriv_data,
            allow_duplicates=request.allow_duplicates,
            is_public_minting=is_public_minting,
        )

    else:
        raise ValueError("Invalid mint and register request type")


def _handle_mint_and_register_with_license_terms_and_royalty_tokens(
    web3: Web3,
    spg_nft_contract: Address,
    recipient: Address,
    metadata: dict,
    license_terms_data: list[dict],
    royalty_shares: list[dict],
    allow_duplicates: bool | None,
    is_public_minting: bool,
) -> TransformedRegistrationRequest:
    """Handle mintAndRegisterIpAndAttachPILTermsAndDistributeRoyaltyTokens."""
    royalty_token_distribution_workflows_client = (
        RoyaltyTokenDistributionWorkflowsClient(web3)
    )
    royalty_token_distribution_workflows_address = (
        royalty_token_distribution_workflows_client.contract.address
    )
    abi_element_identifier = (
        "mintAndRegisterIpAndAttachPILTermsAndDistributeRoyaltyTokens"
    )
    validated_request = {
        "spg_nft_contract": spg_nft_contract,
        "recipient": recipient,
        "metadata": metadata,
        "license_terms_data": license_terms_data,
        "royalty_shares": royalty_shares,
        "allow_duplicates": get_allow_duplicates(
            allow_duplicates, abi_element_identifier
        ),
    }
    encoded_data = royalty_token_distribution_workflows_client.contract.encode_abi(
        abi_element_identifier=abi_element_identifier,
        args=[
            validated_request["spg_nft_contract"],
            validated_request["recipient"],
            validated_request["metadata"],
            validated_request["license_terms_data"],
            validated_request["royalty_shares"],
            validated_request["allow_duplicates"],
        ],
    )

    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=is_public_minting,
        workflow_address=royalty_token_distribution_workflows_address,
        validated_request=validated_request,
        extra_data=None,
    )


def _handle_mint_and_register_with_derivative_and_royalty_tokens(
    web3: Web3,
    spg_nft_contract: Address,
    recipient: Address,
    metadata: dict,
    deriv_data: dict,
    royalty_shares: list[dict],
    allow_duplicates: bool | None,
    is_public_minting: bool,
) -> TransformedRegistrationRequest:
    """Handle mintAndRegisterIpAndMakeDerivativeAndDistributeRoyaltyTokens."""
    royalty_token_distribution_workflows_client = (
        RoyaltyTokenDistributionWorkflowsClient(web3)
    )
    royalty_token_distribution_workflows_address = (
        royalty_token_distribution_workflows_client.contract.address
    )
    abi_element_identifier = (
        "mintAndRegisterIpAndMakeDerivativeAndDistributeRoyaltyTokens"
    )
    validated_request = {
        "spg_nft_contract": spg_nft_contract,
        "recipient": recipient,
        "metadata": metadata,
        "deriv_data": deriv_data,
        "royalty_shares": royalty_shares,
        "allow_duplicates": get_allow_duplicates(
            allow_duplicates, abi_element_identifier
        ),
    }
    encoded_data = royalty_token_distribution_workflows_client.contract.encode_abi(
        abi_element_identifier=abi_element_identifier,
        args=[
            validated_request["spg_nft_contract"],
            validated_request["recipient"],
            validated_request["metadata"],
            validated_request["deriv_data"],
            validated_request["royalty_shares"],
            validated_request["allow_duplicates"],
        ],
    )

    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=is_public_minting,
        workflow_address=royalty_token_distribution_workflows_address,
        validated_request=validated_request,
        extra_data=None,
    )


def _handle_mint_and_register_with_license_terms(
    web3: Web3,
    spg_nft_contract: Address,
    recipient: Address,
    metadata: dict,
    license_terms_data: list[dict],
    allow_duplicates: bool | None,
    is_public_minting: bool,
) -> TransformedRegistrationRequest:
    """Handle mintAndRegisterIpAndAttachPILTerms."""
    license_attachment_workflows_client = LicenseAttachmentWorkflowsClient(web3)
    license_attachment_workflows_address = (
        license_attachment_workflows_client.contract.address
    )
    abi_element_identifier = "mintAndRegisterIpAndAttachPILTerms"
    validated_request = {
        "spg_nft_contract": spg_nft_contract,
        "recipient": recipient,
        "metadata": metadata,
        "license_terms_data": license_terms_data,
        "allow_duplicates": get_allow_duplicates(
            allow_duplicates, abi_element_identifier
        ),
    }
    encoded_data = license_attachment_workflows_client.contract.encode_abi(
        abi_element_identifier=abi_element_identifier,
        args=[
            validated_request["spg_nft_contract"],
            validated_request["recipient"],
            validated_request["metadata"],
            validated_request["license_terms_data"],
            validated_request["allow_duplicates"],
        ],
    )

    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=is_public_minting,
        workflow_address=license_attachment_workflows_address,
        validated_request=validated_request,
        extra_data=None,
    )


def _handle_mint_and_register_with_derivative(
    web3: Web3,
    spg_nft_contract: Address,
    recipient: Address,
    metadata: dict,
    deriv_data: dict,
    allow_duplicates: bool | None,
    is_public_minting: bool,
) -> TransformedRegistrationRequest:
    """Handle mintAndRegisterIpAndMakeDerivative."""
    derivative_workflows_client = DerivativeWorkflowsClient(web3)
    derivative_workflows_address = derivative_workflows_client.contract.address
    abi_element_identifier = "mintAndRegisterIpAndMakeDerivative"
    validated_request = {
        "spg_nft_contract": spg_nft_contract,
        "recipient": recipient,
        "metadata": metadata,
        "deriv_data": deriv_data,
        "allow_duplicates": get_allow_duplicates(
            allow_duplicates, abi_element_identifier
        ),
    }
    encoded_data = derivative_workflows_client.contract.encode_abi(
        abi_element_identifier=abi_element_identifier,
        args=[
            validated_request["spg_nft_contract"],
            validated_request["deriv_data"],
            validated_request["metadata"],
            validated_request["recipient"],
            validated_request["allow_duplicates"],
        ],
    )

    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=is_public_minting,
        workflow_address=derivative_workflows_address,
        validated_request=validated_request,
        extra_data=None,
    )


# =============================================================================
# Register Request Handlers
# =============================================================================


def _handle_register_request(
    request: RegisterRegistrationRequest,
    web3: Web3,
    wallet_address: Address,
    chain_id: int,
) -> TransformedRegistrationRequest:
    """
    Handle register* workflow requests (already minted NFTs).

    Supports:
    - registerIpAndAttachPILTermsAndDeployRoyaltyVault
    - registerIpAndMakeDerivativeAndDeployRoyaltyVault
    - registerIpAndAttachPILTerms
    - registerIpAndMakeDerivative

    Note: register* methods always use SPG's native multicall because
    signatures require msg.sender preservation.
    """
    ip_asset_registry_client = IPAssetRegistryClient(web3)
    ip_id = ip_asset_registry_client.ipId(
        chain_id, request.nft_contract, request.token_id
    )
    if not ip_asset_registry_client.isRegistered(ip_id):
        raise ValueError(f"The NFT with id {request.token_id} is not registered as IP.")

    nft_contract = validate_address(request.nft_contract)
    sign_util = Sign(web3=web3, chain_id=chain_id, account=wallet_address)
    core_metadata_module_client = CoreMetadataModuleClient(web3)
    licensing_module_client = LicensingModuleClient(web3)
    license_terms_data = (
        validate_license_terms_data(request.license_terms_data, web3)
        if request.license_terms_data
        else None
    )
    deriv_data = (
        DerivativeData.from_input(
            web3=web3, input_data=request.deriv_data
        ).get_validated_data()
        if request.deriv_data
        else None
    )
    royalty_shares = (
        get_royalty_shares(request.royalty_shares)["royalty_shares"]
        if request.royalty_shares
        else None
    )
    state = web3.to_bytes(hexstr=HexStr(ZERO_HASH))
    metadata = IPMetadata.from_input(request.ip_metadata).get_validated_data()
    calculated_deadline = sign_util.get_deadline(deadline=request.deadline)
    if license_terms_data and royalty_shares:
        return _handle_register_with_license_terms_and_royalty_vault(
            web3=web3,
            nft_contract=nft_contract,
            token_id=request.token_id,
            metadata=metadata,
            license_terms_data=license_terms_data,
            royalty_shares=royalty_shares,
            ip_id=ip_id,
            wallet_address=wallet_address,
            calculated_deadline=calculated_deadline,
            request_deadline=request.deadline,
            sign_util=sign_util,
            core_metadata_module_client=core_metadata_module_client,
            licensing_module_client=licensing_module_client,
            state=state,
        )

    elif deriv_data and royalty_shares:
        return _handle_register_with_derivative_and_royalty_vault(
            web3=web3,
            nft_contract=nft_contract,
            token_id=request.token_id,
            metadata=metadata,
            deriv_data=deriv_data,
            royalty_shares=royalty_shares,
            ip_id=ip_id,
            wallet_address=wallet_address,
            calculated_deadline=calculated_deadline,
            request_deadline=request.deadline,
            sign_util=sign_util,
            core_metadata_module_client=core_metadata_module_client,
            licensing_module_client=licensing_module_client,
            state=state,
        )

    elif license_terms_data:
        return _handle_register_with_license_terms(
            web3=web3,
            nft_contract=nft_contract,
            token_id=request.token_id,
            metadata=metadata,
            license_terms_data=license_terms_data,
            ip_id=ip_id,
            wallet_address=wallet_address,
            calculated_deadline=calculated_deadline,
            sign_util=sign_util,
            core_metadata_module_client=core_metadata_module_client,
            licensing_module_client=licensing_module_client,
            state=state,
        )

    elif deriv_data:
        return _handle_register_with_derivative(
            web3=web3,
            nft_contract=nft_contract,
            deriv_data=deriv_data,
            metadata=metadata,
            token_id=request.token_id,
            wallet_address=wallet_address,
            ip_id=ip_id,
            calculated_deadline=calculated_deadline,
            sign_util=sign_util,
            core_metadata_module_client=core_metadata_module_client,
            licensing_module_client=licensing_module_client,
            state=state,
        )

    else:
        raise ValueError("Invalid register request type")


def _handle_register_with_license_terms_and_royalty_vault(
    web3: Web3,
    nft_contract: Address,
    token_id: int,
    metadata: dict,
    license_terms_data: list[dict],
    royalty_shares: list[dict],
    ip_id: Address,
    wallet_address: Address,
    calculated_deadline: int,
    request_deadline: int | None,
    sign_util: Sign,
    core_metadata_module_client: CoreMetadataModuleClient,
    licensing_module_client: LicensingModuleClient,
    state: bytes,
) -> TransformedRegistrationRequest:
    """Handle registerIpAndAttachPILTermsAndDeployRoyaltyVault."""
    royalty_token_distribution_workflows_client = (
        RoyaltyTokenDistributionWorkflowsClient(web3)
    )
    royalty_token_distribution_workflows_address = (
        royalty_token_distribution_workflows_client.contract.address
    )
    signature_data = sign_util.get_permission_signature(
        ip_id=ip_id,
        deadline=calculated_deadline,
        state=state,
        permissions=_get_license_terms_permissions(
            ip_id=ip_id,
            signer_address=royalty_token_distribution_workflows_address,
            core_metadata_address=core_metadata_module_client.contract.address,
            licensing_module_address=licensing_module_client.contract.address,
        ),
    )
    abi_element_identifier = "registerIpAndAttachPILTermsAndDeployRoyaltyVault"
    validated_request = {
        "nft_contract": nft_contract,
        "token_id": token_id,
        "metadata": metadata,
        "license_terms_data": license_terms_data,
        "signature_data": {
            "signer": wallet_address,
            "deadline": calculated_deadline,
            "signature": signature_data["signature"],
        },
    }
    encoded_data = royalty_token_distribution_workflows_client.contract.encode_abi(
        abi_element_identifier=abi_element_identifier,
        args=[
            validated_request["nft_contract"],
            validated_request["token_id"],
            validated_request["metadata"],
            validated_request["license_terms_data"],
            validated_request["signature_data"],
        ],
    )

    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=False,
        workflow_address=royalty_token_distribution_workflows_address,
        validated_request=validated_request,
        extra_data=ExtraData(
            royalty_shares=cast(list[RoyaltyShareInput], royalty_shares),
            deadline=request_deadline,
        ),
    )


def _handle_register_with_derivative_and_royalty_vault(
    web3: Web3,
    nft_contract: Address,
    token_id: int,
    metadata: dict,
    deriv_data: dict,
    royalty_shares: list[dict],
    ip_id: Address,
    wallet_address: Address,
    calculated_deadline: int,
    request_deadline: int | None,
    sign_util: Sign,
    core_metadata_module_client: CoreMetadataModuleClient,
    licensing_module_client: LicensingModuleClient,
    state: bytes,
) -> TransformedRegistrationRequest:
    """Handle registerIpAndMakeDerivativeAndDeployRoyaltyVault."""
    royalty_token_distribution_workflows_client = (
        RoyaltyTokenDistributionWorkflowsClient(web3)
    )
    royalty_token_distribution_workflows_address = (
        royalty_token_distribution_workflows_client.contract.address
    )
    signature_response = sign_util.get_permission_signature(
        ip_id=ip_id,
        deadline=calculated_deadline,
        state=state,
        permissions=_get_derivative_permissions(
            ip_id=ip_id,
            signer_address=royalty_token_distribution_workflows_address,
            core_metadata_address=core_metadata_module_client.contract.address,
            licensing_module_address=licensing_module_client.contract.address,
        ),
    )
    abi_element_identifier = "registerIpAndMakeDerivativeAndDeployRoyaltyVault"
    validated_request = {
        "nft_contract": nft_contract,
        "token_id": token_id,
        "metadata": metadata,
        "deriv_data": deriv_data,
        "royalty_shares": royalty_shares,
        "signature_data": {
            "signer": wallet_address,
            "deadline": calculated_deadline,
            "signature": signature_response["signature"],
        },
    }
    encoded_data = royalty_token_distribution_workflows_client.contract.encode_abi(
        abi_element_identifier=abi_element_identifier,
        args=[
            validated_request["nft_contract"],
            validated_request["token_id"],
            validated_request["metadata"],
            validated_request["deriv_data"],
            validated_request["signature_data"],
        ],
    )

    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=False,
        workflow_address=royalty_token_distribution_workflows_address,
        validated_request=validated_request,
        extra_data=ExtraData(
            royalty_shares=cast(list[RoyaltyShareInput], royalty_shares),
            deadline=request_deadline,
        ),
    )


def _handle_register_with_license_terms(
    web3: Web3,
    nft_contract: Address,
    token_id: int,
    metadata: dict,
    license_terms_data: list[dict],
    ip_id: Address,
    wallet_address: Address,
    calculated_deadline: int,
    sign_util: Sign,
    core_metadata_module_client: CoreMetadataModuleClient,
    licensing_module_client: LicensingModuleClient,
    state: bytes,
) -> TransformedRegistrationRequest:
    """Handle registerIpAndAttachPILTerms."""
    license_attachment_workflows_client = LicenseAttachmentWorkflowsClient(web3)
    license_attachment_workflows_address = (
        license_attachment_workflows_client.contract.address
    )
    signature_data = sign_util.get_permission_signature(
        ip_id=ip_id,
        deadline=calculated_deadline,
        state=state,
        permissions=_get_license_terms_permissions(
            ip_id=ip_id,
            signer_address=license_attachment_workflows_address,
            core_metadata_address=core_metadata_module_client.contract.address,
            licensing_module_address=licensing_module_client.contract.address,
        ),
    )
    abi_element_identifier = "registerIpAndAttachPILTerms"
    validated_request = {
        "nft_contract": nft_contract,
        "token_id": token_id,
        "metadata": metadata,
        "license_terms_data": license_terms_data,
        "signature_data": {
            "signer": wallet_address,
            "deadline": calculated_deadline,
            "signature": signature_data["signature"],
        },
    }
    encoded_data = license_attachment_workflows_client.contract.encode_abi(
        abi_element_identifier=abi_element_identifier,
        args=[
            validated_request["nft_contract"],
            validated_request["token_id"],
            validated_request["metadata"],
            validated_request["license_terms_data"],
            validated_request["signature_data"],
        ],
    )

    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=False,
        workflow_address=license_attachment_workflows_address,
        validated_request=validated_request,
        extra_data=None,
    )


def _handle_register_with_derivative(
    web3: Web3,
    nft_contract: Address,
    deriv_data: dict,
    metadata: dict,
    token_id: int,
    ip_id: Address,
    wallet_address: Address,
    calculated_deadline: int,
    sign_util: Sign,
    core_metadata_module_client: CoreMetadataModuleClient,
    licensing_module_client: LicensingModuleClient,
    state: bytes,
) -> TransformedRegistrationRequest:
    """Handle registerIpAndMakeDerivative."""
    derivative_workflows_client = DerivativeWorkflowsClient(web3)
    derivative_workflows_address = derivative_workflows_client.contract.address
    signature_data = sign_util.get_permission_signature(
        ip_id=ip_id,
        deadline=calculated_deadline,
        state=state,
        permissions=_get_derivative_permissions(
            ip_id=ip_id,
            signer_address=derivative_workflows_address,
            core_metadata_address=core_metadata_module_client.contract.address,
            licensing_module_address=licensing_module_client.contract.address,
        ),
    )
    abi_element_identifier = "registerIpAndMakeDerivative"
    validated_request = {
        "nft_contract": nft_contract,
        "token_id": token_id,
        "metadata": metadata,
        "deriv_data": deriv_data,
        "signature_data": {
            "signer": wallet_address,
            "deadline": calculated_deadline,
            "signature": signature_data["signature"],
        },
    }
    encoded_data = derivative_workflows_client.contract.encode_abi(
        abi_element_identifier=abi_element_identifier,
        args=[
            validated_request["nft_contract"],
            validated_request["token_id"],
            validated_request["deriv_data"],
            validated_request["metadata"],
            validated_request["signature_data"],
        ],
    )

    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=False,
        workflow_address=derivative_workflows_address,
        validated_request=validated_request,
        extra_data=None,
    )


# =============================================================================
# Internal Helper Methods
# =============================================================================


def _get_license_terms_permissions(
    ip_id: Address,
    signer_address: Address,
    core_metadata_address: Address,
    licensing_module_address: Address,
) -> list[dict]:
    """Get permissions for license terms operations."""
    return [
        {
            "ipId": ip_id,
            "signer": signer_address,
            "to": core_metadata_address,
            "permission": AccessPermission.ALLOW,
            "func": "setAll(address,string,bytes32,bytes32)",
        },
        {
            "ipId": ip_id,
            "signer": signer_address,
            "to": licensing_module_address,
            "permission": AccessPermission.ALLOW,
            "func": "attachLicenseTerms(address,address,uint256)",
        },
        {
            "ipId": ip_id,
            "signer": signer_address,
            "to": licensing_module_address,
            "permission": AccessPermission.ALLOW,
            "func": "setLicensingConfig(address,address,uint256,(bool,uint256,address,bytes,uint32,bool,uint32,address))",
        },
    ]


def _get_derivative_permissions(
    ip_id: Address,
    signer_address: Address,
    core_metadata_address: Address,
    licensing_module_address: Address,
) -> list[dict]:
    """Get permissions for derivative operations."""
    return [
        {
            "ipId": ip_id,
            "signer": signer_address,
            "to": core_metadata_address,
            "permission": AccessPermission.ALLOW,
            "func": "setAll(address,string,bytes32,bytes32)",
        },
        {
            "ipId": ip_id,
            "signer": signer_address,
            "to": licensing_module_address,
            "permission": AccessPermission.ALLOW,
            "func": "registerDerivative(address,address[],uint256[],address,bytes,uint256,uint32,address)",
        },
    ]
