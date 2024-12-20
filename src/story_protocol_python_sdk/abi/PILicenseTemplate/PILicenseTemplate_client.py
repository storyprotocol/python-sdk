
import json
import os
from web3 import Web3

class PILicenseTemplateClient:
    def __init__(self, web3: Web3):
        self.web3 = web3
        # Assuming config.json is located at the root of the project
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'config.json'))
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        contract_address = None
        for contract in config['contracts']:
            if contract['contract_name'] == 'PILicenseTemplate':
                contract_address = contract['contract_address']
                break
        if not contract_address:
            raise ValueError(f"Contract address for PILicenseTemplate not found in config.json")
        abi_path = os.path.join(os.path.dirname(__file__), '..', '..', 'abi', 'jsons', 'PILicenseTemplate.json')
        with open(abi_path, 'r') as abi_file:
            abi = json.load(abi_file)
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
    
    def initialize(self, accessManager, name, metadataURI):
        
        return self.contract.functions.initialize(accessManager, name, metadataURI).transact()
        
    def build_initialize_transaction(self, accessManager, name, metadataURI, tx_params):
        return self.contract.functions.initialize(accessManager, name, metadataURI).build_transaction(tx_params)
    
    
    def registerLicenseTerms(self, terms):
        
        return self.contract.functions.registerLicenseTerms(terms).transact()
        
    def build_registerLicenseTerms_transaction(self, terms, tx_params):
        return self.contract.functions.registerLicenseTerms(terms).build_transaction(tx_params)
    
    
    def setApproval(self, parentIpId, licenseTermsId, childIpId, approved):
        
        return self.contract.functions.setApproval(parentIpId, licenseTermsId, childIpId, approved).transact()
        
    def build_setApproval_transaction(self, parentIpId, licenseTermsId, childIpId, approved, tx_params):
        return self.contract.functions.setApproval(parentIpId, licenseTermsId, childIpId, approved).build_transaction(tx_params)
    
    
    def setAuthority(self, newAuthority):
        
        return self.contract.functions.setAuthority(newAuthority).transact()
        
    def build_setAuthority_transaction(self, newAuthority, tx_params):
        return self.contract.functions.setAuthority(newAuthority).build_transaction(tx_params)
    
    
    def upgradeToAndCall(self, newImplementation, data):
        
        return self.contract.functions.upgradeToAndCall(newImplementation, data).transact()
        
    def build_upgradeToAndCall_transaction(self, newImplementation, data, tx_params):
        return self.contract.functions.upgradeToAndCall(newImplementation, data).build_transaction(tx_params)
    
    
    def verifyRegisterDerivative(self, childIpId, parentIpId, licenseTermsId, licensee):
        
        return self.contract.functions.verifyRegisterDerivative(childIpId, parentIpId, licenseTermsId, licensee).transact()
        
    def build_verifyRegisterDerivative_transaction(self, childIpId, parentIpId, licenseTermsId, licensee, tx_params):
        return self.contract.functions.verifyRegisterDerivative(childIpId, parentIpId, licenseTermsId, licensee).build_transaction(tx_params)
    
    
    def verifyRegisterDerivativeForAllParents(self, childIpId, parentIpIds, licenseTermsIds, childIpOwner):
        
        return self.contract.functions.verifyRegisterDerivativeForAllParents(childIpId, parentIpIds, licenseTermsIds, childIpOwner).transact()
        
    def build_verifyRegisterDerivativeForAllParents_transaction(self, childIpId, parentIpIds, licenseTermsIds, childIpOwner, tx_params):
        return self.contract.functions.verifyRegisterDerivativeForAllParents(childIpId, parentIpIds, licenseTermsIds, childIpOwner).build_transaction(tx_params)
    
    
    def exists(self, licenseTermsId):
        
        return self.contract.functions.exists(licenseTermsId).call()
        
    
    def getLicenseTerms(self, selectedLicenseTermsId):
        
        return self.contract.functions.getLicenseTerms(selectedLicenseTermsId).call()
        
    
    def getLicenseTermsId(self, terms):
        
        return self.contract.functions.getLicenseTermsId(terms).call()
        
    
    def getRoyaltyPolicy(self, licenseTermsId):
        
        return self.contract.functions.getRoyaltyPolicy(licenseTermsId).call()
        
    