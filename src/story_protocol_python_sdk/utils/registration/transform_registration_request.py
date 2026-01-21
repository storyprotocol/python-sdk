"""Transform registration request utilities."""

from dataclasses import asdict, is_dataclass, replace

from ens.ens import Address, HexStr
from eth_account.signers.local import LocalAccount
from typing_extensions import cast
from web3 import Web3

from story_protocol_python_sdk.abi.CoreMetadataModule.CoreMetadataModule_client import (
    CoreMetadataModuleClient,
)
from story_protocol_python_sdk.abi.DerivativeWorkflows.DerivativeWorkflows_client import (
    DerivativeWorkflowsClient,
)
from story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client import (
    IPAccountImplClient,
)
from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import (
    IPAssetRegistryClient,
)
from story_protocol_python_sdk.abi.IpRoyaltyVaultImpl.IpRoyaltyVaultImpl_client import (
    IpRoyaltyVaultImplClient,
)
from story_protocol_python_sdk.abi.LicenseAttachmentWorkflows.LicenseAttachmentWorkflows_client import (
    LicenseAttachmentWorkflowsClient,
)
from story_protocol_python_sdk.abi.LicensingModule.LicensingModule_client import (
    LicensingModuleClient,
)
from story_protocol_python_sdk.abi.ModuleRegistry.ModuleRegistry_client import (
    ModuleRegistryClient,
)
from story_protocol_python_sdk.abi.RoyaltyModule.RoyaltyModule_client import (
    RoyaltyModuleClient,
)
from story_protocol_python_sdk.abi.RoyaltyTokenDistributionWorkflows.RoyaltyTokenDistributionWorkflows_client import (
    RoyaltyTokenDistributionWorkflowsClient,
)
from story_protocol_python_sdk.abi.SPGNFTImpl.SPGNFTImpl_client import SPGNFTImplClient
from story_protocol_python_sdk.types.common import AccessPermission
from story_protocol_python_sdk.types.resource.IPAsset import (
    ExtraData,
    LicenseTermsDataInput,
    MintAndRegisterRequest,
    RegisterRegistrationRequest,
    TransformedRegistrationRequest,
)
from story_protocol_python_sdk.types.resource.License import LicenseTermsInput
from story_protocol_python_sdk.types.resource.Royalty import RoyaltyShareInput
from story_protocol_python_sdk.utils.constants import ZERO_ADDRESS, ZERO_HASH
from story_protocol_python_sdk.utils.derivative_data import DerivativeData
from story_protocol_python_sdk.utils.function_signature import get_function_signature
from story_protocol_python_sdk.utils.ip_metadata import IPMetadata
from story_protocol_python_sdk.utils.licensing_config_data import LicensingConfigData
from story_protocol_python_sdk.utils.pil_flavor import PILFlavor
from story_protocol_python_sdk.utils.royalty import get_royalty_shares
from story_protocol_python_sdk.utils.sign import Sign
from story_protocol_python_sdk.utils.util import convert_dict_keys_to_camel_case
from story_protocol_python_sdk.utils.validation import (
    get_revenue_share,
    validate_address,
)


def get_public_minting(spg_nft_contract: Address, web3: Web3) -> bool:
    """
    Check if SPG NFT contract has public minting enabled.

    Args:
        spg_nft_contract: The address of the SPG NFT contract.
        web3: Web3 instance.

    Returns:
        True if public minting is enabled, False otherwise.
    """
    spg_client = SPGNFTImplClient(
        web3, contract_address=validate_address(spg_nft_contract)
    )
    return spg_client.publicMinting()


