import pytest

from story_protocol_python_sdk.types.resource.Royalty import NativeRoyaltyPolicy
from story_protocol_python_sdk.utils.constants import (
    ROYALTY_POLICY_LAP_ADDRESS,
    ROYALTY_POLICY_LRP_ADDRESS,
)
from story_protocol_python_sdk.utils.royalty_policy import (
    royalty_policy_input_to_address,
)


class TestRoyaltyPolicyInputToAddress:
    def test_none_input_returns_lap_address(self):
        """Test that None input returns LAP address"""
        result = royalty_policy_input_to_address(None)
        assert result == ROYALTY_POLICY_LAP_ADDRESS

    def test_lap_enum_returns_lap_address(self):
        """Test that NativeRoyaltyPolicy.LAP returns LAP address"""
        result = royalty_policy_input_to_address(NativeRoyaltyPolicy.LAP)
        assert result == ROYALTY_POLICY_LAP_ADDRESS

    def test_lrp_enum_returns_lrp_address(self):
        """Test that NativeRoyaltyPolicy.LRP returns LRP address"""
        result = royalty_policy_input_to_address(NativeRoyaltyPolicy.LRP)
        assert result == ROYALTY_POLICY_LRP_ADDRESS

    def test_valid_custom_address_returns_checksum_address(self):
        """Test that valid custom address returns checksum format address"""
        custom_address = "0x1234567890123456789012345678901234567890"
        result = royalty_policy_input_to_address(custom_address)
        assert result == "0x1234567890123456789012345678901234567890"

    def test_invalid_custom_address_raises_error(self):
        """Test that invalid custom address raises ValueError"""
        invalid_address = "invalid_address"
        with pytest.raises(ValueError):
            royalty_policy_input_to_address(invalid_address)
