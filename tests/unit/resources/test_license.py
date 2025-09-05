from typing import Callable
from unittest.mock import patch

import pytest
from _pytest.fixtures import fixture
from web3 import Web3

from story_protocol_python_sdk.resources.License import License
from story_protocol_python_sdk.utils.constants import ZERO_ADDRESS
from story_protocol_python_sdk.utils.licensing_config_data import LicensingConfig
from tests.unit.fixtures.data import ADDRESS, CHAIN_ID, IP_ID, TX_HASH
from tests.unit.resources.test_ip_account import ZERO_HASH


@fixture
def license(mock_web3, mock_account) -> License:
    return License(web3=mock_web3, account=mock_account, chain_id=CHAIN_ID)


class TestPILTermsRegistration:
    """Tests for PIL (Programmable IP License) terms registration."""

    def test_register_pil_terms_license_terms_id_registered(self, license: License):
        with patch.object(
            license.license_template_client, "getLicenseTermsId", return_value=1
        ), patch.object(
            license.license_terms_util.royalty_module_client,
            "isWhitelistedRoyaltyPolicy",
            return_value=True,
        ), patch.object(
            license.license_terms_util.royalty_module_client,
            "isWhitelistedRoyaltyToken",
            return_value=True,
        ):

            response = license.register_pil_terms(
                default_minting_fee=1513,
                currency=ADDRESS,
                royalty_policy=ADDRESS,
                transferable=False,
                expiration=0,
                commercial_use=True,
                commercial_attribution=False,
                commercializer_checker=ZERO_ADDRESS,
                commercializer_checker_data="0x",
                commercial_rev_share=0,
                commercial_rev_ceiling=0,
                derivatives_allowed=False,
                derivatives_attribution=False,
                derivatives_approval=False,
                derivatives_reciprocal=False,
                derivative_rev_ceiling=0,
                uri="",
            )
            assert response["license_terms_id"] == 1
            assert "tx_hash" not in response

    def test_register_pil_terms_success(self, license: License):
        with patch.object(
            license.license_template_client, "getLicenseTermsId", return_value=0
        ), patch.object(
            license.license_terms_util.royalty_module_client,
            "isWhitelistedRoyaltyPolicy",
            return_value=True,
        ), patch.object(
            license.license_terms_util.royalty_module_client,
            "isWhitelistedRoyaltyToken",
            return_value=True,
        ), patch.object(
            license.license_template_client,
            "build_registerLicenseTerms_transaction",
            return_value={
                "from": ADDRESS,
                "nonce": 1,
                "gas": 2000000,
                "gasPrice": Web3.to_wei("100", "gwei"),
            },
        ):

            response = license.register_pil_terms(
                transferable=False,
                royalty_policy=ADDRESS,
                default_minting_fee=1513,
                expiration=0,
                commercial_use=True,
                commercial_attribution=False,
                commercializer_checker=ZERO_ADDRESS,
                commercializer_checker_data="0x",
                commercial_rev_share=90,
                commercial_rev_ceiling=0,
                derivatives_allowed=False,
                derivatives_attribution=False,
                derivatives_approval=False,
                derivatives_reciprocal=False,
                derivative_rev_ceiling=0,
                currency=ADDRESS,
                uri="",
            )

            assert "tx_hash" in response
            assert response["tx_hash"] == TX_HASH.hex()
            assert isinstance(response["tx_hash"], str)

    def test_register_pil_terms_commercial_rev_share_error_more_than_100(
        self, license: License
    ):
        with patch.object(
            license.license_template_client, "getLicenseTermsId", return_value=0
        ), patch.object(
            license.license_terms_util.royalty_module_client,
            "isWhitelistedRoyaltyPolicy",
            return_value=True,
        ), patch.object(
            license.license_terms_util.royalty_module_client,
            "isWhitelistedRoyaltyToken",
            return_value=True,
        ):

            with pytest.raises(
                ValueError, match="commercial_rev_share should be between 0 and 100."
            ):
                license.register_pil_terms(
                    transferable=False,
                    royalty_policy=ADDRESS,
                    default_minting_fee=1,
                    expiration=0,
                    commercial_use=True,
                    commercial_attribution=False,
                    commercializer_checker=ZERO_ADDRESS,
                    commercializer_checker_data="0x",
                    commercial_rev_share=101,
                    commercial_rev_ceiling=0,
                    derivatives_allowed=False,
                    derivatives_attribution=False,
                    derivatives_approval=False,
                    derivatives_reciprocal=False,
                    derivative_rev_ceiling=0,
                    currency=ADDRESS,
                    uri="",
                )

    def test_register_pil_terms_commercial_rev_share_error_less_than_0(
        self, license: License
    ):
        with patch.object(
            license.license_template_client, "getLicenseTermsId", return_value=0
        ), patch.object(
            license.license_terms_util.royalty_module_client,
            "isWhitelistedRoyaltyPolicy",
            return_value=True,
        ), patch.object(
            license.license_terms_util.royalty_module_client,
            "isWhitelistedRoyaltyToken",
            return_value=True,
        ):

            with pytest.raises(
                ValueError, match="commercial_rev_share should be between 0 and 100."
            ):
                license.register_pil_terms(
                    transferable=False,
                    royalty_policy=ADDRESS,
                    default_minting_fee=1,
                    expiration=0,
                    commercial_use=True,
                    commercial_attribution=False,
                    commercializer_checker=ZERO_ADDRESS,
                    commercializer_checker_data="0x",
                    commercial_rev_share=-1,
                    commercial_rev_ceiling=0,
                    derivatives_allowed=False,
                    derivatives_attribution=False,
                    derivatives_approval=False,
                    derivatives_reciprocal=False,
                    derivative_rev_ceiling=0,
                    currency=ADDRESS,
                    uri="",
                )


