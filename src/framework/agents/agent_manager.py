import yaml
from typing import Dict, List, Optional
from .base_agent import BaseAgent, AgentProfile, ActionType, ActionConfig
from src.framework.data import BaseDataCollector
import logging
import uuid

logger = logging.getLogger(__name__)

class AgentManager:
    """
    Manages the creation and tracking of agents in the simulation
    """
    def __init__(self, config: Dict, data_collector: Optional['BaseDataCollector'] = None):
        """
        Initialize the agent manager
        
        Args:
            config: Agent configuration dictionary
            data_collector: Optional data collector for recording agent actions
        """
        self.config = config
        self.data_collector = data_collector
        self.agents: Dict[str, BaseAgent] = {}
        self.address_to_agent: Dict[str, str] = {}  # address -> agent_id
        
        # Initialize any additional settings from config
        self.agent_distribution = config.get('agent_distribution', {})
        self.simulation_params = config.get('simulation_params', {})
        
        logger.info(f"Initialized AgentManager with {len(self.config['profiles'])} agent profiles")


    def _load_config(self, config_path: str) -> Dict:
        """Load and validate configuration file"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Validate configuration
        required_keys = {'profiles', 'simulation_params'}
        if not all(key in config for key in required_keys):
            raise ValueError(f"Configuration must contain keys: {required_keys}")
            
        return config

    def _create_profile(self, profile_name: str) -> AgentProfile:
        """
        Create an AgentProfile from the config dictionary for the named profile.
        """
        profile_config = self.config['profiles'][profile_name]
        
        # Convert action_configs from dict to ActionConfig objects
        action_configs = {}
        for action_str, cfg in profile_config['actions'].items():
            action_type = ActionType[action_str]     # e.g. "MINT" -> ActionType.MINT
            action_configs[action_type] = ActionConfig(
                probability=cfg['probability'],
                cooldown_blocks=cfg['cooldown_blocks'],
                gas_limit=cfg['gas_limit'],
                min_balance=cfg['min_balance'],
                max_value=cfg['max_value'],
                constraints=cfg.get('constraints', {})
            )
        
        # Build the AgentProfile
        profile = AgentProfile(
            name=profile_name,
            description=profile_config.get('description', ''),
            action_configs=action_configs,
            target_account_count=profile_config.get('target_account_count', 1),
            max_daily_actions=profile_config.get('max_daily_actions', 10),
            risk_tolerance=profile_config.get('risk_tolerance', 0.5),
            preferred_contracts=profile_config.get('preferred_contracts', [])
        )
        return profile

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
        """
        Create multiple agents according to distribution
        
        Args:
            distribution: Optional dictionary of profile_name -> count
                        If not provided, uses configuration distribution
        """
        distribution = distribution or self.agent_distribution
        created_agents = []
        
        for profile_name, count in distribution.items():
            for _ in range(count):
                agent = self.create_agent(profile_name)
                created_agents.append(agent)
                
        logger.info(f"Created {len(created_agents)} agents across {len(distribution)} profiles")
        return created_agents

    def get_agent_by_address(self, address: str) -> Optional[BaseAgent]:
        """Get agent instance by any of their account addresses"""
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

    def get_simulation_params(self) -> Dict:
        """Get simulation parameters from configuration"""
        return self.config['simulation_params']