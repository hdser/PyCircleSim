import logging
from pathlib import Path
import click
from datetime import datetime
import os
from dotenv import load_dotenv
from ape import networks, accounts, chain
from rings_network import (
    NetworkBuilder,
    NetworkEvolver,
    NetworkAnalyzer,
    CirclesDataCollector
)

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

RINGS = "0x3D61f0A272eC69d65F5CFF097212079aaFDe8267"
RINGS_ABI = str(Path(__file__).parent / "abi" / f"{RINGS}.json")

class RingsSimulation:
    def __init__(self, iterations, blocks_per_iteration, db_path):
        self.iterations = iterations
        self.blocks_per_iteration = blocks_per_iteration

        self.collector = CirclesDataCollector(db_path)
        
        # Initialize core components, passing the collector where needed
        self.builder = NetworkBuilder(RINGS, RINGS_ABI)
        self.evolver = NetworkEvolver(RINGS, RINGS_ABI, collector=self.collector)
        self.analyzer = NetworkAnalyzer(RINGS, RINGS_ABI)
        
    def run(self):
        logger.info("Starting Rings network simulation")
        
        try:
            # Build and record initial network state
            logger.info("Building initial network structure...")
            if not self.builder.build_complete_network():
                logger.error("Failed to build network")
                return False
                
            # Record the initial state after network creation
            self._record_network_snapshot()
                
            # Run simulation cycles
            logger.info(f"Running simulation for {self.iterations} iterations")
            for i in range(self.iterations):
                logger.info(f"Iteration {i+1}/{self.iterations}")
                
                # Advance blockchain time
                if not self.evolver.advance_time(self.blocks_per_iteration):
                    logger.error(f"Failed to advance time at iteration {i+1}")
                    return False
                    
                # Perform minting for all accounts and record changes
                mint_results = self.evolver.mint_for_all(accounts.test_accounts)
               # if mint_results:
               #     self._record_mint_activity(mint_results)
                
                # Take a snapshot of network state after each iteration
                self._record_network_snapshot()
            
            # Export all collected data for analysis
            self._export_results()
            logger.info("Simulation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Simulation failed: {e}", exc_info=True)
            return False
        finally:
            self.collector.close()
            
    def _record_network_snapshot(self):
        current_block = chain.blocks.head.number
        current_time = datetime.fromtimestamp(chain.blocks.head.timestamp)
        
        self.collector.record_network_statistics(
            block_number=current_block,
            timestamp=current_time
        )
        
    def _record_mint_activity(self, mint_results):
        current_block = chain.blocks.head.number
        current_time = datetime.fromtimestamp(chain.blocks.head.timestamp)
        
        for account, amount in mint_results.items():
            self.collector.record_balance_change(
                account=account,
                token_id=account,
                block_number=current_block,
                timestamp=current_time,
                previous_balance=self.analyzer.get_balance(account),
                new_balance=amount,
                tx_hash="",
                event_type="MINT"
            )
            
    def _export_results(self):
        output_dir = "simulation_results"
        os.makedirs(output_dir, exist_ok=True)
        self.collector.export_to_csv(output_dir)

# This is the key part that makes it work with Ape
cli = click.Group()

@cli.command()
@click.option('--iterations', default=5, help='Number of simulation iterations')
@click.option('--blocks-per-iteration', default=100, help='Number of blocks per iteration')
@click.option('--db-path', default="rings_simulation.duckdb", help='Path to DuckDB database')
def simulate(iterations, blocks_per_iteration, db_path):
    """Runs the Rings network simulation and collects data for analysis"""
    with networks.gnosis.mainnet_fork.use_provider("foundry"):
        simulation = RingsSimulation(iterations, blocks_per_iteration, db_path)
        success = simulation.run()
        
        if not success:
            click.echo("Simulation failed. Check logs for details.")
            exit(1)
            
        click.echo("Simulation completed successfully!")