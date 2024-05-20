from web3 import Web3
from dotenv import load_dotenv
from src.story_client import StoryClient

load_dotenv()

# Mock ERC721 contract address
MockERC721 = "0x7ee32b8B515dEE0Ba2F25f612A04a731eEc24F49"

# Mock ERC20 contract address (same as used in TypeScript tests)
MockERC20 = "0xB132A6B7AE652c974EE1557A3521D53d18F6739f"

def get_story_client_in_sepolia(web3: Web3, account) -> StoryClient:
    chain_id = 11155111  # Sepolia chain ID
    return StoryClient(web3, account, chain_id)

def get_token_id(nft_contract, web3, account):
    contract_abi = [
        {
            "inputs": [{"internalType": "address", "name": "to", "type": "address"}],
            "name": "mint",
            "outputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]

    contract = web3.eth.contract(address=nft_contract, abi=contract_abi)
    transaction = contract.functions.mint(account.address).build_transaction({
        'from': account.address,
        'nonce': web3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'gasPrice': web3.to_wei('300', 'gwei')
    })
    signed_txn = account.sign_transaction(transaction)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    logs = tx_receipt['logs']
    if logs[0]['topics'][3]:
        return int(logs[0]['topics'][3].hex(), 16)

def mint_tokens(erc20_contract_address, web3, account, to_address, amount):
    contract_abi = [
        {
            "inputs": [
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "amount", "type": "uint256"}
            ],
            "name": "mint",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]

    contract = web3.eth.contract(address=erc20_contract_address, abi=contract_abi)
    transaction = contract.functions.mint(to_address, amount).build_transaction({
        'from': account.address,
        'nonce': web3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'gasPrice': web3.to_wei('300', 'gwei')
    })
    
    signed_txn = account.sign_transaction(transaction)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    
    return tx_receipt

def approve(erc20_contract_address, web3, account, spender_address, amount):
    erc20_contract_address = web3.to_checksum_address(erc20_contract_address)
    spender_address = web3.to_checksum_address(spender_address)

    contract_abi = [
        {
            "inputs": [
                {"internalType": "address", "name": "spender", "type": "address"},
                {"internalType": "uint256", "name": "value", "type": "uint256"}
            ],
            "name": "approve",
            "outputs": [
                {"internalType": "bool", "name": "", "type": "bool"}
            ],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]

    contract = web3.eth.contract(address=erc20_contract_address, abi=contract_abi)
    transaction = contract.functions.approve(spender_address, amount).build_transaction({
        'from': account.address,
        'nonce': web3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'gasPrice': web3.to_wei('300', 'gwei')
    })
    
    signed_txn = account.sign_transaction(transaction)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    
    return tx_receipt
