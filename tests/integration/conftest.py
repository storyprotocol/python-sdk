import pytest

from story_protocol_python_sdk.story_client import StoryClient
from tests.integration.config.test_config import account, account_2, web3
from tests.integration.config.utils import get_story_client


@pytest.fixture(scope="session")
def story_client() -> StoryClient:
    """Fixture to provide the main story client"""
    return get_story_client(web3, account)


@pytest.fixture(scope="session")
def story_client_2() -> StoryClient:
    """Fixture to provide the secondary story client"""
    return get_story_client(web3, account_2)
