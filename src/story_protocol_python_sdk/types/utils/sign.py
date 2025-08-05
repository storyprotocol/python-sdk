from dataclasses import dataclass
from typing import List, Optional

from story_protocol_python_sdk.types.resources.permission import SetPermissionsRequest
from story_protocol_python_sdk.types.types import Address, Hash, Hex


@dataclass
class SignatureArgs:
    """Arguments for signature generation."""

    state: Hash  # hex string representing state
    to: Address  # recipient address
    encode_data: bytes
    verifying_contract: Address
    deadline: Optional[int]


@dataclass
class PermissionSignatureArgs:
    """Arguments for permission signature generation."""

    ip_id: Address  # IP asset address
    state: Hex  # hex string representing state
    permissions: List[SetPermissionsRequest]
    deadline: Optional[int]
