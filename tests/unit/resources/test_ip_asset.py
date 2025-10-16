from unittest.mock import patch

import pytest
from ens.ens import HexStr

from story_protocol_python_sdk.abi.IPAccountImpl.IPAccountImpl_client import (
    IPAccountImplClient,
)
from story_protocol_python_sdk.resources.IPAsset import IPAsset
from story_protocol_python_sdk.utils.constants import ZERO_HASH
from story_protocol_python_sdk.utils.derivative_data import DerivativeDataInput
from story_protocol_python_sdk.utils.ip_metadata import IPMetadata, IPMetadataInput
from story_protocol_python_sdk.utils.royalty_shares import (
    RoyaltyShare,
    RoyaltyShareInput,
)
from tests.integration.config.utils import ZERO_ADDRESS
from tests.unit.fixtures.data import (
    ACCOUNT_ADDRESS,
    ADDRESS,
    CHAIN_ID,
    IP_ID,
    LICENSE_TERMS,
    LICENSING_CONFIG,
    TX_HASH,
)


@pytest.fixture(scope="class")
def ip_asset(mock_web3, mock_account):
    return IPAsset(mock_web3, mock_account, CHAIN_ID)


@pytest.fixture(scope="class")
def mock_get_ip_id(ip_asset):
    def _mock():
        return patch.object(
            ip_asset.ip_asset_registry_client, "ipId", return_value=IP_ID
        )

    return _mock


@pytest.fixture(scope="class")
def mock_is_registered(ip_asset):
    def _mock(is_registered: bool = False):
        return patch.object(
            ip_asset.ip_asset_registry_client,
            "isRegistered",
            return_value=is_registered,
        )

    return _mock


@pytest.fixture(scope="class")
def mock_parse_ip_registered_event(ip_asset):
    def _mock():
        return patch.object(
            ip_asset,
            "_parse_tx_ip_registered_event",
            return_value={"ip_id": IP_ID, "token_id": 3},
        )

    return _mock


@pytest.fixture(scope="class")
def mock_get_function_signature():
    def _mock():
        return patch(
            "story_protocol_python_sdk.resources.IPAsset.get_function_signature",
            return_value="setAll(address,string,bytes32,bytes32)",
        )

    return _mock


@pytest.fixture(scope="class")
def mock_parse_tx_license_terms_attached_event(ip_asset):
    def _mock():
        return patch.object(
            ip_asset,
            "_parse_tx_license_terms_attached_event",
            return_value=[1, 2],
        )

    return _mock


@pytest.fixture
def mock_ip_account_impl_client(ip_asset):
    def _mock():
        return patch.object(
            IPAccountImplClient,
            "state",
            return_value=ip_asset.web3.to_bytes(),
        )

    return _mock


@pytest.fixture
def mock_get_royalty_vault_address_by_ip_id(ip_asset):
    def _mock():
        return patch.object(
            ip_asset,
            "get_royalty_vault_address_by_ip_id",
            return_value=ADDRESS,
        )

    return _mock


class TestIPAssetRegister:
    def test_register_invalid_deadline_type(
        self, ip_asset, mock_get_ip_id, mock_is_registered
    ):
        with mock_get_ip_id(), mock_is_registered():
            with pytest.raises(ValueError, match="Invalid deadline value."):
                ip_asset.register(
                    nft_contract=ADDRESS,
                    token_id=3,
                    deadline="error",
                    ip_metadata={"ip_metadata_uri": "1", "ip_metadata_hash": ZERO_HASH},
                )

    def test_register_already_registered(
        self, ip_asset, mock_get_ip_id, mock_is_registered
    ):
        with mock_get_ip_id(), mock_is_registered(True):
            response = ip_asset.register(ADDRESS, 3)
            assert response["ip_id"] == IP_ID
            assert response["tx_hash"] is None

    def test_register_successful(
        self,
        ip_asset,
        mock_get_ip_id,
        mock_is_registered,
        mock_parse_ip_registered_event,
    ):
        with mock_get_ip_id(), mock_is_registered(), mock_parse_ip_registered_event():

            result = ip_asset.register(ADDRESS, 3)
            assert result["tx_hash"] == TX_HASH.hex()
            assert result["ip_id"] == IP_ID

    def test_register_with_metadata(
        self,
        ip_asset: IPAsset,
        mock_get_ip_id,
        mock_is_registered,
        mock_parse_ip_registered_event,
        mock_signature_related_methods,
    ):

        with mock_get_ip_id(), mock_is_registered(), mock_parse_ip_registered_event():
            with mock_signature_related_methods():
                result = ip_asset.register(
                    nft_contract=ADDRESS,
                    token_id=3,
                    ip_metadata={
                        "ip_metadata_uri": "",
                        "ip_metadata_hash": ZERO_HASH,
                        "nft_metadata_uri": "",
                        "nft_metadata_hash": ZERO_HASH,
                    },
                    deadline=1000,
                )

                assert result["tx_hash"] == TX_HASH.hex()
                assert result["ip_id"] == IP_ID


