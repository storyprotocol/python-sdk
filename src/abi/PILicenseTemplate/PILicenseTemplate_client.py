
import json
import os
from web3 import Web3

class PILicenseTemplateClient:
    def __init__(self, web3: Web3, contract_address: str):
        self.web3 = web3
        abi_path = os.path.join(os.path.dirname(__file__), 'PILicenseTemplate.json')
        with open(abi_path, 'r') as abi_file:
            abi = json.load(abi_file)
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
    
    
    def initialize(self, accessManager, name, metadataURI):
        
        return self.contract.functions.initialize(accessManager, name, metadataURI).transact()
        
    
    
    def registerLicenseTerms(self, terms):
        
        return self.contract.functions.registerLicenseTerms(terms).transact()
        
    
    
    def setApproval(self, parentIpId, licenseTermsId, childIpId, approved):
        
        return self.contract.functions.setApproval(parentIpId, licenseTermsId, childIpId, approved).transact()
        
    
    
    def setAuthority(self, newAuthority):
        
        return self.contract.functions.setAuthority(newAuthority).transact()
        
    
    
    def upgradeToAndCall(self, newImplementation, data):
        
        return self.contract.functions.upgradeToAndCall(newImplementation, data).transact()
        
    
    
    def verifyMintLicenseToken(self, licenseTermsId, licensee, licensorIpId, ):
        
        return self.contract.functions.verifyMintLicenseToken(licenseTermsId, licensee, licensorIpId, ).transact()
        
    
    
    def verifyRegisterDerivative(self, childIpId, parentIpId, licenseTermsId, licensee):
        
        return self.contract.functions.verifyRegisterDerivative(childIpId, parentIpId, licenseTermsId, licensee).transact()
        
    
    
    def verifyRegisterDerivativeForAllParents(self, childIpId, parentIpIds, licenseTermsIds, childIpOwner):
        
        return self.contract.functions.verifyRegisterDerivativeForAllParents(childIpId, parentIpIds, licenseTermsIds, childIpOwner).transact()
        
    
    