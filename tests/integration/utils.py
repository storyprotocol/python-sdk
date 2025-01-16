from web3 import Web3
from dotenv import load_dotenv
from src.story_protocol_python_sdk.story_client import StoryClient

load_dotenv()

# Mock ERC721 contract address
MockERC721 = "0x26f69F92b324B15a14dAd93C3454f7B55Ae03504"

# Mock ERC20 contract address (same as used in TypeScript tests)
MockERC20 = "0x688abA77b2daA886c0aF029961Dc5fd219cEc3f6"

def get_story_client_in_sepolia(web3: Web3, account) -> StoryClient:
    chain_id = 11155111  # Sepolia chain ID
    return StoryClient(web3, account, chain_id)

def get_story_client_in_iliad(web3: Web3, account) -> StoryClient:
    chain_id = 1513  # Sepolia chain ID
    return StoryClient(web3, account, chain_id)

def get_story_client_in_odyssey(web3: Web3, account) -> StoryClient:
    chain_id = 1516  # Odyssey chain ID
    return StoryClient(web3, account, chain_id)

def get_story_client_in_devnet(web3: Web3, account) -> StoryClient:
    chain_id = 1315  # Odyssey chain ID
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
        'gas': 2000000
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

def getBlockTimestamp(web3):
    return (web3.eth.get_block('latest'))['timestamp']

def check_event_in_tx(web3, tx_hash: str, event_text: str) -> bool:
    tx_receipt = web3.eth.get_transaction_receipt(tx_hash)
    event_signature = web3.keccak(text=event_text).hex()

    for log in tx_receipt['logs']:
        if log['topics'][0].hex() == event_signature:
            return True

    return False
