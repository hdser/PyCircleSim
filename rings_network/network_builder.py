from typing import List, Dict, Optional
from ape import Contract, accounts
from eth_pydantic_types import HexBytes

class NetworkBuilder:
    """
    Responsible for building the initial network structure by registering humans
    and creating trust relationships.
    """
    
    def __init__(self, contract_address: str, abi_path: str):
        """
        Initialize the NetworkBuilder.
        
        Args:
            contract_address: Address of the Rings contract
            abi_path: Path to the contract ABI file
        """
        self.contract = Contract(contract_address, abi=abi_path)
        self.test_accounts = accounts.test_accounts
        self.registered_humans: Dict[str, bool] = {}
        
    def register_human(self, account, inviter=None) -> bool:
        """
        Register a human in the network.
        
        Args:
            account: Account to register
            inviter: Optional inviter account (defaults to None for self-registration)
            
        Returns:
            bool: True if registration was successful
        """
        try:
            inviter_address = inviter if inviter else "0x0000000000000000000000000000000000000000"
            receipt = self.contract.registerHuman(
                inviter_address, 
                HexBytes(0), 
                sender=account
            )
            self.registered_humans[str(account)] = True
            return True
        except Exception as e:
            print(f"Failed to register human {account}: {e}")
            return False
            
    def create_trust(self, truster, trustee, limit: int = 10000000) -> bool:
        """
        Create a trust relationship between two accounts.
        
        Args:
            truster: Account that trusts
            trustee: Account being trusted
            limit: Trust limit amount
            
        Returns:
            bool: True if trust creation was successful
        """
        try:
            receipt = self.contract.trust(trustee, limit, sender=truster)
            return True
        except Exception as e:
            print(f"Failed to create trust from {truster} to {trustee}: {e}")
            return False
            
    def build_complete_network(self) -> bool:
        """
        Build a complete network where all test accounts are registered
        and trust each other.
        
        Returns:
            bool: True if network was built successfully
        """
        # Register all accounts
        for account in self.test_accounts:
            if not self.register_human(account):
                return False
                
        # Create trust relationships
        for truster in self.test_accounts:
            for trustee in self.test_accounts:
                if truster != trustee:
                    if not self.create_trust(truster, trustee):
                        return False
                        
        return True