
import json
import os
from web3 import Web3

class IpRoyaltyVaultImplClient:
    def __init__(self, web3: Web3, contract_address=None):
        self.web3 = web3
        abi_path = os.path.join(os.path.dirname(__file__), '..', '..', 'abi', 'jsons', 'IpRoyaltyVaultImpl.json')
        with open(abi_path, 'r') as abi_file:
            abi = json.load(abi_file)
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
    
    def claimRevenueOnBehalfBySnapshotBatch(self, snapshotIds, token, claimer):
        
        return self.contract.functions.claimRevenueOnBehalfBySnapshotBatch(snapshotIds, token, claimer).transact()
        
    def build_claimRevenueOnBehalfBySnapshotBatch_transaction(self, snapshotIds, token, claimer, tx_params):
        return self.contract.functions.claimRevenueOnBehalfBySnapshotBatch(snapshotIds, token, claimer).build_transaction(tx_params)
    
    
    def claimRevenueOnBehalfByTokenBatch(self, snapshotId, tokenList, claimer):
        
        return self.contract.functions.claimRevenueOnBehalfByTokenBatch(snapshotId, tokenList, claimer).transact()
        
    def build_claimRevenueOnBehalfByTokenBatch_transaction(self, snapshotId, tokenList, claimer, tx_params):
        return self.contract.functions.claimRevenueOnBehalfByTokenBatch(snapshotId, tokenList, claimer).build_transaction(tx_params)
    
    
    def snapshot(self, ):
        
        return self.contract.functions.snapshot().transact()
        
    def build_snapshot_transaction(self, tx_params):
        return self.contract.functions.snapshot().build_transaction(tx_params)
    
    
    def claimableRevenue(self, account, snapshotId, token):
        
        return self.contract.functions.claimableRevenue(account, snapshotId, token).call()
        
    