class TestRegisterDerivativeIp:
    def test_ip_is_already_registered(
        self, ip_asset, mock_get_ip_id, mock_is_registered
    ):
        with mock_get_ip_id(), mock_is_registered(True):
            with pytest.raises(
                ValueError, match="The NFT with id 3 is already registered as IP."
            ):
                ip_asset.register_derivative_ip(
                    nft_contract=ADDRESS,
                    token_id=3,
                    deriv_data={
                        "max_minting_fee": 1000000000000000000,
                        "max_rts": 1000000000000000000,
                        "max_revenue_share": 1000000000000000000,
                    },
                )

    def test_parent_ip_id_is_empty(self, ip_asset, mock_get_ip_id, mock_is_registered):
        with mock_get_ip_id(), mock_is_registered():
            with pytest.raises(ValueError, match="The parent IP IDs must be provided."):
                ip_asset.register_derivative_ip(
                    nft_contract=ADDRESS,
                    token_id=3,
                    deriv_data=DerivativeDataInput(
                        parent_ip_ids=[],
                        license_terms_ids=[],
                    ),
                )

    def test_success(
        self,
        ip_asset,
        mock_get_ip_id,
        mock_is_registered,
        mock_parse_ip_registered_event,
        mock_signature_related_methods,
        mock_get_function_signature,
        mock_license_registry_client,
    ):
        with mock_get_ip_id(), mock_is_registered(), mock_parse_ip_registered_event(), mock_get_function_signature(), mock_license_registry_client():
            with mock_signature_related_methods():
                result = ip_asset.register_derivative_ip(
                    nft_contract=ADDRESS,
                    token_id=3,
                    deriv_data=DerivativeDataInput(
                        parent_ip_ids=[IP_ID, IP_ID],
                        license_terms_ids=[1, 2],
                        max_minting_fee=10,
                        max_rts=100,
                        max_revenue_share=100,
                    ),
                )
                assert result["tx_hash"] == TX_HASH.hex()
                assert result["ip_id"] == IP_ID


class TestMint:
    def test_mint_successful(self, ip_asset):
        result = ip_asset.mint(
            nft_contract=ADDRESS,
            to_address=ADDRESS,
            metadata_uri="",
            metadata_hash=ZERO_HASH,
        )
        assert result == f"0x{TX_HASH.hex()}"

    def test_mint_failed_transaction(self, ip_asset):
        with patch.object(ip_asset.web3.eth, "send_raw_transaction") as mock_send:
            mock_send.side_effect = Exception("Transaction failed")
            with pytest.raises(Exception, match="Transaction failed"):
                ip_asset.mint(
                    nft_contract=ADDRESS,
                    to_address=ADDRESS,
                    metadata_uri="",
                    metadata_hash=ZERO_HASH,
                    allow_duplicates=False,
                )


class TestRegisterIpAndAttachPilTerms:
    def test_token_id_is_already_registered(
        self, ip_asset, mock_get_ip_id, mock_is_registered
    ):
        with mock_get_ip_id(), mock_is_registered(True):
            with pytest.raises(
                ValueError, match="The NFT with id 3 is already registered as IP."
            ):
                ip_asset.register_ip_and_attach_pil_terms(
                    nft_contract=ADDRESS,
                    token_id=3,
                    license_terms_data=[],
                )

    def test_royalty_policy_commercial_rev_share_is_less_than_0(
        self, ip_asset, mock_get_ip_id, mock_is_registered
    ):
        with mock_get_ip_id(), mock_is_registered():
            with pytest.raises(
                ValueError, match="commercial_rev_share should be between 0 and 100."
            ):
                ip_asset.register_ip_and_attach_pil_terms(
                    nft_contract=ADDRESS,
                    token_id=3,
                    license_terms_data=[
                        {
                            "terms": {
                                **LICENSE_TERMS,
                                "commercial_rev_share": -1,
                            },
                        }
                    ],
                )

    def test_transaction_to_be_called_with_correct_parameters(
        self,
        ip_asset: IPAsset,
        mock_get_ip_id,
        mock_is_registered,
        mock_parse_ip_registered_event,
        mock_parse_tx_license_terms_attached_event,
        mock_signature_related_methods,
    ):
        with mock_get_ip_id(), mock_is_registered(), mock_parse_ip_registered_event(), mock_parse_tx_license_terms_attached_event(), mock_signature_related_methods():
            with patch.object(
                ip_asset.license_attachment_workflows_client,
                "build_registerIpAndAttachPILTerms_transaction",
            ) as mock_build_registerIpAndAttachPILTerms_transaction:

                ip_asset.register_ip_and_attach_pil_terms(
                    nft_contract=ADDRESS,
                    token_id=3,
                    license_terms_data=[
                        {
                            "terms": LICENSE_TERMS,
                            "licensing_config": LICENSING_CONFIG,
                        }
                    ],
                )
            call_args = mock_build_registerIpAndAttachPILTerms_transaction.call_args[0]
            assert call_args[0] == ADDRESS
            assert call_args[1] == 3
            assert call_args[2] == IPMetadata.from_input().get_validated_data()
            assert call_args[3] == [
                {
                    "terms": {
                        "transferable": True,
                        "royaltyPolicy": "0x1234567890123456789012345678901234567890",
                        "defaultMintingFee": 10,
                        "expiration": 100,
                        "commercialUse": True,
                        "commercialAttribution": True,
                        "commercializerChecker": True,
                        "commercializerCheckerData": b"mock_bytes",
                        "commercialRevShare": 19000000,
                        "commercialRevCeiling": 0,
                        "derivativesAllowed": True,
                        "derivativesAttribution": True,
                        "derivativesApproval": True,
                        "derivativesReciprocal": True,
                        "derivativeRevCeiling": 100,
                        "currency": "0x1234567890123456789012345678901234567890",
                        "uri": "https://example.com",
                    },
                    "licensingConfig": {
                        "isSet": True,
                        "mintingFee": 10,
                        "hookData": b"mock_bytes",
                        "licensingHook": "0x1234567890123456789012345678901234567890",
                        "commercialRevShare": 10000000,
                        "disabled": False,
                        "expectMinimumGroupRewardShare": 10000000,
                        "expectGroupRewardPool": "0x1234567890123456789012345678901234567890",
                    },
                }
            ]

    def test_success(
        self,
        ip_asset: IPAsset,
        mock_get_ip_id,
        mock_is_registered,
        mock_parse_ip_registered_event,
        mock_signature_related_methods,
        mock_parse_tx_license_terms_attached_event,
    ):
        with mock_get_ip_id(), mock_is_registered(), mock_parse_ip_registered_event(), mock_parse_tx_license_terms_attached_event(), mock_signature_related_methods():
            result = ip_asset.register_ip_and_attach_pil_terms(
                nft_contract=ADDRESS,
                token_id=3,
                license_terms_data=[
                    {
                        "terms": LICENSE_TERMS,
                        "licensing_config": LICENSING_CONFIG,
                    }
                ],
                ip_metadata={
                    "ip_metadata_uri": "https://example.com/metadata/custom-value.json",
                    "ip_metadata_hash": "ip_metadata_hash",
                    "nft_metadata_uri": "https://example.com/metadata/custom-value.json",
                    "nft_metadata_hash": "nft_metadata_hash",
                },
            )
            assert result == {
                "tx_hash": TX_HASH.hex(),
                "ip_id": IP_ID,
                "license_terms_ids": [1, 2],
                "token_id": 3,
            }


