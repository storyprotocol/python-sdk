import pytest

from story_protocol_python_sdk.story_client import StoryClient
from story_protocol_python_sdk.utils.constants import (
    ROYALTY_POLICY_LAP_ADDRESS,
    ZERO_ADDRESS,
)
from tests.integration.config.test_config import account, account_2, web3
from tests.integration.config.utils import MockERC20, get_story_client


@pytest.fixture(scope="session")
def story_client() -> StoryClient:
    """Fixture to provide the main story client"""
    return get_story_client(web3, account)


@pytest.fixture(scope="session")
def story_client_2() -> StoryClient:
    """Fixture to provide the secondary story client"""
    return get_story_client(web3, account_2)


@pytest.fixture(scope="module")
def nft_collection(story_client: StoryClient):
    """Fixture to provide the SPG NFT collection"""
    tx_data = story_client.NFTClient.create_nft_collection(
        name="test-collection",
        symbol="TEST",
        max_supply=100,
        is_public_minting=True,
        mint_open=True,
        contract_uri="test-uri",
        mint_fee_recipient=account.address,
    )
    return tx_data["nft_contract"]


@pytest.fixture(scope="module")
def parent_ip_and_license_terms(story_client: StoryClient, nft_collection):
    """Fixture to provide the parent IP and license terms"""
    response = story_client.IPAsset.mint_and_register_ip_asset_with_pil_terms(
        spg_nft_contract=nft_collection,
        terms=[
            {
                "terms": {
                    "transferable": True,
                    "royalty_policy": ROYALTY_POLICY_LAP_ADDRESS,
                    "default_minting_fee": 0,
                    "expiration": 0,
                    "commercial_use": True,
                    "commercial_attribution": False,
                    "commercializer_checker": ZERO_ADDRESS,
                    "commercializer_checker_data": ZERO_ADDRESS,
                    "commercial_rev_share": 50,
                    "commercial_rev_ceiling": 0,
                    "derivatives_allowed": True,
                    "derivatives_attribution": True,
                    "derivatives_approval": False,
                    "derivatives_reciprocal": True,
                    "derivative_rev_ceiling": 0,
                    "currency": MockERC20,
                    "uri": "",
                },
                "licensing_config": {
                    "is_set": True,
                    "minting_fee": 0,
                    "hook_data": ZERO_ADDRESS,
                    "licensing_hook": ZERO_ADDRESS,
                    "commercial_rev_share": 0,
                    "disabled": False,
                    "expect_minimum_group_reward_share": 0,
                    "expect_group_reward_pool": ZERO_ADDRESS,
                },
            }
        ],
    )
    return {
        "parent_ip_id": response["ip_id"],
        "license_terms_id": response["license_terms_ids"][0],
    }
