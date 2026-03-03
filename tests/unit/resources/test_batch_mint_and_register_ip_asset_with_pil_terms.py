"""Unit tests for batch_mint_and_register_ip_asset_with_pil_terms functionality."""

from unittest.mock import Mock, patch

import pytest

from story_protocol_python_sdk.resources.IPAsset import IPAsset

# Test constants
SPG_NFT_CONTRACT = "0x1234567890123456789012345678901234567890"
IP_ID_1 = "0xabcdef1234567890123456789012345678901234"
IP_ID_2 = "0xabcdef1234567890123456789012345678901235"
TX_HASH = "0x129f7dd802200f096221dd89d5b086e4bd3ad6eafb378a0c75e3b04fc375f997"
ZERO_HASH = "0x0000000000000000000000000000000000000000000000000000000000000000"
ROYALTY_POLICY = "0xBe54FB168b3c982b7AaE60dB6CF75Bd8447b390E"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
WIP_TOKEN_ADDRESS = "0x1514000000000000000000000000000000000000"


@pytest.fixture
def ip_asset_client(mock_web3, mock_account):
    """Create IPAsset client for testing."""
    return IPAsset(mock_web3, mock_account, chain_id=1516)


class TestBatchMintAndRegisterIpAssetWithPilTerms:
    """Test suite for batch_mint_and_register_ip_asset_with_pil_terms."""

    def test_batch_mint_successful_with_two_ips(self, ip_asset_client):
        """Test successful batch minting of two IPs"""
        license_terms_template = {
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

        # Create mock logs for IPRegistered events
        mock_topic = Mock()
        mock_topic.hex.return_value = "0xip_registered_sig"
        
        mock_log_1 = {"topics": [mock_topic]}
        mock_log_2 = {"topics": [mock_topic]}
        
        # Mock keccak for event signature
        mock_keccak_result = Mock()
        mock_keccak_result.hex.return_value = "0xip_registered_sig"
        ip_asset_client.web3.keccak = Mock(return_value=mock_keccak_result)
        
        # Mock to_checksum_address
        ip_asset_client.web3.to_checksum_address = Mock(side_effect=lambda x: x)
        
        # Mock event processing
        mock_event_1 = {"args": {"ipId": IP_ID_1, "tokenId": 1, "tokenContract": SPG_NFT_CONTRACT}}
        mock_event_2 = {"args": {"ipId": IP_ID_2, "tokenId": 2, "tokenContract": SPG_NFT_CONTRACT}}
        ip_asset_client.ip_asset_registry_client.contract.events.IPRegistered.process_log = Mock(
            side_effect=[mock_event_1, mock_event_2]
        )

        # Mock mint_and_register_ip_asset_with_pil_terms to return encoded data
        with patch.object(
            ip_asset_client,
            "mint_and_register_ip_asset_with_pil_terms",
            side_effect=[
                {"encoded_tx_data": "0x1234"},
                {"encoded_tx_data": "0x5678"},
            ],
        ):
            # Mock build_and_send_transaction
            with patch(
                "story_protocol_python_sdk.resources.IPAsset.build_and_send_transaction",
                return_value={
                    "tx_hash": TX_HASH,
                    "tx_receipt": {"logs": [mock_log_1, mock_log_2]},
                },
            ):
                # Mock license terms parsing
                with patch.object(
                    ip_asset_client,
                    "_parse_tx_license_terms_attached_event_for_ip",
                    side_effect=[[1, 2], [3]],
                ):
                    result = ip_asset_client.batch_mint_and_register_ip_asset_with_pil_terms(
                        args=[
                            {
                                "spg_nft_contract": SPG_NFT_CONTRACT,
                                "terms": [license_terms_template],
                            },
                            {
                                "spg_nft_contract": SPG_NFT_CONTRACT,
                                "terms": [license_terms_template],
                            },
                        ]
                    )

        assert result["tx_hash"] == TX_HASH
        assert len(result["results"]) == 2
        assert result["results"][0]["ip_id"] == IP_ID_1
        assert result["results"][0]["token_id"] == 1
        assert result["results"][0]["spg_nft_contract"] == SPG_NFT_CONTRACT
        assert result["results"][0]["license_terms_ids"] == [1, 2]
        assert result["results"][1]["ip_id"] == IP_ID_2
        assert result["results"][1]["token_id"] == 2
        assert result["results"][1]["license_terms_ids"] == [3]

    def test_batch_mint_with_metadata(self, ip_asset_client):
        """Test batch minting with IP metadata"""
        license_terms_template = {
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

        # Create mock log for IPRegistered event
        mock_topic = Mock()
        mock_topic.hex.return_value = "0xip_registered_sig"
        mock_log = {"topics": [mock_topic]}
        
        # Mock keccak for event signature
        mock_keccak_result = Mock()
        mock_keccak_result.hex.return_value = "0xip_registered_sig"
        ip_asset_client.web3.keccak = Mock(return_value=mock_keccak_result)
        
        # Mock to_checksum_address
        ip_asset_client.web3.to_checksum_address = Mock(side_effect=lambda x: x)
        
        # Mock event processing
        mock_event = {"args": {"ipId": IP_ID_1, "tokenId": 1, "tokenContract": SPG_NFT_CONTRACT}}
        ip_asset_client.ip_asset_registry_client.contract.events.IPRegistered.process_log = Mock(
            return_value=mock_event
        )

        with patch.object(
            ip_asset_client,
            "mint_and_register_ip_asset_with_pil_terms",
            return_value={"encoded_tx_data": "0x1234"},
        ):
            with patch(
                "story_protocol_python_sdk.resources.IPAsset.build_and_send_transaction",
                return_value={
                    "tx_hash": TX_HASH,
                    "tx_receipt": {"logs": [mock_log]},
                },
            ):
                with patch.object(
                    ip_asset_client,
                    "_parse_tx_license_terms_attached_event_for_ip",
                    return_value=[1],
                ):
                    result = ip_asset_client.batch_mint_and_register_ip_asset_with_pil_terms(
                        args=[
                            {
                                "spg_nft_contract": SPG_NFT_CONTRACT,
                                "terms": [license_terms_template],
                                "ip_metadata": {
                                    "ip_metadata_uri": "https://example.com/metadata",
                                    "ip_metadata_hash": ZERO_HASH,
                                },
                            }
                        ]
                    )

        assert result["tx_hash"] == TX_HASH
        assert len(result["results"]) == 1

    def test_batch_mint_with_recipient(self, ip_asset_client):
        """Test batch minting with custom recipient"""
        recipient = "0x9999999999999999999999999999999999999999"
        license_terms_template = {
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

        # Create mock log for IPRegistered event
        mock_topic = Mock()
        mock_topic.hex.return_value = "0xip_registered_sig"
        mock_log = {"topics": [mock_topic]}
        
        # Mock keccak for event signature
        mock_keccak_result = Mock()
        mock_keccak_result.hex.return_value = "0xip_registered_sig"
        ip_asset_client.web3.keccak = Mock(return_value=mock_keccak_result)
        
        # Mock to_checksum_address
        ip_asset_client.web3.to_checksum_address = Mock(side_effect=lambda x: x)
        
        # Mock event processing
        mock_event = {"args": {"ipId": IP_ID_1, "tokenId": 1, "tokenContract": SPG_NFT_CONTRACT}}
        ip_asset_client.ip_asset_registry_client.contract.events.IPRegistered.process_log = Mock(
            return_value=mock_event
        )

        with patch.object(
            ip_asset_client,
            "mint_and_register_ip_asset_with_pil_terms",
            return_value={"encoded_tx_data": "0x1234"},
        ):
            with patch(
                "story_protocol_python_sdk.resources.IPAsset.build_and_send_transaction",
                return_value={
                    "tx_hash": TX_HASH,
                    "tx_receipt": {"logs": [mock_log]},
                },
            ):
                with patch.object(
                    ip_asset_client,
                    "_parse_tx_license_terms_attached_event_for_ip",
                    return_value=[1],
                ):
                    result = ip_asset_client.batch_mint_and_register_ip_asset_with_pil_terms(
                        args=[
                            {
                                "spg_nft_contract": SPG_NFT_CONTRACT,
                                "terms": [license_terms_template],
                                "recipient": recipient,
                            }
                        ]
                    )

        assert result["tx_hash"] == TX_HASH
        assert len(result["results"]) == 1

    def test_batch_mint_empty_args(self, ip_asset_client):
        """Test batch minting with empty args"""
        with patch(
            "story_protocol_python_sdk.resources.IPAsset.build_and_send_transaction",
            return_value={
                "tx_hash": TX_HASH,
                "tx_receipt": {"logs": []},
            },
        ):
            with patch.object(
                ip_asset_client,
                "_parse_tx_ip_registered_event",
                return_value=[],
            ):
                result = ip_asset_client.batch_mint_and_register_ip_asset_with_pil_terms(
                    args=[]
                )

        assert result["tx_hash"] == TX_HASH
        assert len(result["results"]) == 0
