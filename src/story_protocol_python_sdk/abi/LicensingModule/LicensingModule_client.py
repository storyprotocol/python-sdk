
import json
import os
from web3 import Web3

class LicensingModuleClient:
    def __init__(self, web3: Web3):
        self.web3 = web3
        # Assuming config.json is located at the root of the project
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'config.json'))
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        contract_address = None
        for contract in config['contracts']:
            if contract['contract_name'] == 'LicensingModule':
                contract_address = contract['contract_address']
                break
        if not contract_address:
            raise ValueError(f"Contract address for LicensingModule not found in config.json")
        abi_path = os.path.join(os.path.dirname(__file__), '..', '..', 'abi', 'jsons', 'LicensingModule.json')
        with open(abi_path, 'r') as abi_file:
            abi = json.load(abi_file)
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
    
    def attachLicenseTerms(self, ipId, licenseTemplate, licenseTermsId):
        
        return self.contract.functions.attachLicenseTerms(ipId, licenseTemplate, licenseTermsId).transact()
        
    def build_attachLicenseTerms_transaction(self, ipId, licenseTemplate, licenseTermsId, tx_params):
        return self.contract.functions.attachLicenseTerms(ipId, licenseTemplate, licenseTermsId).build_transaction(tx_params)
    
    
    def initialize(self, accessManager):
        
        return self.contract.functions.initialize(accessManager).transact()
        
    def build_initialize_transaction(self, accessManager, tx_params):
        return self.contract.functions.initialize(accessManager).build_transaction(tx_params)
    
    
    def mintLicenseTokens(self, licensorIpId, licenseTemplate, licenseTermsId, amount, receiver, royaltyContext):
        
        return self.contract.functions.mintLicenseTokens(licensorIpId, licenseTemplate, licenseTermsId, amount, receiver, royaltyContext).transact()
        
    def build_mintLicenseTokens_transaction(self, licensorIpId, licenseTemplate, licenseTermsId, amount, receiver, royaltyContext, tx_params):
        return self.contract.functions.mintLicenseTokens(licensorIpId, licenseTemplate, licenseTermsId, amount, receiver, royaltyContext).build_transaction(tx_params)
    
    
    def pause(self, ):
        
        return self.contract.functions.pause().transact()
        
    def build_pause_transaction(self, tx_params):
        return self.contract.functions.pause().build_transaction(tx_params)
    
    
    def registerDerivative(self, childIpId, parentIpIds, licenseTermsIds, licenseTemplate, royaltyContext):
        
        return self.contract.functions.registerDerivative(childIpId, parentIpIds, licenseTermsIds, licenseTemplate, royaltyContext).transact()
        
    def build_registerDerivative_transaction(self, childIpId, parentIpIds, licenseTermsIds, licenseTemplate, royaltyContext, tx_params):
        return self.contract.functions.registerDerivative(childIpId, parentIpIds, licenseTermsIds, licenseTemplate, royaltyContext).build_transaction(tx_params)
    
    
    def registerDerivativeWithLicenseTokens(self, childIpId, licenseTokenIds, royaltyContext):
        
        return self.contract.functions.registerDerivativeWithLicenseTokens(childIpId, licenseTokenIds, royaltyContext).transact()
        
    def build_registerDerivativeWithLicenseTokens_transaction(self, childIpId, licenseTokenIds, royaltyContext, tx_params):
        return self.contract.functions.registerDerivativeWithLicenseTokens(childIpId, licenseTokenIds, royaltyContext).build_transaction(tx_params)
    
    
    def setAuthority(self, newAuthority):
        
        return self.contract.functions.setAuthority(newAuthority).transact()
        
    def build_setAuthority_transaction(self, newAuthority, tx_params):
        return self.contract.functions.setAuthority(newAuthority).build_transaction(tx_params)
    
    
    def setLicensingConfig(self, ipId, licenseTemplate, licenseTermsId, licensingConfig):
        
        return self.contract.functions.setLicensingConfig(ipId, licenseTemplate, licenseTermsId, licensingConfig).transact()
        
    def build_setLicensingConfig_transaction(self, ipId, licenseTemplate, licenseTermsId, licensingConfig, tx_params):
        return self.contract.functions.setLicensingConfig(ipId, licenseTemplate, licenseTermsId, licensingConfig).build_transaction(tx_params)
    
    
    def unpause(self, ):
        
        return self.contract.functions.unpause().transact()
        
    def build_unpause_transaction(self, tx_params):
        return self.contract.functions.unpause().build_transaction(tx_params)
    
    
    def upgradeToAndCall(self, newImplementation, data):
        
        return self.contract.functions.upgradeToAndCall(newImplementation, data).transact()
        
    def build_upgradeToAndCall_transaction(self, newImplementation, data, tx_params):
        return self.contract.functions.upgradeToAndCall(newImplementation, data).build_transaction(tx_params)
    
    