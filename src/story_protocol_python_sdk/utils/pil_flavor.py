from typing import Optional, TypedDict

from ens.ens import Address
from typing_extensions import cast

from story_protocol_python_sdk.types.resource.License import LicenseTermsInput
from story_protocol_python_sdk.types.resource.Royalty import RoyaltyPolicyInput
from story_protocol_python_sdk.utils.constants import ZERO_ADDRESS
from story_protocol_python_sdk.utils.royalty import royalty_policy_input_to_address
from story_protocol_python_sdk.utils.validation import validate_address


class LicenseTerms(TypedDict):
    """
    The normalized license terms structure used internally by the SDK.
    Uses camelCase keys to match the contract interface.
    """

    transferable: bool
    royaltyPolicy: Address
    defaultMintingFee: int
    expiration: int
    commercialUse: bool
    commercialAttribution: bool
    commercializerChecker: Address
    commercializerCheckerData: str
    commercialRevShare: int
    commercialRevCeiling: int
    derivativesAllowed: bool
    derivativesAttribution: bool
    derivativesApproval: bool
    derivativesReciprocal: bool
    derivativeRevCeiling: int
    currency: Address
    uri: str


class LicenseTermsOverride(TypedDict, total=False):
    """
    Optional override parameters for license terms.
    Uses snake_case keys following SDK conventions.
    """

    transferable: bool
    """Whether the license is transferable."""
    royalty_policy: RoyaltyPolicyInput
    """The type of royalty policy to be used."""
    default_minting_fee: int
    """The fee to be paid when minting a license."""
    expiration: int
    """The expiration period of the license."""
    commercial_use: bool
    """Whether commercial use is allowed."""
    commercial_attribution: bool
    """Whether commercial attribution is required."""
    commercializer_checker: Address
    """The address of the commercializer checker contract."""
    commercializer_checker_data: str
    """Percentage of revenue that must be shared with the licensor. Must be between 0 and 100."""
    commercial_rev_share: int
    """Percentage of revenue that must be shared with the licensor."""
    commercial_rev_ceiling: int
    """The maximum revenue that can be collected from commercial use."""
    derivatives_allowed: bool
    """Whether derivatives are allowed."""
    derivatives_attribution: bool
    """Whether attribution is required for derivatives."""
    derivatives_approval: bool
    """Whether approval is required for derivatives."""
    derivatives_reciprocal: bool
    """Whether derivatives must have the same license terms."""
    derivative_rev_ceiling: int
    """The maximum revenue that can be collected from derivatives."""
    currency: Address
    """The ERC20 token to be used to pay the minting fee."""
    uri: str
    """The URI of the license terms."""


class NonCommercialSocialRemixingRequest(TypedDict, total=False):
    """Request parameters for non-commercial social remixing license."""

    override: LicenseTermsOverride
    """Optional overrides for the default license terms."""


class CommercialUseRequest(TypedDict, total=False):
    """Request parameters for commercial use license."""

    default_minting_fee: int
    """The fee to be paid when minting a license."""
    currency: Address
    """The ERC20 token to be used to pay the minting fee."""
    royalty_policy: RoyaltyPolicyInput
    """The type of royalty policy to be used. Default is LAP."""
    override: LicenseTermsOverride
    """Optional overrides for the default license terms."""


class CommercialRemixRequest(TypedDict, total=False):
    """Request parameters for commercial remix license."""

    default_minting_fee: int
    """The fee to be paid when minting a license."""
    commercial_rev_share: int
    """Percentage of revenue that must be shared with the licensor. Must be between 0 and 100."""
    currency: Address
    """The ERC20 token to be used to pay the minting fee."""
    royalty_policy: RoyaltyPolicyInput
    """The type of royalty policy to be used. Default is LAP."""
    override: LicenseTermsOverride
    """Optional overrides for the default license terms."""


class CreativeCommonsAttributionRequest(TypedDict, total=False):
    """Request parameters for creative commons attribution license."""

    currency: Address
    """The ERC20 token to be used to pay the minting fee."""
    royalty_policy: RoyaltyPolicyInput
    """The type of royalty policy to be used. Default is LAP."""
    override: LicenseTermsOverride
    """Optional overrides for the default license terms."""


