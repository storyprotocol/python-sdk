# src/story_protocol_python_sdk/utils/license_terms.py

from web3 import Web3

from story_protocol_python_sdk.abi.RoyaltyModule.RoyaltyModule_client import RoyaltyModuleClient

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

class LicenseTerms:
    def __init__(self, web3: Web3):
        self.web3 = web3
        self.royalty_module_client = RoyaltyModuleClient(web3)

    PIL_TYPE = {
        'NON_COMMERCIAL_REMIX': 'non_commercial_remix',
        'COMMERCIAL_USE': 'commercial_use',
        'COMMERCIAL_REMIX': 'commercial_remix'
    }

    def get_license_term_by_type(self, type, term=None):
        license_terms = {
            'transferable': True,
            'royaltyPolicy': "0x0000000000000000000000000000000000000000",
            'defaultMintingFee': 0,
            'expiration': 0,
            'commercialUse': False,
            'commercialAttribution': False,
            'commercializerChecker': "0x0000000000000000000000000000000000000000",
            'commercializerCheckerData': "0x0000000000000000000000000000000000000000",
            'commercialRevShare': 0,
            'commercialRevCeiling': 0,
            'derivativesAllowed': True,
            'derivativesAttribution': True,
            'derivativesApproval': False,
            'derivativesReciprocal': True,
            'derivativeRevCeiling': 0,
            'currency': "0x0000000000000000000000000000000000000000",
            'uri': ""
        }

        if type == self.PIL_TYPE['NON_COMMERCIAL_REMIX']:
            license_terms['commercializerCheckerData'] = "0x"
            return license_terms
        elif type == self.PIL_TYPE['COMMERCIAL_USE']:
            if not term or 'defaultMintingFee' not in term or 'currency' not in term:
                raise ValueError("DefaultMintingFee, currency are required for commercial use PIL.")
            
            if 'royaltyPolicyAddress' not in term:
                raise ValueError("royaltyPolicyAddress is required")
                
            license_terms.update({
                'defaultMintingFee': int(term['defaultMintingFee']),
                'currency': term['currency'],
                'commercialUse': True,
                'commercialAttribution': True,
                'derivativesReciprocal': False,
                'royaltyPolicy': term['royaltyPolicyAddress']
            })
            return license_terms
        else:
            if not term or 'defaultMintingFee' not in term or 'currency' not in term or 'commercialRevShare' not in term:
                raise ValueError("DefaultMintingFee, currency and commercialRevShare are required for commercial remix PIL.")
                
            if 'royaltyPolicyAddress' not in term:
                raise ValueError("royaltyPolicyAddress is required")
                
            if term['commercialRevShare'] < 0 or term['commercialRevShare'] > 100:
                raise ValueError("CommercialRevShare should be between 0 and 100.")
                
            license_terms.update({
                'defaultMintingFee': int(term['defaultMintingFee']),
                'currency': term['currency'],
                'commercialUse': True,
                'commercialAttribution': True,
                'commercialRevShare': int((term['commercialRevShare'] / 100) * 100000000),
                'derivativesReciprocal': True,
                'royaltyPolicy': term['royaltyPolicyAddress']
            })
            return license_terms

    def validate_license_terms(self, params):
        royalty_policy = params.get('royalty_policy')
        currency = params.get('currency')

        if royalty_policy != ZERO_ADDRESS:
            is_whitelisted = self.royalty_module_client.isWhitelistedRoyaltyPolicy(royalty_policy)
            if not is_whitelisted:
                raise ValueError("The royalty policy is not whitelisted.")

        if currency != ZERO_ADDRESS:
            is_whitelisted = self.royalty_module_client.isWhitelistedRoyaltyToken(currency)
            if not is_whitelisted:
                raise ValueError("The currency token is not whitelisted.")

        if royalty_policy != ZERO_ADDRESS and currency == ZERO_ADDRESS:
            raise ValueError("Royalty policy requires currency token.")

        params['default_minting_fee'] = int(params.get('default_minting_fee', 0))
        params['expiration'] = int(params.get('expiration', 0))
        params['commercial_rev_ceiling'] = int(params.get('commercial_rev_ceiling', 0))
        params['derivative_rev_ceiling'] = int(params.get('derivative_rev_ceiling', 0))

        self.verify_commercial_use(params)
        self.verify_derivatives(params)

        commercial_rev_share = params.get('commercial_rev_share', 0)
        if commercial_rev_share < 0 or commercial_rev_share > 100:
            raise ValueError("CommercialRevShare should be between 0 and 100.")
        else:
            params['commercial_rev_share'] = int((commercial_rev_share / 100) * 100000000)

        return params

    def verify_commercial_use(self, terms):
        if not terms.get('commercial_use', False):
            if terms.get('commercial_attribution'):
                raise ValueError("Cannot add commercial attribution when commercial use is disabled.")
            if terms.get('commercializer_checker') != ZERO_ADDRESS:
                raise ValueError("Cannot add commercializerChecker when commercial use is disabled.")
            if terms.get('commercial_rev_share', 0) > 0:
                raise ValueError("Cannot add commercial revenue share when commercial use is disabled.")
            if terms.get('commercial_rev_ceiling', 0) > 0:
                raise ValueError("Cannot add commercial revenue ceiling when commercial use is disabled.")
            if terms.get('derivative_rev_ceiling', 0) > 0:
                raise ValueError("Cannot add derivative revenue ceiling when commercial use is disabled.")
            if terms.get('royalty_policy') != ZERO_ADDRESS:
                raise ValueError("Cannot add commercial royalty policy when commercial use is disabled.")
        else:
            if terms.get('royalty_policy') == ZERO_ADDRESS:
                raise ValueError("Royalty policy is required when commercial use is enabled.")

    def verify_derivatives(self, terms):
        if not terms.get('derivatives_allowed', False):
            if terms.get('derivatives_attribution'):
                raise ValueError("Cannot add derivative attribution when derivative use is disabled.")
            if terms.get('derivatives_approval'):
                raise ValueError("Cannot add derivative approval when derivative use is disabled.")
            if terms.get('derivatives_reciprocal'):
                raise ValueError("Cannot add derivative reciprocal when derivative use is disabled.")
            if terms.get('derivative_rev_ceiling', 0) > 0:
                raise ValueError("Cannot add derivative revenue ceiling when derivative use is disabled.")