def validate_license_terms_data(
    license_terms_data: list[LicenseTermsDataInput] | list[dict],
    web3: Web3,
) -> list[dict]:
    """
    Validate the license terms data.

    Args:
        license_terms_data: The license terms data to validate.
        web3: Web3 instance.

    Returns:
        The validated license terms data.
    """
    royalty_module_client = RoyaltyModuleClient(web3)
    module_registry_client = ModuleRegistryClient(web3)

    validated_license_terms_data = []
    for term in license_terms_data:
        if is_dataclass(term):
            terms_dict = asdict(term.terms)
            licensing_config_dict = term.licensing_config
        else:
            terms_dict = term["terms"]
            licensing_config_dict = term["licensing_config"]

        license_terms = PILFlavor.validate_license_terms(
            LicenseTermsInput(**terms_dict)
        )
        license_terms = replace(
            license_terms,
            commercial_rev_share=get_revenue_share(license_terms.commercial_rev_share),
        )
        if license_terms.royalty_policy != ZERO_ADDRESS:
            is_whitelisted = royalty_module_client.isWhitelistedRoyaltyPolicy(
                license_terms.royalty_policy
            )
            if not is_whitelisted:
                raise ValueError("The royalty_policy is not whitelisted.")

        if license_terms.currency != ZERO_ADDRESS:
            is_whitelisted = royalty_module_client.isWhitelistedRoyaltyToken(
                license_terms.currency
            )
            if not is_whitelisted:
                raise ValueError("The currency is not whitelisted.")

        validated_license_terms_data.append(
            {
                "terms": convert_dict_keys_to_camel_case(asdict(license_terms)),
                "licensingConfig": LicensingConfigData.validate_license_config(
                    module_registry_client, licensing_config_dict
                ),
            }
        )
    return validated_license_terms_data


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


