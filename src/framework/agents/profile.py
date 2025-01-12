from dataclasses import dataclass
from typing import Dict, List, Any, Optional

@dataclass 
class BaseConfig:
    """Base configuration for agent behavior"""
    target_account_count: int
    max_daily_actions: int
    risk_tolerance: float
    preferred_networks: List[str]
    
@dataclass
class ActionConfig:
    """Configuration for an individual action"""
    action_type: str
    probability: float
    cooldown_blocks: int
    constraints: Dict[str, Any]
    preset_addresses: Optional[List[str]] = None 

    @classmethod
    def from_dict(cls, action_type: str, config: Dict[str, Any]) -> 'ActionConfig':
        """Create from dictionary configuration"""
        return cls(
            action_type=action_type,
            probability=config['probability'],
            cooldown_blocks=config['cooldown_blocks'],
            constraints=config.get('constraints', {})
        )

@dataclass
class AgentProfile:
    """Complete profile defining agent behavior."""
    name: str
    description: str
    target_account_count: int
    max_daily_actions: int
    risk_tolerance: float
    preferred_networks: List[str]
    preset_addresses: Optional[List[str]]
    action_configs: Dict[str, ActionConfig]

    @classmethod
    def from_dict(cls, name: str, config: Dict) -> 'AgentProfile':
        """Create profile from configuration dictionary"""
        base_config = config.get('base_config', {})
        
        # Convert each action config to ActionConfig object
        action_configs = {}
        for action in config.get('available_actions', []):
            action_type = action['action']
            action_configs[action_type] = ActionConfig.from_dict(action_type, action)

        return cls(
            name=name,
            description=config.get('description', ''),
            target_account_count=base_config.get('target_account_count', 1),
            max_daily_actions=base_config.get('max_daily_actions', 10),
            risk_tolerance=base_config.get('risk_tolerance', 0.5),
            preferred_networks=base_config.get('preferred_networks', []),
            preset_addresses=base_config.get('preset_addresses', None),
            action_configs=action_configs
        )

    def get_action_config(self, action_name: str) -> Optional[ActionConfig]:
        """
        Return the ActionConfig for a given action name, or None if it doesn't exist.
        """
        return self.action_configs.get(action_name, None)

    def can_perform_action(
        self, 
        action_type: str, 
        current_block: int,
        last_block: int
    ) -> bool:
        """Check if action can be performed based on cooldown."""
        config = self.get_action_config(action_type)
        if not config:
            return False

        # No cooldown if first time
        if last_block == 0:
            return True

        # Check cooldown period
        return (current_block - last_block) >= config.cooldown_blocks
