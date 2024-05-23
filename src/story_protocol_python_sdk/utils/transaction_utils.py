# src/story_protcol_python_sdk/utils/transaction_utils.py

from web3 import Web3

def build_and_send_transaction(web3: Web3, account, client_function, *client_args, tx_options=None):
    try:
        # If tx_options is provided, use the values; otherwise, do not include them
        tx_options = tx_options or {}

        # Build the transaction options
        transaction_options = {
            'from': account.address,
            'nonce': web3.eth.get_transaction_count(account.address),
        }

        if 'gasPrice' in tx_options:
            transaction_options['gasPrice'] = web3.to_wei(tx_options['gasPrice'], 'gwei')
        if 'maxFeePerGas' in tx_options:
            transaction_options['maxFeePerGas'] = tx_options['maxFeePerGas']

        # Build the transaction using the client function and arguments
        transaction = client_function(*client_args, transaction_options)

        # Sign the transaction using the account object
        signed_txn = account.sign_transaction(transaction)

        # Send the transaction
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Wait for the transaction receipt
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)  # 5 minutes timeout

        return {
            'txHash': tx_hash.hex(),
            'txReceipt': tx_receipt
        }

    except Exception as e:
        raise e
