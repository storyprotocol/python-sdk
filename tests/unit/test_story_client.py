import pytest

from story_protocol_python_sdk.resources.IPAccount import IPAccount
from story_protocol_python_sdk.resources.IPAsset import IPAsset
from story_protocol_python_sdk.resources.License import License
from story_protocol_python_sdk.resources.Permission import Permission
from story_protocol_python_sdk.resources.Royalty import Royalty
from story_protocol_python_sdk.story_client import StoryClient
from tests.integration.config.test_config import account, web3
from tests.unit.fixtures.data import CHAIN_ID


@pytest.fixture
def story_client():
    return StoryClient(web3, account, CHAIN_ID)


def test_story_client_constructor(story_client):
    assert story_client is not None
    assert isinstance(story_client, StoryClient)


def test_story_client_transport_error():
    with pytest.raises(ValueError):
        StoryClient(None, account, chain_id=CHAIN_ID)


def test_story_client_account_missing():
    with pytest.raises(ValueError):
        StoryClient(web3, None, chain_id=CHAIN_ID)


def test_story_client_wallet_initialization():
    client = StoryClient(web3, account, chain_id=CHAIN_ID)
    assert client is not None
    assert isinstance(client, StoryClient)


def test_ip_asset_client_getter(story_client):
    ip_asset = story_client.IPAsset
    assert ip_asset is not None
    assert isinstance(ip_asset, IPAsset)


def test_license_client_getter(story_client):
    license = story_client.License
    assert license is not None
    assert isinstance(license, License)


def test_royalty_client_getter(story_client):
    royalty = story_client.Royalty
    assert royalty is not None
    assert isinstance(royalty, Royalty)


def test_ip_account_client_getter(story_client):
    ip_account = story_client.IPAccount
    assert ip_account is not None
    assert isinstance(ip_account, IPAccount)


def test_permission_getter(story_client):
    permission = story_client.Permission
    assert permission is not None
    assert isinstance(permission, Permission)
