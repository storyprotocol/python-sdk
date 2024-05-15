import os
import json
import sys
import logging

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

# Now you can import from src
from src.resources.IPAsset import IPAsset

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StoryClient:
    def __init__(self, web3, account, chain_id):
        if not web3 or not account:
            raise ValueError("web3 and account must be provided")

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
