# src/story_protcol_python_sdk/resources/Royalty.py

from web3 import Web3

from story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client import (
    IPAccountImplClient,
)
from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import (
    IPAssetRegistryClient,
)
from story_protocol_python_sdk.abi.IpRoyaltyVaultImpl.IpRoyaltyVaultImpl_client import (
    IpRoyaltyVaultImplClient,
)
from story_protocol_python_sdk.abi.MockERC20.MockERC20_client import MockERC20Client
from story_protocol_python_sdk.abi.Multicall3.Multicall3_client import Multicall3Client
from story_protocol_python_sdk.abi.RoyaltyModule.RoyaltyModule_client import (
    RoyaltyModuleClient,
)
from story_protocol_python_sdk.abi.RoyaltyPolicyLAP.RoyaltyPolicyLAP_client import (
    RoyaltyPolicyLAPClient,
)
from story_protocol_python_sdk.abi.RoyaltyPolicyLRP.RoyaltyPolicyLRP_client import (
    RoyaltyPolicyLRPClient,
)
from story_protocol_python_sdk.abi.RoyaltyWorkflows.RoyaltyWorkflows_client import (
    RoyaltyWorkflowsClient,
)
from story_protocol_python_sdk.abi.WrappedIP.WrappedIP_client import WrappedIPClient
from story_protocol_python_sdk.utils.constants import WIP_TOKEN_ADDRESS
from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction
from story_protocol_python_sdk.utils.validation import (
    validate_address,
    validate_addresses,
)


