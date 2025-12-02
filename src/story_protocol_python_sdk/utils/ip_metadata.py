from dataclasses import dataclass, field

from ens.ens import HexStr

from story_protocol_python_sdk.utils.constants import ZERO_HASH


@dataclass
class IPMetadataInput:
    """
    Input data structure for IP metadata.

    This type defines the data that users need to provide when setting IP metadata.

    Attributes:
        ip_metadata_uri: [Optional] URI for IP metadata (default: "").
        ip_metadata_hash: [Optional] Hash for IP metadata (default: ZERO_HASH).
        nft_metadata_uri: [Optional] URI for NFT metadata (default: "").
        nft_metadata_hash: [Optional] Hash for NFT metadata (default: ZERO_HASH).
    """

    ip_metadata_uri: str = field(default="")
    ip_metadata_hash: HexStr = field(default=ZERO_HASH)
    nft_metadata_uri: str = field(default="")
    nft_metadata_hash: HexStr = field(default=ZERO_HASH)


@dataclass
class IPMetadata:
    """Validated IP metadata for IP asset operations."""

    ip_metadata_uri: str
    ip_metadata_hash: HexStr
    nft_metadata_uri: str
    nft_metadata_hash: HexStr

    @classmethod
    def from_input(cls, input_data: IPMetadataInput | None = None) -> "IPMetadata":
        """
        Create an IPMetadata instance from IPMetadataInput.

        Args:
            input_data: User-provided IP metadata

        Returns:
            IPMetadata instance with validated data
        """
        if input_data is None:
            return cls(
                ip_metadata_uri="",
                ip_metadata_hash=ZERO_HASH,
                nft_metadata_uri="",
                nft_metadata_hash=ZERO_HASH,
            )

        return cls(
            ip_metadata_uri=input_data.ip_metadata_uri,
            ip_metadata_hash=input_data.ip_metadata_hash,
            nft_metadata_uri=input_data.nft_metadata_uri,
            nft_metadata_hash=input_data.nft_metadata_hash,
        )

    def __post_init__(self):
        """Validate data after object creation."""
        self.get_validated_data()

    def get_validated_data(self) -> dict:
        """
        Get the metadata as a dictionary in the format expected by the blockchain.

        Returns:
            Dictionary with validated metadata fields
        """
        return {
            "ipMetadataURI": self.ip_metadata_uri,
            "ipMetadataHash": self.ip_metadata_hash,
            "nftMetadataURI": self.nft_metadata_uri,
            "nftMetadataHash": self.nft_metadata_hash,
        }


# In order to compatible with the previous version, we need to convert the ip_metadata to dict format for methods that expect dict.
# We can remove this function after these method become the internal methods.
def get_ip_metadata_dict(ip_metadata: IPMetadataInput | None = None) -> dict:
    ip_metadata_dict = {
        "ip_metadata_uri": "",
        "ip_metadata_hash": ZERO_HASH,
        "nft_metadata_uri": "",
        "nft_metadata_hash": ZERO_HASH,
    }

    if ip_metadata:
        ip_metadata_dict.update(
            {
                "ip_metadata_uri": (
                    ip_metadata.ip_metadata_uri
                    if ip_metadata.ip_metadata_uri is not None
                    else ""
                ),
                "ip_metadata_hash": (
                    ip_metadata.ip_metadata_hash
                    if ip_metadata.ip_metadata_hash is not None
                    else ZERO_HASH
                ),
                "nft_metadata_uri": (
                    ip_metadata.nft_metadata_uri
                    if ip_metadata.nft_metadata_uri is not None
                    else ""
                ),
                "nft_metadata_hash": (
                    ip_metadata.nft_metadata_hash
                    if ip_metadata.nft_metadata_hash is not None
                    else ZERO_HASH
                ),
            }
        )

    return ip_metadata_dict


# In order to compatible with the previous version, we need to check if the ip_metadata is the initial ip metadata.
# We can move into the IPMetadata class after these method become the internal methods.
def is_initial_ip_metadata(ip_metadata: dict | None = None) -> bool:
    if ip_metadata is None:
        return True

    return (
        ip_metadata.get("ip_metadata_uri", "") == ""
        and ip_metadata.get("ip_metadata_hash", ZERO_HASH) == ZERO_HASH
        and ip_metadata.get("nft_metadata_uri", "") == ""
        and ip_metadata.get("nft_metadata_hash", ZERO_HASH) == ZERO_HASH
    )
