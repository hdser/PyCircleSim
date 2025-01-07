import logging
import click
from typing import Type, Dict, Any
import importlib
from pathlib import Path
from ape import networks

from src.framework.simulation.base import BaseSimulation, BaseSimulationConfig
from src.framework.logging import get_logger

logging.getLogger('ape').setLevel(logging.WARNING)
logger = get_logger(__name__)

def load_simulation_module(simulation_name: str):
    """Dynamically load simulation module and return both simulation class and configs"""
    try:
        module = importlib.import_module(f"src.simulations.{simulation_name}.simulation")
        simulation_class = getattr(module, f"{simulation_name.title()}Simulation")
        config_class = getattr(module, f"{simulation_name.title()}SimulationConfig")
        contract_configs = getattr(module, 'CONTRACT_CONFIGS')
        return simulation_class, config_class, contract_configs
    except Exception as e:
        logger.error(f"Failed to load simulation module: {e}")
        raise

@click.group()
def cli():
    """Network Simulation CLI"""
    pass

@cli.command()
@click.argument('simulation_name')
@click.option('--network-config', default=None, help='Network config file')
@click.option('--agent-config', default=None, help='Agent config file')
@click.option('--fast-mode/--no-fast-mode', default=True, help='Disable DB storage in fast mode')
@click.option('--network-size', type=int, help='Override network size')
@click.option('--batch-size', type=int, help='Override batch size')
@click.option('--iterations', type=int, help='Override iteration count')
@click.option('--blocks-per-iteration', type=int, help='Override blocks per iteration')
def simulate(
    simulation_name: str,
    network_config: str,
    agent_config: str,
    fast_mode: bool,
    network_size: int,
    batch_size: int,
    iterations: int, 
    blocks_per_iteration: int
):
    """Run a network simulation"""
    try:
        # Load simulation module components
        simulation_class, config_class, contract_configs = load_simulation_module(simulation_name)
        
        # Set default config paths if not provided
        if not network_config:
            network_config = f"config/{simulation_name}_config.yaml"
        if not agent_config:
            agent_config = "config/agent_config.yaml"

        # Create config object
        cli_params = {
            'size': network_size,
            'batch_size': batch_size,
            'iterations': iterations,
            'blocks_per_iteration': blocks_per_iteration
        }
        cli_params = {k: v for k, v in cli_params.items() if v is not None}
        
        config = config_class(
            network_config_path=network_config,
            agent_config_path=agent_config,
            cli_params=cli_params
        )

        click.echo(f"\nStarting {simulation_name} simulation in {'fast' if fast_mode else 'normal'} mode")

        # Run simulation
        with networks.gnosis.mainnet_fork.use_provider("foundry"):
            sim = simulation_class(
                config=config, 
                contract_configs=contract_configs,
                fast_mode=fast_mode
            )
            
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

    except Exception as e:
        logger.error(f"Failed to run simulation: {e}", exc_info=True)
        exit(1)

if __name__ == "__main__":
    cli()