class TestRegisterDerivative:
    def test_child_ip_is_not_registered(
        self, ip_asset: IPAsset, mock_get_ip_id, mock_is_registered
    ):
        with mock_get_ip_id(), mock_is_registered(False):
            with pytest.raises(
                ValueError,
                match=f"Failed to register derivative: The child IP with id {IP_ID} is not registered",
            ):
                ip_asset.register_derivative(
                    child_ip_id=IP_ID,
                    parent_ip_ids=[IP_ID, IP_ID],
                    license_terms_ids=[1, 2],
                )

    def test_default_value_when_not_provided(
        self,
        ip_asset: IPAsset,
        mock_get_ip_id,
        mock_is_registered,
        mock_parse_ip_registered_event,
        mock_license_registry_client,
    ):
        with mock_get_ip_id(), mock_is_registered(
            True
        ), mock_parse_ip_registered_event(), mock_license_registry_client():
            with patch.object(
                ip_asset.licensing_module_client,
                "build_registerDerivative_transaction",
            ) as mock_build_registerDerivative_transaction:

                ip_asset.register_derivative(
                    child_ip_id=IP_ID,
                    parent_ip_ids=[IP_ID, IP_ID],
                    license_terms_ids=[1, 2],
                )
                call_args = mock_build_registerDerivative_transaction.call_args[0]
                assert (
                    call_args[3] == "0x1234567890123456789012345678901234567890"
                )  # license_template
                assert (
                    call_args[4] == "0x0000000000000000000000000000000000000000"
                )  # royalty_context
                assert call_args[5] == 0  # max_minting_fee
                assert call_args[6] == 100000000  # max_rts
                assert call_args[7] == 100 * 10**6  # max_revenue_share

    def test_call_value_when_provided(
        self,
        ip_asset: IPAsset,
        mock_get_ip_id,
        mock_is_registered,
        mock_parse_ip_registered_event,
        mock_license_registry_client,
    ):
        with mock_get_ip_id(), mock_is_registered(
            True
        ), mock_parse_ip_registered_event(), mock_license_registry_client():
            with patch.object(
                ip_asset.licensing_module_client,
                "build_registerDerivative_transaction",
            ) as mock_build_registerDerivative_transaction:
                ip_asset.register_derivative(
                    child_ip_id=IP_ID,
                    parent_ip_ids=[IP_ID, IP_ID],
                    license_terms_ids=[1, 2],
                    max_revenue_share=10,
                    max_minting_fee=10,
                    max_rts=100,
                    license_template=ADDRESS,
                )
                call_args = mock_build_registerDerivative_transaction.call_args[0]
                assert call_args[7] == 10 * 10**6  # max_revenue_share
                assert call_args[5] == 10  # max_minting_fee
                assert call_args[6] == 100  # max_rts
                assert call_args[3] == ADDRESS  # license_template


