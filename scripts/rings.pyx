import logging
from pathlib import Path
import click
from datetime import datetime
import os
import yaml
from dotenv import load_dotenv
from ape import networks, chain
from eth_pydantic_types import HexBytes
import random
from typing import Optional, Dict, Any

from src.protocols.ringshub import RingsHubClient
from src.protocols.balancerv3vault import BalancerV3VaultClient
from src.protocols.wxdai import WXDAIClient
from src.framework.data import DataCollector
from src.framework.agents import AgentManager, BalanceTracker
from src.framework.core import (
    NetworkBuilder, 
    NetworkEvolver,
)
from src.framework.logging import get_logger

# Load environment variables
load_dotenv()

logging.getLogger('ape').setLevel(logging.WARNING)
logger = get_logger(__name__) 

PROJECT_ROOT = Path(__file__).parent.parent
ABIS_DIR = PROJECT_ROOT / "src" / "protocols" / "abis"


CONTRACT_CONFIGS = {
    'rings': {
        'address': '0x3D61f0A272eC69d65F5CFF097212079aaFDe8267',
        'client_class': 'RingsHubClient',
        'module_name': 'ringshub',
        'abi_folder': 'rings'
    },
    'balancerv3vault': {
        'address': '0xbA1333333333a1BA1108E8412f11850A5C319bA9', 
        'client_class': 'BalancerV3VaultClient',
        'module_name': 'balancerv3vault',
        'abi_folder': 'balancer_v3'
    },
    'wxdai': {
        'address': '0xe91d153e0b41518a2ce8dd3d7944fa863463a97d', 
        'client_class': 'WXDAIClient', 
        'module_name': 'wxdai',
        'abi_folder': 'tokens'
    }
}



def validate_abi_path(path: Path, name: str) -> str:
    if not path.exists():
        logger.warning(f"{name} ABI file not found at {path}, using empty ABI")
        return "{}"
    return str(path)

class SimulationConfig:
    """Configuration holder for simulation parameters"""
    def __init__(
        self,
        rings_config_path: str = "config/rings_config.yaml",
        agent_config_path: str = "config/agent_config.yaml",
        cli_params: Optional[Dict] = None
    ):
        self.rings_config = self._load_config(rings_config_path)
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
        if 'size' not in self.rings_config:
            self.rings_config['size'] = 20
        if 'trust_density' not in self.rings_config:
            self.rings_config['trust_density'] = 0.1
        if 'batch_size' not in self.rings_config:
            self.rings_config['batch_size'] = 10
        if 'iterations' not in self.rings_config:
            self.rings_config['iterations'] = 10
        if 'blocks_per_iteration' not in self.rings_config:
            self.rings_config['blocks_per_iteration'] = 100
        if 'block_time' not in self.rings_config:
            self.rings_config['block_time'] = 5

    def _apply_cli_params(self, params: Dict):
        for key in ['size', 'trust_density', 'batch_size', 'iterations', 'blocks_per_iteration', 'block_time']:
            if params.get(key) is not None:
                self.rings_config[key] = params[key]

    def _validate_config(self):
        required_network_params = ['size', 'trust_density', 'batch_size', 'iterations']
        for param in required_network_params:
            if param not in self.rings_config:
                raise ValueError(f"Missing required network parameter: {param}")
        if 'profiles' not in self.agent_config:
            raise ValueError("Agent configuration must define agent profiles")

    @property
    def network_size(self) -> int:
        return self.rings_config['size']

    @property
    def trust_density(self) -> float:
        return self.rings_config['trust_density']

    @property
    def batch_size(self) -> int:
        return self.rings_config['batch_size']

    @property
    def iterations(self) -> int:
        return self.rings_config['iterations']

    @property
    def blocks_per_iteration(self) -> int:
        return self.rings_config['blocks_per_iteration']

    @property
    def block_time(self) -> int:
        return self.rings_config['block_time']

    @property
    def agent_distribution(self) -> Dict[str, float]:
        raw_dist = self.agent_config.get('agent_distribution', {})
        if not raw_dist:
            raw_dist = {'honest_user': 10, 'group_creator': 1, 'sybil_attacker': 2, 'trust_hub': 5}
        total = sum(raw_dist.values())
        return {k: v / total for k, v in raw_dist.items()}

