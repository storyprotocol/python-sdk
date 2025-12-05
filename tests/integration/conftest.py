import pytest

from story_protocol_python_sdk.story_client import StoryClient
from tests.integration.config.test_config import account, account_2, private_key, web3
from tests.integration.config.utils import get_story_client


@pytest.fixture(scope="session")
def story_client() -> StoryClient:
    """Fixture to provide the main story client"""
    return get_story_client(web3, account)


@pytest.fixture(scope="session")
def story_client_2() -> StoryClient:
    """Fixture to provide the secondary story client"""
    if not private_key:
        raise ValueError("Private key is not set")

    story_client_2 = get_story_client(web3, account_2)
    balance = story_client_2.get_wallet_balance()
    if balance < web3.to_wei(5, "ether"):
        tx = {
            "from": account.address,
            "to": account_2.address,
            "value": web3.to_wei(5, "ether"),
            "nonce": web3.eth.get_transaction_count(account.address),
            "gas": 21000,
            "gasPrice": web3.eth.gas_price,
            "chainId": web3.eth.chain_id,
        }
        signed_tx = account.sign_transaction(tx)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        web3.eth.wait_for_transaction_receipt(tx_hash)
    return story_client_2


@pytest.fixture(scope="module")
def nft_collection(story_client: StoryClient):
    tx_data = story_client.NFTClient.create_nft_collection(
        name="test-collection",
        symbol="TEST",
        max_supply=100,
        is_public_minting=True,
        mint_open=True,
        contract_uri="test-uri",
        mint_fee_recipient=account.address,
    )
    return tx_data["nft_contract"]