class TestNonComSocialRemixingPIL:
    """Tests for non-commercial social remixing PIL functionality."""

    def test_register_non_com_social_remixing_pil_license_terms_id_registered(
        self, license: License
    ):
        with patch.object(
            license.license_template_client, "getLicenseTermsId", return_value=1
        ):
            response = license.register_non_com_social_remixing_pil()
            assert response["license_terms_id"] == 1
            assert "tx_hash" not in response

    def test_register_non_com_social_remixing_pil_success(self, license: License):
        with patch.object(
            license.license_template_client, "getLicenseTermsId", return_value=0
        ), patch.object(
            license.license_template_client,
            "build_registerLicenseTerms_transaction",
            return_value={
                "from": ADDRESS,
                "nonce": 1,
                "gas": 2000000,
                "gasPrice": Web3.to_wei("100", "gwei"),
            },
        ), patch.object(
            license, "_parse_tx_license_terms_registered_event", return_value=1
        ):

            response = license.register_non_com_social_remixing_pil()
            assert "tx_hash" in response
            assert response["tx_hash"] == TX_HASH.hex()
            assert isinstance(response["tx_hash"], str)
            assert "license_terms_id" in response
            assert response["license_terms_id"] == 1

    def test_register_non_com_social_remixing_pil_error(self, license: License):
        with patch.object(
            license.license_template_client, "getLicenseTermsId", return_value=0
        ), patch.object(
            license.license_terms_util.royalty_module_client,
            "isWhitelistedRoyaltyPolicy",
            return_value=True,
        ), patch.object(
            license.license_template_client,
            "build_registerLicenseTerms_transaction",
            side_effect=Exception("request fail."),
        ):

            with pytest.raises(Exception, match="request fail."):
                license.register_non_com_social_remixing_pil()


class TestCommercialUsePIL:
    """Tests for commercial use PIL functionality."""

    def test_register_commercial_use_pil_license_terms_id_registered(
        self, license: License
    ):
        with patch.object(
            license.license_template_client, "getLicenseTermsId", return_value=1
        ):
            response = license.register_commercial_use_pil(
                default_minting_fee=1, currency=ZERO_ADDRESS
            )
            assert response["license_terms_id"] == 1
            assert "tx_hash" not in response

    def test_register_commercial_use_pil_success_without_logs(self, license: License):
        with patch.object(
            license.license_template_client, "getLicenseTermsId", return_value=0
        ), patch.object(
            license.license_terms_util.royalty_module_client,
            "isWhitelistedRoyaltyPolicy",
            return_value=True,
        ), patch.object(
            license.license_template_client,
            "build_registerLicenseTerms_transaction",
            return_value={
                "from": ADDRESS,
                "nonce": 1,
                "gas": 2000000,
                "gasPrice": Web3.to_wei("100", "gwei"),
            },
        ), patch.object(
            license, "_parse_tx_license_terms_registered_event", return_value=1
        ):

            response = license.register_commercial_use_pil(
                default_minting_fee=1, currency=ZERO_ADDRESS
            )
            assert response is not None
            assert "tx_hash" in response
            assert response["tx_hash"] == TX_HASH.hex()
            assert isinstance(response["tx_hash"], str)

    def test_register_commercial_use_pil_error(self, license: License):
        with patch.object(
            license.license_template_client, "getLicenseTermsId", return_value=0
        ), patch.object(
            license.license_terms_util.royalty_module_client,
            "isWhitelistedRoyaltyPolicy",
            return_value=True,
        ), patch.object(
            license.license_template_client,
            "build_registerLicenseTerms_transaction",
            side_effect=Exception("request fail."),
        ):
            with pytest.raises(Exception, match="request fail."):
                license.register_commercial_use_pil(
                    default_minting_fee=1, currency=ZERO_ADDRESS
                )


