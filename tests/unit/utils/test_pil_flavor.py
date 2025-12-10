import pytest

from story_protocol_python_sdk import (
    ROYALTY_POLICY_LAP_ADDRESS,
    ROYALTY_POLICY_LRP_ADDRESS,
    WIP_TOKEN_ADDRESS,
    ZERO_ADDRESS,
    LicenseTermsInput,
    LicenseTermsOverride,
    NativeRoyaltyPolicy,
    PILFlavor,
)
from story_protocol_python_sdk.utils.pil_flavor import PILFlavorError
from tests.unit.fixtures.data import ADDRESS


class TestPILFlavor:
    """Test PILFlavor class."""

    class TestNonCommercialSocialRemixing:
        """Test non commercial social remixing PIL flavor."""

        def test_default_values(self):
            """Test default values."""
            pil_flavor = PILFlavor.non_commercial_social_remixing()
            assert pil_flavor == LicenseTermsInput(
                transferable=True,
                commercial_attribution=False,
                commercial_rev_ceiling=0,
                commercial_rev_share=0,
                commercial_use=False,
                commercializer_checker=ZERO_ADDRESS,
                commercializer_checker_data=ZERO_ADDRESS,
                currency=ZERO_ADDRESS,
                derivative_rev_ceiling=0,
                derivatives_allowed=True,
                derivatives_approval=False,
                derivatives_attribution=True,
                derivatives_reciprocal=True,
                expiration=0,
                default_minting_fee=0,
                royalty_policy=ZERO_ADDRESS,
                uri="https://github.com/piplabs/pil-document/blob/998c13e6ee1d04eb817aefd1fe16dfe8be3cd7a2/off-chain-terms/NCSR.json",
            )

        def test_override_values(self):
            """Test override values."""
            pil_flavor = PILFlavor.non_commercial_social_remixing(
                override=LicenseTermsOverride(
                    commercial_use=True,
                    commercial_attribution=True,
                    royalty_policy=NativeRoyaltyPolicy.LAP,
                    currency=WIP_TOKEN_ADDRESS,
                ),
            )
            assert pil_flavor == LicenseTermsInput(
                transferable=True,
                commercial_attribution=True,
                commercial_rev_ceiling=0,
                commercial_rev_share=0,
                commercial_use=True,
                commercializer_checker=ZERO_ADDRESS,
                commercializer_checker_data=ZERO_ADDRESS,
                currency=WIP_TOKEN_ADDRESS,
                derivative_rev_ceiling=0,
                derivatives_allowed=True,
                derivatives_approval=False,
                derivatives_attribution=True,
                derivatives_reciprocal=True,
                expiration=0,
                default_minting_fee=0,
                royalty_policy=ROYALTY_POLICY_LAP_ADDRESS,
                uri="https://github.com/piplabs/pil-document/blob/998c13e6ee1d04eb817aefd1fe16dfe8be3cd7a2/off-chain-terms/NCSR.json",
            )

        def test_throw_commercial_attribution_error_when_commercial_use_is_false(self):
            """Test throw commercial attribution error when commercial use is false."""
            with pytest.raises(
                PILFlavorError,
                match="cannot add commercial_attribution when commercial_use is False.",
            ):
                PILFlavor.non_commercial_social_remixing(
                    override=LicenseTermsOverride(commercial_attribution=True),
                )

        def test_throw_commercializer_checker_error_when_commercial_use_is_false(self):
            """Test throw commercializer checker error when commercial use is false."""
            with pytest.raises(
                PILFlavorError,
                match="cannot add commercializer_checker when commercial_use is False.",
            ):
                PILFlavor.non_commercial_social_remixing(
                    override=LicenseTermsOverride(commercializer_checker=ADDRESS),
                )

        def test_throw_commercial_rev_share_error_when_commercial_use_is_false(self):
            """Test throw commercial rev share error when commercial use is false."""
            with pytest.raises(
                PILFlavorError,
                match="cannot add commercial_rev_share when commercial_use is False.",
            ):
                PILFlavor.non_commercial_social_remixing(
                    override=LicenseTermsOverride(commercial_rev_share=10),
                )

        def test_throw_commercial_rev_ceiling_error_when_commercial_use_is_false(self):
            """Test throw commercial rev ceiling error when commercial use is false."""
            with pytest.raises(
                PILFlavorError,
                match="cannot add commercial_rev_ceiling when commercial_use is False.",
            ):
                PILFlavor.non_commercial_social_remixing(
                    override=LicenseTermsOverride(commercial_rev_ceiling=10000),
                )

        def test_throw_derivative_rev_ceiling_error_when_commercial_use_is_false(self):
            """Test throw derivative rev ceiling error when commercial use is false."""
            with pytest.raises(
                PILFlavorError,
                match="cannot add derivative_rev_ceiling when commercial_use is False.",
            ):
                PILFlavor.non_commercial_social_remixing(
                    override=LicenseTermsOverride(derivative_rev_ceiling=10000),
                )

        def test_throw_royalty_policy_error_when_commercial_use_is_false(self):
            """Test throw royalty policy error when commercial use is false."""
            with pytest.raises(
                PILFlavorError,
                match="cannot add royalty_policy when commercial_use is False.",
            ):
                PILFlavor.non_commercial_social_remixing(
                    override=LicenseTermsOverride(
                        royalty_policy=ADDRESS, currency=WIP_TOKEN_ADDRESS
                    ),
                )

    class TestCommercialUse:
        """Test commercial use PIL flavor."""

        def test_default_values(self):
            """Test default values."""
            pil_flavor = PILFlavor.commercial_use(
                default_minting_fee=10000,
                currency=WIP_TOKEN_ADDRESS,
                royalty_policy=ADDRESS,
            )
            assert pil_flavor == LicenseTermsInput(
                transferable=True,
                commercial_attribution=True,
                commercial_rev_ceiling=0,
                commercial_rev_share=0,
                commercial_use=True,
                commercializer_checker=ZERO_ADDRESS,
                commercializer_checker_data=ZERO_ADDRESS,
                currency=WIP_TOKEN_ADDRESS,
                derivative_rev_ceiling=0,
                derivatives_allowed=False,
                derivatives_approval=False,
                derivatives_attribution=False,
                derivatives_reciprocal=False,
                expiration=0,
                default_minting_fee=10000,
                royalty_policy=ADDRESS,
                uri="https://github.com/piplabs/pil-document/blob/9a1f803fcf8101a8a78f1dcc929e6014e144ab56/off-chain-terms/CommercialUse.json",
            )

        def test_without_royalty_policy(self):
            """Test without royalty policy."""
            pil_flavor = PILFlavor.commercial_use(
                default_minting_fee=10000,
                currency=WIP_TOKEN_ADDRESS,
            )
            assert pil_flavor == LicenseTermsInput(
                transferable=True,
                commercial_attribution=True,
                commercial_rev_ceiling=0,
                commercial_rev_share=0,
                commercial_use=True,
                commercializer_checker=ZERO_ADDRESS,
                commercializer_checker_data=ZERO_ADDRESS,
                currency=WIP_TOKEN_ADDRESS,
                derivative_rev_ceiling=0,
                derivatives_allowed=False,
                derivatives_approval=False,
                derivatives_attribution=False,
                derivatives_reciprocal=False,
                expiration=0,
                default_minting_fee=10000,
                royalty_policy=ROYALTY_POLICY_LAP_ADDRESS,
                uri="https://github.com/piplabs/pil-document/blob/9a1f803fcf8101a8a78f1dcc929e6014e144ab56/off-chain-terms/CommercialUse.json",
            )

        def test_with_custom_values(self):
            """Test with custom values."""
            pil_flavor = PILFlavor.commercial_use(
                default_minting_fee=10000,
                currency=WIP_TOKEN_ADDRESS,
                royalty_policy=ADDRESS,
                override=LicenseTermsOverride(
                    commercial_attribution=False,
                    derivatives_allowed=True,
                    derivatives_attribution=True,
                    derivatives_approval=False,
                    derivatives_reciprocal=True,
                    uri="https://example.com",
                    royalty_policy=NativeRoyaltyPolicy.LRP,
                    default_minting_fee=10,
                    commercial_rev_share=10,
                ),
            )
            assert pil_flavor == LicenseTermsInput(
                transferable=True,
                commercial_attribution=False,
                commercial_rev_ceiling=0,
                commercial_rev_share=10,
                commercial_use=True,
                commercializer_checker=ZERO_ADDRESS,
                commercializer_checker_data=ZERO_ADDRESS,
                currency=WIP_TOKEN_ADDRESS,
                derivative_rev_ceiling=0,
                derivatives_allowed=True,
                derivatives_approval=False,
                derivatives_attribution=True,
                derivatives_reciprocal=True,
                expiration=0,
                default_minting_fee=10,
                royalty_policy=ROYALTY_POLICY_LRP_ADDRESS,
                uri="https://example.com",
            )

        def test_throw_error_when_royalty_policy_is_not_zero_address_and_currency_is_zero_address(
            self,
        ):
            """Test throw error when royalty policy is not zero address and currency is zero address."""
            with pytest.raises(
                PILFlavorError,
                match="royalty_policy is not zero address and currency cannot be zero address.",
            ):
                PILFlavor.commercial_use(
                    default_minting_fee=10000,
                    currency=ZERO_ADDRESS,
                    royalty_policy=ADDRESS,
                )

        def test_throw_error_when_default_minting_fee_is_less_than_zero(self):
            """Test throw error when default minting fee is less than zero."""
            with pytest.raises(
                PILFlavorError,
                match="default_minting_fee should be greater than or equal to 0.",
            ):
                PILFlavor.commercial_use(
                    default_minting_fee=-1,
                    currency=WIP_TOKEN_ADDRESS,
                    royalty_policy=ADDRESS,
                )

        def test_not_throw_error_when_default_minting_fee_is_zero_and_royalty_policy_is_not_zero_address(
            self,
        ):
            """Test not throw error when default minting fee is zero and royalty policy is not zero address."""
            pil_flavor = PILFlavor.commercial_use(
                default_minting_fee=0,
                currency=WIP_TOKEN_ADDRESS,
                royalty_policy=ADDRESS,
            )
            assert pil_flavor.default_minting_fee == 0

        def test_not_throw_error_when_default_minting_fee_is_100_(self):
            """Test not throw error when default minting fee is 100"""
            pil_flavor = PILFlavor.commercial_use(
                default_minting_fee=100,
                currency=WIP_TOKEN_ADDRESS,
                royalty_policy=ADDRESS,
            )
            assert pil_flavor.default_minting_fee == 100

        def test_throw_error_when_default_minting_fee_is_greater_than_zero_and_royalty_policy_is_zero_address(
            self,
        ):
            """Test throw error when default minting fee is greater than zero and royalty policy is zero address."""
            with pytest.raises(
                PILFlavorError,
                match="royalty_policy is required when default_minting_fee is greater than 0.",
            ):
                PILFlavor.commercial_use(
                    default_minting_fee=10000,
                    currency=WIP_TOKEN_ADDRESS,
                    royalty_policy=ZERO_ADDRESS,
                )

        def test_throw_error_when_commercial_rev_share_is_less_than_zero(self):
            """Test throw error when commercial rev share is less than zero."""
            with pytest.raises(
                PILFlavorError, match="commercial_rev_share must be between 0 and 100."
            ):
                PILFlavor.commercial_use(
                    default_minting_fee=10000,
                    currency=WIP_TOKEN_ADDRESS,
                    royalty_policy=ADDRESS,
                    override=LicenseTermsOverride(commercial_rev_share=-1),
                )

        def test_throw_error_when_commercial_rev_share_is_greater_than_100(self):
            """Test throw error when commercial rev share is greater than 100."""
            with pytest.raises(
                PILFlavorError, match="commercial_rev_share must be between 0 and 100."
            ):
                PILFlavor.commercial_use(
                    default_minting_fee=10000,
                    currency=WIP_TOKEN_ADDRESS,
                    royalty_policy=ADDRESS,
                    override=LicenseTermsOverride(commercial_rev_share=101),
                )

        def test_throw_error_when_commercial_is_true_and_royalty_policy_is_zero_address(
            self,
        ):
            """Test throw error when commercial is true and royalty policy is zero address."""
            with pytest.raises(
                PILFlavorError,
                match="royalty_policy is required when commercial_use is True.",
            ):
                PILFlavor.commercial_use(
                    default_minting_fee=0,
                    currency=WIP_TOKEN_ADDRESS,
                    royalty_policy=ZERO_ADDRESS,
                )

    class TestCommercialRemix:
        """Test commercial remix PIL flavor."""

        def test_default_values(self):
            """Test default values."""
            pil_flavor = PILFlavor.commercial_remix(
                default_minting_fee=10000,
                currency=WIP_TOKEN_ADDRESS,
                commercial_rev_share=10,
            )
            assert pil_flavor == LicenseTermsInput(
                transferable=True,
                commercial_attribution=True,
                commercial_rev_ceiling=0,
                commercial_rev_share=10,
                commercial_use=True,
                commercializer_checker=ZERO_ADDRESS,
                commercializer_checker_data=ZERO_ADDRESS,
                currency=WIP_TOKEN_ADDRESS,
                derivative_rev_ceiling=0,
                derivatives_allowed=True,
                derivatives_approval=False,
                derivatives_attribution=True,
                derivatives_reciprocal=True,
                expiration=0,
                default_minting_fee=10000,
                royalty_policy=ROYALTY_POLICY_LAP_ADDRESS,
                uri="https://github.com/piplabs/pil-document/blob/ad67bb632a310d2557f8abcccd428e4c9c798db1/off-chain-terms/CommercialRemix.json",
            )

        def test_with_custom_values(self):
            """Test with custom values."""
            pil_flavor = PILFlavor.commercial_remix(
                default_minting_fee=10000,
                currency=WIP_TOKEN_ADDRESS,
                commercial_rev_share=100,
                override=LicenseTermsOverride(
                    commercial_attribution=False,
                    derivatives_allowed=True,
                    derivatives_attribution=True,
                    derivatives_approval=False,
                    derivatives_reciprocal=True,
                    uri="https://example.com",
                    royalty_policy=NativeRoyaltyPolicy.LRP,
                    default_minting_fee=10,
                    commercial_rev_share=10,
                ),
            )
            assert pil_flavor == LicenseTermsInput(
                transferable=True,
                commercial_attribution=False,
                commercial_rev_ceiling=0,
                derivative_rev_ceiling=0,
                derivatives_allowed=True,
                derivatives_approval=False,
                derivatives_attribution=True,
                derivatives_reciprocal=True,
                currency=WIP_TOKEN_ADDRESS,
                commercial_rev_share=10,
                commercial_use=True,
                commercializer_checker=ZERO_ADDRESS,
                commercializer_checker_data=ZERO_ADDRESS,
                expiration=0,
                default_minting_fee=10,
                royalty_policy=ROYALTY_POLICY_LRP_ADDRESS,
                uri="https://example.com",
            )

    class TestCreativeCommonsAttribution:
        """Test creative commons attribution PIL flavor."""

        def test_default_values(self):
            """Test default values."""
            pil_flavor = PILFlavor.creative_commons_attribution(
                currency=WIP_TOKEN_ADDRESS,
            )
            assert pil_flavor == LicenseTermsInput(
                transferable=True,
                commercial_attribution=True,
                commercial_rev_ceiling=0,
                commercial_rev_share=0,
                commercial_use=True,
                commercializer_checker=ZERO_ADDRESS,
                commercializer_checker_data=ZERO_ADDRESS,
                currency=WIP_TOKEN_ADDRESS,
                derivative_rev_ceiling=0,
                derivatives_allowed=True,
                derivatives_approval=False,
                derivatives_attribution=True,
                derivatives_reciprocal=True,
                expiration=0,
                default_minting_fee=0,
                royalty_policy=ROYALTY_POLICY_LAP_ADDRESS,
                uri="https://github.com/piplabs/pil-document/blob/998c13e6ee1d04eb817aefd1fe16dfe8be3cd7a2/off-chain-terms/CC-BY.json",
            )

        def test_with_custom_values(self):
            """Test with custom values."""
            pil_flavor = PILFlavor.creative_commons_attribution(
                currency=WIP_TOKEN_ADDRESS,
                override=LicenseTermsOverride(
                    commercial_attribution=False,
                    derivatives_allowed=True,
                    derivatives_attribution=True,
                    derivatives_approval=False,
                    derivatives_reciprocal=True,
                    uri="https://example.com",
                    royalty_policy=ADDRESS,
                ),
            )
            assert pil_flavor == LicenseTermsInput(
                transferable=True,
                commercial_attribution=False,
                commercial_rev_ceiling=0,
                commercial_rev_share=0,
                commercial_use=True,
                commercializer_checker=ZERO_ADDRESS,
                commercializer_checker_data=ZERO_ADDRESS,
                currency=WIP_TOKEN_ADDRESS,
                derivative_rev_ceiling=0,
                derivatives_allowed=True,
                derivatives_approval=False,
                derivatives_attribution=True,
                derivatives_reciprocal=True,
                expiration=0,
                default_minting_fee=0,
                royalty_policy=ADDRESS,
                uri="https://example.com",
            )

        def test_throw_derivatives_attribution_error_when_derivatives_allowed_is_false(
            self,
        ):
            """Test throw derivatives attribution error when derivatives allowed is false."""
            with pytest.raises(
                PILFlavorError,
                match="cannot add derivatives_attribution when derivatives_allowed is False.",
            ):
                PILFlavor.creative_commons_attribution(
                    currency=WIP_TOKEN_ADDRESS,
                    override=LicenseTermsOverride(
                        derivatives_allowed=False,
                    ),
                )

        def test_throw_derivatives_approval_error_when_derivatives_allowed_is_false(
            self,
        ):
            """Test throw derivatives approval error when derivatives allowed is false."""
            with pytest.raises(
                PILFlavorError,
                match="cannot add derivatives_approval when derivatives_allowed is False.",
            ):
                PILFlavor.creative_commons_attribution(
                    currency=WIP_TOKEN_ADDRESS,
                    override=LicenseTermsOverride(
                        derivatives_allowed=False,
                        derivatives_approval=True,
                        derivatives_attribution=False,
                    ),
                )

        def test_throw_derivatives_reciprocal_error_when_derivatives_allowed_is_false(
            self,
        ):
            """Test throw derivatives reciprocal error when derivatives allowed is false."""
            with pytest.raises(
                PILFlavorError,
                match="cannot add derivatives_reciprocal when derivatives_allowed is False.",
            ):
                PILFlavor.creative_commons_attribution(
                    currency=WIP_TOKEN_ADDRESS,
                    override=LicenseTermsOverride(
                        derivatives_allowed=False,
                        derivatives_reciprocal=True,
                        derivatives_attribution=False,
                        derivatives_approval=False,
                    ),
                )

        def test_throw_derivative_rev_ceiling_error_when_derivatives_allowed_is_false(
            self,
        ):
            """Test throw derivative rev ceiling error when derivatives allowed is false."""
            with pytest.raises(
                PILFlavorError,
                match="cannot add derivative_rev_ceiling when derivatives_allowed is False.",
            ):
                PILFlavor.creative_commons_attribution(
                    currency=WIP_TOKEN_ADDRESS,
                    override=LicenseTermsOverride(
                        derivatives_allowed=False,
                        derivative_rev_ceiling=10000,
                        derivatives_attribution=False,
                        derivatives_approval=False,
                        derivatives_reciprocal=False,
                    ),
                )
