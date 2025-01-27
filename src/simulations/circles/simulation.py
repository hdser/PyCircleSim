from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import random
from eth_pydantic_types import HexBytes
from ape import networks, chain

from src.framework.simulation.base import BaseSimulation, BaseSimulationConfig
from src.framework.logging import get_logger
from src.protocols.interfaces.circleshub import CirclesHubClient
from src.protocols.interfaces.circlesbackingfactory import CirclesBackingFactoryClient
from src.protocols.interfaces.wxdai import WXDAIClient
from src.protocols.interfaces.balancerv2vault import BalancerV2VaultClient
from src.protocols.interfaces.balancerv2lbpfactory import BalancerV2LBPFactoryClient
from src.protocols.interfaces.erc20 import ERC20Client

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
        'circleslbp': {
            'address': '0x4bB5A425a68ed73Cf0B26ce79F5EEad9103C30fc',
            'client_class': CirclesBackingFactoryClient,
            'module_name': 'circlesbackingfactory',
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
        'balancerv2': {
            'address': '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
            'client_class': BalancerV2VaultClient,
            'module_name': 'balancerv2vault',
            'abi_folder': 'balancer_v2',
            'strategy': 'basic'
        },
        'balancerv2lbp': {
            'address': '0x85a80afee867aDf27B50BdB7b76DA70f1E853062',
            'client_class': BalancerV2LBPFactoryClient,
            'module_name': 'balancerv2lbpfactory',
            'abi_folder': 'balancer_v2',
            'strategy': 'basic'
        },
        'erc20': {
        'address': '',  # Generic
        'client_class': ERC20Client,
        'module_name': 'erc20',
        'abi_folder': 'tokens',
        'abi_name': 'erc20.json',
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
                    #result[address][token_id] = balance
                    datetime_object = datetime.fromtimestamp(chain.blocks.head.timestamp)
                    result[address][token_id] = {'balance': balance, 'last_day_updated': datetime_object.date()}

            #print(result)
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


    def update_state_from_transaction(self, tx, context: 'SimulationContext') -> None:
        """Update simulation state based on transaction data."""
        try:
            circles_state = context.network_state['contract_states']['CirclesHub']['state']
            involved_addresses = set()
            client = context.get_client('circleshub')
            if not client:
                return

            def clean_address(value: Any) -> Optional[str]:
                if not value:
                    return None
                if isinstance(value, (bytes, HexBytes)):
                    value = value.hex()
                if not isinstance(value, str):
                    return None
                value = value.replace('0x', '')
                if len(value) == 64:
                    value = value[-40:]
                elif len(value) != 40:
                    return None
                if not all(c in '0123456789abcdefABCDEF' for c in value):
                    return None
                return f"0x{value}"[:42]

            # First process Trust events and update trustMarkers
            decoded_logs = tx.decode_logs(abi=self.abis)
            trusts_updated = False
            
            for decoded_log in decoded_logs:
                if decoded_log.event_name == 'Trust':
                    event_data = decoded_log.event_arguments
                    truster = event_data.get('truster')
                    trustee = event_data.get('trustee')
                    expiry = event_data.get('expiry')
             
                    if truster and trustee and expiry:
                        # Update trust markers
                        if not isinstance(circles_state.get('trustMarkers'), dict):
                            circles_state['trustMarkers'] = {}
                        if truster not in circles_state['trustMarkers']:
                            circles_state['trustMarkers'][truster] = {}
                        
                        circles_state['trustMarkers'][truster][trustee] = expiry
                        trusts_updated = True
                        logger.debug(f"Updated trustMarkers: {truster} trusts {trustee} until {expiry}")
                        
                        # Add both addresses to involved set
                        involved_addresses.add(truster)
                        involved_addresses.add(trustee)

                elif decoded_log.event_name == 'PoolRegistered':
                    
                    if not isinstance(context.network_state['contract_states'].get('BalancerV2LBPFactory'), dict):
                        lbpfactory_state = context.network_state['contract_states']['BalancerV2LBPFactory'] =  {
                            'address': self.CONTRACT_CONFIGS['balancerv2lbp']['address'],
                            'state': {}
                            }
                        
                    lbpfactory_state = context.network_state['contract_states']['BalancerV2LBPFactory']['state']

                    event_data = decoded_log.event_arguments
                    poolId = event_data.get('poolId')
                    poolAddress = event_data.get('poolAddress')

                    
                    if not isinstance(lbpfactory_state.get('LBPs'), dict):
                        lbpfactory_state['LBPs'] = {}
                    if poolId not in lbpfactory_state['LBPs']:
                        lbpfactory_state['LBPs'][poolId] = {
                            'poolAddress': poolAddress,
                            'tokens': []
                        }

                elif decoded_log.event_name == 'TokensRegistered':
                    lbpfactory_state = context.network_state['contract_states']['BalancerV2LBPFactory']['state']

                    event_data = decoded_log.event_arguments
                    poolId = event_data.get('poolId')
                    tokens = event_data.get('tokens')
                    lbpfactory_state['LBPs'][poolId]['tokens'] = tokens

            # Now collect all other involved addresses from the transaction
            for decoded_log in decoded_logs:
                event_data = decoded_log.event_arguments
                for value in event_data.values():
                    if isinstance(value, (str, bytes, HexBytes)):
                        addr = clean_address(value)
                        if addr:
                            involved_addresses.add(addr)
                    elif isinstance(value, (list, tuple)):
                        for item in value:
                            addr = clean_address(item)
                            if addr:
                                involved_addresses.add(addr)

            if hasattr(tx, 'sender'):
                addr = clean_address(tx.sender)
                if addr:
                    involved_addresses.add(addr)
            if hasattr(tx, 'receiver'):
                addr = clean_address(tx.receiver)
                if addr:
                    involved_addresses.add(addr)

            logger.debug(f"Found involved addresses: {involved_addresses}")

            # For each involved address, also get their trusted addresses
            addresses_to_check = set(involved_addresses)
            if trusts_updated:  # Only do this expanded check if trust relationships changed
                for address in list(involved_addresses):
                    # Get addresses this account trusts
                    trust_markers = circles_state.get('trustMarkers', {}).get(address, {})
                    for trustee, expiry in trust_markers.items():
                        if expiry > context.chain.blocks.head.timestamp:  # Only include active trusts
                            addresses_to_check.add(trustee)
                    
                    # Get addresses that trust this account
                    for truster, trustees in circles_state.get('trustMarkers', {}).items():
                        if address in trustees:
                            if trustees[address] > context.chain.blocks.head.timestamp:  # Only include active trusts
                                addresses_to_check.add(truster)

            logger.debug(f"Checking balances for addresses: {addresses_to_check}")
            
            # Update token balances for all affected addresses
            if addresses_to_check:
                self._update_token_balances(context, addresses_to_check)
                        
        except Exception as e:
            logger.error(f"Failed to update state from transaction: {str(e)}", exc_info=True)


    def _update_token_balances(
        self, 
        context: 'SimulationContext', 
        addresses: set, 
        token_id: Optional[int] = None
    ) -> None:
        """
        Update token balances for the given addresses in CirclesHub.
        For each involved address, check their balance of all involved addresses' tokens.
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
            # Get token IDs for all involved addresses
            token_ids = {}  # address -> token_id mapping
            for addr in addresses:
                try:
                    token_ids[addr] = client.toTokenId(addr)
                except Exception as e:
                    logger.debug(f"Error getting token ID for {addr}: {e}")
                    continue

            # For each involved address, check their balance of each involved token
            balance_checks = set()  # (account, token_id) pairs to check
            for address in addresses:  # address holding the tokens
                for token_addr, token_id in token_ids.items():  # tokens to check
                    balance_checks.add((address, token_id))

            # Convert balance_checks to lists for balanceOfBatch
            for account, token_id in balance_checks:
                accounts_list.append(account)
                ids_list.append(token_id)
                mapping.append((account, token_id))

            if accounts_list:
                logger.debug(f"Querying {len(accounts_list)} balances")
                balances = client.balanceOfBatch(accounts_list, ids_list)
                date_object = datetime.fromtimestamp(context.chain.blocks.head.timestamp).date()

                for (address, t_id), bal in zip(mapping, balances):
                    if bal > 0:
                        if address not in token_balances:
                            token_balances[address] = {}
                        token_balances[address][t_id] = {
                            'balance': bal, 
                            'last_day_updated': date_object
                        }
                        logger.debug(f"Updated balance for {address} token {t_id}: {bal}")
                    else:
                        # Clean up zero balances
                        if address in token_balances and t_id in token_balances[address]:
                            del token_balances[address][t_id]
                            if not token_balances[address]:
                                del token_balances[address]

        except Exception as e:
            logger.error(f"Failed to update token balances: {e}", exc_info=True)
