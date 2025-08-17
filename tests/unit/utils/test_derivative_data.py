from unittest.mock import MagicMock, patch

import pytest
from pytest import raises

from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import (
    IPAssetRegistryClient,
)
from story_protocol_python_sdk.abi.LicenseRegistry.LicenseRegistry_client import (
    LicenseRegistryClient,
)
from story_protocol_python_sdk.abi.PILicenseTemplate.PILicenseTemplate_client import (
    PILicenseTemplateClient,
)
from story_protocol_python_sdk.utils.constants import MAX_ROYALTY_TOKEN
from story_protocol_python_sdk.utils.derivative_data import (
    DerivativeData,
    DerivativeDataInput,
)
from tests.unit.fixtures.data import ADDRESS, IP_ID


@pytest.fixture(scope="module")
def mock_ip_asset_registry_client():
    """Fixture to mock IPAssetRegistryClient"""

    def _mock_ip_registered(is_registered=True):
        return patch.object(
            IPAssetRegistryClient,
            "__new__",
            return_value=MagicMock(isRegistered=MagicMock(return_value=is_registered)),
        )

    return _mock_ip_registered


@pytest.fixture(scope="module")
def mock_license_registry_client():
    """Fixture to mock LicenseRegistryClient"""

    def _mock_license_registry_client(
        has_ip_attached_license_terms=True, get_royalty_percent=10
    ):
        return patch.object(
            LicenseRegistryClient,
            "__new__",
            return_value=MagicMock(
                hasIpAttachedLicenseTerms=MagicMock(
                    return_value=has_ip_attached_license_terms
                ),
                getRoyaltyPercent=MagicMock(return_value=get_royalty_percent),
            ),
        )

    return _mock_license_registry_client


@pytest.fixture(scope="module")
def mock_pi_license_template_client():
    """Fixture to mock PILicenseTemplateClient"""

    def _mock_pi_license_template_client():
        mock_instance = MagicMock()
        mock_instance.contract = MagicMock()
        mock_instance.contract.address = ADDRESS
        return patch.object(
            PILicenseTemplateClient,
            "__new__",
            return_value=mock_instance,
        )

    return _mock_pi_license_template_client


class TestValidateParentIpIdsAndLicenseTermsIds:
    def test_validate_parent_ip_ids_is_empty(self, mock_web3):
        with raises(ValueError, match="The parent IP IDs must be provided."):
            DerivativeData(
                web3=mock_web3,
                parent_ip_ids=[],
                license_terms_ids=[2],
                max_minting_fee=10,
                max_rts=10,
                max_revenue_share=100,
                license_template="0x1234567890123456789012345678901234567890",
            )

    def test_validate_license_terms_ids_is_empty(self, mock_web3):
        with raises(ValueError, match="The license terms IDs must be provided."):
            DerivativeData(
                web3=mock_web3,
                parent_ip_ids=[ADDRESS],
                license_terms_ids=[],
                max_minting_fee=10,
                max_rts=10,
                max_revenue_share=100,
                license_template="0x1234567890123456789012345678901234567890",
            )

    def test_validate_parent_ip_ids_and_license_terms_ids_are_not_equal(
        self, mock_web3
    ):
        with raises(
            ValueError,
            match="The number of parent IP IDs must match the number of license terms IDs.",
        ):
            DerivativeData(
                web3=mock_web3,
                parent_ip_ids=[ADDRESS],
                license_terms_ids=[2, 3],
                max_minting_fee=10,
                max_rts=10,
                max_revenue_share=100,
                license_template="0x1234567890123456789012345678901234567890",
            )

    def test_validate_parent_ip_ids_is_not_valid_address(
        self, mock_web3, mock_is_checksum_address
    ):
        with mock_is_checksum_address(is_checksum_address=False):
            with raises(ValueError, match="The parent IP ID must be a valid address."):
                DerivativeData(
                    web3=mock_web3,
                    parent_ip_ids=["0x1234567890123456789012345678901234567890"],
                    license_terms_ids=[2],
                    max_minting_fee=10,
                    max_rts=10,
                    max_revenue_share=100,
                    license_template="0x1234567890123456789012345678901234567890",
                )

    def test_validate_parent_ip_ids_is_not_registered(
        self,
        mock_web3,
        mock_is_checksum_address,
        mock_ip_asset_registry_client,
    ):
        with mock_is_checksum_address(), mock_ip_asset_registry_client(
            is_registered=False
        ):
            with raises(
                ValueError,
                match=f"The parent IP ID {IP_ID} must be registered.",
            ):
                DerivativeData(
                    web3=mock_web3,
                    parent_ip_ids=[IP_ID],
                    license_terms_ids=[2],
                    max_minting_fee=10,
                    max_rts=10,
                    max_revenue_share=100,
                    license_template="0x1234567890123456789012345678901234567890",
                )

    def test_validate_license_terms_not_attached(
        self,
        mock_web3,
        mock_is_checksum_address,
        mock_ip_asset_registry_client,
        mock_license_registry_client,
    ):
        with mock_is_checksum_address(), mock_ip_asset_registry_client(
            is_registered=True
        ), mock_license_registry_client(has_ip_attached_license_terms=False):
            with raises(
                ValueError,
                match=f"License terms id 2 must be attached to the parent ipId {IP_ID} before registering derivative.",
            ):
                DerivativeData(
                    web3=mock_web3,
                    parent_ip_ids=[IP_ID],
                    license_terms_ids=[2],
                    max_minting_fee=10,
                    max_rts=10,
                    max_revenue_share=100,
                    license_template="0x1234567890123456789012345678901234567890",
                )

    def test_validate_royalty_percent_exceeds_max_revenue_share(
        self,
        mock_web3,
        mock_is_checksum_address,
        mock_ip_asset_registry_client,
        mock_license_registry_client,
    ):
        with mock_is_checksum_address(), mock_ip_asset_registry_client(
            is_registered=True
        ), mock_license_registry_client(
            has_ip_attached_license_terms=True, get_royalty_percent=1500000000000
        ):
            with raises(
                ValueError,
                match=f"The total royalty percent for the parent IP {IP_ID} is greater than the maximum revenue share 1000000",
            ):
                DerivativeData(
                    web3=mock_web3,
                    parent_ip_ids=[IP_ID],
                    license_terms_ids=[2],
                    max_minting_fee=10,
                    max_rts=10,
                    max_revenue_share=1,
                    license_template="0x1234567890123456789012345678901234567890",
                )

    def test_validate_royalty_percent_is_less_than_max_revenue_share(
        self,
        mock_web3,
        mock_is_checksum_address,
        mock_ip_asset_registry_client,
        mock_license_registry_client,
    ):
        with mock_is_checksum_address(), mock_ip_asset_registry_client(), mock_license_registry_client():
            derivative_data = DerivativeData.from_input(
                web3=mock_web3,
                input_data=DerivativeDataInput(
                    parent_ip_ids=[IP_ID],
                    license_terms_ids=[2],
                    max_minting_fee=10,
                    max_rts=10,
                    license_template="0x1234567890123456789012345678901234567890",
                ),
            )
            assert derivative_data.max_revenue_share == MAX_ROYALTY_TOKEN


