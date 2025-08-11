from unittest.mock import patch

import pytest

from story_protocol_python_sdk.resources.IPAsset import IPAsset
from story_protocol_python_sdk.utils.constants import ZERO_HASH
from story_protocol_python_sdk.utils.derivative_data import DerivativeDataInput
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
            ip_asset, "_parse_tx_ip_registered_event", return_value={"ip_id": IP_ID}
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
