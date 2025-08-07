from typing import Optional

from eth_typing import HexStr

from story_protocol_python_sdk.types.common import IpMetadataForWorkflow
from story_protocol_python_sdk.utils.constants import ZERO_HASH


def get_ip_metadata_for_workflow(
    ip_metadata_uri: Optional[str],
    ip_metadata_hash: Optional[HexStr],
    nft_metadata_uri: Optional[str],
    nft_metadata_hash: Optional[HexStr],
) -> IpMetadataForWorkflow:
    return {
        "ip_metadata_uri": ip_metadata_uri or "",
        "ip_metadata_hash": ip_metadata_hash or ZERO_HASH,
        "nft_metadata_uri": nft_metadata_uri or "",
        "nft_metadata_hash": nft_metadata_hash or ZERO_HASH,
    }
