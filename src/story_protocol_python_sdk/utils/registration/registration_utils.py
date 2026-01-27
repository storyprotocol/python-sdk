"""Registration utilities for IP asset operations."""

from ens.ens import Address, HexStr
from eth_account.signers.local import LocalAccount
from web3 import Web3

from story_protocol_python_sdk.abi.Multicall3.Multicall3_client import Multicall3Client
from story_protocol_python_sdk.types.resource.IPAsset import IPRoyaltyVault
from story_protocol_python_sdk.types.utils import (
    AggregatedRequestData,
    ExtraData,
    TransformedRegistrationRequest,
)
from story_protocol_python_sdk.utils.registration.transform_registration_request import (
    transform_distribute_royalty_tokens_request,
)
from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction


def aggregate_multicall_requests(
    requests: list[TransformedRegistrationRequest],
    is_use_multicall3: bool,
    web3: Web3,
) -> dict[Address, AggregatedRequestData]:
    """
    Aggregate multicall requests by grouping them by target address.

    Groups requests that should be sent to the same multicall address together,
    collecting their encoded transaction data and method references.
    """
    aggregated_requests: dict[Address, AggregatedRequestData] = {}
    multicall3_client = Multicall3Client(web3)

    for request in requests:
        # Determine the target address for this request
        target_address = (
            multicall3_client.contract.address
            if request.is_use_multicall3 and is_use_multicall3
            else request.workflow_address
        )

        # Initialize entry if it doesn't exist
        if target_address not in aggregated_requests:
            aggregated_requests[target_address] = {
                "call_data": [],
                "license_terms_data": [],
                "method_reference": (
                    multicall3_client.build_aggregate3_transaction
                    if target_address == multicall3_client.contract.address
                    else request.workflow_multicall_reference
                ),
            }
        if target_address == multicall3_client.contract.address:
            aggregated_requests[target_address]["call_data"].append(
                {
                    "target": request.workflow_address,
                    "allowFailure": False,
                    "value": 0,
                    "callData": request.encoded_tx_data,
                }
            )
        else:
            aggregated_requests[target_address]["call_data"].append(
                request.encoded_tx_data
            )
        license_terms_data = (
            request.extra_data.get("license_terms_data") or []
            if request.extra_data is not None
            else []
        )
        aggregated_requests[target_address]["license_terms_data"].append(
            license_terms_data
        )

    return aggregated_requests


def prepare_distribute_royalty_tokens_requests(
    extra_data_list: list[ExtraData],
    web3: Web3,
    ip_registered: list[dict[str, int | Address]],
    royalty_vault: list[dict[str, Address]],
    account: LocalAccount,
    chain_id: int,
) -> tuple[list[TransformedRegistrationRequest], list[IPRoyaltyVault]]:
    if not extra_data_list:
        return [], []
    transformed_requests: list[TransformedRegistrationRequest] = []
    matching_vaults: list[IPRoyaltyVault] = []
    for extra_data in extra_data_list:
        # Find matching IP registration
        ip_registered_match = next(
            (
                x
                for x in ip_registered
                if x["tokenContract"] == extra_data["nft_contract"]
                and x["tokenId"] == extra_data["token_id"]
            ),
            None,
        )
        if not ip_registered_match:
            continue

        ip_id = ip_registered_match["ipId"]

        # Find matching royalty vault
        matching_vault = next(
            (x for x in royalty_vault if x["ipId"] == ip_id),
            None,
        )
        if not matching_vault:
            continue

        ip_royalty_vault = matching_vault["ipRoyaltyVault"]
        matching_vaults.append(
            IPRoyaltyVault(ip_id=ip_id, royalty_vault=ip_royalty_vault)
        )
        transformed_request = transform_distribute_royalty_tokens_request(
            ip_id=ip_id,
            royalty_vault=ip_royalty_vault,
            deadline=extra_data["deadline"],
            web3=web3,
            account=account,
            chain_id=chain_id,
            royalty_shares=extra_data["royalty_shares"],
            total_amount=extra_data["royalty_total_amount"],
        )
        transformed_requests.append(transformed_request)
    return transformed_requests, matching_vaults


def send_transactions(
    transformed_requests: list[TransformedRegistrationRequest],
    is_use_multicall3: bool,
    web3: Web3,
    account: LocalAccount,
    tx_options: dict | None = None,
) -> tuple[list[dict[str, HexStr | dict]], dict[Address, AggregatedRequestData]]:
    aggregated_requests: dict[Address, AggregatedRequestData] = (
        aggregate_multicall_requests(
            requests=transformed_requests,
            is_use_multicall3=is_use_multicall3,
            web3=web3,
        )
    )
    tx_results: list[dict[str, HexStr | dict]] = []
    for request_data in aggregated_requests.values():
        response = build_and_send_transaction(
            web3,
            account,
            request_data["method_reference"],
            request_data["call_data"],
            tx_options=tx_options,
        )
        tx_results.append(
            {
                "tx_hash": response["tx_hash"],
                "tx_receipt": response["tx_receipt"],
            }
        )
    return tx_results, aggregated_requests
