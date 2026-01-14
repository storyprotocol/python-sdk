from dataclasses import asdict, replace
from unittest.mock import MagicMock, patch

import pytest

from story_protocol_python_sdk.utils.registration.registration_utils import (
    get_public_minting,
    validate_license_terms_data,
)
from tests.unit.fixtures.data import (
    ADDRESS,
    LICENSE_TERMS_DATA,
    LICENSE_TERMS_DATA_CAMEL_CASE,
)


@pytest.fixture
def mock_spg_nft_client():
    """Mock SPGNFTImplClient."""

    def _mock(public_minting: bool = True):
        return patch(
            "story_protocol_python_sdk.utils.registration.registration_utils.SPGNFTImplClient",
            return_value=MagicMock(
                publicMinting=MagicMock(return_value=public_minting)
            ),
        )

    return _mock


@pytest.fixture
def mock_royalty_module_client():
    """Mock RoyaltyModuleClient."""

    def _mock(is_whitelisted_policy: bool = True, is_whitelisted_token: bool = True):
        return patch(
            "story_protocol_python_sdk.utils.registration.registration_utils.RoyaltyModuleClient",
            return_value=MagicMock(
                isWhitelistedRoyaltyPolicy=MagicMock(
                    return_value=is_whitelisted_policy
                ),
                isWhitelistedRoyaltyToken=MagicMock(return_value=is_whitelisted_token),
            ),
        )

    return _mock


@pytest.fixture
def mock_module_registry_client():
    """Mock ModuleRegistryClient."""
    return patch(
        "story_protocol_python_sdk.utils.registration.registration_utils.ModuleRegistryClient",
        return_value=MagicMock(),
    )


class TestGetPublicMinting:
    def test_returns_true_when_public_minting_enabled(
        self, mock_web3, mock_spg_nft_client
    ):
        with mock_spg_nft_client(public_minting=True):
            result = get_public_minting(ADDRESS, mock_web3)
            assert result is True

    def test_returns_false_when_public_minting_disabled(
        self, mock_web3, mock_spg_nft_client
    ):
        with mock_spg_nft_client(public_minting=False):
            result = get_public_minting(ADDRESS, mock_web3)
            assert result is False

    def test_throws_error_when_spg_nft_contract_invalid(self, mock_web3):
        with pytest.raises(Exception):
            get_public_minting("invalid_address", mock_web3)


class TestValidateLicenseTermsData:
    def test_validates_license_terms_with_dataclass_input(
        self,
        mock_web3,
        mock_royalty_module_client,
        mock_module_registry_client,
    ):
        with (
            mock_royalty_module_client(),
            mock_module_registry_client,
        ):
            result = validate_license_terms_data(LICENSE_TERMS_DATA, mock_web3)
            assert isinstance(result, list)
            assert len(result) == len(LICENSE_TERMS_DATA)
            assert result[0] == LICENSE_TERMS_DATA_CAMEL_CASE

    def test_validates_license_terms_with_dict_input(
        self,
        mock_web3,
        mock_royalty_module_client,
        mock_module_registry_client,
    ):
        with (
            mock_royalty_module_client(),
            mock_module_registry_client,
        ):
            result = validate_license_terms_data(
                [
                    {
                        "terms": asdict(LICENSE_TERMS_DATA[0].terms),
                        "licensing_config": LICENSE_TERMS_DATA[0].licensing_config,
                    }
                ],
                mock_web3,
            )
            assert result[0] == LICENSE_TERMS_DATA_CAMEL_CASE

    def test_throws_error_when_royalty_policy_not_whitelisted(
        self,
        mock_web3,
        mock_royalty_module_client,
        mock_module_registry_client,
    ):
        with (
            mock_royalty_module_client(is_whitelisted_policy=False),
            mock_module_registry_client,
            pytest.raises(ValueError, match="The royalty_policy is not whitelisted."),
        ):
            validate_license_terms_data(LICENSE_TERMS_DATA, mock_web3)

    def test_throws_error_when_currency_not_whitelisted(
        self,
        mock_web3,
        mock_royalty_module_client,
        mock_module_registry_client,
    ):
        with (
            mock_royalty_module_client(is_whitelisted_token=False),
            mock_module_registry_client,
            pytest.raises(ValueError, match="The currency is not whitelisted."),
        ):
            validate_license_terms_data(LICENSE_TERMS_DATA, mock_web3)

    def test_validates_multiple_license_terms(
        self,
        mock_web3,
        mock_royalty_module_client,
        mock_module_registry_client,
    ):
        # Use LICENSE_TERMS_DATA twice to test multiple terms
        license_terms_data = LICENSE_TERMS_DATA + [
            replace(
                LICENSE_TERMS_DATA[0],
                terms=replace(LICENSE_TERMS_DATA[0].terms, commercial_rev_share=20),
            )
        ]

        with (
            mock_royalty_module_client(),
            mock_module_registry_client,
        ):
            result = validate_license_terms_data(license_terms_data, mock_web3)
            assert result[0] == LICENSE_TERMS_DATA_CAMEL_CASE
            assert result[1] == {
                "terms": {
                    **LICENSE_TERMS_DATA_CAMEL_CASE["terms"],
                    "commercialRevShare": 20 * 10**6,
                },
                "licensingConfig": LICENSE_TERMS_DATA_CAMEL_CASE["licensingConfig"],
            }
