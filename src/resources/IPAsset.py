import logging
from web3 import Web3
from src.abi.IPAssetRegistry_client import IPAssetRegistryClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IPAsset:
    def __init__(self, web3: Web3, account, chain_id, config):
        self.web3 = web3
        self.account = account
        self.chain_id = chain_id

        # Load contract configuration
        self.config = config

        self.ip_asset_registry_address = self._get_contract_address('IPAssetRegistry')
        self.ip_asset_registry_client = IPAssetRegistryClient(web3, self.ip_asset_registry_address)

    def _get_contract_address(self, contract_name):
        for contract in self.config['contracts']:
            if contract['contract_name'] == contract_name:
                return contract['contract_address']
        raise ValueError(f"Contract {contract_name} not found in configuration")

    def _get_ip_id(self, token_contract, token_id):
        return self.ip_asset_registry_client.contract.functions.ipId(self.chain_id, token_contract, token_id).call()

    def _is_registered(self, ip_id):
        return self.ip_asset_registry_client.contract.functions.isRegistered(ip_id).call()

    def register(self, token_contract, token_id):
        try:
            # Check if the token is already registered
            ip_id = self._get_ip_id(token_contract, token_id)
            if self._is_registered(ip_id):
                return {
                    'message': 'Token is already registered',
                    'ipId': ip_id
                }

            # Build the transaction
            transaction = self.ip_asset_registry_client.contract.functions.register(self.chain_id, token_contract, token_id).build_transaction({
                'from': self.account.address,
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'gas': 2000000,
                'gasPrice': self.web3.to_wei('100', 'gwei')  # Adjusted gas price for faster processing
            })

            # Sign the transaction using the account object
            signed_txn = self.account.sign_transaction(transaction)

            # Send the transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

            return {
                'txHash': tx_hash.hex(),
                'ipId': ip_id
            }

        except Exception as e:
            logger.error(f"Error interacting with contract: {e}")
            return None
