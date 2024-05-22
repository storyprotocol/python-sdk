import os
from dotenv import load_dotenv
from web3 import Web3

from story_protocol_python_sdk import StoryClient
from demo_utils import get_token_id, MockERC721, MockERC20, mint_tokens


def main():
    # 1. Set up your Story Config
    load_dotenv()
    private_key = os.getenv('WALLET_PRIVATE_KEY')
    rpc_url = os.getenv('RPC_PROVIDER_URL')

    # Initialize Web3
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    if not web3.is_connected():
        raise Exception("Failed to connect to Web3 provider")

    # Set up the account with the private key
    account = web3.eth.account.from_key(private_key)

    # Create StoryClient instance
    story_client = StoryClient(web3, account, 11155111)

    # 2. Register an IP Asset
    token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
    registered_ip_asset_response = story_client.IPAsset.register(
        token_contract=MockERC721,
        token_id=token_id
    )
    print(f"Root IPA created at transaction hash {registered_ip_asset_response['txHash']}, IPA ID: {registered_ip_asset_response['ipId']}")

    # 3. Register PIL Terms
    commercial_use_params = {
        'currency': MockERC20,
        'minting_fee': 2,
        'royalty_policy': "0xAAbaf349C7a2A84564F9CC4Ac130B3f19A718E86"
    }
    register_pil_terms_response = story_client.License.registerCommercialUsePIL(
        minting_fee=commercial_use_params['minting_fee'],
        currency=commercial_use_params['currency'],
        royalty_policy=commercial_use_params['royalty_policy']
    )
    if 'txHash' in register_pil_terms_response:
        print(f"PIL Terms registered at transaction hash {register_pil_terms_response['txHash']}, License Terms ID: {register_pil_terms_response['licenseTermsId']}")
    else:
        print(f"License Terms ID: {register_pil_terms_response['licenseTermsId']}, already registered.")

    # 4. Attach License Terms to IP
    try:
        attach_license_terms_response = story_client.License.attachLicenseTerms(
            ip_id=registered_ip_asset_response['ipId'],
            license_template="0x260B6CB6284c89dbE660c0004233f7bB99B5edE7",
            license_terms_id=register_pil_terms_response['licenseTermsId']
        )
        print(f"Attached License Terms to IP at transaction hash {attach_license_terms_response['txHash']}")
    except Exception as e:
        print(f"License Terms ID {register_pil_terms_response['licenseTermsId']} already attached to this IPA.")

    #Before you mint make sure you have enough ERC20 tokens according to the minting fee above
    token_ids = mint_tokens(MockERC20, web3, account, account.address, 2)

    # 5. Mint License
    mint_license_response = story_client.License.mintLicenseTokens(
        licensor_ip_id=registered_ip_asset_response['ipId'],
        license_template="0x260B6CB6284c89dbE660c0004233f7bB99B5edE7",
        license_terms_id=register_pil_terms_response['licenseTermsId'],
        amount=1,
        receiver=account.address
    )
    print(f"License Token minted at transaction hash {mint_license_response['txHash']}, License Token IDs: {mint_license_response['licenseTokenIds']}")

    # 6. Mint derivative IP Asset using your license
    derivative_token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
    registered_ip_asset_derivative_response = story_client.IPAsset.register(
        token_contract=MockERC721,
        token_id=derivative_token_id
    )
    print(f"Derivative IPA created at transaction hash {registered_ip_asset_derivative_response['txHash']}, IPA ID: {registered_ip_asset_derivative_response['ipId']}")

    link_derivative_response = story_client.IPAsset.registerDerivativeWithLicenseTokens(
        child_ip_id=registered_ip_asset_derivative_response['ipId'],
        license_token_ids=mint_license_response['licenseTokenIds']
    )
    print(f"Derivative IPA linked to parent at transaction hash {link_derivative_response['txHash']}")

    # 7. Collect Royalty Tokens
    collect_royalty_tokens_response = story_client.Royalty.collectRoyaltyTokens(
        parent_ip_id=registered_ip_asset_response['ipId'],
        child_ip_id=registered_ip_asset_derivative_response['ipId']
    )
    print(f"Collected royalty token {collect_royalty_tokens_response['royaltyTokensCollected']} at transaction hash {collect_royalty_tokens_response['txHash']}")

    # 8. Claim Revenue
    snapshot_response = story_client.Royalty.snapshot(
        child_ip_id=registered_ip_asset_derivative_response['ipId']
    )
    print(f"Took a snapshot with ID {snapshot_response['snapshotId']} at transaction hash {snapshot_response['txHash']}")

    claim_revenue_response = story_client.Royalty.claimRevenue(
        snapshot_ids=[snapshot_response['snapshotId']],
        child_ip_id=registered_ip_asset_derivative_response['ipId'],
        token=MockERC20
    )
    print(f"Claimed revenue token {claim_revenue_response['claimableToken']} at transaction hash {claim_revenue_response['txHash']}")

if __name__ == "__main__":
    main()













# Test 1 of the license functions
try:
    licensor_ip_id = "0x431A7Cc86381F9bA437b575D3F9E931652fFbbdd"  # Replace with actual Licensor IP ID
    license_template = "0x260B6CB6284c89dbE660c0004233f7bB99B5edE7"  # Replace with actual License Template address
    license_terms_id = 2  # Replace with actual License Terms ID
    amount = 2  # Replace with the amount of license tokens to mint
    receiver = "0x14dC79964da2C08b23698B3D3cc7Ca32193d9955"  # Replace with the address of the receiver

    response = story_client.License.mintLicenseTokens(licensor_ip_id, license_template, license_terms_id, amount, receiver)
    
    print("Response: ", response)

except Exception as e:
    print(f"An error occurred: {e}")
