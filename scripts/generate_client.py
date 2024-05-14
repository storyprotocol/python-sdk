import requests
import json
import os
from jinja2 import Template
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Get the API key from environment variables
api_key = os.getenv('API_KEY')
if not api_key:
    raise ValueError("Please set API_KEY in the .env file")

def fetch_abi(contract_address, api_key):
    url = f"https://api-sepolia.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}"
    response = requests.get(url)
    response_json = response.json()
    if response_json.get('status') == '1':
        abi = json.loads(response_json['result'])
        return abi
    else:
        raise Exception(f"Error fetching ABI for address {contract_address}: {response_json.get('message')}")

def fetch_proxy_implementation_address(proxy_address, api_key):
    url = "https://api-sepolia.etherscan.io/api"
    params = {
        "module": "proxy",
        "action": "eth_getStorageAt",
        "address": proxy_address,
        "position": "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc",
        "tag": "latest",
        "apikey": api_key
    }
    response = requests.get(url, params=params)
    response_json = response.json()
    print(f"Response JSON for {proxy_address}: {response_json}")  # Debugging output
    if 'result' in response_json:
        storage_value = response_json['result']
        if storage_value and storage_value != '0x':
            implementation_address = "0x" + storage_value[-40:]
            return implementation_address
        else:
            raise Exception(f"No valid implementation address found in storage for proxy {proxy_address}")
    else:
        raise Exception(f"Error fetching implementation address from storage for proxy {proxy_address}: {response_json}")

def fetch_proxy_abi(proxy_address, api_key):
    try:
        implementation_address = fetch_proxy_implementation_address(proxy_address, api_key)
        return fetch_abi(implementation_address, api_key)
    except Exception as e:
        print(f"Failed to fetch proxy implementation address for {proxy_address}: {e}")
        return None

def save_abi(abi, output_path):
    with open(output_path, 'w') as abi_file:
        json.dump(abi, abi_file, indent=2)

class_template = Template('''
import json
import os
from web3 import Web3

class {{ class_name }}:
    def __init__(self, web3: Web3, contract_address: str):
        self.web3 = web3
        abi_path = os.path.join(os.path.dirname(__file__), '{{ contract_name }}.json')
        with open(abi_path, 'r') as abi_file:
            abi = json.load(abi_file)
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
    
    {% for function in functions %}
    def {{ function.name }}(self, {{ function.inputs | join(', ') }}):
        return self.contract.functions.{{ function.name }}({{ function.inputs | join(', ') }}).transact()
    
    {% endfor %}
''')

def generate_python_classes_from_abi(abi, contract_name, functions, output_dir):
    class_name = contract_name + 'Client'  # Use the contract_name directly for proper capitalization
    
    selected_functions = []
    for item in abi:
        if item['type'] == 'function' and item['name'] in functions:
            function = {
                'name': item['name'],
                'inputs': [input['name'] for input in item['inputs']]
            }
            selected_functions.append(function)
    
    rendered_class = class_template.render(
        class_name=class_name,
        contract_name=contract_name,
        functions=selected_functions
    )
    
    output_file_path = os.path.join(output_dir, f"{contract_name}_client.py")
    with open(output_file_path, 'w') as output_file:
        output_file.write(rendered_class)
    
    print(f"Generated {class_name} class from ABI")

def main(config_path, output_dir):
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    
    for contract in config['contracts']:
        contract_name = contract['contract_name']
        contract_address = contract['contract_address']
        functions = contract['functions']
        
        abi = fetch_proxy_abi(contract_address, api_key)
        if abi:
            save_abi(abi, os.path.join(output_dir, f'{contract_name}.json'))
            generate_python_classes_from_abi(abi, contract_name, functions, output_dir)
        else:
            print(f"Skipping generation for {contract_name} due to failed ABI fetch.")

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    output_dir = os.path.join(os.path.dirname(__file__), '../src/abi')
    os.makedirs(output_dir, exist_ok=True)
    main(config_path, output_dir)
