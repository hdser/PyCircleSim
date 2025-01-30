from typing import Dict, Optional, Any, List, Tuple
from datetime import datetime
import random
from ape import chain
from src.framework.agents import AgentManager, BaseAgent, ActionType
from src.framework.data import DataCollector
from src.framework.logging import get_logger
from .context import SimulationContext
import importlib 

logger = get_logger(__name__)

class NetworkEvolver():
    """Enhanced NetworkEvolver with dynamic action handling"""
    
    def __init__(
        self,
        clients: Dict[str, Any],
        agent_manager: AgentManager,
        collector: Optional[DataCollector] = None,
        gas_limits: Optional[Dict] = None,
        strategy_config: Optional[Dict] = None
    ):
        self.clients = clients
        self.agent_manager = agent_manager
        self.collector = collector
        self.gas_limits = gas_limits
        self.strategy_config = strategy_config
        self._iteration_cache = {}
        
        # Track last action times
        self.last_action_times: Dict[str, int] = {}
        self.min_blocks_between_actions = 5
        
        self.network_state = {
            'current_block': 0,
            'current_time': 0,
            'contract_states': {},  # Will store per-contract state
            'running_state': {}     # For dynamic state
        }

        # Initialize all available handlers
        self.handlers = {}
        self._initialize_handlers()

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
        """Initialize all available action handlers with configured strategies"""
        registry = self.agent_manager.registry

        for action_name, metadata in registry._actions.items():
            try:
                interface_path = f"src.protocols.interfaces.{metadata.module_name}"
                module = importlib.import_module(interface_path)
                handler_class = getattr(module, metadata.handler_class)

                client = self._get_client_for_module(metadata.module_name)
                if not client:
                    continue

                strategy = getattr(self, 'strategy_config', {}).get(
                    metadata.module_name,
                    'basic'
                )
                
                handler = handler_class(
                    client=client,
                    chain=chain,
                    logger=logger,
                    strategy_name=strategy
                )
                
                # Store the handler directly since it includes its own strategy
                self.handlers[action_name] = handler
                
                logger.info(
                    f"Initialized handler {action_name} with {strategy} strategy"
                )
                
            except Exception as e:
                logger.error(
                    f"Failed to initialize handler for {action_name}: {e}",
                    exc_info=True
                )

    def _initialize_handlers2(self):
        """Initialize all available action handlers with configured strategies"""
        registry = self.agent_manager.registry

        for action_name, metadata in registry._actions.items():
            try:
                interface_path = f"src.protocols.interfaces.{metadata.module_name}"
                module = importlib.import_module(interface_path)
                handler_class = getattr(module, metadata.handler_class)

                client = self._get_client_for_module(metadata.module_name)
                if not client:
                    continue

                strategy = getattr(self, 'strategy_config', {}).get(
                    metadata.module_name,
                    'basic'
                )
                
                handler = handler_class(
                    client=client,
                    chain=chain,
                    logger=logger,
                    strategy_name=strategy
                )
                self.handlers[action_name] = handler
                
                logger.info(
                    f"Initialized handler {action_name} with {strategy} strategy"
                )
                
            except Exception as e:
                logger.error(
                    f"Failed to initialize handler for {action_name}: {e}",
                    exc_info=True
                )
        
                
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
        self._iteration_cache.clear()

        stats = {
            'total_actions': 0,
            'successful_actions': 0,
            'action_counts': {}
        }
        
        try:
            all_agents = list(self.agent_manager.agents.values())
            random.shuffle(all_agents)

            self.network_state.update({
                'current_block': chain.blocks.head.number,
                'current_time': chain.blocks.head.timestamp,
            })
            import time
            for agent in all_agents:
                if not self._check_action_timing(agent.agent_id, self.network_state['current_block']):
                    continue

                # Pass all clients to context
                context = SimulationContext(
                    agent=agent,
                    agent_manager=self.agent_manager,
                    clients=self.clients,
                    chain=chain,
                    network_state=self.network_state,
                    simulation=self.simulation,
                    iteration=iteration,
                    iteration_cache=self._iteration_cache
                )
                
                action_name = self._select_action(context)
                if not action_name:
                    continue

                handler = self.handlers.get(action_name)
                print('handler',handler.strategy, action_name)
                if not handler:
                    continue
                    
                 # Get complete parameters from the strategy
                execution_params = handler.strategy.get_params(context)
                #print(execution_params)
                #if not execution_params:
                #    continue

                stats['total_actions'] += 1
                success = handler.execute(context,execution_params)
                if success:
                    stats['successful_actions'] += 1
                    stats['action_counts'][action_name] = stats['action_counts'].get(action_name, 0) + 1

                    agent.record_action(
                        action_name=action_name,
                        address=execution_params.get('sender', ''),
                        block_number=self.network_state['current_block'],
                        success=True
                    )
            return stats
            
        except Exception as e:
            logger.error(f"Network evolution failed: {e}")
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