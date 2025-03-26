from web3 import Web3
from story_protocol_python_sdk.abi.DisputeModule.DisputeModule_client import DisputeModuleClient
from story_protocol_python_sdk.abi.ArbitrationPolicyUMA.ArbitrationPolicyUMA_client import ArbitrationPolicyUMAClient
from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction
from story_protocol_python_sdk.utils.ipfs import convert_cid_to_hash_ipfs
from eth_abi.abi import encode
from story_protocol_python_sdk.resources.WIP import WIP
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

class Dispute:
    """
    A class to manage disputes on Story Protocol.

    :param web3 Web3: An instance of Web3.
    :param account: The account to use for transactions.
    :param chain_id int: The ID of the blockchain network.
    """
    def __init__(self, web3: Web3, account, chain_id: int):
        self.web3 = web3
        self.account = account
        self.chain_id = chain_id

        self.dispute_module_client = DisputeModuleClient(web3)
        self.arbitration_policy_uma_client = ArbitrationPolicyUMAClient(web3)
        self.WIP = WIP(web3, account, chain_id)
        
    def _validate_address(self, address: str) -> str:
        """
        Validates if a string is a valid Ethereum address.
        
        :param address str: The address to validate
        :return str: The validated address
        :raises ValueError: If the address is invalid
        """
        if not self.web3.is_address(address):
            raise ValueError(f"Invalid address: {address}.")
        return address

    def raiseDispute(self, target_ip_id: str, target_tag: str, cid: str, liveness: int, bond: int, tx_options: dict = None) -> dict:
        """
        Raises a dispute on a given IP ID.

        :param target_ip_id str: The IP ID being disputed.
        :param target_tag str: The tag to be applied to the IP.
        :param cid str: The IPFS CID containing dispute evidence.
        :param liveness int: The liveness period for the dispute.
        :param bond int: The bond amount for the dispute.
        :param tx_options dict: [Optional] Transaction options.
        :return dict: A dictionary containing the transaction hash and dispute ID.
        """
        try:
            # Validate target IP address
            target_ip_id = self._validate_address(target_ip_id)

            # Convert tag to bytes32
            tag_bytes = self.web3.to_hex(text=target_tag).ljust(66, '0')

            # Check if tag is whitelisted
            is_whitelisted = self.dispute_module_client.isWhitelistedDisputeTag(tag_bytes)
            if not is_whitelisted:
                raise ValueError(f"The target tag {target_tag} is not whitelisted.")

            # Get liveness bounds
            min_liveness = self.arbitration_policy_uma_client.minLiveness()
            max_liveness = self.arbitration_policy_uma_client.maxLiveness()
            if liveness < min_liveness or liveness > max_liveness:
                raise ValueError(f"Liveness must be between {min_liveness} and {max_liveness}.")

            # Check bond amount
            max_bonds = self.arbitration_policy_uma_client.maxBonds(
                token=self.web3.to_checksum_address("0x1514000000000000000000000000000000000000")
            )
            if bond > max_bonds:
                raise ValueError(f"Bond must be less than {max_bonds}.")

            deposit_response = self.WIP.deposit(
                amount=bond
            )

            # Convert CID to IPFS hash
            dispute_evidence_hash = convert_cid_to_hash_ipfs(cid)

            # Encode the data for the arbitration policy
            data = encode(
                ["uint64", "address", "uint256"],
                [
                    liveness,
                    "0x1514000000000000000000000000000000000000", 
                    bond
                ]
            )
            
            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.dispute_module_client.build_raiseDispute_transaction,
                target_ip_id,
                dispute_evidence_hash,
                tag_bytes,
                data,
                tx_options=tx_options
            )

            dispute_id = self._parse_tx_dispute_raised_event(response['txReceipt'])

            return {
                'txHash': response['txHash'],
                'disputeId': dispute_id if dispute_id else None
            }

        except Exception as e:
            raise ValueError(f"Failed to raise dispute: {str(e)}")

    def cancelDispute(self, dispute_id: int, data: str = "0x", tx_options: dict = None) -> dict:
        """
        Cancels an ongoing dispute.

        :param dispute_id int: The ID of the dispute to cancel.
        :param data str: [Optional] Additional data for the cancellation.
        :param tx_options dict: [Optional] Transaction options.
        :return dict: A dictionary containing the transaction hash.
        """
        try:
            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.dispute_module_client.build_cancelDispute_transaction,
                dispute_id,
                data,
                tx_options=tx_options
            )

            return {
                'txHash': response['txHash']
            }

        except Exception as e:
            raise ValueError(f"Failed to cancel dispute: {str(e)}")

    def resolveDispute(self, dispute_id: int, data: str, tx_options: dict = None) -> dict:
        """
        Resolves a dispute after it has been judged.

        :param dispute_id int: The ID of the dispute to resolve.
        :param data str: The resolution data.
        :param tx_options dict: [Optional] Transaction options.
        :return dict: A dictionary containing the transaction hash.
        """
        try:
            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.dispute_module_client.build_resolveDispute_transaction,
                dispute_id,
                data,
                tx_options=tx_options
            )

            return {
                'txHash': response['txHash']
            }

        except Exception as e:
            raise ValueError(f"Failed to resolve dispute: {str(e)}")

    def tagIfRelatedIpInfringed(self, infringement_tags: list, tx_options: dict = None) -> list:
        """
        Tags a derivative if a parent has been tagged with an infringement tag.

        :param infringement_tags list: List of dictionaries containing IP IDs and dispute IDs.
            :param ip_id str: The IP ID to tag.
            :param dispute_id int: The ID of the dispute.
        :param tx_options dict: [Optional] Transaction options.
        :return list: A list of transaction hashes.
        """
        try:
            tx_hashes = []
            
            for tag in infringement_tags:
                ip_id = self._validate_address(tag['ip_id'])
                
                response = build_and_send_transaction(
                    self.web3,
                    self.account,
                    self.dispute_module_client.build_tagIfRelatedIpInfringed_transaction,
                    ip_id,
                    tag['dispute_id'],
                    tx_options=tx_options
                )
                
                tx_hashes.append(response['txHash'])

            return tx_hashes

        except Exception as e:
            raise ValueError(f"Failed to tag related IP infringed: {str(e)}")

    def _parse_tx_dispute_raised_event(self, tx_receipt: dict) -> dict:
        """
        Parse the DisputeRaised event from a transaction receipt.

        :param tx_receipt dict: The transaction receipt.
        :return dict: The dispute ID from the event.
        """
        event_signature = self.web3.keccak(
            text="DisputeRaised(uint256,address,address,uint256,address,bytes32,bytes32,bytes)"
        ).hex()

        for log in tx_receipt['logs']:
            if log['topics'][0].hex() == event_signature:
                data = log['data']
                dispute_id = int.from_bytes(data[:32], byteorder='big')
                return dispute_id
        return None
