from typing import Optional, Dict
from ape import chain, Contract
from datetime import datetime, timedelta

class NetworkEvolver:
    """
    Responsible for evolving the network state through time by mining blocks
    and performing actions like minting.
    """
    
    def __init__(self, contract_address: str, abi_path: str):
        """
        Initialize the NetworkEvolver.
        
        Args:
            contract_address: Address of the Rings contract
            abi_path: Path to the contract ABI file
        """
        self.contract = Contract(contract_address, abi=abi_path)
        
    def advance_time(self, blocks: int, block_time: int = 12) -> bool:
        """
        Advance the chain by mining new blocks.
        
        Args:
            blocks: Number of blocks to mine
            block_time: Time between blocks in seconds
            
        Returns:
            bool: True if time advancement was successful
        """
        try:
            chain.mine(blocks)
            chain.pending_timestamp = chain.pending_timestamp + (blocks * block_time)
            return True
        except Exception as e:
            print(f"Failed to advance time: {e}")
            return False
            
    def personal_mint(self, account) -> Optional[int]:
        """
        Perform personal minting for an account.
        
        Args:
            account: Account to mint for
            
        Returns:
            Optional[int]: Amount minted or None if failed
        """
        try:
            receipt = self.contract.personalMint(sender=account)
            # Extract minted amount from receipt logs
            for log in receipt.decode_logs():
                if log.event_name == "PersonalMint":
                    return log.amount
            return None
        except Exception as e:
            print(f"Failed to mint for {account}: {e}")
            return None
            
    def mint_for_all(self, accounts) -> Dict[str, int]:
        """
        Perform minting for multiple accounts.
        
        Args:
            accounts: List of accounts to mint for
            
        Returns:
            Dict[str, int]: Mapping of account addresses to minted amounts
        """
        results = {}
        for account in accounts:
            amount = self.personal_mint(account)
            if amount is not None:
                results[str(account)] = amount
        return results