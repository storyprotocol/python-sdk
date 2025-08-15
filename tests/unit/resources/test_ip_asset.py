from unittest.mock import patch

import pytest

from story_protocol_python_sdk.resources.IPAsset import IPAsset
from story_protocol_python_sdk.utils.constants import ZERO_HASH
from story_protocol_python_sdk.utils.derivative_data import DerivativeDataInput
from story_protocol_python_sdk.utils.ip_metadata import IPMetadata
from tests.unit.fixtures.data import (
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
            return_value={"ip_id": IP_ID, "token_id": 1},
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
            )
            assert result == {
                "tx_hash": TX_HASH.hex(),
                "ip_id": IP_ID,
                "license_terms_ids": [1, 2],
                "token_id": 1,
            }


class TestRegisterDerivative:
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
                print(call_args)
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
