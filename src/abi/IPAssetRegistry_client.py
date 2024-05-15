
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
    
    
    def __ProtocolPausable_init(self, accessManager):
        
        return self.contract.functions.__ProtocolPausable_init(accessManager).transact()
        
    
    
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
        
    
    
    def ERC6551_PUBLIC_REGISTRY(self, ):
        
        return self.contract.functions.ERC6551_PUBLIC_REGISTRY().call()
        
    
    
    def IP_ACCOUNT_IMPL(self, ):
        
        return self.contract.functions.IP_ACCOUNT_IMPL().call()
        
    
    
    def IP_ACCOUNT_SALT(self, ):
        
        return self.contract.functions.IP_ACCOUNT_SALT().call()
        
    
    
    def UPGRADE_INTERFACE_VERSION(self, ):
        
        return self.contract.functions.UPGRADE_INTERFACE_VERSION().call()
        
    
    
    def authority(self, ):
        
        return self.contract.functions.authority().call()
        
    
    
    def getIPAccountImpl(self, ):
        
        return self.contract.functions.getIPAccountImpl().call()
        
    
    
    def ipAccount(self, chainId, tokenContract, tokenId):
        
        return self.contract.functions.ipAccount(chainId, tokenContract, tokenId).call()
        
    
    
    def ipId(self, chainId, tokenContract, tokenId):
        
        return self.contract.functions.ipId(chainId, tokenContract, tokenId).call()
        
    
    
    def isConsumingScheduledOp(self, ):
        
        return self.contract.functions.isConsumingScheduledOp().call()
        
    
    
    def isRegistered(self, id):
        
        return self.contract.functions.isRegistered(id).call()
        
    
    
    def paused(self, ):
        
        return self.contract.functions.paused().call()
        
    
    
    def proxiableUUID(self, ):
        
        return self.contract.functions.proxiableUUID().call()
        
    
    
    def totalSupply(self, ):
        
        return self.contract.functions.totalSupply().call()
        
    
    