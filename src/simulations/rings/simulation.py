from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import random
from eth_pydantic_types import HexBytes
from ape import networks, chain

from src.framework.simulation.base import BaseSimulation, BaseSimulationConfig
from src.framework.logging import get_logger
from src.protocols.interfaces.ringshub import RingsHubClient
#from src.protocols.interfaces.balancerv3vault import BalancerV3VaultClient
from src.protocols.interfaces.wxdai import WXDAIClient

logger = get_logger(__name__)

# Contract configurations
CONTRACT_CONFIGS = {
    'rings': {
        'address': '0x3D61f0A272eC69d65F5CFF097212079aaFDe8267',
        'client_class': RingsHubClient,
        'module_name': 'ringshub',
        'abi_folder': 'rings',
        'strategy': 'basic'  # Default strategy, can be overridden in config
    },
  #  'balancerv3vault': {
  #      'address': '0xbA1333333333a1BA1108E8412f11850A5C319bA9',
  #      'client_class': BalancerV3VaultClient,
  #      'module_name': 'balancerv3vault',
  #      'abi_folder': 'balancer_v3',
  #      'strategy': 'basic'
  #  },
    'wxdai': {
        'address': '0xe91d153e0b41518a2ce8dd3d7944fa863463a97d',
        'client_class': WXDAIClient,
        'module_name': 'wxdai',
        'abi_folder': 'tokens',
        'strategy': 'basic'
    }
}

class RingsSimulationConfig(BaseSimulationConfig):
    """Configuration for Rings simulation"""

    def _validate_config(self):
        """Validate Rings-specific configuration"""
        if 'strategies' not in self.network_config:
            self.network_config['strategies'] = {
                'rings': 'basic',
                'wxdai': 'basic'
            }

        """Validate Rings-specific configuration"""
        if 'trust_density' not in self.network_config:
            self.network_config['trust_density'] = 0.1

        required_params = ['size', 'trust_density', 'batch_size', 'iterations']
        for param in required_params:
            if param not in self.network_config:
                raise ValueError(f"Missing required parameter: {param}")

    def get_agent_distribution(self) -> Dict[str, int]:
        """Get distribution of agent types"""
        raw_dist = self.agent_config.get('agent_distribution', {})
        if not raw_dist:
            raw_dist = {
                'honest_user': 10,
                'group_creator': 1,
                'sybil_attacker': 2,
                'trust_hub': 5
            }

        # Calculate actual numbers
        distribution = {}
        remaining = self.network_size
        
        for profile, weight in raw_dist.items():
            if profile == list(raw_dist.keys())[-1]:
                distribution[profile] = remaining
            else:
                count = int(self.network_size * weight / sum(raw_dist.values()))
                distribution[profile] = count
                remaining -= count

        return distribution

class RingsSimulation(BaseSimulation):
    """Implementation of Rings simulation"""

    def _initialize_clients(self) -> Dict[str, Any]:
        """Initialize all contract clients"""
        clients = {}
        
        for name, config in CONTRACT_CONFIGS.items():
            try:
                # Build ABI path and validate
                abi_dir = self.project_root / "src" / "protocols" / "abis" / config['abi_folder']
                abi_path = abi_dir / f"{config['address']}.json"
                
                if not abi_path.exists():
                    logger.warning(f"ABI file not found for {name}")
                    continue

                # Initialize client
                client = config['client_class'](
                    config['address'],
                    str(abi_path),
                    gas_limits=self.config.network_config.get('gas_limits', {}),
                    data_collector=self.collector
                )
                
                clients[config['module_name']] = client
                setattr(self, f"{name}_client", client)
                
                logger.debug(f"Initialized {name} client")
                
            except Exception as e:
                logger.error(f"Failed to initialize {name} client: {e}")
                raise
                
        return clients

    def _initialize_handler(self, contract_name: str, handler_class, client):
        """Initialize a handler with configured strategy"""
        strategy = self.config.network_config['strategies'].get(
            contract_name, 
            CONTRACT_CONFIGS[contract_name]['strategy']
        )
        
        return handler_class(
            client=client,
            chain=chain,
            logger=logger,
            strategy_name=strategy
        )
        
    def _initialize_evolver(self) -> 'NetworkEvolver':
        evolver = super()._initialize_evolver()
        # Pass strategy configuration to evolver
        evolver.strategy_config = self.config.network_config['strategies']
        return evolver

    def get_initial_actions(self) -> List[Dict[str, Any]]:
        """Get initial actions for network building"""
        return [
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

    def get_initial_state(self) -> Dict[str, Any]:
        """Get initial state for agents"""
        return {
            "trusted_addresses": set(),
            "group_count": 0
        }

    def get_simulation_description(self) -> str:
        """Get simulation description"""
        return "Rings Network Agent-based Simulation"

    def _create_simulation_metadata(self) -> Dict[str, Any]:
        """Create simulation metadata"""
        return {
            'start_time': self.simulation_start_time.isoformat(),
            'config': {
                'network_size': self.config.network_size,
                'trust_density': self.config.network_config['trust_density'],
                'batch_size': self.config.batch_size,
                'iterations': self.config.iterations,
                'blocks_per_iteration': self.config.blocks_per_iteration,
                'block_time': self.config.block_time,
                'agent_profiles': list(self.config.agent_config.get('profiles', {}).keys()),
                'fast_mode': self.fast_mode
            },
            'contracts': {
                name: cfg['address'] 
                for name, cfg in CONTRACT_CONFIGS.items()
            },
            'chain_id': networks.provider.chain_id
        }