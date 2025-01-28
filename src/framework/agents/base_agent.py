from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import random
import secrets
from eth_account import Account
from ape import networks
from .profile import AgentProfile
from src.framework.data import BaseDataCollector
from src.framework.logging import get_logger
from dataclasses import dataclass
import logging

logger = get_logger(__name__,logging.INFO)

@dataclass
class BalanceUpdate:
    contract: str
    account: str 
    balance: int
    timestamp: datetime
    block: int

@dataclass
class ActionState:
    """Track state for a specific action sequence"""
    sequence_index: int = 0
    remaining_repeats: int = 0
    last_block: int = 0
    daily_count: int = 0

class BaseAgent:
    """
    Base agent class providing core functionality for network simulation.
    This class should remain protocol-agnostic and contain only essential features.
    Specific behaviors should be implemented in protocol-specific agent classes.
    """
    
    def __init__(self, 
                 agent_id: str, 
                 profile: AgentProfile, 
                 data_collector: Optional['BaseDataCollector'] = None):
        """Initialize base agent with core attributes"""
        self.agent_id = agent_id
        self.profile = profile
        self.collector = data_collector
        
        # Initialize dictionaries first
        self.accounts: Dict[str, bytes] = {}  # address -> private_key
        self.action_counts: Dict[str, Dict[str, int]] = {}  # address -> {action_name -> count}
        
        # Generic state management
        self.state: Dict[str, Any] = {
            'balances-ERC20': {},  # {account: {contract: balance}}
            'balances-history': [],  # List of BalanceUpdate
            'isGroup': []
        }
        
        # Action tracking
        self.action_history: List[Tuple[str, str, int]] = []  # List of (action, address, block)
        self.address_states: Dict[str, Dict[str, ActionState]] = {}  # address -> {action -> state}
        self.sequence_states: Dict[str, ActionState] = {} # Per-address sequence state
        
        self.creation_time = datetime.now()

        # Initialize with preset addresses if provided
        if self.profile.preset_addresses:
            for address in self.profile.preset_addresses:
                self.accounts[address] = bytes()  # Empty bytes since we'll impersonate
                self.action_counts[address] = {}  # Initialize action counts for this address
                self._initialize_address_state(address)

    def _initialize_address_state(self, address: str):
        """Initialize tracking state for a new address"""
        # Initialize action states
        self.address_states[address] = {
            action: ActionState()
            for action in self.profile.action_configs.keys()
        }
        
        # Initialize sequence state if needed
        if self.profile.actions_sequence:
            self.sequence_states[address] = ActionState()
            # Set initial repeats for first action
            action, repeats = self.profile.actions_sequence[0]
            self.sequence_states[address].remaining_repeats = repeats
        
    def create_account(self, preset_addr: Optional[str]=None) -> Tuple[str, bytes]:
        """Create a new blockchain account or use preset addresses"""
        try:
            if preset_addr:
                self.accounts[preset_addr] = bytes()
                self._initialize_address_state(preset_addr)
                # Initialize action counts for this address
                self.action_counts[preset_addr] = {}
                logger.debug(f"Using preset address {preset_addr} for agent {self.agent_id}")
                return preset_addr, bytes()
            
            private_key = secrets.token_bytes(32)
            account = Account.from_key(private_key)
            
            # Store account info
            self.accounts[account.address] = private_key
            self._initialize_address_state(account.address)
            
            # Fund account
            networks.provider.set_balance(account.address, int(10000e18))
            
            # Record if collector exists
            if self.collector and self.collector.current_run_id:
                self.collector.record_agent_address(
                    self.agent_id,
                    account.address,
                    is_primary=(len(self.accounts) == 1)
                )
                
            # Initialize action counts for new address
            self.action_counts[account.address] = {}

            return account.address, private_key
            
        except Exception as e:
            logger.error(f"Failed to create account: {e}")
            raise

    def _get_next_sequence_action(self, address: str, current_block: int) -> Optional[Tuple[str, str, Dict]]:
        """Get next action in sequence for an address"""
        if not self.profile.actions_sequence:
            return None
            
        sequence_state = self.sequence_states[address]
        
        # If we've completed current action's repeats
        if sequence_state.remaining_repeats <= 0:
            # Move to next action in sequence
            sequence_state.sequence_index = (sequence_state.sequence_index + 1) % len(self.profile.actions_sequence)
            action_name, repeats = self.profile.actions_sequence[sequence_state.sequence_index]
            sequence_state.remaining_repeats = repeats
        
        # Get current action details
        action_name, _ = self.profile.actions_sequence[sequence_state.sequence_index]
        
        # Check if we can perform this action
        if not self.can_perform_action(action_name, current_block, {}):
            return None
            
        # Update state and get parameters
        sequence_state.remaining_repeats -= 1
        sequence_state.last_block = current_block
        
        
        params = self._get_base_params(action_name, address)
        return action_name, address, params
            
    def get_accounts(self) -> List[str]:
        """Get all controlled addresses"""
        return list(self.accounts.keys())
        
    def get_random_account(self) -> Optional[Tuple[str, bytes]]:
        """Get a random controlled account"""
        if not self.accounts:
            return None
        address = random.choice(list(self.accounts.keys()))
        return address, self.accounts[address]
        
    def select_action(self, current_block: int, network_state: Dict[str, Any]) -> Tuple[Optional[str], str, Dict]:
        """
        Select an action based on profile configuration and current state
        Returns: (action_name, acting_address, params) or (None, "", {})
        """
        
        # If we have a sequence defined, use it
        if self.profile.actions_sequence:
            # Try each address until we find a valid action
            for address in self.accounts:
                result = self._get_next_sequence_action(address, current_block)
                if result:
                    return result
            return None, "", {}
        
        # First, filter out actions that have reached max_executions for any address
        available_actions = []
        for action_name, config in self.profile.action_configs.items():
            for address in self.accounts:
                # Get current count for this action and address
                current_count = self.action_counts.get(address, {}).get(action_name, 0)
                
                # Skip if hit max_executions
                if config.max_executions is not None and current_count >= config.max_executions:
                    logger.debug(f"Skipping {action_name} for {address}: reached max executions {current_count}/{config.max_executions}")
                    continue
                    
                action_state = self.address_states[address].get(action_name)
                if action_state and self._can_perform_action(action_name, address, current_block):
                    available_actions.append((action_name, address, config.probability))

        if not available_actions:
            return None, "", {}
            
        # Weight selection by probability
        action_weights = [x[2] for x in available_actions]
        selected_action = random.choices(available_actions, weights=action_weights)[0]
        action_name, address, _ = selected_action
        
        # Double-check max_executions before returning
        config = self.profile.get_action_config(action_name)
        current_count = self.action_counts.get(address, {}).get(action_name, 0)
        if config.max_executions is not None and current_count >= config.max_executions:
            logger.debug(f"Cannot select {action_name} for {address}: reached max executions {current_count}/{config.max_executions}")
            return None, "", {}
        
        logger.debug(f"Selected action {action_name} for {address} (count: {current_count})")
        
        # Get parameters
        params = self._get_base_params(action_name, address)
        return action_name, address, params
    
    def _can_perform_action(self, action_name: str, address: str, current_block: int) -> bool:
        """Check if an action can be performed by an address"""
        action_config = self.profile.get_action_config(action_name)
        if not action_config:
            return False
            
        # Check max executions first
        current_count = self.action_counts.get(address, {}).get(action_name, 0)
        if action_config.max_executions is not None and current_count >= action_config.max_executions:
            return False
                
        action_state = self.address_states[address].get(action_name)
        if not action_state:
            return False
                
        # Check cooldown
        blocks_passed = current_block - action_state.last_block
        if blocks_passed < action_config.cooldown_blocks:
            return False
                
        return True
            
    def can_perform_action(self, action_name: str, current_block: int, network_state: Dict) -> bool:
        """Check if action can be performed based on constraints"""
        try:
            action = self.profile.get_action_config(action_name)
            if not action:
                return False
                
            # For each address, check if action can be performed
            return any(
                self._can_perform_action(action_name, addr, current_block)
                for addr in self.accounts
            )
            
        except Exception as e:
            logger.error(f"Error checking action eligibility: {e}")
            return False
            
    def _get_base_params(self, action_name: str, acting_address: str) -> Dict:
        """Get basic parameters needed for any action"""
        action = self.profile.get_action_config(action_name)
        if not action:
            return {}
            
        return {
            'sender': acting_address,
        }
        
    def record_action(self, action_name: str, address: str, block_number: int, success: bool):
        """Record action execution with enhanced tracking"""
        if success:
            # Update action state
            if address in self.address_states and action_name in self.address_states[address]:
                action_state = self.address_states[address][action_name]
                action_state.last_block = block_number
                action_state.daily_count += 1
            
                # Only update counts if action was successful
                if address not in self.action_counts:
                    self.action_counts[address] = {}
                self.action_counts[address][action_name] = self.action_counts[address].get(action_name, 0) + 1
            
            # Record in history
            self.action_history.append((action_name, address, block_number))
                
    def update_state(self, key: str, value: Any):
        """Update agent's internal state"""
        self.state[key] = value
        
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get value from agent's state"""
        return self.state.get(key, default)
    
    def update_balance(self, account: str, contract: str, balance: int, 
                      timestamp: datetime, block: int) -> None:
        """Update the ERC20 balance for an account/contract pair"""
        # Skip if not our account
        if account not in self.accounts:
            return
            
        # Initialize if needed
        if account not in self.state['balances-ERC20']:
            self.state['balances-ERC20'][account] = {}
        
        # Only store if non-zero or updating existing entry
        if balance > 0 or contract in self.state['balances-ERC20'][account]:
            self.state['balances-ERC20'][account][contract] = balance
            
            # Add to history
            update = BalanceUpdate(
                contract=contract,
                account=account,
                balance=balance,
                timestamp=timestamp,
                block=block
            )
            self.state['balances-history'].append(update)

    def get_last_balance(self, account: str, contract: str) -> Optional[int]:
        """Get last recorded balance for account/contract pair"""
        return self.state['balances-ERC20'].get(account, {}).get(contract)

    def get_balance_history(self, account: str = None, 
                          contract: str = None) -> List[BalanceUpdate]:
        """Get balance update history, optionally filtered"""
        history = self.state['balances-history']
        
        if account:
            history = [h for h in history if h.account == account]
        if contract:
            history = [h for h in history if h.contract == contract]
            
        return history
    