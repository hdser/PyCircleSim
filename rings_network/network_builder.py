from typing import List, Dict, Optional, Tuple
from ape import Contract, chain
import logging
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue
from datetime import datetime, timedelta

from .data_collector import CirclesDataCollector
from .agent_manager import AgentManager
from .base_agent import BaseAgent
from eth_account import Account
from eth_pydantic_types import HexBytes

logger = logging.getLogger(__name__)

class NetworkBuilder:
    """
    Enhanced NetworkBuilder with agent-based behavior and parallel processing.
    Actually performs on-chain transactions for registerHuman() and trust().
    """
    
    def __init__(
        self,
        contract_address: str,
        abi_path: str,
        batch_size: int = 1000,
        agent_manager: Optional[AgentManager] = None,
        data_collector: Optional[CirclesDataCollector] = None
    ):
        """
        Initialize NetworkBuilder with contract and optional data collection.
        
        Args:
            contract_address: Address of the Rings contract
            abi_path: Path to the contract ABI file
            batch_size: Number of accounts to process in each batch
            agent_manager: Optional AgentManager
            data_collector: Optional CirclesDataCollector
        """
        self.contract = Contract(contract_address, abi=abi_path)
        self.batch_size = batch_size
        self.registered_humans: Dict[str, bool] = {}
        
        # Data collection and agent management
        self.data_collector = data_collector
        self.agent_manager = agent_manager or AgentManager(config={})
        
        self.address_queue = queue.Queue(maxsize=batch_size * 2)
        self.executor = ThreadPoolExecutor(max_workers=min(32, batch_size))
        self.generation_progress = 0
        self.progress_lock = threading.Lock()
        self.current_simulation_id = None 

        # Event callbacks
        self.on_human_registered = None
        self.on_trust_created = None

    def build_large_network(
        self,
        target_size: int,
        profile_distribution: Dict[str, int]
    ) -> bool:
        """
        Build the network with the specified size and agent distribution.
        
        Args:
            target_size: Total number of agents to create
            profile_distribution: Dictionary mapping profile names to number of agents
        
        Returns:
            bool: True if network was built successfully
        """
        try:
            logger.info(f"Creating {target_size} agents with distribution: {profile_distribution}")
            
            # Create agents according to distribution
            created_agents = self.agent_manager.create_agents(profile_distribution)
            if len(created_agents) != target_size:
                logger.error(f"Created {len(created_agents)} agents, expected {target_size}")
                return False
                
            # Register humans on-chain for each newly created agent
            self._register_agent_batch(created_agents)
            
            # Establish initial trust relationships
            self._establish_initial_trust_network(created_agents)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to build network: {e}", exc_info=True)
            return False


    def _register_agent_batch(self, agents_data: List[BaseAgent]):
        """
        Register all agents as humans in the Rings contract (actual contract call).
        
        Args:
            agents_data: List of BaseAgent instances
        """
        registration_block = chain.blocks.head.number
        registration_time = datetime.fromtimestamp(chain.blocks.head.timestamp)
        
        for agent in agents_data:
            try:
                if not agent.accounts:
                    logger.warning(f"Agent {agent.agent_id} has no accounts to register.")
                    continue
                
                # Pick random address as the "primary" for registration
                address = random.choice(list(agent.accounts.keys()))
                private_key = agent.accounts[address]
                temp_account = Account.from_key(private_key)
                
                # Actual call to registerHuman in the contract
                receipt = self.contract.registerHuman(
                    "0x0000000000000000000000000000000000000000",
                    HexBytes(0),
                    sender=temp_account.address
                )
                
                self.registered_humans[address] = True

                # Fire callback
                if self.on_human_registered:
                    self.on_human_registered(
                        address=address,
                        inviter="0x0000000000000000000000000000000000000000",
                        block=registration_block,
                        timestamp=registration_time
                    )
                
                # Record in the data collector
                if self.data_collector and self.current_simulation_id:
                    self.data_collector.record_human_registration(
                        address=address,
                        block_number=registration_block,
                        timestamp=registration_time,
                        inviter_address="0x0000000000000000000000000000000000000000",
                        welcome_bonus=0.0
                    )
                    
            except Exception as e:
                logger.error(f"Failed to register agent {agent.agent_id}: {e}", exc_info=True)


    def _establish_initial_trust_network(self, agents: List[BaseAgent]):
        """
        Establish some initial trust relationships by actually calling self.contract.trust().
        """
        try:
            trust_block = chain.blocks.head.number
            trust_time = datetime.fromtimestamp(chain.blocks.head.timestamp)
            
            for agent in agents:
                potential_trustees = [a for a in agents if a != agent]
                random.shuffle(potential_trustees)
                
                # Suppose each agent tries to trust up to 2 random other agents
                for trustee_agent in potential_trustees[:2]:
                    if not agent.accounts:
                        continue
                    truster_address = random.choice(list(agent.accounts.keys()))
                    
                    if not trustee_agent.accounts:
                        continue
                    trustee_address = random.choice(list(trustee_agent.accounts.keys()))
                    
                    try:
                        trust_limit = 10_000_000
                        private_key = agent.accounts[truster_address]
                        truster_account = Account.from_key(private_key)
                        
                        # Actual contract call
                        receipt = self.contract.trust(
                            trustee_address,
                            trust_limit,
                            sender=truster_account.address
                        )
                        
                        # Update agent memory
                        agent.trusted_addresses.add(trustee_address)

                        # Fire callback if provided
                        if self.on_trust_created:
                            self.on_trust_created(
                                truster=truster_address,
                                trustee=trustee_address,
                                limit=trust_limit,
                                block=trust_block,
                                timestamp=trust_time
                            )
                        
                        # Record trust in data collector
                        if self.data_collector:
                            self.data_collector.record_trust_relationship(
                                truster=truster_address,
                                trustee=trustee_address,
                                block_number=trust_block,
                                timestamp=trust_time,
                                trust_limit=trust_limit,
                                expiry_time=trust_time + timedelta(days=365)
                            )

                    except Exception as e:
                        logger.error(f"Failed to create trust from {agent.agent_id} to {trustee_agent.agent_id}: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Failed to establish trust network: {e}", exc_info=True)
            raise

    def close(self):
        """Shutdown any resources if needed."""
        self.executor.shutdown(wait=True)

    def _create_trust_batch(self, trust_pairs: List[Dict]) -> Dict[Tuple[str, str], bool]:
        """Create trust relationships between pairs of accounts in batch (optional)."""
        results = {}
        for pair in trust_pairs:
            truster_addr, truster_key = pair['truster']
            trustee_addr, trustee_key = pair['trustee']
            try:
                truster_account = Account.from_key(truster_key)
                trust_limit = 10_000_000
                receipt = self.contract.trust(
                    trustee_addr,
                    trust_limit,
                    sender=truster_account.address
                )
                
                results[(truster_addr, trustee_addr)] = True
                
                if self.on_trust_created:
                    self.on_trust_created(
                        truster=truster_addr,
                        trustee=trustee_addr,
                        limit=trust_limit,
                        block=chain.blocks.head.number,
                        timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp)
                    )
                    
            except Exception as e:
                logger.error(f"Failed to create trust from {truster_addr} to {trustee_addr}: {e}", exc_info=True)
                results[(truster_addr, trustee_addr)] = False
                
        return results
    
    def create_trust_batch(self, trust_pairs: List[Dict]) -> Dict[Tuple[str, str], bool]:
        """
        Public method for creating trust relationships in batch.
        """
        return self._create_trust_batch(trust_pairs)
