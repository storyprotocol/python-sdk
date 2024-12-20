# src/story_protocol_python_sdk/story_client.py

import os
import sys

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from story_protocol_python_sdk.resources.IPAsset import IPAsset
from story_protocol_python_sdk.resources.License import License
from story_protocol_python_sdk.resources.Royalty import Royalty
from story_protocol_python_sdk.resources.IPAccount import IPAccount
from story_protocol_python_sdk.resources.Permission import Permission
from story_protocol_python_sdk.resources.NFTClient import NFTClient

class StoryClient:
    """
    A client for interacting with Story Protocol, providing access to IPAsset, License, and Royalty resources.

    :param web3 Web3: An instance of Web3.
    :param account: The account to use for transactions.
    :param chain_id int: The ID of the blockchain network.
    """
    def __init__(self, web3, account, chain_id: int):
        """
        Initialize the StoryClient with the given web3 instance, account, and chain ID.

        :param web3 Web3: An instance of Web3.
        :param account: The account to use for transactions.
        :param chain_id int: The ID of the blockchain network.
        :raises ValueError: If web3 or account is not provided.
        """
        if not web3 or not account:
            raise ValueError("web3 and account must be provided")

        if chain_id != 1516:
            raise ValueError("only support Odyssey chain")

        self.web3 = web3
        self.account = account
        self.chain_id = chain_id

        self._ip_asset = None
        self._license = None
        self._royalty = None
        self._ip_account = None
        self._permission = None
        self._nft_client = None

    @property
    def IPAsset(self) -> IPAsset:
        """
        Access the IPAsset resource.

        :return IPAsset: An instance of IPAsset.
        """
        if self._ip_asset is None:
            self._ip_asset = IPAsset(self.web3, self.account, self.chain_id)
        return self._ip_asset

    @property
    def License(self) -> License:
        """
        Access the License resource.

        :return License: An instance of License.
        """
        if self._license is None:
            self._license = License(self.web3, self.account, self.chain_id)
        return self._license
    
    @property
    def Royalty(self) -> Royalty:
        """
        Access the Royalty resource.

        :return Royalty: An instance of Royalty.
        """
        if self._royalty is None:
            self._royalty = Royalty(self.web3, self.account, self.chain_id)
        return self._royalty
    
    @property
    def IPAccount(self) -> IPAccount:
        """
        Access the IPAccount resource.

        :return IPAccount: An instance of IPAccount.
        """
        if self._ip_account is None:
            self._ip_account = IPAccount(self.web3, self.account, self.chain_id)
        return self._ip_account
    
    @property
    def Permission(self) -> Permission:
        """
        Access the Permission resource.

        :return Permission: An instance of Permission.
        """
        if self._permission is None:
            self._permission = Permission(self.web3, self.account, self.chain_id)
        return self._permission
    
    @property
    def NFTClient(self) -> NFTClient:
        """
        Access the NFTClient resource.

        :return NFTClient: An instance of NFTClient.
        """
        if self._nft_client is None:
            self._nft_client = NFTClient(self.web3, self.account, self.chain_id)
        return self._nft_client