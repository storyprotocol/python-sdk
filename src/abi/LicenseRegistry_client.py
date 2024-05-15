
import json
import os
from web3 import Web3

class LicenseRegistryClient:
    def __init__(self, web3: Web3, contract_address: str):
        self.web3 = web3
        abi_path = os.path.join(os.path.dirname(__file__), 'LicenseRegistry.json')
        with open(abi_path, 'r') as abi_file:
            abi = json.load(abi_file)
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
    
    
    def attachLicenseTermsToIp(self, ipId, licenseTemplate, licenseTermsId):
        
        return self.contract.functions.attachLicenseTermsToIp(ipId, licenseTemplate, licenseTermsId).transact()
        
    
    
    def initialize(self, accessManager):
        
        return self.contract.functions.initialize(accessManager).transact()
        
    
    
    def registerDerivativeIp(self, childIpId, parentIpIds, licenseTemplate, licenseTermsIds):
        
        return self.contract.functions.registerDerivativeIp(childIpId, parentIpIds, licenseTemplate, licenseTermsIds).transact()
        
    
    
    def registerLicenseTemplate(self, licenseTemplate):
        
        return self.contract.functions.registerLicenseTemplate(licenseTemplate).transact()
        
    
    
    def setAuthority(self, newAuthority):
        
        return self.contract.functions.setAuthority(newAuthority).transact()
        
    
    
    def setDefaultLicenseTerms(self, newLicenseTemplate, newLicenseTermsId):
        
        return self.contract.functions.setDefaultLicenseTerms(newLicenseTemplate, newLicenseTermsId).transact()
        
    
    
    def setExpireTime(self, ipId, expireTime):
        
        return self.contract.functions.setExpireTime(ipId, expireTime).transact()
        
    
    
    def setLicensingConfigForIp(self, ipId, licensingConfig):
        
        return self.contract.functions.setLicensingConfigForIp(ipId, licensingConfig).transact()
        
    
    
    def setLicensingConfigForLicense(self, ipId, licenseTemplate, licenseTermsId, licensingConfig):
        
        return self.contract.functions.setLicensingConfigForLicense(ipId, licenseTemplate, licenseTermsId, licensingConfig).transact()
        
    
    
    def upgradeToAndCall(self, newImplementation, data):
        
        return self.contract.functions.upgradeToAndCall(newImplementation, data).transact()
        
    
    