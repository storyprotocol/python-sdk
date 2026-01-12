"""Transform registration request utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

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
    EncodedTxData,
    ExtraData,
    MintAndRegisterRequest,
    RegisterRegistrationRequest,
    TransformedRegistrationRequest,
)
from story_protocol_python_sdk.utils.constants import ZERO_HASH
from story_protocol_python_sdk.utils.derivative_data import DerivativeData
from story_protocol_python_sdk.utils.ip_metadata import IPMetadata
from story_protocol_python_sdk.utils.registration_utils import (
    get_public_minting,
    validate_license_terms_data,
)
from story_protocol_python_sdk.utils.royalty import get_royalty_shares
from story_protocol_python_sdk.utils.sign import Sign
from story_protocol_python_sdk.utils.validation import validate_address

if TYPE_CHECKING:
    pass


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
        ip_asset: The IPAsset instance for validation and encoding

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
    - Exception: Royalty distribution methods always use SPG's native multicall
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

    # Validate request
    royalty_token_distribution_workflows_client = (
        RoyaltyTokenDistributionWorkflowsClient(web3)
    )
    royalty_token_distribution_workflows_address = (
        royalty_token_distribution_workflows_client.contract.address
    )
    # Build encoded data based on request type
    if license_terms_data and royalty_shares:
        encoded_data = royalty_token_distribution_workflows_client.contract.encode_abi(
            abi_element_identifier="mintAndRegisterIpAndAttachPILTermsAndDistributeRoyaltyTokens",
            args=[
                spg_nft_contract,
                recipient,
                IPMetadata.from_input(request.ip_metadata).get_validated_data(),
                license_terms_data,
                royalty_shares,
                # TODO Need to base on request type to determine if allow_duplicates is true or false, due to history reasons
                # We also need unified the allow_duplicates logic for all request types, due to history reasons. But it can cause breaking changes.
                request.allow_duplicates,
            ],
        )

        return TransformedRegistrationRequest(
            # TODO: not sure if need the property
            encoded_tx_data=EncodedTxData(
                to=royalty_token_distribution_workflows_address, data=encoded_data
            ),
            is_use_multicall3=is_public_minting,
            workflow_address=royalty_token_distribution_workflows_address,
            extra_data=None,
        )

    elif deriv_data and royalty_shares:
        encoded_data = royalty_token_distribution_workflows_client.contract.encode_abi(
            abi_element_identifier="mintAndRegisterIpAndMakeDerivativeAndDistributeRoyaltyTokens",
            args=[
                spg_nft_contract,
                recipient,
                IPMetadata.from_input(request.ip_metadata).get_validated_data(),
                deriv_data,
                royalty_shares,
                request.allow_duplicates,
            ],
        )

        return TransformedRegistrationRequest(
            encoded_tx_data=EncodedTxData(
                to=royalty_token_distribution_workflows_address, data=encoded_data
            ),
            is_use_multicall3=is_public_minting,
            workflow_address=royalty_token_distribution_workflows_address,
            extra_data=None,
        )

    elif license_terms_data:
        license_attachment_workflows_client = LicenseAttachmentWorkflowsClient(web3)
        license_attachment_workflows_address = (
            license_attachment_workflows_client.contract.address
        )
        encoded_data = license_attachment_workflows_client.contract.encode_abi(
            abi_element_identifier="mintAndRegisterIpAndAttachPILTerms",
            args=[
                spg_nft_contract,
                recipient,
                IPMetadata.from_input(request.ip_metadata).get_validated_data(),
                license_terms_data,
                request.allow_duplicates,
            ],
        )
        return TransformedRegistrationRequest(
            encoded_tx_data=EncodedTxData(
                to=license_attachment_workflows_address, data=encoded_data
            ),
            is_use_multicall3=is_public_minting,
            workflow_address=license_attachment_workflows_address,
            extra_data=None,
        )

    elif deriv_data:
        derivative_workflows_client = DerivativeWorkflowsClient(web3)
        derivative_workflows_address = derivative_workflows_client.contract.address
        encoded_data = derivative_workflows_client.contract.encode_abi(
            abi_element_identifier="mintAndRegisterIpAndMakeDerivative",
            args=[
                spg_nft_contract,
                deriv_data,
                IPMetadata.from_input(request.ip_metadata).get_validated_data(),
                recipient,
                request.allow_duplicates,
            ],
        )

        return TransformedRegistrationRequest(
            encoded_tx_data=EncodedTxData(
                to=derivative_workflows_address, data=encoded_data
            ),
            is_use_multicall3=is_public_minting,
            workflow_address=derivative_workflows_address,
            extra_data=None,
        )

    else:
        raise ValueError("Invalid mint and register request type")


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
    royalty_token_distribution_workflows_client = (
        RoyaltyTokenDistributionWorkflowsClient(web3)
    )
    royalty_token_distribution_workflows_address = (
        royalty_token_distribution_workflows_client.contract.address
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
    deadline = sign_util.get_deadline(deadline=request.deadline)
    if license_terms_data and royalty_shares:
        signature_response = sign_util.get_permission_signature(
            ip_id=ip_id,
            deadline=deadline,
            state=web3.to_bytes(hexstr=HexStr(ZERO_HASH)),
            permissions=[
                {
                    "ipId": ip_id,
                    "signer": royalty_token_distribution_workflows_address,
                    "to": core_metadata_module_client.contract.address,
                    "permission": AccessPermission.ALLOW,
                    "func": "setAll(address,string,bytes32,bytes32)",
                },
                {
                    "ipId": ip_id,
                    "signer": royalty_token_distribution_workflows_address,
                    "to": licensing_module_client.contract.address,
                    "permission": AccessPermission.ALLOW,
                    "func": "attachLicenseTerms(address,address,uint256)",
                },
                {
                    "ipId": ip_id,
                    "signer": royalty_token_distribution_workflows_address,
                    "to": licensing_module_client.contract.address,
                    "permission": AccessPermission.ALLOW,
                    "func": "setLicensingConfig(address,address,uint256,(bool,uint256,address,bytes,uint32,bool,uint32,address))",
                },
            ],
        )
        encoded_data = royalty_token_distribution_workflows_client.contract.encode_abi(
            abi_element_identifier="registerIpAndAttachPILTermsAndDeployRoyaltyVault",
            args=[
                nft_contract,
                request.token_id,
                IPMetadata.from_input(request.ip_metadata).get_validated_data(),
                license_terms_data,
                {
                    "signer": web3.to_checksum_address(wallet_address),
                    "deadline": deadline,
                    "signature": signature_response["signature"],
                },
            ],
        )

        return TransformedRegistrationRequest(
            encoded_tx_data=EncodedTxData(
                to=royalty_token_distribution_workflows_address, data=encoded_data
            ),
            is_use_multicall3=False,
            workflow_address=royalty_token_distribution_workflows_address,
            extra_data=ExtraData(
                royalty_shares=royalty_shares,
                deadline=request.deadline,
            ),
        )

    elif deriv_data and royalty_shares:
        signature_response = sign_util.get_permission_signature(
            ip_id=ip_id,
            deadline=deadline,
            state=web3.to_bytes(hexstr=HexStr(ZERO_HASH)),
            permissions=[
                {
                    "ipId": ip_id,
                    "signer": royalty_token_distribution_workflows_address,
                    "to": core_metadata_module_client.contract.address,
                    "permission": AccessPermission.ALLOW,
                    "func": "setAll(address,string,bytes32,bytes32)",
                },
                {
                    "ipId": ip_id,
                    "signer": royalty_token_distribution_workflows_address,
                    "to": licensing_module_client.contract.address,
                    "permission": AccessPermission.ALLOW,
                    "func": "registerDerivative(address,address[],uint256[],address,bytes,uint256,uint32,address)",
                },
            ],
        )

        encoded_data = royalty_token_distribution_workflows_client.contract.encode_abi(
            abi_element_identifier="registerIpAndMakeDerivativeAndDeployRoyaltyVault",
            args=[
                nft_contract,
                request.token_id,
                IPMetadata.from_input(request.ip_metadata).get_validated_data(),
                deriv_data,
                {
                    "signer": wallet_address,
                    "deadline": deadline,
                    "signature": signature_response["signature"],
                },
            ],
        )

        return TransformedRegistrationRequest(
            encoded_tx_data=EncodedTxData(
                to=royalty_token_distribution_workflows_address, data=encoded_data
            ),
            is_use_multicall3=False,
            workflow_address=royalty_token_distribution_workflows_address,
            extra_data=ExtraData(
                royalty_shares=royalty_shares,
                deadline=deadline,
            ),
        )

    elif license_terms_data:
        license_attachment_workflows_client = LicenseAttachmentWorkflowsClient(web3)
        license_attachment_workflows_address = (
            license_attachment_workflows_client.contract.address
        )
        encoded_data = license_attachment_workflows_client.contract.encode_abi(
            abi_element_identifier="registerIpAndAttachPILTerms",
            args=[
                nft_contract,
                request.token_id,
                IPMetadata.from_input(request.ip_metadata).get_validated_data(),
                license_terms_data,
            ],
        )

        return TransformedRegistrationRequest(
            encoded_tx_data=EncodedTxData(
                to=license_attachment_workflows_address, data=encoded_data
            ),
            is_use_multicall3=False,
            workflow_address=license_attachment_workflows_address,
            extra_data=None,
        )

    elif deriv_data:
        derivative_workflows_client = DerivativeWorkflowsClient(web3)
        derivative_workflows_address = derivative_workflows_client.contract.address
        encoded_data = derivative_workflows_client.contract.encode_abi(
            abi_element_identifier="registerIpAndMakeDerivative",
            args=[
                nft_contract,
                deriv_data,
                IPMetadata.from_input(request.ip_metadata).get_validated_data(),
                wallet_address,
            ],
        )
        return TransformedRegistrationRequest(
            encoded_tx_data=EncodedTxData(
                to=derivative_workflows_address, data=encoded_data
            ),
            is_use_multicall3=False,
            workflow_address=derivative_workflows_address,
            extra_data=None,
        )

    else:
        raise ValueError("Invalid mint and register request type")
