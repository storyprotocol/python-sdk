
import json
import os
from web3 import Web3

class SPGClient:
    def __init__(self, web3: Web3):
        self.web3 = web3
        # Assuming config.json is located at the root of the project
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'config.json'))
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        contract_address = None
        for contract in config['contracts']:
            if contract['contract_name'] == 'SPG':
                contract_address = contract['contract_address']
                break
        if not contract_address:
            raise ValueError(f"Contract address for SPG not found in config.json")
        abi_path = os.path.join(os.path.dirname(__file__), 'SPG.json')
        with open(abi_path, 'r') as abi_file:
            abi = json.load(abi_file)
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
    
    def createCollection(self, name, symbol, maxSupply, mintFee, mintFeeToken, owner):
        
        return self.contract.functions.createCollection(name, symbol, maxSupply, mintFee, mintFeeToken, owner).transact()
        
    def build_createCollection_transaction(self, name, symbol, maxSupply, mintFee, mintFeeToken, owner, tx_params):
        return self.contract.functions.createCollection(name, symbol, maxSupply, mintFee, mintFeeToken, owner).build_transaction(tx_params)
    
    
    def mintAndRegisterIpAndAttachPILTerms(self, nftContract, recipient, metadata, terms):
        
        return self.contract.functions.mintAndRegisterIpAndAttachPILTerms(nftContract, recipient, metadata, terms).transact()
        
    def build_mintAndRegisterIpAndAttachPILTerms_transaction(self, nftContract, recipient, metadata, terms, tx_params):
        return self.contract.functions.mintAndRegisterIpAndAttachPILTerms(nftContract, recipient, metadata, terms).build_transaction(tx_params)
    
    
    def registerIp(self, nftContract, tokenId, metadata, sigMetadata):
        
        return self.contract.functions.registerIp(nftContract, tokenId, metadata, sigMetadata).transact()
        
    def build_registerIp_transaction(self, nftContract, tokenId, metadata, sigMetadata, tx_params):
        return self.contract.functions.registerIp(nftContract, tokenId, metadata, sigMetadata).build_transaction(tx_params)
    
    
    def registerIpAndAttachPILTerms(self, nftContract, tokenId, metadata, terms, sigMetadata, sigAttach):
        
        return self.contract.functions.registerIpAndAttachPILTerms(nftContract, tokenId, metadata, terms, sigMetadata, sigAttach).transact()
        
    def build_registerIpAndAttachPILTerms_transaction(self, nftContract, tokenId, metadata, terms, sigMetadata, sigAttach, tx_params):
        return self.contract.functions.registerIpAndAttachPILTerms(nftContract, tokenId, metadata, terms, sigMetadata, sigAttach).build_transaction(tx_params)
    
    
    def registerIpAndMakeDerivative(self, nftContract, tokenId, derivData, metadata, sigMetadata, sigRegister):
        
        return self.contract.functions.registerIpAndMakeDerivative(nftContract, tokenId, derivData, metadata, sigMetadata, sigRegister).transact()
        
    def build_registerIpAndMakeDerivative_transaction(self, nftContract, tokenId, derivData, metadata, sigMetadata, sigRegister, tx_params):
        return self.contract.functions.registerIpAndMakeDerivative(nftContract, tokenId, derivData, metadata, sigMetadata, sigRegister).build_transaction(tx_params)
    
    