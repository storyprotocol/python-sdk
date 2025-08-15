from unittest.mock import patch

import pytest
from ens.ens import HexStr

from story_protocol_python_sdk.resources.IPAsset import IPAsset
from story_protocol_python_sdk.utils.constants import ZERO_HASH
from story_protocol_python_sdk.utils.derivative_data import DerivativeDataInput
from story_protocol_python_sdk.utils.ip_metadata import IPMetadataInput
from tests.integration.config.utils import ZERO_ADDRESS
from tests.unit.fixtures.data import ADDRESS, CHAIN_ID, IP_ID, TX_HASH


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
