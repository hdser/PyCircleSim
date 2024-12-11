from ape import networks, accounts, Contract
from eth_pydantic_types import HexBytes

RINGS = "0x3D61f0A272eC69d65F5CFF097212079aaFDe8267"
RINGS_ABI = f"abi/{RINGS}.json"

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ZERO_BYTES = HexBytes(0)



def main():
    with networks.gnosis.mainnet_fork.use_provider("foundry") as foundry:

        contract = Contract(RINGS, abi=RINGS_ABI)

        # Register Humans
        for account in accounts.test_accounts:
            rcpt_registerHuman = contract.registerHuman(ZERO_ADDRESS,ZERO_BYTES, sender=account)
            print(rcpt_registerHuman.show_trace())

        # Create Trust
        for truster in accounts.test_accounts:
            for trustee in accounts.test_accounts:
                if truster != trustee:
                    rcpt_trust = contract.trust(trustee,10000000,sender=truster)
                    print(rcpt_trust.show_trace())