class TestCommercialRemixPIL:
    """Tests for commercial remix PIL functionality."""

    def test_register_commercial_remix_pil_license_terms_id_registered(
        self, license: License
    ):
        with patch.object(
            license.license_template_client, "getLicenseTermsId", return_value=1
        ), patch.object(
            license.license_terms_util.royalty_module_client,
            "isWhitelistedRoyaltyPolicy",
            return_value=True,
        ):
            response = license.register_commercial_remix_pil(
                default_minting_fee=1,
                commercial_rev_share=100,
                currency=ZERO_ADDRESS,
                royalty_policy=ZERO_ADDRESS,
            )
            assert response["license_terms_id"] == 1
            assert "tx_hash" not in response

    def test_register_commercial_remix_pil_success(self, license: License):
        with patch.object(
            license.license_template_client, "getLicenseTermsId", return_value=0
        ), patch.object(
            license.license_terms_util.royalty_module_client,
            "isWhitelistedRoyaltyPolicy",
            return_value=True,
        ), patch.object(
            license.license_template_client,
            "build_registerLicenseTerms_transaction",
            return_value={
                "from": ADDRESS,
                "nonce": 1,
                "gas": 2000000,
                "gasPrice": Web3.to_wei("100", "gwei"),
            },
        ), patch.object(
            license, "_parse_tx_license_terms_registered_event", return_value=1
        ):

            response = license.register_commercial_remix_pil(
                default_minting_fee=1,
                commercial_rev_share=100,
                currency=ZERO_ADDRESS,
                royalty_policy=ZERO_ADDRESS,
            )
            assert response is not None
            assert "tx_hash" in response
            assert response["tx_hash"] == TX_HASH.hex()
            assert isinstance(response["tx_hash"], str)


class TestLicenseAttachment:
    """Tests for license attachment functionality."""

    def test_attach_license_terms_ip_not_registered(self, license: License):
        with patch.object(
            license.ip_asset_registry_client, "isRegistered", return_value=False
        ):
            with pytest.raises(
                ValueError, match=f"The IP with id {ZERO_ADDRESS} is not registered."
            ):
                license.attach_license_terms(
                    ip_id=ZERO_ADDRESS,
                    license_template=ZERO_ADDRESS,
                    license_terms_id=1,
                )

    def test_attach_license_terms_license_terms_not_exist(self, license: License):
        with patch.object(
            license.ip_asset_registry_client, "isRegistered", return_value=True
        ), patch.object(license.license_registry_client, "exists", return_value=False):
            with pytest.raises(ValueError, match="License terms id 1 do not exist."):
                license.attach_license_terms(
                    ip_id=ZERO_ADDRESS,
                    license_template=ZERO_ADDRESS,
                    license_terms_id=1,
                )

    def test_attach_license_terms_already_attached(self, license):
        with patch.object(
            license.ip_asset_registry_client, "isRegistered", return_value=True
        ), patch.object(
            license.license_registry_client, "exists", return_value=True
        ), patch.object(
            license.license_registry_client,
            "hasIpAttachedLicenseTerms",
            return_value=True,
        ):
            with pytest.raises(
                ValueError,
                match=f"License terms id 1 is already attached to the IP with id {ZERO_ADDRESS}.",
            ):
                license.attach_license_terms(
                    ip_id=ZERO_ADDRESS,
                    license_template=ZERO_ADDRESS,
                    license_terms_id=1,
                )

    def test_attach_license_terms_success(self, license: License):
        with patch.object(
            license.ip_asset_registry_client, "isRegistered", return_value=True
        ), patch.object(
            license.license_registry_client, "exists", return_value=True
        ), patch.object(
            license.license_registry_client,
            "hasIpAttachedLicenseTerms",
            return_value=False,
        ), patch.object(
            license.licensing_module_client,
            "build_attachLicenseTerms_transaction",
            return_value={
                "from": ADDRESS,
                "nonce": 1,
                "gas": 2000000,
                "gasPrice": Web3.to_wei("100", "gwei"),
            },
        ), patch.object(
            license, "_parse_tx_license_terms_registered_event", return_value=1
        ):

            response = license.attach_license_terms(
                ip_id=ZERO_ADDRESS, license_template=ZERO_ADDRESS, license_terms_id=1
            )

            assert "tx_hash" in response
            assert response["tx_hash"] == TX_HASH.hex()
            assert isinstance(response["tx_hash"], str)