class Royalty:
    """
    A class to claim and pay royalties on Story Protocol.

    :param web3 Web3: An instance of Web3.
    :param account: The account to use for transactions.
    :param chain_id int: The ID of the blockchain network.
    """

    def __init__(self, web3: Web3, account, chain_id: int):
        self.web3 = web3
        self.account = account
        self.chain_id = chain_id

        self.ip_asset_registry_client = IPAssetRegistryClient(web3)
        self.royalty_policy_lap_client = RoyaltyPolicyLAPClient(web3)
        self.royalty_module_client = RoyaltyModuleClient(web3)
        self.ip_royalty_vault_client = IpRoyaltyVaultImplClient(web3)
        self.royalty_workflows_client = RoyaltyWorkflowsClient(web3)
        self.ip_account_impl_client = IPAccountImplClient(web3)
        self.mock_erc20_client = MockERC20Client(web3)
        self.royalty_policy_lrp_client = RoyaltyPolicyLRPClient(web3)
        self.wrapped_ip_client = WrappedIPClient(web3)
        self.multicall3_client = Multicall3Client(web3)

    def get_royalty_vault_address(self, ip_id: str) -> str:
        """
        Get the royalty vault address for a given IP ID.

        :param ip_id str: The IP ID.
        :return str: The respective royalty vault address.
        """
        is_registered = self.ip_asset_registry_client.isRegistered(ip_id)
        if not is_registered:
            raise ValueError(f"The IP with id {ip_id} is not registered.")

        return self.royalty_module_client.ipRoyaltyVaults(ip_id)

    def claimable_revenue(
        self, royalty_vault_ip_id: str, claimer: str, token: str
    ) -> int:
        """
        Calculates the amount of revenue token claimable by a token holder.

        :param royalty_vault_ip_id str: The id of the royalty vault.
        :param claimer str: The address of the royalty token holder.
        :param token str: The revenue token to claim.
        :return int: The claimable revenue amount.
        """
        try:
            proxy_address = self.get_royalty_vault_address(royalty_vault_ip_id)
            ip_royalty_vault_client = IpRoyaltyVaultImplClient(
                self.web3, contract_address=proxy_address
            )

            claimable_revenue = ip_royalty_vault_client.claimableRevenue(
                claimer=claimer, token=token
            )

            return claimable_revenue

        except Exception as e:
            raise e

    def pay_royalty_on_behalf(
        self,
        receiver_ip_id: str,
        payer_ip_id: str,
        token: str,
        amount: int,
        tx_options: dict | None = None,
    ) -> dict:
        """
        Allows the function caller to pay royalties to the receiver IP asset on behalf of the payer IP asset.

        :param receiver_ip_id str: The IP ID that receives the royalties.
        :param payer_ip_id str: The ID of the IP asset that pays the royalties.
        :param token str: The token to use to pay the royalties.
        :param amount int: The amount to pay.
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash.
        """
        try:
            is_receiver_registered = self.ip_asset_registry_client.isRegistered(
                receiver_ip_id
            )
            if not is_receiver_registered:
                raise ValueError(
                    f"The receiver IP with id {receiver_ip_id} is not registered."
                )

            is_payer_registered = self.ip_asset_registry_client.isRegistered(
                payer_ip_id
            )
            if not is_payer_registered:
                raise ValueError(
                    f"The payer IP with id {payer_ip_id} is not registered."
                )

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.royalty_module_client.build_payRoyaltyOnBehalf_transaction,
                receiver_ip_id,
                payer_ip_id,
                token,
                amount,
                tx_options=tx_options,
            )

            return {"tx_hash": response["tx_hash"]}

        except Exception as e:
            raise e

    def claim_all_revenue(
        self,
        ancestor_ip_id: str,
        claimer: str,
        child_ip_ids: list,
        royalty_policies: list,
        currency_tokens: list,
        claim_options: dict | None = None,
        tx_options: dict | None = None,
    ) -> dict:
        """
        Claims all revenue from the child IPs of an ancestor IP, then transfer all claimed tokens to the wallet if the wallet owns the IP or is the claimer. If claimed token is `WIP(Wrapped IP)`, it will also be converted back to native tokens.

        Even if there are no child IPs, you must still populate `currency_tokens` with the token addresses you wish to claim. This is required for the claim operation to know which token balances to process.
             :param ancestor_ip_id str: The IP ID of the ancestor.
             :param claimer str: The address of the claimer.
             :param child_ip_ids list: List of child IP IDs.
             :param royalty_policies list: List of royalty policy addresses.
             :param currency_tokens list: List of currency token addresses.
             :param claim_options dict: [Optional] Options for `auto_transfer_all_claimed_tokens_from_ip` and `auto_unwrap_ip_tokens`. Default values are True.
             :param tx_options dict: [Optional] The transaction options.
             :return dict: A dictionary with transaction details and claimed tokens.
        """
        try:

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.royalty_workflows_client.build_claimAllRevenue_transaction,
                validate_address(ancestor_ip_id),
                validate_address(claimer),
                validate_addresses(child_ip_ids),
                validate_addresses(royalty_policies),
                validate_addresses(currency_tokens),
                tx_options=tx_options,
            )

            tx_hashes = [response["tx_hash"]]

            # Determine if the claimer is an IP owned by the wallet.
            owns_claimer, is_claimer_ip, ip_account = self._get_claimer_info(claimer)
            claimed_tokens = self._parse_tx_revenue_token_claimed_event(
                response["tx_receipt"]
            )

            auto_transfer = (
                claim_options.get("auto_transfer_all_claimed_tokens_from_ip", True)
                if claim_options
                else True
            )
            auto_unwrap = (
                claim_options.get("auto_unwrap_ip_tokens", True)
                if claim_options
                else True
            )

            if auto_transfer and is_claimer_ip and owns_claimer:
                hashes = self._transfer_claimed_tokens_from_ip_to_wallet(
                    ip_account, claimed_tokens
                )
                tx_hashes.extend(hashes)

            if auto_unwrap and owns_claimer:
                hashes = self._unwrap_claimed_tokens_from_ip_to_wallet(claimed_tokens)
                tx_hashes.extend(hashes)

            return {
                "receipt": response["tx_receipt"],
                "claimed_tokens": claimed_tokens,
                "tx_hashes": tx_hashes,
            }

        except Exception as e:
            raise ValueError(f"Failed to claim all revenue: {str(e)}")

    def batch_claim_all_revenue(
        self,
        ancestor_ips: list[dict],
        claim_options: dict | None = None,
        options: dict | None = None,
        tx_options: dict | None = None,
    ) -> dict:
        """
        Batch claims all revenue from the child IPs of multiple ancestor IPs.
        If multicall is disabled, it will call claim_all_revenue for each ancestor IP.
        Then transfer all claimed tokens to the wallet if the wallet owns the IP or is the claimer.
        If claimed token is WIP, it will also be converted back to native tokens.

        Even if there are no child IPs, you must still populate `currency_tokens` in each ancestor IP
        with the token addresses you wish to claim. This is required for the claim operation to know which
        token balances to process.

        :param ancestor_ips list[dict]: List of ancestor IP configurations, each containing:
            :param ip_id str: The IP ID of the ancestor.
            :param claimer str: The address of the claimer.
            :param child_ip_ids list: List of child IP IDs.
            :param royalty_policies list: List of royalty policy addresses.
            :param currency_tokens list: List of currency token addresses.
        :param claim_options dict: [Optional] Options for auto_transfer_all_claimed_tokens_from_ip and auto_unwrap_ip_tokens. Default values are True.
        :param options dict: [Optional] Options for use_multicall_when_possible. Default is True.
        :param tx_options dict: [Optional] Transaction options.
        :return dict: Dictionary with transaction hashes, receipts, and claimed tokens.
            :return tx_hashes list[str]: List of transaction hashes.
            :return receipts list[dict]: List of transaction receipts.
            :return claimed_tokens list[dict]: Aggregated list of claimed tokens.
        """
        try:
            tx_hashes = []
            receipts = []
            claimed_tokens = []

            use_multicall = (
                options.get("use_multicall_when_possible", True) if options else True
            )

            # If only 1 ancestor IP or multicall is disabled, call claim_all_revenue for each
            if len(ancestor_ips) == 1 or not use_multicall:
                for ancestor_ip in ancestor_ips:
                    result = self.claim_all_revenue(
                        ancestor_ip_id=ancestor_ip["ip_id"],
                        claimer=ancestor_ip["claimer"],
                        child_ip_ids=ancestor_ip["child_ip_ids"],
                        royalty_policies=ancestor_ip["royalty_policies"],
                        currency_tokens=ancestor_ip["currency_tokens"],
                        claim_options={
                            "auto_transfer_all_claimed_tokens_from_ip": False,
                            "auto_unwrap_ip_tokens": False,
                        },
                        tx_options=tx_options,
                    )
                    tx_hashes.extend(result["tx_hashes"])
                    receipts.append(result["receipt"])
                    if result.get("claimed_tokens"):
                        claimed_tokens.extend(result["claimed_tokens"])
            else:
                # Batch claimAllRevenue calls into a single multicall
                encoded_txs = []
                for ancestor_ip in ancestor_ips:
                    encoded_data = self.royalty_workflows_client.contract.functions.claimAllRevenue(
                        validate_address(ancestor_ip["ip_id"]),
                        validate_address(ancestor_ip["claimer"]),
                        validate_addresses(ancestor_ip["child_ip_ids"]),
                        validate_addresses(ancestor_ip["royalty_policies"]),
                        validate_addresses(ancestor_ip["currency_tokens"]),
                    )._encode_transaction_data()
                    encoded_txs.append(encoded_data)

                response = build_and_send_transaction(
                    self.web3,
                    self.account,
                    self.royalty_workflows_client.build_multicall_transaction,
                    encoded_txs,
                    tx_options=tx_options,
                )
                tx_hashes.append(response["tx_hash"])
                receipts.append(response["tx_receipt"])

                # Parse claimed tokens from the receipt
                claimed_token_logs = self._parse_tx_revenue_token_claimed_event(
                    response["tx_receipt"]
                )
                claimed_tokens.extend(claimed_token_logs)

            # Aggregate claimed tokens by claimer and token address
            aggregated_claimed_tokens = {}
            for token in claimed_tokens:
                key = f"{token['claimer']}_{token['token']}"
                if key not in aggregated_claimed_tokens:
                    aggregated_claimed_tokens[key] = dict(token)
                else:
                    aggregated_claimed_tokens[key]["amount"] += token["amount"]

            aggregated_claimed_tokens = list(aggregated_claimed_tokens.values())

            # Get unique claimers
            claimers = list(set(ancestor_ip["claimer"] for ancestor_ip in ancestor_ips))

            auto_transfer = (
                claim_options.get("auto_transfer_all_claimed_tokens_from_ip", True)
                if claim_options
                else True
            )
            auto_unwrap = (
                claim_options.get("auto_unwrap_ip_tokens", True)
                if claim_options
                else True
            )

            wip_claimable_amounts = 0

            for claimer in claimers:
                owns_claimer, is_claimer_ip, ip_account = self._get_claimer_info(
                    claimer
                )

                # If ownsClaimer is false, skip
                if not owns_claimer:
                    continue

                filter_claimed_tokens = [
                    token
                    for token in aggregated_claimed_tokens
                    if token["claimer"] == claimer
                ]

                # Transfer claimed tokens from IP to wallet if wallet owns IP
                if auto_transfer and is_claimer_ip and owns_claimer:
                    hashes = self._transfer_claimed_tokens_from_ip_to_wallet(
                        ip_account, filter_claimed_tokens
                    )
                    tx_hashes.extend(hashes)

                # Sum up the amount of WIP tokens claimed
                for token in filter_claimed_tokens:
                    if token["token"] == WIP_TOKEN_ADDRESS:
                        wip_claimable_amounts += token["amount"]

            # Unwrap WIP tokens if needed
            if wip_claimable_amounts > 0 and auto_unwrap:
                hashes = self._unwrap_claimed_tokens_from_ip_to_wallet(
                    [
                        {
                            "token": WIP_TOKEN_ADDRESS,
                            "amount": wip_claimable_amounts,
                            "claimer": self.account.address,
                        }
                    ]
                )
                tx_hashes.extend(hashes)

            return {
                "receipts": receipts,
                "claimed_tokens": aggregated_claimed_tokens,
                "tx_hashes": tx_hashes,
            }

        except Exception as e:
            error_msg = str(e).replace("Failed to claim all revenue: ", "").strip()
            raise ValueError(f"Failed to batch claim all revenue: {error_msg}")

    def transfer_to_vault(
        self,
        ip_id: str,
        ancestor_ip_id: str,
        token: str,
        royalty_policy: str = "LAP",
        tx_options: dict | None = None,
    ) -> dict:
        """
        Transfers to vault an amount of revenue tokens claimable via a royalty policy.

        :param ip_id str: The IP ID.
        :param ancestor_ip_id str: The ancestor IP ID.
        :param token str: The token address.
        :param royalty_policy str: The royalty policy to use ("LAP" or "LRP").
        :param tx_options dict: [Optional] Transaction options.
        :return dict: A dictionary with the transaction hash and receipt.
        """
        try:
            if not self.web3.is_address(token):
                raise ValueError(f'Token address "{token}" is invalid.')
            royalty_policy_client: (
                RoyaltyPolicyLAPClient | RoyaltyPolicyLRPClient | None
            ) = None
            # Determine which royalty policy to use
            if royalty_policy == "LAP":
                royalty_policy_client = self.royalty_policy_lap_client
            elif royalty_policy == "LRP":
                royalty_policy_client = self.royalty_policy_lrp_client
            else:
                # If it's a custom address
                if not self.web3.is_address(royalty_policy):
                    raise ValueError(
                        f'Royalty policy address "{royalty_policy}" is invalid.'
                    )
                royalty_policy_client = (
                    self.royalty_policy_lap_client
                )  # Same ABI for all royalty policies
                royalty_policy_client.contract.address = self.web3.to_checksum_address(
                    royalty_policy
                )

            response = build_and_send_transaction(
                self.web3,
                self.account,
                royalty_policy_client.build_transferToVault_transaction,
                ip_id,
                ancestor_ip_id,
                token,
                tx_options=tx_options,
            )

            return {"tx_hash": response["tx_hash"], "receipt": response["tx_receipt"]}

        except Exception as e:
            raise ValueError(f"Failed to transfer to vault: {str(e)}")

    def _get_claimer_info(self, claimer):
        """
        Get information about the claimer address.

        :param claimer str: The claimer address to check
        :return dict: Dictionary containing:
            - owns_claimer (bool): Whether the wallet owns the claimer
            - is_claimer_ip (bool): Whether the claimer is an IP
            - ip_account (IpAccountImplClient): IP account client if claimer is an IP
        """
        is_claimer_ip = self.ip_asset_registry_client.isRegistered(claimer)
        owns_claimer = claimer == self.account.address
        ip_account = None
        if is_claimer_ip:
            ip_account = IPAccountImplClient(self.web3, contract_address=claimer)
            ip_owner = ip_account.owner()
            owns_claimer = ip_owner == self.account.address

        return owns_claimer, is_claimer_ip, ip_account

    def _transfer_claimed_tokens_from_ip_to_wallet(
        self, ip_account, claimed_tokens: list
    ) -> list:
        """
        Transfer claimed tokens from an IP account to the wallet.

        :param ancestor_ip_id str: The IP ID of the ancestor.
        :param ip_account IpAccountImplClient: The IP account to transfer from
        :param claimed_tokens list: List of claimed tokens, each containing token address and amount
        :return list: List of transaction hashes
        """
        calls = []

        for claimed_token in claimed_tokens:
            token = claimed_token["token"]
            amount = claimed_token["amount"]

            if amount <= 0:
                continue

            # Build ERC20 transfer function data
            transfer_data = self.mock_erc20_client.contract.encode_abi(
                abi_element_identifier="transfer", args=[self.account.address, amount]
            )
            calls.append(
                {
                    "target": token,
                    "value": 0,
                    "data": transfer_data,
                }
            )
        if len(calls) > 0:
            response = build_and_send_transaction(
                self.web3,
                self.account,
                ip_account.build_executeBatch_transaction,
                calls,
                0,
            )
            return [response["tx_hash"]]
        return []

    def _parse_tx_revenue_token_claimed_event(self, tx_receipt: dict) -> list:
        """
        Parse the RevenueTokenClaimed events from a transaction receipt.

        :param tx_receipt dict: The transaction receipt.
        :return list: List of claimed tokens with claimer address, token address and amount.
        """
        event_signature = Web3.keccak(
            text="RevenueTokenClaimed(address,address,uint256)"
        ).hex()
        claimed_tokens = []
        for log in tx_receipt.get("logs", []):
            if log["topics"][0].hex() == event_signature:
                event_result = self.ip_royalty_vault_client.contract.events.RevenueTokenClaimed.process_log(
                    log
                )[
                    "args"
                ]
                claimed_tokens.append(event_result)

        return claimed_tokens

    def _unwrap_claimed_tokens_from_ip_to_wallet(self, claimed_tokens: list) -> list:
        """
        Unwrap claimed tokens from an IP account to the wallet.

        :param claimed_tokens list: List of claimed tokens, each containing token address and amount
        :return list: List of transaction hashes
        """
        tx_hashes: list[str] = []

        # Filter for WIP tokens
        wip_tokens = [
            token for token in claimed_tokens if token["token"] == WIP_TOKEN_ADDRESS
        ]

        if len(wip_tokens) > 1:
            raise ValueError("Multiple WIP tokens found in the claimed tokens.")

        if not wip_tokens:
            return tx_hashes

        wip_token = wip_tokens[0]
        if wip_token["amount"] <= 0:
            return tx_hashes

        # Withdraw WIP tokens
        response = build_and_send_transaction(
            self.web3,
            self.account,
            self.wrapped_ip_client.build_withdraw_transaction,
            wip_token["amount"],
        )

        tx_hashes.append(response["tx_hash"])
        return tx_hashes
