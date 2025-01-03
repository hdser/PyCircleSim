from typing import Dict, Optional, List, Any
from datetime import datetime
import logging
import random

from ape import chain
from eth_pydantic_types import HexBytes

from src.framework.agents import AgentManager, BaseAgent, ActionType
from src.framework.data import CirclesDataCollector
from src.protocols.ringshub import RingsHubClient
from src.protocols.fjordlbpproxyv6 import FjordLbpProxyV6Client
from src.protocols.balancerv3vault import BalancerV3VaultClient

# Import your handler classes
from src.protocols.ringshub import (
    PersonalMintHandler,
    RegisterHumanHandler,
    TrustHandler,
    RegisterGroupHandler,
    SafeTransferFromHandler,
    WrapHandler
)
from src.framework.logging import get_logger

logger = get_logger(__name__)


class NetworkEvolver():
    """Enhanced NetworkEvolver with proper action timing control"""
    
    def __init__(
        self,
        client: RingsHubClient,
        agent_manager: AgentManager,
        collector: Optional[CirclesDataCollector] = None,
        gas_limits: Optional[Dict] = None,
        fjord_client: Optional[FjordLbpProxyV6Client] = None
    ):
        
        # Initialize clients
        self.client = client
        self.fjord_client = fjord_client
        
        self.agent_manager = agent_manager
        self.collector = collector
        
        # Track last action times
        self.last_action_times: Dict[str, int] = {}
        self.min_blocks_between_actions = 5  # Minimum blocks between actions
        
        # Default gas limits
        self.gas_limits = gas_limits or {
            'register_human': 500000,
            'trust': 300000,
            'mint': 300000,
            'transfer': 300000,
            'create_group': 1000000,
            'wrap': 500000,
        }

        # Initialize handler classes
        self.mint_handler = PersonalMintHandler(
            client=self.client,
            chain=chain,
            logger=logger,
        )

        self.trust_handler = TrustHandler(
            client=self.client,
            chain=chain,
            logger=logger
        )

        self.transfer_handler = SafeTransferFromHandler(
            client=self.client,
            chain=chain,
            logger=logger,
        )

        self.group_creation_handler = RegisterGroupHandler(
            client=self.client,
            chain=chain,
            logger=logger,
        )

        self.human_registration_handler = RegisterHumanHandler(
            client=self.client,
            chain=chain,
            logger=logger
        )
        self.wrap_handler = WrapHandler(
            client=self.client,
            chain=chain,
            logger=logger
        )

    def advance_time(self, blocks: int, block_time: int = 5) -> bool:
        """
        Central time advancement method - only called by main simulation loop
        """
        try:
            batch_size = 5
            total_mined = 0
            
            while total_mined < blocks:
                current_batch = min(batch_size, blocks - total_mined)
                chain.mine(current_batch)
                chain.pending_timestamp += current_batch * block_time
                total_mined += current_batch

            logger.debug(
                f"Advanced chain by {blocks} blocks. "
                f"New block: {chain.blocks.head.number}, "
                f"Time: {datetime.fromtimestamp(chain.blocks.head.timestamp)}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to advance time: {e}", exc_info=True)
            return False

    def evolve_network(self, iteration: int) -> Dict[str, int]:
        """
        Evolve network with proper action timing and state tracking
        """
        stats = {
            'total_actions': 0,
            'successful_actions': 0,
            'action_counts': {}
        }
        
        try:
            all_agents = list(self.agent_manager.agents.values())
            random.shuffle(all_agents)

            # Current chain state
            chain_state = {
                'current_block': chain.blocks.head.number,
                'current_time': chain.blocks.head.timestamp,
                'balances': {}
            }

            # Process each agent's action in the current block
            for agent in all_agents:
                if not self._check_action_timing(agent.agent_id, chain_state['current_block']):
                    continue
                    
                action_type, acting_address, params = agent.select_action(
                    current_block=chain_state['current_block'],
                    state=chain_state
                )
                
                if action_type is None:
                    continue

                stats['total_actions'] += 1
                
                # Execute action without advancing time
                success = self._execute_action(
                    agent, 
                    action_type,
                    acting_address,
                    params
                )
                
                if success:
                    stats['successful_actions'] += 1
                    action_name = action_type.name.lower()
                    stats['action_counts'][action_name] = stats['action_counts'].get(action_name, 0) + 1
                    self.last_action_times[agent.agent_id] = chain_state['current_block']
                    
                    # Record successful action
                    agent.record_action(
                        action_type.name,
                        chain_state['current_block'],
                        True
                    )

            logger.info(
                f"Iteration {iteration} complete - "
                f"Actions processed: {stats['total_actions']}, "
                f"Successful: {stats['successful_actions']}"
            )
            return stats
            
        except Exception as e:
            logger.error(f"Network evolution failed: {e}", exc_info=True)
            return stats

    def _check_action_timing(self, agent_id: str, current_block: int) -> bool:
        """Check if enough blocks have passed since last action"""
        last_action = self.last_action_times.get(agent_id, 0)
        blocks_passed = current_block - last_action
        return blocks_passed >= self.min_blocks_between_actions

    def _execute_action(
        self,
        agent: BaseAgent,
        action_type: ActionType,
        acting_address: str,
        params: Dict
    ) -> bool:
        """Execute action without time advancement"""
        try:
            if action_type == ActionType.MINT:
                return self.mint_handler.execute(agent)
            elif action_type == ActionType.TRUST:
                return self.trust_handler.execute(agent,self.agent_manager)
            elif action_type == ActionType.TRANSFER:
                return self.transfer_handler.execute(agent)
            elif action_type == ActionType.CREATE_GROUP:
                return self.group_creation_handler.execute(agent)
            elif action_type == ActionType.REGISTER_HUMAN:
                return self.human_registration_handler.execute(agent)
            elif action_type == ActionType.WRAP_TOKEN:
                return self.wrap_handler.execute(agent)
            return False
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}", exc_info=True)
            return False

    def get_chain_state(self) -> Dict[str, Any]:
        """Get current chain state"""
        return {
            'current_block': chain.blocks.head.number,
            'current_time': chain.blocks.head.timestamp,
            'timestamp': datetime.fromtimestamp(chain.blocks.head.timestamp),
            'gas_price': chain.gas_price,
            'last_action_times': self.last_action_times.copy()
        }
        
    def _update_statistics(self, stats: Dict[str, int], action_type: ActionType, success: bool):
        """Update action statistics"""
        stats['total_actions'] += 1
        if success:
            stats['successful_actions'] += 1
            action_name = action_type.name.lower()
            stats['action_counts'][action_name] = stats['action_counts'].get(action_name, 0) + 1
            
    def validate_mint_period(self, address: str) -> bool:
        """
        Validate if address is in a valid mint period without advancing time
        """
        try:
            if not self.client.isHuman(address):
                return False
            if self.client.stopped(address):
                return False
                
            issuance, start_period, end_period = self.client.calculateIssuance(address)
            if issuance == 0:
                return False
                
            current_time = chain.blocks.head.timestamp
            return start_period <= current_time <= end_period
            
        except Exception as e:
            logger.error(f"Error validating mint period: {e}", exc_info=True)
            return False
            
    def verify_network_state(self) -> bool:
        """
        Verify network evolution state and constraints
        """
        try:
            current_block = chain.blocks.head.number
            current_time = chain.blocks.head.timestamp
            
            logger.info(
                f"Network state verification:\n"
                f"Current block: {current_block}\n"
                f"Current time: {datetime.fromtimestamp(current_time)}\n"
                f"Active agents: {len(self.agent_manager.agents)}"
            )
            
            # Verify minimum block spacing between actions
            for agent_id, last_action in self.last_action_times.items():
                if current_block - last_action < self.min_blocks_between_actions:
                    logger.warning(f"Insufficient block spacing for agent {agent_id}")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Network state verification failed: {e}", exc_info=True)
            return False
