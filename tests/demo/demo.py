# tests/demo/demo.py

import os, sys
from dotenv import load_dotenv
from web3 import Web3

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from utils import get_token_id, MockERC721




#############################

from src.story_client import StoryClient





load_dotenv()
private_key = os.getenv('WALLET_PRIVATE_KEY')
rpc_url = os.getenv('RPC_PROVIDER_URL')

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(rpc_url))
if not web3.is_connected():
    raise Exception("Failed to connect to Web3 provider")

# Set up the account with the private key
account = web3.eth.account.from_key(private_key)

# Initialize the story client
story_client = StoryClient(web3, account, 11155111)

def main():
    # Step 1: Create and register parent IP asset
    # parent_token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
    # parent_ip_response = story_client.IPAsset.register(
    #     token_contract=MockERC721,
    #     token_id=parent_token_id
    # )
    # if not parent_ip_response or 'ipId' not in parent_ip_response:
    #     print("Failed to register parent IP asset")
    #     return
    parent_ip_id = "0x37792aFDbE15b57Cc59455bB1FF0Fb65f7802D38" # parent_ip_response['ipId']
    print(f"Parent IP asset registered with IP ID: {parent_ip_id}")

    # Step 2: Create and register child IP asset
    # child_token_id = get_token_id(MockERC721, story_client.web3, story_client.account)
    # child_ip_response = story_client.IPAsset.register(
    #     token_contract=MockERC721,
    #     token_id=child_token_id
    # )
    # if not child_ip_response or 'ipId' not in child_ip_response:
    #     print("Failed to register child IP asset")
    #     return
    child_ip_id = "0x3CC53f205B00dfa4DDFE5b830f230D0f6a410c42" #child_ip_response['ipId']
    print(f"Child IP asset registered with IP ID: {child_ip_id}")

    # Step 3: Register non-commercial license terms
    # license_terms_response = story_client.License.registerNonComSocialRemixingPIL()
    # if not license_terms_response or 'licenseTermsId' not in license_terms_response:
    #     print("Failed to register non-commercial license terms")
    #     return
    license_terms_id = 2 #license_terms_response['licenseTermsId']
    print(f"Non-commercial license terms registered with ID: {license_terms_id}")

    # Step 4: Attach license terms to the parent IP asset
    # license_template = "0x260B6CB6284c89dbE660c0004233f7bB99B5edE7"
    # attach_license_response = story_client.License.attachLicenseTerms(
    #     ip_id=parent_ip_id,
    #     license_template=license_template,
    #     license_terms_id=license_terms_id
    # )
    # if not attach_license_response or 'txHash' not in attach_license_response:
    #     print("Failed to attach license terms to parent IP asset")
    #     return
    # print(f"License terms attached to parent IP asset with transaction hash: {attach_license_response['txHash']}")
    print(f"License terms attached to parent IP asset with transaction hash: 0x5fa7edcc63d971242e83f1461d1301d300708a8ff109d751b3e4204c2e43b6c1")

    # Step 5: Mint license tokens
    # mint_response = story_client.License.mintLicenseTokens(
    #     licensor_ip_id=parent_ip_id,
    #     license_template=license_template,
    #     license_terms_id=license_terms_id,
    #     amount=1,  # Replace with the number of tokens to mint
    #     receiver=story_client.account.address
    # )
    # if not mint_response or 'txHash' not in mint_response:
    #     print("Failed to mint license tokens")
    #     return
    # print(f"License tokens minted with transaction hash: {mint_response['txHash']}")
    print(f"License tokens minted with transaction hash: 0x84668c79d669f2b07b475f2523ce931816a30849a8b44b97d68d9a63221f468f")

    # Assume the token ID is known or can be fetched
    license_token_ids = [1189] #mint_response['licenseTokenIds'][0]

    # Step 6: Register derivative with license tokens
    # register_derivative_response = story_client.IPAsset.registerDerivativeWithLicenseTokens(
    #     child_ip_id=child_ip_id,
    #     license_token_ids=license_token_ids
    # )
    # if not register_derivative_response or 'txHash' not in register_derivative_response:
    #     print("Failed to register derivative with license tokens")
    #     return
    # print(f"Derivative registered with license tokens with transaction hash: {register_derivative_response['txHash']}")
    print(f"Derivative registered with license tokens with transaction hash: 0x4a3a259bad26b87e41077bbcc267370b6ca13538a574dd78363af03ba6c09e1d")


if __name__ == "__main__":
    main()
