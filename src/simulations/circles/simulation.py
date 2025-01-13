# simulation.py

from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import random
from eth_pydantic_types import HexBytes
from ape import networks, chain

from src.framework.simulation.base import BaseSimulation, BaseSimulationConfig
from src.framework.logging import get_logger
from src.protocols.interfaces.circleshub import CirclesHubClient
from src.protocols.interfaces.wxdai import WXDAIClient

logger = get_logger(__name__)


class CirclesSimulationConfig(BaseSimulationConfig):
    """Configuration for Rings simulation"""

    def _validate_config(self):
        """Validate Rings-specific configuration"""
        super()._validate_config()

        if 'strategies' not in self.network_config:
            self.network_config['strategies'] = {
                'circles': 'basic',
                'wxdai': 'basic'
            }

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
        
        total_weight = sum(raw_dist.values())
        for profile, weight in raw_dist.items():
            if profile == list(raw_dist.keys())[-1]:
                # Assign all remaining to the last profile
                distribution[profile] = remaining
            else:
                count = int(self.network_size * weight / total_weight)
                distribution[profile] = count
                remaining -= count

        return distribution


class CirclesSimulation(BaseSimulation):
    """Implementation of a Rings-based simulation"""
    
    CONTRACT_CONFIGS = {
        'circles': {
            'address': '0xc12C1E50ABB450d6205Ea2C3Fa861b3B834d13e8',
            'client_class': CirclesHubClient,
            'module_name': 'circleshub',
            'abi_folder': 'circles',
            'strategy': 'basic'
        },
        'wxdai': {
            'address': '0xe91d153e0b41518a2ce8dd3d7944fa863463a97d',
            'client_class': WXDAIClient,
            'module_name': 'wxdai',
            'abi_folder': 'tokens',
            'strategy': 'basic'
        }
    }


    def get_initial_actions(self) -> List[Dict[str, Any]]:
        """Get initial actions to be performed on network build"""
        return []

    def get_initial_state(self) -> Dict[str, Any]:
        """Get initial state including decoded contract state"""
        state = super().get_initial_state()
        
        # Add simulation-specific state
        state.update({
            'trusted_addresses': set(),
            'group_count': 0
        })
        
        return state

    def get_simulation_description(self) -> str:
        """A short description of this simulation run"""
        return "Circles Network Agent-based Simulation"

    def _create_simulation_metadata(self) -> Dict[str, Any]:
        """Create simulation metadata for logging / database"""
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
                for name, cfg in self.CONTRACT_CONFIGS.items()
            },
            'chain_id': networks.provider.chain_id
        }
