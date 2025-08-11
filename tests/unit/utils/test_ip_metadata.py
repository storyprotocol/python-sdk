from ens.ens import HexStr

from story_protocol_python_sdk.utils.constants import ZERO_HASH
from story_protocol_python_sdk.utils.ip_metadata import IPMetadata, IPMetadataInput
from tests.unit.fixtures.data import TX_HASH


class TestIPMetadata:
    def test_from_input_with_default_values(self):
        ip_metadata = IPMetadata.from_input(IPMetadataInput(ip_metadata_hash=TX_HASH))
        assert ip_metadata.get_validated_data() == {
            "ipMetadataURI": "",
            "ipMetadataHash": TX_HASH,
            "nftMetadataURI": "",
            "nftMetadataHash": ZERO_HASH,
        }

    def test_from_input_with_custom_values(self):
        ip_metadata = IPMetadata.from_input(
            IPMetadataInput(
                ip_metadata_uri="https://ipfs.io/ipfs/Qm...",
                ip_metadata_hash=HexStr("0x1234567890"),
                nft_metadata_uri="https://ipfs.io/ipfs/Qm...",
                nft_metadata_hash=HexStr("0x1234567890"),
            )
        )
        assert ip_metadata.get_validated_data() == {
            "ipMetadataURI": "https://ipfs.io/ipfs/Qm...",
            "ipMetadataHash": HexStr("0x1234567890"),
            "nftMetadataURI": "https://ipfs.io/ipfs/Qm...",
            "nftMetadataHash": HexStr("0x1234567890"),
        }

    def test_from_input_with_none(self):
        ip_metadata = IPMetadata.from_input(None)
        assert ip_metadata.get_validated_data() == {
            "ipMetadataURI": "",
            "ipMetadataHash": ZERO_HASH,
            "nftMetadataURI": "",
            "nftMetadataHash": ZERO_HASH,
        }
