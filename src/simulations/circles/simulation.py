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

from src.framework.state.graph_converter import StateToGraphConverter
from src.pathfinder import GraphManager
import logging

logger = get_logger(__name__, logging.DEBUG)


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

    def _rebuild_graph(self, context: 'SimulationContext') -> None:
        """Rebuild graph from current state"""
        try:
            circles_state = context.network_state['contract_states']['CirclesHub']['state']
            client = context.get_client('circleshub')
            
            if not client:
                return

            # Convert state to dataframes using our converter
            converter = StateToGraphConverter()
            df_trusts, df_balances = converter.convert_state_to_dataframes(
                state=circles_state,
                current_time=context.chain.blocks.head.timestamp            
            )

            # Create or update graph manager
            context.graph_manager = GraphManager(
                (df_trusts, df_balances),
                graph_type='ortools'
            )
                
        except Exception as e:
            logger.error(f"Failed to rebuild graph: {e}", exc_info=True)

    def _compute_initial_balances(self) -> Dict[str, Dict[int, int]]:
        """
        Compute balances for all avatars based on the trustMarkers state.
        Returns: dict of { avatar_address : { token_id: balance } }.
        """
        # We read from self.initial_state['CirclesHub'], which is set up in get_initial_state()
        circles_state = self.initial_state.get('CirclesHub', {})
        
        # trustMarkers is dict-of-dicts: {truster: {trustee: expiry}, ...}
        trustMarkers: Dict[str, Dict[str, int]] = circles_state.get('trustMarkers', {})
        avatars: List[str] = circles_state.get('avatars', [])

        if not trustMarkers and not avatars:
            logger.info(f"Current state keys: {self.initial_state.keys()}")
            logger.info(f"CirclesHub state content: {circles_state}")
            logger.warning("No trustMarkers or avatars found for balance computation")
            return {}

        client = self.clients.get('circleshub')
        if not client:
            logger.warning("No CirclesHub client found for balance computation")
            return {}

        # We'll gather (account, tokenID) pairs in bulk for balanceOfBatch
        accounts_list = []
        ids_list = []
        mapping = []
        unique_pairs = set()

        # 1) Convert each avatar to a tokenId if possible
        token_ids = {}
        for avatar in avatars:
            try:
                token_ids[avatar] = client.toTokenId(avatar)
            except Exception as e:
                logger.debug(f"Skipping avatar {avatar} token creation: {e}")

        # 2) For each avatar: check their own token, and tokens of those they trust
        for avatar in avatars:
            if avatar in token_ids:
                pair = (avatar, token_ids[avatar])
                if pair not in unique_pairs:
                    accounts_list.append(avatar)
                    ids_list.append(token_ids[avatar])
                    mapping.append(pair)
                    unique_pairs.add(pair)

            # Check all trustees
            trusted_map = trustMarkers.get(avatar, {})
            for trustee, expiry in trusted_map.items():
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
            # 3) Use client to fetch all balances in one batch
            balances = client.balanceOfBatch(accounts_list, ids_list)
            
            # 4) Build results
            result: Dict[str, Dict[int, int]] = {}
            for (address, token_id), balance in zip(mapping, balances):
                if balance > 0:
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
        """
        Get initial state including decoded contract state. 
        Now we ensure token_balances is stored inside CirclesHub, 
        instead of at the top level.
        """
        # 1) Start with the parent's decoded state
        base_state = super().get_initial_state()

        # 2) If CirclesHub is missing, create it
        if 'CirclesHub' not in base_state:
            base_state['CirclesHub'] = {}
        circles_hub_state = base_state['CirclesHub']

        # 3) Ensure we have sub-keys
        circles_hub_state.setdefault('avatars', [])
        circles_hub_state.setdefault('trustMarkers', {})
        circles_hub_state.setdefault('token_balances', {})

        # 4) Add simulation-specific top-level state
        base_state['trusted_addresses'] = set()
        base_state['group_count'] = 0

        # 5) Optionally compute initial balances if configured
        if self.config.network_config.get('compute_initial_balances', False):
            logger.info("Computing initial balances...")
            balances = self._compute_initial_balances()
            if balances:
                circles_hub_state['token_balances'] = balances
                non_zero_balances = sum(len(tokens) for tokens in balances.values())
                logger.info(f"Added {non_zero_balances} non-zero balances to initial state")

        # 6) Put the updated CirclesHub state back into base_state
        base_state['CirclesHub'] = circles_hub_state
        return base_state

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

    def _update_simulation_state(self, context: 'SimulationContext', action_name: str, params: Dict[str, Any]) -> None:
        """
        Update simulation state after a successful action execution.
        """
        try:
            client = context.get_client('circleshub')
            if not client:
                return

            # Access our CirclesHub state from context
            circles_state = context.network_state['contract_states']['CirclesHub']['state']

            logger.debug(f"Action: {action_name}")

            # 1) If registering a Human or Group => add to 'avatars'
            if action_name in ['circleshub_RegisterHuman', 'circleshub_RegisterGroup']:
                address = params.get('sender')
                if address:
                    if 'avatars' not in circles_state:
                        circles_state['avatars'] = []
                    if address not in circles_state['avatars']:
                        circles_state['avatars'].append(address)
                    logger.debug(f"avatars now has {len(circles_state['avatars'])} addresses")

            # 2) If 'Trust' => update trustMarkers
            elif action_name == 'circleshub_Trust':
                truster = params.get('sender')
                trustee = params.get('_trustReceiver')
                expiry = params.get('_expiry')
                
                if truster and trustee and expiry:
                    if not isinstance(circles_state.get('trustMarkers'), dict):
                        circles_state['trustMarkers'] = {}
                    if truster not in circles_state['trustMarkers']:
                        circles_state['trustMarkers'][truster] = {}

                    circles_state['trustMarkers'][truster][trustee] = expiry
                    logger.debug(
                        f"Updated trustMarkers for truster={truster}, trustee={trustee}, expiry={expiry}"
                    )

            # 3) If this action can affect balances, update them
            if action_name in [
                'circleshub_PersonalMint',
                'circleshub_GroupMint',
                'circleshub_SafeTransferFrom',
                'circleshub_Burn',
                'circleshub_MulticallPathfinderTransfer',
            ]:
                addresses = set()
                from_addr = params.get('_from')
                to_addr = params.get('_to')
                sender = params.get('sender')

                if from_addr:
                    addresses.add(from_addr)
                if to_addr:
                    addresses.add(to_addr)
                if not addresses and sender:
                    addresses.add(sender)

                logger.debug(f"Involved addresses: {addresses}")

                # Check if we have a specific token ID
                token_id_param = params.get('_id')
                self._update_token_balances(context, addresses, token_id_param)

        except Exception as e:
            logger.error(f"Failed to update simulation state: {str(e)}", exc_info=True)
            logger.debug("Current state structure:", circles_state)

    def _update_token_balances(
        self, 
        context: 'SimulationContext', 
        addresses: set, 
        token_id: Optional[int] = None
    ) -> None:
        """
        Update token balances for the given addresses in CirclesHub.
        If `token_id` is specified, we only query that ID for each address.
        Otherwise, we derive the ID via client.toTokenId(address).
        """
        client = context.get_client('circleshub')
        if not client:
            return

        circles_state = context.network_state['contract_states']['CirclesHub']['state']
        token_balances = circles_state.setdefault('token_balances', {})

        if not addresses:
            return

        accounts_list = []
        ids_list = []
        mapping = []

        try:
            if token_id is not None:
                # 1) If specific _id is given, apply it for each address
                for addr in addresses:
                    if isinstance(addr, str):
                        accounts_list.append(addr)
                        ids_list.append(token_id)
                        mapping.append((addr, token_id))
            else:
                # 2) Otherwise compute the token ID from each address
                for addr in addresses:
                    if not isinstance(addr, str):
                        continue

                    try:
                        derived_id = client.toTokenId(addr)
                        accounts_list.append(addr)
                        ids_list.append(derived_id)
                        mapping.append((addr, derived_id))
                    except Exception as e:
                        logger.debug(f"Error getting token ID for {addr}: {e}")
                        continue

            if accounts_list:
                logger.debug(f"Querying balances for accounts={accounts_list}, ids={ids_list}")
                balances = client.balanceOfBatch(accounts_list, ids_list)

                for (address, t_id), bal in zip(mapping, balances):
                    if bal > 0:
                        if address not in token_balances:
                            token_balances[address] = {}
                        token_balances[address][t_id] = bal
                        logger.debug(f"Updated balance for {address} token {t_id}: {bal}")
                    else:
                        # Clean up zero
                        if address in token_balances and t_id in token_balances[address]:
                            del token_balances[address][t_id]
                            if not token_balances[address]:
                                del token_balances[address]

                #logger.debug(f"Updated token balances: {token_balances}")

        except Exception as e:
            logger.error(f"Failed to update token balances: {e}", exc_info=True)
