from typing import Dict, Optional, Any
from datetime import datetime
import random
from ape import chain
from src.framework.agents import AgentManager, BaseAgent, ActionType
from src.framework.data import DataCollector
from src.framework.logging import get_logger
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
    ):
        self.clients = clients
        self.agent_manager = agent_manager
        self.collector = collector
        
        # Track last action times
        self.last_action_times: Dict[str, int] = {}
        self.min_blocks_between_actions = 5
        
        # Initialize all available handlers
        self.handlers = {}
        self._initialize_handlers()

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
        
    def _execute_action(
        self,
        agent: BaseAgent,
        action_name: str,
       # acting_address: str,
        params: Dict
    ) -> bool:
        """Execute action using appropriate handler"""
        try:
            # Get handler for action
            handler = self.handlers.get(action_name)
            if not handler:
                logger.error(f"No handler found for action {action_name}")
                return False
    
            success = handler.execute(agent, self.agent_manager)

            if success:
                logger.debug(f"Successfully executed {action_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}", exc_info=True)
            return False
            
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
        """Evolve network with action tracking"""
        stats = {
            'total_actions': 0,
            'successful_actions': 0,
            'action_counts': {}
        }
        
        try:
            all_agents = list(self.agent_manager.agents.values())
            random.shuffle(all_agents)

            # Current chain state
            chain_state = {
                'current_block': chain.blocks.head.number,
                'current_time': chain.blocks.head.timestamp,
                'balances': {}
            }

            # Process each agent's action
            for agent in all_agents:
                if not self._check_action_timing(agent.agent_id, chain_state['current_block']):
                    continue
                    
                action_name, acting_address, params = agent.select_action(
                    current_block=chain_state['current_block'],
                    network_state=chain_state
                )
                if action_name is None:
                    continue

                stats['total_actions'] += 1
                
                success = self._execute_action(
                    agent, 
                    action_name,
                    params
                )
                if success:
                    stats['successful_actions'] += 1
                    stats['action_counts'][action_name] = stats['action_counts'].get(action_name, 0) + 1
                    self.last_action_times[agent.agent_id] = chain_state['current_block']
                    
                    agent.record_action(
                        action_name,
                        chain_state['current_block'],
                        True
                    )
                    

            logger.info(
                f"Iteration {iteration} complete - "
                f"Actions: {stats['total_actions']}, "
                f"Successful: {stats['successful_actions']}"
            )
            return stats
            
        except Exception as e:
            logger.error(f"Network evolution failed: {e}", exc_info=True)
            return stats
            
    def _check_action_timing(self, agent_id: str, current_block: int) -> bool:
        """Check if enough blocks have passed since last action"""
        last_action = self.last_action_times.get(agent_id, 0)
        blocks_passed = current_block - last_action
        return blocks_passed >= self.min_blocks_between_actions