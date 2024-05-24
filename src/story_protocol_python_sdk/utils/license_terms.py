# src/story_protocol_python_sdk/utils/license_terms.py

PIL_TYPE = {
    'NON_COMMERCIAL_REMIX': 'non_commercial_remix',
    'COMMERCIAL_USE': 'commercial_use',
    'COMMERCIAL_REMIX': 'commercial_remix'
}

def get_license_term_by_type(type, term=None):
    license_terms = {
        'transferable': True,
        'royaltyPolicy': "0x0000000000000000000000000000000000000000",
        'mintingFee': 0,
        'expiration': 0,
        'commercialUse': False,
        'commercialAttribution': False,
        'commercializerChecker': "0x0000000000000000000000000000000000000000",
        'commercializerCheckerData': "0x0000000000000000000000000000000000000000",
        'commercialRevShare': 0,
        'commercialRevCelling': 0,
        'derivativesAllowed': True,
        'derivativesAttribution': True,
        'derivativesApproval': False,
        'derivativesReciprocal': True,
        'derivativeRevCelling': 0,
        'currency': "0x0000000000000000000000000000000000000000",
        'uri': ""
    }

    if type == PIL_TYPE['NON_COMMERCIAL_REMIX']:
        return license_terms
    elif type == PIL_TYPE['COMMERCIAL_USE']:
        if not term or 'mintingFee' not in term or 'currency' not in term or 'royaltyPolicy' not in term:
            raise ValueError("mintingFee, currency, and royaltyPolicy are required for commercial use PIL.")
        license_terms.update({
            'mintingFee': term['mintingFee'],
            'currency': term['currency'],
            'commercialUse': True,
            'commercialAttribution': True,
            'derivativesReciprocal': False,
            'royaltyPolicy': term['royaltyPolicy']
        })
        return license_terms
    elif type == PIL_TYPE['COMMERCIAL_REMIX']:
        if not term or 'mintingFee' not in term or 'currency' not in term or 'commercialRevShare' not in term:
            raise ValueError("mintingFee, currency, and commercialRevShare are required for commercial remix PIL.")
        license_terms.update({
            'mintingFee': term['mintingFee'],
            'currency': term['currency'],
            'commercialUse': True,
            'commercialAttribution': True,
            'commercialRevShare': term['commercialRevShare'],
            'derivativesReciprocal': True,
            'royaltyPolicy': term['royaltyPolicy']
        })
        return license_terms

    return license_terms  # Return default if type is not matched
