from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Any
import random
import logging
import secrets
import uuid
from datetime import datetime
from eth_account import Account

logger = logging.getLogger(__name__)

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

@dataclass
class ActionConfig:
    """Configuration for a single action type"""
    probability: float
    cooldown_blocks: int
    gas_limit: int
    min_balance: float
    max_value: float
    constraints: Dict[str, Any]

@dataclass
class AgentProfile:
    """Defines an agent's behavioral characteristics"""
    name: str
    description: str
    action_configs: Dict[ActionType, ActionConfig]
    target_account_count: int
    max_daily_actions: int
    risk_tolerance: float
    preferred_contracts: List[str]

class BaseAgent:
    """
    Base agent class that defines behavior characteristics and action selection
    but not action implementation
    """
    def __init__(self, agent_id: str, profile: AgentProfile):
        self.agent_id = agent_id
        self.profile = profile
        self.accounts: Dict[str, bytes] = {}  # address -> private_key
        self.controlled_addresses: Set[str] = set()
        self.trusted_addresses: Set[str] = set()
        self.last_actions: Dict[ActionType, int] = {}
        self.daily_action_counts = {}
        self.creation_time = datetime.now()

    def create_account(self) -> Tuple[str, bytes]:
        """Create a new blockchain account controlled by this agent"""
        private_key = secrets.token_bytes(32)
        account = Account.from_key(private_key)
        self.accounts[account.address] = private_key
        self.controlled_addresses.add(account.address)
        return account.address, private_key

    def get_accounts(self) -> List[str]:
        """Get all addresses controlled by this agent"""
        return list(self.accounts.keys())

    def get_random_account(self) -> Optional[Tuple[str, bytes]]:
        """Get a random account controlled by this agent"""
        if not self.accounts:
            return None
        address = random.choice(list(self.accounts.keys()))
        return address, self.accounts[address]

    def select_action(self, current_block: int, state: Dict[str, Any]) -> Tuple[Optional[ActionType], str, Dict]:
        """
        Decide what action to take based on profile configuration and current state
        
        Args:
            current_block: Current blockchain block number
            state: Current network state information
            
        Returns:
            Tuple of (action type, acting address, action parameters) or (None, None, {})
        """
        # Check daily action limit
        today = datetime.now().date().isoformat()
        if self.daily_action_counts.get(today, 0) >= self.profile.max_daily_actions:
            return None, "", {}

        # Get available actions based on configuration
        available_actions = []
        for action_type, config in self.profile.action_configs.items():
            if self._can_perform_action(action_type, current_block, state):
                available_actions.append((action_type, config.probability))

        if not available_actions:
            return None, "", {}

        # Select action based on probabilities
        action_type = random.choices(
            [a[0] for a in available_actions],
            weights=[a[1] for a in available_actions]
        )[0]

        # Select account to perform action
        account_tuple = self.get_random_account()
        if not account_tuple:
            return None, "", {}
            
        acting_address, _ = account_tuple

        # Get basic parameters for the action
        params = self._get_action_params(action_type, acting_address, state)

        return action_type, acting_address, params

    def _can_perform_action(self, action_type: ActionType, current_block: int, state: Dict) -> bool:
        """Check if an action can be performed based on constraints"""
        config = self.profile.action_configs[action_type]

        # Check cooldown
        last_action = self.last_actions.get(action_type, 0)
        if current_block - last_action < config.cooldown_blocks:
            return False

        # Check account limit for registration
        if action_type == ActionType.REGISTER_HUMAN:
            if len(self.controlled_addresses) >= self.profile.target_account_count:
                return False

        # Check balance requirements if specified
        if config.min_balance > 0:
            account = self.get_random_account()
            if not account:
                return False
            balance = state.get('balances', {}).get(account[0], 0)
            if balance < config.min_balance:
                return False

        return True

    def _get_action_params(self, action_type: ActionType, acting_address: str, state: Dict) -> Dict:
        """Get basic parameters for an action"""
        config = self.profile.action_configs[action_type]
        
        # Basic parameters common to most actions
        params = {
            'gas_limit': config.gas_limit,
            'acting_address': acting_address,
            'max_value': config.max_value,
            'risk_tolerance': self.profile.risk_tolerance
        }
        
        # Add action-specific constraints
        params.update(config.constraints)
        
        return params

    def record_action(self, action_type: ActionType, block_number: int, success: bool):
        """Record a performed action"""
        if success:
            self.last_actions[action_type] = block_number
            today = datetime.now().date().isoformat()
            self.daily_action_counts[today] = self.daily_action_counts.get(today, 0) + 1