
import json
import os
from web3 import Web3

class LicenseRegistryClient:
    def __init__(self, web3: Web3):
        self.web3 = web3
        # Assuming config.json is located at the root of the project
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'config.json'))
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        contract_address = None
        for contract in config['contracts']:
            if contract['contract_name'] == 'LicenseRegistry':
                contract_address = contract['contract_address']
                break
        if not contract_address:
            raise ValueError(f"Contract address for LicenseRegistry not found in config.json")
        abi_path = os.path.join(os.path.dirname(__file__), '..', '..', 'abi', 'jsons', 'LicenseRegistry.json')
        with open(abi_path, 'r') as abi_file:
            abi = json.load(abi_file)
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
    
    def authority(self, ):
        
        return self.contract.functions.authority().call()
        
    
    def exists(self, licenseTemplate, licenseTermsId):
        
        return self.contract.functions.exists(licenseTemplate, licenseTermsId).call()
        
    
    def getAttachedLicenseTerms(self, ipId, index):
        
        return self.contract.functions.getAttachedLicenseTerms(ipId, index).call()
        
    
    def getAttachedLicenseTermsCount(self, ipId):
        
        return self.contract.functions.getAttachedLicenseTermsCount(ipId).call()
        
    
    def getDefaultLicenseTerms(self, ):
        
        return self.contract.functions.getDefaultLicenseTerms().call()
        
    
    def getDerivativeIp(self, parentIpId, index):
        
        return self.contract.functions.getDerivativeIp(parentIpId, index).call()
        
    
    def getDerivativeIpCount(self, parentIpId):
        
        return self.contract.functions.getDerivativeIpCount(parentIpId).call()
        
    
    def getExpireTime(self, ipId):
        
        return self.contract.functions.getExpireTime(ipId).call()
        
    
    def getLicensingConfig(self, ipId, licenseTemplate, licenseTermsId):
        
        return self.contract.functions.getLicensingConfig(ipId, licenseTemplate, licenseTermsId).call()
        
    
    def getParentIp(self, childIpId, index):
        
        return self.contract.functions.getParentIp(childIpId, index).call()
        
    
    def getParentIpCount(self, childIpId):
        
        return self.contract.functions.getParentIpCount(childIpId).call()
        
    
    def hasDerivativeIps(self, parentIpId):
        
        return self.contract.functions.hasDerivativeIps(parentIpId).call()
        
    
    def hasIpAttachedLicenseTerms(self, ipId, licenseTemplate, licenseTermsId):
        
        return self.contract.functions.hasIpAttachedLicenseTerms(ipId, licenseTemplate, licenseTermsId).call()
        
    
    def isConsumingScheduledOp(self, ):
        
        return self.contract.functions.isConsumingScheduledOp().call()
        
    
    def isDerivativeIp(self, childIpId):
        
        return self.contract.functions.isDerivativeIp(childIpId).call()
        
    
    def isExpiredNow(self, ipId):
        
        return self.contract.functions.isExpiredNow(ipId).call()
        
    
    def isParentIp(self, parentIpId, childIpId):
        
        return self.contract.functions.isParentIp(parentIpId, childIpId).call()
        
    
    def isRegisteredLicenseTemplate(self, licenseTemplate):
        
        return self.contract.functions.isRegisteredLicenseTemplate(licenseTemplate).call()
        
    
    def proxiableUUID(self, ):
        
        return self.contract.functions.proxiableUUID().call()
        
    
    def verifyMintLicenseToken(self, licensorIpId, licenseTemplate, licenseTermsId, isMintedByIpOwner):
        
        return self.contract.functions.verifyMintLicenseToken(licensorIpId, licenseTemplate, licenseTermsId, isMintedByIpOwner).call()
        
    