class TestValidateMaxMintingFee:
    def test_validate_max_minting_fee_is_less_than_0(
        self,
        mock_web3,
        mock_is_checksum_address,
        mock_ip_asset_registry_client,
        mock_license_registry_client,
    ):
        with mock_is_checksum_address(), mock_ip_asset_registry_client(), mock_license_registry_client():
            with raises(
                ValueError, match="The max minting fee must be greater than 0."
            ):
                DerivativeData(
                    web3=mock_web3,
                    parent_ip_ids=[IP_ID],
                    license_terms_ids=[2],
                    max_minting_fee=-1,
                    max_rts=10,
                    max_revenue_share=100,
                    license_template="0x1234567890123456789012345678901234567890",
                )


class TestValidateMaxRts:
    def test_validate_max_rts_is_less_than_0(
        self,
        mock_web3,
        mock_is_checksum_address,
        mock_ip_asset_registry_client,
        mock_license_registry_client,
    ):
        with mock_is_checksum_address(), mock_ip_asset_registry_client(), mock_license_registry_client():
            with raises(
                ValueError,
                match="The maxRts must be greater than 0 and less than 100000000.",
            ):
                DerivativeData.from_input(
                    web3=mock_web3,
                    input_data=DerivativeDataInput(
                        parent_ip_ids=[IP_ID],
                        license_terms_ids=[2],
                        max_rts=-1,
                    ),
                )

    def test_validate_max_rts_is_greater_than_100_000_000(
        self, mock_web3, mock_ip_asset_registry_client, mock_license_registry_client
    ):
        with mock_ip_asset_registry_client(), mock_license_registry_client():
            with raises(
                ValueError,
                match="The maxRts must be greater than 0 and less than 100000000.",
            ):
                DerivativeData.from_input(
                    web3=mock_web3,
                    input_data=DerivativeDataInput(
                        parent_ip_ids=[IP_ID],
                        license_terms_ids=[2],
                        max_rts=1000000000001,
                    ),
                )

    def test_validate_max_rts_default_value_is_max_rts(
        self,
        mock_web3,
        mock_is_checksum_address,
        mock_ip_asset_registry_client,
        mock_license_registry_client,
    ):
        with mock_is_checksum_address(), mock_ip_asset_registry_client(), mock_license_registry_client():
            derivative_data = DerivativeData.from_input(
                web3=mock_web3,
                input_data=DerivativeDataInput(
                    parent_ip_ids=[IP_ID],
                    license_terms_ids=[2],
                ),
            )
            assert derivative_data.max_rts == MAX_ROYALTY_TOKEN