class RingsSimulation:
    """Main simulation class orchestrating the agent-based simulation"""

    def __init__(self, config: SimulationConfig, fast_mode: bool = True):
        # First assign the config
        self.config = config  # Move this line up
        self.fast_mode = fast_mode
        self.simulation_start_time = datetime.now()

        # Now validate agent distribution matches network size
        agent_total = sum(int(self.config.network_size * weight) 
                        for weight in config.agent_distribution.values())
        if agent_total != config.network_size:
            logger.warning(
                f"Agent distribution total {agent_total} adjusted to match "
                f"network size {config.network_size}"
            )
       
        # Initialize collector if not in fast mode
        self.collector = None if fast_mode else DataCollector(
            config.rings_config.get('db_path', "rings_simulation.duckdb")
        )


       # Initialize all clients
        self.clients = self.initialize_clients(config)

        # Initialize managers
        self.agent_manager = AgentManager(
            config=config.agent_config,
            data_collector=self.collector
        )
        protocols_path = str(Path(__file__).parent.parent / "src" / "protocols")
        self.agent_manager.registry.discover_actions(protocols_path)

        self.builder = NetworkBuilder(
            #client=self.rings_client,  # Pass the client instance
            clients=self.clients,
            batch_size=config.batch_size,
            agent_manager=self.agent_manager,
            collector=self.collector
        )

        self.evolver = NetworkEvolver(
            clients=self.clients,
            agent_manager=self.agent_manager,
            collector=self.collector,
            gas_limits=config.rings_config.get('gas_limits'),
        )


        # Initialize tracking
        self.iteration_stats = []

        self.balance_tracker = BalanceTracker(self.agent_manager)
        if self.collector:
            self.balance_tracker.subscribe(self.collector.event_logger)
        

    def initialize_clients(self, config: SimulationConfig) -> Dict[str, Any]:
        """Initialize all contract clients from configuration"""
        clients = {}
        
        for contract_name, contract_config in CONTRACT_CONFIGS.items():
            try:
                # Build ABI path
                abi_path = ABIS_DIR / contract_config['abi_folder'] / f"{contract_config['address']}.json"
                validated_abi = validate_abi_path(abi_path, contract_name.title())
                
                # Parse ABI content
                if validated_abi == "{}":
                    # Empty ABI case
                    abi_content = []
                else:
                    # Read actual ABI content from file
                    with open(validated_abi, 'r') as f:
                        abi_content = f.read()
                
                # Import client class dynamically
                module = __import__(
                    f"src.protocols.{contract_config['module_name']}", 
                    fromlist=[contract_config['client_class']]
                )
                client_class = getattr(module, contract_config['client_class'])
                
                # Initialize client
                client = client_class(
                    contract_config['address'],
                    abi_content,  # Pass ABI content instead of path
                    gas_limits=config.rings_config.get('gas_limits', {}),
                    data_collector=self.collector
                )
                
                # Store client instance
                setattr(self, f"{contract_name}_client", client)
                clients[contract_config['module_name']] = client
                
                # Create ABI directory if it doesn't exist
              #  (ABIS_DIR / contract_config['module_name']).mkdir(exist_ok=True)
                
                logger.debug(f"Successfully initialized {contract_name} client")
                
            except Exception as e:
                logger.error(f"Failed to initialize {contract_name} client: {e}")
                raise
        
        return clients

    def run(self) -> bool:
        """Execute the entire simulation"""
        try:
            logger.info("Starting Rings network simulation")
            metadata = self._create_simulation_metadata()

            if self.collector:
                self.collector.start_simulation_run(
                    parameters=metadata,
                    description="Rings Network Simulation"
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
        """Build the initial network with agents"""
        try:
            logger.info(f"Building initial network with {self.config.network_size} agents")
            
            # Calculate agent distribution
            distribution = {}
            remaining = self.config.network_size
            
            for profile, weight in self.config.agent_distribution.items():
                if profile == list(self.config.agent_distribution.keys())[-1]:
                    # Last profile gets remaining agents
                    distribution[profile] = remaining
                else:
                    count = int(weight * self.config.network_size)
                    distribution[profile] = count
                    remaining -= count
            
            
            initial_actions = [
                {
                    "action": "ringshub_RegisterHuman",
                    "param_function": lambda agent, _: {
                        "_inviter": "0x0000000000000000000000000000000000000000",
                        "_metadataDigest": HexBytes("0x00"),
                        "sender": next(iter(agent.accounts.keys()))
                    } if agent.accounts else None
                },
                {
                    "action": "ringshub_Trust",
                    "param_function": lambda agent, all_agents: {
                        "_trustReceiver": next(iter(random.choice([
                            a for a in all_agents if a != agent and len(a.accounts) > 0
                        ]).accounts.keys())),
                        "_expiry": int(chain.pending_timestamp + 365*24*60*60),
                        "sender": next(iter(agent.accounts.keys()))
                    } if agent.accounts else None
                }
            ]

            initial_state = {
                "trusted_addresses": set(),
                "group_count": 0
            }

            success = self.builder.build_large_network(
                target_size=self.config.network_size,
                profile_distribution=distribution,
                initial_actions=initial_actions,
                initial_state=initial_state
            )

            
            if success:
                logger.info("Successfully built initial network")
            else:
                logger.error("Failed to build initial network")
            
            return success
            
        except Exception as e:
            logger.error(f"Error building initial network: {e}")
            #self._log_event('network_build_error', error=str(e))
            return False


    def _run_iterations(self) -> bool:
        """Run all simulation iterations"""
        logger.info(f"Running {self.config.iterations} iterations")
        
        for i in range(self.config.iterations):
            
            if not self.evolver.advance_time(
                self.config.blocks_per_iteration,
                self.config.block_time
            ):
                logger.error(f"Failed to advance time at iteration {i+1}")
                return False
                
            # Process network evolution
            stats = self.evolver.evolve_network(i + 1)
            
            self.iteration_stats.append(stats)
            self._log_iteration_summary(i + 1, stats)
            
        return True

    def _create_simulation_metadata(self) -> dict:
        return {
            'start_time': self.simulation_start_time.isoformat(),
            'config': {
                'network_size': self.config.network_size,
                'trust_density': self.config.trust_density,
                'batch_size': self.config.batch_size,
                'iterations': self.config.iterations,
                'blocks_per_iteration': self.config.blocks_per_iteration,
                'block_time': self.config.block_time,
                'agent_profiles': list(self.config.agent_config.get('profiles', {}).keys()),
                'fast_mode': self.fast_mode
            },
            'contracts': {key: CONTRACT_CONFIGS[key]['address'] for key in CONTRACT_CONFIGS},
            'chain_id': networks.provider.chain_id
        }

    def _log_iteration_summary(self, iteration: int, stats: dict):
        """Log summary of iteration results"""
        logger.info(
            f"Iteration {iteration} complete:\n"
            f"  - Total actions: {stats['total_actions']}\n"
            f"  - Successful actions: {stats['successful_actions']}\n"
            f"  - Action breakdown: {stats.get('action_counts', {})}"
        )


    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive simulation statistics"""
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

@click.group()
def cli():
    """Rings Network Agent-based Simulation CLI"""
    pass

@cli.command()
@click.option('--rings-config', default='config/rings_config.yaml', help='Rings config file')
@click.option('--agent-config', default='config/agent_config.yaml', help='Agent config file')
@click.option('--fast-mode/--no-fast-mode', default=True, help='Disable DB storage in fast mode')
@click.option('--network-size', type=int, help='Override network size')
@click.option('--trust-density', type=float, help='Override trust density')
@click.option('--batch-size', type=int, help='Override batch size')
@click.option('--iterations', type=int, help='Override iteration count')
@click.option('--blocks-per-iteration', type=int, help='Override blocks per iteration')
def simulate(rings_config, agent_config, fast_mode, network_size,
             trust_density, batch_size, iterations, blocks_per_iteration):
    """Run the Rings simulation"""
    cli_params = {
        'size': network_size,
        'trust_density': trust_density,
        'batch_size': batch_size,
        'iterations': iterations,
        'blocks_per_iteration': blocks_per_iteration
    }
    # Filter out None values
    cli_params = {k: v for k, v in cli_params.items() if v is not None}

    config = SimulationConfig(
        rings_config_path=rings_config,
        agent_config_path=agent_config,
        cli_params=cli_params
    )
    
    click.echo(f"\nStarting simulation in {'fast' if fast_mode else 'normal'} mode")

    with networks.gnosis.mainnet_fork.use_provider("foundry"):
        sim = RingsSimulation(config, fast_mode=fast_mode)
        if not sim.run():
            click.echo("Simulation failed. Check logs for details.")
            exit(1)
            
        stats = sim.get_statistics()
        click.echo("\nSimulation completed successfully!")
        click.echo(f"\nSummary Statistics:")
        click.echo(f"  Duration: {stats['duration']:.2f} seconds")
        click.echo(f"  Network Size: {stats['network_size']:,} agents")
        click.echo(f"  Total Actions: {stats['total_actions']:,}")
        click.echo(f"  Successful Actions: {stats['successful_actions']:,}")
        click.echo("\nAction Breakdown:")
        for action, count in stats['action_counts'].items():
            click.echo(f"  - {action}: {count:,}")

if __name__ == "__main__":
    cli()