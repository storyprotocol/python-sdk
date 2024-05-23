
import json
import os
from web3 import Web3

class IpRoyaltyVaultImplClient:
    def __init__(self, web3: Web3, contract_address=None):
        self.web3 = web3
        abi_path = os.path.join(os.path.dirname(__file__), 'IpRoyaltyVaultImpl.json')
        with open(abi_path, 'r') as abi_file:
            abi = json.load(abi_file)
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
    
    def claimRevenueBySnapshotBatch(self, snapshotIds, token):
        
        return self.contract.functions.claimRevenueBySnapshotBatch(snapshotIds, token).transact()
        
    def build_claimRevenueBySnapshotBatch_transaction(self, snapshotIds, token, tx_params):
        return self.contract.functions.claimRevenueBySnapshotBatch(snapshotIds, token).build_transaction(tx_params)
    
    
    def collectRoyaltyTokens(self, ancestorIpId):
        
        return self.contract.functions.collectRoyaltyTokens(ancestorIpId).transact()
        
    def build_collectRoyaltyTokens_transaction(self, ancestorIpId, tx_params):
        return self.contract.functions.collectRoyaltyTokens(ancestorIpId).build_transaction(tx_params)
    
    
    def snapshot(self, ):
        
        return self.contract.functions.snapshot().transact()
        
    def build_snapshot_transaction(self, tx_params):
        return self.contract.functions.snapshot().build_transaction(tx_params)
    
    
    def claimableRevenue(self, account, snapshotId, token):
        
        return self.contract.functions.claimableRevenue(account, snapshotId, token).call()
        
    
    def unclaimedRoyaltyTokens(self, ):
        
        return self.contract.functions.unclaimedRoyaltyTokens().call()
        
    