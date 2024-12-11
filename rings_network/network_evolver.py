from typing import Optional, Dict
from ape import chain, Contract
from datetime import datetime, timedelta
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rings_simulation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NetworkEvolver:
    """
    Responsible for evolving the network state through time by mining blocks
    and performing actions like minting.
    """
    
    def __init__(self, contract_address: str, abi_path: str, collector=None):
        """
        Initialize the NetworkEvolver with a contract and optional data collector.
        
        Args:
            contract_address: Address of the Rings contract
            abi_path: Path to the contract ABI file
            collector: Optional CirclesDataCollector to record network changes
        """
        self.contract = Contract(contract_address, abi=abi_path)
        self.collector = collector
        
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
        Perform personal minting for an account and record the resulting balance change.
        
        We need to handle the blockchain's native 18-decimal representation consistently
        throughout our recording process.
        """
        try:
            # Get balance directly from the contract without scaling yet
            previous_balance = self.contract.balanceOf(account, int(str(account), 16))
            
            # Perform the mint operation
            receipt = self.contract.personalMint(sender=account)
            
            # Extract minted amount from receipt logs
            for log in receipt.decode_logs():
                if log.event_name == "PersonalMint":
                    minted_amount = log.amount
                    
                    # Record the balance change using the full precision numbers
                    self.collector.record_balance_change(
                        account=str(account),
                        token_id=str(account),
                        block_number=chain.blocks.head.number,
                        timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp),
                        previous_balance=previous_balance,
                        new_balance=previous_balance + minted_amount, 
                        tx_hash=receipt.txn_hash, 
                        event_type="MINT"
                    )
                    
                    # Return the amount for informational purposes
                    return minted_amount
                
        except Exception as e:
            logger.error(f"Failed to mint for {account}: {e}")
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