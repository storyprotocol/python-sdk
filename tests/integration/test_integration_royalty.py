import pytest

from story_protocol_python_sdk.abi.DerivativeWorkflows.DerivativeWorkflows_client import (
    DerivativeWorkflowsClient,
)
from story_protocol_python_sdk.story_client import StoryClient
from story_protocol_python_sdk.utils.constants import WIP_TOKEN_ADDRESS
from story_protocol_python_sdk.utils.derivative_data import DerivativeDataInput

from .setup_for_integration import (
    PIL_LICENSE_TEMPLATE,
    ROYALTY_MODULE,
    ROYALTY_POLICY,
    ZERO_ADDRESS,
    MockERC20,
    MockERC721,
    account,
    approve,
    get_token_id,
    mint_tokens,
    web3,
)


class TestRoyalty:

    @pytest.fixture(scope="module")
    def setup_ips_and_licenses(self, story_client: StoryClient):
        """Setup parent and child IPs with proper license relationships"""

        parent_token_id = get_token_id(
            MockERC721, story_client.web3, story_client.account
        )
        parent_ip_response = story_client.IPAsset.register(
            nft_contract=MockERC721, token_id=parent_token_id
        )
        parent_ip_id = parent_ip_response["ip_id"]

        child_token_id = get_token_id(
            MockERC721, story_client.web3, story_client.account
        )
        child_ip_response = story_client.IPAsset.register(
            nft_contract=MockERC721, token_id=child_token_id
        )
        child_ip_id = child_ip_response["ip_id"]

        license_terms_response = story_client.License.register_commercial_remix_pil(
            default_minting_fee=100000,
            currency=MockERC20,
            commercial_rev_share=10,
            royalty_policy=ROYALTY_POLICY,
        )
        if license_terms_response is None:
            raise ValueError("Failed to register license terms")
        license_terms_id = license_terms_response["license_terms_id"]

        story_client.License.attach_license_terms(
            ip_id=parent_ip_id,
            license_template=PIL_LICENSE_TEMPLATE,
            license_terms_id=license_terms_id,
        )

        story_client.IPAsset.register_derivative(
            child_ip_id=child_ip_id,
            parent_ip_ids=[parent_ip_id],
            license_terms_ids=[license_terms_id],
            max_minting_fee=0,
            max_rts=0,
            max_revenue_share=0,
        )

        mint_tokens(
            erc20_contract_address=MockERC20,
            web3=web3,
            account=account,
            to_address=account.address,
            amount=100000 * 10**6,
        )

        approve(
            erc20_contract_address=MockERC20,
            web3=web3,
            account=account,
            spender_address=ROYALTY_MODULE,
            amount=100000 * 10**6,
        )

        return {
            "parent_ip_id": parent_ip_id,
            "child_ip_id": child_ip_id,
            "license_terms_id": license_terms_id,
        }

    def test_pay_royalty_on_behalf(
        self, story_client: StoryClient, setup_ips_and_licenses
    ):
        """Test paying royalty on behalf of a payer IP to a receiver IP"""
        parent_ip_id = setup_ips_and_licenses["parent_ip_id"]
        child_ip_id = setup_ips_and_licenses["child_ip_id"]

        response = story_client.Royalty.pay_royalty_on_behalf(
            receiver_ip_id=parent_ip_id,
            payer_ip_id=child_ip_id,
            token=MockERC20,
            amount=1,
        )

        assert response is not None
        assert response["tx_hash"] is not None and isinstance(response["tx_hash"], str)

    def test_claimable_revenue(self, story_client: StoryClient, setup_ips_and_licenses):
        """Test checking claimable revenue"""
        parent_ip_id = setup_ips_and_licenses["parent_ip_id"]

        response = story_client.Royalty.claimable_revenue(
            royalty_vault_ip_id=parent_ip_id, claimer=account.address, token=MockERC20
        )

        assert isinstance(response, int)

    def test_pay_royalty_unregistered_receiver(
        self, story_client: StoryClient, setup_ips_and_licenses
    ):
        """Test that paying royalty to unregistered IP fails appropriately"""
        child_ip_id = setup_ips_and_licenses["child_ip_id"]
        unregistered_ip_id = "0x1234567890123456789012345678901234567890"

        with pytest.raises(
            ValueError,
            match=f"The receiver IP with id {unregistered_ip_id} is not registered",
        ):
            story_client.Royalty.pay_royalty_on_behalf(
                receiver_ip_id=unregistered_ip_id,
                payer_ip_id=child_ip_id,
                token=MockERC20,
                amount=1000,
            )

    def test_pay_royalty_invalid_amount(
        self, story_client: StoryClient, setup_ips_and_licenses
    ):
        """Test that paying with invalid amount fails appropriately"""
        parent_ip_id = setup_ips_and_licenses["parent_ip_id"]
        child_ip_id = setup_ips_and_licenses["child_ip_id"]

        with pytest.raises(Exception):
            story_client.Royalty.pay_royalty_on_behalf(
                receiver_ip_id=parent_ip_id,
                payer_ip_id=child_ip_id,
                token=MockERC20,
                amount=-1,
            )

    def test_batch_claim_all_revenue_single_ancestor(self, story_client: StoryClient):
        """Test batch claiming revenue using the same pattern as test_claim_all_revenue

        This test verifies that batch_claim_all_revenue works correctly by:
        1. Creating a derivative chain A->B->C
        2. Using batch_claim_all_revenue to claim revenue for A
        3. Verifying the claimed amount matches expectations
        """
        # Create NFT collection
        collection_response = story_client.NFTClient.create_nft_collection(
            name="batch-claim-test",
            symbol="BCT",
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=ZERO_ADDRESS,
        )
        spg_nft_contract = collection_response["nft_contract"]

        def wrapper_derivative_with_wip(parent_ip_id, license_terms_id):
            """Helper to create derivative with WIP tokens"""
            minting_fee = story_client.License.predict_minting_license_fee(
                licensor_ip_id=parent_ip_id,
                license_terms_id=license_terms_id,
                amount=1,
            )
            amount = minting_fee["amount"]

            story_client.WIP.deposit(amount=amount)
            story_client.WIP.approve(spender=spg_nft_contract, amount=amount)
            derivative_workflows_address = DerivativeWorkflowsClient(
                story_client.web3
            ).contract.address
            story_client.WIP.approve(
                spender=derivative_workflows_address, amount=amount
            )

            response = story_client.IPAsset.mint_and_register_ip_and_make_derivative(
                spg_nft_contract=spg_nft_contract,
                deriv_data=DerivativeDataInput(
                    parent_ip_ids=[parent_ip_id],
                    license_terms_ids=[license_terms_id],
                ),
            )
            return response["ip_id"]

        # Define license terms: 100 WIP minting fee + 10% royalty share
        license_terms_template = [
            {
                "terms": {
                    "transferable": True,
                    "royalty_policy": ROYALTY_POLICY,
                    "default_minting_fee": 100,
                    "expiration": 0,
                    "commercial_use": True,
                    "commercial_attribution": False,
                    "commercializer_checker": ZERO_ADDRESS,
                    "commercializer_checker_data": ZERO_ADDRESS,
                    "commercial_rev_share": 10,
                    "commercial_rev_ceiling": 0,
                    "derivatives_allowed": True,
                    "derivatives_attribution": True,
                    "derivatives_approval": False,
                    "derivatives_reciprocal": True,
                    "derivative_rev_ceiling": 0,
                    "currency": WIP_TOKEN_ADDRESS,
                    "uri": "",
                },
                "licensing_config": {
                    "is_set": True,
                    "minting_fee": 100,
                    "hook_data": ZERO_ADDRESS,
                    "licensing_hook": ZERO_ADDRESS,
                    "commercial_rev_share": 0,
                    "disabled": False,
                    "expect_minimum_group_reward_share": 0,
                    "expect_group_reward_pool": ZERO_ADDRESS,
                },
            }
        ]

        # Register IP A with PIL terms
        ip_a_response = story_client.IPAsset.mint_and_register_ip_asset_with_pil_terms(
            spg_nft_contract=spg_nft_contract,
            terms=license_terms_template,
        )
        ip_a = ip_a_response["ip_id"]
        license_terms_id = ip_a_response["license_terms_ids"][0]

        # Build derivative chain: A -> B -> C -> D (same as test_claim_all_revenue)
        ip_b = wrapper_derivative_with_wip(ip_a, license_terms_id)  # B pays 100 WIP
        ip_c = wrapper_derivative_with_wip(
            ip_b, license_terms_id
        )  # C pays 100 WIP (10 to A, 90 to B)
        wrapper_derivative_with_wip(
            ip_c, license_terms_id
        )  # D pays 100 WIP (10 to A, 10 to B, 80 to C)

        # Batch claim revenue for IP A (should get 120 WIP: 100 from B + 10 from C + 10 from D)
        # Note: Only pass [ip_b, ip_c] as child_ip_ids, not ip_d, matching test_claim_all_revenue
        response = story_client.Royalty.batch_claim_all_revenue(
            ancestor_ips=[
                {
                    "ip_id": ip_a,
                    "claimer": ip_a,
                    "child_ip_ids": [ip_b, ip_c],
                    "royalty_policies": [ROYALTY_POLICY, ROYALTY_POLICY],
                    "currency_tokens": [WIP_TOKEN_ADDRESS, WIP_TOKEN_ADDRESS],
                },
            ],
            claim_options={
                "auto_transfer_all_claimed_tokens_from_ip": False,
                "auto_unwrap_ip_tokens": False,
            },
        )

        # Verify response
        assert response is not None
        assert "tx_hashes" in response
        assert len(response["tx_hashes"]) >= 1
        assert "receipts" in response
        assert len(response["receipts"]) >= 1
        assert "claimed_tokens" in response
        assert len(response["claimed_tokens"]) >= 1

        # Verify IP A received 120 WIP tokens (100 from B + 10 from C + 10 from D)
        assert response["claimed_tokens"][0]["amount"] == 120

    def test_batch_claim_all_revenue_multiple_ancestors(
        self, story_client: StoryClient
    ):
        """Test batch claiming revenue from multiple ancestor IPs

        This test creates two independent derivative chains and claims revenue for both ancestors:
        - Chain 1: A1 -> B1 -> C1 -> D1 (A1 gets 120 WIP)
        - Chain 2: A2 -> B2 -> C2 (A2 gets 110 WIP)
        """
        # Create NFT collection
        collection_response = story_client.NFTClient.create_nft_collection(
            name="multi-ancestor-test",
            symbol="MAT",
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=ZERO_ADDRESS,
        )
        spg_nft_contract = collection_response["nft_contract"]

        def wrapper_derivative_with_wip(parent_ip_id, license_terms_id):
            """Helper to create derivative with WIP tokens"""
            minting_fee = story_client.License.predict_minting_license_fee(
                licensor_ip_id=parent_ip_id,
                license_terms_id=license_terms_id,
                amount=1,
            )
            amount = minting_fee["amount"]

            story_client.WIP.deposit(amount=amount)
            story_client.WIP.approve(spender=spg_nft_contract, amount=amount)
            derivative_workflows_address = DerivativeWorkflowsClient(
                story_client.web3
            ).contract.address
            story_client.WIP.approve(
                spender=derivative_workflows_address, amount=amount
            )

            response = story_client.IPAsset.mint_and_register_ip_and_make_derivative(
                spg_nft_contract=spg_nft_contract,
                deriv_data=DerivativeDataInput(
                    parent_ip_ids=[parent_ip_id],
                    license_terms_ids=[license_terms_id],
                ),
            )
            return response["ip_id"]

        # Define license terms: 100 WIP minting fee + 10% royalty share
        license_terms_template = [
            {
                "terms": {
                    "transferable": True,
                    "royalty_policy": ROYALTY_POLICY,
                    "default_minting_fee": 100,
                    "expiration": 0,
                    "commercial_use": True,
                    "commercial_attribution": False,
                    "commercializer_checker": ZERO_ADDRESS,
                    "commercializer_checker_data": ZERO_ADDRESS,
                    "commercial_rev_share": 10,
                    "commercial_rev_ceiling": 0,
                    "derivatives_allowed": True,
                    "derivatives_attribution": True,
                    "derivatives_approval": False,
                    "derivatives_reciprocal": True,
                    "derivative_rev_ceiling": 0,
                    "currency": WIP_TOKEN_ADDRESS,
                    "uri": "",
                },
                "licensing_config": {
                    "is_set": True,
                    "minting_fee": 100,
                    "hook_data": ZERO_ADDRESS,
                    "licensing_hook": ZERO_ADDRESS,
                    "commercial_rev_share": 0,
                    "disabled": False,
                    "expect_minimum_group_reward_share": 0,
                    "expect_group_reward_pool": ZERO_ADDRESS,
                },
            }
        ]

        # Register IP A1 with PIL terms
        ip_a1_response = story_client.IPAsset.mint_and_register_ip_asset_with_pil_terms(
            spg_nft_contract=spg_nft_contract,
            terms=license_terms_template,
        )
        ip_a1 = ip_a1_response["ip_id"]
        license_terms_id = ip_a1_response["license_terms_ids"][0]

        # Build derivative chain 1: A1 -> B1 -> C1 -> D1
        ip_b1 = wrapper_derivative_with_wip(ip_a1, license_terms_id)
        ip_c1 = wrapper_derivative_with_wip(ip_b1, license_terms_id)
        wrapper_derivative_with_wip(ip_c1, license_terms_id)  # D1

        # Register IP A2 and attach the same license terms (to avoid duplicate license terms error)
        ip_a2_response = story_client.IPAsset.mint_and_register_ip(
            spg_nft_contract=spg_nft_contract,
        )
        ip_a2 = ip_a2_response["ip_id"]

        # Attach the same license terms to IP A2
        story_client.License.attach_license_terms(
            ip_id=ip_a2,
            license_template=PIL_LICENSE_TEMPLATE,
            license_terms_id=license_terms_id,
        )

        # Build derivative chain 2: A2 -> B2 -> C2
        ip_b2 = wrapper_derivative_with_wip(ip_a2, license_terms_id)
        wrapper_derivative_with_wip(ip_b2, license_terms_id)

        # Batch claim revenue for both ancestors (disable multicall to avoid potential issues)
        response = story_client.Royalty.batch_claim_all_revenue(
            ancestor_ips=[
                {
                    "ip_id": ip_a1,
                    "claimer": ip_a1,
                    "child_ip_ids": [ip_b1, ip_c1],
                    "royalty_policies": [ROYALTY_POLICY, ROYALTY_POLICY],
                    "currency_tokens": [WIP_TOKEN_ADDRESS, WIP_TOKEN_ADDRESS],
                },
                {
                    "ip_id": ip_a2,
                    "claimer": ip_a2,
                    "child_ip_ids": [ip_b2],
                    "royalty_policies": [ROYALTY_POLICY],
                    "currency_tokens": [WIP_TOKEN_ADDRESS],
                },
            ],
            claim_options={
                "auto_transfer_all_claimed_tokens_from_ip": False,
                "auto_unwrap_ip_tokens": False,
            },
            options={
                "use_multicall_when_possible": False,  # Disable multicall for stability
            },
        )

        # Verify response
        assert response is not None
        assert "tx_hashes" in response
        assert len(response["tx_hashes"]) >= 2  # Should have 2 separate txs
        assert "receipts" in response
        assert len(response["receipts"]) >= 2
        assert "claimed_tokens" in response
        assert len(response["claimed_tokens"]) == 2  # Two ancestors claimed

        # Verify both ancestors received their expected amounts
        # A1 should get 120 WIP (100 from B1 + 10 from C1 + 10 from D1)
        # A2 should get 110 WIP (100 from B2 + 10 from C2)
        claimed_amounts = {
            token["claimer"]: token["amount"] for token in response["claimed_tokens"]
        }
        assert claimed_amounts[ip_a1] == 120
        assert claimed_amounts[ip_a2] == 110


