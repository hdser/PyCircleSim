import logging
from pathlib import Path
import click
from datetime import datetime, timedelta
import os
import yaml
from dotenv import load_dotenv
from ape import networks, chain
import pandas as pd
import json
from typing import Optional, Dict, Any

from src.protocols.rings import RingsClient
from src.protocols.fjord import FjordClient, PoolConfig
from src.framework.data import BaseDataCollector, CirclesDataCollector
from src.framework.agents import AgentManager
from src.framework.core import (
    NetworkBuilder, 
    NetworkEvolver,
    NetworkAnalyzer,
    NetworkAction,
    ActionResult,
    ActionRegistry,
    NetworkActionExecutor
)

# Load environment variables
load_dotenv()

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
RINGS = "0x3D61f0A272eC69d65F5CFF097212079aaFDe8267"
FJORD_LBP = "0x1ddf1109f8cb373dbb66f3d30077571ab21bdd58"

PROJECT_ROOT = Path(__file__).parent.parent
ABIS_DIR = PROJECT_ROOT / "src" / "protocols" / "abis"
RINGS_ABI = ABIS_DIR / "rings" / f"{RINGS}.json"
FJORD_ABI = ABIS_DIR / "fjord" / f"{FJORD_LBP}.json"

ABIS_DIR.mkdir(parents=True, exist_ok=True)
(ABIS_DIR / "rings").mkdir(exist_ok=True)
(ABIS_DIR / "fjord").mkdir(exist_ok=True)

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
        self.collector = None if fast_mode else CirclesDataCollector(
            config.rings_config.get('db_path', "rings_simulation.duckdb")
        )


        # Initialize clients
        rings_abi_path = validate_abi_path(RINGS_ABI, "Rings")
        self.rings_client = RingsClient(
            RINGS,
            rings_abi_path,
            gas_limits=config.rings_config.get('gas_limits', {}),
            cache_config={'enabled': not fast_mode, 'ttl': 60},
            data_collector=self.collector 
        )
        
        self.fjord_client = None  # Optional Fjord initialization here if needed

        # Initialize managers
        self.agent_manager = AgentManager(
            config=config.agent_config,
            data_collector=self.collector
        )

        self.builder = NetworkBuilder(
            rings_client=self.rings_client,  # Pass the client instance
            batch_size=config.batch_size,
            agent_manager=self.agent_manager,
            data_collector=self.collector
        )

        self.evolver = NetworkEvolver(
            rings_client=self.rings_client,  # Pass the client instance
            agent_manager=self.agent_manager,
            collector=self.collector,
            gas_limits=config.rings_config.get('gas_limits'),
            fjord_client=self.fjord_client
        )


        # Initialize tracking
        self.iteration_stats = []
        self.event_logs = []
        
        # Register event handlers
        self._register_event_handlers()

        

    def _log_event(self, event_name: str, **data):
        """Log an event with comprehensive details"""
        try:
            # Get current state
            block = chain.blocks.head
            
            event = {
                'timestamp': datetime.now().isoformat(),
                'block_number': block.number,
                'block_timestamp': block.timestamp,
                'event_type': event_name,
                'network_size': self.config.network_size,
                'iteration': len(self.iteration_stats),
                
                # Transaction details if available
                'tx_hash': data.get('tx_hash'),
                'tx_from': data.get('tx_from'),
                'tx_to': data.get('tx_to'),
                'tx_value': data.get('tx_value'),
                'tx_gas_used': data.get('tx_gas_used'),
                
                # Event-specific data
                'agent_id': data.get('agent_id'),
                'agent_profile': data.get('agent_profile'),
                'address': data.get('address'),
                'recipient': data.get('recipient'),
                'amount': data.get('amount'),
                'success': data.get('success', True),
                'error': data.get('error'),
                
                # Additional event context
                'details': data.get('details', {}),
            }

            # Remove None values
            event = {k: v for k, v in event.items() if v is not None}
            
            # Add to internal event logs
            self.event_logs.append(event)
            
            # If collector is available, also log to contract events
            if self.collector and hasattr(self.collector, 'record_simulation_event'):
                self.collector.record_simulation_event(event)
            
            logger.debug(f"Logged event: {event_name}")

        except Exception as e:
            logger.error(f"Failed to log event {event_name}: {e}")
            # Log error event
            error_event = {
                'timestamp': datetime.now().isoformat(),
                'event_type': 'ERROR',
                'original_event': event_name,
                'error': str(e)
            }
            self.event_logs.append(error_event)


    def _register_event_handlers(self):
        """Set up comprehensive event handlers for all network events"""
        
        # Transaction event handlers
        def on_transfer(from_addr, to_addr, amount, tx_hash=None, **kwargs):
            self._log_event('TRANSFER',
                tx_from=from_addr, 
                tx_to=to_addr,
                amount=amount,
                tx_hash=tx_hash,
                **kwargs)

        def on_mint(address, amount, tx_hash=None, **kwargs):
            self._log_event('MINT',
                address=address,
                amount=amount,
                tx_hash=tx_hash,
                **kwargs)
                
        def on_trust(truster, trustee, expiry, tx_hash=None, **kwargs):
            self._log_event('TRUST',
                tx_from=truster,
                tx_to=trustee, 
                expiry=expiry,
                tx_hash=tx_hash,
                **kwargs)

        # Registration events
        def on_human_registered(address, inviter, tx_hash=None, **kwargs):
            self._log_event('REGISTER_HUMAN',
                address=address,
                inviter=inviter,
                tx_hash=tx_hash,
                **kwargs)

        def on_group_created(creator, group_addr, name, tx_hash=None, **kwargs):
            self._log_event('GROUP_CREATED', 
                creator=creator,
                group_address=group_addr,
                name=name,
                tx_hash=tx_hash,
                **kwargs)

        # Agent events
        def on_agent_action(agent_id, action_type, success, **kwargs):
            self._log_event('AGENT_ACTION',
                agent_id=agent_id,
                action_type=action_type,
                success=success,
                **kwargs)

        def on_agent_created(agent_id, profile, **kwargs):
            self._log_event('AGENT_CREATED',
                agent_id=agent_id,
                agent_profile=profile,
                **kwargs)
                
        # Protocol events
        def on_stop_minting(address, tx_hash=None, **kwargs):
            self._log_event('STOP_MINTING',
                address=address,
                tx_hash=tx_hash,
                **kwargs)

        def on_wrap_token(avatar, amount, token_type, tx_hash=None, **kwargs):
            self._log_event('WRAP_TOKEN',
                avatar=avatar,
                amount=amount,
                token_type=token_type,
                tx_hash=tx_hash,
                **kwargs)
                
        # Error events    
        def on_error(context, error, **kwargs):
            self._log_event('ERROR',
                context=context,
                error=str(error),
                **kwargs)

        # Register with RingsClient
        self.rings_client.on_transfer = on_transfer
        self.rings_client.on_trust = on_trust
        self.rings_client.on_mint = on_mint
        self.rings_client.on_human_registered = on_human_registered
        self.rings_client.on_group_created = on_group_created
        self.rings_client.on_stop_minting = on_stop_minting
        self.rings_client.on_wrap_token = on_wrap_token
        self.rings_client.on_error = on_error

        # Register with components
        for component in [self.builder, self.evolver]:
            if hasattr(component, 'register_handler'):
                component.register_handler('transfer', on_transfer)
                component.register_handler('trust', on_trust) 
                component.register_handler('mint', on_mint)
                component.register_handler('human_registered', on_human_registered)
                component.register_handler('group_created', on_group_created)
                component.register_handler('agent_action', on_agent_action)
                component.register_handler('agent_created', on_agent_created)
                component.register_handler('stop_minting', on_stop_minting)
                component.register_handler('wrap_token', on_wrap_token)
                component.register_handler('error', on_error)

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

                # Set up event logging if not in fast mode
            #    contracts = {
            #        'rings': self.rings_client.contract
            #    }
            #    if self.fjord_client:
            #        contracts['fjord'] = self.fjord_client.contract
            #    
            #    self.collector.setup_contract_listeners(contracts)

            if not self._build_initial_network():
                return False
            if not self._run_iterations():
                return False

            if not self.fast_mode:
                self._export_results(metadata)

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
            
            self._log_event('network_build_start', 
                          target_size=self.config.network_size)
            
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
            
            success = self.builder.build_large_network(
                target_size=self.config.network_size,
                profile_distribution=distribution
            )
            
            self._log_event('network_build_complete',
                          success=success,
                          distribution=distribution)
            
            if success:
                logger.info("Successfully built initial network")
            else:
                logger.error("Failed to build initial network")
            
            return success
            
        except Exception as e:
            logger.error(f"Error building initial network: {e}")
            self._log_event('network_build_error', error=str(e))
            return False

    def _run_iterations(self) -> bool:
        """Run all simulation iterations"""
        logger.info(f"Running {self.config.iterations} iterations")
        
        for i in range(self.config.iterations):
            # Log iteration start
            self._log_event('iteration_start', iteration_number=i+1)
            
            if not self.evolver.advance_time(
                self.config.blocks_per_iteration,
                self.config.block_time
            ):
                logger.error(f"Failed to advance time at iteration {i+1}")
                return False
                
            # Process network evolution
            stats = self.evolver.evolve_network(i + 1)
            
            # Log the stats from this iteration
            self._log_event('iteration_complete', 
                          iteration_number=i+1,
                          total_actions=stats['total_actions'],
                          successful_actions=stats['successful_actions'],
                          action_counts=stats.get('action_counts', {}))
            
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
            'contracts': {
                'rings': RINGS,
                'fjord': FJORD_LBP if not self.fast_mode else None
            },
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

    def _export_results(self, metadata: dict):
        """Export simulation results"""
        out_dir = f"simulation_results/sim_{self.simulation_start_time:%Y%m%d_%H%M%S}"
        os.makedirs(out_dir, exist_ok=True)

        # Export standard tables
        if self.collector:
            self.collector.export_to_csv(out_dir)
            
            # Export event statistics
            event_stats = self.collector.get_event_statistics()
            if event_stats:
                pd.DataFrame(event_stats).to_csv(
                    os.path.join(out_dir, 'event_statistics.csv'),
                    index=False
                )
                
            # Export full event log
          #  events = self.collector.get_events(limit=1000000)
          #  if events:
          #      pd.DataFrame(events).to_csv(
          #          os.path.join(out_dir, 'contract_events.csv'),
          #          index=False
          #      )

        # Export simulation events log
        if self.event_logs:
            pd.DataFrame(self.event_logs).to_csv(
                os.path.join(out_dir, 'simulation_events.csv'),
                index=False
            )

        # Export other results
        if self.iteration_stats:
            pd.DataFrame(self.iteration_stats).to_csv(
                os.path.join(out_dir, 'iteration_statistics.csv'),
                index_label="iteration"
            )
        
        # Export agent statistics
        self._export_agent_statistics(out_dir)
        
        # Save metadata
        with open(os.path.join(out_dir, 'simulation_metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)

    def _export_agent_statistics(self, output_dir: str):
        """Export statistics about agents"""
        agent_stats = []
        for agent_id, agent in self.agent_manager.agents.items():
            agent_stats.append({
                'agent_id': agent_id,
                'profile_name': agent.profile.name,
                'account_count': len(agent.accounts),
                'trusted_count': len(agent.trusted_addresses),
                'max_daily_actions': agent.profile.max_daily_actions,
                'risk_tolerance': agent.profile.risk_tolerance,
                'target_account_count': agent.profile.target_account_count,
                'action_types': len(agent.profile.action_configs),
                'preferred_contracts': ','.join(agent.profile.preferred_contracts)
            })
            
        pd.DataFrame(agent_stats).to_csv(
            os.path.join(output_dir, 'agent_statistics.csv'),
            index=False
        )

    def _export_event_logs(self, out_dir: str):
        """Export event logs to CSV"""
        if not self.event_logs:
            logger.warning("No event logs to export")
            return
            
        try:
            df = pd.DataFrame(self.event_logs)
            
            # Ensure timestamp column is datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            # Export to CSV
            out_file = os.path.join(out_dir, "event_logs.csv")
            df.to_csv(out_file, index=False)
            logger.info(f"Exported {len(df)} events to {out_file}")
            
        except Exception as e:
            logger.error(f"Failed to export event logs: {e}")

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

@cli.command()
@click.argument('db_path', default="rings_simulation.duckdb")
def analyze(db_path):
    """Analyze simulation results in the DB"""
    collector = CirclesDataCollector(db_path)
    click.echo("\nAnalysis Results:")
    for name, query in collector.get_analysis_queries().items():
        click.echo(f"\n{name.upper()}:")
        results = collector.con.execute(query).df()
        click.echo(results.to_string())
    collector.close()

if __name__ == "__main__":
    cli()