from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
import random
import logging
from src.framework.logging import get_logger

logger = get_logger(__name__, logging.INFO)

@dataclass 
class BaseConfig:
    """Base configuration for agent behavior"""
    target_account_count: int
    max_executions: int = 10  # For collector compatibility
    risk_tolerance: float = 0.5  # For collector compatibility
    sequence_probability: float = 0.5
    max_sequence_iterations: Optional[int] = None
    preferred_networks: List[str] = field(default_factory=list)

@dataclass
class SequenceStep:
    """Represents a single step in an action sequence"""
    action: str
    repeat: int
    constraints: Dict[str, Any]
    batchcall: Optional[Dict[str, float]] = None
    current_repeat: int = 0

@dataclass
class ActionSequence:
    """Represents a complete sequence of actions"""
    name: str
    max_executions: Optional[int]
    steps: List[SequenceStep]
    current_execution: int = 0
    current_step_index: int = 0

@dataclass
class ActionConfig:
    """Configuration for an individual action"""
    action_type: str
    probability: float
    cooldown_blocks: int
    constraints: Dict[str, Any]
    batchcall: Optional[Union[str, Dict[str, float]]] = None
    max_executions: Optional[int] = None
    current_executions: int = 0

    @classmethod
    def from_dict(cls, action_type: str, config: Dict[str, Any]) -> 'ActionConfig':
        """Create from dictionary configuration"""
        # Handle batchcall configuration
        batchcall = config.get('batchcall')
        if isinstance(batchcall, str):
            # Single call type
            batchcall = {batchcall: 1.0}
        elif isinstance(batchcall, dict):
            # Multiple call types with probabilities
            total = sum(batchcall.values())
            batchcall = {k: v/total for k, v in batchcall.items()}  # Normalize probabilities

        return cls(
            action_type=action_type,
            probability=config['probability'],
            cooldown_blocks=config['cooldown_blocks'],
            constraints=config.get('constraints', {}),
            batchcall=batchcall,
            max_executions=config.get('max_executions', None),
            current_executions=0
        )

