import time
from typing import Any

from ens.ens import Address

from story_protocol_python_sdk.story_client import StoryClient

from .setup_for_integration import (
    EVEN_SPLIT_GROUP_POOL,
    PIL_LICENSE_TEMPLATE,
    ROYALTY_POLICY_LRP,
    ZERO_ADDRESS,
    MockERC20,
    web3,
)


class GroupTestHelper:
    """Helper class for Group integration tests."""

    @staticmethod
    def mint_and_register_ip_asset_with_pil_terms(
        story_client: StoryClient, nft_collection: Address
    ) -> dict[str, Any]:
        """Helper to mint and register an IP asset with PIL terms."""
        license_terms_data = [
            {
                "terms": {
                    "commercial_attribution": True,
                    "commercial_rev_ceiling": 10,
                    "commercial_rev_share": 10,
                    "commercial_use": True,
                    "commercializer_checker": ZERO_ADDRESS,
                    "commercializer_checker_data": ZERO_ADDRESS,
                    "currency": MockERC20,
                    "derivative_rev_ceiling": 0,
                    "derivatives_allowed": True,
                    "derivatives_approval": False,
                    "derivatives_attribution": True,
                    "derivatives_reciprocal": True,
                    "expiration": 0,
                    "default_minting_fee": 0,
                    "royalty_policy": ROYALTY_POLICY_LRP,
                    "transferable": True,
                    "uri": "https://github.com/piplabs/pil-document/blob/ad67bb632a310d2557f8abcccd428e4c9c798db1/off-chain-terms/CommercialRemix.json",
                },
                "licensing_config": {
                    "is_set": True,
                    "minting_fee": 0,
                    "hook_data": ZERO_ADDRESS,
                    "licensing_hook": ZERO_ADDRESS,
                    "commercial_rev_share": 10,
                    "disabled": False,
                    "expect_minimum_group_reward_share": 0,
                    "expect_group_reward_pool": EVEN_SPLIT_GROUP_POOL,
                },
            }
        ]

        # Create unique metadata
        metadata = {
            "ip_metadata_uri": f"test-uri-{int(time.time())}",
            "ip_metadata_hash": web3.to_hex(
                web3.keccak(text=f"test-metadata-hash-{int(time.time())}")
            ),
            "nft_metadata_uri": f"test-nft-uri-{int(time.time())}",
            "nft_metadata_hash": web3.to_hex(
                web3.keccak(text=f"test-nft-metadata-hash-{int(time.time())}")
            ),
        }

        result = story_client.IPAsset.mint_and_register_ip_asset_with_pil_terms(
            spg_nft_contract=nft_collection,
            terms=license_terms_data,
            ip_metadata=metadata,
        )

        return {
            "ip_id": result["ip_id"],
            "license_terms_id": result["license_terms_ids"][0],
        }

    @staticmethod
    def mint_and_register_ip_and_make_derivative(
        story_client: StoryClient,
        nft_collection: Address,
        group_id: Address,
        license_id: int,
    ) -> Address:
        """Helper to mint and register an IP and make it a derivative of another IP."""
        # Step 1: Mint and register IP
        metadata = {
            "ip_metadata_uri": f"test-derivative-uri-{int(time.time())}",
            "ip_metadata_hash": web3.to_hex(
                web3.keccak(text=f"test-derivative-metadata-hash-{int(time.time())}")
            ),
            "nft_metadata_uri": f"test-derivative-nft-uri-{int(time.time())}",
            "nft_metadata_hash": web3.to_hex(
                web3.keccak(
                    text=f"test-derivative-nft-metadata-hash-{int(time.time())}"
                )
            ),
        }

        result = story_client.IPAsset.mint_and_register_ip(
            spg_nft_contract=nft_collection,
            ip_metadata=metadata,
        )
        child_ip_id = result["ip_id"]

        # Step 2: Register as derivative
        story_client.IPAsset.register_derivative(
            child_ip_id=child_ip_id,
            parent_ip_ids=[group_id],
            license_terms_ids=[license_id],
            max_minting_fee=0,
            max_rts=10,
            max_revenue_share=0,
        )

        return child_ip_id

    @staticmethod
    def pay_royalty_and_transfer_to_vault(
        story_client: StoryClient,
        child_ip_id: Address,
        group_id: Address,
        token: Address,
        amount: int,
    ) -> None:
        """Helper to pay royalty on behalf and transfer to vault."""
        # Pay royalties from group IP id to child IP id
        story_client.Royalty.pay_royalty_on_behalf(
            receiver_ip_id=child_ip_id,
            payer_ip_id=group_id,
            token=token,
            amount=amount,
        )

        # Transfer to vault
        story_client.Royalty.transfer_to_vault(
            royalty_policy="LRP",
            ip_id=child_ip_id,
            ancestor_ip_id=group_id,
            token=token,
        )

    @staticmethod
    def register_group_and_attach_license(
        story_client: StoryClient, license_id: int, ip_ids: list[Address]
    ) -> Address:
        """Helper to register a group and attach license."""
        result = story_client.Group.register_group_and_attach_license_and_add_ips(
            group_pool=EVEN_SPLIT_GROUP_POOL,
            max_allowed_reward_share=100,
            ip_ids=ip_ids,
            license_data={
                "license_terms_id": license_id,
                "license_template": PIL_LICENSE_TEMPLATE,
                "licensing_config": {
                    "is_set": True,
                    "minting_fee": 0,
                    "hook_data": ZERO_ADDRESS,
                    "licensing_hook": ZERO_ADDRESS,
                    "commercial_rev_share": 10,
                    "disabled": False,
                    "expect_minimum_group_reward_share": 0,
                    "expect_group_reward_pool": ZERO_ADDRESS,
                },
            },
        )

        return result["group_id"]


