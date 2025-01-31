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

logger = get_logger(__name__, logging.DEBUG)


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

        self._initialize_accounts()

    def _initialize_accounts(self):
        """Ensure agent has required number of accounts."""
        target_count = self.profile.base_config.target_account_count
        assigned_addresses = self.profile.preset_addresses or []
        
        # Initialize preset addresses first
        for addr in assigned_addresses:
            self.accounts[addr] = bytes()  # Placeholder
            self._initialize_address(addr, preset=True)

        # Create new accounts if needed
        while len(self.accounts) < target_count:
            address, private_key = self.create_account()
            self.accounts[address] = private_key
            self._initialize_address(address)



    def _initialize_accounts(self):
        """Ensure agent has required number of accounts."""
        target_count = self.profile.base_config.target_account_count
        assigned_addresses = self.profile.preset_addresses or []
        
        # Initialize preset addresses first
        for addr in assigned_addresses:
            self.create_account(preset_addr=addr)
            # Add debug log
            balance = networks.provider.get_balance(addr)
            logger.debug(f"Initialized account {addr} with balance {balance/1e18} xDAI")

        # Create new accounts if needed
        while len(self.accounts) < target_count:
            address, _ = self.create_account()
            balance = networks.provider.get_balance(address)
            logger.debug(f"Created new account {address} with balance {balance/1e18} xDAI")

        logger.debug(f"Initialized accounts: {list(self.accounts.keys())}")

    def create_account(self, preset_addr: Optional[str] = None) -> Tuple[str, bytes]:
        """Create and return a new blockchain account."""
        try:
            if preset_addr:
                address = preset_addr
                private_key = bytes()  # Placeholder for preset addresses
            else:
                private_key = secrets.token_bytes(32)
                account = Account.from_key(private_key)
                address = account.address

            # Initialize tracking state
            self.accounts[address] = private_key
            self._initialize_address(address, preset=bool(preset_addr))

            networks.provider.set_balance(address, int(10000e18))

            return address, private_key
        except Exception as e:
            logger.error(f"Failed to create account: {e}")
            raise

    def _initialize_address(self, address: str, preset: bool = False):
        """Initialize tracking state for an address"""
        # Initialize sequence states (per-sequence)
        self.sequence_states[address] = {}
        for seq in self.profile.sequences:
            self.sequence_states[address][seq.name] = {
                "active": False,
                "current_step_index": 0,
                "executed_repeats_for_step": 0,
                "sequence_executions": 0  # how many times the entire sequence was done
            }

        # Initialize action tracking dictionaries
        if not hasattr(self, 'action_states'):
            self.action_states = {}
        if not hasattr(self, 'last_action_blocks'):
            self.last_action_blocks = {}
            
        self.action_states[address] = {}
        self.last_action_blocks[address] = {}
        
        # Initialize action states for each available action
        for action_name, config in self.profile.action_configs.items():
            self.action_states[address][action_name] = {
                'cooldown_block': 0,
                'executions': 0
            }
        self.last_action_blocks[address][action_name] = 0


    def select_action(self, current_block: int, network_state: Dict[str, Any]) -> Tuple[Optional[str], str, Dict]:
        """Selects an action for an agent. Prioritizes executing active sequences."""
        addresses = list(self.accounts.keys())

        # First check any active sequences that need to be completed
        for address in addresses:
            seq_state = self.sequence_states.get(address)
            if not seq_state:
                continue

            # Check each sequence
            for sequence in self.profile.sequences:
                seq_name = sequence.name
                if seq_name not in seq_state:
                    continue
                    
                state = seq_state[seq_name]
                
                # If sequence is active, continue it
                if state.get("active"):
                    action_tuple = self._execute_sequence_step(address, sequence, state, current_block)
                    if action_tuple:
                        return action_tuple

                    # If no action returned, the sequence step is complete, move to next step
                    state["current_step_index"] += 1
                    state["executed_repeats_for_step"] = 0
                    if state["current_step_index"] >= len(sequence.steps):
                        state["active"] = False
                        state["sequence_executions"] = state.get("sequence_executions", 0) + 1

        # Then look for addresses that can start a new sequence
        for address in addresses:
            for sequence in self.profile.sequences:
                state = self.sequence_states[address][sequence.name]
                # Check if we can start a new sequence
                if not state.get("active") and state.get("sequence_executions", 0) < sequence.max_executions:
                    state["active"] = True
                    state["current_step_index"] = 0
                    state["executed_repeats_for_step"] = 0
                    return self._execute_sequence_step(address, sequence, state, current_block)

        return self._select_individual_action(current_block)

    def _execute_sequence_step(self, address: str, sequence: 'ActionSequence', state: Dict[str, Any], current_block: int) -> Optional[Tuple[str, str, Dict]]:
        """Execute the next step of an active sequence for an address."""
        steps = sequence.steps
        step_index = state["current_step_index"]

        if step_index >= len(steps):
            logger.debug(f"{address} completed sequence {sequence.name}")
            state["sequence_executions"] = state.get("sequence_executions", 0) + 1
            state["active"] = False
            return None

        step = steps[step_index]
        action_name = step.action

        logger.debug(f"{address} executing step {step_index} ({action_name}) in sequence {sequence.name}")

        last_block = self.last_action_blocks.get(address, {}).get(action_name, 0)
        cooldown = step.constraints.get("cooldown_blocks", 0)

        if (current_block - last_block) < cooldown:
            logger.warning(f"{action_name} skipped due to cooldown ({cooldown}) for {address}")
            return None

        params = {"sender": address}
        if hasattr(step, 'constraints') and step.constraints:
            params.update(step.constraints)
        if step.batchcall:
            params["batchcall"] = step.batchcall

        logger.debug(f"{address} executing {action_name} with parameters {params}")

        return action_name, address, params


    def select_action3(self, current_block: int, network_state: Dict[str, Any]) -> Tuple[Optional[str], str, Dict]:
        """
        1) Try to continue any sequence that is active for any address.
        2) If none is active, activate a new sequence for the first address that hasn't completed it.
        """
        base_cfg = self.profile.base_config
        seq_probability = getattr(base_cfg, "sequence_probability", 0.0)
        preset_addrs = self.profile.preset_addresses if self.profile.preset_addresses else list(self.accounts.keys())

        # First check any active sequences
        for address in preset_addrs:
            for seq_def in self.profile.sequences:
                seq_name = seq_def.name
                seq_state = self.sequence_states[address][seq_name]
                
                # Skip if sequence is completed for this address
                if seq_state["sequence_executions"] >= seq_def.max_executions:
                    continue

                # Activate sequence if not active
                if not seq_state["active"] and random.random() < seq_probability:
                    logger.info(f"Activating sequence {seq_name} for address {address}")
                    seq_state["active"] = True

                # Try to execute next step if sequence is active
                if seq_state["active"]:
                    logger.debug(f"Checking sequence {seq_name} for {address}: step {seq_state['current_step_index']}, "
                            f"repeats {seq_state['executed_repeats_for_step']}")
                    action_tuple = self._select_sequence_step(address, seq_def, seq_state, current_block)
                    if action_tuple:
                        action_name, _, params = action_tuple
                        # Force the address to be consistent
                        params['sender'] = address
                        # Return with the correct address
                        return action_name, address, params

        # Fall back to individual actions
        return self._select_individual_action(current_block)
    
    def _select_sequence_step3(
        self,
        address: str,
        seq_def: Any,
        state: Dict[str, Any],
        current_block: int
    ) -> Optional[Tuple[str, str, Dict]]:
        """
        Return (action_name, address, params) for the next step in this sequence
        """
        # If already finished max_executions, deactivate
        if state["sequence_executions"] >= seq_def.max_executions:
            state["active"] = False
            return None

        steps = seq_def.steps
        step_index = state["current_step_index"]
        
        # Check if we're within sequence steps
        if step_index >= len(steps):
            # Reset for next iteration
            state["current_step_index"] = 0
            state["executed_repeats_for_step"] = 0
            step_index = 0
            state["sequence_executions"] += 1
            
            # If we've hit max executions, deactivate
            if state["sequence_executions"] >= seq_def.max_executions:
                state["active"] = False
                return None

        # Get current step
        current_step = steps[step_index]
        action_name = current_step.action  # Access as attribute
        repeats_needed = current_step.repeat  # Access as attribute
        repeats_done = state["executed_repeats_for_step"]

        # Check if we need more repeats for this step
        if repeats_done >= repeats_needed:
            logger.info(f"Step {step_index} ({action_name}) completed all repeats for {address}")
            # Move to next step
            state["current_step_index"] += 1
            state["executed_repeats_for_step"] = 0
            return self._select_sequence_step(address, seq_def, state, current_block)

        # Check cooldown
        last_block = self.last_action_blocks[address].get(action_name, 0)
        if hasattr(current_step, 'cooldown_blocks'):
            cooldown = current_step.cooldown_blocks
        else:
            cooldown = 0
            
        if (current_block - last_block) < cooldown:
            return None

        # Build params
        params = {
            "sender": address,  # Always use the sequence address
            "value": 0
        }
        
        # Add constraints if they exist
        if hasattr(current_step, 'constraints') and current_step.constraints:
            params.update(current_step.constraints)
            # Ensure sender isn't overwritten by constraints
            params["sender"] = address

        # Handle batchcall if present
        if hasattr(current_step, 'batchcall') and current_step.batchcall:
            params["batchcall"] = current_step.batchcall

        logger.info(f"Selected step {step_index} ({action_name}) for address {address}, "
                f"repeat {repeats_done + 1}/{repeats_needed}")
        return (action_name, address, params)


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
        """Select a standalone action if no sequence is available."""
        available_actions = []
        for action_name, config in self.profile.action_configs.items():
            for address in self.accounts:
                # Skip actions that exceed max executions
                if config.max_executions and config.current_executions >= config.max_executions:
                    continue
                
                # Check cooldown
                last_block = self.last_action_blocks[address].get(action_name, 0)
                if (current_block - last_block) < config.cooldown_blocks:
                    continue

                available_actions.append((action_name, address, config.probability))

        if not available_actions:
            return None, "", {}

        # Select action based on probabilities
        action, address, _ = random.choices(
            available_actions, 
            weights=[x[2] for x in available_actions],
            k=1
        )[0]

        params = self.profile.action_configs[action].constraints
        params["sender"] = address
        return action, address, params

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
        """Record action execution and update sequence state"""
        if not success:
            return
            
        logger.debug(f"Recording action {action_name} for address {address}")

        # Update sequence states if applicable
        for sequence in self.profile.sequences:
            state = self.sequence_states[address][sequence.name]
            if not state.get("active"):
                continue
                
            current_step_idx = state["current_step_index"]
            if current_step_idx >= len(sequence.steps):
                continue
                
            current_step = sequence.steps[current_step_idx]
            
            # If this is the current step's action
            if current_step.action == action_name:
                logger.debug(f"Found matching step {current_step_idx} for action {action_name}")
                
                # Increment repeats for this step
                state["executed_repeats_for_step"] += 1
                logger.debug(f"Executed repeats: {state['executed_repeats_for_step']}/{current_step.repeat}")
                
                # If step complete
                if state["executed_repeats_for_step"] >= current_step.repeat:
                    # Move to next step
                    state["current_step_index"] += 1
                    state["executed_repeats_for_step"] = 0
                    
                    # If sequence complete
                    if state["current_step_index"] >= len(sequence.steps):
                        logger.debug(f"Completed sequence {sequence.name} for {address}")
                        state["active"] = False
                        state["current_step_index"] = 0
                        state["sequence_executions"] = state.get("sequence_executions", 0) + 1
                    else:
                        logger.debug(f"Moving to step {state['current_step_index']} for {address}")

        # Update action states
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