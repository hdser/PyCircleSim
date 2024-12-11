import logging
from pathlib import Path
import click
from ape import networks, accounts
from rings_network import (
    NetworkBuilder,
    NetworkEvolver,
    NetworkAnalyzer,
    DataCollector
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Contract configuration
RINGS = "0x3D61f0A272eC69d65F5CFF097212079aaFDe8267"
RINGS_ABI = str(Path(__file__).parent / "abi" / f"{RINGS}.json")

def main():
    """
    Main function to be called by ape.
    """
    with networks.gnosis.mainnet_fork.use_provider("foundry") as provider:
        logger.info("Starting Rings network simulation")
        
        # Initialize components
        builder = NetworkBuilder(RINGS, RINGS_ABI)
        evolver = NetworkEvolver(RINGS, RINGS_ABI)
        analyzer = NetworkAnalyzer(RINGS, RINGS_ABI)
        collector = DataCollector(analyzer)
        
        # Build network
        logger.info("Building network...")
        if not builder.build_complete_network():
            logger.error("Failed to build network")
            return
            
        # Run simulation for 5 iterations
        logger.info("Running simulation...")
        for i in range(5):
            logger.info(f"Iteration {i+1}/5")
            
            # Collect state
            collector.collect_state(accounts.test_accounts)
            
            # Advance time and mint
            evolver.advance_time(100)
            evolver.mint_for_all(accounts.test_accounts)
            
        # Save final results
        logger.info("Saving results...")
        collector.export_data("network_evolution.json")
        
        logger.info("Simulation completed")

if __name__ == "__main__":
    main()