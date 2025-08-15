# src/story_protocol_python_sdk/utils/license_terms.py

from ens.async_ens import HexStr
from web3 import Web3

from story_protocol_python_sdk.abi.RoyaltyModule.RoyaltyModule_client import (
    RoyaltyModuleClient,
)
from story_protocol_python_sdk.types.common import RevShareType
from story_protocol_python_sdk.utils.constants import (
    ROYALTY_POLICY_LAP_ADDRESS,
    ZERO_ADDRESS,
)
from story_protocol_python_sdk.utils.validation import get_revenue_share


class LicenseTerms:
    def __init__(self, web3: Web3):
        self.web3 = web3
        self.royalty_module_client = RoyaltyModuleClient(web3)

    PIL_TYPE = {
        "NON_COMMERCIAL_REMIX": "non_commercial_remix",
        "COMMERCIAL_USE": "commercial_use",
        "COMMERCIAL_REMIX": "commercial_remix",
    }

    def get_license_term_by_type(self, type, term=None):
        license_terms = {
            "transferable": True,
            "royaltyPolicy": "0x0000000000000000000000000000000000000000",
            "defaultMintingFee": 0,
            "expiration": 0,
            "commercialUse": False,
            "commercialAttribution": False,
            "commercializerChecker": "0x0000000000000000000000000000000000000000",
            "commercializerCheckerData": "0x0000000000000000000000000000000000000000",
            "commercialRevShare": 0,
            "commercialRevCeiling": 0,
            "derivativesAllowed": True,
            "derivativesAttribution": True,
            "derivativesApproval": False,
            "derivativesReciprocal": True,
            "derivativeRevCeiling": 0,
            "currency": "0x0000000000000000000000000000000000000000",
            "uri": "",
        }

        if type == self.PIL_TYPE["NON_COMMERCIAL_REMIX"]:
            license_terms["commercializerCheckerData"] = "0x"
            return license_terms
        elif type == self.PIL_TYPE["COMMERCIAL_USE"]:
            if not term or "defaultMintingFee" not in term or "currency" not in term:
                raise ValueError(
                    "DefaultMintingFee, currency are required for commercial use PIL."
                )

            if term["royaltyPolicyAddress"] is None:
                term["royaltyPolicyAddress"] = ROYALTY_POLICY_LAP_ADDRESS

            license_terms.update(
                {
                    "defaultMintingFee": int(term["defaultMintingFee"]),
                    "currency": term["currency"],
                    "commercialUse": True,
                    "commercialAttribution": True,
                    "derivativesReciprocal": False,
                    "royaltyPolicy": term["royaltyPolicyAddress"],
                }
            )
            return license_terms
        else:
            if (
                not term
                or "defaultMintingFee" not in term
                or "currency" not in term
                or "commercialRevShare" not in term
            ):
                raise ValueError(
                    "DefaultMintingFee, currency and commercialRevShare are required for commercial remix PIL."
                )

            if "royaltyPolicyAddress" not in term:
                raise ValueError("royaltyPolicyAddress is required")

            if term["commercialRevShare"] < 0 or term["commercialRevShare"] > 100:
                raise ValueError("CommercialRevShare should be between 0 and 100.")

            license_terms.update(
                {
                    "defaultMintingFee": int(term["defaultMintingFee"]),
                    "currency": term["currency"],
                    "commercialUse": True,
                    "commercialAttribution": True,
                    "commercialRevShare": get_revenue_share(term["commercialRevShare"]),
                    "derivativesReciprocal": True,
                    "royaltyPolicy": term["royaltyPolicyAddress"],
                }
            )
            return license_terms

    def validate_license_terms(self, params):
        royalty_policy = params.get("royalty_policy")
        currency = params.get("currency")
        if royalty_policy != ZERO_ADDRESS:
            is_whitelisted = self.royalty_module_client.isWhitelistedRoyaltyPolicy(
                royalty_policy
            )
            if not is_whitelisted:
                raise ValueError("The royalty policy is not whitelisted.")

        if currency != ZERO_ADDRESS:
            is_whitelisted = self.royalty_module_client.isWhitelistedRoyaltyToken(
                currency
            )
            if not is_whitelisted:
                raise ValueError("The currency token is not whitelisted.")

        if royalty_policy != ZERO_ADDRESS and currency == ZERO_ADDRESS:
            raise ValueError("Royalty policy requires currency token.")

        commercial_rev_share = params.get("commercial_rev_share", 0)
        if commercial_rev_share < 0 or commercial_rev_share > 100:
            raise ValueError("commercial_rev_share should be between 0 and 100.")

        validated_params = {
            "transferable": params.get("transferable"),
            "royaltyPolicy": params.get("royalty_policy"),
            "defaultMintingFee": int(params.get("default_minting_fee", 0)),
            "expiration": int(params.get("expiration", 0)),
            "commercialUse": params.get("commercial_use"),
            "commercialAttribution": params.get("commercial_attribution"),
            "commercializerChecker": params.get("commercializer_checker"),
            "commercializerCheckerData": Web3.to_bytes(
                hexstr=HexStr(params.get("commercializer_checker_data", ZERO_ADDRESS))
            ),
            "commercialRevShare": get_revenue_share(
                params.get("commercial_rev_share", 0)
            ),
            "commercialRevCeiling": int(params.get("commercial_rev_ceiling", 0)),
            "derivativesAllowed": params.get("derivatives_allowed"),
            "derivativesAttribution": params.get("derivatives_attribution"),
            "derivativesApproval": params.get("derivatives_approval"),
            "derivativesReciprocal": params.get("derivatives_reciprocal"),
            "derivativeRevCeiling": int(params.get("derivative_rev_ceiling", 0)),
            "currency": params.get("currency"),
            "uri": params.get("uri"),
        }

        self.verify_commercial_use(validated_params)
        self.verify_derivatives(validated_params)
        return validated_params

    def validate_licensing_config(self, params):
        if not isinstance(params, dict):
            raise TypeError("Licensing config parameters must be a dictionary")

        required_params = {
            "is_set": bool,
            "minting_fee": int,
            "hook_data": str,
            "licensing_hook": str,
            "commercial_rev_share": int,
            "disabled": bool,
            "expect_minimum_group_reward_share": int,
            "expect_group_reward_pool": str,
        }

        for param, expected_type in required_params.items():
            if param in params:
                if not isinstance(params[param], expected_type):
                    raise TypeError(f"{param} must be of type {expected_type.__name__}")

        default_params = {
            "isSet": False,
            "mintingFee": 0,
            "hookData": ZERO_ADDRESS,
            "licensingHook": ZERO_ADDRESS,
            "commercialRevShare": 0,
            "disabled": False,
            "expectMinimumGroupRewardShare": 0,
            "expectGroupRewardPool": ZERO_ADDRESS,
        }

        if not params.get("is_set", False):
            return default_params

        if params.get("minting_fee", 0) < 0:
            raise ValueError("Minting fee cannot be negative")

        if (
            params.get("commercial_rev_share", 0) < 0
            or params.get("commercial_rev_share", 0) > 100
        ):
            raise ValueError("Commercial revenue share must be between 0 and 100")
        if (
            params.get("expect_minimum_group_reward_share", 0) < 0
            or params.get("expect_minimum_group_reward_share", 0) > 100
        ):
            raise ValueError(
                "Expect minimum group reward share must be between 0 and 100"
            )
        validated_params = {
            "isSet": params.get("is_set", False),
            "mintingFee": params.get("minting_fee", 0),
            "hookData": Web3.to_bytes(hexstr=HexStr(params["hook_data"])),
            "licensingHook": params.get("licensing_hook", ZERO_ADDRESS),
            "commercialRevShare": get_revenue_share(params["commercial_rev_share"]),
            "disabled": params.get("disabled", False),
            "expectMinimumGroupRewardShare": get_revenue_share(
                params["expect_minimum_group_reward_share"],
                RevShareType.EXPECT_MINIMUM_GROUP_REWARD_SHARE,
            ),
            "expectGroupRewardPool": params.get(
                "expect_group_reward_pool", ZERO_ADDRESS
            ),
        }

        return validated_params

    def verify_commercial_use(self, terms):
        if not terms.get("commercialUse", False):
            if terms.get("commercialAttribution", False):
                raise ValueError(
                    "Cannot add commercial attribution when commercial use is disabled."
                )
            if terms.get("commercializerChecker") != ZERO_ADDRESS:
                raise ValueError(
                    "Cannot add commercializerChecker when commercial use is disabled."
                )
            if terms.get("commercialRevShare", 0) > 0:
                raise ValueError(
                    "Cannot add commercial revenue share when commercial use is disabled."
                )
            if terms.get("commercialRevCeiling", 0) > 0:
                raise ValueError(
                    "Cannot add commercial revenue ceiling when commercial use is disabled."
                )
            if terms.get("derivativeRevCeiling", 0) > 0:
                raise ValueError(
                    "Cannot add derivative revenue ceiling when commercial use is disabled."
                )
            if terms.get("royaltyPolicy") != ZERO_ADDRESS:
                raise ValueError(
                    "Cannot add commercial royalty policy when commercial use is disabled."
                )
        else:
            if terms.get("royaltyPolicy") == ZERO_ADDRESS:
                raise ValueError(
                    "Royalty policy is required when commercial use is enabled."
                )

    def verify_derivatives(self, terms):
        if not terms.get("derivativesAllowed", False):
            if terms.get("derivativesAttribution", False):
                raise ValueError(
                    "Cannot add derivative attribution when derivative use is disabled."
                )
            if terms.get("derivativesApproval", False):
                raise ValueError(
                    "Cannot add derivative approval when derivative use is disabled."
                )
            if terms.get("derivativesReciprocal", False):
                raise ValueError(
                    "Cannot add derivative reciprocal when derivative use is disabled."
                )
            if terms.get("derivativeRevCeiling", 0) > 0:
                raise ValueError(
                    "Cannot add derivative revenue ceiling when derivative use is disabled."
                )

    def get_revenue_share(self, rev_share: int | str) -> int:
        """
        Convert revenue share percentage to token amount.

        :param rev_share int|str: Revenue share percentage between 0-100
        :return int: Revenue share token amount
        """
        try:
            rev_share_number = float(rev_share)
        except ValueError:
            raise ValueError("CommercialRevShare must be a valid number.")

        if rev_share_number < 0 or rev_share_number > 100:
            raise ValueError("CommercialRevShare should be between 0 and 100.")

        MAX_ROYALTY_TOKEN = 100000000
        return int((rev_share_number / 100) * MAX_ROYALTY_TOKEN)
