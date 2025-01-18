# src/story_protcol_python_sdk/utils/sign.py

from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_abi.abi import encode
from datetime import datetime

from story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client import IPAccountImplClient
from story_protocol_python_sdk.abi.AccessController.AccessController_client import AccessControllerClient

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

class Sign:
    def __init__(self, web3: Web3, chain_id: int, account):
        self.web3 = web3
        self.chain_id = chain_id
        self.account = account

        self.ip_account_client = IPAccountImplClient(web3)
        self.access_controller_client = AccessControllerClient(web3)

    def get_signature(self, state: str, to: str, encode_data: bytes, verifying_contract: str, deadline: int) -> dict:
        """
        Get the signature.

        :param state str: The IP Account's state.
        :param to str: The recipient address.
        :param encode_data bytes: The encoded data.
        :param verifying_contract str: The verifying contract address.
        :param deadline int: The deadline for the signature in milliseconds.
        :return dict: A dictionary containing the signature and nonce.
        """
        try:
            execute_data = self.ip_account_client.contract.encode_abi(
                abi_element_identifier="execute",
                args=[
                    to,
                    0,
                    encode_data
                ]
            )

            #expected_state = nonce
            expected_state = Web3.keccak(
                encode(
                    ["bytes32", "bytes"],
                    [
                        state,  # Current state (nonce)
                        Web3.to_bytes(hexstr=execute_data)  # Convert hex string to bytes
                    ]
                )
            )

            domain_data = {
                "name": "Story Protocol IP Account",
                "version": "1",
                "chainId": self.chain_id,
                "verifyingContract": verifying_contract,
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
                "to": to,
                "value": 0,
                "data": encode_data,
                "nonce": expected_state,
                "deadline": deadline,
            }

            signable_message = encode_typed_data(domain_data, message_types, message_data)
            signed_message = Account.sign_message(signable_message, self.account.key)

            return {
                "signature": signed_message.signature.hex(),
                "nonce": expected_state
            }

        except Exception as e:
            raise e
        
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
        
    def get_permission_signature(self, ip_id: str, deadline: int, permissions: list, permission_func: str = "setPermission", state: str = None) -> dict:
        """
        Get the signature for setting permissions.

        :param ip_id str: The IP ID
        :param deadline int: The deadline
        :param permissions list: The permissions
        :param permission_func str: The permission function (defaults to "setPermission")
        :param state str: The state
        :return dict: The signature response
        """
        try:
            # Get permission function name
            permission_function = permission_func if permission_func else "setPermission"

            # Get access controller address for chain
            access_address = self.access_controller_client.contract.address

            if permission_function == "setPermission":
                # Encode single permission
                encode_data = self.access_controller_client.contract.encode_abi(
                    abi_element_identifier="setPermission",
                    args=[
                        self.web3.to_checksum_address(permissions[0]['ipId']),
                        self.web3.to_checksum_address(permissions[0]['signer']),
                        self.web3.to_checksum_address(permissions[0]['to']),
                        Web3.keccak(text=permissions[0]['func'])[:4] if permissions[0].get('func') else b'\x00\x00\x00\x00',
                        permissions[0]['permission']
                    ]
                )
            else:
                # Encode multiple permissions
                formatted_permissions = [{
                    'ipAccount': self.web3.to_checksum_address(p['ipId']),
                    'signer': self.web3.to_checksum_address(p['signer']),
                    'to': self.web3.to_checksum_address(p['to']),
                    'func': Web3.keccak(text=p[0]['func'])[:4].hex() if p[0].get('func') else "0x00000000",
                    'permission': p['permission']
                } for p in permissions]

                encode_data = self.access_controller_client.contract.encode_abi(
                    abi_element_identifier=permission_function,
                    args=[formatted_permissions]
                )

            return self.get_signature(
                state=state,
                to=access_address,
                encode_data=encode_data,
                verifying_contract=ip_id,
                deadline=deadline
            )

        except Exception as e:
            raise e
