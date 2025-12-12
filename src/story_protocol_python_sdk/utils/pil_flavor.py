from dataclasses import asdict, replace
from typing import Optional

from ens.ens import Address

from story_protocol_python_sdk.types.resource.License import (
    LicenseTermsInput,
    LicenseTermsOverride,
)
from story_protocol_python_sdk.types.resource.Royalty import RoyaltyPolicyInput
from story_protocol_python_sdk.utils.constants import ZERO_ADDRESS
from story_protocol_python_sdk.utils.royalty import royalty_policy_input_to_address
from story_protocol_python_sdk.utils.validation import validate_address


def _apply_override(
    base: LicenseTermsInput, override: Optional[LicenseTermsOverride]
) -> LicenseTermsInput:
    """Apply override values to base license terms, ignoring None values."""
    if not override:
        return base
    # Filter out None values from override
    overrides = {k: v for k, v in asdict(override).items() if v is not None}
    return replace(base, **overrides)


# PIL URIs for off-chain terms
PIL_URIS = {
    "NCSR": "https://github.com/piplabs/pil-document/blob/998c13e6ee1d04eb817aefd1fe16dfe8be3cd7a2/off-chain-terms/NCSR.json",
    "COMMERCIAL_USE": "https://github.com/piplabs/pil-document/blob/9a1f803fcf8101a8a78f1dcc929e6014e144ab56/off-chain-terms/CommercialUse.json",
    "COMMERCIAL_REMIX": "https://github.com/piplabs/pil-document/blob/ad67bb632a310d2557f8abcccd428e4c9c798db1/off-chain-terms/CommercialRemix.json",
    "CC_BY": "https://github.com/piplabs/pil-document/blob/998c13e6ee1d04eb817aefd1fe16dfe8be3cd7a2/off-chain-terms/CC-BY.json",
}

# Common default values for license terms
COMMON_DEFAULTS: LicenseTermsInput = LicenseTermsInput(
    transferable=True,
    royalty_policy=ZERO_ADDRESS,
    default_minting_fee=0,
    expiration=0,
    commercial_use=False,
    commercial_attribution=False,
    commercializer_checker=ZERO_ADDRESS,
    commercializer_checker_data=ZERO_ADDRESS,
    commercial_rev_share=0,
    commercial_rev_ceiling=0,
    derivatives_allowed=False,
    derivatives_attribution=False,
    derivatives_approval=False,
    derivatives_reciprocal=False,
    derivative_rev_ceiling=0,
    currency=ZERO_ADDRESS,
    uri="",
)


class PILFlavorError(Exception):
    """Exception for PIL flavor validation errors."""

    pass


