from typing import Dict, Optional, List, Any
from ape import chain
from eth_pydantic_types import HexBytes
from src.framework.agents import AgentManager, BaseAgent
from src.framework.data import DataCollector
from src.framework.logging import get_logger
from src.framework.core.context import SimulationContext
import importlib

logger = get_logger(__name__)

class NetworkBuilder:
    """
    Enhanced NetworkBuilder that handles initial network setup in a generalized way
    """
    
    def __init__(
        self,
        clients: Dict[str, Any],
        batch_size: int = 10,
        agent_manager: Optional[AgentManager] = None,
        collector: Optional[DataCollector] = None
    ):
        self.clients = clients
        self.batch_size = batch_size
        self.agent_manager = agent_manager
        self.collector = collector
        self.network_state = {
            'current_block': 0,
            'current_time': 0,
            'contract_states': {},
            'running_state': {}
        }

    def build_large_network(
        self,
        target_size: int,
        profile_distribution: Dict[str, int],
        initial_state: Optional[Dict[str, Any]] = None,
        initial_actions: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Build initial network state"""
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
                agent.state['trusted_addresses'] = set()

            # Set initial network state
            if initial_state:
                self.network_state['contract_states'] = initial_state
                if not self._set_initial_state(created_agents, initial_state):
                    return False

            # Execute initial actions
            if initial_actions:
                if not self._execute_initial_actions(created_agents, initial_actions):
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to build network: {e}", exc_info=True)
            return False
            
    def _ensure_agent_accounts(self, agent: BaseAgent):
        """Make sure agent has required number of accounts"""
        target_accounts = agent.profile.target_account_count
        current_accounts = len(agent.accounts)
        
        for _ in range(current_accounts, target_accounts):
            agent.create_account()

    def _execute_initial_actions(
        self, 
        agents: List[BaseAgent],
        actions: List[Dict[str, Any]]
    ) -> bool:
        total_executed = 0
        total_failures = 0

        # Create accounts first
        for agent in agents:
            self._ensure_agent_accounts(agent)
            
        # Update network state with current block/time
        self.network_state.update({
            'current_block': chain.blocks.head.number,
            'current_time': chain.blocks.head.timestamp,
        })

        # Then execute actions
        for action_spec in actions:
            action_type = action_spec["action"]
            handler = self._get_handler_for_action(action_type)
            if not handler:
                continue

            for agent in agents:
                # Create context for this action
                context = SimulationContext(
                    agent=agent,
                    agent_manager=self.agent_manager,
                    clients=self.clients,
                    chain=chain,
                    network_state=self.network_state,
                    iteration=0,
                    iteration_cache={}
                )

                params = self._prepare_action_params(context, action_spec)
                if not params:
                    continue

                success = handler.execute(context, params)
                total_executed += 1
                if not success:
                    total_failures += 1

        return total_failures <= total_executed * 0.2
    
    def _set_initial_state(
        self, 
        agents: List[BaseAgent],
        state: Dict[str, Any]
    ) -> bool:
        """Set initial network state"""
        try:
            for agent in agents:
                for key, value in state.items():
                    agent.update_state(key, value)
            return True
        except Exception as e:
            logger.error(f"Failed to set initial state: {e}")
            return False

    def _get_handler_for_action(self, action_type: str):
        """Get appropriate handler for action type"""
        try:
            action_meta = self.agent_manager.registry.get_metadata(action_type)
            if not action_meta:
                return None

            # Import handler
            mod_path = action_meta.module_path.replace("/", ".").replace(".py", "")
            module = importlib.import_module(mod_path)
            handler_class = getattr(module, action_meta.handler_class)

            # Initialize handler with appropriate client
            client = self.clients.get(action_meta.module_name)
            if client:
                return handler_class(client=client, chain=chain, logger=logger)
                
        except Exception as e:
            logger.error(f"Failed to get handler for {action_type}: {e}")
            return None

    def _prepare_action_params(
        self,
        context: SimulationContext,
        action_spec: Dict[str, Any]  
    ) -> Dict[str, Any]:
        """Prepare params handling both static and dynamic parameters"""
        params = {}
        for key, value in action_spec.items():
            if key == "param_function":
                continue
            if callable(value):
                params[key] = value(context.agent)
            else:
                params[key] = value

        if "param_function" in action_spec:
            params.update(action_spec["param_function"](
                context.agent, 
                context.agent_manager.get_all_agents()
            ))
            
        if "sender" not in params and context.agent.accounts:
            params["sender"] = next(iter(context.agent.accounts.keys()))
        return params