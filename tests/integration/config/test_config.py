import os

from dotenv import load_dotenv
from web3 import Web3

# Load environment variables
load_dotenv(override=True)
private_key = os.getenv("WALLET_PRIVATE_KEY")
private_key_2 = os.getenv("WALLET_PRIVATE_KEY_2")
rpc_url = os.getenv("RPC_PROVIDER_URL")
wallet_address = os.getenv("WALLET_ADDRESS")
wallet_address_2 = os.getenv("WALLET_ADDRESS_2")

if not private_key:
    raise ValueError("WALLET_PRIVATE_KEY environment variable is not set")
if not rpc_url:
    raise ValueError("RPC_PROVIDER_URL environment variable is not set")

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(rpc_url))
if not web3.is_connected():
    raise Exception("Failed to connect to Web3 provider")

# Set up the account with the private key
account = web3.eth.account.from_key(private_key)
account_2 = web3.eth.account.from_key(private_key_2)

# Export all configuration
__all__ = [
    "web3",
    "account",
    "account_2",
    "wallet_address",
    "wallet_address_2",
    "private_key",
    "private_key_2",
]
