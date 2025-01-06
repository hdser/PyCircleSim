from typing import Dict, List, Optional
from .base_agent import BaseAgent
from .profile import AgentProfile
from .action_registry import ActionRegistry
from src.framework.data import BaseDataCollector
from src.framework.logging import get_logger
import uuid

logger = get_logger(__name__)

class AgentManager:
    """
    Manages the creation and tracking of agents in the simulation
    """
    def __init__(self, config: Dict, data_collector: Optional['BaseDataCollector'] = None):
        self.config = config
        self.data_collector = data_collector
        self.agents: Dict[str, BaseAgent] = {}
        self.address_to_agent: Dict[str, str] = {}  # address -> agent_id
        self.registry = ActionRegistry()
        
        # Initialize any additional settings from config
        self.agent_distribution = config.get('agent_distribution', {})
        self.simulation_params = config.get('simulation_params', {})
        
        logger.info(f"Initialized AgentManager with {len(self.config['profiles'])} agent profiles")


    def _create_profile(self, profile_name: str) -> AgentProfile:
        """Create profile from configuration dictionary"""
        try:
            profile_config = self.config['profiles'][profile_name]
            return AgentProfile.from_dict(profile_name, profile_config)
        except KeyError as e:
            logger.error(f"Missing required configuration key for profile {profile_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating profile {profile_name}: {e}")
            raise

    def create_agent(self, profile_name: str) -> BaseAgent:
        """Create a new agent given a profile name."""
        profile = self._create_profile(profile_name)
        agent_id = str(uuid.uuid4())

        agent = BaseAgent(agent_id, profile, self.data_collector)
        
        # Record agent BEFORE creating any addresses
        if self.data_collector and self.data_collector.current_run_id:
            self.data_collector.record_agent(agent)
            
        # Now create address
        address, _ = agent.create_account()
        
        self.agents[agent_id] = agent
        self.address_to_agent[address] = agent_id
        

        return agent

    def create_agents(self, distribution: Optional[Dict[str, int]] = None) -> List[BaseAgent]:
        """Create multiple agents according to distribution"""
        distribution = distribution or self.agent_distribution
        created_agents = []
        
        for profile_name, count in distribution.items():
            for _ in range(count):
                agent = self.create_agent(profile_name)
                created_agents.append(agent)
                
        logger.info(f"Created {len(created_agents)} agents across {len(distribution)} profiles")
        return created_agents

    def get_agent_by_address(self, address: str) -> Optional[BaseAgent]:
        """Get agent instance by address"""
        agent_id = self.address_to_agent.get(address)
        return self.agents.get(agent_id)

    def register_address(self, address: str, agent_id: str):
        """Register a new address as belonging to an agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        self.address_to_agent[address] = agent_id

    def get_all_agents(self) -> List[BaseAgent]:
        """Get list of all registered agents"""
        return list(self.agents.values())