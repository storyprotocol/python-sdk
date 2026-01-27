from dataclasses import dataclass
from typing import TypedDict

from ens.ens import Address, HexStr
from typing_extensions import Callable


class Multicall3Call(TypedDict):
    target: Address
    allowFailure: bool
    value: int
    callData: bytes


class AggregatedRequestData(TypedDict):
    """Aggregated request data structure."""

    call_data: list[bytes | Multicall3Call]
    license_terms_data: list[list[dict]]
    method_reference: Callable[[list[bytes], dict], HexStr]


# =============================================================================
# Transform Registration Request Types
# =============================================================================
class ExtraData(TypedDict, total=False):
    """
    Extra data for post-processing after registration.

    Attributes:
        royalty_shares: [Optional] The royalty shares for distribution.
        deadline: [Optional] The deadline for the signature.
        royalty_total_amount: [Optional] The total amount of royalty tokens to distribute.
        nft_contract: [Optional] The NFT contract address.
        token_id: [Optional] The token ID.
        license_terms_data: [Optional] The license terms data.
    """

    royalty_shares: list[dict]
    deadline: int
    royalty_total_amount: int
    nft_contract: Address
    token_id: int
    license_terms_data: list[dict] | None


@dataclass
class TransformedRegistrationRequest:
    """
    Transformed registration request with encoded data and multicall info.

    Attributes:
        encoded_tx_data: The encoded transaction data.
        is_use_multicall3: Whether to use multicall3 or SPG's native multicall.
        workflow_address: The workflow contract address.
        validated_request: The validated request arguments for the contract method.
        original_method_reference: The original method reference for building transactions.
        extra_data: [Optional] Extra data for post-processing.
    """

    encoded_tx_data: bytes
    is_use_multicall3: bool
    workflow_address: Address
    validated_request: list[Address | int | str | bytes | dict | bool]
    # TODO: need to rename with multicall3 method reference
    original_method_reference: Callable[..., HexStr]
    extra_data: ExtraData | None = None
