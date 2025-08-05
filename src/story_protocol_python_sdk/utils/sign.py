from datetime import datetime

from eth_abi.abi import encode
from eth_account import Account
from eth_account.messages import encode_typed_data
from web3 import Web3

from story_protocol_python_sdk.abi.AccessController.AccessController_client import (
    AccessControllerClient,
)
from story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client import (
    IPAccountImplClient,
)
from story_protocol_python_sdk.types.utils.sign import (
    PermissionSignatureArgs,
    SignatureArgs,
)
from story_protocol_python_sdk.utils.constants import DEFAULT_FUNCTION_SELECTOR
from story_protocol_python_sdk.utils.validation import validate_address

# ABI for access controller contract
ACCESS_CONTROLLER_ABI = [
    {
        "name": "setTransientPermission",
        "type": "function",
        "inputs": [
            {"name": "ipAccount", "type": "address"},
            {"name": "signer", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "func", "type": "bytes4"},
            {"name": "permission", "type": "uint8"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "name": "setBatchTransientPermissions",
        "type": "function",
        "inputs": [
            {
                "name": "permissions",
                "type": "tuple[]",
                "components": [
                    {"name": "ipAccount", "type": "address"},
                    {"name": "signer", "type": "address"},
                    {"name": "to", "type": "address"},
                    {"name": "func", "type": "bytes4"},
                    {"name": "permission", "type": "uint8"},
                ],
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
]


class Sign:
    def __init__(self, web3: Web3, chain_id: int, account):
        self.web3 = web3
        self.chain_id = chain_id
        self.account = account

        self.ip_account_client = IPAccountImplClient(web3)
        self.access_controller_client = AccessControllerClient(web3)

    def get_signature(
        self,
        args: SignatureArgs,
    ) -> tuple[str, str]:
        """
        Get the signature.

        :param args SignatureArgs: The signature arguments containing state, to, encode_data, verifying_contract, and deadline.
        :return dict: A dictionary containing the signature and nonce.
        """
        execute_data = self.ip_account_client.contract.encode_abi(
            abi_element_identifier="execute", args=[args.to, 0, args.encode_data]
        )

        nonce = Web3.keccak(
            encode(
                ["bytes32", "bytes"],
                [
                    args.state,
                    Web3.to_bytes(hexstr=execute_data),
                ],
            )
        )

        domain_data = {
            "name": "Story Protocol IP Account",
            "version": "1",
            "chainId": self.chain_id,
            "verifyingContract": args.verifying_contract,
        }

        message_types = {
            "Execute": [
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "data", "type": "bytes"},
                {"name": "nonce", "type": "bytes32"},
                {"name": "deadline", "type": "uint256"},
            ],
        }

        message_data = {
            "to": args.to,
            "value": 0,
            "data": args.encode_data,
            "nonce": nonce,
            "deadline": args.deadline,
        }

        signable_message = encode_typed_data(domain_data, message_types, message_data)
        signed_message = Account.sign_message(signable_message, self.account.key)

        return ("0x" + signed_message.signature.hex(), nonce)

    def get_deadline(self, deadline: int = None) -> int:
        """
        Calculate the deadline for a transaction.

        :param deadline int: [Optional] The deadline value in milliseconds.
        :return int: The calculated deadline in milliseconds.
        """
        current_timestamp = int(datetime.now().timestamp() * 1000)

        if deadline is not None:
            if not isinstance(deadline, int) or deadline < 0:
                raise ValueError("Invalid deadline value.")
            return current_timestamp + deadline
        else:
            return current_timestamp + 1000

    def get_permission_signature(
        self, param: PermissionSignatureArgs
    ) -> tuple[str, str]:
        """
        Get permission signature for setting transient permissions.

        Args:
            param: Permission signature request containing all necessary parameters

        Returns:
            SignatureResponse: Contains the signature and nonce
        """

        ip_id = param.ip_id
        deadline = param.deadline
        state = param.state
        permissions = param.permissions
        access_address = self.access_controller_client.contract.address
        is_batch_permission_function = len(permissions) >= 2

        function_name = (
            "setBatchTransientPermissions"
            if is_batch_permission_function
            else "setTransientPermission"
        )

        if is_batch_permission_function:
            args = [
                [
                    {
                        "ipAccount": validate_address(item.ip_id),
                        "signer": validate_address(item.signer),
                        "to": validate_address(item.to),
                        "func": Web3.keccak(
                            text=item.func or DEFAULT_FUNCTION_SELECTOR
                        )[:4],
                        "permission": item.permission.value,
                    }
                    for item in permissions
                ]
            ]
        else:
            permission = permissions[0]
            args = [
                validate_address(permission.ip_id),
                validate_address(permission.signer),
                validate_address(permission.to),
                Web3.keccak(text=permission.func or DEFAULT_FUNCTION_SELECTOR)[:4],
                permission.permission.value,
            ]

        data = self.access_controller_client.contract.encode_abi(
            abi_element_identifier=function_name, args=args
        )

        return self.get_signature(
            SignatureArgs(
                state=state,
                to=access_address,
                encode_data=data,
                verifying_contract=ip_id,
                deadline=deadline,
            ),
        )
