from ens.ens import HexStr

from story_protocol_python_sdk import (
    IPMetadataInput,
    LicenseTermsDataInput,
    LicenseTermsInput,
)
from story_protocol_python_sdk.utils.constants import ZERO_ADDRESS, ZERO_HASH

CHAIN_ID = 1315
ADDRESS = "0x1234567890123456789012345678901234567890"
TX_HASH = b"tx_hash_bytes"
# STATE as bytes32 (32 bytes = 64 hex characters)
STATE = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
IP_ID = "0xFEB4eE75600768635010D80D56a5711268D26DaB"
LICENSE_TERMS = {
    "royalty_policy": ADDRESS,
    "commercial_rev_share": 19,
    "currency": ADDRESS,
    "default_minting_fee": 10,
    "expiration": 100,
    "commercial_use": True,
    "commercial_attribution": True,
    "commercializer_checker": True,
    "commercializer_checker_data": ADDRESS,
    "derivatives_allowed": True,
    "derivatives_attribution": True,
    "derivatives_approval": True,
    "derivatives_reciprocal": True,
    "derivative_rev_ceiling": 100,
    "uri": "https://example.com",
    "transferable": True,
}

LICENSING_CONFIG = {
    "is_set": True,
    "minting_fee": 10,
    "licensing_hook": ADDRESS,
    "hook_data": ADDRESS,
    "commercial_rev_share": 10,
    "disabled": False,
    "expect_minimum_group_reward_share": 10,
    "expect_group_reward_pool": ADDRESS,
}
ACCOUNT_ADDRESS = "0xF60cBF0Ea1A61567F1dDaf79A6219D20d189155c"

LICENSE_TERMS_DATA = [
    LicenseTermsDataInput(
        terms=LicenseTermsInput(
            transferable=True,
            royalty_policy=ADDRESS,
            default_minting_fee=10000,
            expiration=1000,
            commercial_use=True,
            commercial_attribution=False,
            commercializer_checker=ZERO_ADDRESS,
            commercializer_checker_data=ZERO_HASH,
            commercial_rev_share=10,
            commercial_rev_ceiling=0,
            derivatives_allowed=True,
            derivatives_attribution=True,
            derivatives_approval=False,
            derivatives_reciprocal=True,
            derivative_rev_ceiling=0,
            currency=ADDRESS,
            uri="test-uri",
        ),
        licensing_config={
            "is_set": True,
            "minting_fee": 10,
            "licensing_hook": ADDRESS,
            "hook_data": ZERO_HASH,
            "commercial_rev_share": 10,
            "disabled": False,
            "expect_minimum_group_reward_share": 0,
            "expect_group_reward_pool": ZERO_ADDRESS,
        },
    )
]
IP_METADATA = IPMetadataInput(
    ip_metadata_uri="https://example.com/ip-metadata.json",
    ip_metadata_hash=HexStr("0x" + "a" * 64),
    nft_metadata_uri="https://example.com/nft-metadata.json",
    nft_metadata_hash=HexStr("0x" + "b" * 64),
)