class TestMintAndRegisterIpAndMakeDerivative:
    def test_throw_error_when_spg_nft_contract_is_invalid(
        self, ip_asset, mock_license_registry_client
    ):
        with mock_license_registry_client():
            with pytest.raises(ValueError, match="Invalid address: invalid."):
                ip_asset.mint_and_register_ip_and_make_derivative(
                    spg_nft_contract="invalid",
                    deriv_data=DerivativeDataInput(
                        parent_ip_ids=[IP_ID, IP_ID],
                        license_terms_ids=[1, 2],
                    ),
                )

    def test_success_and_expect_value_when_default_values_not_provided(
        self,
        ip_asset: IPAsset,
        mock_license_registry_client,
        mock_parse_ip_registered_event,
    ):
        with mock_parse_ip_registered_event(), mock_license_registry_client():
            with patch.object(
                ip_asset.derivative_workflows_client,
                "build_mintAndRegisterIpAndMakeDerivative_transaction",
                return_value={"tx_hash": TX_HASH.hex()},
            ) as mock_build_transaction:
                result = ip_asset.mint_and_register_ip_and_make_derivative(
                    spg_nft_contract=ADDRESS,
                    deriv_data=DerivativeDataInput(
                        parent_ip_ids=[IP_ID, IP_ID],
                        license_terms_ids=[1, 2],
                    ),
                )
            assert result["tx_hash"] == TX_HASH.hex()
            assert result["ip_id"] == IP_ID
            assert result["token_id"] == 3
            assert mock_build_transaction.call_args[0][1] == {
                "parentIpIds": [IP_ID, IP_ID],
                "licenseTermsIds": [1, 2],
                "maxMintingFee": 0,
                "maxRts": 100 * 10**6,
                "maxRevenueShare": 100 * 10**6,
                "royaltyContext": ZERO_ADDRESS,
                "licenseTemplate": "0x1234567890123456789012345678901234567890",
            }
            assert mock_build_transaction.call_args[0][2] == {
                "ipMetadataURI": "",
                "ipMetadataHash": ZERO_HASH,
                "nftMetadataURI": "",
                "nftMetadataHash": ZERO_HASH,
            }
            assert (
                mock_build_transaction.call_args[0][3]
                == "0xF60cBF0Ea1A61567F1dDaf79A6219D20d189155c"
            )  # recipient
            assert mock_build_transaction.call_args[0][4]  # allowDuplicates

    def test_with_custom_value(
        self,
        ip_asset: IPAsset,
        mock_license_registry_client,
        mock_parse_ip_registered_event,
    ):
        with mock_parse_ip_registered_event(), mock_license_registry_client():
            with patch.object(
                ip_asset.derivative_workflows_client,
                "build_mintAndRegisterIpAndMakeDerivative_transaction",
                return_value={"tx_hash": TX_HASH.hex()},
            ) as mock_build_transaction:
                result = ip_asset.mint_and_register_ip_and_make_derivative(
                    spg_nft_contract=ADDRESS,
                    deriv_data=DerivativeDataInput(
                        parent_ip_ids=[IP_ID, IP_ID],
                        license_terms_ids=[1, 2],
                        max_minting_fee=10,
                        max_rts=100,
                        max_revenue_share=10,
                        license_template=ADDRESS,
                    ),
                    ip_metadata=IPMetadataInput(
                        ip_metadata_uri="https://example.com/metadata/custom-value.json",
                        ip_metadata_hash=HexStr("ip_metadata_hash"),
                        nft_metadata_uri="https://example.com/metadata/custom-value.json",
                        nft_metadata_hash=HexStr("nft_metadata_hash"),
                    ),
                    recipient=ADDRESS,
                    allow_duplicates=False,
                )
            assert result["tx_hash"] == TX_HASH.hex()
            assert result["ip_id"] == IP_ID
            assert result["token_id"] == 3

            assert mock_build_transaction.call_args[0][1] == {
                "parentIpIds": [IP_ID, IP_ID],
                "licenseTermsIds": [1, 2],
                "maxMintingFee": 10,
                "maxRts": 100,
                "maxRevenueShare": 10 * 10**6,
                "royaltyContext": ZERO_ADDRESS,
                "licenseTemplate": ADDRESS,
            }
            assert mock_build_transaction.call_args[0][2] == {
                "ipMetadataURI": "https://example.com/metadata/custom-value.json",
                "ipMetadataHash": "ip_metadata_hash",
                "nftMetadataURI": "https://example.com/metadata/custom-value.json",
                "nftMetadataHash": "nft_metadata_hash",
            }
            assert mock_build_transaction.call_args[0][3] == ADDRESS  # recipient
            assert not mock_build_transaction.call_args[0][4]  # allowDuplicates


@pytest.fixture(scope="class")
def mock_owner_of(ip_asset: IPAsset):
    def _mock(owner: str = ACCOUNT_ADDRESS):
        return patch.object(
            ip_asset.license_token_client, "ownerOf", return_value=owner
        )

    return _mock


