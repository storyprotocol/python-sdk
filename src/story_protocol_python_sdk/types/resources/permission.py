from dataclasses import dataclass, field
from enum import IntEnum

from story_protocol_python_sdk.types.types import Address

DEFAULT_FUNCTION_SELECTOR = "0x00000000"


class AccessPermission(IntEnum):
    """
    Permission level enum.

    This enum represents the different permission levels that can be granted
    to a signer for executing transactions on behalf of an IP Account.
    """

    # ABSTAIN means having not enough information to make decision at
    # current level, deferred decision to up.
    ABSTAIN = 0

    # ALLOW means the permission is granted to transaction signer to call the function.
    ALLOW = 1

    # DENY means the permission is denied to transaction signer to call the function.
    DENY = 2


@dataclass
class SetPermissionsRequest:
    """Request to set permissions for an IP Account.

    This dataclass represents the parameters needed to grant permission
    to a signer to execute transactions on behalf of an IP Account.
    """

    # The IP ID that grants the permission for signer
    ip_id: Address

    # The address that will be granted permission to execute transactions.
    # This address will be able to call functions on 'to' on behalf of the IP Account
    signer: Address

    # The address that can be called by the signer (currently only modules can be 'to')
    to: Address

    # The new permission level of AccessPermission
    permission: AccessPermission

    # The function selector string of 'to' that can be called by the signer on behalf of the IP Account.
    # By default, it allows all functions.
    func: str = field(default=DEFAULT_FUNCTION_SELECTOR)
