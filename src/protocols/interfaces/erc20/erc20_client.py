from typing import Dict, Any, Optional, List, Tuple
from ape import Contract
from src.framework.data import BaseDataCollector
from src.framework.logging import get_logger
import logging
import json

logger = get_logger(__name__, logging.DEBUG)

class ERC20Client:
    """Generic ERC20 token client that can be instantiated with any token address"""
    
    def __init__(self, 
                 address: str,  # Will be empty string
                 abi_path: str,
                 gas_limits: Optional[Dict[str, int]] = None,
                 data_collector: Optional[BaseDataCollector] = None):
        """Initialize with required parameters
        
        Args:
            address: Contract address (empty for generic ERC20)
            abi_path: Path to ABI JSON file
            gas_limits: Optional gas limits for functions
            data_collector: Optional data collector
        """
        self.address = address
        self.abi_path = abi_path
        self.data_collector = data_collector
        self.gas_limits = gas_limits or {}
        self._contracts: Dict[str, Contract] = {}
        
        # Load ABI from file
        try:
            with open(abi_path) as f:
                self.abi = json.load(f)
            logger.info(f"Successfully loaded ERC20 ABI from {abi_path}")
        except Exception as e:
            logger.error(f"Failed to load ABI from {abi_path}: {e}")
            raise

    def get_contract(self, token_address: str) -> Optional[Contract]:
        """Get or create Contract instance for token address"""
        if token_address not in self._contracts:
            try:
                logger.info(f"Creating new contract instance for token {token_address}")
                # Create contract using address and loaded ABI
                self._contracts[token_address] = Contract(
                    address=token_address,
                    abi=self.abi
                )
                logger.info(f"Successfully created contract instance for {token_address}")
            except Exception as e:
                logger.error(f"Failed to create contract for {token_address}: {e}")
                return None
        return self._contracts[token_address]

    # Basic ERC20 Functions
    def total_supply(self, token_address: str) -> int:
        """Get total token supply"""
        contract = self.get_contract(token_address)
        return contract.totalSupply()

    def balance_of(self, token_address: str, account: str) -> int:
        """Get token balance for account"""
        contract = self.get_contract(token_address)
        return contract.balanceOf(account)

    def allowance(self, token_address: str, owner: str, spender: str) -> int:
        """Get amount spender is allowed to spend on behalf of owner"""
        contract = self.get_contract(token_address)
        return contract.allowance(owner, spender)

    def transfer(self, token_address: str, to: str, amount: int, sender: str, **kwargs) -> Any:
        """Transfer tokens to an address"""
        contract = self.get_contract(token_address)
        return contract.transfer(to, amount, sender=sender, **kwargs)

    def approve(self, token_address: str, spender: str, amount: int, sender: str, **kwargs) -> Any:
        """Approve spender to spend tokens"""
        contract = self.get_contract(token_address)
        return contract.approve(spender, amount, sender=sender, **kwargs)

    def transfer_from(self, token_address: str, sender: str, recipient: str, amount: int, tx_sender: str, **kwargs) -> Any:
        """Transfer tokens from one address to another"""
        contract = self.get_contract(token_address)
        return contract.transferFrom(sender, recipient, amount, sender=tx_sender, **kwargs)

    # Extended Functions
    def name(self, token_address: str) -> str:
        """Get token name"""
        contract = self.get_contract(token_address)
        return contract.name()

    def symbol(self, token_address: str) -> str:
        """Get token symbol"""
        contract = self.get_contract(token_address)
        return contract.symbol()

    def decimals(self, token_address: str) -> int:
        """Get token decimals"""
        contract = self.get_contract(token_address)
        return contract.decimals()

    def increase_allowance(self, token_address: str, spender: str, added_value: int, sender: str, **kwargs) -> Any:
        """Increase allowance for spender"""
        contract = self.get_contract(token_address)
        return contract.increaseAllowance(spender, added_value, sender=sender, **kwargs)

    def decrease_allowance(self, token_address: str, spender: str, subtracted_value: int, sender: str, **kwargs) -> Any:
        """Decrease allowance for spender"""
        contract = self.get_contract(token_address)
        return contract.decreaseAllowance(spender, subtracted_value, sender=sender, **kwargs)

    def transfer_and_call(self, token_address: str, to: str, value: int, data: bytes, sender: str, **kwargs) -> Any:
        """Transfer tokens and call contract in one transaction"""
        contract = self.get_contract(token_address)
        return contract.transferAndCall(to, value, data, sender=sender, **kwargs)

    # Minting Functions
    def mint(self, token_address: str, to: str, amount: int, sender: str, **kwargs) -> Any:
        """Mint new tokens (if authorized)"""
        contract = self.get_contract(token_address)
        return contract.mint(to, amount, sender=sender, **kwargs)

    def finish_minting(self, token_address: str, sender: str, **kwargs) -> Any:
        """Finish minting (if authorized)"""
        contract = self.get_contract(token_address)
        return contract.finishMinting(sender=sender, **kwargs)

    # Burning Functions
    def burn(self, token_address: str, value: int, sender: str, **kwargs) -> Any:
        """Burn tokens"""
        contract = self.get_contract(token_address)
        return contract.burn(value, sender=sender, **kwargs)

    # Ownership Functions
    def owner(self, token_address: str) -> str:
        """Get token contract owner"""
        contract = self.get_contract(token_address)
        return contract.owner()

    def transfer_ownership(self, token_address: str, new_owner: str, sender: str, **kwargs) -> Any:
        """Transfer contract ownership (if authorized)"""
        contract = self.get_contract(token_address)
        return contract.transferOwnership(new_owner, sender=sender, **kwargs)

    def renounce_ownership(self, token_address: str, sender: str, **kwargs) -> Any:
        """Renounce contract ownership (if authorized)"""
        contract = self.get_contract(token_address)
        return contract.renounceOwnership(sender=sender, **kwargs)

    # Bridge Functions
    def bridge_contract(self, token_address: str) -> str:
        """Get bridge contract address"""
        contract = self.get_contract(token_address)
        return contract.bridgeContract()

    def set_bridge_contract(self, token_address: str, bridge_contract: str, sender: str, **kwargs) -> Any:
        """Set bridge contract (if authorized)"""
        contract = self.get_contract(token_address)
        return contract.setBridgeContract(bridge_contract, sender=sender, **kwargs)

    def is_bridge(self, token_address: str, address: str) -> bool:
        """Check if address is bridge"""
        contract = self.get_contract(token_address)
        return contract.isBridge(address)

    # Permit Functions
    def permit(self, token_address: str, holder: str, spender: str, value: int, deadline: int,
               v: int, r: bytes, s: bytes, sender: str, **kwargs) -> Any:
        """Execute permit function"""
        contract = self.get_contract(token_address)
        return contract.permit(holder, spender, value, deadline, v, r, s, sender=sender, **kwargs)

    def nonces(self, token_address: str, owner: str) -> int:
        """Get current nonce for owner"""
        contract = self.get_contract(token_address)
        return contract.nonces(owner)

    # Movement Functions
    def push(self, token_address: str, to: str, amount: int, sender: str, **kwargs) -> Any:
        """Push tokens to address"""
        contract = self.get_contract(token_address)
        return contract.push(to, amount, sender=sender, **kwargs)

    def pull(self, token_address: str, from_addr: str, amount: int, sender: str, **kwargs) -> Any:
        """Pull tokens from address"""
        contract = self.get_contract(token_address)
        return contract.pull(from_addr, amount, sender=sender, **kwargs)

    def move(self, token_address: str, from_addr: str, to: str, amount: int, sender: str, **kwargs) -> Any:
        """Move tokens between addresses"""
        contract = self.get_contract(token_address)
        return contract.move(from_addr, to, amount, sender=sender, **kwargs)