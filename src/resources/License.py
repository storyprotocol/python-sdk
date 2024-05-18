import logging
from web3 import Web3
from web3.exceptions import LogTopicError

from src.abi.PILicenseTemplate.PILicenseTemplate_client import PILicenseTemplateClient
from src.abi.LicenseRegistry.LicenseRegistry_client import LicenseRegistryClient
from src.abi.LicensingModule.LicensingModule_client import LicensingModuleClient
from src.abi.IPAssetRegistry.IPAssetRegistry_client import IPAssetRegistryClient
from src.utils.license_terms import get_license_term_by_type, PIL_TYPE

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to capture all log messages
logger = logging.getLogger(__name__)

class License:
    def __init__(self, web3: Web3, account, chain_id):
        self.web3 = web3
        self.account = account
        self.chain_id = chain_id

        self.license_template_client = PILicenseTemplateClient(web3)
        self.license_registry_client = LicenseRegistryClient(web3)
        self.licensing_module_client  = LicensingModuleClient(web3)
        self.ip_asset_registry_client = IPAssetRegistryClient(web3)

    def _get_license_terms_id(self, license_terms):
        logger.info(f"Getting license terms ID for: {license_terms}")
        return self.license_template_client.getLicenseTermsId(license_terms)

    def registerNonComSocialRemixingPIL(self):
        try:
            # Get the license terms for non-commercial social remixing PIL
            license_terms = get_license_term_by_type(PIL_TYPE['NON_COMMERCIAL_REMIX'])
            logger.info(f"License terms: {license_terms}")

            # Check if the license terms are already registered
            license_terms_id = self._get_license_terms_id(license_terms)
            logger.info(f"License terms ID: {license_terms_id}")
            if (license_terms_id is not None) and (license_terms_id != 0):
                return {'licenseTermsId': license_terms_id}

            # Build the transaction
            transaction = self.license_template_client.build_registerLicenseTerms_transaction(
                license_terms, {
                    'from': self.account.address,
                    'nonce': self.web3.eth.get_transaction_count(self.account.address),
                    'gas': 2000000,
                    'gasPrice': self.web3.to_wei('100', 'gwei')  # Adjusted gas price for faster processing
                }
            )
            logger.info(f"Transaction: {transaction}")

            # Sign the transaction using the account object
            signed_txn = self.account.sign_transaction(transaction)
            logger.info(f"Signed transaction: {signed_txn}")

            # Send the transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.info(f"Transaction hash: {tx_hash.hex()}")

            # Wait for transaction receipt with a longer timeout
            try:
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)  # 10 minutes timeout
                logger.info(f"Transaction receipt: {tx_receipt}")

                # Parse the event logs for LicenseTermsRegistered
                target_logs = self._parse_tx_license_terms_registered_event(tx_receipt)
                return {
                    'txHash': tx_hash.hex(),
                    'licenseTermsId': target_logs
                }

            except Exception as e:
                logger.error(f"Transaction {tx_hash.hex()} was not mined within the timeout period: {e}")
                return None

        except Exception as e:
            logger.error(f"Error interacting with contract: {e}")
            return None
        
    def registerCommercialUsePIL(self, minting_fee, currency, royalty_policy, tx_options=None):
        try:
            logger.info(f"Starting registerCommercialUsePIL with minting_fee: {minting_fee}, currency: {currency}, royalty_policy: {royalty_policy}")

            # Construct complete license terms
            complete_license_terms = get_license_term_by_type(PIL_TYPE['COMMERCIAL_USE'], {
                'mintingFee': minting_fee,
                'currency': currency,
                'royaltyPolicy': royalty_policy,
            })
            logger.info(f"Complete license terms: {complete_license_terms}")

            # Check if the license terms are already registered
            license_terms_id = self._get_license_terms_id(complete_license_terms)
            logger.info(f"License terms ID: {license_terms_id}")
            if (license_terms_id is not None) and (license_terms_id != 0):
                return {'licenseTermsId': license_terms_id}

            # Build the transaction
            transaction = self.license_template_client.build_registerLicenseTerms_transaction(
                complete_license_terms, {
                    'from': self.account.address,
                    'nonce': self.web3.eth.get_transaction_count(self.account.address),
                    'gas': 2000000,
                    'gasPrice': self.web3.to_wei('100', 'gwei')  # Adjusted gas price for faster processing
                }
            )
            logger.info(f"Built transaction: {transaction}")

            # Sign the transaction using the account object
            signed_txn = self.account.sign_transaction(transaction)
            logger.info(f"Signed transaction: {signed_txn}")

            # Send the transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.info(f"Transaction hash: {tx_hash.hex()}")

            # Wait for transaction receipt with a longer timeout
            try:
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)  # 10 minutes timeout
                logger.info(f"Transaction receipt: {tx_receipt}")

                # Parse the event logs for LicenseTermsRegistered
                if not tx_receipt.logs:
                    logger.error(f"No logs found in transaction receipt: {tx_receipt}")
                    return None

                target_logs = self._parse_tx_license_terms_registered_event(tx_receipt)
                return {
                    'txHash': tx_hash.hex(),
                    'licenseTermsId': target_logs
                }

            except Exception as e:
                logger.error(f"Transaction {tx_hash.hex()} was not mined within the timeout period: {e}")
                return None

        except Exception as e:
            logger.error(f"Error interacting with contract: {e}")
            return None

    def registerCommercialRemixPIL(self, minting_fee, currency, commercial_rev_share, royalty_policy, tx_options=None):
        try:
            logger.info(f"Starting registerCommercialRemixPIL with minting_fee: {minting_fee}, currency: {currency}, commercial_rev_share: {commercial_rev_share}, royalty_policy: {royalty_policy}")

            # Construct complete license terms
            complete_license_terms = get_license_term_by_type(PIL_TYPE['COMMERCIAL_REMIX'], {
                'mintingFee': minting_fee,
                'currency': currency,
                'commercialRevShare': commercial_rev_share,
                'royaltyPolicy': royalty_policy,
            })
            logger.info(f"Complete license terms: {complete_license_terms}")

            # Check if the license terms are already registered
            license_terms_id = self._get_license_terms_id(complete_license_terms)
            logger.info(f"License terms ID: {license_terms_id}")
            if license_terms_id and license_terms_id != 0:
                return {'licenseTermsId': license_terms_id}

            # Build the transaction
            transaction = self.license_template_client.build_registerLicenseTerms_transaction(
                complete_license_terms, {
                    'from': self.account.address,
                    'nonce': self.web3.eth.get_transaction_count(self.account.address),
                    'gas': 2000000,
                    'gasPrice': self.web3.to_wei('100', 'gwei')
                }
            )
            logger.info(f"Built transaction: {transaction}")

            # Sign the transaction using the account object
            signed_txn = self.account.sign_transaction(transaction)
            logger.info(f"Signed transaction: {signed_txn}")

            # Send the transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.info(f"Transaction hash: {tx_hash.hex()}")

            # Wait for transaction receipt with a longer timeout
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
            logger.info(f"Transaction receipt: {tx_receipt}")

            # Parse the event logs for LicenseTermsRegistered
            if not tx_receipt.logs:
                logger.error(f"No logs found in transaction receipt: {tx_receipt}")
                return None

            target_logs = self._parse_tx_license_terms_registered_event(tx_receipt)
            return {
                'txHash': tx_hash.hex(),
                'licenseTermsId': target_logs
            }

        except Exception as e:
            logger.error(f"Error interacting with contract: {e}")
            return None

    def _parse_tx_license_terms_registered_event(self, tx_receipt):
        event_signature = self.web3.keccak(text="LicenseTermsRegistered(uint256,address,bytes)").hex()

        for log in tx_receipt['logs']:
            if log['topics'][0].hex() == event_signature:
                return int(log['topics'][1].hex(), 16)

        return None
    
    def attachLicenseTerms(self, ip_id, license_template, license_terms_id):
        try:
            logger.info(f"Starting attachLicenseTerms with ip_id: {ip_id}, license_template: {license_template}, license_terms_id: {license_terms_id}")

            # Check if the IP is registered
            is_registered = self.ip_asset_registry_client.isRegistered(ip_id)
            if not is_registered:
                raise ValueError(f"The IP with id {ip_id} is not registered.")

            # Check if the license terms exist
            is_existed = self.license_registry_client.exists(license_template, license_terms_id)
            if not is_existed:
                raise ValueError(f"License terms id {license_terms_id} do not exist.")

            # Check if the license terms are already attached to the IP
            is_attached_license_terms = self.license_registry_client.hasIpAttachedLicenseTerms(ip_id, license_template, license_terms_id)
            if is_attached_license_terms:
                raise ValueError(f"License terms id {license_terms_id} is already attached to the IP with id {ip_id}.")

            # Build the transaction
            transaction = self.licensing_module_client.build_attachLicenseTerms_transaction(
                ip_id, license_template, license_terms_id, {
                    'from': self.account.address,
                    'nonce': self.web3.eth.get_transaction_count(self.account.address),
                    'gas': 2000000,
                    'gasPrice': self.web3.to_wei('100', 'gwei')
                }
            )
            logger.info(f"Built transaction: {transaction}")

            # Sign the transaction
            signed_txn = self.account.sign_transaction(transaction)
            logger.info(f"Signed transaction: {signed_txn}")

            # Send the transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.info(f"Transaction hash: {tx_hash.hex()}")

            # Wait for the transaction receipt
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
            logger.info(f"Transaction receipt: {tx_receipt}")

            return {'txHash': tx_hash.hex()}
        
        except Exception as e:
            logger.error(f"Failed to attach license terms: {e}")
            return None
        
    def mintLicenseTokens(self, licensor_ip_id, license_template, license_terms_id, amount, receiver):
        try:
            logger.info(f"Starting mintLicenseTokens with licensor_ip_id: {licensor_ip_id}, license_template: {license_template}, license_terms_id: {license_terms_id}, amount: {amount}, receiver: {receiver}")

            # Check if the licensor IP is registered
            is_registered = self.ip_asset_registry_client.isRegistered(licensor_ip_id)
            if not is_registered:
                raise ValueError(f"The licensor IP with id {licensor_ip_id} is not registered.")

            # Check if the license terms exist
            is_existed = self.license_template_client.exists(license_terms_id)
            if not is_existed:
                raise ValueError(f"License terms id {license_terms_id} do not exist.")

            # Check if the license terms are attached to the IP
            is_attached_license_terms = self.license_registry_client.hasIpAttachedLicenseTerms(licensor_ip_id, license_template, license_terms_id)
            if not is_attached_license_terms:
                raise ValueError(f"License terms id {license_terms_id} is not attached to the IP with id {licensor_ip_id}.")

            # Build the transaction
            transaction = self.licensing_module_client.build_mintLicenseTokens_transaction(
                licensor_ip_id, license_template, license_terms_id, amount, receiver, '0x0000000000000000000000000000000000000000', {
                    'from': self.account.address,
                    'nonce': self.web3.eth.get_transaction_count(self.account.address),
                    'gas': 2000000,
                    'gasPrice': self.web3.to_wei('100', 'gwei')
                }
            )
            logger.info(f"Built transaction: {transaction}")

            # Sign the transaction
            signed_txn = self.account.sign_transaction(transaction)
            logger.info(f"Signed transaction: {signed_txn}")

            # Send the transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.info(f"Transaction hash: {tx_hash.hex()}")

            # Wait for the transaction receipt
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
            logger.info(f"Transaction receipt: {tx_receipt}")

            # Parse the event logs for LicenseTokensMinted
            target_logs = self._parse_tx_license_tokens_minted_event(tx_receipt)
            print("the license token id is " , target_logs)
            return {
                'txHash': tx_hash.hex(),
                'licenseTokenIds': target_logs
            }

        except Exception as e:
            logger.error(f"Failed to mint license tokens: {e}")
            return None

    def _parse_tx_license_tokens_minted_event(self, tx_receipt):
        event_signature = self.web3.keccak(text="LicenseTokenMinted(address,address,uint256)").hex()
        token_ids = []

        for log in tx_receipt['logs']:
            if log['topics'][0].hex() == event_signature:
                start_license_token_id = int(log['topics'][3].hex(), 16)
                token_ids.append(start_license_token_id)

        return token_ids if token_ids else None
    
    def getLicenseTerms(self, selectedLicenseTermsId):
        try:
            return self.license_template_client.getLicenseTerms(selectedLicenseTermsId)
        except Exception as e:
            raise ValueError(f"Failed to get license terms: {str(e)}")