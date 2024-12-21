from datetime import datetime
import logging
from typing import Optional

from eth_pydantic_types import HexBytes
from ape import chain
from src.framework.agents import BaseAgent, AgentManager
from src.framework.data import CirclesDataCollector
from src.protocols.rings import RingsClient


class GroupCreationActionHandler:
    """Encapsulates logic to execute a CREATE_GROUP action."""

    def __init__(
        self,
        rings_client: RingsClient,
        chain,
        logger: logging.Logger,
        collector: Optional[CirclesDataCollector],
        agent_manager: AgentManager,
        on_group_created=None
    ):
        self.rings_client = rings_client
        self.chain = chain
        self.logger = logger
        self.collector = collector
        self.agent_manager = agent_manager
        self.on_group_created = on_group_created

    def execute(self, agent: BaseAgent) -> bool:
        """Execute group creation action."""
        try:
            group_number = getattr(agent, 'group_count', 0) + 1
            creator_address, _ = agent.create_account()

            # Create a name/symbol
            group_name = f"RingsGroup{creator_address[:4]}{group_number}"
            group_symbol = f"RG{creator_address[:2]}{group_number}"

            # Retrieve a default mint policy from config
            mint_policy = self.agent_manager.config.get(
                'mint_policy_address',
                "0x79Cbc9C7077dF161b92a745345A6Ade3fC626A60"
            )

            success = self.rings_client.register_group(
                creator_address,
                mint_policy,
                group_name,
                group_symbol,
                HexBytes(0)
            )

            if success:
                # Update agent's group count
                agent.group_count = group_number

                # Record in collector
                if self.collector:
                    self.collector.record_group_registration(
                        address=creator_address,
                        creator=agent.agent_id,
                        block_number=self.chain.blocks.head.number,
                        timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
                        name=group_name,
                        symbol=group_symbol,
                        mint_policy=mint_policy
                    )

                # Optional callback
                if self.on_group_created:
                    self.on_group_created(
                        creator=creator_address,
                        group_address=creator_address,
                        name=group_name,
                        block=self.chain.blocks.head.number,
                        timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp)
                    )

            return success

        except Exception as e:
            self.logger.error(f"Group creation failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False
