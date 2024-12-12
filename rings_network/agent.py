from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
from abc import ABC, abstractmethod
import random
import logging
from eth_account import Account
import secrets
import uuid

logger = logging.getLogger(__name__)

class AgentPersonality(Enum):
    """Defines different personality types that influence agent behavior"""
    CONSERVATIVE = "conservative"   # Careful with trust, maintains fewer connections
    SOCIAL = "social"              # Readily creates trust connections
    ENTREPRENEUR = "entrepreneur"  # Focuses on group creation and economic activity
    OPPORTUNIST = "opportunist"    # Optimizes for personal gain
    COMMUNITY = "community"        # Prioritizes network health over personal gain

class AgentEconomicStatus(Enum):
    """Defines the economic status/capacity of an agent"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class AgentProfile:
    """Holds the characteristics that define an agent's behavior"""
    personality: AgentPersonality
    economic_status: AgentEconomicStatus
    trust_threshold: float = field(default=0.5)  # Threshold for establishing trust
    max_connections: int = field(default=100)    # Maximum number of trust connections
    activity_level: float = field(default=0.5)   # How frequently the agent acts (0-1)
    risk_tolerance: float = field(default=0.5)   # Willingness to take economic risks
    
    @classmethod
    def random(cls) -> 'AgentProfile':
        """Create a random agent profile"""
        return cls(
            personality=random.choice(list(AgentPersonality)),
            economic_status=random.choice(list(AgentEconomicStatus)),
            trust_threshold=random.uniform(0.3, 0.8),
            max_connections=random.randint(50, 200),
            activity_level=random.uniform(0.2, 0.9),
            risk_tolerance=random.uniform(0.2, 0.8)
        )

class Agent:
    """Base agent class representing an actor in the Rings network"""
    
    def __init__(self, profile: Optional[AgentProfile] = None):
        self.profile = profile or AgentProfile.random()
        self.accounts: Dict[str, bytes] = {}  # address -> private_key
        self.trusted_agents: Set[str] = set()  # addresses of trusted agents
        self.groups: Set[str] = set()  # groups created/owned by this agent
        
    def create_account(self) -> Tuple[str, bytes]:
        """Create a new account for this agent"""
        private_key = secrets.token_bytes(32)
        account = Account.from_key(private_key)
        self.accounts[account.address] = private_key
        return account.address, private_key
        
    def should_trust(self, other_agent: 'Agent') -> bool:
        """Determine if this agent should trust another agent"""
        # Base trust decision on personality and other factors
        if len(self.trusted_agents) >= self.profile.max_connections:
            return False
            
        # Different personalities have different trust strategies
        if self.profile.personality == AgentPersonality.CONSERVATIVE:
            # Conservative agents need higher trust threshold
            return random.random() > (self.profile.trust_threshold + 0.2)
        elif self.profile.personality == AgentPersonality.SOCIAL:
            # Social agents are more likely to trust
            return random.random() > (self.profile.trust_threshold - 0.2)
        else:
            return random.random() > self.profile.trust_threshold
            
    def should_act_this_iteration(self) -> bool:
        """Determine if agent should take action in current iteration"""
        return random.random() < self.profile.activity_level
        
    def decide_action(self) -> Tuple[str, Dict]:
        """Decide what action to take this iteration"""
        available_actions = self._get_available_actions()
        weights = self._calculate_action_weights()
        
        action = random.choices(
            list(available_actions.keys()),
            weights=[weights[a] for a in available_actions.keys()]
        )[0]
        
        return action, available_actions[action]
        
    def _get_available_actions(self) -> Dict[str, Dict]:
        """Get dictionary of available actions and their parameters"""
        actions = {
            "mint": {"probability": 1},
            "establish_trust": {"probability": 0.3},
            "transfer": {"probability": 0.2}
        }
        
        # Add group-related actions based on personality
        if self.profile.personality in [AgentPersonality.ENTREPRENEUR, AgentPersonality.COMMUNITY]:
            actions["create_group"] = {"probability": 0.1}
            
        return actions
        
    def _calculate_action_weights(self) -> Dict[str, float]:
        """Calculate weights for different actions based on agent profile"""
        weights = {}
        
        for action, params in self._get_available_actions().items():
            base_prob = params["probability"]
            
            # Modify probabilities based on personality
            if self.profile.personality == AgentPersonality.ENTREPRENEUR:
                if action in ["create_group", "transfer"]:
                    base_prob *= 1.5
            elif self.profile.personality == AgentPersonality.SOCIAL:
                if action == "establish_trust":
                    base_prob *= 1.5
            elif self.profile.personality == AgentPersonality.CONSERVATIVE:
                if action == "mint":
                    base_prob *= 1.3
                    
            weights[action] = base_prob
            
        return weights

class AgentManager:
    """Manages a collection of agents in the simulation"""
    
    def __init__(self, data_collector: Optional['CirclesDataCollector'] = None):
        self.agents: Dict[str, Agent] = {}  # agent_id -> Agent
        self.address_to_agent_id: Dict[str, str] = {}  # address -> agent_id
        self.data_collector = data_collector

    def create_agent(self, profile: Optional[AgentProfile] = None) -> Tuple[Agent, str, str]:
        """
        Create a new agent with initial account.
        
        Returns:
            Tuple of (Agent instance, agent_id, primary_address)
        """
        # Create the agent with the profile
        agent = Agent(profile)
        
        # Generate the blockchain address and private key
        address, private_key = agent.create_account()
        
        # Generate unique ID for the agent
        agent_id = str(uuid.uuid4())
        
        # Store the mappings
        self.agents[agent_id] = agent
        self.address_to_agent_id[address] = agent_id
        
        # Record in database if collector is available
        if self.data_collector:
            self.data_collector.record_agent(agent_id, agent.profile)
            self.data_collector.record_agent_address(agent_id, address, is_primary=True)
            
        return agent, agent_id, address

    def create_random_agents(
        self,
        count: int,
        personality_weights: Optional[Dict[AgentPersonality, float]] = None
    ) -> List[Tuple[Agent, str, str]]:
        """
        Create multiple agents with random or weighted personalities.
        
        Returns:
            List of tuples (Agent, agent_id, primary_address)
        """
        if personality_weights is None:
            personality_weights = {p: 1.0 for p in AgentPersonality}
            
        agents_data = []
        for _ in range(count):
            personality = random.choices(
                list(personality_weights.keys()),
                weights=list(personality_weights.values())
            )[0]
            
            profile = AgentProfile(
                personality=personality,
                economic_status=random.choice(list(AgentEconomicStatus)),
                trust_threshold=random.uniform(0.3, 0.8),
                max_connections=random.randint(50, 200),
                activity_level=random.uniform(0.2, 0.9),
                risk_tolerance=random.uniform(0.2, 0.8)
            )
            
            agents_data.append(self.create_agent(profile))
            
        return agents_data

    def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """Get agent instance by its ID."""
        return self.agents.get(agent_id)

    def get_agent_by_address(self, address: str) -> Optional[Agent]:
        """Get agent instance by any of their account addresses."""
        agent_id = self.address_to_agent_id.get(address)
        return self.agents.get(agent_id)

    def get_agent_id_by_address(self, address: str) -> Optional[str]:
        """Get agent ID associated with an address."""
        return self.address_to_agent_id.get(address)