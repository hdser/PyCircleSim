from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Set
from src.framework.agents.agent_manager import AgentManager
from src.framework.agents.base_agent import BaseAgent
import time
from src.framework.logging import get_logger
import logging
from src.pathfinder import GraphManager
from datetime import datetime

logger = get_logger(__name__)

@dataclass
class CacheEntry:
    """Represents a cached value with timestamp"""
    value: Any
    timestamp: float
    
class SimulationContext:
    """Encapsulates the context needed for simulation actions with caching"""
    def __init__(
        self,
        agent: BaseAgent,
        acting_address: str,
        agent_manager: AgentManager,
        clients: Dict[str, Any],
        chain: Any,
        network_state: Dict[str, Any],
        simulation: 'BaseSimulation', 
        iteration: int,
        iteration_cache: Dict[str, Any]
    ):
        self.agent = agent
        self.acting_address = acting_address
        self.agent_manager = agent_manager
        self.clients = clients
        self.chain = chain
        self.network_state = network_state
        self.simulation = simulation
        self.iteration = iteration
        self._cache = iteration_cache
        self.graph_manager: Optional[GraphManager] = None
        self._last_graph_rebuild: Optional[datetime] = None
        self.current_action: Optional[str] = None 

        
    def rebuild_graph(self) -> None:
        """Rebuild graph if needed"""
        if not hasattr(self.simulation, '_rebuild_graph'):
            return
            
        current_time = datetime.now()
        if (not self._last_graph_rebuild or 
            (current_time - self._last_graph_rebuild).total_seconds() > 1):  # Rate limit rebuilds
            self.simulation._rebuild_graph(self)
            self._last_graph_rebuild = current_time

    def get_client(self, contract_id: str) -> Any:
        """Get client for specific contract"""
        return self.clients.get(contract_id)

    def get_contract_state(self, contract_id: str, var_name: str, default: Any = None) -> Any:
        """Helper to get contract state"""
        return self.network_state.get('contract_states', {}).get(contract_id, {}).get('state', {}).get(var_name, default)

    def get_running_state(self, key: str, default: Any = None) -> Any:
        """Helper to get running state"""
        return self.network_state.get('running_state', {}).get(key, default)

    def update_running_state(self, updates: Dict[str, Any]):
        """Helper to update running state"""
        if 'running_state' not in self.network_state:
            self.network_state['running_state'] = {}
        self.network_state['running_state'].update(updates)


    def get_cache_key(self, base_key: str, identifiers: Dict[str, Any] = None) -> str:
        """Generate consistent cache keys"""
        if not identifiers:
            return base_key
            
        # For block-dependent data, use block ranges instead of exact blocks
        if 'block' in identifiers:
            # Cache for 10 blocks
            block_range = identifiers['block'] // 10
            return f"{base_key}_block_{block_range}"
            
        # For agent data, use short identifier
        if 'agent_id' in identifiers:
            short_id = identifiers['agent_id'][:8]
            return f"{base_key}_agent_{short_id}"
            
        return base_key

    def get_cached(self, key: str) -> Optional[Any]:
        """Get a cached value if still valid"""
        entry = self._cache.get(key)
        if not entry:
            return None
        
        if time.time() - entry.timestamp > self.cache_ttl:
            del self._cache[key]
            return None
            
        return entry.value
    

    def get_or_cache(self, key: str, generator_func):
        iteration_key = f"{key}_iter_{self.iteration}"
        if iteration_key in self._cache.keys():
            logger.debug(f"Cache hit for {key}")
            return self._cache[iteration_key]
                
        logger.debug(f"Cache miss for {key}")
        result = generator_func()
        self._cache[iteration_key] = result
        return result
        
    # Helper methods for common cached operations
    def get_filtered_addresses(self, predicate_func, cache_key: Optional[str] = None) -> List[str]:
        """Get filtered addresses with iteration-based caching"""
        if not cache_key:
            return [addr for addr in self.agent_manager.address_to_agent.keys() 
                   if predicate_func(addr)]
                   
        iteration_key = f"{cache_key}_iter_{self.iteration}"
        
        if iteration_key in self._cache:
            logger.debug(f"Cache hit for {iteration_key}")
            return self._cache[iteration_key]
            
        logger.debug(f"Cache miss for {cache_key}")
        result = [addr for addr in self.agent_manager.address_to_agent.keys() 
                 if predicate_func(addr)]
        self._cache[iteration_key] = result
        return result
    

    #------------------------------------
    # Balancer V2 specific methods
    #------------------------------------
    def find_swap_path(self, start_token: str, end_token: str) -> List[Dict]:
        """Find path between tokens using Balancer pools"""
        if not hasattr(self.simulation, 'find_token_path'):
            logger.warning("Simulation does not have find_token_path method")
            return []
        return self.simulation.find_token_path(start_token, end_token)