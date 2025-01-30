import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import yaml
from abc import ABC, abstractmethod
from ethpm_types.abi import EventABI
import json

from ape import chain
from src.framework.data import DataCollector
from src.framework.agents import AgentManager
from src.framework.core import NetworkBuilder, NetworkEvolver, SimulationContext
from src.framework.logging import get_logger
from src.framework.state.decoder import StateDecoder


logger = get_logger(__name__)


class BaseSimulationConfig:
    """Base configuration class that can be extended for specific simulations"""
    
    def __init__(
        self,
        network_config_path: str,
        agent_config_path: str,
        cli_params: Optional[Dict] = None
    ):
        self.network_config = self._load_config(network_config_path)
        self.agent_config = self._load_config(agent_config_path)
        self._set_default_values()
        if cli_params:
            self._apply_cli_params(cli_params)
        self._validate_config()

    def _load_config(self, path: str) -> Dict:
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load config from {path}: {e}")
            return {}

    def _set_default_values(self):
        """Set default values for common parameters"""
        defaults = {
            'batch_size': 10,
            'iterations': 10,
            'blocks_per_iteration': 100,
            'block_time': 5
        }
        for key, value in defaults.items():
            if key not in self.network_config:
                self.network_config[key] = value

    def _apply_cli_params(self, params: Dict):
        """Apply command line parameters"""
        for key, value in params.items():
            if value is not None:
                self.network_config[key] = value

    def _validate_config(self):
        """Validate configuration specifics"""
        # Validate basic params remain the same
        required_params = ['batch_size', 'iterations']
        for param in required_params:
            if param not in self.network_config:
                raise ValueError(f"Missing required parameter: {param}")

        # Validate agent distribution exists
        if 'agent_distribution' not in self.agent_config:
            raise ValueError("Missing 'agent_distribution' in agent config")

                
    def _validate_state_config(self, state_config: Dict) -> None:
        """Validate state variable configuration"""
        for contract_id, config in state_config.items():
            if 'variables' not in config:
                raise ValueError(f"Missing 'variables' section for contract {contract_id}")
                
            for var_name, var_config in config['variables'].items():
                if 'type' not in var_config:
                    raise ValueError(f"Missing type for variable {var_name} in contract {contract_id}")
                if 'slot' not in var_config:
                    raise ValueError(f"Missing slot for variable {var_name} in contract {contract_id}")


    @property
    def state_variables(self) -> Dict[str, Dict[str, Any]]:
        """Get state variable configuration"""
        return self.network_config.get('state_variables', {})

    @property
    def network_size(self) -> int:
        """Calculate total network size from agent distribution"""
        distribution = self.agent_config.get('agent_distribution', {})
        if not distribution:
            raise ValueError("No agent distribution configured")
        return sum(distribution.values())

    @property
    def batch_size(self) -> int:
        return self.network_config['batch_size']

    @property
    def iterations(self) -> int:
        return self.network_config['iterations']

    @property
    def blocks_per_iteration(self) -> int:
        return self.network_config['blocks_per_iteration']

    @property
    def block_time(self) -> int:
        return self.network_config['block_time']

    @abstractmethod
    def get_agent_distribution(self) -> Dict[str, int]:
        """Get the distribution of agent types"""
        pass


BASE_CONTRACT_CONFIGS: Dict[str, Dict[str, Any]] = {}


