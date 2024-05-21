# src/story_client.py

import os
import json
import sys
import logging

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from story_protocol_python_sdk.resources.IPAsset import IPAsset
from story_protocol_python_sdk.resources.License import License
from story_protocol_python_sdk.resources.Royalty import Royalty

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

        # Initialize clients only when accessed
        self._ip_asset = None
        self._license = None
        self._royalty = None

    @property
    def IPAsset(self):
        if self._ip_asset is None:
            self._ip_asset = IPAsset(self.web3, self.account, self.chain_id)
        return self._ip_asset

    @property
    def License(self):
        if self._license is None:
            self._license = License(self.web3, self.account, self.chain_id)
        return self._license
    
    @property
    def Royalty(self):
        if self._royalty is None:
            self._royalty = Royalty(self.web3, self.account, self.chain_id)
        return self._royalty