class TestRegisterIpAndMakeDerivativeWithLicenseTokens:
    def test_nft_already_registered(
        self, ip_asset: IPAsset, mock_get_ip_id, mock_is_registered
    ):
        """Test error when NFT is already registered as IP."""
        with mock_get_ip_id(), mock_is_registered(True):
            with pytest.raises(
                ValueError, match="The NFT with id 3 is already registered as IP."
            ):
                ip_asset.register_ip_and_make_derivative_with_license_tokens(
                    nft_contract=ADDRESS,
                    token_id=3,
                    license_token_ids=[1, 2, 3],
                )

    def test_empty_license_token_ids(
        self, ip_asset: IPAsset, mock_get_ip_id, mock_is_registered
    ):
        """Test error when license token IDs list is empty."""
        with mock_get_ip_id(), mock_is_registered(False):
            with pytest.raises(ValueError, match="License token IDs must be provided."):
                ip_asset.register_ip_and_make_derivative_with_license_tokens(
                    nft_contract=ADDRESS,
                    token_id=3,
                    license_token_ids=[],
                )

    def test_license_token_not_owned_by_caller(
        self, ip_asset: IPAsset, mock_get_ip_id, mock_is_registered, mock_owner_of
    ):
        """Test error when license token is not owned by caller."""
        with mock_get_ip_id(), mock_is_registered(False), mock_owner_of(
            "0x1234567890123456789012345678901234567890"
        ):
            with pytest.raises(
                ValueError, match="License token id 1 must be owned by the caller."
            ):
                ip_asset.register_ip_and_make_derivative_with_license_tokens(
                    nft_contract=ADDRESS,
                    token_id=3,
                    license_token_ids=[1, 2, 3],
                )

    def test_invalid_max_rts(
        self, ip_asset: IPAsset, mock_get_ip_id, mock_is_registered, mock_owner_of
    ):
        """Test error when max_rts is invalid."""
        with mock_get_ip_id(), mock_is_registered(False), mock_owner_of():
            with pytest.raises(
                ValueError,
                match="The maxRts must be greater than 0 and less than 100,000,000.",
            ):
                ip_asset.register_ip_and_make_derivative_with_license_tokens(
                    nft_contract=ADDRESS,
                    token_id=3,
                    license_token_ids=[1, 2, 3],
                    max_rts=1000000000000000000,
                )

    def test_success_with_default_values(
        self,
        ip_asset: IPAsset,
        mock_get_ip_id,
        mock_is_registered,
        mock_owner_of,
        mock_parse_ip_registered_event,
        mock_signature_related_methods,
        mock_get_function_signature,
    ):
        """Test successful registration with default values."""
        with mock_get_ip_id(), mock_is_registered(
            False
        ), mock_owner_of(), mock_parse_ip_registered_event(), mock_signature_related_methods(), mock_get_function_signature():
            with patch.object(
                ip_asset.derivative_workflows_client,
                "build_registerIpAndMakeDerivativeWithLicenseTokens_transaction",
                return_value={"tx_hash": TX_HASH.hex()},
            ) as mock_build_transaction:
                result = ip_asset.register_ip_and_make_derivative_with_license_tokens(
                    nft_contract=ADDRESS,
                    token_id=3,
                    license_token_ids=[1, 2, 3],
                )

                # Verify the method was called with correct parameters
                call_args = mock_build_transaction.call_args[0]
                assert call_args[0] == ADDRESS  # nft_contract
                assert call_args[1] == 3  # token_id
                assert call_args[2] == [1, 2, 3]  # license_token_ids
                assert call_args[3] == ZERO_ADDRESS  # royaltyContext
                assert call_args[4] == 100_000_000  # max_rts (default)
                assert (
                    call_args[5] == IPMetadata.from_input().get_validated_data()
                )  # ip_metadata

                # Verify response
                assert result["tx_hash"] == TX_HASH.hex()
                assert result["ip_id"] == IP_ID
                assert result["token_id"] == 3

    def test_success_with_custom_values(
        self,
        ip_asset: IPAsset,
        mock_get_ip_id,
        mock_is_registered,
        mock_owner_of,
        mock_parse_ip_registered_event,
        mock_signature_related_methods,
        mock_get_function_signature,
    ):
        """Test successful registration with custom values."""
        with mock_get_ip_id(), mock_is_registered(
            False
        ), mock_owner_of(), mock_parse_ip_registered_event(), mock_signature_related_methods(), mock_get_function_signature():
            with patch.object(
                ip_asset.derivative_workflows_client,
                "build_registerIpAndMakeDerivativeWithLicenseTokens_transaction",
                return_value={"tx_hash": TX_HASH.hex()},
            ) as mock_build_transaction:
                result = ip_asset.register_ip_and_make_derivative_with_license_tokens(
                    nft_contract=ADDRESS,
                    token_id=3,
                    license_token_ids=[1, 2, 3],
                    max_rts=50_000_000,
                    deadline=2000,
                    ip_metadata=IPMetadataInput(
                        ip_metadata_uri="https://example.com/metadata.json",
                        ip_metadata_hash=HexStr("0x1234567890abcdef"),
                        nft_metadata_uri="https://example.com/nft.json",
                        nft_metadata_hash=HexStr("0xabcdef1234567890"),
                    ),
                )

                # Verify the method was called with correct parameters
                call_args = mock_build_transaction.call_args[0]
                assert call_args[0] == ADDRESS  # nft_contract
                assert call_args[1] == 3  # token_id
                assert call_args[2] == [1, 2, 3]  # license_token_ids
                assert call_args[3] == ZERO_ADDRESS  # royaltyContext
                assert call_args[4] == 50_000_000  # max_rts (custom)
                assert (
                    call_args[5]
                    == IPMetadata.from_input(
                        IPMetadataInput(
                            ip_metadata_uri="https://example.com/metadata.json",
                            ip_metadata_hash=HexStr("0x1234567890abcdef"),
                            nft_metadata_uri="https://example.com/nft.json",
                            nft_metadata_hash=HexStr("0xabcdef1234567890"),
                        )
                    ).get_validated_data()
                )  # ip_metadata

                # Verify metadata was processed correctly
                metadata = call_args[5]
                assert metadata["ipMetadataURI"] == "https://example.com/metadata.json"
                assert metadata["nftMetadataURI"] == "https://example.com/nft.json"

                # Verify signature data
                sig_data = call_args[6]
                assert "signer" in sig_data
                assert "deadline" in sig_data
                assert "signature" in sig_data

                # Verify response
                assert result["tx_hash"] == TX_HASH.hex()
                assert result["ip_id"] == IP_ID
                assert result["token_id"] == 3


