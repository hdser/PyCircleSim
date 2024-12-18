import logging
from pathlib import Path
import click
from datetime import datetime, timedelta
import os
import yaml
from dotenv import load_dotenv
from ape import networks, accounts, chain
import pandas as pd
import json
from typing import Optional, Dict

from src.protocols.rings import RingsClient
from src.framework.data import CirclesDataCollector
from src.framework.agents import AgentManager
from src.framework.core import (
    NetworkBuilder,
    NetworkEvolver,
    NetworkAnalyzer
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rings_simulation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Contract configuration

PROJECT_ROOT = Path(__file__).parent.parent

# Define contract addresses
RINGS = "0x3D61f0A272eC69d65F5CFF097212079aaFDe8267"
FJORD_LBP = "0x1ddf1109f8cb373dbb66f3d30077571ab21bdd58"

# Define ABI paths relative to project root
RINGS_ABI = str(PROJECT_ROOT / "src" / "protocols" / "rings" / "abis" / f"{RINGS}.json")
FJORD_ABI = str(PROJECT_ROOT / "src" / "protocols" / "fjord" / "abis" / f"{FJORD_LBP}.json")


class SimulationConfig:
    """Configuration holder for simulation parameters"""
    def __init__(
        self,
        rings_config_path: str = "config/rings_config.yaml",
        agent_config_path: str = "config/agent_config.yaml",
        cli_params: Optional[Dict] = None
    ):
        """
        Initialize simulation configuration with both network and agent parameters.
        
        The configuration is loaded from two files:
        - rings_config.yaml: Contains network-level parameters
        - agent_config.yaml: Contains agent behavior definitions
        
        CLI parameters can override values from either configuration.
        """
        # Load base configurations
        self.rings_config = self._load_config(rings_config_path)
        self.agent_config = self._load_config(agent_config_path)
        
        # Set default values for essential parameters
        self._set_default_values()
        
        # Apply CLI parameters if provided
        if cli_params:
            self._apply_cli_params(cli_params)
            
        # Validate the configuration
        self._validate_config()


    def _set_default_values(self):
        """Set default values for essential configuration parameters"""
        # Network parameters
        if 'size' not in self.rings_config:
            self.rings_config['size'] = 1_000_000
        if 'trust_density' not in self.rings_config:
            self.rings_config['trust_density'] = 0.1
        if 'batch_size' not in self.rings_config:
            self.rings_config['batch_size'] = 5000
        if 'iterations' not in self.rings_config:
            self.rings_config['iterations'] = 5
        if 'blocks_per_iteration' not in self.rings_config:
            self.rings_config['blocks_per_iteration'] = 100
        if 'block_time' not in self.rings_config:
            self.rings_config['block_time'] = 12

    def _load_config(self, path: str) -> Dict:
        """
        Load and parse a YAML configuration file.
        
        Returns an empty dict if the file cannot be loaded, allowing the system
        to fall back to default values.
        """
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load config from {path}: {e}")
            return {}
            
    def _apply_cli_params(self, params: Dict):
        """
        Apply CLI parameters, overriding configuration values.
        
        CLI parameters take precedence over file-based configuration.
        """
        # Override network parameters
        for key in ['size', 'trust_density', 'batch_size', 'iterations', 
                   'blocks_per_iteration', 'block_time']:
            if params.get(key) is not None:
                self.rings_config[key] = params[key]

    def _validate_config(self):
        """
        Validate the configuration values for correctness.
        
        Raises ValueError if configuration is invalid.
        """
        required_network_params = ['size', 'trust_density', 'batch_size', 'iterations']
        for param in required_network_params:
            if param not in self.rings_config:
                raise ValueError(f"Missing required network parameter: {param}")

        if 'profiles' not in self.agent_config:
            raise ValueError("Agent configuration must define agent profiles")


    @property
    def network_size(self) -> int:
        """Get the configured network size"""
        return self.rings_config['size']

    @property
    def trust_density(self) -> float:
        """Get the configured trust density"""
        return self.rings_config['trust_density']

    @property
    def batch_size(self) -> int:
        """Get the configured batch size"""
        return self.rings_config['batch_size']

    @property
    def iterations(self) -> int:
        """Get the configured number of iterations"""
        return self.rings_config['iterations']

    @property
    def blocks_per_iteration(self) -> int:
        """Get the configured blocks per iteration"""
        return self.rings_config['blocks_per_iteration']

    @property
    def block_time(self) -> int:
        """Get the configured block time"""
        return self.rings_config['block_time']
    
    @property
    def agent_distribution(self) -> Dict[str, float]:
        """
        Get the normalized agent distribution from the configuration.
        This converts the raw counts from agent_config into proportional weights.
        """
        # Get distribution from agent config
        raw_distribution = self.agent_config.get('agent_distribution', {})
        
        if not raw_distribution:
            # Provide default distribution if none specified
            raw_distribution = {
                'honest_user': 10,
                'group_creator': 1,
                'sybil_attacker': 2,
                'trust_hub': 5
            }
            
        # Calculate total for normalization
        total = sum(raw_distribution.values())
        
        # Return normalized weights
        return {
            profile: count/total 
            for profile, count in raw_distribution.items()
        }

    def get_profile_config(self, profile_name: str) -> Dict:
        """
        Get configuration for a specific agent profile.
        This provides a clean interface to access profile-specific settings.
        """
        profiles = self.agent_config.get('profiles', {})
        if profile_name not in profiles:
            raise ValueError(f"Unknown agent profile: {profile_name}")
        return profiles[profile_name]

class RingsSimulation:
    """Main simulation class that orchestrates the agent-based Rings network simulation"""
    
    def __init__(self, config: SimulationConfig, fast_mode: bool = True):
        self.fast_mode = fast_mode
        self.config = config
        self.simulation_start_time = datetime.now()
        
        # Initialize Rings client with minimal caching in fast mode
        self.rings_client = RingsClient(
            RINGS,
            RINGS_ABI,
            gas_limits=config.rings_config.get('gas_limits', {}),
            cache_config={'enabled': not fast_mode, 'ttl': 60}
        )
        
        # Only initialize collector if not in fast mode
        self.collector = None if fast_mode else CirclesDataCollector(
            config.rings_config.get('db_path', "rings_simulation.duckdb")
        )

        # Initialize agent manager with optional collector
        self.agent_manager = AgentManager(
            config=config.agent_config,
            data_collector=self.collector
        )
        
        # Initialize network components
        self.builder = NetworkBuilder(
            RINGS,
            RINGS_ABI,
            batch_size=config.rings_config.get('batch_size', 5000),
            agent_manager=self.agent_manager,
            data_collector=self.collector
        )
        
        self.evolver = NetworkEvolver(
            RINGS,
            RINGS_ABI,
            agent_manager=self.agent_manager,
            collector=self.collector,
            gas_limits=config.rings_config.get('gas_limits', None)
        )
        
        self.analyzer = NetworkAnalyzer(RINGS, RINGS_ABI)
        
        # Setup result tracking
        self.iteration_stats = []
        self.event_logs = []
        
        # Register event handlers
        self._register_event_handlers()

    def _register_event_handlers(self):
        """Set up comprehensive event handling for all network actions"""
        
        def on_human_registered(address: str, inviter: str = None, block: int = None, timestamp: datetime = None):
            current_block = block if block is not None else chain.blocks.head.number
            current_time = timestamp if timestamp is not None else datetime.fromtimestamp(chain.blocks.head.timestamp)
            
            event = {
                'event': 'human_registered',
                'address': address,
                'inviter': inviter,
                'timestamp': current_time,
                'block': current_block
            }
            self.event_logs.append(event)
            
            if self.collector:
                self.collector.record_human_registration(
                    address=address,
                    block_number=current_block,
                    timestamp=current_time,
                    inviter_address=inviter,
                    welcome_bonus=200.0 if inviter else 0.0
                )

        def on_trust_created(truster: str, trustee: str, limit: int, block: int = None, timestamp: datetime = None):
            current_block = block if block is not None else chain.blocks.head.number
            current_time = timestamp if timestamp is not None else datetime.fromtimestamp(chain.blocks.head.timestamp)
            
            event = {
                'event': 'trust_created',
                'truster': truster,
                'trustee': trustee,
                'limit': limit,
                'timestamp': current_time,
                'block': current_block
            }
            self.event_logs.append(event)

        def on_mint_performed(address: str, amount: int, block: int = None, timestamp: datetime = None):
            current_block = block if block is not None else chain.blocks.head.number
            current_time = timestamp if timestamp is not None else datetime.fromtimestamp(chain.blocks.head.timestamp)
            
            event = {
                'event': 'mint',
                'address': address,
                'amount': amount,
                'timestamp': current_time,
                'block': current_block
            }
            self.event_logs.append(event)

        def on_transfer_performed(from_address: str, to_address: str, amount: int, block: int = None, timestamp: datetime = None):
            current_block = block if block is not None else chain.blocks.head.number
            current_time = timestamp if timestamp is not None else datetime.fromtimestamp(chain.blocks.head.timestamp)
            
            event = {
                'event': 'transfer',
                'from_address': from_address,
                'to_address': to_address,
                'amount': amount,
                'timestamp': current_time,
                'block': current_block
            }
            self.event_logs.append(event)

        def on_group_created(creator: str, group_address: str, name: str, block: int = None, timestamp: datetime = None):
            current_block = block if block is not None else chain.blocks.head.number
            current_time = timestamp if timestamp is not None else datetime.fromtimestamp(chain.blocks.head.timestamp)
            
            event = {
                'event': 'group_created',
                'creator': creator,
                'group_address': group_address,
                'name': name,
                'timestamp': current_time,
                'block': current_block
            }
            self.event_logs.append(event)

        # Register all event handlers
        self.builder.on_human_registered = on_human_registered
        self.builder.on_trust_created = on_trust_created
        self.evolver.on_mint_performed = on_mint_performed
        self.evolver.on_transfer_performed = on_transfer_performed
        self.evolver.on_group_created = on_group_created



    def run(self):
        """Run the complete simulation"""
        try:
            logger.info("Starting Rings network simulation")
            simulation_metadata = self._create_simulation_metadata()
            
            # Start simulation run
            if self.collector:
                self.current_simulation_id = self.collector.start_simulation_run(
                    parameters=simulation_metadata,
                    description="Rings Network Simulation"
                )
                
            # Build initial network
            if not self._build_initial_network():
                return False
                
            # Run network evolution
            if not self._run_iterations():
                return False
                
            # Export results
            self._export_results(simulation_metadata)
            
            if self.collector:
                self.collector.end_simulation_run()
                
            return True
            
        except Exception as e:
            logger.error(f"Simulation failed: {e}", exc_info=True)
            return False
        

    def _build_initial_network(self) -> bool:
        """Build the initial network with agents"""
        try:
            logger.info(f"Building initial network with {self.config.network_size:,} agents...")
            
            # Calculate number of agents per profile
            distribution = {
                profile: int(weight * self.config.network_size)
                for profile, weight in self.config.agent_distribution.items()
            }
            
            # Ensure we don't lose agents to rounding
            total_allocated = sum(distribution.values())
            if total_allocated < self.config.network_size:
                # Add remaining agents to the largest group
                largest_profile = max(distribution.items(), key=lambda x: x[1])[0]
                distribution[largest_profile] += self.config.network_size - total_allocated
            
            success = self.builder.build_large_network(
                target_size=self.config.network_size,
                profile_distribution=distribution
            )
            
            if success:
                self._record_network_snapshot("initial")
                logger.info("Successfully built initial network")
                return True
                
            logger.error("Failed to build initial network")
            return False
            
        except Exception as e:
            logger.error(f"Error building initial network: {e}")
            return False

    def _run_iterations(self) -> bool:
        """Run all simulation iterations"""
        logger.info(f"Running {self.config.iterations} iterations")
        
        for i in range(self.config.iterations):
            logger.info(f"Starting iteration {i+1}/{self.config.iterations}")
            
            # Advance time
            if not self.evolver.advance_time(
                self.config.blocks_per_iteration,
                self.config.block_time
            ):
                logger.error(f"Failed to advance time at iteration {i+1}")
                return False
                
            # Process agent actions
            stats = self.evolver.evolve_network(i + 1)
            self.iteration_stats.append(stats)
            
            # Only record snapshot if not in fast mode
            if not self.fast_mode:
                self._record_network_snapshot(f"iteration_{i+1}")
                
            # Log progress
            self._log_iteration_summary(i + 1, stats)
            
        return True

    def _record_network_snapshot(self, label: str):
        """Record network state with label, only if not in fast mode"""
        if not self.fast_mode and self.collector:
            try:
                self.collector.record_network_statistics(
                    block_number=chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp)
                )
            except Exception as e:
                logger.error(f"Failed to record network snapshot '{label}': {e}")


    def _create_simulation_metadata(self) -> dict:
        """
        Create metadata about the simulation run.
        
        This metadata includes all relevant configuration parameters and 
        system information needed to reproduce the simulation.
        """
        return {
            'start_time': self.simulation_start_time.isoformat(),
            'config': {
                'network_size': self.config.network_size,
                'trust_density': self.config.trust_density,
                'batch_size': self.config.batch_size,
                'iterations': self.config.iterations,
                'blocks_per_iteration': self.config.blocks_per_iteration,
                'block_time': self.config.block_time,
                'agent_profiles': list(self.config.agent_config.get('profiles', {}).keys())
            },
            'contract_address': RINGS,
            'chain_id': networks.provider.chain_id
        }

    def _log_iteration_summary(self, iteration: int, stats: dict):
        """Log summary of iteration results"""
        logger.info(
            f"Iteration {iteration} complete:\n"
            f"  - Total actions: {stats.get('total_actions', 0)}\n"
            f"  - Humans registered: {stats.get('register_human', 0)}\n"
            f"  - Mints: {stats.get('mint', 0)}\n"
            f"  - Trusts: {stats.get('trust', 0)}\n"
            f"  - Transfers: {stats.get('transfer', 0)}\n"
            f"  - Groups created: {stats.get('create_group', 0)}"
        )

    def _export_results(self, metadata: dict):
        """Export simulation results if not in fast mode"""
        if self.fast_mode:
            logger.info("Skipping result export in fast mode")
            return
            
        output_dir = f"simulation_results/sim_{self.simulation_start_time:%Y%m%d_%H%M%S}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Export database tables
        self.collector.export_to_csv(output_dir)
        
        # Export agent statistics 
        self._export_agent_statistics(output_dir)
        
        # Export iteration statistics
        self._export_iteration_statistics(output_dir)
        
        # Export event logs
        self._export_event_logs(output_dir)
        
        # Save metadata
        with open(os.path.join(output_dir, 'simulation_metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)

    def _export_agent_statistics(self, output_dir: str):
        """Export statistics about agents and their activities"""
        agent_stats = []
        for agent_id, agent in self.agent_manager.agents.items():
            agent_stats.append({
                'agent_id': agent_id,
                'profile_name': agent.profile.name,
                'description': agent.profile.description,
                'accounts': len(agent.accounts),
                'trusted_addresses': len(agent.trusted_addresses),
                'max_daily_actions': agent.profile.max_daily_actions,
                'risk_tolerance': agent.profile.risk_tolerance,
                'target_account_count': agent.profile.target_account_count,
                # Add action configuration statistics
                'action_types': len(agent.profile.action_configs),
                'preferred_contracts': ','.join(agent.profile.preferred_contracts)
            })
            
        pd.DataFrame(agent_stats).to_csv(
            os.path.join(output_dir, 'agent_statistics.csv'),
            index=False
        )

    def _export_iteration_statistics(self, output_dir: str):
        """Export per-iteration statistics"""
        pd.DataFrame(self.iteration_stats).to_csv(
            os.path.join(output_dir, 'iteration_statistics.csv'),
            index_label='iteration'
        )

    def _export_event_logs(self, output_dir: str):
        """Export chronological event logs"""
        pd.DataFrame(self.event_logs).to_csv(
            os.path.join(output_dir, 'event_logs.csv'),
            index=False
        )

@click.group()
def cli():
    """Rings Network Agent-based Simulation CLI"""
    pass

@cli.command()
@click.option('--rings-config', default='config/rings_config.yaml', help='Rings configuration file')
@click.option('--agent-config', default='config/agent_config.yaml', help='Agent configuration file')
@click.option('--fast-mode/--no-fast-mode', default=True, help='Run in fast mode without data collection')
@click.option('--network-size', type=int, help='Override network size')
@click.option('--trust-density', type=float, help='Override trust density')
@click.option('--batch-size', type=int, help='Override batch size')
@click.option('--iterations', type=int, help='Override iteration count')
@click.option('--blocks-per-iteration', type=int, help='Override blocks per iteration')
def simulate(rings_config, agent_config, fast_mode, network_size, trust_density, 
            batch_size, iterations, blocks_per_iteration):
    """Run the Rings network simulation"""
    
    cli_params = {
        'size': network_size,
        'trust_density': trust_density,
        'batch_size': batch_size,
        'iterations': iterations,
        'blocks_per_iteration': blocks_per_iteration
    }
    
    config = SimulationConfig(
        rings_config_path=rings_config,
        agent_config_path=agent_config,
        cli_params={k: v for k, v in cli_params.items() if v is not None}
    )
    
    click.echo(f"\nStarting simulation in {'fast' if fast_mode else 'normal'} mode")
    
    with networks.gnosis.mainnet_fork.use_provider("foundry"):
        simulation = RingsSimulation(config, fast_mode=fast_mode)
        if not simulation.run():
            click.echo("Simulation failed. Check logs for details.")
            exit(1)
        click.echo("Simulation completed successfully!")


@cli.command()
@click.argument('db_path', default="rings_simulation.duckdb")
def analyze(db_path):
    """Analyze simulation results"""
    collector = CirclesDataCollector(db_path)
    
    click.echo("\nAnalysis Results:")
    for name, query in collector.get_analysis_queries().items():
        click.echo(f"\n{name.upper()}:")
        results = collector.con.execute(query).df()
        click.echo(results.to_string())
        
    collector.close()

if __name__ == "__main__":
    cli()