class TestLicenseTokens:
    """Tests for license token minting functionality."""

    def test_mint_license_tokens_licensor_ip_not_registered(self, license: License):
        with patch.object(
            license.ip_asset_registry_client, "isRegistered", return_value=False
        ):
            with pytest.raises(
                ValueError,
                match=f"The licensor IP with id {ZERO_ADDRESS} is not registered.",
            ):
                license.mint_license_tokens(
                    licensor_ip_id=ZERO_ADDRESS,
                    license_template=ZERO_ADDRESS,
                    license_terms_id=1,
                    amount=1,
                    receiver=ZERO_ADDRESS,
                )

    def test_mint_license_tokens_license_terms_not_exist(self, license: License):
        with patch.object(
            license.ip_asset_registry_client, "isRegistered", return_value=True
        ), patch.object(license.license_template_client, "exists", return_value=False):
            with pytest.raises(ValueError, match="License terms id 1 do not exist."):
                license.mint_license_tokens(
                    licensor_ip_id=ZERO_ADDRESS,
                    license_template=ZERO_ADDRESS,
                    license_terms_id=1,
                    amount=1,
                    receiver=ZERO_ADDRESS,
                )

    def test_mint_license_tokens_not_attached(self, license: License):
        with patch.object(
            license.ip_asset_registry_client, "isRegistered", return_value=True
        ), patch.object(
            license.license_template_client, "exists", return_value=True
        ), patch.object(
            license.license_registry_client,
            "hasIpAttachedLicenseTerms",
            return_value=False,
        ):
            with pytest.raises(
                ValueError,
                match=f"License terms id 1 is not attached to the IP with id {ZERO_ADDRESS}.",
            ):
                license.mint_license_tokens(
                    licensor_ip_id=ZERO_ADDRESS,
                    license_template=ZERO_ADDRESS,
                    license_terms_id=1,
                    amount=1,
                    receiver=ZERO_ADDRESS,
                )

    def test_mint_license_tokens_invalid_template(self, license: License):
        with patch.object(
            license.ip_asset_registry_client, "isRegistered", return_value=True
        ):
            with pytest.raises(ValueError, match="Invalid address: invalid address"):
                license.mint_license_tokens(
                    licensor_ip_id=ZERO_ADDRESS,
                    license_template="invalid address",
                    license_terms_id=1,
                    amount=1,
                    receiver=ZERO_ADDRESS,
                )

    def test_mint_license_tokens_invalid_receiver(self, license: License):
        with patch.object(
            license.ip_asset_registry_client, "isRegistered", return_value=True
        ):
            with pytest.raises(ValueError, match="Invalid address: invalid address"):
                license.mint_license_tokens(
                    licensor_ip_id=ZERO_ADDRESS,
                    license_template=ZERO_ADDRESS,
                    license_terms_id=1,
                    amount=1,
                    receiver="invalid address",
                )

    def test_mint_license_tokens_success(self, license: License):
        with patch.object(
            license.ip_asset_registry_client, "isRegistered", return_value=True
        ), patch.object(
            license.license_template_client, "exists", return_value=True
        ), patch.object(
            license.license_registry_client,
            "hasIpAttachedLicenseTerms",
            return_value=True,
        ), patch.object(
            license.licensing_module_client,
            "build_mintLicenseTokens_transaction",
            return_value={
                "from": ADDRESS,
                "nonce": 1,
                "gas": 2000000,
                "gasPrice": Web3.to_wei("100", "gwei"),
            },
        ), patch.object(
            license, "_parse_tx_license_terms_registered_event", return_value=1
        ):

            response = license.mint_license_tokens(
                licensor_ip_id=ZERO_ADDRESS,
                license_template=ZERO_ADDRESS,
                license_terms_id=1,
                amount=1,
                receiver=ZERO_ADDRESS,
            )

            assert "tx_hash" in response
            assert response["tx_hash"] == TX_HASH.hex()
            assert isinstance(response["tx_hash"], str)


class TestLicenseTerms:
    """Tests for retrieving license terms."""

    def test_get_license_terms_success(self, license: License):
        mock_response = {
            "terms": {
                "transferable": True,
                "royaltyPolicy": ZERO_ADDRESS,
                "defaultMintingFee": 1,
                "expiration": 1,
                "commercialUse": True,
                "commercialAttribution": True,
                "commercializerChecker": ZERO_ADDRESS,
                "commercializerCheckerData": ZERO_ADDRESS,
                "commercialRevShare": 100,
                "commercialRevCeiling": 1,
                "derivativesAllowed": True,
                "derivativesAttribution": True,
                "derivativesApproval": True,
                "derivativesReciprocal": True,
                "derivativeRevCeiling": 1,
                "currency": ZERO_ADDRESS,
                "uri": "string",
            }
        }
        with patch.object(
            license.license_template_client,
            "getLicenseTerms",
            return_value=mock_response,
        ):
            response = license.get_license_terms(1)
            assert response == mock_response

    def test_get_license_terms_not_exist(self, license: License):
        with patch.object(
            license.license_template_client,
            "getLicenseTerms",
            side_effect=Exception("Given licenseTermsId is not exist."),
        ):
            with pytest.raises(
                ValueError,
                match="Failed to get license terms: Given licenseTermsId is not exist.",
            ):
                license.get_license_terms(1)


@fixture
def patch_is_registered(license: License) -> Callable:
    def _patch(is_registered: bool = True):
        return patch.object(
            license.ip_asset_registry_client, "isRegistered", return_value=is_registered
        )

    return _patch


