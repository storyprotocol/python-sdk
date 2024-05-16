
import json
import os
from web3 import Web3

class LicensingModuleClient:
    def __init__(self, web3: Web3, contract_address: str):
        self.web3 = web3
        abi_path = os.path.join(os.path.dirname(__file__), 'LicensingModule.json')
        with open(abi_path, 'r') as abi_file:
            abi = json.load(abi_file)
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
    
    
    def __ProtocolPausable_init(self, accessManager):
        
        return self.contract.functions.__ProtocolPausable_init(accessManager).transact()
        
    
    
    def attachLicenseTerms(self, ipId, licenseTemplate, licenseTermsId):
        
        return self.contract.functions.attachLicenseTerms(ipId, licenseTemplate, licenseTermsId).transact()
        
    
    
    def initialize(self, accessManager):
        
        return self.contract.functions.initialize(accessManager).transact()
        
    
    
    def mintLicenseTokens(self, licensorIpId, licenseTemplate, licenseTermsId, amount, receiver, royaltyContext):
        
        return self.contract.functions.mintLicenseTokens(licensorIpId, licenseTemplate, licenseTermsId, amount, receiver, royaltyContext).transact()
        
    
    
    def pause(self, ):
        
        return self.contract.functions.pause().transact()
        
    
    
    def registerDerivative(self, childIpId, parentIpIds, licenseTermsIds, licenseTemplate, royaltyContext):
        
        return self.contract.functions.registerDerivative(childIpId, parentIpIds, licenseTermsIds, licenseTemplate, royaltyContext).transact()
        
    
    
    def registerDerivativeWithLicenseTokens(self, childIpId, licenseTokenIds, royaltyContext):
        
        return self.contract.functions.registerDerivativeWithLicenseTokens(childIpId, licenseTokenIds, royaltyContext).transact()
        
    
    
    def setAuthority(self, newAuthority):
        
        return self.contract.functions.setAuthority(newAuthority).transact()
        
    
    
    def setLicensingConfig(self, ipId, licenseTemplate, licenseTermsId, licensingConfig):
        
        return self.contract.functions.setLicensingConfig(ipId, licenseTemplate, licenseTermsId, licensingConfig).transact()
        
    
    
    def unpause(self, ):
        
        return self.contract.functions.unpause().transact()
        
    
    
    def upgradeToAndCall(self, newImplementation, data):
        
        return self.contract.functions.upgradeToAndCall(newImplementation, data).transact()
        
    
    