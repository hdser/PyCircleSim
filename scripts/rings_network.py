from ape import networks, accounts, Contract
from eth_pydantic_types import HexBytes

RINGS = "0x3D61f0A272eC69d65F5CFF097212079aaFDe8267"
RINGS_ABI = f"abi/{RINGS}.json"


def main():
    with networks.gnosis.mainnet_fork.use_provider("foundry") as foundry:

        print(foundry.name)
        contract = Contract(RINGS, abi=RINGS_ABI)

        for account in accounts.test_accounts:

            rcpt_registerHuman = contract.registerHuman("0x0000000000000000000000000000000000000000", HexBytes(0), sender=account)
            print(rcpt_registerHuman.show_trace())