class TestMintAndRegisterIpAndMakeDerivativeWithLicenseTokens:

    def test_throw_error_when_license_token_ids_is_not_owned_by_caller(
        self,
        ip_asset: IPAsset,
        mock_owner_of,
    ):
        with mock_owner_of("0x1234567890123456789012345678901234567890"):
            with pytest.raises(
                ValueError, match="License token id 1 must be owned by the caller."
            ):
                ip_asset.mint_and_register_ip_and_make_derivative_with_license_tokens(
                    spg_nft_contract=ADDRESS,
                    license_token_ids=[1, 2, 3],
                    max_rts=100,
                )

    def test_throw_error_when_max_rts_is_invalid(
        self,
        ip_asset: IPAsset,
        mock_owner_of,
    ):
        with mock_owner_of():
            with pytest.raises(
                ValueError,
                match="The maxRts must be greater than 0 and less than 100,000,000.",
            ):
                ip_asset.mint_and_register_ip_and_make_derivative_with_license_tokens(
                    spg_nft_contract=ADDRESS,
                    license_token_ids=[1, 2, 3],
                    max_rts=1000000000000000000,
                )

    def test_success_when_default_values_not_provided(
        self,
        ip_asset: IPAsset,
        mock_owner_of,
        mock_parse_ip_registered_event,
    ):
        with mock_owner_of():
            with patch.object(
                ip_asset.derivative_workflows_client,
                "build_mintAndRegisterIpAndMakeDerivativeWithLicenseTokens_transaction",
                return_value={"tx_hash": TX_HASH.hex()},
            ) as mock_build_transaction:
                with mock_parse_ip_registered_event():
                    result = ip_asset.mint_and_register_ip_and_make_derivative_with_license_tokens(
                        spg_nft_contract=ADDRESS,
                        license_token_ids=[1, 2],
                        max_rts=100,
                    )
            assert mock_build_transaction.call_args[0][:7] == (
                ADDRESS,
                [1, 2],
                ZERO_ADDRESS,
                100,
                IPMetadata.from_input().get_validated_data(),
                ACCOUNT_ADDRESS,
                True,
            )
            assert result["tx_hash"] == TX_HASH.hex()
            assert result["ip_id"] == IP_ID
            assert result["token_id"] == 3

    def test_with_custom_value(
        self,
        ip_asset: IPAsset,
        mock_owner_of,
        mock_parse_ip_registered_event,
    ):
        with mock_owner_of():
            with patch.object(
                ip_asset.derivative_workflows_client,
                "build_mintAndRegisterIpAndMakeDerivativeWithLicenseTokens_transaction",
                return_value={"tx_hash": TX_HASH.hex()},
            ) as mock_build_transaction:
                with mock_parse_ip_registered_event():
                    result = ip_asset.mint_and_register_ip_and_make_derivative_with_license_tokens(
                        spg_nft_contract=ADDRESS,
                        license_token_ids=[1, 2, 3],
                        max_rts=100,
                        ip_metadata=IPMetadataInput(
                            ip_metadata_uri="https://example.com/metadata/custom-value.json",
                            ip_metadata_hash=HexStr("ip_metadata_hash"),
                            nft_metadata_uri="https://example.com/metadata/custom-value.json",
                            nft_metadata_hash=HexStr("nft_metadata_hash"),
                        ),
                        recipient=ADDRESS,
                        allow_duplicates=False,
                    )
                    assert mock_build_transaction.call_args[0][:7] == (
                        ADDRESS,
                        [1, 2, 3],
                        ZERO_ADDRESS,
                        100,
                        IPMetadata.from_input(
                            IPMetadataInput(
                                ip_metadata_uri="https://example.com/metadata/custom-value.json",
                                ip_metadata_hash=HexStr("ip_metadata_hash"),
                                nft_metadata_uri="https://example.com/metadata/custom-value.json",
                                nft_metadata_hash=HexStr("nft_metadata_hash"),
                            ),
                        ).get_validated_data(),
                        ADDRESS,
                        False,
                    )
                    assert result["tx_hash"] == TX_HASH.hex()
                    assert result["ip_id"] == IP_ID
                    assert result["token_id"] == 3

    def test_throw_error_when_transaction_failed(
        self,
        ip_asset: IPAsset,
        mock_owner_of,
    ):
        with mock_owner_of():
            with patch.object(
                ip_asset.derivative_workflows_client,
                "build_mintAndRegisterIpAndMakeDerivativeWithLicenseTokens_transaction",
                side_effect=Exception("Transaction failed."),
            ):
                with pytest.raises(Exception, match="Transaction failed."):
                    ip_asset.mint_and_register_ip_and_make_derivative_with_license_tokens(
                        spg_nft_contract=ADDRESS,
                        license_token_ids=[1, 2, 3],
                        max_rts=100,
                    )


