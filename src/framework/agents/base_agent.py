from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import random
import secrets
from dataclasses import dataclass
from eth_account import Account
from ape import networks
from .profile import AgentProfile
from src.framework.data import BaseDataCollector
from src.framework.logging import get_logger
import logging

logger = get_logger(__name__, logging.INFO)


@dataclass
class BalanceUpdate:
    """Records a balance update for an account"""
    contract: str
    account: str 
    balance: int
    timestamp: datetime
    block: int

class BaseAgent:
    def __init__(self, 
                 agent_id: str, 
                 profile: AgentProfile, 
                 data_collector: Optional['BaseDataCollector'] = None):
        self.agent_id = agent_id
        self.profile = profile
        self.collector = data_collector
        
        # Account management
        self.accounts: Dict[str, bytes] = {}  # address -> private_key
        
        # Action tracking - enhanced for sequences
        self.action_states: Dict[str, Dict[str, Dict]] = {}  # address -> {action -> state}
        self.sequence_states: Dict[str, Dict] = {}  # address -> sequence state
        self.last_action_blocks: Dict[str, Dict[str, int]] = {}  # address -> {action -> block}
        
        # State tracking
        self.state: Dict[str, Any] = {
            'balances-ERC20': {},
            'balances-history': [],
            'isGroup': []
        }
        
        self.creation_time = datetime.now()

        # Initialize with preset addresses if provided
        if self.profile.preset_addresses:
            for address in self.profile.preset_addresses:
                self._initialize_address(address, preset=True)

    def _initialize_address(self, address: str, preset: bool = False):
        """Initialize tracking state for an address"""
        if preset:
            self.accounts[address] = bytes()
        
        # Initialize action states
        self.action_states[address] = {}
        self.last_action_blocks[address] = {}
        
        # Initialize action tracking
        for action_name, config in self.profile.action_configs.items():
            self.action_states[address][action_name] = {
                'cooldown_block': 0,
                'executions': 0
            }
            self.last_action_blocks[address][action_name] = 0

        # Initialize sequence states
        self.sequence_states[address] = {
            seq.name: {'current_step': 0, 'executions': 0}
            for seq in self.profile.sequences
        }

    def create_account(self, preset_addr: Optional[str] = None) -> Tuple[str, bytes]:
        """Create a new blockchain account or use preset address"""
        try:
            if preset_addr:
                self._initialize_address(preset_addr, preset=True)
                networks.provider.set_balance(preset_addr, int(10000e18))
                return preset_addr, bytes()
            
            # Create new account
            private_key = secrets.token_bytes(32)
            account = Account.from_key(private_key)
            address = account.address
            
            # Initialize tracking state
            self._initialize_address(address)
            self.accounts[address] = private_key
            
            # Fund account
            networks.provider.set_balance(address, int(10000e18))
            
            # Record in collector
            if self.collector and self.collector.current_run_id:
                self.collector.record_agent_address(
                    self.agent_id,
                    address,
                    is_primary=(len(self.accounts) == 1)
                )
                
            return address, private_key
            
        except Exception as e:
            logger.error(f"Failed to create account: {e}")
            raise

    def select_action(self, current_block: int, network_state: Dict[str, Any]) -> Tuple[Optional[str], str, Dict]:
        """Enhanced action selection with sequence support"""
        # First check if we should execute a sequence
        if self.profile.should_execute_sequence():
            action = self._select_sequence_action(current_block)
            if action:
                return action

        # Fall back to individual action selection
        return self._select_individual_action(current_block)

    def _select_sequence_action(self, current_block: int) -> Optional[Tuple[str, str, Dict]]:
        """Select next action from available sequences"""
        for sequence in self.profile.sequences:
            # Try each address until we find a valid execution
            for address in self.accounts:
                # Skip if sequence can't be executed for this address
                if not self.profile.can_execute_sequence(sequence, address):
                    continue

                # Get current step
                current_step = sequence.steps[sequence.current_step_index]
                if not self.profile.can_execute_step(current_step):
                    continue

                # Check cooldown
                last_block = self.last_action_blocks[address].get(current_step.action, 0)
                if current_block - last_block < current_step.repeat:
                    continue

                # Prepare parameters
                params = self._prepare_action_params(
                    current_step.action,
                    address,
                    current_step.constraints,
                    current_step.batchcall
                )
                if not params:
                    continue

                # Update tracking
                self.profile.update_sequence_progress(sequence, current_step)
                self.last_action_blocks[address][current_step.action] = current_block

                return current_step.action, address, params

        return None

    def _select_individual_action(self, current_block: int) -> Tuple[Optional[str], str, Dict]:
        """Select an individual action based on probabilities"""
        # Get available actions
        available_actions = []
        for action_name, config in self.profile.action_configs.items():
            for address in self.accounts:
                # Skip if max executions reached
                if (config.max_executions is not None and 
                    self.action_states[address][action_name]['executions'] >= config.max_executions):
                    continue
                    
                # Check cooldown
                last_block = self.last_action_blocks[address].get(action_name, 0)
                if current_block - last_block < config.cooldown_blocks:
                    continue
                    
                available_actions.append((action_name, address, config.probability))

        if not available_actions:
            return None, "", {}

        # Select action based on probabilities
        action = random.choices(
            available_actions,
            weights=[x[2] for x in available_actions],
            k=1
        )[0]

        action_name, address = action[0], action[1]
        
        # Prepare parameters
        config = self.profile.get_action_config(action_name)
        params = self._prepare_action_params(
            action_name,
            address,
            config.constraints,
            config.batchcall
        )

        if not params:
            return None, "", {}

        # Update tracking
        self.action_states[address][action_name]['executions'] += 1
        self.last_action_blocks[address][action_name] = current_block

        return action_name, address, params

    def _prepare_action_params(self, 
                             action_name: str, 
                             address: str,
                             constraints: Dict[str, Any],
                             batchcall: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Prepare parameters for action execution"""
        params = {
            'sender': address,
            'value': 0
        }

        # Add constraints
        if constraints:
            params.update(constraints)

        # Handle batch call configuration
        if batchcall:
            options = list(batchcall.items())
            selected_call, _ = random.choices(
                options,
                weights=[x[1] for x in options],
                k=1
            )[0]
            params['batchcall'] = selected_call[0]

        return params

    def record_action(self, action_name: str, address: str, block_number: int, success: bool):
        """Record successful action execution with enhanced tracking"""
        if not success:
            return
            
        # Update action state
        if address in self.action_states and action_name in self.action_states[address]:
            self.action_states[address][action_name]['cooldown_block'] = block_number
            self.action_states[address][action_name]['executions'] += 1
            self.last_action_blocks[address][action_name] = block_number

    def update_state(self, key: str, value: Any):
        """Update agent's internal state"""
        self.state[key] = value
        
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get value from agent's state"""
        return self.state.get(key, default)

    def can_perform_action(self, action_name: str, current_block: int) -> bool:
        """Check if action can be performed based on cooldown and constraints"""
        config = self.profile.get_action_config(action_name)
        if not config:
            return False

        for address in self.accounts:
            # Check max executions
            executions = self.action_states[address][action_name]['executions']
            if config.max_executions is not None and executions >= config.max_executions:
                continue

            # Check cooldown
            last_block = self.last_action_blocks[address].get(action_name, 0)
            if current_block - last_block >= config.cooldown_blocks:
                return True

        return False

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