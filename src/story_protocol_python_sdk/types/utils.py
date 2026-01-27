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
