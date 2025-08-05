from dataclasses import dataclass, field
from typing import Optional

from story_protocol_python_sdk.utils.constants import ZERO_HASH


@dataclass
class IpMetadataForWorkflow:
    """Metadata for IP workflow operations."""

    # The URI of the metadata for the IP
    ip_metadata_uri: str = ""

    # The hash of the metadata for the IP
    ip_metadata_hash: str = field(default=ZERO_HASH)

    # The URI of the metadata for the NFT
    nft_metadata_uri: str = ""

    # The hash of the metadata for the IP NFT
    nft_metadata_hash: str = field(default=ZERO_HASH)


def get_ip_metadata_for_workflow(
    ip_metadata: Optional[dict] = None,
) -> tuple[str, str, str, str]:
    """
    Get IP metadata for workflow with default values.

    Args:
        ip_metadata: Optional partial metadata dictionary

    Returns:
        IpMetadataForWorkflow: Complete metadata with defaults
    """
    if ip_metadata is None:
        ip_metadata = {}

    return (
        ip_metadata.get("ip_metadata_uri", ""),
        ip_metadata.get("ip_metadata_hash", ZERO_HASH),
        ip_metadata.get("nft_metadata_uri", ""),
        ip_metadata.get("nft_metadata_hash", ZERO_HASH),
    )
