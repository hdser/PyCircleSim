from typing import Dict, List, Tuple
from ape import Contract
import pandas as pd

class NetworkAnalyzer:
    """
    Responsible for analyzing the current state of the network including
    balance distributions and trust relationships.
    """
    
    def __init__(self, contract_address: str, abi_path: str):
        """
        Initialize the NetworkAnalyzer.
        
        Args:
            contract_address: Address of the Rings contract
            abi_path: Path to the contract ABI file
        """
        self.contract = Contract(contract_address, abi=abi_path)
        
    def get_balance(self, account) -> int:
        """
        Get the current balance of an account.
        
        Args:
            account: Account to check balance for (address string starting with 0x)
            
        Returns:
            int: Current balance
            
        Note:
            The token ID for an account is derived directly from its address value.
            In Solidity: uint256(uint160(address)) 
            In Python: int(address, 16)
        """
        try:
            # Convert the address string to its numerical value
            # This matches the Solidity toTokenId() function's behavior
            token_id = int(str(account), 16)
            
            # Call balanceOf with both the original account address and the derived token ID
            return self.contract.balanceOf(account, token_id)
        except Exception as e:
            print(f"Failed to get balance for {account}: {e}")
            return 0
                
    def get_trust_status(self, truster, trustee) -> bool:
        """
        Check if one account trusts another.
        
        Args:
            truster: Account that might trust
            trustee: Account that might be trusted
            
        Returns:
            bool: True if trust relationship exists
        """
        try:
            return self.contract.isTrusted(truster, trustee)
        except Exception as e:
            print(f"Failed to check trust status between {truster} and {trustee}: {e}")
            return False
            
    def analyze_network(self, accounts) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Perform comprehensive network analysis.
        
        Args:
            accounts: List of accounts to analyze
            
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Balance and trust matrices
        """
        # Create balance DataFrame
        balances = {}
        for account in accounts:
            balances[str(account)] = self.get_balance(account)
        balance_df = pd.DataFrame(balances.items(), columns=['Account', 'Balance'])
        
        # Create trust matrix
        trust_data = []
        for truster in accounts:
            trust_row = []
            for trustee in accounts:
                trust_row.append(self.get_trust_status(truster, trustee))
            trust_data.append(trust_row)
            
        trust_df = pd.DataFrame(
            trust_data, 
            columns=[str(a) for a in accounts],
            index=[str(a) for a in accounts]
        )
        
        return balance_df, trust_df