@fixture
def patch_exists(license: License) -> Callable:
    def _patch(exists: bool = True):
        return patch.object(
            license.license_template_client, "exists", return_value=exists
        )

    return _patch


@fixture
def patch_has_ip_attached_license_terms(license: License) -> Callable:
    def _patch(has_ip_attached_license_terms: bool = True):
        return patch.object(
            license.license_registry_client,
            "hasIpAttachedLicenseTerms",
            return_value=has_ip_attached_license_terms,
        )

    return _patch


@fixture
def default_licensing_config() -> LicensingConfig:
    """Default licensing configuration for testing."""
    return {
        "is_set": True,
        "minting_fee": 1,
        "licensing_hook": ZERO_ADDRESS,
        "hook_data": "0x",
        "commercial_rev_share": 0,
        "disabled": False,
        "expect_minimum_group_reward_share": 0,
        "expect_group_reward_pool": ZERO_ADDRESS,
    }


class TestMintLicenseTokens:
    def test_default_value_when_not_provided(
        self,
        license: License,
        patch_is_registered,
        patch_exists,
        patch_has_ip_attached_license_terms,
    ):
        with patch_is_registered(), patch_exists(), patch_has_ip_attached_license_terms():
            with patch.object(
                license.licensing_module_client,
                "build_mintLicenseTokens_transaction",
            ) as mock_build_mintLicenseTokens_transaction:

                license.mint_license_tokens(
                    licensor_ip_id=IP_ID,
                    license_template=ADDRESS,
                    license_terms_id=1,
                    amount=1,
                    receiver=ZERO_ADDRESS,
                )
            call_args = mock_build_mintLicenseTokens_transaction.call_args[0]
            assert call_args[6] == 0  # max_minting_fee
            assert call_args[7] == 100 * 10**6  # max_revenue_share

    def test_call_value_when_provided(
        self,
        license: License,
        patch_is_registered,
        patch_exists,
        patch_has_ip_attached_license_terms,
    ):
        with patch_is_registered(), patch_exists(), patch_has_ip_attached_license_terms():
            with patch.object(
                license.licensing_module_client,
                "build_mintLicenseTokens_transaction",
            ) as mock_build_mintLicenseTokens_transaction:

                license.mint_license_tokens(
                    licensor_ip_id=IP_ID,
                    license_template=ADDRESS,
                    license_terms_id=1,
                    amount=1,
                    receiver=ZERO_ADDRESS,
                    max_revenue_share=10,
                    max_minting_fee=10,
                )
            call_args = mock_build_mintLicenseTokens_transaction.call_args[0]
            assert call_args[6] == 10  # max_minting_fee
            assert call_args[7] == 10 * 10**6  # max_revenue_share


