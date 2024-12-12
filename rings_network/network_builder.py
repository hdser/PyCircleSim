from typing import List, Dict, Optional, Generator, Tuple
from eth_account import Account
from eth_pydantic_types import HexBytes
from ape import Contract, accounts, chain
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue
from .agent import AgentManager, Agent, AgentPersonality, AgentProfile
from .data_collector import CirclesDataCollector
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NetworkBuilder:
    """
    Enhanced NetworkBuilder with agent-based behavior and parallel processing
    """
    
    def __init__(self, contract_address: str, abi_path: str, batch_size: int = 1000, 
                 agent_manager: Optional[AgentManager] = None,
                 data_collector: Optional['CirclesDataCollector'] = None):
        """Initialize NetworkBuilder with contract and optional data collection."""
        self.contract = Contract(contract_address, abi=abi_path)
        self.batch_size = batch_size
        self.registered_humans: Dict[str, bool] = {}
        
        # Data collection and agent management
        self.data_collector = data_collector
        self.agent_manager = agent_manager or AgentManager(data_collector)
        
        self.address_queue = queue.Queue(maxsize=batch_size * 2)
        self.executor = ThreadPoolExecutor(max_workers=min(32, batch_size))
        self.generation_progress = 0
        self.progress_lock = threading.Lock()
        self.current_simulation_id = None 

        self.on_human_registered = None
        self.on_trust_created = None


    def build_large_network(self, target_size: int, 
                            personality_weights: Optional[Dict[AgentPersonality, float]] = None,
                            simulation_params: Optional[Dict] = None) -> bool:
        """
        Build the complete network as a single operation.
        
        Args:
            target_size: Number of agents to create
            personality_weights: Optional weights for different personality types
            simulation_params: Optional parameters to record with the simulation run
        """
        try:
            logger.info(f"Starting network build for {target_size:,} agents")
            

            # Create and register agents
            agents_with_addresses = self.agent_manager.create_random_agents(
                target_size,
                personality_weights
            )
            
            self._register_agent_batch(agents_with_addresses)
            self._establish_initial_trust_network(agents_with_addresses)
            
            # Record final network statistics if we're collecting data
            if self.data_collector:
                self.data_collector.record_network_statistics(
                    block_number=chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp)
                )
                
            logger.info(f"Network build completed with {len(self.agent_manager.agents)} agents")
            return True

        except Exception as e:
            logger.error(f"Failed to build network: {str(e)}")
            return False


    def _register_agent_batch(self, agents_data: List[Tuple[Agent, str, str]]):
        """
        Register all agents in a single batch operation.
        
        Args:
            agents_data: List of tuples (Agent, agent_id, primary_address)
        """
        # Record the current block for consistent event recording
        registration_block = chain.blocks.head.number
        registration_time = datetime.fromtimestamp(chain.blocks.head.timestamp)
        
        for agent, agent_id, address in agents_data:
            try:
                private_key = agent.accounts[address]
                temp_account = Account.from_key(private_key)
                
                receipt = self.contract.registerHuman(
                    "0x0000000000000000000000000000000000000000",
                    HexBytes(0),
                    sender=temp_account.address
                )
                
                self.registered_humans[address] = True
                
                # Trigger the registration event with correct parameter names
                if self.on_human_registered:
                    self.on_human_registered(
                        address=address,
                        inviter="0x0000000000000000000000000000000000000000",  # Changed from inviter_address to inviter
                        block=registration_block,
                        timestamp=registration_time
                    )
                
                # Record the registration if we have a collector
                if self.data_collector and self.current_simulation_id:
                    self.data_collector.record_human_registration(
                        address=address,
                        inviter_address="0x0000000000000000000000000000000000000000",
                        block_number=registration_block,
                        timestamp=registration_time
                    )
                    
            except Exception as e:
                logger.error(f"Failed to register agent {agent_id} (address: {address}): {str(e)}")




    def _establish_initial_trust_network(self, agents_data: List[Tuple[Agent, str, str]]):
        """
        Establish initial trust relationships in a single batch.
        
        Args:
            agents_data: List of tuples (Agent, agent_id, primary_address)
        """
        try:
            trust_block = chain.blocks.head.number
            trust_time = datetime.fromtimestamp(chain.blocks.head.timestamp)
            
            for i, (agent1, agent_id1, addr1) in enumerate(agents_data):
                for j, (agent2, agent_id2, addr2) in enumerate(agents_data):
                    if i != j and agent1.should_trust(agent2):
                        try:
                            truster_account = Account.from_key(agent1.accounts[addr1])
                            trust_limit = 10000000

                            receipt = self.contract.trust(
                                addr2,
                                trust_limit,
                                sender=truster_account.address
                            )

                            # Trigger the trust creation event
                            if self.on_trust_created:
                                self.on_trust_created(
                                    truster=addr1,
                                    trustee=addr2,
                                    limit=trust_limit,
                                    block=trust_block,
                                    timestamp=trust_time
                                )
                            
                            # Record the trust relationship if we have a collector
                            if self.data_collector:
                                self.data_collector.record_trust_relationship(
                                    truster=addr1,
                                    trustee=addr2,
                                    block_number=trust_block,
                                    timestamp=trust_time,
                                    trust_limit=trust_limit,
                                    expiry_time=trust_time + timedelta(days=365)
                                )
                                
                        except Exception as e:
                            logger.error(f"Failed to create trust from {addr1} to {addr2}: {str(e)}")
                            
        except Exception as e:
            logger.error(f"Failed to establish trust network: {str(e)}")
            raise

    def _create_trust_batch(self, trust_pairs: List[Dict]) -> Dict[Tuple[str, str], bool]:
        """Create trust relationships between pairs of accounts in batch"""
        results = {}
        
        for pair in trust_pairs:
            truster_addr, truster_key = pair['truster']
            trustee_addr, trustee_key = pair['trustee']
            
            try:
                truster_account = Account.from_key(truster_key)
                receipt = self.contract.trust(
                    trustee_addr,
                    10000000,  # Standard trust limit
                    sender=truster_account.address
                )
                
                results[(truster_addr, trustee_addr)] = True
                
                if self.on_trust_created:
                    self.on_trust_created(truster_addr, trustee_addr, 10000000)
                    
            except Exception as e:
                logger.error(f"Failed to create trust from {truster_addr} to {trustee_addr}: {e}")
                results[(truster_addr, trustee_addr)] = False
                
        return results
    
    def create_trust_batch(self, trust_pairs: List[Dict]) -> Dict[Tuple[str, str], bool]:
        """Public method for creating trust relationships in batch"""
        return self._create_trust_batch(trust_pairs)