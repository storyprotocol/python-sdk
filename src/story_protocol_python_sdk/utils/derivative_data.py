from dataclasses import dataclass, field
from typing import List, Optional

from ens.ens import Address
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
class DerivativeDataInput:
    """
    Input data structure for creating derivative IP assets.

    This type defines the data that users need to provide when creating derivative works.

    Attributes:
        parent_ip_ids: List of parent IP asset addresses that this derivative is based on.
        license_terms_ids: List of license terms IDs corresponding to each parent IP.
        max_minting_fee: [Optional] The maximum minting fee that the caller is willing to pay. if set to 0 then no limit. (default: 0).
        max_rts: [Optional] The maximum number of royalty tokens that can be distributed to the external royalty policies. (max: 100,000,000) (default: 100,000,000).
        max_revenue_share: [Optional] The maximum revenue share percentage allowed for minting the License Tokens. Must be between 0 and 100 (where 100% represents 100,000,000) (default: 100).
        license_template: [Optional] The address of the license template. Defaults to [License Template](https://docs.story.foundation/docs/programmable-ip-license) address if not provided
    """

    parent_ip_ids: List[Address]
    license_terms_ids: List[int]
    max_minting_fee: int | float = field(default=0)
    max_rts: int | float = field(default=MAX_ROYALTY_TOKEN)
    max_revenue_share: int = field(default=100)
    license_template: Optional[Address] = field(default=None)


@dataclass
class DerivativeData:
    """Validated derivative data for IP creation."""

    web3: Web3
    parent_ip_ids: List[str]
    license_terms_ids: List[int]
    max_minting_fee: int | float
    max_rts: int | float
    max_revenue_share: int
    license_template: Optional[str]

    pi_license_template_client: PILicenseTemplateClient = field(init=False)
    ip_asset_registry_client: IPAssetRegistryClient = field(init=False)
    license_registry_client: LicenseRegistryClient = field(init=False)

    @classmethod
    def from_input(
        cls, web3: Web3, input_data: DerivativeDataInput
    ) -> "DerivativeData":
        """
        Create a DerivativeData instance from DerivativeDataInput.

        Args:
            web3: Web3 instance for blockchain interaction
            input_data: User-provided derivative data

        Returns:
            DerivativeData instance with validated data
        """
        return cls(
            web3=web3,
            parent_ip_ids=input_data.parent_ip_ids,
            license_terms_ids=input_data.license_terms_ids,
            max_minting_fee=input_data.max_minting_fee,
            max_rts=input_data.max_rts,
            max_revenue_share=input_data.max_revenue_share,
            license_template=input_data.license_template,
        )

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

        total_royalty_percent = 0
        for parent_ip_id, license_terms_id in zip(
            self.parent_ip_ids, self.license_terms_ids
        ):
            if not Web3.is_checksum_address(parent_ip_id):
                raise ValueError("The parent IP ID must be a valid address.")
            if not self.ip_asset_registry_client.isRegistered(parent_ip_id):
                raise ValueError(f"The parent IP ID {parent_ip_id} must be registered.")
            if not self.license_registry_client.hasIpAttachedLicenseTerms(
                parent_ip_id, self.license_template, license_terms_id
            ):
                raise ValueError(
                    f"License terms id {license_terms_id} must be attached to the parent ipId {parent_ip_id} before registering derivative."
                )
            royalty_percent = self.license_registry_client.getRoyaltyPercent(
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
