"""Registration utilities for IP asset operations."""

from dataclasses import asdict, is_dataclass, replace

from ens.ens import Address
from web3 import Web3

from story_protocol_python_sdk.abi.ModuleRegistry.ModuleRegistry_client import (
    ModuleRegistryClient,
)
from story_protocol_python_sdk.abi.RoyaltyModule.RoyaltyModule_client import (
    RoyaltyModuleClient,
)
from story_protocol_python_sdk.abi.SPGNFTImpl.SPGNFTImpl_client import SPGNFTImplClient
from story_protocol_python_sdk.types.resource.IPAsset import LicenseTermsDataInput
from story_protocol_python_sdk.types.resource.License import LicenseTermsInput
from story_protocol_python_sdk.utils.constants import ZERO_ADDRESS
from story_protocol_python_sdk.utils.licensing_config_data import LicensingConfigData
from story_protocol_python_sdk.utils.pil_flavor import PILFlavor
from story_protocol_python_sdk.utils.util import convert_dict_keys_to_camel_case
from story_protocol_python_sdk.utils.validation import (
    get_revenue_share,
    validate_address,
)


def get_public_minting(spg_nft_contract: Address, web3: Web3) -> bool:
    """
    Check if SPG NFT contract has public minting enabled.

    Args:
        spg_nft_contract: The address of the SPG NFT contract.
        web3: Web3 instance.

    Returns:
        True if public minting is enabled, False otherwise.
    """
    spg_client = SPGNFTImplClient(
        web3, contract_address=validate_address(spg_nft_contract)
    )
    return spg_client.publicMinting()


def validate_license_terms_data(
    license_terms_data: list[LicenseTermsDataInput] | list[dict],
    web3: Web3,
) -> list[dict]:
    """
    Validate the license terms data.

    Args:
        license_terms_data: The license terms data to validate.
        web3: Web3 instance.

    Returns:
        The validated license terms data.
    """
    royalty_module_client = RoyaltyModuleClient(web3)
    module_registry_client = ModuleRegistryClient(web3)

    validated_license_terms_data = []
    for term in license_terms_data:
        if is_dataclass(term):
            terms_dict = asdict(term.terms)
            licensing_config_dict = term.licensing_config
        else:
            terms_dict = term["terms"]
            licensing_config_dict = term["licensing_config"]

        license_terms = PILFlavor.validate_license_terms(
            LicenseTermsInput(**terms_dict)
        )
        license_terms = replace(
            license_terms,
            commercial_rev_share=get_revenue_share(license_terms.commercial_rev_share),
        )
        if license_terms.royalty_policy != ZERO_ADDRESS:
            is_whitelisted = royalty_module_client.isWhitelistedRoyaltyPolicy(
                license_terms.royalty_policy
            )
            if not is_whitelisted:
                raise ValueError("The royalty_policy is not whitelisted.")

        if license_terms.currency != ZERO_ADDRESS:
            is_whitelisted = royalty_module_client.isWhitelistedRoyaltyToken(
                license_terms.currency
            )
            if not is_whitelisted:
                raise ValueError("The currency is not whitelisted.")

        validated_license_terms_data.append(
            {
                "terms": convert_dict_keys_to_camel_case(asdict(license_terms)),
                "licensingConfig": LicensingConfigData.validate_license_config(
                    module_registry_client, licensing_config_dict
                ),
            }
        )
    return validated_license_terms_data
