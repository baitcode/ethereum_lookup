import functools
import json
import argparse
from etherscan import Etherscan

parser = argparse.ArgumentParser(
    prog='GetEthAddressInfo',
    description='Fetches etherium address information and outputs it as formatted json object',
)
parser.add_argument('apiKey', help="etherscan api key")           
parser.add_argument('address', help="etheirium address to check")           

args = parser.parse_args()

ETHERSCAN_API_URL = "https://api.etherscan.io/api"
ETHERSCAN_API_KEY = args.apiKey
BLOCKS_TO_LOOKUP_COUNT = 1000
creator_address = args.address
eth = Etherscan(ETHERSCAN_API_KEY)

def wrap_with_default(f, default):
    
    @functools.wraps(f)
    def wrapper():
        try:
            return f()
        except Exception as e:
            return default
    
    return wrapper
    
last_block_number = int(eth.get_proxy_block_number(), 16)
contract_source = wrap_with_default(eth.get_contract_source_code(address=creator_address), None)()

normal_tx = wrap_with_default(
    lambda: eth.get_normal_txs_by_address(
        address=creator_address, 
        startblock=last_block_number - BLOCKS_TO_LOOKUP_COUNT, 
        endblock=last_block_number,
        sort="asc"
    ), 
    []
)()

internal_tx = wrap_with_default(
    lambda: eth.get_internal_txs_by_address(
        address=creator_address,
        startblock=last_block_number - BLOCKS_TO_LOOKUP_COUNT, 
        endblock=last_block_number,
        sort="asc"
    ), 
    []
)()

data = {
    "is_contract": contract_source != None,
    "contract_source": contract_source,
    "balance": eth.get_eth_balance(address=creator_address),
    "normal_tx": normal_tx,
    "internal_tx": internal_tx,
}

print(json.dumps(
    data,
    indent=4, 
    sort_keys=True
))
