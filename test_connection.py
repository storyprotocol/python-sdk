#!/usr/bin/env python3

import os
import sys
import requests
from dotenv import load_dotenv
from web3 import Web3

def test_rpc_connection():
    load_dotenv()
    rpc_url = os.getenv('RPC_PROVIDER_URL')
    
    print(f"\n1. Testing basic HTTP connection to {rpc_url}")
    try:
        # First test basic HTTP connectivity
        response = requests.post(rpc_url, 
            json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"HTTP Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")  # Print first 200 chars of response
    except Exception as e:
        print(f"HTTP connection error: {str(e)}")
    
    print("\n2. Testing Web3 connection")
    try:
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        connected = web3.is_connected()
        print(f"Web3 connected: {connected}")
        
        if connected:
            print(f"Chain ID: {web3.eth.chain_id}")
            print(f"Latest block: {web3.eth.block_number}")
    except Exception as e:
        print(f"Web3 connection error: {str(e)}")
    
    print("\n3. Testing network metadata")
    try:
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        network_version = web3.net.version
        listening = web3.net.listening
        peer_count = web3.net.peer_count
        print(f"Network version: {network_version}")
        print(f"Node listening: {listening}")
        print(f"Peer count: {peer_count}")
    except Exception as e:
        print(f"Network metadata error: {str(e)}")

if __name__ == "__main__":
    test_rpc_connection()