class PILFlavor:
    """
    Pre-configured Programmable IP License (PIL) flavors for ease of use.

    The PIL is highly configurable, but these pre-configured license terms (flavors)
    are the most popular options that cover common use cases.

    See: https://docs.story.foundation/concepts/programmable-ip-license/pil-flavors

    Example:
        # Create a commercial use license
        commercial_license = PILFlavor.commercial_use(
            default_minting_fee=1000000000000000000,  # 1 IP minting fee
            currency="0x1234...",  # currency token
            royalty_policy="LAP"  # royalty policy
        )

        # Create a non-commercial social remixing license
        remix_license = PILFlavor.non_commercial_social_remixing()
    """

    _non_commercial_social_remixing_pil = replace(
        COMMON_DEFAULTS,
        commercial_use=False,
        commercial_attribution=False,
        derivatives_allowed=True,
        derivatives_attribution=True,
        derivatives_approval=False,
        derivatives_reciprocal=True,
        uri=PIL_URIS["NCSR"],
    )

    _commercial_use = replace(
        COMMON_DEFAULTS,
        commercial_use=True,
        commercial_attribution=True,
        derivatives_allowed=False,
        derivatives_attribution=False,
        derivatives_approval=False,
        derivatives_reciprocal=False,
        uri=PIL_URIS["COMMERCIAL_USE"],
    )

    _commercial_remix = replace(
        COMMON_DEFAULTS,
        commercial_use=True,
        commercial_attribution=True,
        derivatives_allowed=True,
        derivatives_attribution=True,
        derivatives_approval=False,
        derivatives_reciprocal=True,
        uri=PIL_URIS["COMMERCIAL_REMIX"],
    )

    _creative_commons_attribution = replace(
        COMMON_DEFAULTS,
        commercial_use=True,
        commercial_attribution=True,
        derivatives_allowed=True,
        derivatives_attribution=True,
        derivatives_approval=False,
        derivatives_reciprocal=True,
        uri=PIL_URIS["CC_BY"],
    )

    @staticmethod
    def non_commercial_social_remixing(
        override: Optional[LicenseTermsOverride] = None,
    ) -> LicenseTermsInput:
        """
        Gets the values to create a Non-Commercial Social Remixing license terms flavor.

        See: https://docs.story.foundation/concepts/programmable-ip-license/pil-flavors#non-commercial-social-remixing

        :param `override` `Optional[LicenseTermsOverride]`: Optional overrides for the default license terms.
        :return: `LicenseTermsInput`: The license terms.
        """
        terms = _apply_override(PILFlavor._non_commercial_social_remixing_pil, override)
        return PILFlavor.validate_license_terms(terms)

    @staticmethod
    def commercial_use(
        default_minting_fee: int,
        currency: Address,
        royalty_policy: Optional[RoyaltyPolicyInput] = None,
        override: Optional[LicenseTermsOverride] = None,
    ) -> LicenseTermsInput:
        """
        Gets the values to create a Commercial Use license terms flavor.

        See: https://docs.story.foundation/concepts/programmable-ip-license/pil-flavors#commercial-use

        :param `default_minting_fee` int: The fee to be paid when minting a license.
        :param `currency` Address: The ERC20 token to be used to pay the minting fee.
        :param `royalty_policy` `Optional[RoyaltyPolicyInput]`: The type of royalty policy to be used.(default: LAP)
        :param `override` `Optional[LicenseTermsOverride]`: Optional overrides for the default license terms.
        :return: `LicenseTermsInput`: The license terms.
        """
        base = replace(
            PILFlavor._commercial_use,
            default_minting_fee=default_minting_fee,
            currency=currency,
            royalty_policy=royalty_policy,
        )
        terms = _apply_override(base, override)
        return PILFlavor.validate_license_terms(terms)

    @staticmethod
    def commercial_remix(
        default_minting_fee: int,
        currency: Address,
        commercial_rev_share: int,
        royalty_policy: Optional[RoyaltyPolicyInput] = None,
        override: Optional[LicenseTermsOverride] = None,
    ) -> LicenseTermsInput:
        """
        Gets the values to create a Commercial Remixing license terms flavor.

        See: https://docs.story.foundation/concepts/programmable-ip-license/pil-flavors#commercial-remix

        :param `default_minting_fee` int: The fee to be paid when minting a license.
        :param `currency` Address: The ERC20 token to be used to pay the minting fee.
        :param `commercial_rev_share` int: Percentage of revenue that must be shared with the licensor. Must be between 0 and 100.
        :param `royalty_policy` `Optional[RoyaltyPolicyInput]`: The type of royalty policy to be used.(default: LAP)
        :param `override` `Optional[LicenseTermsOverride]`: Optional overrides for the default license terms.
        :return: `LicenseTermsInput`: The license terms.
        """
        base = replace(
            PILFlavor._commercial_remix,
            default_minting_fee=default_minting_fee,
            currency=currency,
            commercial_rev_share=commercial_rev_share,
            royalty_policy=royalty_policy,
        )
        terms = _apply_override(base, override)
        return PILFlavor.validate_license_terms(terms)

    @staticmethod
    def creative_commons_attribution(
        currency: Address,
        royalty_policy: Optional[RoyaltyPolicyInput] = None,
        override: Optional[LicenseTermsOverride] = None,
    ) -> LicenseTermsInput:
        """
        Gets the values to create a Creative Commons Attribution (CC-BY) license terms flavor.

        See: https://docs.story.foundation/concepts/programmable-ip-license/pil-flavors#creative-commons-attribution

        :param `currency` Address: The ERC20 token to be used to pay the minting fee.
        :param `royalty_policy` `Optional[RoyaltyPolicyInput]`: The type of royalty policy to be used.(default: LAP)
        :param `override` `Optional[LicenseTermsOverride]`: Optional overrides for the default license terms.
        :return: `LicenseTermsInput`: The license terms.
        """
        base = replace(
            PILFlavor._creative_commons_attribution,
            currency=currency,
            royalty_policy=royalty_policy,
        )
        terms = _apply_override(base, override)
        return PILFlavor.validate_license_terms(terms)

    @staticmethod
    def validate_license_terms(params: LicenseTermsInput) -> LicenseTermsInput:
        """
        Validates and normalizes license terms.

        :param params `LicenseTermsInput`: The license terms parameters to validate.
        :return: `LicenseTermsInput`: The validated and normalized license terms.
        :raises PILFlavorError: If validation fails.
        """
        # Normalize royalty_policy to address
        royalty_policy = royalty_policy_input_to_address(params.royalty_policy)
        currency = validate_address(params.currency)

        normalized = replace(
            params,
            royalty_policy=royalty_policy,
        )

        # Validate royalty policy and currency relationship
        if royalty_policy != ZERO_ADDRESS and currency == ZERO_ADDRESS:
            raise PILFlavorError(
                "royalty_policy is not zero address and currency cannot be zero address."
            )

        # Validate default_minting_fee
        if normalized.default_minting_fee < 0:
            raise PILFlavorError(
                "default_minting_fee should be greater than or equal to 0."
            )

        if normalized.default_minting_fee > 0 and royalty_policy == ZERO_ADDRESS:
            raise PILFlavorError(
                "royalty_policy is required when default_minting_fee is greater than 0."
            )

        # Validate commercial use and derivatives
        PILFlavor._verify_commercial_use(normalized)
        PILFlavor._verify_derivatives(normalized)

        if normalized.commercial_rev_share > 100 or normalized.commercial_rev_share < 0:
            raise PILFlavorError("commercial_rev_share must be between 0 and 100.")

        return normalized

    @staticmethod
    def _verify_commercial_use(terms: LicenseTermsInput) -> None:
        """Verify commercial use related fields."""
        royalty_policy = royalty_policy_input_to_address(terms.royalty_policy)

        if not terms.commercial_use:
            commercial_fields = [
                ("commercial_attribution", terms.commercial_attribution),
                (
                    "commercializer_checker",
                    terms.commercializer_checker != ZERO_ADDRESS,
                ),
                ("commercial_rev_share", terms.commercial_rev_share > 0),
                ("commercial_rev_ceiling", terms.commercial_rev_ceiling > 0),
                ("derivative_rev_ceiling", terms.derivative_rev_ceiling > 0),
                ("royalty_policy", royalty_policy != ZERO_ADDRESS),
            ]

            for field, value in commercial_fields:
                if value:
                    raise PILFlavorError(
                        f"cannot add {field} when commercial_use is False."
                    )
        else:
            if royalty_policy == ZERO_ADDRESS:
                raise PILFlavorError(
                    "royalty_policy is required when commercial_use is True."
                )

    @staticmethod
    def _verify_derivatives(terms: LicenseTermsInput) -> None:
        """Verify derivatives related fields."""
        if not terms.derivatives_allowed:
            derivative_fields = [
                ("derivatives_attribution", terms.derivatives_attribution),
                ("derivatives_approval", terms.derivatives_approval),
                ("derivatives_reciprocal", terms.derivatives_reciprocal),
                ("derivative_rev_ceiling", terms.derivative_rev_ceiling > 0),
            ]

            for field, value in derivative_fields:
                if value:
                    raise PILFlavorError(
                        f"cannot add {field} when derivatives_allowed is False."
                    )
