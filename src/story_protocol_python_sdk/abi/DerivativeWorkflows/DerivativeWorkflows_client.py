import json
import os

from web3 import Web3


class DerivativeWorkflowsClient:
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
            if contract["contract_name"] == "DerivativeWorkflows":
                contract_address = contract["contract_address"]
                break
        if not contract_address:
            raise ValueError(
                "Contract address for DerivativeWorkflows not found in config.json"
            )
        abi_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "abi",
            "jsons",
            "DerivativeWorkflows.json",
        )
        with open(abi_path, "r") as abi_file:
            abi = json.load(abi_file)
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)

    def mintAndRegisterIpAndMakeDerivative(
        self, spgNftContract, derivData, ipMetadata, recipient, allowDuplicates
    ):
        return self.contract.functions.mintAndRegisterIpAndMakeDerivative(
            spgNftContract, derivData, ipMetadata, recipient, allowDuplicates
        ).transact()

    def build_mintAndRegisterIpAndMakeDerivative_transaction(
        self,
        spgNftContract,
        derivData,
        ipMetadata,
        recipient,
        allowDuplicates,
        tx_params,
    ):
        return self.contract.functions.mintAndRegisterIpAndMakeDerivative(
            spgNftContract, derivData, ipMetadata, recipient, allowDuplicates
        ).build_transaction(tx_params)

    def mintAndRegisterIpAndMakeDerivativeWithLicenseTokens(
        self,
        spgNftContract,
        licenseTokenIds,
        royaltyContext,
        maxRts,
        ipMetadata,
        recipient,
        allowDuplicates,
    ):
        return (
            self.contract.functions.mintAndRegisterIpAndMakeDerivativeWithLicenseTokens(
                spgNftContract,
                licenseTokenIds,
                royaltyContext,
                maxRts,
                ipMetadata,
                recipient,
                allowDuplicates,
            ).transact()
        )

    def build_mintAndRegisterIpAndMakeDerivativeWithLicenseTokens_transaction(
        self,
        spgNftContract,
        licenseTokenIds,
        royaltyContext,
        maxRts,
        ipMetadata,
        recipient,
        allowDuplicates,
        tx_params,
    ):
        return (
            self.contract.functions.mintAndRegisterIpAndMakeDerivativeWithLicenseTokens(
                spgNftContract,
                licenseTokenIds,
                royaltyContext,
                maxRts,
                ipMetadata,
                recipient,
                allowDuplicates,
            ).build_transaction(tx_params)
        )

    def registerIpAndMakeDerivative(
        self, nftContract, tokenId, derivData, ipMetadata, sigMetadataAndRegister
    ):
        return self.contract.functions.registerIpAndMakeDerivative(
            nftContract, tokenId, derivData, ipMetadata, sigMetadataAndRegister
        ).transact()

    def build_registerIpAndMakeDerivative_transaction(
        self,
        nftContract,
        tokenId,
        derivData,
        ipMetadata,
        sigMetadataAndRegister,
        tx_params,
    ):
        return self.contract.functions.registerIpAndMakeDerivative(
            nftContract, tokenId, derivData, ipMetadata, sigMetadataAndRegister
        ).build_transaction(tx_params)

    def registerIpAndMakeDerivativeWithLicenseTokens(
        self,
        nftContract,
        tokenId,
        licenseTokenIds,
        royaltyContext,
        maxRts,
        ipMetadata,
        sigMetadataAndRegister,
    ):
        return self.contract.functions.registerIpAndMakeDerivativeWithLicenseTokens(
            nftContract,
            tokenId,
            licenseTokenIds,
            royaltyContext,
            maxRts,
            ipMetadata,
            sigMetadataAndRegister,
        ).transact()

    def build_registerIpAndMakeDerivativeWithLicenseTokens_transaction(
        self,
        nftContract,
        tokenId,
        licenseTokenIds,
        royaltyContext,
        maxRts,
        ipMetadata,
        sigMetadataAndRegister,
        tx_params,
    ):
        return self.contract.functions.registerIpAndMakeDerivativeWithLicenseTokens(
            nftContract,
            tokenId,
            licenseTokenIds,
            royaltyContext,
            maxRts,
            ipMetadata,
            sigMetadataAndRegister,
        ).build_transaction(tx_params)
