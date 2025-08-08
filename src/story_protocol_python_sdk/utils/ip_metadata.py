from story_protocol_python_sdk.utils.constants import ZERO_HASH


def get_ip_metadata(
    metadata: dict | None = None,
) -> dict:
    return {
        "ipMetadataURI": metadata.get("ip_metadata_uri", "") if metadata else "",
        "ipMetadataHash": (
            metadata.get("ip_metadata_hash", ZERO_HASH) if metadata else ZERO_HASH
        ),
        "nftMetadataURI": metadata.get("nft_metadata_uri", "") if metadata else "",
        "nftMetadataHash": (
            metadata.get("nft_metadata_hash", ZERO_HASH) if metadata else ZERO_HASH
        ),
    }
