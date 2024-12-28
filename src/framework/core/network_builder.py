from typing import Dict, Optional, List, Any
from datetime import datetime
import logging
from ape import chain
import random

from src.protocols.rings import RingsClient
from src.protocols.fjord import FjordClient
from src.framework.data import CirclesDataCollector
from src.framework.agents import AgentManager, BaseAgent
from .network_component import NetworkComponent
from .network_actions import NetworkActionExecutor, ActionRegistry, HumanRegistrationAction, TrustCreationAction, TokenMintAction
from src.framework.logging import get_logger

logger = get_logger(__name__)

class NetworkBuilder(NetworkComponent):
    """Enhanced NetworkBuilder using modular action system"""
    
    def __init__(
        self,
       # contract_address: str,
        #abi_path: str,
        rings_client: RingsClient,
        batch_size: int = 1000,
        agent_manager: Optional[AgentManager] = None,
        data_collector: Optional[CirclesDataCollector] = None
    ):
        super().__init__()
        
        # Initialize clients
        #self.rings_client = RingsClient(contract_address, abi_path)
        self.rings_client = rings_client
        self.fjord_client=None #self.fjord_client = FjordClient(...)  # Initialize with appropriate params
        
        self.batch_size = batch_size
        self.agent_manager = agent_manager
        self.collector = data_collector
        
        # Initialize action registry
        self.registry = ActionRegistry()
        self._register_default_actions()
        
        # Initialize executor
        self.executor = NetworkActionExecutor(self.registry)

    def _register_default_actions(self):
        """Register default network actions"""
        self.registry.register_action(
            'register_human',
            HumanRegistrationAction(
                self.rings_client,
                self.fjord_client,
                self.collector
            )
        )
        
        self.registry.register_action(
            'create_trust',
            TrustCreationAction(
                self.rings_client,
                self.fjord_client,
                self.collector
            )
        )
        
        self.registry.register_action(
            'mint_tokens',
            TokenMintAction(
                self.rings_client,
                self.fjord_client,
                self.collector
            )
        )
        # Register additional actions as needed

    def build_large_network(
        self,
        target_size: int,
        profile_distribution: Dict[str, int]
    ) -> bool:
        """Build network using action system"""
        try:
            logger.info(f"Creating {target_size} agents with distribution: {profile_distribution}")
            
            # Create agents
            created_agents = self.agent_manager.create_agents(profile_distribution)
            if len(created_agents) != target_size:
                logger.error(f"Created {len(created_agents)} agents, expected {target_size}")
                return False
                
            # Register humans in batches
            for batch in self._get_agent_batches(created_agents):
                registration_actions = [
                    ('register_human', agent, {
                        'address': agent.get_random_account()[0],
                        'inviter': None,
                        'metadata_digest': None
                    })
                    for agent in batch
                ]
                
                results = self.executor.batch_execute(registration_actions)
                if not all(r.success for r in results):
                    logger.error("Some registrations failed")
                    return False
                    
            # Establish initial trust relationships
            self._establish_initial_trust(created_agents)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to build network: {e}", exc_info=True)
            return False

    def _establish_initial_trust(self, agents: List[BaseAgent]):
        """Create initial trust relationships"""
        for agent in agents:
            potential_trustees = [a for a in agents if a != agent]
            random.shuffle(potential_trustees)
            
            for trustee in potential_trustees[:2]:  # Trust up to 2 random agents
                if not agent.accounts or not trustee.accounts:
                    continue
                    
                # Execute trust action with unpacked parameters
                result = self.executor.execute_action(
                    action_name='create_trust',
                    agent=agent,
                    truster=agent.get_random_account()[0],
                    trustee=trustee.get_random_account()[0],
                    expiry=int(chain.blocks.head.timestamp + 365*24*60*60)
                )
                
                if result.success:
                    agent.trusted_addresses.add(trustee.get_random_account()[0])

    def _get_agent_batches(self, agents: List[BaseAgent]):
        """Split agents into batches"""
        for i in range(0, len(agents), self.batch_size):
            yield agents[i:i + self.batch_size]