@dataclass
class AgentProfile:
    """Complete profile defining agent behavior."""
    name: str
    description: str
    base_config: BaseConfig
    sequences: List[ActionSequence]
    action_configs: Dict[str, ActionConfig]
    preset_addresses: Optional[List[str]] = None
    current_sequence_iterations: Dict[str, int] = field(default_factory=dict)
    
    # Expose these for collector compatibility
    target_account_count: int = field(init=False)
    max_executions: int = field(init=False)
    risk_tolerance: float = field(init=False)

    def __post_init__(self):
        """Initialize tracking dictionaries and expose needed fields"""
        if self.current_sequence_iterations is None:
            self.current_sequence_iterations = {seq.name: 0 for seq in self.sequences}
            
        # Expose fields needed by collector
        self.target_account_count = self.base_config.target_account_count
        self.max_executions = self.base_config.max_executions
        self.risk_tolerance = self.base_config.risk_tolerance


    @classmethod
    def from_dict(cls, name: str, config: Dict) -> 'AgentProfile':
        """Create profile from configuration dictionary"""
        # Parse base config
        base_config = BaseConfig(
            target_account_count=config.get('base_config', {}).get('target_account_count', 1),
            max_executions=config.get('base_config', {}).get('max_executions', 10),
            risk_tolerance=config.get('base_config', {}).get('risk_tolerance', 0.5),
            sequence_probability=config.get('base_config', {}).get('sequence_probability', 0.5),
            max_sequence_iterations=config.get('base_config', {}).get('max_sequence_iterations'),
            preferred_networks=config.get('base_config', {}).get('preferred_networks', [])
        )

        # Parse sequences
        sequences = []
        for seq in config.get('action_sequences', []):
            steps = []
            for step in seq.get('steps', []):
                steps.append(SequenceStep(
                    action=step['action'],
                    repeat=step.get('repeat', 1),
                    constraints=step.get('constraints', {}),
                    batchcall=step.get('batchcall'),
                    current_repeat=0
                ))
            sequences.append(ActionSequence(
                name=seq['name'],
                max_executions=seq.get('max_executions'),
                steps=steps,
                current_execution=0,
                current_step_index=0
            ))

        # Parse action configs - including both available_actions and sequence actions
        action_configs = {}

        # Add available_actions
        for action in config.get('available_actions', []):
            action_type = action['action']
            action_configs[action_type] = ActionConfig.from_dict(action_type, action)

        # Add sequence actions if they're not already in action_configs
        for sequence in sequences:
            for step in sequence.steps:
                action_type = step.action
                if action_type not in action_configs:
                    # Create action config from sequence step
                    action_config = ActionConfig(
                        action_type=action_type,
                        probability=1.0,  # Sequences have their own probability handling
                        cooldown_blocks=0,  # Use sequence's own cooldown handling
                        constraints=step.constraints or {},
                        batchcall=step.batchcall,
                        max_executions=None  # Sequences handle their own execution limits
                    )
                    action_configs[action_type] = action_config

        logger.info(f"Created profile with actions: {list(action_configs.keys())}")

        return cls(
            name=name,
            description=config.get('description', ''),
            base_config=base_config,
            sequences=sequences,
            action_configs=action_configs,
            preset_addresses=config.get('base_config', {}).get('preset_addresses'),
            current_sequence_iterations=None  # Will be initialized in post_init
        )

    @classmethod
    def from_dict2(cls, name: str, config: Dict) -> 'AgentProfile':
        """Create profile from configuration dictionary"""
        # Parse base config
        base_config = BaseConfig(
            target_account_count=config.get('base_config', {}).get('target_account_count', 1),
            max_executions=config.get('base_config', {}).get('max_executions', 10),
            risk_tolerance=config.get('base_config', {}).get('risk_tolerance', 0.5),
            sequence_probability=config.get('base_config', {}).get('sequence_probability', 0.5),
            max_sequence_iterations=config.get('base_config', {}).get('max_sequence_iterations'),
            preferred_networks=config.get('base_config', {}).get('preferred_networks', [])
        )

        # Parse sequences
        sequences = []
        for seq in config.get('action_sequences', []):
            steps = []
            for step in seq.get('steps', []):
                steps.append(SequenceStep(
                    action=step['action'],
                    repeat=step.get('repeat', 1),
                    constraints=step.get('constraints', {}),
                    batchcall=step.get('batchcall'),
                    current_repeat=0
                ))
            sequences.append(ActionSequence(
                name=seq['name'],
                max_executions=seq.get('max_executions'),
                steps=steps,
                current_execution=0,
                current_step_index=0
            ))

        # Parse action configs
        action_configs = {}
        for action in config.get('available_actions', []):
            action_type = action['action']
            action_configs[action_type] = ActionConfig.from_dict(action_type, action)

        return cls(
            name=name,
            description=config.get('description', ''),
            base_config=base_config,
            sequences=sequences,
            action_configs=action_configs,
            preset_addresses=config.get('base_config', {}).get('preset_addresses'),
            current_sequence_iterations=None  # Will be initialized in post_init
        )

    def get_action_config(self, action_name: str) -> Optional[ActionConfig]:
        """Get configuration for a specific action"""
        return self.action_configs.get(action_name)

    def can_execute_sequence(self, sequence: ActionSequence, address: str) -> bool:
        """Check if a sequence can be executed"""
        # Check max executions
        if (sequence.max_executions is not None and 
            sequence.current_execution >= sequence.max_executions):
            return False

        # Check max iterations per address
        if (self.base_config.max_sequence_iterations is not None and
            self.current_sequence_iterations[sequence.name] >= self.base_config.max_sequence_iterations):
            return False

        return True

    def can_execute_step(self, step: SequenceStep) -> bool:
        """Check if a sequence step can be executed"""
        return step.current_repeat < step.repeat

    def update_sequence_progress(self, sequence: ActionSequence, step: SequenceStep):
        """Update progress tracking for sequence execution"""
        step.current_repeat += 1
        
        # If step complete, move to next
        if step.current_repeat >= step.repeat:
            step.current_repeat = 0
            sequence.current_step_index = (sequence.current_step_index + 1) % len(sequence.steps)
            
            # If sequence complete, update counters
            if sequence.current_step_index == 0:
                sequence.current_execution += 1
                self.current_sequence_iterations[sequence.name] += 1

    def reset_sequence_progress(self, sequence: ActionSequence):
        """Reset progress tracking for a sequence"""
        sequence.current_step_index = 0
        for step in sequence.steps:
            step.current_repeat = 0

    def should_execute_sequence(self) -> bool:
        """Determine if we should execute a sequence or individual action"""
        return (random.random() < self.base_config.sequence_probability and 
                bool(self.sequences))