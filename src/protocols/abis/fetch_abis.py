#!/usr/bin/env python3

import os
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv() 

def fetch_abi(address: str, api_key: str) -> list:
    """
    Fetch the ABI for a given contract address from GnosisScan using the provided API key.
    
    :param address: The contract address (e.g., '0x123abc...')
    :param api_key: Your GnosisScan API key
    :return: A list representing the ABI (parsed JSON)
    """
    base_url = "https://api.gnosisscan.io/api"
    params = {
        "module": "contract",
        "action": "getabi",
        "address": address,
        "apikey": api_key
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check for success from the API
        if data.get("status") == "1":
            # Parse the ABI, which comes in as a JSON string
            contract_abi = json.loads(data["result"])
            return contract_abi
        else:
            # The API might return an error, e.g. "NOTOK"
            error_message = data.get("result", "Unknown error from GnosisScan")
            raise ValueError(f"Error fetching ABI for {address}: {error_message}")

    except requests.exceptions.RequestException as e:
        # Handle connection errors, timeouts, etc.
        raise RuntimeError(f"Network error while fetching ABI for {address}: {e}")


def save_abi_to_file(address: str, abi: list) -> None:
    """
    Save the ABI as a JSON file named {address}.json, pretty-printed.
    
    :param address: The contract address
    :param abi: The ABI (list of dicts)
    """
    filename = f"{address}.json"
    with open(filename, "w") as f:
        json.dump(abi, f, indent=4)
    print(f"Saved ABI for {address} to {filename}")


def main():
    """
    Main execution flow:
    1. Read API key from environment variable.
    2. Define or retrieve a list of contract addresses.
    3. For each address, fetch the ABI and save to JSON.
    4. Sleep 0.2s between calls (5 requests/sec) to avoid rate-limit issues.
    """
    # 1. Read API key
    api_key = os.getenv("GNOSISSCAN_API_KEY")
    if not api_key:
        print("Error: No API key found in environment variable GNOSISSCAN_API_KEY.")
        return

    # 2. List of contract addresses to fetch
    addresses = [
        "0x045d7b6374C14b250eC05b064156465c71EE99B1",
        "0x7213Fa0F97881D2DF0aC8A146E698B3770dcAac4",
        "0xc27cDd9a22943Da7906a355346073070fE2458D8",
        "0x79Cbc9C7077dF161b92a745345A6Ade3fC626A60",
        "0x3545955Bc3900bda704261e4991f239BBd99ecE5",
        "0xF47c14035e23E35D551F7d3d96Abbc028143CC11",
        "0x28141b6743c8569Ad8B20Ac09046Ba26F9Fb1c90"
    ]

    # 3. Fetch and save each address's ABI
    for addr in addresses:
        try:
            print(f"Fetching ABI for {addr}...")
            abi = fetch_abi(addr, api_key)
            save_abi_to_file(addr, abi)
            
            # 4. Rate-limit: 5 requests per second => sleep 0.2s
            time.sleep(0.2)
        
        except Exception as e:
            print(f"Failed to process address {addr}: {e}")


if __name__ == "__main__":
    main()