# PIL URIs for off-chain terms
PIL_URIS = {
    "NCSR": "https://github.com/piplabs/pil-document/blob/998c13e6ee1d04eb817aefd1fe16dfe8be3cd7a2/off-chain-terms/NCSR.json",
    "COMMERCIAL_USE": "https://github.com/piplabs/pil-document/blob/9a1f803fcf8101a8a78f1dcc929e6014e144ab56/off-chain-terms/CommercialUse.json",
    "COMMERCIAL_REMIX": "https://github.com/piplabs/pil-document/blob/ad67bb632a310d2557f8abcccd428e4c9c798db1/off-chain-terms/CommercialRemix.json",
    "CC_BY": "https://github.com/piplabs/pil-document/blob/998c13e6ee1d04eb817aefd1fe16dfe8be3cd7a2/off-chain-terms/CC-BY.json",
}

# Common default values for license terms
COMMON_DEFAULTS: LicenseTerms = {
    "transferable": True,
    "royaltyPolicy": ZERO_ADDRESS,
    "defaultMintingFee": 0,
    "expiration": 0,
    "commercialUse": False,
    "commercialAttribution": False,
    "commercializerChecker": ZERO_ADDRESS,
    "commercializerCheckerData": ZERO_ADDRESS,
    "commercialRevShare": 0,
    "commercialRevCeiling": 0,
    "derivativesAllowed": False,
    "derivativesAttribution": False,
    "derivativesApproval": False,
    "derivativesReciprocal": False,
    "derivativeRevCeiling": 0,
    "currency": ZERO_ADDRESS,
    "uri": "",
}


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

    _non_commercial_social_remixing_pil: LicenseTerms = {
        **COMMON_DEFAULTS,
        "commercialUse": False,
        "commercialAttribution": False,
        "derivativesAllowed": True,
        "derivativesAttribution": True,
        "derivativesApproval": False,
        "derivativesReciprocal": True,
        "uri": PIL_URIS["NCSR"],
    }

    _commercial_use: LicenseTerms = {
        **COMMON_DEFAULTS,
        "commercialUse": True,
        "commercialAttribution": True,
        "derivativesAllowed": False,
        "derivativesAttribution": False,
        "derivativesApproval": False,
        "derivativesReciprocal": False,
        "uri": PIL_URIS["COMMERCIAL_USE"],
    }

    _commercial_remix: LicenseTerms = {
        **COMMON_DEFAULTS,
        "commercialUse": True,
        "commercialAttribution": True,
        "derivativesAllowed": True,
        "derivativesAttribution": True,
        "derivativesApproval": False,
        "derivativesReciprocal": True,
        "uri": PIL_URIS["COMMERCIAL_REMIX"],
    }

    _creative_commons_attribution: LicenseTerms = {
        **COMMON_DEFAULTS,
        "commercialUse": True,
        "commercialAttribution": True,
        "derivativesAllowed": True,
        "derivativesAttribution": True,
        "derivativesApproval": False,
        "derivativesReciprocal": True,
        "uri": PIL_URIS["CC_BY"],
    }

    # Mapping from snake_case to camelCase for license terms
    _OVERRIDE_KEY_MAP = {
        "transferable": "transferable",
        "royalty_policy": "royaltyPolicy",
        "default_minting_fee": "defaultMintingFee",
        "expiration": "expiration",
        "commercial_use": "commercialUse",
        "commercial_attribution": "commercialAttribution",
        "commercializer_checker": "commercializerChecker",
        "commercializer_checker_data": "commercializerCheckerData",
        "commercial_rev_share": "commercialRevShare",
        "commercial_rev_ceiling": "commercialRevCeiling",
        "derivatives_allowed": "derivativesAllowed",
        "derivatives_attribution": "derivativesAttribution",
        "derivatives_approval": "derivativesApproval",
        "derivatives_reciprocal": "derivativesReciprocal",
        "derivative_rev_ceiling": "derivativeRevCeiling",
        "currency": "currency",
        "uri": "uri",
    }

    @staticmethod
    def _convert_override_to_camel_case(override: LicenseTermsOverride) -> dict:
        """Convert snake_case override keys to camelCase for internal use."""
        result = {}
        for key, value in override.items():
            camel_key = PILFlavor._OVERRIDE_KEY_MAP.get(key)
            if camel_key:
                result[camel_key] = value
        return result

    @staticmethod
    def _convert_camel_case_to_snake_case(camel_case_key: str) -> str:
        """Convert camelCase to snake_case for internal use."""
        for key, value in PILFlavor._OVERRIDE_KEY_MAP.items():
            if value == camel_case_key:
                return key
        raise ValueError(f"Unknown camelCase key: {camel_case_key}")  # pragma: no cover

    @staticmethod
    def _convert_camel_case_to_snake_case_license_terms(
        terms: LicenseTerms,
    ) -> LicenseTermsInput:
        """Convert license terms to LicenseTermsInput."""
        result = {}
        for key, value in terms.items():
            if key in PILFlavor._OVERRIDE_KEY_MAP:
                result[PILFlavor._convert_camel_case_to_snake_case(key)] = value
        return cast(LicenseTermsInput, result)

    @staticmethod
    def non_commercial_social_remixing(
        override: Optional[LicenseTermsOverride] = None,
    ) -> LicenseTermsInput:
        """
        Gets the values to create a Non-Commercial Social Remixing license terms flavor.

        See: https://docs.story.foundation/concepts/programmable-ip-license/pil-flavors#non-commercial-social-remixing

        :param override: Optional overrides for the default license terms.
        :return: The license terms dictionary.
        """
        terms = {**PILFlavor._non_commercial_social_remixing_pil}
        if override:
            terms.update(PILFlavor._convert_override_to_camel_case(override))
        validated_terms = PILFlavor.validate_license_terms(terms)
        return PILFlavor._convert_camel_case_to_snake_case_license_terms(
            validated_terms
        )

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

        :param default_minting_fee: The fee to be paid when minting a license.
        :param currency: The ERC20 token to be used to pay the minting fee.
        :param royalty_policy: The type of royalty policy to be used. Default is LAP.
        :param override: Optional overrides for the default license terms.
        :return: The license terms dictionary.
        """
        terms = {
            **PILFlavor._commercial_use,
            "defaultMintingFee": default_minting_fee,
            "currency": currency,
            "royaltyPolicy": royalty_policy,
        }
        if override:
            terms.update(PILFlavor._convert_override_to_camel_case(override))
        validated_terms = PILFlavor.validate_license_terms(terms)
        return PILFlavor._convert_camel_case_to_snake_case_license_terms(
            validated_terms
        )

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

        :param default_minting_fee: The fee to be paid when minting a license.
        :param currency: The ERC20 token to be used to pay the minting fee.
        :param commercial_rev_share: Percentage of revenue that must be shared with the licensor. Must be between 0 and 100.
        :param royalty_policy: The type of royalty policy to be used. Default is LAP.
        :param override: Optional overrides for the default license terms.
        :return: The license terms dictionary.
        """
        terms = {
            **PILFlavor._commercial_remix,
            "defaultMintingFee": default_minting_fee,
            "currency": currency,
            "commercialRevShare": commercial_rev_share,
            "royaltyPolicy": royalty_policy,
        }
        if override:
            terms.update(PILFlavor._convert_override_to_camel_case(override))
        validated_terms = PILFlavor.validate_license_terms(terms)
        return PILFlavor._convert_camel_case_to_snake_case_license_terms(
            validated_terms
        )

    @staticmethod
    def creative_commons_attribution(
        currency: Address,
        royalty_policy: Optional[RoyaltyPolicyInput] = None,
        override: Optional[LicenseTermsOverride] = None,
    ) -> LicenseTermsInput:
        """
        Gets the values to create a Creative Commons Attribution (CC-BY) license terms flavor.

        See: https://docs.story.foundation/concepts/programmable-ip-license/pil-flavors#creative-commons-attribution

        :param currency: The ERC20 token to be used to pay the minting fee.
        :param royalty_policy: The type of royalty policy to be used. Default is LAP.
        :param override: Optional overrides for the default license terms.
        :return: The license terms dictionary.
        """
        terms = {
            **PILFlavor._creative_commons_attribution,
            "currency": currency,
            "royaltyPolicy": royalty_policy,
        }
        if override:
            terms.update(PILFlavor._convert_override_to_camel_case(override))
        validated_terms = PILFlavor.validate_license_terms(terms)
        return PILFlavor._convert_camel_case_to_snake_case_license_terms(
            validated_terms
        )

    @staticmethod
    def validate_license_terms(params: dict) -> LicenseTerms:
        """
        Validates and normalizes license terms.

        :param params: The license terms parameters to validate.
        :return: The validated and normalized license terms.
        :raises PILFlavorError: If validation fails.
        """
        normalized: LicenseTerms = {
            "transferable": params.get("transferable", True),
            "royaltyPolicy": royalty_policy_input_to_address(
                params.get("royaltyPolicy")
            ),
            "defaultMintingFee": int(params.get("defaultMintingFee", 0)),
            "expiration": int(params.get("expiration", 0)),
            "commercialUse": params.get("commercialUse", False),
            "commercialAttribution": params.get("commercialAttribution", False),
            "commercializerChecker": params.get("commercializerChecker", ZERO_ADDRESS),
            "commercializerCheckerData": params.get(
                "commercializerCheckerData", ZERO_ADDRESS
            ),
            "commercialRevShare": params.get("commercialRevShare", 0),
            "commercialRevCeiling": int(params.get("commercialRevCeiling", 0)),
            "derivativesAllowed": params.get("derivativesAllowed", False),
            "derivativesAttribution": params.get("derivativesAttribution", False),
            "derivativesApproval": params.get("derivativesApproval", False),
            "derivativesReciprocal": params.get("derivativesReciprocal", False),
            "derivativeRevCeiling": int(params.get("derivativeRevCeiling", 0)),
            "currency": validate_address(params.get("currency", ZERO_ADDRESS)),
            "uri": params.get("uri", ""),
        }

        royalty_policy = normalized["royaltyPolicy"]
        currency = normalized["currency"]

        # Validate royalty policy and currency relationship
        if royalty_policy != ZERO_ADDRESS and currency == ZERO_ADDRESS:
            raise PILFlavorError(
                "royalty_policy is not zero address and currency cannot be zero address."
            )

        # Validate defaultMintingFee
        if normalized["defaultMintingFee"] < 0:
            raise PILFlavorError(
                "default_minting_fee should be greater than or equal to 0."
            )

        if (
            normalized["defaultMintingFee"] > 0
            and normalized["royaltyPolicy"] == ZERO_ADDRESS
        ):
            raise PILFlavorError(
                "royalty_policy is required when default_minting_fee is greater than 0."
            )

        # Validate commercial use and derivatives
        PILFlavor._verify_commercial_use(normalized)
        PILFlavor._verify_derivatives(normalized)

        if (
            normalized["commercialRevShare"] > 100
            or normalized["commercialRevShare"] < 0
        ):
            raise PILFlavorError("commercial_rev_share must be between 0 and 100.")

        return normalized

    @staticmethod
    def _verify_commercial_use(terms: LicenseTerms) -> None:
        """Verify commercial use related fields."""
        if not terms["commercialUse"]:
            commercial_fields = [
                ("commercialAttribution", terms["commercialAttribution"]),
                (
                    "commercializerChecker",
                    terms["commercializerChecker"] != ZERO_ADDRESS,
                ),
                ("commercialRevShare", terms["commercialRevShare"] > 0),
                ("commercialRevCeiling", terms["commercialRevCeiling"] > 0),
                ("derivativeRevCeiling", terms["derivativeRevCeiling"] > 0),
                ("royaltyPolicy", terms["royaltyPolicy"] != ZERO_ADDRESS),
            ]

            for field, value in commercial_fields:
                if value:
                    raise PILFlavorError(
                        f"cannot add {PILFlavor._convert_camel_case_to_snake_case(field)} when commercial_use is False."
                    )
        else:
            if terms["royaltyPolicy"] == ZERO_ADDRESS:
                raise PILFlavorError(
                    "royalty_policy is required when commercial_use is True."
                )

    @staticmethod
    def _verify_derivatives(terms: LicenseTerms) -> None:
        """Verify derivatives related fields."""
        if not terms["derivativesAllowed"]:
            derivative_fields = [
                ("derivativesAttribution", terms["derivativesAttribution"]),
                ("derivativesApproval", terms["derivativesApproval"]),
                ("derivativesReciprocal", terms["derivativesReciprocal"]),
                ("derivativeRevCeiling", terms["derivativeRevCeiling"] > 0),
            ]

            for field, value in derivative_fields:
                if value:
                    raise PILFlavorError(
                        f"cannot add {PILFlavor._convert_camel_case_to_snake_case(field)} when derivatives_allowed is False."
                    )