class TestRegisterPilTermsAndAttach:

    def test_throw_error_when_ip_is_not_registered(
        self,
        ip_asset: IPAsset,
        mock_is_registered,
    ):
        with mock_is_registered(False):
            with pytest.raises(
                ValueError,
                match=f"The IP with id {IP_ID} is not registered.",
            ):
                ip_asset.register_pil_terms_and_attach(
                    ip_id=IP_ID,
                    license_terms_data=[
                        {
                            "terms": LICENSE_TERMS,
                            "licensing_config": LICENSING_CONFIG,
                        },
                        {
                            "terms": {
                                **LICENSE_TERMS,
                                "commercial_rev_share": 10,
                            },
                            "licensing_config": {
                                **LICENSING_CONFIG,
                                "commercial_rev_share": 10,
                            },
                        },
                    ],
                )

    def test_successful_registration(
        self,
        ip_asset: IPAsset,
        mock_is_registered,
        mock_get_function_signature,
        mock_signature_related_methods,
        mock_parse_tx_license_terms_attached_event,
        mock_ip_account_impl_client,
    ):
        with mock_is_registered(
            True
        ), mock_get_function_signature(), mock_signature_related_methods(), mock_parse_tx_license_terms_attached_event(), mock_ip_account_impl_client():
            with patch.object(
                ip_asset.license_attachment_workflows_client,
                "build_registerPILTermsAndAttach_transaction",
                return_value={"tx_hash": TX_HASH.hex()},
            ) as mock_build_transaction:
                result = ip_asset.register_pil_terms_and_attach(
                    ip_id=IP_ID,
                    license_terms_data=[
                        {
                            "terms": LICENSE_TERMS,
                            "licensing_config": LICENSING_CONFIG,
                        },
                        {
                            "terms": LICENSE_TERMS,
                            "licensing_config": LICENSING_CONFIG,
                        },
                    ],
                )
            assert mock_build_transaction.call_args[0][1][0] == {
                "terms": {
                    "transferable": True,
                    "royaltyPolicy": "0x1234567890123456789012345678901234567890",
                    "defaultMintingFee": 10,
                    "expiration": 100,
                    "commercialUse": True,
                    "commercialAttribution": True,
                    "commercializerChecker": True,
                    "commercializerCheckerData": b"mock_bytes",
                    "commercialRevShare": 19000000,
                    "commercialRevCeiling": 0,
                    "derivativesAllowed": True,
                    "derivativesAttribution": True,
                    "derivativesApproval": True,
                    "derivativesReciprocal": True,
                    "derivativeRevCeiling": 100,
                    "currency": "0x1234567890123456789012345678901234567890",
                    "uri": "https://example.com",
                },
                "licensingConfig": {
                    "isSet": True,
                    "mintingFee": 10,
                    "hookData": b"mock_bytes",
                    "licensingHook": "0x1234567890123456789012345678901234567890",
                    "commercialRevShare": 10000000,
                    "disabled": False,
                    "expectMinimumGroupRewardShare": 10000000,
                    "expectGroupRewardPool": "0x1234567890123456789012345678901234567890",
                },
            }
            assert result["tx_hash"] == TX_HASH.hex()
            assert result["license_terms_ids"] == [1, 2]

    def test_registration_with_transaction_failed(
        self,
        ip_asset: IPAsset,
        mock_is_registered,
        mock_get_function_signature,
        mock_signature_related_methods,
        mock_parse_tx_license_terms_attached_event,
        mock_ip_account_impl_client,
    ):
        with mock_is_registered(
            True
        ), mock_get_function_signature(), mock_signature_related_methods(), mock_parse_tx_license_terms_attached_event(), mock_ip_account_impl_client():
            with patch.object(
                ip_asset.license_attachment_workflows_client,
                "build_registerPILTermsAndAttach_transaction",
                side_effect=Exception("Transaction failed."),
            ):
                with pytest.raises(Exception, match="Transaction failed."):
                    ip_asset.register_pil_terms_and_attach(
                        ip_id=IP_ID,
                        license_terms_data=[
                            {
                                "terms": LICENSE_TERMS,
                                "licensing_config": LICENSING_CONFIG,
                            },
                        ],
                    )