class TestSetLicensingConfig:
    """Tests for setLicensingConfig validation errors in execution order."""

    def test_set_licensing_config_negative_minting_fee(
        self, license: License, default_licensing_config: LicensingConfig
    ):
        """Test validation error when minting fee is negative."""
        config: LicensingConfig = default_licensing_config.copy()
        config["minting_fee"] = -1

        with pytest.raises(
            ValueError,
            match="Failed to set licensing config: The minting fee must be greater than 0.",
        ):
            license.set_licensing_config(
                ip_id=ZERO_ADDRESS,
                license_terms_id=1,
                licensing_config=config,
            )

    def test_set_licensing_config_invalid_licensing_hook_address(
        self, license: License, default_licensing_config: LicensingConfig
    ):
        """Test validation error when licensing hook is not a valid address."""
        config: LicensingConfig = default_licensing_config.copy()
        config["licensing_hook"] = "invalid_hook_address"

        with pytest.raises(
            ValueError,
            match="Failed to set licensing config: Invalid address: invalid_hook_address.",
        ):
            license.set_licensing_config(
                ip_id=ZERO_ADDRESS,
                license_terms_id=1,
                licensing_config=config,
            )

    def test_set_licensing_config_unregistered_licensing_hook(
        self, license: License, default_licensing_config: LicensingConfig
    ):
        """Test validation error when licensing hook is not registered."""
        custom_hook_address = "0x1234567890123456789012345678901234567890"
        config: LicensingConfig = default_licensing_config.copy()
        config["licensing_hook"] = custom_hook_address

        with patch.object(
            license.module_registry_client, "isRegistered", return_value=False
        ):
            with pytest.raises(
                ValueError,
                match="Failed to set licensing config: The licensing hook is not registered.",
            ):
                license.set_licensing_config(
                    ip_id=ZERO_ADDRESS,
                    license_terms_id=1,
                    licensing_config=config,
                )

    def test_set_licensing_config_commercial_rev_share_below_zero(
        self, license: License, default_licensing_config: LicensingConfig
    ):
        """Test validation error when commercial revenue share is below 0%."""
        config: LicensingConfig = default_licensing_config.copy()
        config["commercial_rev_share"] = -1  # < 0%

        with pytest.raises(
            ValueError,
            match="Failed to set licensing config: The commercial_rev_share must be between 0 and 100.",
        ):
            license.set_licensing_config(
                ip_id=ZERO_ADDRESS,
                license_terms_id=1,
                licensing_config=config,
            )

    def test_set_licensing_config_commercial_rev_share_above_100(
        self, license: License, default_licensing_config: LicensingConfig
    ):
        """Test validation error when commercial revenue share is above 100%."""
        config: LicensingConfig = default_licensing_config.copy()
        config["commercial_rev_share"] = 101  # > 100%

        with pytest.raises(
            ValueError,
            match="Failed to set licensing config: The commercial_rev_share must be between 0 and 100.",
        ):
            license.set_licensing_config(
                ip_id=ZERO_ADDRESS,
                license_terms_id=1,
                licensing_config=config,
            )

    def test_set_licensing_config_expect_minimum_group_reward_share_below_zero(
        self, license: License, default_licensing_config: LicensingConfig
    ):
        """Test validation error when expect minimum group reward share is below 0%."""
        config: LicensingConfig = default_licensing_config.copy()
        config["expect_minimum_group_reward_share"] = -1  # < 0%

        with pytest.raises(
            ValueError,
            match="Failed to set licensing config: The expect_minimum_group_reward_share must be between 0 and 100.",
        ):
            license.set_licensing_config(
                ip_id=ZERO_ADDRESS,
                license_terms_id=1,
                licensing_config=config,
            )

    def test_set_licensing_config_expect_minimum_group_reward_share_above_100(
        self, license: License, default_licensing_config: LicensingConfig
    ):
        """Test validation error when expect minimum group reward share is above 100%."""
        config: LicensingConfig = default_licensing_config.copy()
        config["expect_minimum_group_reward_share"] = 101  # > 100%

        with pytest.raises(
            ValueError,
            match="Failed to set licensing config: The expect_minimum_group_reward_share must be between 0 and 100.",
        ):
            license.set_licensing_config(
                ip_id=ZERO_ADDRESS,
                license_terms_id=1,
                licensing_config=config,
            )

    def test_set_licensing_config_invalid_group_reward_pool_address(
        self, license: License, default_licensing_config: LicensingConfig
    ):
        """Test validation error when group reward pool is not a valid address."""
        config: LicensingConfig = default_licensing_config.copy()
        config["expect_group_reward_pool"] = "invalid_pool_address"

        with pytest.raises(
            ValueError,
            match="Failed to set licensing config: Invalid address: invalid_pool_address.",
        ):
            license.set_licensing_config(
                ip_id=ZERO_ADDRESS,
                license_terms_id=1,
                licensing_config=config,
            )

    def test_set_licensing_config_invalid_license_template_address(
        self, license: License, default_licensing_config: LicensingConfig
    ):
        """Test validation error when license template is not a valid address."""
        with pytest.raises(
            ValueError,
            match="Failed to set licensing config: Invalid address: invalid_template.",
        ):
            license.set_licensing_config(
                ip_id=ZERO_ADDRESS,
                license_terms_id=1,
                license_template="invalid_template",
                licensing_config=default_licensing_config,
            )

    def test_set_licensing_config_zero_address_template_with_non_zero_rev_share(
        self,
        license,
        default_licensing_config: LicensingConfig,
    ):
        """Test validation error when license template is zero address but commercial revenue share is not zero."""
        config: LicensingConfig = default_licensing_config.copy()
        config["commercial_rev_share"] = 10  # Non-zero

        with patch.object(
            license.ip_asset_registry_client, "isRegistered", return_value=True
        ):
            with pytest.raises(
                ValueError,
                match="Failed to set licensing config: The license template cannot be zero address if commercial revenue share is not zero.",
            ):
                license.set_licensing_config(
                    ip_id=ZERO_ADDRESS,
                    license_terms_id=0,
                    license_template=ZERO_ADDRESS,
                    licensing_config=config,
                )

    def test_set_licensing_config_invalid_ip_id_address(
        self, license: License, default_licensing_config: LicensingConfig
    ):
        """Test validation error when IP ID is not a valid address."""
        with pytest.raises(
            ValueError,
            match="Failed to set licensing config: Invalid address: invalid_address.",
        ):
            license.set_licensing_config(
                ip_id="invalid_address",
                license_terms_id=1,
                licensing_config=default_licensing_config,
            )

    def test_set_licensing_config_ip_not_registered(
        self,
        license: License,
        default_licensing_config: LicensingConfig,
        patch_is_registered,
    ):
        """Test validation error when IP is not registered."""
        with patch_is_registered(is_registered=False):
            with pytest.raises(
                ValueError,
                match=f"Failed to set licensing config: The licensor IP with id {ZERO_ADDRESS} is not registered.",
            ):
                license.set_licensing_config(
                    ip_id=ZERO_ADDRESS,
                    license_terms_id=1,
                    licensing_config=default_licensing_config,
                )

    def test_set_licensing_config_license_terms_not_exist(
        self,
        license: License,
        default_licensing_config: LicensingConfig,
        patch_is_registered,
        patch_exists,
    ):
        """Test validation error when license terms ID does not exist."""
        with patch_is_registered(is_registered=True), patch_exists(exists=False):
            with pytest.raises(
                ValueError,
                match="Failed to set licensing config: License terms id 1 does not exist.",
            ):
                license.set_licensing_config(
                    ip_id=ZERO_ADDRESS,
                    license_terms_id=1,
                    licensing_config=default_licensing_config,
                )

    def test_set_licensing_config_template_zero_address_with_non_zero_terms_id(
        self,
        license: License,
        default_licensing_config: LicensingConfig,
        patch_is_registered,
    ):
        """Test validation error when license template is zero address but license terms ID is not zero."""
        with patch_is_registered():
            with pytest.raises(
                ValueError,
                match="Failed to set licensing config: The license template is zero address but license terms id is not zero.",
            ):
                license.set_licensing_config(
                    ip_id=ZERO_ADDRESS,
                    license_terms_id=1,
                    license_template=ZERO_ADDRESS,
                    licensing_config=default_licensing_config,
                )

    def test_set_licensing_config_success_with_default_template(
        self,
        license: License,
        patch_is_registered,
        patch_exists,
    ):
        """Test successful licensing config setting with default license template."""
        with patch_is_registered(), patch_exists():
            with patch.object(
                license.licensing_module_client,
                "build_setLicensingConfig_transaction",
                return_value={"nonce": 1},
            ) as mock_build_setLicensingConfig_transaction:

                result = license.set_licensing_config(
                    ip_id=ZERO_ADDRESS,
                    license_terms_id=1,
                    licensing_config=LicensingConfig(
                        is_set=True,
                        minting_fee=1,
                        licensing_hook=ZERO_ADDRESS,
                        hook_data=ZERO_HASH,
                        commercial_rev_share=10,
                        disabled=False,
                        expect_minimum_group_reward_share=100,
                        expect_group_reward_pool=ZERO_ADDRESS,
                    ),
                )

            assert result["success"] is True
            assert result["tx_hash"] == TX_HASH.hex()  # Convert bytes to hex string
            assert (
                mock_build_setLicensingConfig_transaction.call_args[0][1]
                == license.license_template_client.contract.address
            )
            assert mock_build_setLicensingConfig_transaction.call_args[0][3] == {
                "isSet": True,
                "mintingFee": 1,
                "licensingHook": ZERO_ADDRESS,
                "hookData": ZERO_HASH,
                "commercialRevShare": 10 * 10**6,
                "disabled": False,
                "expectMinimumGroupRewardShare": 100 * 10**6,
                "expectGroupRewardPool": ZERO_ADDRESS,
            }

    def test_set_licensing_config_success_with_custom_template(
        self,
        license: License,
        default_licensing_config: LicensingConfig,
        patch_is_registered,
        patch_exists,
    ):
        """Test successful licensing config setting with custom license template."""
        custom_template = "0x1234567890123456789012345678901234567890"

        with patch_is_registered(is_registered=True), patch_exists(exists=True):
            with patch.object(
                license.licensing_module_client,
                "build_setLicensingConfig_transaction",
                return_value={"nonce": 1},
            ) as mock_build_setLicensingConfig_transaction:
                result = license.set_licensing_config(
                    ip_id=ZERO_ADDRESS,
                    license_terms_id=1,
                    license_template=custom_template,
                    licensing_config=default_licensing_config,
                )

            assert result["success"] is True
            assert result["tx_hash"] == TX_HASH.hex()
            assert (
                mock_build_setLicensingConfig_transaction.call_args[0][1]
                == custom_template
            )
            assert mock_build_setLicensingConfig_transaction.call_args[0][3] == {
                "isSet": True,
                "mintingFee": 1,
                "licensingHook": ZERO_ADDRESS,
                "hookData": "0x",
                "commercialRevShare": 0,
                "disabled": False,
                "expectMinimumGroupRewardShare": 0,
                "expectGroupRewardPool": ZERO_ADDRESS,
            }

    def test_set_licensing_config_success_with_tx_options(
        self,
        license: License,
        default_licensing_config: LicensingConfig,
        patch_is_registered,
        patch_exists,
    ):
        """Test successful licensing config setting with transaction options."""
        tx_options = {"gasPrice": 1, "nonce": 3}

        with patch_is_registered(is_registered=True), patch_exists(exists=True):
            with patch.object(
                license.licensing_module_client,
                "build_setLicensingConfig_transaction",
                return_value={"tx_hash": TX_HASH},
            ) as mock_build_setLicensingConfig_transaction:
                result = license.set_licensing_config(
                    ip_id=ZERO_ADDRESS,
                    license_terms_id=1,
                    licensing_config=default_licensing_config,
                    tx_options=tx_options,
                )

            assert result["success"] is True
            assert result["tx_hash"] == TX_HASH.hex()

            assert mock_build_setLicensingConfig_transaction.call_args[0][4] == {
                "from": "0xF60cBF0Ea1A61567F1dDaf79A6219D20d189155c",
                "gasPrice": 1,  #  mock_web3.to_wei return 1
                "nonce": 3,
            }


