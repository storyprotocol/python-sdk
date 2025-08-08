from dataclasses import dataclass, field
from typing import List, Optional

from web3 import Web3

from story_protocol_python_sdk.abi.IPAssetRegistry.IPAssetRegistry_client import (
    IPAssetRegistryClient,
)
from story_protocol_python_sdk.abi.LicenseRegistry.LicenseRegistry_client import (
    LicenseRegistryClient,
)
from story_protocol_python_sdk.abi.PILicenseTemplate.PILicenseTemplate_client import (
    PILicenseTemplateClient,
)
from story_protocol_python_sdk.types.common import RevShareType
from story_protocol_python_sdk.utils.constants import MAX_ROYALTY_TOKEN, ZERO_ADDRESS
from story_protocol_python_sdk.utils.validation import get_revenue_share


@dataclass
class DerivativeData:
    """Validated derivative data for IP creation."""

    web3: Web3
    parent_ip_ids: List[str]
    license_terms_ids: List[int]
    max_minting_fee: int | float = field(default=0)
    max_rts: int | float = field(default=MAX_ROYALTY_TOKEN)
    max_revenue_share: int = field(default=100)
    license_template: Optional[str] = field(default=None)

    pi_license_template_client: PILicenseTemplateClient = field(init=False)
    ip_asset_registry_client: IPAssetRegistryClient = field(init=False)
    license_registry_client: LicenseRegistryClient = field(init=False)

    def __post_init__(self):
        """Initialize clients and validate data after object creation."""

        self.pi_license_template_client = PILicenseTemplateClient(self.web3)
        self.ip_asset_registry_client = IPAssetRegistryClient(self.web3)
        self.license_registry_client = LicenseRegistryClient(self.web3)

        if self.license_template is None:
            self.license_template = self.pi_license_template_client.contract.address
        self.max_revenue_share = get_revenue_share(
            self.max_revenue_share, type=RevShareType.MAX_REVENUE_SHARE
        )

        self.validate_max_minting_fee()
        self.validate_max_rts()
        self.validate_parent_ip_ids_and_license_terms_ids()

    def validate_parent_ip_ids_and_license_terms_ids(self):
        if len(self.parent_ip_ids) == 0:
            raise ValueError("The parent IP IDs must be provided.")

        if len(self.license_terms_ids) == 0:
            raise ValueError("The license terms IDs must be provided.")

        if len(self.parent_ip_ids) != len(self.license_terms_ids):
            raise ValueError(
                "The number of parent IP IDs must match the number of license terms IDs."
            )

        ip_asset_registry_client: IPAssetRegistryClient = self.ip_asset_registry_client
        license_registry_client: LicenseRegistryClient = self.license_registry_client
        total_royalty_percent = 0
        for parent_ip_id, license_terms_id in zip(
            self.parent_ip_ids, self.license_terms_ids
        ):
            if not Web3.is_checksum_address(parent_ip_id):
                raise ValueError("The parent IP ID must be a valid address.")
            if not ip_asset_registry_client.isRegistered(parent_ip_id):
                raise ValueError(f"The parent IP ID {parent_ip_id} must be registered.")
            if not license_registry_client.hasIpAttachedLicenseTerms(
                parent_ip_id, self.license_template, license_terms_id
            ):
                raise ValueError(
                    f"License terms id {license_terms_id} must be attached to the parent ipId {parent_ip_id} before registering derivative."
                )
            royalty_percent = license_registry_client.getRoyaltyPercent(
                parent_ip_id, self.license_template, license_terms_id
            )
            total_royalty_percent += royalty_percent
            if (
                self.max_revenue_share != 0
                and total_royalty_percent > self.max_revenue_share
            ):
                raise ValueError(
                    f"The total royalty percent for the parent IP {parent_ip_id} is greater than the maximum revenue share {self.max_revenue_share}."
                )

    def validate_max_minting_fee(self):
        if self.max_minting_fee < 0:
            raise ValueError("The max minting fee must be greater than 0.")

    def validate_max_rts(self):
        if self.max_rts < 0 or self.max_rts > MAX_ROYALTY_TOKEN:
            raise ValueError(
                f"The maxRts must be greater than 0 and less than {MAX_ROYALTY_TOKEN}."
            )

    def get_validated_data(self) -> dict:
        return {
            "parentIpIds": self.parent_ip_ids,
            "licenseTermsIds": self.license_terms_ids,
            "maxMintingFee": self.max_minting_fee,
            "maxRts": self.max_rts,
            "maxRevenueShare": self.max_revenue_share,
            "licenseTemplate": self.license_template,
            "royaltyContext": ZERO_ADDRESS,
        }
