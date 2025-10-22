import json
import os

from web3 import Web3


class Multicall3Client:
    def __init__(self, web3: Web3):
        self.web3 = web3
        # Assuming config.json is located at the root of the project
        config_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "scripts", "config.json"
            )
        )
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
        contract_address = None
        for contract in config["contracts"]:
            if contract["contract_name"] == "Multicall3":
                contract_address = contract["contract_address"]
                break
        if not contract_address:
            raise ValueError("Contract address for Multicall3 not found in config.json")
        abi_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "abi", "jsons", "Multicall3.json"
        )
        with open(abi_path, "r") as abi_file:
            abi = json.load(abi_file)
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)

    def aggregate3Value(self, calls):
        return self.contract.functions.aggregate3Value(calls).transact()

    def build_aggregate3Value_transaction(self, calls, tx_params):
        return self.contract.functions.aggregate3Value(calls).build_transaction(
            tx_params
        )