class TestCollectRoyaltyAndClaimReward:
    """Test class for collecting royalties and claiming rewards functionality."""

    def test_collect_royalties(
        self, story_client: StoryClient, nft_collection: Address
    ):
        """Test collecting royalties into the pool."""
        # Register IP id
        result1 = GroupTestHelper.mint_and_register_ip_asset_with_pil_terms(
            story_client, nft_collection
        )
        ip_id = result1["ip_id"]
        license_terms_id = result1["license_terms_id"]

        # Register group id
        group_ip_id = GroupTestHelper.register_group_and_attach_license(
            story_client, license_terms_id, [ip_id]
        )

        # Mint and register child IP id
        child_ip_id = GroupTestHelper.mint_and_register_ip_and_make_derivative(
            story_client, nft_collection, group_ip_id, license_terms_id
        )

        # Pay royalties from group IP id to child IP id and transfer to vault
        GroupTestHelper.pay_royalty_and_transfer_to_vault(
            story_client, child_ip_id, group_ip_id, MockERC20, 100
        )

        # Collect royalties
        result = story_client.Group.collect_royalties(
            group_ip_id=group_ip_id, currency_token=MockERC20
        )

        assert "tx_hash" in result
        assert isinstance(result["tx_hash"], str)
        assert len(result["tx_hash"]) > 0
        assert result["collected_royalties"] == 10  # 10% of 100 = 10

    def test_claim_reward(self, story_client: StoryClient, nft_collection: Address):
        """Test claiming rewards for group members."""
        # Register IP id
        result1 = GroupTestHelper.mint_and_register_ip_asset_with_pil_terms(
            story_client, nft_collection
        )
        ip_id = result1["ip_id"]
        license_terms_id = result1["license_terms_id"]

        # Register group id
        group_ip_id = GroupTestHelper.register_group_and_attach_license(
            story_client, license_terms_id, [ip_id]
        )

        # Mint license tokens to the IP id which doesn't have a royalty vault
        story_client.License.mint_license_tokens(
            licensor_ip_id=ip_id,
            license_template=PIL_LICENSE_TEMPLATE,
            license_terms_id=license_terms_id,
            amount=100,
            receiver=ip_id,
            max_minting_fee=1,
            max_revenue_share=100,
        )

        # Claim reward
        result = story_client.Group.claim_rewards(
            group_ip_id=group_ip_id,
            currency_token=MockERC20,
            member_ip_ids=[ip_id],
        )

        assert "tx_hash" in result
        assert isinstance(result["tx_hash"], str)
        assert "claimed_rewards" in result
        assert len(result["claimed_rewards"]["ip_ids"]) == 1
        assert len(result["claimed_rewards"]["amounts"]) == 1
        assert result["claimed_rewards"]["token"] == MockERC20
        assert result["claimed_rewards"]["group_id"] == group_ip_id

    def test_collect_and_distribute_group_royalties(
        self, story_client: StoryClient, nft_collection: Address
    ):
        """Test collecting and distributing group royalties in one transaction."""
        ip_ids = []

        # Create two IPs
        result1 = GroupTestHelper.mint_and_register_ip_asset_with_pil_terms(
            story_client, nft_collection
        )
        result2 = GroupTestHelper.mint_and_register_ip_asset_with_pil_terms(
            story_client, nft_collection
        )
        ip_ids.append(result1["ip_id"])
        ip_ids.append(result2["ip_id"])
        license_terms_id = result1["license_terms_id"]

        # Register group
        group_id = GroupTestHelper.register_group_and_attach_license(
            story_client, license_terms_id, ip_ids
        )

        # Create derivative IPs
        child_ip_id1 = GroupTestHelper.mint_and_register_ip_and_make_derivative(
            story_client, nft_collection, group_id, license_terms_id
        )
        child_ip_id2 = GroupTestHelper.mint_and_register_ip_and_make_derivative(
            story_client, nft_collection, group_id, license_terms_id
        )

        # Pay royalties
        GroupTestHelper.pay_royalty_and_transfer_to_vault(
            story_client, child_ip_id1, group_id, MockERC20, 100
        )
        GroupTestHelper.pay_royalty_and_transfer_to_vault(
            story_client, child_ip_id2, group_id, MockERC20, 100
        )

        # Collect and distribute royalties
        response = story_client.Group.collect_and_distribute_group_royalties(
            group_ip_id=group_id, currency_tokens=[MockERC20], member_ip_ids=ip_ids
        )

        assert "tx_hash" in response
        assert isinstance(response["tx_hash"], str)
        assert len(response["tx_hash"]) > 0

        assert "collected_royalties" in response
        assert len(response["collected_royalties"]) > 0
        assert response["collected_royalties"][0]["amount"] == 20

        assert "royalties_distributed" in response
        assert len(response["royalties_distributed"]) == 2
        assert response["royalties_distributed"][0]["amount"] == 10
        assert response["royalties_distributed"][1]["amount"] == 10

    def test_get_claimable_reward(
        self, story_client: StoryClient, nft_collection: Address
    ):
        """Test getting claimable rewards for group members."""
        # Register IP id
        result1 = GroupTestHelper.mint_and_register_ip_asset_with_pil_terms(
            story_client, nft_collection
        )
        ip_id1 = result1["ip_id"]
        license_terms_id1 = result1["license_terms_id"]
        result2 = GroupTestHelper.mint_and_register_ip_asset_with_pil_terms(
            story_client, nft_collection
        )
        ip_id2 = result2["ip_id"]
        license_terms_id2 = result2["license_terms_id"]

        # Register group id
        group_ip_id = GroupTestHelper.register_group_and_attach_license(
            story_client, license_terms_id1, [ip_id1, ip_id2]
        )
        # Create a derivative IP and pay royalties
        child_ip_id = GroupTestHelper.mint_and_register_ip_and_make_derivative(
            story_client, nft_collection, group_ip_id, license_terms_id1
        )
        child_ip_id2 = GroupTestHelper.mint_and_register_ip_and_make_derivative(
            story_client, nft_collection, group_ip_id, license_terms_id2
        )

        # Pay royalties from group IP id to child IP id
        GroupTestHelper.pay_royalty_and_transfer_to_vault(
            story_client, child_ip_id, group_ip_id, MockERC20, 100
        )
        GroupTestHelper.pay_royalty_and_transfer_to_vault(
            story_client, child_ip_id2, group_ip_id, MockERC20, 100
        )

        # Collect royalties
        story_client.Group.collect_royalties(
            group_ip_id=group_ip_id,
            currency_token=MockERC20,
        )
        # Get claimable rewards after royalties are collected
        claimable_rewards = story_client.Group.get_claimable_reward(
            group_ip_id=group_ip_id,
            currency_token=MockERC20,
            member_ip_ids=[ip_id1, ip_id2],
        )

        assert isinstance(claimable_rewards, list)
        assert len(claimable_rewards) == 2
        assert claimable_rewards[0] == 10
        assert claimable_rewards[1] == 10
