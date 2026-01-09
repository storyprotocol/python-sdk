"""Registration utilities for IP asset operations."""

from ens.ens import Address
from web3 import Web3

from story_protocol_python_sdk.abi.SPGNFTImpl.SPGNFTImpl_client import SPGNFTImplClient


def get_public_minting(spg_nft_contract: Address, web3: Web3) -> bool:
    """
    Check if SPG NFT contract has public minting enabled.

    Args:
        spg_nft_contract: The address of the SPG NFT contract.
        web3: Web3 instance.

    Returns:
        True if public minting is enabled, False otherwise.
    """
    spg_client = SPGNFTImplClient(
        web3, contract_address=Web3.to_checksum_address(spg_nft_contract)
    )
    return spg_client.publicMinting()