class TestValidateMaxRevenueShare:
    def test_validate_max_revenue_share_is_less_than_0(
        self, mock_web3, mock_ip_asset_registry_client, mock_license_registry_client
    ):
        with mock_ip_asset_registry_client(), mock_license_registry_client():
            with raises(
                ValueError, match="max_revenue_share must be between 0 and 100."
            ):
                DerivativeData.from_input(
                    web3=mock_web3,
                    input_data=DerivativeDataInput(
                        parent_ip_ids=[IP_ID],
                        license_terms_ids=[2],
                        max_minting_fee=10,
                        max_rts=10,
                        max_revenue_share=-1,
                    ),
                )

    def test_validate_max_revenue_share_is_greater_than_100(
        self,
        mock_web3,
        mock_is_checksum_address,
        mock_ip_asset_registry_client,
        mock_license_registry_client,
    ):
        with mock_is_checksum_address(), mock_ip_asset_registry_client(), mock_license_registry_client():
            with raises(
                ValueError, match="max_revenue_share must be between 0 and 100."
            ):
                DerivativeData.from_input(
                    web3=mock_web3,
                    input_data=DerivativeDataInput(
                        parent_ip_ids=[IP_ID],
                        license_terms_ids=[2],
                        max_minting_fee=10,
                        max_rts=10,
                        max_revenue_share=101,
                    ),
                )

    def test_validate_max_revenue_share_default_value_is_100(
        self,
        mock_web3,
        mock_is_checksum_address,
        mock_ip_asset_registry_client,
        mock_license_registry_client,
    ):
        with mock_is_checksum_address(), mock_ip_asset_registry_client(), mock_license_registry_client():
            derivative_data = DerivativeData.from_input(
                web3=mock_web3,
                input_data=DerivativeDataInput(
                    parent_ip_ids=[IP_ID],
                    license_terms_ids=[2],
                ),
            )
            assert derivative_data.max_revenue_share == MAX_ROYALTY_TOKEN


class TestValidateLicenseTemplate:
    def test_validate_license_template_default_value_is_pi_license_template(
        self,
        mock_web3,
        mock_is_checksum_address,
        mock_pi_license_template_client,
        mock_ip_asset_registry_client,
        mock_license_registry_client,
    ):
        with mock_is_checksum_address(), mock_pi_license_template_client(), mock_ip_asset_registry_client(), mock_license_registry_client():
            derivative_data = DerivativeData.from_input(
                web3=mock_web3,
                input_data=DerivativeDataInput(
                    parent_ip_ids=[IP_ID],
                    license_terms_ids=[2],
                ),
            )
            assert derivative_data.license_template == ADDRESS


class TestGetValidatedData:
    def test_get_validated_data_with_default_values(
        self,
        mock_web3,
        mock_is_checksum_address,
        mock_pi_license_template_client,
        mock_ip_asset_registry_client,
        mock_license_registry_client,
    ):
        with mock_is_checksum_address(), mock_pi_license_template_client(), mock_ip_asset_registry_client(), mock_license_registry_client():
            derivative_data = DerivativeData.from_input(
                web3=mock_web3,
                input_data=DerivativeDataInput(
                    parent_ip_ids=[IP_ID],
                    license_terms_ids=[2],
                ),
            )
            assert derivative_data.get_validated_data() == {
                "parentIpIds": [IP_ID],
                "licenseTermsIds": [2],
                "maxMintingFee": 0,
                "maxRts": MAX_ROYALTY_TOKEN,
                "maxRevenueShare": MAX_ROYALTY_TOKEN,
                "licenseTemplate": ADDRESS,
                "royaltyContext": "0x0000000000000000000000000000000000000000",
            }

    def test_get_validated_data_with_custom_values(
        self,
        mock_web3,
        mock_ip_asset_registry_client,
        mock_license_registry_client,
        mock_pi_license_template_client,
        mock_is_checksum_address,
    ):
        with mock_is_checksum_address(), mock_pi_license_template_client(), mock_ip_asset_registry_client(), mock_license_registry_client():
            derivative_data = DerivativeData(
                web3=mock_web3,
                parent_ip_ids=[IP_ID],
                license_terms_ids=[2],
                max_minting_fee=10,
                max_rts=10,
                max_revenue_share=10,
                license_template="0x1234567890123456789012345678901234567890",
            )
            assert derivative_data.get_validated_data() == {
                "parentIpIds": [IP_ID],
                "licenseTermsIds": [2],
                "maxMintingFee": 10,
                "maxRts": 10,
                "maxRevenueShare": 10000000.0,
                "licenseTemplate": "0x1234567890123456789012345678901234567890",
                "royaltyContext": "0x0000000000000000000000000000000000000000",
            }
