from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
import random
import secrets
import logging
from eth_account import Account
from .types import ActionType, AgentProfile, ActionConfig

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base agent with simplified action selection and execution"""
    
    def __init__(self, agent_id: str, profile: AgentProfile):
        self.agent_id = agent_id
        self.profile = profile
        self.accounts: Dict[str, bytes] = {}
        self.controlled_addresses: Set[str] = set()
        self.trusted_addresses: Set[str] = set()
        self.last_actions: Dict[str, int] = {}  # Keyed by action name for flexibility
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

    def select_action(self, current_block: int, state: Dict[str, Any]) -> Tuple[Optional[str], str, Dict]:
        """
        Select an action based on profile configuration and current state
        Returns: (action_name, acting_address, params) or (None, "", {})
        """
        # Check daily action limit
        today = datetime.now().date().isoformat()
        if self.daily_action_counts.get(today, 0) >= self.profile.max_daily_actions:
            return None, "", {}

        # Get available actions based on configuration
        available_actions = []
        for action_name, config in self.profile.action_configs.items():
            if self.can_perform_action(action_name, current_block, state):
                available_actions.append((action_name, config.probability))

        if not available_actions:
            return None, "", {}

        # Select action based on probabilities
        action_name = random.choices(
            [a[0] for a in available_actions],
            weights=[a[1] for a in available_actions]
        )[0]

        # Select acting account
        account_tuple = self.get_random_account()
        if not account_tuple:
            return None, "", {}
            
        acting_address, _ = account_tuple

        # Get parameters
        params = self._get_base_params(action_name, acting_address)
        
        return action_name, acting_address, params

    def can_perform_action(self, action_name: str, current_block: int, state: Dict) -> bool:
        """Check if action can be performed based on basic constraints"""
        try:
            config = self.profile.action_configs[action_name]

            # Time-based cooldown
            last_action = self.last_actions.get(action_name, 0)
            if current_block - last_action < config.cooldown_blocks:
                return False

            # Base requirements
            if config.min_balance > 0:
                account = self.get_random_account()
                if not account:
                    return False
                balance = state.get('balances', {}).get(account[0], 0)
                if balance < config.min_balance:
                    return False

            return True

        except Exception as e:
            logger.error(f"Error checking action eligibility: {e}")
            return False

    def _get_base_params(self, action_name: str, acting_address: str) -> Dict:
        """Get basic parameters for the action"""
        config = self.profile.action_configs[action_name]
        return {
            'gas_limit': config.gas_limit,
            'acting_address': acting_address,
            'max_value': config.max_value,
            'risk_tolerance': self.profile.risk_tolerance
        }

    def record_action(self, action_name: str, block_number: int, success: bool):
        """Record a performed action"""
        if success:
            self.last_actions[action_name] = block_number
            today = datetime.now().date().isoformat()
            self.daily_action_counts[today] = self.daily_action_counts.get(today, 0) + 1