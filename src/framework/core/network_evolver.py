from typing import Dict, Optional, Any, List, Tuple
from datetime import datetime
import random
from ape import chain
from src.framework.agents.agent_manager import AgentManager
from src.framework.agents.base_agent import BaseAgent
from src.framework.data import DataCollector
from src.framework.logging import get_logger
from .context import SimulationContext
import importlib 

logger = get_logger(__name__)

class NetworkEvolver():
    def __init__(
        self,
        clients: Dict[str, Any],
        agent_manager: AgentManager,
        collector: Optional[DataCollector] = None,
        gas_limits: Optional[Dict] = None,
    ):
        self.clients = clients
        self.agent_manager = agent_manager
        self.collector = collector
        self.gas_limits = gas_limits
        self._iteration_cache = {}
        
        self.network_state = {
            'current_block': 0,
            'current_time': 0,
            'contract_states': {},
            'running_state': {}
        }

        # Initialize master handler
        self.master_handler = None
        if 'master' in self.clients:
            from src.protocols.interfaces.master.master_handler import MasterHandler
            self.master_handler = MasterHandler(
                client=self.clients['master'],
                chain=chain,
                logger=logger
            )
            logger.info("Master handler initialized")

    def set_simulation(self, simulation: 'BaseSimulation'):
        """Set the simulation instance"""
        self.simulation = simulation

    def initialize_contract_states(self, contract_states: Dict[str, Dict[str, Any]]):
        """Initialize per-contract state data"""
        self.network_state['contract_states'] = contract_states

    def get_contract_state(self, contract_id: str, var_name: str, default: Any = None) -> Any:
        """Get specific contract state variable"""
        contract_state = self.network_state['contract_states'].get(contract_id, {}).get('state', {})
        return contract_state.get(var_name, default)

   
    def _initialize_handlers(self):
        """Initialize all available handlers"""
        # Only initialize master handler
        if 'master' in self.clients:
            from src.protocols.interfaces.master.master_handler import MasterHandler
            self.handlers['master_execute'] = MasterHandler(
                client=self.clients['master'],
                chain=chain,
                logger=logger
            )
            logger.info("Master handler initialized")

        
                
    def _get_client_for_module(self, module_name: str) -> Any:
        """Get appropriate client for module"""
        return self.clients.get(module_name)
        
            
    def advance_time(self, blocks: int, block_time: int = 5) -> bool:
        """
        Advance chain time by specified blocks
        """
        try:
            batch_size = 5
            total_mined = 0
            
            while total_mined < blocks:
                current_batch = min(batch_size, blocks - total_mined)
                chain.mine(current_batch)
                chain.pending_timestamp += current_batch * block_time
                total_mined += current_batch

            logger.debug(
                f"Advanced chain by {blocks} blocks. "
                f"New block: {chain.blocks.head.number}, "
                f"Time: {datetime.fromtimestamp(chain.blocks.head.timestamp)}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to advance time: {e}", exc_info=True)
            return False
            
    def evolve_network(self, iteration: int) -> Dict[str, int]:
        """Main evolution loop"""
        self._iteration_cache.clear()
        stats = {'total_actions': 0, 'successful_actions': 0, 'action_counts': {}}
        
        try:
            logger.debug(f"Starting iteration {iteration}")
            logger.debug(f"Master handler present: {self.master_handler is not None}")
            logger.debug(f"Master client present: {bool(self.clients.get('master'))}")

            all_agents = list(self.agent_manager.agents.values())
            random.shuffle(all_agents)

            self.network_state.update({
                'current_block': chain.blocks.head.number,
                'current_time': chain.blocks.head.timestamp,
            })

            for agent in all_agents:
                logger.debug(f"Processing agent {agent.agent_id}")
                context = SimulationContext(
                    agent=agent,
                    acting_address='',
                    agent_manager=self.agent_manager, 
                    clients=self.clients,
                    chain=chain,
                    network_state=self.network_state,
                    simulation=self.simulation,
                    iteration=iteration,
                    iteration_cache=self._iteration_cache
                )

                implementation, acting_address = agent.select_action(
                    self.network_state['current_block'],
                    self.network_state
                )

                if not implementation:
                    logger.debug("No implementation selected")
                    continue

                if not self.master_handler:
                    logger.debug("No master handler available")
                    continue

                logger.info(f"Executing implementation {implementation} for address {acting_address}")
                
                params = {
                    'sender': acting_address,
                    'implementation': implementation
                }
                context.acting_address = acting_address
                stats['total_actions'] += 1
                success = self.master_handler.execute(context, params)
                
                if success:
                    stats['successful_actions'] += 1
                    stats['action_counts'][implementation] = stats['action_counts'].get(implementation, 0) + 1
                    
                agent.record_action(
                    action_name=implementation,
                    address=acting_address,
                    block_number=self.network_state['current_block'],
                    success=success,
                    context=context
                )

            return stats
            
        except Exception as e:
            logger.error(f"Network evolution failed: {e}", exc_info=True)
            return stats
        
    
        
    def _select_action(self, context: SimulationContext) -> Optional[str]:
        """Select an action for the agent to perform"""
        try:
            action_name, acting_address, params = context.agent.select_action(
                current_block=self.network_state['current_block'],
                network_state=self.network_state
            )
            if action_name is None:
                return None

            if not self.handlers.get(action_name):
                logger.debug(f"No handler found for action {action_name}")
                return None

            return action_name

        except Exception as e:
            logger.error(f"Failed to select action: {e}")
            return None
        
            
    def _check_action_timing(self, agent_id: str, current_block: int) -> bool:
        """Check if enough blocks have passed since last action"""
        last_action = self.last_action_times.get(agent_id, 0)
        blocks_passed = current_block - last_action
        return blocks_passed >= self.min_blocks_between_actions