
import json
import os
from web3 import Web3

class AccessControllerClient:
    def __init__(self, web3: Web3):
        self.web3 = web3
        # Assuming config.json is located at the root of the project
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'config.json'))
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        contract_address = None
        for contract in config['contracts']:
            if contract['contract_name'] == 'AccessController':
                contract_address = contract['contract_address']
                break
        if not contract_address:
            raise ValueError(f"Contract address for AccessController not found in config.json")
        abi_path = os.path.join(os.path.dirname(__file__), '..', '..', 'abi', 'jsons', 'AccessController.json')
        with open(abi_path, 'r') as abi_file:
            abi = json.load(abi_file)
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
    
    def checkPermission(self, ipAccount, signer, to, func):
        
        return self.contract.functions.checkPermission(ipAccount, signer, to, func).call()
        
    