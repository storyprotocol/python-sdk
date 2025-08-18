from web3 import Web3

TRANSACTION_TIMEOUT = 300


def build_and_send_transaction(
    web3: Web3,
    account,
    client_function,
    *client_args,
    tx_options: dict | None = None,
) -> dict:
    """
    Builds and sends a transaction using the provided client function and arguments.

    :param web3 Web3: An instance of Web3.
    :param account: The account to use for signing the transaction.
    :param client_function: The client function to build the transaction.
    :param client_args: Arguments to pass to the client function.
    :param tx_options dict: Optional transaction options. Can include:
                            - 'nonce': Custom nonce value (int). If not provided, nonce will be fetched from web3.eth.get_transaction_count().
                            - 'wait_for_receipt': Whether to wait for transaction receipt (bool, default True).
                            - 'timeout': Custom timeout in seconds for waiting for receipt (int/float, default TRANSACTION_TIMEOUT).
                            - 'encodedTxDataOnly': If True, returns encoded transaction data without sending.
                            - 'value': Transaction value in wei.
                            - 'gasPrice': Gas price in gwei.
                            - 'maxFeePerGas': Max fee per gas in wei.
    :return dict: A dictionary with the transaction hash and optionally receipt (if wait_for_receipt is True),
                  or encoded data if encodedTxDataOnly is True.
    :raises Exception: If there is an error during the transaction process.
    """
    try:
        tx_options = tx_options or {}

        transaction_options = {
            "from": account.address,
        }

        if "nonce" in tx_options:
            nonce = tx_options["nonce"]
            if not isinstance(nonce, int) or nonce < 0:
                raise ValueError(
                    f"Invalid nonce value: {nonce}. Nonce must be a non-negative integer."
                )
            transaction_options["nonce"] = nonce
        else:
            transaction_options["nonce"] = web3.eth.get_transaction_count(
                account.address
            )

        if "value" in tx_options:
            transaction_options["value"] = tx_options["value"]

        if "gasPrice" in tx_options:
            transaction_options["gasPrice"] = web3.to_wei(
                tx_options["gasPrice"], "gwei"
            )
        if "maxFeePerGas" in tx_options:
            transaction_options["maxFeePerGas"] = tx_options["maxFeePerGas"]

        transaction = client_function(*client_args, transaction_options)

        if tx_options.get("encodedTxDataOnly"):
            return {"encodedTxData": transaction}

        signed_txn = account.sign_transaction(transaction)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

        wait_for_receipt = tx_options.get("wait_for_receipt", True)

        if wait_for_receipt:
            timeout = tx_options.get("timeout", TRANSACTION_TIMEOUT)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            return {"tx_hash": tx_hash.hex(), "tx_receipt": tx_receipt}
        else:
            return {"tx_hash": tx_hash.hex()}

    except Exception as e:
        raise e
