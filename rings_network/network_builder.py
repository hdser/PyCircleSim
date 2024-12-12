from typing import List, Dict, Optional, Generator, Tuple
from eth_account import Account
from eth_pydantic_types import HexBytes
from ape import Contract, accounts, chain
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue
from .agent import AgentManager, Agent, AgentPersonality, AgentProfile
from datetime import datetime

logger = logging.getLogger(__name__)

class NetworkBuilder:
    """
    Enhanced NetworkBuilder with agent-based behavior and parallel processing
    """
    
    def __init__(self, contract_address: str, abi_path: str, batch_size: int = 1000, agent_manager: Optional[AgentManager] = None):
        self.contract = Contract(contract_address, abi=abi_path)
        self.batch_size = batch_size
        self.registered_humans: Dict[str, bool] = {}
        
        # Initialize agent manager
        self.agent_manager = agent_manager or AgentManager()
        
        # Thread-safe queue for address generation
        self.address_queue = queue.Queue(maxsize=batch_size * 2)
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=min(32, batch_size))
        
        # Progress tracking
        self.generation_progress = 0
        self.progress_lock = threading.Lock()
        
        # Callbacks
        self.on_human_registered = None
        self.on_trust_created = None

    def build_large_network(self, target_size: int, personality_weights: Optional[Dict[AgentPersonality, float]] = None) -> bool:
        """Build the complete network as a single operation"""
        try:
            logger.info(f"Starting network build for {target_size:,} agents")
            
            # Create all agents first
            agents_with_addresses = self.agent_manager.create_random_agents(
                target_size,
                personality_weights
            )
            
            # Register all agents in a single batch
            self._register_agent_batch(agents_with_addresses)
            
            # Establish trust relationships
            self._establish_initial_trust_network(agents_with_addresses)
            
            logger.info(f"Network build completed with {len(self.agent_manager.agents)} agents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to build network: {e}")
            return False

    def _register_agent_batch(self, agents_with_addresses: List[Tuple[Agent, str]]):
        """Register all agents in a single batch operation"""
        # Record the current block for consistent event recording
        registration_block = chain.blocks.head.number
        registration_time = datetime.fromtimestamp(chain.blocks.head.timestamp)
        
        for agent, address in agents_with_addresses:
            try:
                private_key = agent.accounts[address]
                temp_account = Account.from_key(private_key)
                
                receipt = self.contract.registerHuman(
                    "0x0000000000000000000000000000000000000000",
                    HexBytes(0),
                    sender=temp_account.address
                )
                
                self.registered_humans[address] = True
                
                if self.on_human_registered:
                    # Use consistent block/time for all registrations
                    self.on_human_registered(
                        address=address,
                        inviter=None,
                        block=registration_block,
                        timestamp=registration_time
                    )
                    
            except Exception as e:
                logger.error(f"Failed to register agent {address}: {e}")

    def _establish_initial_trust_network(self, agents_with_addresses: List[Tuple[Agent, str]]):
        """Establish initial trust relationships in a single batch"""
        try:
            trust_block = chain.blocks.head.number
            trust_time = datetime.fromtimestamp(chain.blocks.head.timestamp)
            trust_pairs = []
            
            # Collect all potential trust relationships
            for i, (agent1, addr1) in enumerate(agents_with_addresses):
                for j, (agent2, addr2) in enumerate(agents_with_addresses):
                    if i != j and agent1.should_trust(agent2):
                        trust_pairs.append({
                            'truster': (addr1, agent1.accounts[addr1]),
                            'trustee': (addr2, agent2.accounts[addr2])
                        })
            
            # Process all trust relationships
            for pair in trust_pairs:
                try:
                    truster_addr, truster_key = pair['truster']
                    trustee_addr = pair['trustee'][0]
                    
                    truster_account = Account.from_key(truster_key)
                    receipt = self.contract.trust(
                        trustee_addr,
                        10000000,
                        sender=truster_account.address
                    )
                    
                    if self.on_trust_created:
                        # Use consistent block/time for all trust relationships
                        self.on_trust_created(
                            truster=truster_addr,
                            trustee=trustee_addr,
                            limit=10000000,
                            block=trust_block,
                            timestamp=trust_time
                        )
                        
                except Exception as e:
                    logger.error(f"Failed to create trust from {truster_addr} to {trustee_addr}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to establish trust network: {e}")
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