class TestGetLicensingConfig:
    """Tests for getLicensingConfig functionality."""

    def test_get_licensing_config_invalid_ip_id_address(self, license: License):
        """Test validation error when IP ID is not a valid address."""
        with pytest.raises(
            ValueError,
            match="Failed to get licensing config: Invalid address: invalid_address.",
        ):
            license.get_licensing_config(
                ip_id="invalid_address",
                license_terms_id=1,
            )

    def test_get_licensing_config_invalid_license_template_address(
        self, license: License
    ):
        """Test validation error when license template is not a valid address."""
        with pytest.raises(
            ValueError,
            match="Failed to get licensing config: Invalid address: invalid_template",
        ):
            license.get_licensing_config(
                ip_id=ZERO_ADDRESS,
                license_terms_id=1,
                license_template="invalid_template",
            )

    def test_get_licensing_config_success_with_default_template(self, license: License):
        """Test successful licensing config retrieval with default license template."""
        mock_tuple_data = (
            True,  # is_set
            100,  # minting_fee
            ZERO_ADDRESS,  # licensing_hook
            ZERO_HASH,  # hook_data
            10 * 10**6,  # commercial_rev_share (converted to raw value)
            False,  # disabled
            50 * 10**6,  # expect_minimum_group_reward_share (converted to raw value)
            ZERO_ADDRESS,  # expect_group_reward_pool
        )

        with patch.object(
            license.license_registry_client,
            "getLicensingConfig",
            return_value=mock_tuple_data,
        ) as mock_get_licensing_config:
            result = license.get_licensing_config(
                ip_id=ZERO_ADDRESS,
                license_terms_id=1,
            )

            # Verify the correct parameters were passed to the contract call
            mock_get_licensing_config.assert_called_once_with(
                ZERO_ADDRESS, license.license_template_client.contract.address, 1
            )

            # Verify the returned LicensingConfig structure
            expected_config = {
                "is_set": True,
                "minting_fee": 100,
                "licensing_hook": ZERO_ADDRESS,
                "hook_data": ZERO_HASH,
                "commercial_rev_share": 10 * 10**6,
                "disabled": False,
                "expect_minimum_group_reward_share": 50 * 10**6,
                "expect_group_reward_pool": ZERO_ADDRESS,
            }

            assert result == expected_config
            assert isinstance(result, dict)
            assert len(result) == 8

    def test_get_licensing_config_success_with_custom_template(self, license: License):
        """Test successful licensing config retrieval with custom license template."""
        custom_template = "0x1234567890123456789012345678901234567890"
        mock_tuple_data = (
            False,  # is_set
            0,  # minting_fee
            ZERO_ADDRESS,  # licensing_hook
            "0x",  # hook_data
            0,  # commercial_rev_share
            True,  # disabled
            0,  # expect_minimum_group_reward_share
            ZERO_ADDRESS,  # expect_group_reward_pool
        )

        with patch.object(
            license.license_registry_client,
            "getLicensingConfig",
            return_value=mock_tuple_data,
        ) as mock_get_licensing_config:
            result = license.get_licensing_config(
                ip_id=ZERO_ADDRESS,
                license_terms_id=1,
                license_template=custom_template,
            )

            # Verify the correct template was passed to the contract call
            mock_get_licensing_config.assert_called_once_with(
                ZERO_ADDRESS, custom_template, 1
            )

            # Verify the returned LicensingConfig structure
            expected_config = {
                "is_set": False,
                "minting_fee": 0,
                "licensing_hook": ZERO_ADDRESS,
                "hook_data": "0x",
                "commercial_rev_share": 0,
                "disabled": True,
                "expect_minimum_group_reward_share": 0,
                "expect_group_reward_pool": ZERO_ADDRESS,
            }

            assert result == expected_config
            assert isinstance(result, dict)
            assert result["disabled"] is True
            assert result["is_set"] is False

    def test_get_licensing_config_contract_call_failure(self, license: License):
        """Test error handling when contract call fails."""
        with patch.object(
            license.license_registry_client,
            "getLicensingConfig",
            side_effect=Exception("Contract call failed"),
        ):
            with pytest.raises(
                ValueError,
                match="Failed to get licensing config: Contract call failed",
            ):
                license.get_licensing_config(
                    ip_id=ZERO_ADDRESS,
                    license_terms_id=1,
                )
