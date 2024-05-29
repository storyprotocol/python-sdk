#src/story_protcol_python_sdk/resources/NFTClient.py

from web3 import Web3

from story_protocol_python_sdk.abi.SPG.SPG_client import SPGClient

from story_protocol_python_sdk.utils.license_terms import get_license_term_by_type, PIL_TYPE
from story_protocol_python_sdk.utils.transaction_utils import build_and_send_transaction

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ZERO_HASH = "0x0000000000000000000000000000000000000000000000000000000000000000"

class NFTClient:
    """
    NFTClient handles the creation of SPG NFT collections.

    :param web3 Web3: An instance of Web3.
    :param account: The account to use for transactions.
    :param chain_id int: The ID of the blockchain network.
    """    
    def __init__(self, web3: Web3, account, chain_id: int):
        self.web3 = web3
        self.account = account
        self.chain_id = chain_id

        self.spg_client = SPGClient(web3)


    def createNFTCollection(self, name: str, symbol: str, max_supply: int, mint_fee: int, mint_fee_token: str, owner: str, tx_options: dict = None) -> dict:
        """
        Creates a new SPG NFT Collection.

        :param name str: The name of the collection.
        :param symbol str: The symbol of the collection.
        :param max_supply int: The maximum supply of the collection.
        :param mint_fee int: The cost to mint a token.
        :param mint_fee_token str: The token to mint.
        :param owner str: The owner of the collection.
        :param tx_options dict: [Optional] The transaction options.
        :return dict: A dictionary with the transaction hash and collection address.
        """
        try:
            if mint_fee is not None and (mint_fee < 0 or not self.web3.is_address(mint_fee_token or "")):
                raise ValueError("Invalid mint fee token address, mint fee is greater than 0.")

            response = build_and_send_transaction(
                self.web3,
                self.account,
                self.spg_client.build_createCollection_transaction,
                name,
                symbol,
                max_supply if max_supply is not None else 2**32 - 1,
                mint_fee if mint_fee is not None else 0,
                mint_fee_token if mint_fee_token is not None else ZERO_ADDRESS,
                owner if owner else self.account.address,
                tx_options=tx_options
            )

            collection_address  = self._parse_tx_collection_created_event(response['txReceipt'])

            return {
                'txHash': response['txHash'],
                'nftContract': collection_address
            }

        except Exception as e:
            raise e
        
    def _parse_tx_collection_created_event(self, tx_receipt: dict) -> int:
        """
        Parse the CollectionCreated event from a transaction receipt.

        :param tx_receipt dict: The transaction receipt.
        :return int: The ID of the license terms.
        """
        event_signature = self.web3.keccak(text="CollectionCreated(address)").hex()

        for log in tx_receipt['logs']:
            if log['topics'][0].hex() == event_signature:
                return self.web3.to_checksum_address('0x' + log['topics'][1].hex()[-40:])

        return None