import time

from web3 import Web3

TRANSACTION_TIMEOUT = 300
REPLACEMENT_UNDERPRICED_RETRY_DELAY = 5
REPLACEMENT_GAS_BUMP_RATIO = 1.2


def _validate_nonce(nonce) -> int:
    """Validate and return nonce. Raises ValueError if invalid."""
    if not isinstance(nonce, int) or nonce < 0:
        raise ValueError(
            f"Invalid nonce value: {nonce}. Nonce must be a non-negative integer."
        )
    return nonce


def _get_transaction_options(
    web3: Web3,
    account,
    tx_options: dict,
    *,
    nonce_override: int | None = None,
    bump_gas: bool = False,
) -> dict:
    """
    Build the transaction options dict (from, nonce, value, gas).
    Used for both encodedTxDataOnly and send path.
    """
    opts = {"from": account.address}

    # Nonce: use override (retry), explicit from tx_options, or fetch from chain
    if nonce_override is not None:
        opts["nonce"] = nonce_override
    elif "nonce" in tx_options:
        opts["nonce"] = _validate_nonce(tx_options["nonce"])
    else:
        opts["nonce"] = web3.eth.get_transaction_count(account.address)

    if "value" in tx_options:
        opts["value"] = tx_options["value"]

    # Gas: bump for replacement, or use tx_options
    if bump_gas:
        try:
            opts["gasPrice"] = int(
                web3.eth.gas_price * REPLACEMENT_GAS_BUMP_RATIO
            )
        except Exception:
            opts["gasPrice"] = web3.to_wei(2, "gwei")
    else:
        if "gasPrice" in tx_options:
            opts["gasPrice"] = web3.to_wei(tx_options["gasPrice"], "gwei")
        if "maxFeePerGas" in tx_options:
            opts["maxFeePerGas"] = tx_options["maxFeePerGas"]

    # Gas limit: use explicit gas if provided to avoid estimation
    if "gas" in tx_options:
        opts["gas"] = tx_options["gas"]

    return opts


def _is_retryable_send_error(exc: Exception) -> bool:
    """True if we should retry send (same nonce, higher gas)."""
    msg = str(exc).lower()
    return (
        "replacement transaction underpriced" in msg
        or "nonce too low" in msg
    )


def _send_one(
    web3: Web3,
    account,
    client_function,
    client_args: tuple,
    tx_options: dict,
    transaction_options: dict,
) -> dict:
    """Build, sign, send one transaction. No retry."""
    transaction = client_function(*client_args, transaction_options)
    signed_txn = account.sign_transaction(transaction)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

    if not tx_options.get("wait_for_receipt", True):
        return {"tx_hash": tx_hash.hex()}

    timeout = tx_options.get("timeout", TRANSACTION_TIMEOUT)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
    return {"tx_hash": tx_hash.hex(), "tx_receipt": tx_receipt}


def build_and_send_transaction(
    web3: Web3,
    account,
    client_function,
    *client_args,
    tx_options: dict | None = None,
) -> dict:
    """
    Builds and sends a transaction using the provided client function and arguments.

    On "replacement transaction underpriced" or "nonce too low", retries once
    after a short delay with the same nonce and higher gas.

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
    tx_options = tx_options or {}
    client_args = tuple(client_args)

    # Encode-only path: build options and return encoded data, no send
    if tx_options.get("encodedTxDataOnly"):
        opts = _get_transaction_options(web3, account, tx_options)
        encoded = client_function(*client_args, opts)
        return {"encodedTxData": encoded}

    # Send path: optionally retry once with same nonce + higher gas
    used_nonce = None
    last_error = None

    for attempt in range(2):
        opts = _get_transaction_options(
            web3,
            account,
            tx_options,
            nonce_override=used_nonce,
            bump_gas=(attempt == 1),
        )
        if used_nonce is None:
            used_nonce = opts["nonce"]

        try:
            return _send_one(
                web3,
                account,
                client_function,
                client_args,
                tx_options,
                opts,
            )
        except Exception as e:
            last_error = e
            if not _is_retryable_send_error(e):
                raise
            if attempt == 0:
                time.sleep(REPLACEMENT_UNDERPRICED_RETRY_DELAY)

    raise last_error
