from dataclasses import dataclass
from typing import TypedDict

from ens.ens import Address, HexStr

from story_protocol_python_sdk.abi.ModuleRegistry.ModuleRegistry_client import (
    ModuleRegistryClient,
)
from story_protocol_python_sdk.types.common import RevShareType
from story_protocol_python_sdk.utils.constants import ZERO_ADDRESS, ZERO_HASH
from story_protocol_python_sdk.utils.validation import (
    get_revenue_share,
    validate_address,
)


class LicensingConfig(TypedDict):
    """
    Structure for licensing configuration.

    Attributes:
        is_set: Whether the licensing configuration is active. If false, the configuration is ignored.
        minting_fee: The minting fee to be paid when minting license tokens.
        licensing_hook: The licensingHook is an address to a smart contract that implements the `ILicensingHook` interface.
            This contract's `beforeMintLicenseTokens` function is executed before a user mints a License Token,
            allowing for custom validation or business logic to be enforced during the minting process.
            For detailed documentation on licensing hook, visit https://docs.story.foundation/concepts/hooks#licensing-hooks
        hook_data: The data to be used by the licensing hook. For detailed documentation on hook data, visit https://docs.story.foundation/concepts/hooks#hook-data
        commercial_rev_share: Percentage of revenue that must be shared with the licensor. Must be between 0 and 100 (where 100% represents 100_000_000).
        disabled: Whether the licensing is disabled or not. If this is true, then no licenses can be minted and no more derivatives can be attached at all.
        expect_minimum_group_reward_share: The minimum percentage of the group’s reward share (from 0 to 100%, represented as 100_000_000) that can be allocated to the IP when it is added to the group.
            Must be between 0 and 100 (where 100% represents 100_000_000).
        expect_group_reward_pool: The address of the expected group reward pool. The IP can only be added to a group with this specified reward pool address, or `zeroAddress` if the IP does not want to be added to any group.
            For detailed documentation on group reward pool, visit https://docs.story.foundation/concepts/hooks#group-reward-pool
    """

    is_set: bool
    minting_fee: int
    licensing_hook: Address
    hook_data: HexStr
    commercial_rev_share: int
    disabled: bool
    expect_minimum_group_reward_share: int
    expect_group_reward_pool: Address


class ValidatedLicensingConfig(TypedDict):
    """
    Validated licensing configuration.
    """

    isSet: bool
    mintingFee: int
    licensingHook: Address
    hookData: HexStr
    commercialRevShare: int
    disabled: bool
    expectMinimumGroupRewardShare: int
    expectGroupRewardPool: Address


@dataclass
class LicensingConfigData:
    """
    Licensing configuration data.
    """

    @classmethod
    def from_tuple(cls, tuple_data: tuple) -> LicensingConfig:
        """
        Convert tuple data to LicensingConfig.

        Args:
            tuple_data: tuple data

        Returns:
            LicensingConfig
        """
        return LicensingConfig(
            is_set=tuple_data[0],
            minting_fee=tuple_data[1],
            licensing_hook=tuple_data[2],
            hook_data=tuple_data[3],
            commercial_rev_share=tuple_data[4],
            disabled=tuple_data[5],
            expect_minimum_group_reward_share=tuple_data[6],
            expect_group_reward_pool=tuple_data[7],
        )

    @classmethod
    def validate_license_config(
        cls,
        module_registry_client: ModuleRegistryClient,
        licensing_config: LicensingConfig | None = None,
    ) -> ValidatedLicensingConfig:
        """
        Validates and normalizes licensing configuration.

        If no licensing_config is provided, returns default values.

        Args:
            licensing_config: Optional licensing configuration input

        Returns:
            LicensingConfig: Validated and normalized licensing configuration

        Raises:
            ValueError: If validation fails for any field
        """
        if licensing_config is None:
            return ValidatedLicensingConfig(
                isSet=False,
                mintingFee=0,
                licensingHook=ZERO_ADDRESS,
                hookData=ZERO_HASH,
                commercialRevShare=0,
                disabled=False,
                expectMinimumGroupRewardShare=0,
                expectGroupRewardPool=ZERO_ADDRESS,
            )

        if licensing_config["minting_fee"] < 0:
            raise ValueError("The minting fee must be greater than 0.")
        if licensing_config["licensing_hook"] != ZERO_ADDRESS:
            if not module_registry_client.isRegistered(
                licensing_config["licensing_hook"]
            ):
                raise ValueError("The licensing hook is not registered.")

        return ValidatedLicensingConfig(
            isSet=licensing_config["is_set"],
            mintingFee=licensing_config["minting_fee"],
            licensingHook=validate_address(licensing_config["licensing_hook"]),
            hookData=licensing_config["hook_data"],
            commercialRevShare=get_revenue_share(
                licensing_config["commercial_rev_share"]
            ),
            disabled=licensing_config["disabled"],
            expectMinimumGroupRewardShare=get_revenue_share(
                licensing_config["expect_minimum_group_reward_share"],
                RevShareType.EXPECT_MINIMUM_GROUP_REWARD_SHARE,
            ),
            expectGroupRewardPool=validate_address(
                licensing_config["expect_group_reward_pool"]
            ),
        )
