
import json
import os
from web3 import Web3

class IPAssetRegistryClient:
    def __init__(self, web3: Web3, contract_address: str):
        self.web3 = web3
        abi_path = os.path.join(os.path.dirname(__file__), 'IPAssetRegistry.json')
        with open(abi_path, 'r') as abi_file:
            abi = json.load(abi_file)
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
    
    
    def initialize(self, accessManager):
        return self.contract.functions.initialize(accessManager).transact()
    
    
    def pause(self, ):
        return self.contract.functions.pause().transact()
    
    
    def register(self, chainid, tokenContract, tokenId):
        return self.contract.functions.register(chainid, tokenContract, tokenId).transact()
    
    
    def registerIpAccount(self, chainId, tokenContract, tokenId):
        return self.contract.functions.registerIpAccount(chainId, tokenContract, tokenId).transact()
    
    
    def setAuthority(self, newAuthority):
        return self.contract.functions.setAuthority(newAuthority).transact()
    
    
    def unpause(self, ):
        return self.contract.functions.unpause().transact()
    
    
    def upgradeToAndCall(self, newImplementation, data):
        return self.contract.functions.upgradeToAndCall(newImplementation, data).transact()
    
    