from typing import Dict, Optional, List, Any, Tuple
from datetime import datetime
import random
import logging

from ape import chain
from eth_pydantic_types import HexBytes

from src.framework.agents import AgentManager, BaseAgent
from src.framework.data import DataCollector
from src.protocols.ringshub import RingsHubClient

from src.protocols.ringshub import (
    PersonalMintHandler,
    RegisterHumanHandler,
    TrustHandler,
    RegisterGroupHandler
)

from src.framework.logging import get_logger

logger = get_logger(__name__)

class BatchExecutionResult:
    """Container for batch execution results"""
    def __init__(self):
        self.total = 0
        self.successful = 0
        self.failed = 0
        self.errors = []

class NetworkBuilder():
    """Enhanced NetworkBuilder using handler-based architecture"""
    
    def __init__(
        self,
        client: RingsHubClient,
        batch_size: int = 10,
        agent_manager: Optional[AgentManager] = None,
        collector: Optional[DataCollector] = None
    ):

        self.client = client
        self.batch_size = batch_size
        self.agent_manager = agent_manager
        self.collector = collector
        
        # Initialize handlers
        self.register_human_handler = RegisterHumanHandler(
            client=self.client,
            chain=chain,
            logger=logger
        )
        
        self.trust_handler = TrustHandler(
            client=self.client,
            chain=chain,
            logger=logger
        )
        
        self.mint_handler = PersonalMintHandler(
            client=self.client,
            chain=chain,
            logger=logger
        )
        
        self.group_handler = RegisterGroupHandler(
            client=self.client,
            chain=chain,
            logger=logger
        )

    def build_large_network(
        self,
        target_size: int,
        profile_distribution: Dict[str, int]
    ) -> bool:
        try:
            logger.info(f"Creating {target_size} agents with distribution: {profile_distribution}")
            
            # Create agents
            created_agents = self.agent_manager.create_agents(profile_distribution)
            if len(created_agents) != target_size:
                logger.error(f"Created {len(created_agents)} agents, expected {target_size}")
                return False
            
            # Create accounts for each agent based on their profile
            for agent in created_agents:
                self._ensure_agent_accounts(agent)
            
            # Register humans in batches
            if not self._batch_register_humans(created_agents):
                return False
            
            # Establish initial trust relationships
            if not self._establish_initial_trust(created_agents):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to build network: {e}", exc_info=True)
            return False
            
    def _ensure_agent_accounts(self, agent: BaseAgent):
        """Make sure agent has required number of accounts"""
        target_accounts = agent.profile.target_account_count
        current_accounts = len(agent.accounts)
        
        # Create additional accounts if needed
        for _ in range(current_accounts, target_accounts):
            agent.create_account()

    def _batch_register_humans(self, agents: List[BaseAgent]) -> bool:
        """Register humans in batches"""
        total_registrations = 0
        total_failures = 0
        
        try:
            for batch in self._get_agent_batches(agents):
                result = self._execute_registration_batch(batch)
                total_registrations += result.successful
                total_failures += result.failed
                
                if result.failed > 0:
                    logger.warning(f"Batch had {result.failed} registration failures")
                
                logger.info(f"Batch registration complete - Success: {result.successful}, Failed: {result.failed}")
                
            # Check overall success rate
            if total_failures > total_registrations * 0.2:  # Allow up to 20% failure rate
                logger.error(f"Too many registration failures: {total_failures} out of {total_registrations + total_failures}")
                return False
                
            return True
                
        except Exception as e:
            logger.error(f"Batch registration failed: {e}")  
            return False
            
    def _execute_registration_batch(self, agents: List[BaseAgent]) -> BatchExecutionResult:
        """Execute a batch of registrations"""
        result = BatchExecutionResult()
        
        for agent in agents:
            try:
                # Get primary account for registration
                primary_account = next(iter(agent.accounts.keys()))
                if not primary_account:
                    logger.error(f"Agent {agent.agent_id} has no accounts")
                    result.failed += 1
                    continue

                success = self.register_human_handler.execute(
                    agent,
                    params={
                        'sender': primary_account,
                        '_inviter': "0x0000000000000000000000000000000000000000",
                        '_metadataDigest': HexBytes(0),
                    }
                )
                
                result.total += 1
                if success:
                    result.successful += 1
                else:
                    result.failed += 1
                    
            except Exception as e:
                result.failed += 1
                result.errors.append(str(e))
                logger.error(f"Registration failed for agent {agent.agent_id}: {e}")
                
        return result

    def _establish_initial_trust(self, agents: List[BaseAgent]) -> bool:
        """Create initial trust relationships"""
        trust_failures = 0
        total_trust = 0
        
        for agent in agents:
            # Select random trustees
            potential_trustees = [a for a in agents if a != agent] 
            random.shuffle(potential_trustees)
            target_trustees = potential_trustees[:2]  # Trust up to 2 random agents
            
            for trustee in target_trustees:
                try:
                    if not agent.accounts or not trustee.accounts:
                        continue
                        
                    truster_addr = next(iter(agent.accounts.keys()))  # Get primary account
                    trustee_addr = next(iter(trustee.accounts.keys()))  # Get trustee's primary account
                    
                    # Calculate trust expiry (1 year)
                    expiry = int(chain.blocks.head.timestamp + 365 * 24 * 60 * 60)
                    
                    success = self.trust_handler.execute(
                        agent,
                        params={
                            'sender': truster_addr,
                            '_trustReceiver': trustee_addr,
                            '_expiry': expiry,
                        }
                    )
                    
                    total_trust += 1
                    if not success:
                        trust_failures += 1
                        
                    if success:
                        agent.trusted_addresses.add(trustee_addr)
                        
                except Exception as e:
                    trust_failures += 1
                    logger.error(f"Trust establishment failed: {e}")

        # Allow some failures but ensure majority succeed
        if trust_failures > total_trust / 2:
            logger.error(f"Too many trust failures: {trust_failures}/{total_trust}")
            return False
            
        return True

    def _get_agent_batches(self, agents: List[BaseAgent]) -> List[List[BaseAgent]]:
        """Split agents into batches"""
        for i in range(0, len(agents), self.batch_size):
            yield agents[i:i + self.batch_size]

    def verify_network_state(self) -> bool:
        """Verify network build state"""
        try:
            # Verify all agents are registered
            for agent in self.agent_manager.get_all_agents():
                registered = False
                for addr in agent.accounts.keys():
                    if self.client.isHuman(addr):
                        registered = True
                        break
                if not registered:
                    logger.error(f"Agent {agent.agent_id} not properly registered")
                    return False
                    
            # Verify trust network density
            total_agents = len(self.agent_manager.agents)
            total_trust = sum(
                len(agent.trusted_addresses) 
                for agent in self.agent_manager.agents.values()
            )
            
            avg_trust = total_trust / total_agents if total_agents > 0 else 0
            if avg_trust < 1.5:  # Each agent should trust ~2 others
                logger.warning(f"Low trust density: {avg_trust:.2f} average trust connections")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Network state verification failed: {e}")
            return False