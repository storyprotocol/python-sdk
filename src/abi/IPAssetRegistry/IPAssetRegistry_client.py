
import json
import os
from web3 import Web3

class IPAssetRegistryClient:
    def __init__(self, web3: Web3):
        self.web3 = web3
        # Assuming config.json is located at the root of the project
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts', 'config.json'))
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        contract_address = None
        for contract in config['contracts']:
            if contract['contract_name'] == 'IPAssetRegistry':
                contract_address = contract['contract_address']
                break
        if not contract_address:
            raise ValueError(f"Contract address for IPAssetRegistry not found in config.json")
        abi_path = os.path.join(os.path.dirname(__file__), 'IPAssetRegistry.json')
        with open(abi_path, 'r') as abi_file:
            abi = json.load(abi_file)
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
    
    def initialize(self, accessManager):
        return self.contract.functions.initialize(accessManager).transact()
        
    def build_initialize_transaction(self, accessManager, tx_params):
        return self.contract.functions.initialize(accessManager).build_transaction(tx_params)
    
    def pause(self, ):
        return self.contract.functions.pause().transact()
        
    def build_pause_transaction(self, tx_params):
        return self.contract.functions.pause().build_transaction(tx_params)
    
    def register(self, chainid, tokenContract, tokenId):
        return self.contract.functions.register(chainid, tokenContract, tokenId).transact()
        
    def build_register_transaction(self, chainid, tokenContract, tokenId, tx_params):
        return self.contract.functions.register(chainid, tokenContract, tokenId).build_transaction(tx_params)
    
    def registerIpAccount(self, chainId, tokenContract, tokenId):
        return self.contract.functions.registerIpAccount(chainId, tokenContract, tokenId).transact()
        
    def build_registerIpAccount_transaction(self, chainId, tokenContract, tokenId, tx_params):
        return self.contract.functions.registerIpAccount(chainId, tokenContract, tokenId).build_transaction(tx_params)
    
    def setAuthority(self, newAuthority):
        return self.contract.functions.setAuthority(newAuthority).transact()
        
    def build_setAuthority_transaction(self, newAuthority, tx_params):
        return self.contract.functions.setAuthority(newAuthority).build_transaction(tx_params)
    
    def unpause(self, ):
        return self.contract.functions.unpause().transact()
        
    def build_unpause_transaction(self, tx_params):
        return self.contract.functions.unpause().build_transaction(tx_params)
    
    def upgradeToAndCall(self, newImplementation, data):
        return self.contract.functions.upgradeToAndCall(newImplementation, data).transact()
        
    def build_upgradeToAndCall_transaction(self, newImplementation, data, tx_params):
        return self.contract.functions.upgradeToAndCall(newImplementation, data).build_transaction(tx_params)
    
    def authority(self, ):
        return self.contract.functions.authority().call()
        
    def build_authority_transaction(self, tx_params):
        return self.contract.functions.authority().build_transaction(tx_params)
    
    def getIPAccountImpl(self, ):
        return self.contract.functions.getIPAccountImpl().call()
        
    def build_getIPAccountImpl_transaction(self, tx_params):
        return self.contract.functions.getIPAccountImpl().build_transaction(tx_params)
    
    def ipAccount(self, chainId, tokenContract, tokenId):
        return self.contract.functions.ipAccount(chainId, tokenContract, tokenId).call()
        
    def build_ipAccount_transaction(self, chainId, tokenContract, tokenId, tx_params):
        return self.contract.functions.ipAccount(chainId, tokenContract, tokenId).build_transaction(tx_params)
    
    def ipId(self, chainId, tokenContract, tokenId):
        return self.contract.functions.ipId(chainId, tokenContract, tokenId).call()
        
    def build_ipId_transaction(self, chainId, tokenContract, tokenId, tx_params):
        return self.contract.functions.ipId(chainId, tokenContract, tokenId).build_transaction(tx_params)
    
    def isConsumingScheduledOp(self, ):
        return self.contract.functions.isConsumingScheduledOp().call()
        
    def build_isConsumingScheduledOp_transaction(self, tx_params):
        return self.contract.functions.isConsumingScheduledOp().build_transaction(tx_params)
    
    def isRegistered(self, id):
        return self.contract.functions.isRegistered(id).call()
        
    def build_isRegistered_transaction(self, id, tx_params):
        return self.contract.functions.isRegistered(id).build_transaction(tx_params)
    
    def paused(self, ):
        return self.contract.functions.paused().call()
        
    def build_paused_transaction(self, tx_params):
        return self.contract.functions.paused().build_transaction(tx_params)
    
    def proxiableUUID(self, ):
        return self.contract.functions.proxiableUUID().call()
        
    def build_proxiableUUID_transaction(self, tx_params):
        return self.contract.functions.proxiableUUID().build_transaction(tx_params)
    
    def totalSupply(self, ):
        return self.contract.functions.totalSupply().call()
        
    def build_totalSupply_transaction(self, tx_params):
        return self.contract.functions.totalSupply().build_transaction(tx_params)
    