class TestClaimAllRevenue:
    def test_claim_all_revenue(self, story_client: StoryClient):
        """Test claiming all revenue with WIP tokens and automatic unwrapping

        Test flow:
        1. Create NFT collection
        2. Set up derivative chain: A->B->C->D
           - Each derivative pays 100 WIP tokens as minting fee
           - 10% LAP royalty share is configured
        3. IP A earns 120 WIP tokens total (100 + 10 + 10)
        4. Claim revenue with default options (auto_transfer=True, auto_unwrap=True)
        5. Verify WIP tokens are automatically unwrapped to native tokens

        Expected: Wallet balance increases by 120 native tokens (WIP unwrapped)
        """
        # Create NFT collection
        collection_response = story_client.NFTClient.create_nft_collection(
            name="free-collection",
            symbol="test-collection",
            is_public_minting=True,
            mint_open=True,
            contract_uri="test-uri",
            mint_fee_recipient=ZERO_ADDRESS,
        )
        spg_nft_contract = collection_response["nft_contract"]

        def wrapper_derivative_with_wip(parent_ip_id, license_terms_id):
            """
            Helper function to create a derivative IP using WIP tokens for minting fee.

            Steps:
            1. Predict the minting fee for the license
            2. Deposit native tokens to get WIP tokens
            3. Approve the SPG contract to spend WIP tokens
            4. Mint and register IP as derivative
            """
            # Predict how much WIP tokens are needed for minting fee
            minting_fee = story_client.License.predict_minting_license_fee(
                licensor_ip_id=parent_ip_id,
                license_terms_id=license_terms_id,
                amount=1,
            )
            amount = minting_fee["amount"]

            # Deposit native tokens to get WIP tokens
            story_client.WIP.deposit(amount=amount)

            # Approve SPG contract to spend WIP tokens
            story_client.WIP.approve(spender=spg_nft_contract, amount=amount)
            derivative_workflows_address = DerivativeWorkflowsClient(
                story_client.web3
            ).contract.address
            story_client.WIP.approve(
                spender=derivative_workflows_address, amount=amount
            )

            # Mint and register the derivative IP
            response = story_client.IPAsset.mint_and_register_ip_and_make_derivative(
                spg_nft_contract=spg_nft_contract,
                deriv_data=DerivativeDataInput(
                    parent_ip_ids=[parent_ip_id],
                    license_terms_ids=[license_terms_id],
                ),
            )
            return response["ip_id"]

        # Define license terms: 100 WIP minting fee + 10% royalty share
        license_terms_template = [
            {
                "terms": {
                    "transferable": True,
                    "royalty_policy": ROYALTY_POLICY,
                    "default_minting_fee": 100,
                    "expiration": 0,
                    "commercial_use": True,
                    "commercial_attribution": False,
                    "commercializer_checker": ZERO_ADDRESS,
                    "commercializer_checker_data": ZERO_ADDRESS,
                    "commercial_rev_share": 10,  # 10% royalty share
                    "commercial_rev_ceiling": 0,
                    "derivatives_allowed": True,
                    "derivatives_attribution": True,
                    "derivatives_approval": False,
                    "derivatives_reciprocal": True,
                    "derivative_rev_ceiling": 0,
                    "currency": WIP_TOKEN_ADDRESS,  # Use WIP tokens for payments
                    "uri": "",
                },
                "licensing_config": {
                    "is_set": True,
                    "minting_fee": 100,  # Base minting fee
                    "hook_data": ZERO_ADDRESS,
                    "licensing_hook": ZERO_ADDRESS,
                    "commercial_rev_share": 0,
                    "disabled": False,
                    "expect_minimum_group_reward_share": 0,
                    "expect_group_reward_pool": ZERO_ADDRESS,
                },
            }
        ]

        # Register IP A with PIL terms (root IP in derivative chain)
        ip_a_response = story_client.IPAsset.mint_and_register_ip_asset_with_pil_terms(
            spg_nft_contract=spg_nft_contract,
            terms=license_terms_template,
        )
        ip_a = ip_a_response["ip_id"]
        license_terms_id = ip_a_response["license_terms_ids"][0]

        # Build derivative chain: A -> B -> C -> D
        # Each derivative mints with WIP tokens, generating revenue for ancestors
        ip_b = wrapper_derivative_with_wip(ip_a, license_terms_id)  # B pays 100 WIP
        ip_c = wrapper_derivative_with_wip(
            ip_b, license_terms_id
        )  # C pays 100 WIP (10 to A, 90 to B)
        wrapper_derivative_with_wip(
            ip_c, license_terms_id
        )  # D pays 100 WIP (10 to A, 10 to B, 80 to C)

        # Record wallet WIP balance before claiming
        wip_token_balance_before = story_client.WIP.balance_of(address=account.address)

        # Claim all revenue from child IPs for ancestor IP A
        # With default options: auto_transfer=True, auto_unwrap=True
        # This will automatically unwrap WIP tokens to native tokens
        response = story_client.Royalty.claim_all_revenue(
            ancestor_ip_id=ip_a,
            claimer=ip_a,
            child_ip_ids=[ip_b, ip_c],
            royalty_policies=[ROYALTY_POLICY, ROYALTY_POLICY],
            currency_tokens=[WIP_TOKEN_ADDRESS, WIP_TOKEN_ADDRESS],
        )

        # Record wallet WIP balance after claiming
        wip_token_balance_after = story_client.WIP.balance_of(address=account.address)

        # Verify the claim response
        assert response is not None
        assert "tx_hashes" in response
        assert isinstance(response["tx_hashes"], list)
        assert len(response["tx_hashes"]) > 0

        # Verify IP A received 120 WIP tokens total (100 from B + 10 from C + 10 from D)
        assert response["claimed_tokens"][0]["amount"] == 120

        # Verify WIP tokens were automatically unwrapped
        assert wip_token_balance_after == wip_token_balance_before
