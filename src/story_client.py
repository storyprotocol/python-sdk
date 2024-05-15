import os
import json
import sys
from web3 import Web3
from dotenv import load_dotenv
import logging

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

# Now you can import from src
from src.resources.IPAsset import IPAsset  # Adjust the import path as needed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get the private key and RPC URL from environment variables
private_key = os.getenv('WALLET_PRIVATE_KEY')
rpc_url = os.getenv('RPC_PROVIDER_URL')

# Ensure the environment variables are set
if not private_key or not rpc_url:
    raise ValueError("Please set WALLET_PRIVATE_KEY and RPC_PROVIDER_URL in the .env file")

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(rpc_url))

# Check if connected
if web3.is_connected():
    logger.info("Connected to Web3 provider")
else:
    logger.error("Failed to connect to Web3 provider")

# Set up the account with the private key
account = web3.eth.account.from_key(private_key)

class StoryClient:
    def __init__(self, web3, account, chain_id):
        self.web3 = web3
        self.account = account
        self.chain_id = chain_id

        # Internal configuration path
        config_path = os.path.join(os.path.dirname(__file__), '../scripts/config.json')

        # Load contract configuration
        with open(config_path, 'r') as config_file:
            self.config = json.load(config_file)

        # Initialize IPAsset client only when accessed
        self._ip_asset = None

    @property
    def IPAsset(self):
        if self._ip_asset is None:
            self._ip_asset = IPAsset(self.web3, self.account, self.chain_id, self.config)
        return self._ip_asset




#SAMPLE EXAMPLE

# Initialize the StoryClient
chain_id = 11155111  # Sepolia chain ID
story_client = StoryClient(web3, account, chain_id)
logger.info("StoryClient instance created")

# Example usage
token_contract = "0xb4a4520BdEBE0690812eF0812EBAea648334365A"
token_id = 206

response = story_client.IPAsset.register(token_contract, token_id)
if response:
    if 'txHash' in response:
        logger.info(f"Root IPA created at transaction hash {response['txHash']}")
        logger.info(f"IP ID: {response['ipId']}")
    else:
        logger.info(f"Token is already registered with IP ID: {response['ipId']}")
else:
    logger.error("Failed to register IP asset")
