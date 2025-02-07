from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import random
import secrets
from eth_account import Account
from ape import networks
from src.framework.logging import get_logger
from src.framework.data import BaseDataCollector
from .profile import AgentProfile 
import logging

logger = get_logger(__name__, logging.INFO)



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
            'isGroup': []
        }
        
        self.creation_time = datetime.now()

        self._initialize_accounts()

    def _validate_action(self, action_name: str) -> bool:
        # Import IMPLEMENTATIONS locally to break the cycle
        from src.protocols.implementations import IMPLEMENTATIONS
        return action_name in IMPLEMENTATIONS
    
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
                "sequence_executions": 0  # Track completed sequences
            }

        # Initialize action tracking dictionaries
        if not hasattr(self, 'action_states'):
            self.action_states = {}
        if not hasattr(self, 'last_action_blocks'):
            self.last_action_blocks = {}
            
        self.action_states[address] = {}
        self.last_action_blocks[address] = {}
        
        # Collect all action names from both regular actions and sequence steps
        action_names = set()
        
        # Add actions from action_configs
        for action_name in self.profile.action_configs.keys():
            action_names.add(action_name)
            
        # Add actions from sequences
        for sequence in self.profile.sequences:
            for step in sequence.steps:
                action_names.add(step.action)
                
        # Initialize action states for each action
        for action_name in action_names:
            self.action_states[address][action_name] = {
                'cooldown_block': 0,
                'executions': 0
            }
            self.last_action_blocks[address][action_name] = 0


    def select_action(self, current_block: int, network_state: Dict[str, Any]) -> Tuple[Optional[str], str]:
        """
        Selects an action for an agent, prioritizing sequences but handling failures gracefully.
        """
        base_cfg = self.profile.base_config
        seq_probability = getattr(base_cfg, "sequence_probability", 0.0)
        addresses = list(self.accounts.keys())

        logger.debug(f"Selecting action with sequence probability {seq_probability}")
        logger.debug(f"Available sequences: {[s.name for s in self.profile.sequences]}")

        # 1. First check any incomplete active sequences
        for address in addresses:
            for seq_def in self.profile.sequences:
                seq_name = seq_def.name
                seq_state = self.sequence_states[address][seq_name]

                # Skip if sequence has reached max executions
                if seq_def.max_executions is not None and seq_state["sequence_executions"] >= seq_def.max_executions:
                    continue

                # If sequence is active and not in cooldown, try to continue it
                if seq_state["active"]:
                    if seq_state.get("last_failed_block") and (current_block - seq_state["last_failed_block"]) < 300:
                        continue  # Skip if in cooldown from failure
                        
                    action_tuple = self._execute_sequence_step(address, seq_def, seq_state, current_block)
                    if action_tuple:
                        action_name, addr, _ = action_tuple
                        return action_name, addr

        # 2. Then check if we should start a new sequence or retry a failed one
        if random.random() < seq_probability:
            for address in addresses:
                for seq_def in self.profile.sequences:
                    seq_name = seq_def.name
                    seq_state = self.sequence_states[address][seq_name]
                    
                    # Skip if reached max executions
                    if seq_def.max_executions is not None and seq_state["sequence_executions"] >= seq_def.max_executions:
                        continue
                        
                    # Skip if in cooldown
                    if seq_state.get("last_failed_block") and (current_block - seq_state["last_failed_block"]) < 300:
                        continue

                    if not seq_state["active"]:
                        logger.info(f"Starting/resuming sequence {seq_name} for address {address}")
                        seq_state["active"] = True
                        # Don't reset step index if resuming after failure
                        if "failed_step" not in seq_state:
                            seq_state["current_step_index"] = 0
                            seq_state["executed_repeats_for_step"] = 0
                        
                        action_tuple = self._execute_sequence_step(address, seq_def, seq_state, current_block)
                        if action_tuple:
                            action_name, addr, _ = action_tuple
                            return action_name, addr

        # Fall back to individual actions
        individual_action = self._select_individual_action(current_block)
        if individual_action[0]:
            return individual_action[0], individual_action[1]
            
        return None, ""
    
    def _prepare_master_params(self, action_config: Dict[str, Any], address: str) -> Dict[str, Any]:
        """New method to prepare master interface parameters"""
        params = {
            'sender': address,
            'value': 0,
            'implementation': action_config.get('implementation')
        }
        
        # Add all constraints as parameters
        if 'constraints' in action_config:
            params.update(action_config['constraints'])
            
        return params

    def _select_sequence_action(self, current_block: int) -> Optional[Tuple[str, str, Dict]]:
        """Modified to handle master interface actions in sequences"""
        for sequence in self.profile.sequences:
            for address in self.accounts:
                step = sequence.get_current_step()
                if not step:
                    continue
                    
                # Handle master interface actions
                if step.action.startswith('master_'):
                    params = self._prepare_master_params(step, address)
                    return step.action, address, params
                    
                # Original action handling...

    def _select_individual_action(self, current_block: int) -> Tuple[Optional[str], str, Dict]:
        """Modified to handle master interface actions"""
        available_actions = []
        
        for action_name, config in self.profile.action_configs.items():
            # Skip sequence-only actions
            if config.sequence_only:
                continue
                
            for address in self.accounts:
                # Skip if max executions reached
                if self._max_executions_reached(action_name, address):
                    continue
                    
                # Skip if in cooldown
                if self._in_cooldown(action_name, address, current_block):
                    continue
                    
                available_actions.append((action_name, address, config))

        if not available_actions:
            return None, "", {}

        # Select action based on probabilities
        action_name, address, config = random.choices(
            available_actions,
            weights=[x[2].probability for x in available_actions],
            k=1
        )[0]

        # Handle master interface actions
        if action_name.startswith('master_'):
            params = self._prepare_master_params(config, address)
        else:
            params = self._prepare_action_params(action_name, address, config)
            
        return action_name, address, params
    
    def _max_executions_reached(self, action_name: str, address: str) -> bool:
        config = self.profile.get_action_config(action_name)
        if not config:
            return True
        executions = self.action_states[address][action_name]['executions']
        return config.max_executions is not None and executions >= config.max_executions

    def _in_cooldown(self, action_name: str, address: str, current_block: int) -> bool:
        config = self.profile.get_action_config(action_name)
        if not config:
            return True
        last_block = self.last_action_blocks[address].get(action_name, 0) 
        return (current_block - last_block) < config.cooldown_blocks
    
    def _execute_sequence_step(self, address: str, sequence: Any, state: Dict[str, Any], current_block: int) -> Optional[Tuple[str, str, Dict]]:
        """Execute the next step of a sequence"""
        steps = sequence.steps
        step_index = state["current_step_index"]
        
        logger.debug(f"Executing step {step_index} of sequence {sequence.name}")

        # Check if we're done with the sequence
        if step_index >= len(steps):
            logger.debug(f"Sequence {sequence.name} completed")
            state["sequence_executions"] = state.get("sequence_executions", 0) + 1
            state["active"] = False
            state["current_step_index"] = 0
            state["executed_repeats_for_step"] = 0
            return None

        current_step = steps[step_index]
        action_name = current_step.action

        logger.debug(f"Current step action: {action_name}")

        # Check cooldown
        last_block = self.last_action_blocks[address].get(action_name, 0)
        cooldown = getattr(current_step, 'cooldown_blocks', 0)
        if (current_block - last_block) < cooldown:
            logger.debug(f"Action {action_name} in cooldown")
            return None

        # Check if we've done enough repeats
        repeats_done = state["executed_repeats_for_step"]
        repeats_needed = current_step.repeat
        if repeats_done >= repeats_needed:
            logger.debug(f"Step {step_index} completed all repeats")
            state["current_step_index"] += 1
            state["executed_repeats_for_step"] = 0
            return self._execute_sequence_step(address, sequence, state, current_block)

        # Build parameters
        params = {"sender": address}
        if hasattr(current_step, 'constraints') and current_step.constraints:
            params.update(current_step.constraints)

        logger.debug(f"Built parameters for action {action_name}: {params}")

        return action_name, address, params


    def _prepare_action_params(self, 
                         action_name: str, 
                         address: str,
                         constraints: Dict[str, Any]
        ) -> Dict[str, Any]:
        """
        Prepare parameters for action execution by combining base parameters with constraints.
        
        Args:
            action_name: Name of the action being executed
            address: Address initiating the action
            constraints: Dictionary of constraint parameters for the action

        Returns:
            Dict containing all parameters needed for action execution
        """
        # Initialize with required base parameters
        params = {
            'sender': address,
            'value': 0
        }

        # Add constraints if provided, ensuring we handle both dict and ActionConfig objects
        if constraints:
            if isinstance(constraints, dict):
                params.update(constraints)
            elif hasattr(constraints, 'constraints'):
                # Handle case where we receive an ActionConfig object
                params.update(constraints.constraints)

        return params

    def record_action(
        self, 
        action_name: str, 
        address: str, 
        block_number: int, 
        success: bool, 
        context: Optional['SimulationContext'] = None
    ):
        """Record action execution and update sequence state."""
        logger.debug(f"Recording action {action_name} for address {address} (success={success})")

        # Handle action failure
        if not success:
            error_msg = None
            if context and hasattr(context, 'last_error'):
                error_msg = context.last_error.get('batch_call')
                
            # Update sequence states to mark failure
            for seq_name, seq_state in self.sequence_states[address].items():
                if seq_state.get("active"):
                    logger.info(f"Sequence {seq_name} failed at step {seq_state['current_step_index']}")
                    logger.info(f"Failure reason: {error_msg}")
                    
                    # Store failure info but allow retry
                    seq_state.update({
                        "active": False,
                        "last_failed_block": block_number,
                        "failed_step": seq_state["current_step_index"],
                        "failed_action": action_name
                    })
            return

        # Update action tracking state
        if address in self.action_states and action_name in self.action_states[address]:
            self.action_states[address][action_name].update({
                'cooldown_block': block_number,
                'executions': self.action_states[address][action_name]['executions'] + 1
            })
            self.last_action_blocks[address][action_name] = block_number

        # Update sequence states for successful execution
        for sequence in self.profile.sequences:
            state = self.sequence_states[address][sequence.name]

            if not state.get("active"):
                continue
                
            current_step_idx = state["current_step_index"]
            if current_step_idx >= len(sequence.steps):
                continue
                
            current_step = sequence.steps[current_step_idx]
            
            # Check if this action matches current sequence step
            if current_step.action == action_name:
                logger.debug(f"Found matching step {current_step_idx} for action {action_name}")
                
                # Update step execution count
                state["executed_repeats_for_step"] += 1
                logger.debug(f"Executed repeats: {state['executed_repeats_for_step']}/{current_step.repeat}")
                
                # Clear any failure state on success
                state.pop("failed_step", None)
                state.pop("failed_action", None)
                state.pop("last_failed_block", None)
                
                # Check if step is complete
                if state["executed_repeats_for_step"] >= current_step.repeat:
                    # Move to next step
                    state["current_step_index"] += 1
                    state["executed_repeats_for_step"] = 0
                    
                    # Check if sequence is complete
                    if state["current_step_index"] >= len(sequence.steps):
                        logger.debug(f"Completed sequence {sequence.name} for {address}")
                        state.update({
                            "active": False,
                            "current_step_index": 0,
                            "sequence_executions": state.get("sequence_executions", 0) + 1
                        })
                    else:
                        logger.debug(f"Moving to step {state['current_step_index']} for {address}")


    def can_execute_sequence(self, sequence: 'ActionSequence', address: str) -> bool:
        """Check if a sequence can be executed, including retry logic"""
        # Check max executions
        if (sequence.max_executions is not None and 
            sequence.current_execution >= sequence.max_executions):
            return False

        # Check max iterations per address
        if (self.base_config.max_sequence_iterations is not None and
            self.current_sequence_iterations[sequence.name] >= self.base_config.max_sequence_iterations):
            return False

        # Get sequence state
        seq_state = self.sequence_states[address][sequence.name]
        
        # If sequence recently failed, check cooldown
        if "last_failed_block" in seq_state:
            current_block = self.chain.blocks.head.number
            blocks_since_failure = current_block - seq_state["last_failed_block"]
            
            # Exponential backoff for retries (300 blocks * 2^failure_count)
            retry_cooldown = 300 * (2 ** (seq_state.get("failure_count", 0) - 1))
            if blocks_since_failure < retry_cooldown:
                return False
            
            # Reset failure state to allow retry
            if not seq_state.get("active"):
                seq_state.update({
                    "active": False,
                    "current_step_index": 0,
                    "executed_repeats_for_step": 0
                })

        return True


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

