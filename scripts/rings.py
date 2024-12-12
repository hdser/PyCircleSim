import logging
from pathlib import Path
import click
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from ape import networks, accounts, chain
import pandas as pd
import json
from rings_network import (
    NetworkBuilder,
    NetworkEvolver,
    NetworkAnalyzer,
    CirclesDataCollector,
    AgentManager,
    AgentPersonality,
    AgentProfile,
    AgentEconomicStatus
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
RINGS = "0x3D61f0A272eC69d65F5CFF097212079aaFDe8267"
RINGS_ABI = str(Path(__file__).parent / "abi" / f"{RINGS}.json")

class SimulationConfig:
    """Configuration holder for simulation parameters"""
    def __init__(
        self,
        network_size: int = 1_000_000,
        trust_density: float = 0.1,
        batch_size: int = 5000,
        iterations: int = 5,
        blocks_per_iteration: int = 100,
        block_time: int = 12,
        db_path: str = "rings_simulation.duckdb",
        personality_weights: dict = None
    ):
        self.network_size = network_size
        self.trust_density = trust_density
        self.batch_size = batch_size
        self.iterations = iterations
        self.blocks_per_iteration = blocks_per_iteration
        self.block_time = block_time
        self.db_path = db_path
        
        # Default personality distribution if none provided
        self.personality_weights = personality_weights or {
            AgentPersonality.CONSERVATIVE: 0.2,
            AgentPersonality.SOCIAL: 0.3,
            AgentPersonality.ENTREPRENEUR: 0.2,
            AgentPersonality.OPPORTUNIST: 0.15,
            AgentPersonality.COMMUNITY: 0.15
        }

class RingsSimulation:
    """Main simulation class that orchestrates the agent-based Rings network simulation"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.simulation_start_time = datetime.now()
        
        # Initialize components
        self.collector = CirclesDataCollector(config.db_path)
        self.agent_manager = AgentManager()
        
        self.builder = NetworkBuilder(
            RINGS,
            RINGS_ABI,
            batch_size=config.batch_size,
            agent_manager=self.agent_manager 
        )
        
        # Pass the collector to NetworkEvolver
        self.evolver = NetworkEvolver(
            RINGS,
            RINGS_ABI,
            agent_manager=self.agent_manager,
            collector=self.collector 
        )
        
        self.analyzer = NetworkAnalyzer(RINGS, RINGS_ABI)
        
        # Setup result tracking
        self.iteration_stats = []
        self.event_logs = []
        
        # Register event handlers
        self._register_event_handlers()

    def _register_event_handlers(self):
        def on_human_registered(address: str, inviter: str = None, block: int = None, timestamp: datetime = None):
            # Use provided block/timestamp or get current if not provided
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
            
            self.collector.record_human_registration(
                address=address,
                block_number=current_block,
                timestamp=current_time,
                inviter_address=inviter,
                welcome_bonus=200.0 if inviter else 0.0
            )

        def on_trust_created(truster: str, trustee: str, limit: int, block: int = None, timestamp: datetime = None):
            # Use provided block/timestamp or get current if not provided
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
            
            self.collector.record_trust_relationship(
                truster=truster,
                trustee=trustee,
                block_number=current_block,
                timestamp=current_time,
                trust_limit=float(limit),
                expiry_time=current_time + timedelta(days=365)
            )

        self.builder.on_human_registered = on_human_registered
        self.builder.on_trust_created = on_trust_created

    def run(self):
        """Run the complete simulation with clear phase separation"""
        try:
            logger.info("Starting Rings network simulation")
            simulation_metadata = self._create_simulation_metadata()
            
            # Phase 1: Build Network
            logger.info("Phase 1: Building Initial Network")
            if not self._build_initial_network():
                return False
                
            # Record initial state before evolution
            self._record_network_snapshot("network_built")
            
            # Phase 2: Network Evolution
            logger.info("Phase 2: Starting Network Evolution")
            if not self._run_iterations():
                return False
                
            self._export_results(simulation_metadata)
            return True
            
        except Exception as e:
            logger.error(f"Simulation failed: {e}", exc_info=True)
            return False

    def _build_initial_network(self) -> bool:
        """Build the initial network with agents"""
        logger.info(f"Building initial network with {self.config.network_size:,} agents...")
        success = self.builder.build_large_network(
            target_size=self.config.network_size,
            personality_weights=self.config.personality_weights
        )
        
        if success:
            self._record_network_snapshot("initial")
            return True
            
        logger.error("Failed to build initial network")
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
            
            # Record snapshot
            self._record_network_snapshot(f"iteration_{i+1}")
            
            # Log progress
            self._log_iteration_summary(i + 1, stats)
            
        return True

    def _record_network_snapshot(self, label: str):
        """Record network state with label"""
        try:
            self.collector.record_network_statistics(
                block_number=chain.blocks.head.number,
                timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp)
            )
        except Exception as e:
            logger.error(f"Failed to record network snapshot '{label}': {e}")

    def _create_simulation_metadata(self) -> dict:
        """Create metadata about the simulation run"""
        return {
            'start_time': self.simulation_start_time.isoformat(),
            'config': {
                'network_size': self.config.network_size,
                'trust_density': self.config.trust_density,
                'batch_size': self.config.batch_size,
                'iterations': self.config.iterations,
                'blocks_per_iteration': self.config.blocks_per_iteration,
                'block_time': self.config.block_time,
                'personality_weights': {
                    k.value: v for k, v in self.config.personality_weights.items()
                }
            },
            'contract_address': RINGS,
            'chain_id': networks.provider.chain_id
        }

    def _log_iteration_summary(self, iteration: int, stats: dict):
        """Log summary of iteration results"""
        logger.info(
            f"Iteration {iteration} complete:\n"
            f"  - Total actions: {stats['total_actions']}\n"
            f"  - Mints: {stats['mints']}\n"
            f"  - Trusts: {stats['trusts']}\n"
            f"  - Transfers: {stats['transfers']}\n"
            f"  - Groups created: {stats['groups_created']}"
        )

    def _export_results(self, metadata: dict):
        """Export all simulation results"""
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
        """Export statistics about agents"""
        agent_stats = []
        for address, agent in self.agent_manager.agents.items():
            agent_stats.append({
                'address': address,
                'personality': agent.profile.personality.value,
                'economic_status': agent.profile.economic_status.value,
                'accounts': len(agent.accounts),
                'trusted_agents': len(agent.trusted_agents),
                'groups': len(agent.groups),
                'trust_threshold': agent.profile.trust_threshold,
                'activity_level': agent.profile.activity_level,
                'risk_tolerance': agent.profile.risk_tolerance
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
@click.option('--network-size', default=1_000_000, help='Number of agents')
@click.option('--trust-density', default=0.1, help='Trust relationship density')
@click.option('--batch-size', default=5000, help='Processing batch size')
@click.option('--iterations', default=5, help='Simulation iterations')
@click.option('--blocks-per-iteration', default=100, help='Blocks per iteration')
@click.option('--block-time', default=12, help='Seconds per block')
@click.option('--db-path', default="rings_simulation.duckdb", help='Database path')
@click.option('--conservative-weight', default=0.2, help='Conservative personality weight')
@click.option('--social-weight', default=0.3, help='Social personality weight')
@click.option('--entrepreneur-weight', default=0.2, help='Entrepreneur personality weight')
@click.option('--opportunist-weight', default=0.15, help='Opportunist personality weight')
@click.option('--community-weight', default=0.15, help='Community personality weight')
def simulate(
    network_size, trust_density, batch_size, iterations,
    blocks_per_iteration, block_time, db_path,
    conservative_weight, social_weight, entrepreneur_weight,
    opportunist_weight, community_weight
):
    """Run the Rings network simulation"""
    personality_weights = {
        AgentPersonality.CONSERVATIVE: conservative_weight,
        AgentPersonality.SOCIAL: social_weight,
        AgentPersonality.ENTREPRENEUR: entrepreneur_weight,
        AgentPersonality.OPPORTUNIST: opportunist_weight,
        AgentPersonality.COMMUNITY: community_weight
    }
    
    # Normalize weights
    total = sum(personality_weights.values())
    personality_weights = {k: v/total for k, v in personality_weights.items()}
    
    config = SimulationConfig(
        network_size=network_size,
        trust_density=trust_density,
        batch_size=batch_size,
        iterations=iterations,
        blocks_per_iteration=blocks_per_iteration,
        block_time=block_time,
        db_path=db_path,
        personality_weights=personality_weights
    )
    
    click.echo("\nStarting simulation with configuration:")
    click.echo(f"Network size: {network_size:,} agents")
    click.echo(f"Personality distribution: {personality_weights}")
    click.echo(f"Trust density target: {trust_density}")
    click.echo(f"Iterations: {iterations}")
    
    with networks.gnosis.mainnet_fork.use_provider("foundry"):
        simulation = RingsSimulation(config)
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