class TestMintAndRegisterIpAndMakeDerivativeAndDistributeRoyaltyTokens:
    def test_throw_error_when_royalty_shares_empty(self, ip_asset: IPAsset):
        with pytest.raises(ValueError, match="Royalty shares must be provided."):
            ip_asset.mint_and_register_ip_and_make_derivative_and_distribute_royalty_tokens(
                spg_nft_contract=ADDRESS,
                deriv_data=DerivativeDataInput(
                    parent_ip_ids=[IP_ID],
                    license_terms_ids=[1],
                ),
                royalty_shares=[],
            )

    def test_throw_error_when_deriv_data_is_invalid(self, ip_asset: IPAsset):
        with pytest.raises(ValueError, match="The parent IP IDs must be provided."):
            ip_asset.mint_and_register_ip_and_make_derivative_and_distribute_royalty_tokens(
                spg_nft_contract=ADDRESS,
                deriv_data=DerivativeDataInput(
                    parent_ip_ids=[],
                    license_terms_ids=[1],
                ),
                royalty_shares=[
                    RoyaltyShareInput(recipient=ACCOUNT_ADDRESS, percentage=50.0)
                ],
            )

    def test_success_with_default_values(
        self,
        ip_asset: IPAsset,
        mock_license_registry_client,
        mock_parse_ip_registered_event,
        mock_get_royalty_vault_address_by_ip_id,
    ):
        royalty_shares = [
            RoyaltyShareInput(recipient=ACCOUNT_ADDRESS, percentage=50.0),
            RoyaltyShareInput(recipient=ADDRESS, percentage=30.0),
        ]

        with mock_parse_ip_registered_event(), mock_license_registry_client(), mock_get_royalty_vault_address_by_ip_id():
            with patch.object(
                ip_asset.royalty_token_distribution_workflows_client,
                "build_mintAndRegisterIpAndMakeDerivativeAndDistributeRoyaltyTokens_transaction",
                return_value={"tx_hash": TX_HASH.hex()},
            ) as mock_build_transaction:
                result = ip_asset.mint_and_register_ip_and_make_derivative_and_distribute_royalty_tokens(
                    spg_nft_contract=ADDRESS,
                    deriv_data=DerivativeDataInput(
                        parent_ip_ids=[IP_ID, IP_ID],
                        license_terms_ids=[1, 2],
                    ),
                    royalty_shares=royalty_shares,
                )
            called_args = mock_build_transaction.call_args[0]
            assert called_args[2] == IPMetadata.from_input().get_validated_data()
            assert (
                called_args[4]
                == RoyaltyShare.get_royalty_shares(royalty_shares)["royalty_shares"]
            )
            assert called_args[5] is True

            assert result["tx_hash"] == TX_HASH.hex()
            assert result["ip_id"] == IP_ID
            assert result["token_id"] == 3
            assert result["royalty_vault"] == ADDRESS

    def test_royalty_vault_address(
        self,
        ip_asset: IPAsset,
        mock_license_registry_client,
        mock_parse_ip_registered_event,
        mock_get_royalty_vault_address_by_ip_id,
    ):
        royalty_shares = [
            RoyaltyShareInput(recipient=ACCOUNT_ADDRESS, percentage=50.0),
            RoyaltyShareInput(recipient=ADDRESS, percentage=30.0),
        ]

        with mock_parse_ip_registered_event(), mock_license_registry_client(), mock_get_royalty_vault_address_by_ip_id():
            with patch(
                "story_protocol_python_sdk.resources.IPAsset.build_and_send_transaction",
                return_value={
                    "tx_hash": TX_HASH,
                    "tx_receipt": {
                        "logs": [
                            {
                                "topics": [
                                    ip_asset.web3.keccak(
                                        text="IpRoyaltyVaultDeployed(address,address)"
                                    )
                                ],
                                "data": IP_ID + ADDRESS,
                            }
                        ]
                    },
                },
            ):
                result = ip_asset.mint_and_register_ip_and_make_derivative_and_distribute_royalty_tokens(
                    spg_nft_contract=ADDRESS,
                    deriv_data=DerivativeDataInput(
                        parent_ip_ids=[IP_ID, IP_ID],
                        license_terms_ids=[1, 2],
                    ),
                    royalty_shares=royalty_shares,
                )
            assert result["royalty_vault"] == ADDRESS

    def test_success_with_custom_values(
        self,
        ip_asset: IPAsset,
        mock_license_registry_client,
        mock_parse_ip_registered_event,
        mock_get_royalty_vault_address_by_ip_id,
    ):
        royalty_shares = [
            RoyaltyShareInput(recipient=ACCOUNT_ADDRESS, percentage=60.0),
        ]
        ip_metadata = IPMetadataInput(
            ip_metadata_uri="https://example.com/ip-metadata",
            ip_metadata_hash="0x1234567890abcdef",
            nft_metadata_uri="https://example.com/nft-metadata",
            nft_metadata_hash="0xabcdef1234567890",
        )
        with mock_parse_ip_registered_event(), mock_license_registry_client(), mock_get_royalty_vault_address_by_ip_id():
            with patch.object(
                ip_asset.royalty_token_distribution_workflows_client,
                "build_mintAndRegisterIpAndMakeDerivativeAndDistributeRoyaltyTokens_transaction",
                return_value={"tx_hash": TX_HASH.hex()},
            ) as mock_build_transaction:

                result = ip_asset.mint_and_register_ip_and_make_derivative_and_distribute_royalty_tokens(
                    spg_nft_contract=ADDRESS,
                    deriv_data=DerivativeDataInput(
                        parent_ip_ids=[IP_ID],
                        license_terms_ids=[1],
                        max_minting_fee=10000,
                        max_rts=10,
                        max_revenue_share=100,
                    ),
                    royalty_shares=royalty_shares,
                    ip_metadata=ip_metadata,
                    recipient=ACCOUNT_ADDRESS,
                    allow_duplicates=False,
                )

            called_args = mock_build_transaction.call_args[0]
            assert (
                called_args[2]
                == IPMetadata.from_input(ip_metadata).get_validated_data()
            )
            assert (
                called_args[4]
                == RoyaltyShare.get_royalty_shares(royalty_shares)["royalty_shares"]
            )
            assert called_args[5] is False

            assert result["tx_hash"] == TX_HASH.hex()
            assert result["ip_id"] == IP_ID
            assert result["token_id"] == 3
            assert result["royalty_vault"] == ADDRESS

    def test_throw_error_when_transaction_failed(
        self,
        ip_asset: IPAsset,
        mock_license_registry_client,
        mock_parse_ip_registered_event,
    ):
        with mock_parse_ip_registered_event(), mock_license_registry_client():
            with patch.object(
                ip_asset.royalty_token_distribution_workflows_client,
                "build_mintAndRegisterIpAndMakeDerivativeAndDistributeRoyaltyTokens_transaction",
                side_effect=Exception("Transaction failed."),
            ):
                with pytest.raises(Exception, match="Transaction failed."):
                    ip_asset.mint_and_register_ip_and_make_derivative_and_distribute_royalty_tokens(
                        spg_nft_contract=ADDRESS,
                        deriv_data=DerivativeDataInput(
                            parent_ip_ids=[IP_ID],
                            license_terms_ids=[1],
                        ),
                        royalty_shares=[
                            RoyaltyShareInput(
                                recipient=ACCOUNT_ADDRESS, percentage=50.0
                            )
                        ],
                    )
