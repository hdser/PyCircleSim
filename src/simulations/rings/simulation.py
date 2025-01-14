# simulation.py

from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import random
from eth_pydantic_types import HexBytes
from ape import networks, chain

from src.framework.simulation.base import BaseSimulation, BaseSimulationConfig
from src.framework.logging import get_logger
from src.protocols.interfaces.ringshub import RingsHubClient
from src.protocols.interfaces.circleshub import CirclesHubClient
from src.protocols.interfaces.wxdai import WXDAIClient

logger = get_logger(__name__)


class RingsSimulationConfig(BaseSimulationConfig):
    """Configuration for Rings simulation"""

    def _validate_config(self):
        """Validate Rings-specific configuration"""
        super()._validate_config()

        if 'strategies' not in self.network_config:
            self.network_config['strategies'] = {
                'rings': 'basic',
                'circles': 'basic',
                'wxdai': 'basic'
            }


    def get_agent_distribution(self) -> Dict[str, int]:
        """Get distribution of agent types"""
        distribution = self.agent_config.get('agent_distribution', {})
        if not distribution:
            raise ValueError("No agent distribution configured")
            
        return distribution


class RingsSimulation(BaseSimulation):
    """Implementation of a Rings-based simulation"""
    
    CONTRACT_CONFIGS = {
        'rings': {
            'address': '0x3D61f0A272eC69d65F5CFF097212079aaFDe8267',
            'client_class': RingsHubClient,
            'module_name': 'ringshub',
            'abi_folder': 'rings',
            'strategy': 'sybil'  # default strategy
        },
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
                        a for a in all_agents 
                        if a != agent and len(a.accounts) > 0
                    ]).accounts.keys())),
                    "_expiry": int(chain.pending_timestamp + 365 * 24 * 60 * 60),
                    "sender": next(iter(agent.accounts.keys()))
                } if agent.accounts else None
            }
        ]

    def get_initial_state(self) -> Dict[str, Any]:
        """Get initial state for agents before simulation starts"""
        return {
            "trusted_addresses": set(),
            "group_count": 0
        }

    def get_simulation_description(self) -> str:
        """A short description of this simulation run"""
        return "Rings Network Agent-based Simulation"

    def _create_simulation_metadata(self) -> Dict[str, Any]:
        """Create simulation metadata for logging / database"""
        return {
            'start_time': self.simulation_start_time.isoformat(),
            'config': {
                'network_size': self.config.network_size,
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
