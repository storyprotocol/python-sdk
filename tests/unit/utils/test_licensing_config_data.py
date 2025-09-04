import pytest

from story_protocol_python_sdk.utils.constants import ZERO_ADDRESS, ZERO_HASH
from story_protocol_python_sdk.utils.licensing_config_data import (
    LicensingConfig,
    LicensingConfigData,
)


class TestValidateLicenseConfig:
    def test_validate_license_config_default_values(self):
        """Test validate_license_config with no input returns default values."""
        result = LicensingConfigData.validate_license_config()
        assert result == LicensingConfig(
            is_set=False,
            minting_fee=0,
            licensing_hook=ZERO_ADDRESS,
            hook_data=ZERO_HASH,
            commercial_rev_share=0,
            disabled=False,
            expect_minimum_group_reward_share=0,
            expect_group_reward_pool=ZERO_ADDRESS,
        )

    def test_validate_license_config_valid_input(self):
        """Test validate_license_config with valid input."""
        input_config: LicensingConfig = {
            "is_set": True,
            "minting_fee": 100,
            "licensing_hook": ZERO_ADDRESS,
            "hook_data": "0xabcdef",
            "commercial_rev_share": 50,
            "disabled": False,
            "expect_minimum_group_reward_share": 25,
            "expect_group_reward_pool": ZERO_ADDRESS,
        }

        result = LicensingConfigData.validate_license_config(input_config)

        assert result == LicensingConfig(
            is_set=True,
            minting_fee=100,
            licensing_hook=ZERO_ADDRESS,
            hook_data="0xabcdef",
            commercial_rev_share=50 * 10**6,
            disabled=False,
            expect_minimum_group_reward_share=25 * 10**6,
            expect_group_reward_pool=ZERO_ADDRESS,
        )

    def test_validate_license_config_invalid_commercial_rev_share_negative(self):
        """Test validate_license_config raises error for negative commercial_rev_share."""
        input_config: LicensingConfig = {
            "is_set": False,
            "minting_fee": 0,
            "licensing_hook": ZERO_ADDRESS,
            "hook_data": ZERO_HASH,
            "commercial_rev_share": -1,
            "disabled": False,
            "expect_minimum_group_reward_share": 0,
            "expect_group_reward_pool": ZERO_ADDRESS,
        }

        with pytest.raises(
            ValueError,
            match="The commercial_rev_share must be between 0 and 100.",
        ):
            LicensingConfigData.validate_license_config(input_config)

    def test_validate_license_config_invalid_commercial_rev_share_too_high(self):
        """Test validate_license_config raises error for commercial_rev_share > 100."""
        input_config: LicensingConfig = {
            "is_set": False,
            "minting_fee": 0,
            "licensing_hook": ZERO_ADDRESS,
            "hook_data": ZERO_HASH,
            "commercial_rev_share": 101,
            "disabled": False,
            "expect_minimum_group_reward_share": 0,
            "expect_group_reward_pool": ZERO_ADDRESS,
        }

        with pytest.raises(
            ValueError,
            match="The commercial_rev_share must be between 0 and 100.",
        ):
            LicensingConfigData.validate_license_config(input_config)

    def test_validate_license_config_invalid_expect_minimum_group_reward_share_negative(
        self,
    ):
        """Test validate_license_config raises error for negative expect_minimum_group_reward_share."""
        input_config: LicensingConfig = {
            "is_set": False,
            "minting_fee": 0,
            "licensing_hook": ZERO_ADDRESS,
            "hook_data": ZERO_HASH,
            "commercial_rev_share": 0,
            "disabled": False,
            "expect_minimum_group_reward_share": -1,
            "expect_group_reward_pool": ZERO_ADDRESS,
        }

        with pytest.raises(
            ValueError,
            match="The expect_minimum_group_reward_share must be between 0 and 100.",
        ):
            LicensingConfigData.validate_license_config(input_config)

    def test_validate_license_config_invalid_expect_minimum_group_reward_share_too_high(
        self,
    ):
        """Test validate_license_config raises error for expect_minimum_group_reward_share > 100."""
        input_config: LicensingConfig = {
            "is_set": False,
            "minting_fee": 0,
            "licensing_hook": ZERO_ADDRESS,
            "hook_data": ZERO_HASH,
            "commercial_rev_share": 0,
            "disabled": False,
            "expect_minimum_group_reward_share": 101,
            "expect_group_reward_pool": ZERO_ADDRESS,
        }

        with pytest.raises(
            ValueError,
            match="The expect_minimum_group_reward_share must be between 0 and 100.",
        ):
            LicensingConfigData.validate_license_config(input_config)

    def test_validate_license_config_invalid_minting_fee_negative(self):
        """Test validate_license_config raises error for negative minting_fee."""
        input_config: LicensingConfig = {
            "is_set": False,
            "minting_fee": -1,
            "licensing_hook": ZERO_ADDRESS,
            "hook_data": ZERO_HASH,
            "commercial_rev_share": 0,
            "disabled": False,
            "expect_minimum_group_reward_share": 0,
            "expect_group_reward_pool": ZERO_ADDRESS,
        }

        with pytest.raises(ValueError, match="The minting_fee must be greater than 0."):
            LicensingConfigData.validate_license_config(input_config)

    def test_validate_license_config_invalid_address(self):
        """Test validate_license_config raises error for invalid address."""
        input_config: LicensingConfig = {
            "is_set": False,
            "minting_fee": 0,
            "licensing_hook": "invalid_address",
            "hook_data": ZERO_HASH,
            "commercial_rev_share": 0,
            "disabled": False,
            "expect_minimum_group_reward_share": 0,
            "expect_group_reward_pool": ZERO_ADDRESS,
        }

        with pytest.raises(ValueError, match="Invalid address: invalid_address."):
            LicensingConfigData.validate_license_config(input_config)


class TestLicensingConfigFromTuple:
    def test_licensing_config_from_tuple(self):
        """Test licensing_config_from_tuple with valid input."""
        input_tuple = (
            True,
            100,
            ZERO_ADDRESS,
            ZERO_HASH,
            50,
            False,
            25,
            ZERO_ADDRESS,
        )

        result = LicensingConfigData.from_tuple(input_tuple)

        assert result == LicensingConfig(
            is_set=True,
            minting_fee=100,
            licensing_hook=ZERO_ADDRESS,
            hook_data=ZERO_HASH,
            commercial_rev_share=50,
            disabled=False,
            expect_minimum_group_reward_share=25,
            expect_group_reward_pool=ZERO_ADDRESS,
        )