def transform_request(
    request: MintAndRegisterRequest | RegisterRegistrationRequest,
    web3: Web3,
    account: LocalAccount,
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
        account: The account for signing and recipient fallback
        chain_id: The chain ID for IP ID calculation

    Returns:
        TransformedRegistrationRequest with encoded data and multicall strategy

    Raises:
        ValueError: If the request is invalid
    """
    # Check request type by attribute presence (following TypeScript SDK pattern)
    if hasattr(request, "spg_nft_contract"):
        return _handle_mint_and_register_request(
            cast(MintAndRegisterRequest, request), web3, account.address
        )
    elif hasattr(request, "nft_contract") and hasattr(request, "token_id"):
        return _handle_register_request(request, web3, account, chain_id)
    else:
        raise ValueError("Invalid registration request type")


def transform_distribute_royalty_tokens_request(
    ip_id: Address,
    royalty_vault: Address,
    deadline: int,
    web3: Web3,
    account: LocalAccount,
    chain_id: int,
    royalty_shares: list[RoyaltyShareInput],
    total_amount: int,
) -> TransformedRegistrationRequest:
    """
    Transform a distribute royalty tokens request into encoded transaction data with multicall info.
    distributeRoyaltyTokens method don't support multicall3 due to `msg.sender` check.
    Args:
        ip_id: The IP ID
        royalty_vault: The royalty vault address
        deadline: The deadline for the transaction
        web3: The web3 instance
        account: The account for signing and recipient fallback
        chain_id: The chain ID for IP ID calculation
        royalty_shares: The validated royalty shares with recipient and percentage.
    Returns:
        TransformedRegistrationRequest with encoded data and multicall strategy
    Raises:
        ValueError: If the request is invalid
    """
    ip_account_impl_client = IPAccountImplClient(web3, ip_id)
    state = ip_account_impl_client.state()
    royalty_token_distribution_workflows_client = (
        RoyaltyTokenDistributionWorkflowsClient(web3)
    )
    ip_royalty_vault_client = IpRoyaltyVaultImplClient(web3, royalty_vault)
    signature_response = Sign(web3, chain_id, account).get_signature(
        state=state,
        to=royalty_vault,
        encode_data=ip_royalty_vault_client.contract.encode_abi(
            abi_element_identifier="approve",
            args=[
                RoyaltyTokenDistributionWorkflowsClient(web3).contract.address,
                total_amount,
            ],
        ),
        verifying_contract=ip_id,
        deadline=deadline,
    )
    validated_request = [
        ip_id,
        royalty_shares,
        {
            "signer": web3.to_checksum_address(account.address),
            "deadline": deadline,
            "signature": signature_response["signature"],
        },
    ]
    encoded_data = royalty_token_distribution_workflows_client.contract.encode_abi(
        abi_element_identifier="distributeRoyaltyTokens",
        args=validated_request,
    )
    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=False,
        workflow_address=royalty_token_distribution_workflows_client.contract.address,
        validated_request=validated_request,
        original_method_reference=royalty_token_distribution_workflows_client.build_multicall_transaction,
        extra_data=None,
        contract_call=None,
    )


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
    validated_request = [
        spg_nft_contract,
        recipient,
        metadata,
        license_terms_data,
        royalty_shares,
        get_allow_duplicates(allow_duplicates, abi_element_identifier),
    ]
    encoded_data = royalty_token_distribution_workflows_client.contract.encode_abi(
        abi_element_identifier=abi_element_identifier,
        args=validated_request,
    )

    def contract_call() -> HexStr:
        response = royalty_token_distribution_workflows_client.mintAndRegisterIpAndAttachPILTermsAndDistributeRoyaltyTokens(
            *validated_request
        )
        web3.eth.wait_for_transaction_receipt(response["tx_hash"])
        return response["tx_hash"]

    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=is_public_minting,
        workflow_address=royalty_token_distribution_workflows_address,
        original_method_reference=royalty_token_distribution_workflows_client.build_multicall_transaction,
        validated_request=validated_request,
        extra_data=None,
        contract_call=contract_call,
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
    validated_request = [
        spg_nft_contract,
        recipient,
        metadata,
        deriv_data,
        royalty_shares,
        get_allow_duplicates(allow_duplicates, abi_element_identifier),
    ]
    encoded_data = royalty_token_distribution_workflows_client.contract.encode_abi(
        abi_element_identifier=abi_element_identifier,
        args=validated_request,
    )

    def contract_call() -> HexStr:
        response = royalty_token_distribution_workflows_client.mintAndRegisterIpAndMakeDerivativeAndDistributeRoyaltyTokens(
            *validated_request
        )
        web3.eth.wait_for_transaction_receipt(response["tx_hash"])
        return response["tx_hash"]

    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=is_public_minting,
        workflow_address=royalty_token_distribution_workflows_address,
        validated_request=validated_request,
        extra_data=None,
        contract_call=contract_call,
        original_method_reference=royalty_token_distribution_workflows_client.build_multicall_transaction,
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
    validated_request = [
        spg_nft_contract,
        recipient,
        metadata,
        license_terms_data,
        get_allow_duplicates(allow_duplicates, abi_element_identifier),
    ]
    encoded_data = license_attachment_workflows_client.contract.encode_abi(
        abi_element_identifier=abi_element_identifier,
        args=validated_request,
    )

    def contract_call() -> HexStr:
        response = (
            license_attachment_workflows_client.mintAndRegisterIpAndAttachPILTerms(
                *validated_request
            )
        )
        web3.eth.wait_for_transaction_receipt(response["tx_hash"])
        return response["tx_hash"]

    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=is_public_minting,
        workflow_address=license_attachment_workflows_address,
        validated_request=validated_request,
        extra_data=None,
        contract_call=contract_call,
        original_method_reference=license_attachment_workflows_client.build_multicall_transaction,
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
    validated_request = [
        spg_nft_contract,
        deriv_data,
        metadata,
        recipient,
        get_allow_duplicates(allow_duplicates, abi_element_identifier),
    ]
    encoded_data = derivative_workflows_client.contract.encode_abi(
        abi_element_identifier=abi_element_identifier,
        args=validated_request,
    )

    def contract_call() -> HexStr:
        response = derivative_workflows_client.mintAndRegisterIpAndMakeDerivative(
            *validated_request
        )
        web3.eth.wait_for_transaction_receipt(response["tx_hash"])
        return response["tx_hash"]

    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=is_public_minting,
        workflow_address=derivative_workflows_address,
        validated_request=validated_request,
        extra_data=None,
        contract_call=contract_call,
        original_method_reference=derivative_workflows_client.build_multicall_transaction,
    )


# =============================================================================
# Register Request Handlers
# =============================================================================


def _handle_register_request(
    request: RegisterRegistrationRequest,
    web3: Web3,
    account: LocalAccount,
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
    if ip_asset_registry_client.isRegistered(ip_id):
        raise ValueError(
            f"The NFT with id {request.token_id} is already registered as IP."
        )

    nft_contract = validate_address(request.nft_contract)
    sign_util = Sign(web3=web3, chain_id=chain_id, account=account)
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
        get_royalty_shares(request.royalty_shares) if request.royalty_shares else None
    )
    state = web3.to_bytes(hexstr=HexStr(ZERO_HASH))
    metadata = IPMetadata.from_input(request.ip_metadata).get_validated_data()
    calculated_deadline = sign_util.get_deadline(deadline=request.deadline)
    wallet_address = account.address
    if license_terms_data and royalty_shares:
        return _handle_register_with_license_terms_and_royalty_vault(
            web3=web3,
            nft_contract=nft_contract,
            token_id=request.token_id,
            metadata=metadata,
            license_terms_data=license_terms_data,
            royalty_shares=royalty_shares["royalty_shares"],
            royalty_total_amount=royalty_shares["total_amount"],
            ip_id=ip_id,
            wallet_address=wallet_address,
            calculated_deadline=calculated_deadline,
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
            royalty_shares=royalty_shares["royalty_shares"],
            ip_id=ip_id,
            wallet_address=wallet_address,
            calculated_deadline=calculated_deadline,
            sign_util=sign_util,
            core_metadata_module_client=core_metadata_module_client,
            licensing_module_client=licensing_module_client,
            state=state,
            royalty_total_amount=royalty_shares["total_amount"],
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
    sign_util: Sign,
    core_metadata_module_client: CoreMetadataModuleClient,
    licensing_module_client: LicensingModuleClient,
    state: bytes,
    royalty_total_amount: int,
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
            core_metadata_client=core_metadata_module_client,
            licensing_module_client=licensing_module_client,
        ),
    )
    abi_element_identifier = "registerIpAndAttachPILTermsAndDeployRoyaltyVault"
    validated_request = [
        nft_contract,
        token_id,
        metadata,
        license_terms_data,
        {
            "signer": wallet_address,
            "deadline": calculated_deadline,
            "signature": signature_data["signature"],
        },
    ]
    encoded_data = royalty_token_distribution_workflows_client.contract.encode_abi(
        abi_element_identifier=abi_element_identifier,
        args=validated_request,
    )

    def contract_call() -> HexStr:
        response = royalty_token_distribution_workflows_client.registerIpAndAttachPILTermsAndDeployRoyaltyVault(
            *validated_request
        )
        web3.eth.wait_for_transaction_receipt(response["tx_hash"])
        return response["tx_hash"]

    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=False,
        workflow_address=royalty_token_distribution_workflows_address,
        validated_request=validated_request,
        extra_data=ExtraData(
            royalty_shares=cast(list[RoyaltyShareInput], royalty_shares),
            deadline=calculated_deadline,
            royalty_total_amount=royalty_total_amount,
            nft_contract=nft_contract,
            token_id=token_id,
        ),
        contract_call=contract_call,
        original_method_reference=royalty_token_distribution_workflows_client.build_multicall_transaction,
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
    sign_util: Sign,
    core_metadata_module_client: CoreMetadataModuleClient,
    licensing_module_client: LicensingModuleClient,
    state: bytes,
    royalty_total_amount: int,
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
            core_metadata_client=core_metadata_module_client,
            licensing_module_client=licensing_module_client,
        ),
    )
    abi_element_identifier = "registerIpAndMakeDerivativeAndDeployRoyaltyVault"
    validated_request = [
        nft_contract,
        token_id,
        metadata,
        deriv_data,
        {
            "signer": wallet_address,
            "deadline": calculated_deadline,
            "signature": signature_response["signature"],
        },
    ]
    encoded_data = royalty_token_distribution_workflows_client.contract.encode_abi(
        abi_element_identifier=abi_element_identifier,
        args=validated_request,
    )

    def contract_call() -> HexStr:
        response = royalty_token_distribution_workflows_client.registerIpAndMakeDerivativeAndDeployRoyaltyVault(
            *validated_request
        )
        web3.eth.wait_for_transaction_receipt(response["tx_hash"])
        return response["tx_hash"]

    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=False,
        workflow_address=royalty_token_distribution_workflows_address,
        validated_request=validated_request,
        extra_data=ExtraData(
            royalty_shares=cast(list[RoyaltyShareInput], royalty_shares),
            deadline=calculated_deadline,
            royalty_total_amount=royalty_total_amount,
            nft_contract=nft_contract,
            token_id=token_id,
        ),
        contract_call=contract_call,
        original_method_reference=royalty_token_distribution_workflows_client.build_multicall_transaction,
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
            core_metadata_client=core_metadata_module_client,
            licensing_module_client=licensing_module_client,
        ),
    )
    abi_element_identifier = "registerIpAndAttachPILTerms"
    validated_request = [
        nft_contract,
        token_id,
        metadata,
        license_terms_data,
        {
            "signer": wallet_address,
            "deadline": calculated_deadline,
            "signature": signature_data["signature"],
        },
    ]
    encoded_data = license_attachment_workflows_client.contract.encode_abi(
        abi_element_identifier=abi_element_identifier,
        args=validated_request,
    )

    def contract_call() -> HexStr:
        response = license_attachment_workflows_client.registerIpAndAttachPILTerms(
            *validated_request
        )
        web3.eth.wait_for_transaction_receipt(response["tx_hash"])
        return response["tx_hash"]

    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=False,
        workflow_address=license_attachment_workflows_address,
        validated_request=validated_request,
        extra_data=None,
        contract_call=contract_call,
        original_method_reference=license_attachment_workflows_client.build_multicall_transaction,
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
            core_metadata_client=core_metadata_module_client,
            licensing_module_client=licensing_module_client,
        ),
    )
    abi_element_identifier = "registerIpAndMakeDerivative"
    validated_request = [
        nft_contract,
        token_id,
        deriv_data,
        metadata,
        {
            "signer": wallet_address,
            "deadline": calculated_deadline,
            "signature": signature_data["signature"],
        },
    ]
    encoded_data = derivative_workflows_client.contract.encode_abi(
        abi_element_identifier=abi_element_identifier,
        args=validated_request,
    )

    def contract_call() -> HexStr:
        response = derivative_workflows_client.registerIpAndMakeDerivative(
            *validated_request
        )
        web3.eth.wait_for_transaction_receipt(response["tx_hash"])
        return response["tx_hash"]

    return TransformedRegistrationRequest(
        encoded_tx_data=encoded_data,
        is_use_multicall3=False,
        workflow_address=derivative_workflows_address,
        validated_request=validated_request,
        extra_data=None,
        contract_call=contract_call,
        original_method_reference=derivative_workflows_client.build_multicall_transaction,
    )


# =============================================================================
# Internal Helper Methods
# =============================================================================


def _get_license_terms_permissions(
    ip_id: Address,
    signer_address: Address,
    core_metadata_client: CoreMetadataModuleClient,
    licensing_module_client: LicensingModuleClient,
) -> list[dict]:
    """Get permissions for license terms operations."""
    return [
        {
            "ipId": ip_id,
            "signer": signer_address,
            "to": core_metadata_client.contract.address,
            "permission": AccessPermission.ALLOW,
            "func": get_function_signature(core_metadata_client.contract.abi, "setAll"),
        },
        {
            "ipId": ip_id,
            "signer": signer_address,
            "to": licensing_module_client.contract.address,
            "permission": AccessPermission.ALLOW,
            "func": get_function_signature(
                licensing_module_client.contract.abi, "attachLicenseTerms"
            ),
        },
        {
            "ipId": ip_id,
            "signer": signer_address,
            "to": licensing_module_client.contract.address,
            "permission": AccessPermission.ALLOW,
            "func": get_function_signature(
                licensing_module_client.contract.abi, "setLicensingConfig"
            ),
        },
    ]


def _get_derivative_permissions(
    ip_id: Address,
    signer_address: Address,
    core_metadata_client: CoreMetadataModuleClient,
    licensing_module_client: LicensingModuleClient,
) -> list[dict]:
    """Get permissions for derivative operations."""
    return [
        {
            "ipId": ip_id,
            "signer": signer_address,
            "to": core_metadata_client.contract.address,
            "permission": AccessPermission.ALLOW,
            "func": get_function_signature(core_metadata_client.contract.abi, "setAll"),
        },
        {
            "ipId": ip_id,
            "signer": signer_address,
            "to": licensing_module_client.contract.address,
            "permission": AccessPermission.ALLOW,
            "func": get_function_signature(
                licensing_module_client.contract.abi, "registerDerivative"
            ),
        },
    ]
