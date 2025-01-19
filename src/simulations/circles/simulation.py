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
from src.protocols.interfaces.balancerv2vault import BalancerV2VaultClient

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


    def get_agent_distribution(self) -> Dict[str, int]:
        """Get distribution of agent types"""
        distribution = self.agent_config.get('agent_distribution', {})
        if not distribution:
            raise ValueError("No agent distribution configured")
            
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
        },
         'wxdai': {
            'address': '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
            'client_class': BalancerV2VaultClient,
            'module_name': 'balancerv2vault',
            'abi_folder': 'balancer_v2',
            'strategy': 'basic'
        }
    }

    def _compute_initial_balances(self) -> Dict[str, Dict[int, int]]:
        """
        Compute balances for all avatars based on trustMarkers state.
        Returns Dict[avatar_address, Dict[token_id, balance]]
        """
        circles_state = self.initial_state.get('CirclesHub', {})
        
        trustMarkers = circles_state.get('trustMarkers', {})
        avatars = circles_state.get('avatars', [])

        if not trustMarkers and not avatars:
            logger.info(f"Current state keys: {self.initial_state.keys()}")
            logger.info(f"CirclesHub state content: {circles_state}")
            logger.warning("No trustMarkers or avatars state found for balance computation")
            return {}

        client = self.clients.get('circleshub')
        if not client:
            logger.warning("No CirclesHub client found for balance computation")
            return {}

        # Build lists for batch call
        accounts_list = []
        ids_list = []
        mapping = []  # To track address->tokenId mapping
        unique_pairs = set()  # Track unique (address, token_id) pairs

        # First get all token IDs
        token_ids = {}  # address -> token_id mapping
        for avatar in avatars:
            try:
                token_ids[avatar] = client.toTokenId(avatar)
            except Exception as e:
                logger.debug(f"Skipping avatar {avatar} token creation: {e}")

        # For each avatar, check their balance of tokens they trust
        for avatar in avatars:
            # Check their own token balance
            if avatar in token_ids:
                pair = (avatar, token_ids[avatar])
                if pair not in unique_pairs:
                    accounts_list.append(avatar)
                    ids_list.append(token_ids[avatar])
                    mapping.append(pair)
                    unique_pairs.add(pair)

            # Check tokens from trust relationships
            trusted = trustMarkers.get(avatar, {})
            for trustee, _ in trusted:
                if trustee in token_ids:
                    pair = (avatar, token_ids[trustee])
                    if pair not in unique_pairs:
                        accounts_list.append(avatar)
                        ids_list.append(token_ids[trustee])
                        mapping.append(pair)
                        unique_pairs.add(pair)

        if not accounts_list:
            logger.warning("No accounts found to check balances")
            return {}

        try:
            # Get balances in batch
            balances = client.balanceOfBatch(accounts_list, ids_list)
            
            # Create result dict with nested structure
            result = {}
            for (address, token_id), balance in zip(mapping, balances):
                if balance > 0:  # Filter zero balances
                    if address not in result:
                        result[address] = {}
                    result[address][token_id] = balance

            logger.info(f"Successfully computed balances for {len(result)} addresses")
            return result

        except Exception as e:
            logger.error(f"Failed to compute balances: {e}")
            return {}
        
    def get_initial_actions(self) -> List[Dict[str, Any]]:
        """Get initial actions to be performed on network build"""
        return []

    def get_initial_state(self) -> Dict[str, Any]:
        """Get initial state including decoded contract state"""
        # First get the base state
        state = super().get_initial_state()
        
        # Add simulation-specific state
        state.update({
            'trusted_addresses': set(),
            'group_count': 0,
            'token_balances': {}  # Initialize empty balances
        })

        # Only compute balances once if configured
        if self.config.network_config.get('compute_initial_balances', False):
            logger.info("Computing initial balances...")
            balances = self._compute_initial_balances()
            if balances:
                state['token_balances'] = balances
                non_zero_balances = sum(len(tokens) for tokens in balances.values())
                logger.info(f"Added {non_zero_balances} non-zero balances to initial state")

        print(state['token_balances'])
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
