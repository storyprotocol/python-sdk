from unittest.mock import MagicMock, Mock

import pytest

from story_protocol_python_sdk.utils.constants import ZERO_ADDRESS, ZERO_HASH
from story_protocol_python_sdk.utils.licensing_config_data import (
    LicensingConfig,
    LicensingConfigData,
    ValidatedLicensingConfig,
)


@pytest.fixture
def mock_module_registry_client():
    """Mock module registry client fixture with configurable registration status."""

    def _mock_module_registry_client(is_registered=True):
        return Mock(isRegistered=MagicMock(return_value=is_registered))

    return _mock_module_registry_client


class TestValidateLicenseConfig:
    def test_validate_license_config_default_values(self, mock_module_registry_client):
        """Test validate_license_config with no input returns default values."""
        result = LicensingConfigData.validate_license_config(
            mock_module_registry_client()
        )

        assert result == ValidatedLicensingConfig(
            isSet=False,
            mintingFee=0,
            licensingHook=ZERO_ADDRESS,
            hookData=ZERO_HASH,
            commercialRevShare=0,
            disabled=False,
            expectMinimumGroupRewardShare=0,
            expectGroupRewardPool=ZERO_ADDRESS,
        )

    def test_validate_license_config_valid_input(self, mock_module_registry_client):
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

        result = LicensingConfigData.validate_license_config(
            mock_module_registry_client(), input_config
        )

        assert result == ValidatedLicensingConfig(
            isSet=True,
            mintingFee=100,
            licensingHook=ZERO_ADDRESS,
            hookData="0xabcdef",
            commercialRevShare=50 * 10**6,
            disabled=False,
            expectMinimumGroupRewardShare=25 * 10**6,
            expectGroupRewardPool=ZERO_ADDRESS,
        )

    def test_validate_license_config_invalid_commercial_rev_share_negative(
        self, mock_module_registry_client
    ):
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
            LicensingConfigData.validate_license_config(
                mock_module_registry_client(), input_config
            )

    def test_validate_license_config_invalid_commercial_rev_share_too_high(
        self, mock_module_registry_client
    ):
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
            LicensingConfigData.validate_license_config(
                mock_module_registry_client(), input_config
            )

    def test_validate_license_config_invalid_expect_minimum_group_reward_share_negative(
        self, mock_module_registry_client
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
            LicensingConfigData.validate_license_config(
                mock_module_registry_client(), input_config
            )

    def test_validate_license_config_invalid_expect_minimum_group_reward_share_too_high(
        self, mock_module_registry_client
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
            LicensingConfigData.validate_license_config(
                mock_module_registry_client(), input_config
            )

    def test_validate_license_config_invalid_minting_fee_negative(
        self, mock_module_registry_client
    ):
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

        with pytest.raises(ValueError, match="The minting fee must be greater than 0."):
            LicensingConfigData.validate_license_config(
                mock_module_registry_client(), input_config
            )

    def test_validate_license_config_invalid_licensing_hook_address(
        self, mock_module_registry_client
    ):
        """Test validate_license_config raises error for invalid licensing_hook address."""
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
            LicensingConfigData.validate_license_config(
                mock_module_registry_client(), input_config
            )

    def test_validate_license_config_invalid_expect_group_reward_pool_address(
        self, mock_module_registry_client
    ):
        """Test validate_license_config raises error for invalid expect_group_reward_pool address."""
        input_config: LicensingConfig = {
            "is_set": False,
            "minting_fee": 0,
            "licensing_hook": ZERO_ADDRESS,
            "hook_data": ZERO_HASH,
            "commercial_rev_share": 0,
            "disabled": False,
            "expect_minimum_group_reward_share": 0,
            "expect_group_reward_pool": "invalid_address",
        }

        with pytest.raises(ValueError, match="Invalid address: invalid_address."):
            LicensingConfigData.validate_license_config(
                mock_module_registry_client(), input_config
            )

    def test_validate_license_config_unregistered_licensing_hook(
        self, mock_module_registry_client
    ):
        """Test validate_license_config raises error for unregistered licensing hook."""

        mock_client = mock_module_registry_client(is_registered=False)
        input_config: LicensingConfig = {
            "is_set": False,
            "minting_fee": 0,
            "licensing_hook": "0x1234567890123456789012345678901234567890",
            "hook_data": ZERO_HASH,
            "commercial_rev_share": 0,
            "disabled": False,
            "expect_minimum_group_reward_share": 0,
            "expect_group_reward_pool": ZERO_ADDRESS,
        }

        with pytest.raises(ValueError, match="The licensing hook is not registered."):
            LicensingConfigData.validate_license_config(mock_client, input_config)

    def test_validate_license_config_registered_licensing_hook(
        self, mock_module_registry_client
    ):
        """Test validate_license_config succeeds for registered licensing hook."""

        input_config: LicensingConfig = {
            "is_set": False,
            "minting_fee": 0,
            "licensing_hook": "0x1234567890123456789012345678901234567890",
            "hook_data": ZERO_HASH,
            "commercial_rev_share": 0,
            "disabled": False,
            "expect_minimum_group_reward_share": 0,
            "expect_group_reward_pool": ZERO_ADDRESS,
        }

        result = LicensingConfigData.validate_license_config(
            mock_module_registry_client(), input_config
        )

        assert result == ValidatedLicensingConfig(
            isSet=False,
            mintingFee=0,
            licensingHook="0x1234567890123456789012345678901234567890",
            hookData=ZERO_HASH,
            commercialRevShare=0,
            disabled=False,
            expectMinimumGroupRewardShare=0,
            expectGroupRewardPool=ZERO_ADDRESS,
        )

    def test_validate_license_config_zero_address_licensing_hook_skips_registration_check(
        self, mock_module_registry_client
    ):
        """Test validate_license_config skips registration check for ZERO_ADDRESS licensing hook."""
        input_config: LicensingConfig = {
            "is_set": False,
            "minting_fee": 0,
            "licensing_hook": ZERO_ADDRESS,
            "hook_data": ZERO_HASH,
            "commercial_rev_share": 0,
            "disabled": False,
            "expect_minimum_group_reward_share": 0,
            "expect_group_reward_pool": ZERO_ADDRESS,
        }

        result = LicensingConfigData.validate_license_config(
            mock_module_registry_client(), input_config
        )
        assert result == ValidatedLicensingConfig(
            isSet=False,
            mintingFee=0,
            licensingHook=ZERO_ADDRESS,
            hookData=ZERO_HASH,
            commercialRevShare=0,
            disabled=False,
            expectMinimumGroupRewardShare=0,
            expectGroupRewardPool=ZERO_ADDRESS,
        )


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