class BaseSimulation(ABC):
    """Base simulation class that can be extended for specific simulations"""

    def __init__(
        self,
        config: BaseSimulationConfig,
        contract_configs: Dict[str, Dict[str, Any]],
        fast_mode: bool = True,
        project_root: Optional[Path] = None
    ):
        self.config = config
        self.contract_configs = contract_configs
        self.fast_mode = fast_mode
        self.project_root = project_root or Path(__file__).parents[3]
        self.simulation_start_time = datetime.now()
        self.strategy_config = self.config.network_config.get('strategies', {})

        # Load all ABIs first so they're available for everything else
        self.abis = self._load_contract_abis()

        # Initialize infrastructure
        self.collector = self._initialize_collector()
        self.agent_manager = self._initialize_agent_manager()
        self.clients = self._initialize_clients()

        # Initialize contract states
        self.contract_states = self._initialize_contract_states(config, contract_configs)
        
        # Put decoded states into initial_state for backward compatibility
        self.initial_state = {
            contract_id: state_data['state'] 
            for contract_id, state_data in self.contract_states.items()
        }

        self.builder = self._initialize_builder()
        self.evolver = self._initialize_evolver()

        # Tracking
        self.iteration_stats: List[Dict[str, Any]] = []


    def _load_contract_abis(self) -> List[EventABI]:
        """Load all contract ABIs from the abi folder and subfolders and convert them to EventABI objects."""
        all_abis = []
        try:
            # Base ABI folder path
            abi_base_path = self.project_root / "src" / "protocols" / "abis"
            
            # Recursively find all JSON files under the ABI folder
            for abi_path in abi_base_path.rglob("*.json"):
                try:
                    with open(abi_path) as f:
                        contract_abi = json.load(f)
                        # Filter for event ABIs and convert to EventABI objects
                        event_abis = [
                            EventABI(
                                name=item['name'],
                                inputs=item.get('inputs', []),
                                anonymous=item.get('anonymous', False)
                            )
                            for item in contract_abi
                            if item.get('type') == 'event'
                        ]
                        all_abis.extend(event_abis)
                        logger.info(f"Loaded {len(event_abis)} events from ABI file: {abi_path}")
                except Exception as e:
                    logger.error(f"Failed to load ABI from {abi_path}: {e}")
        except Exception as e:
            logger.error(f"Error while traversing ABI folder: {e}")

        return all_abis

    def _load_contract_abis2(self) -> List[EventABI]:
        """Load all contract ABIs from config and convert to EventABI objects"""
        all_abis = []
        for name, cfg in self.contract_configs.items():
            try:
                abi_path = (self.project_root / "src" / "protocols" / 
                           "abis" / cfg['abi_folder'] / f"{cfg['address']}.json")
                if abi_path.exists():
                    with open(abi_path) as f:
                        contract_abi = json.load(f)
                        # Filter for event ABIs and convert to EventABI objects
                        event_abis = [
                            EventABI(
                                name=item['name'],
                                inputs=item.get('inputs', []),
                                anonymous=item.get('anonymous', False)
                            )
                            for item in contract_abi 
                            if item.get('type') == 'event'
                        ]
                        all_abis.extend(event_abis)
                        logger.info(f"Loaded {len(event_abis)} events from ABI for {name}")
                else:
                    logger.warning(f"ABI file not found: {abi_path}")
            except Exception as e:
                logger.error(f"Failed to load ABI for {name}: {e}")
                
        return all_abis

    def _initialize_contract_states(self, config: BaseSimulationConfig, contract_configs: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Initialize contract states from configuration"""
        initialized_states = {}

        if not config.state_variables:
            return initialized_states

        for contract_id, state_config in config.state_variables.items():
            try:
                # Get contract address - from state config or contract_configs
                if 'address' in state_config:
                    contract_address = state_config['address']
                elif contract_id in contract_configs:
                    contract_address = contract_configs[contract_id]['address']
                else:
                    logger.error(f"No address found for contract {contract_id}")
                    continue

                # Verify contract exists
                if not contract_address:
                    logger.error(f"Invalid address for contract {contract_id}")
                    continue

                # Initialize decoder and decode state
                decoder = StateDecoder(contract_address)
                decoded_state = decoder.decode_state(state_config['variables'])
                
                initialized_states[contract_id] = {
                    'address': contract_address,
                    'state': decoded_state
                }
                
                #import json
                #with open("sample.json", "w") as outfile:
                #    json.dump(decoded_state, outfile)

                logger.info(f"Decoded state for {contract_id} ({contract_address}): {decoded_state.keys()}")

            except Exception as e:
                logger.error(f"Failed to decode state for contract {contract_id}: {e}")
                continue

        return initialized_states

    def get_initial_state(self) -> Dict[str, Any]:
        """Get initial state for agents"""
        # Override in specific simulations to use decoded state
        return self.initial_state

    def _initialize_collector(self) -> Optional[DataCollector]:
        """Initialize data collector if not in fast mode"""
        if self.fast_mode:
            return None
        return DataCollector(
            db_path=self.config.network_config.get('db_path', 'simulation.duckdb'),
            abis=self.abis 
        )

    def _initialize_agent_manager(self) -> AgentManager:
        """Initialize agent manager"""
        manager = AgentManager(
            config=self.config.agent_config,
            data_collector=self.collector
        )
        protocols_path = str(self.project_root / "src" / "protocols")
        manager.registry.discover_actions(protocols_path)
        return manager
    
    def _initialize_clients(self) -> Dict[str, Any]:
        """Initialize all contract clients including MultiCall and BatchCall"""
        clients = {}
        
        # First initialize all regular clients
        for name, config in self.contract_configs.items():
            if name in ['multicall', 'batchcall']:  # Skip special clients for now
                continue
                    
            try:
                abi_dir = self.project_root / "src" / "protocols" / "abis" / config['abi_folder']
                
                # Handle generic ABIs (like ERC20) vs contract-specific ABIs
                if config.get('abi_name'):
                    # Use specified ABI name for generic interfaces
                    abi_path = abi_dir / config['abi_name']
                else:
                    # Use contract address for specific contracts
                    abi_path = abi_dir / f"{config['address']}.json"
                
                if not abi_path.exists():
                    logger.warning(f"ABI file not found for {name} at {abi_path}")
                    continue

                # Fallback if module_name is not in config:
                module_name = config.get('module_name', name)

                strategy = config.get(
                    config['module_name'], 
                    config.get('strategy', 'basic')
                )
                logger.info(f"Initializing {name} client with {strategy} strategy")

                client = config['client_class'](
                    config['address'],
                    str(abi_path),
                    gas_limits=self.config.network_config.get('gas_limits', {}),
                    data_collector=self.collector
                )
                
                # Store clients by their module_name
                clients[module_name] = client
                setattr(self, f"{name}_client", client)
                
            except Exception as e:
                logger.error(f"Failed to initialize {name} client: {e}")
                raise
                
        # Now initialize special clients (MultiCall and BatchCall) with all available clients
        try:
            if 'multicall' in self.contract_configs:
                from src.protocols.interfaces.multicall import MultiCallClient
                multicall_client = MultiCallClient(clients, collector=self.collector)
                clients['multicall'] = multicall_client
                setattr(self, 'multicall_client', multicall_client)
                logger.info("Initialized MultiCall client with all available contracts")

            if 'batchcall' in self.contract_configs:
                from src.protocols.interfaces.batchcall import BatchCallClient
                batchcall_client = BatchCallClient(clients, collector=self.collector)
                clients['batchcall'] = batchcall_client
                setattr(self, 'batchcall_client', batchcall_client)
                logger.info("Initialized BatchCall client with all available contracts")

        except Exception as e:
            logger.error(f"Failed to initialize special clients: {e}")
            raise
        
        return clients

    def _initialize_clients2(self) -> Dict[str, Any]:
        """Initialize all contract clients"""
        clients = {}
        
        for name, config in self.contract_configs.items():
            try:
                abi_dir = self.project_root / "src" / "protocols" / "abis" / config['abi_folder']
                
                # Handle generic ABIs (like ERC20) vs contract-specific ABIs
                if config.get('abi_name'):
                    # Use specified ABI name for generic interfaces
                    abi_path = abi_dir / config['abi_name']
                else:
                    # Use contract address for specific contracts
                    abi_path = abi_dir / f"{config['address']}.json"
                
                if not abi_path.exists():
                    logger.warning(f"ABI file not found for {name} at {abi_path}")
                    continue

                # Fallback if module_name is not in config:
                module_name = config.get('module_name', name)

                strategy = config.get(
                    config['module_name'], 
                    config.get('strategy', 'basic')
                )
                logger.info(f"Initializing {name} client with {strategy} strategy")

                client = config['client_class'](
                    config['address'],
                    str(abi_path),
                    gas_limits=self.config.network_config.get('gas_limits', {}),
                    data_collector=self.collector
                )
                
                # Store clients by their module_name
                clients[module_name] = client
                setattr(self, f"{name}_client", client)
                
            except Exception as e:
                logger.error(f"Failed to initialize {name} client: {e}")
                raise
                
        return clients
    

    def _initialize_builder(self) -> NetworkBuilder:
        """Initialize network builder"""
        builder = NetworkBuilder(
            clients=self.clients,
            batch_size=self.config.batch_size,
            agent_manager=self.agent_manager,
            collector=self.collector
        )
        builder.set_simulation(self)
        return builder

    def _initialize_evolver(self) -> NetworkEvolver:
        """Initialize network evolver with strategies"""
        evolver = NetworkEvolver(
            clients=self.clients,
            agent_manager=self.agent_manager,
            collector=self.collector,
            gas_limits=self.config.network_config.get('gas_limits'),
            strategy_config=self.strategy_config
        )
        evolver.initialize_contract_states(self.contract_states)
        evolver.set_simulation(self)
        return evolver

    @abstractmethod
    def get_initial_actions(self) -> List[Dict[str, Any]]:
        """Get list of initial actions to perform when building network"""
        pass


    @abstractmethod
    def get_simulation_description(self) -> str:
        """Get description of the simulation"""
        pass

    @abstractmethod
    def _create_simulation_metadata(self) -> Dict[str, Any]:
        """Create metadata for the simulation run"""
        pass

    def run(self) -> bool:
        """Execute the simulation from start to finish"""
        try:
            logger.info("Starting simulation")
            metadata = self._create_simulation_metadata()

            if self.collector:
                self.collector.start_simulation_run(
                    parameters=metadata,
                    description=self.get_simulation_description()
                )

            if not self._build_initial_network():
                return False
            if not self._run_iterations():
                return False

            if self.collector:
                self.collector.end_simulation_run()

            logger.info("Simulation completed successfully")
            return True

        except Exception as e:
            logger.error(f"Simulation failed: {e}", exc_info=True)
            return False

    def _build_initial_network(self) -> bool:
        """Build the initial network"""
        try:
            logger.info(f"Building initial network with {self.config.network_size} agents")
            
            success = self.builder.build_large_network(
                target_size=self.config.network_size,
                profile_distribution=self.config.get_agent_distribution(),
                initial_actions=self.get_initial_actions(),
                initial_state=self.get_initial_state()
            )
            
            if success:
                logger.info("Successfully built initial network")
            else:
                logger.error("Failed to build initial network")
            
            return success
            
        except Exception as e:
            logger.error(f"Error building initial network: {e}")
            return False
        

    def _record_current_state(self):
        """Record current state in the data collector"""
        if not self.collector:
            return
            
        try:
            # Get current state data from evolver's network_state
            state_data = {
                'contract_states': self.contract_states,
                'network_state': {
                    k: v for k, v in self.evolver.network_state.items() 
                    if k != 'contract_states'  # Avoid duplicate data
                }
            }
            
            # Record in collector
            self.collector.record_state(
                block_number=chain.blocks.head.number,
                block_timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp),
                state_data=state_data
            )
            
        except Exception as e:
            logger.error(f"Failed to record state: {e}", exc_info=True)

    def _run_iterations(self) -> bool:
        """Run simulation iterations"""
        logger.info(f"Running {self.config.iterations} iterations")
        
        for i in range(self.config.iterations):
            if not self.evolver.advance_time(
                self.config.blocks_per_iteration,
                self.config.block_time
            ):
                logger.error(f"Failed to advance time at iteration {i+1}")
                return False
                
            stats = self.evolver.evolve_network(i + 1)
            self.iteration_stats.append(stats)

            self._record_current_state()

            self._log_iteration_summary(i + 1, stats)
            
        return True

    def _log_iteration_summary(self, iteration: int, stats: Dict[str, Any]):
        """Log iteration summary"""
        logger.info(
            f"Iteration {iteration} complete:\n"
            f"  - Total actions: {stats['total_actions']}\n"
            f"  - Successful actions: {stats['successful_actions']}\n"
            f"  - Action breakdown: {stats.get('action_counts', {})}"
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get simulation statistics after execution"""
        total_actions = sum(s.get('total_actions', 0) for s in self.iteration_stats)
        successful_actions = sum(s.get('successful_actions', 0) for s in self.iteration_stats)
        action_counts = {}
        for s in self.iteration_stats:
            for k, v in s.get('action_counts', {}).items():
                action_counts[k] = action_counts.get(k, 0) + v

        return {
            'duration': (datetime.now() - self.simulation_start_time).total_seconds(),
            'network_size': self.config.network_size,
            'iterations_completed': len(self.iteration_stats),
            'total_actions': total_actions,
            'successful_actions': successful_actions,
            'current_block': chain.blocks.head.number,
            'action_counts': action_counts
        }

    def update_state_from_transaction(self, tx, context: 'SimulationContext') -> None:
        """
        Generic method to update simulation state based on transaction data.
        Override in specific simulations to implement custom state tracking.
        
        Args:
            tx: The transaction receipt/result
            context: Current simulation context
        """
        pass 