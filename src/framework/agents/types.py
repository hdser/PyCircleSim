from dataclasses import dataclass
from typing import Dict, List, Any
from enum import Enum, auto

class ActionType(Enum):
    """All possible actions an agent can perform"""
    MINT = auto()
    TRANSFER = auto()
    TRUST = auto()
    CREATE_GROUP = auto()
    REGISTER_HUMAN = auto()
    SET_FLAGS = auto()
    WRAP_TOKEN = auto()
    OPERATE_MATRIX = auto()
    CREATE_POOL = auto()
    EXIT_POOL = auto()
    UPDATE_WEIGHTS = auto()
    SET_SWAP_ENABLED = auto()

@dataclass
class ActionConfig:
    """Configuration for a single action type"""
    probability: float
    cooldown_blocks: int
    gas_limit: int
    min_balance: float
    max_value: float
    constraints: Dict[str, any]

@dataclass
class AgentProfile:
    """Defines an agent's behavioral characteristics"""
    name: str
    description: str
    action_configs: Dict[str, ActionConfig]
    target_account_count: int
    max_daily_actions: int
    risk_tolerance: float
    preferred_contracts: List[str]