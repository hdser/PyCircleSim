import random
from datetime import datetime
import logging
from typing import Optional

from eth_pydantic_types import HexBytes
from ape import chain
from src.framework.agents import BaseAgent, AgentManager
from src.framework.data import CirclesDataCollector
from src.protocols.rings import RingsClient

class HumanRegistrationActionHandler:
    """Encapsulates logic to execute a REGISTER_HUMAN action."""

    def __init__(
        self,
        rings_client: RingsClient,
        chain,
        logger: logging.Logger,
        collector: Optional[CirclesDataCollector],
        agent_manager: AgentManager
    ):
        self.rings_client = rings_client
        self.chain = chain
        self.logger = logger
        self.collector = collector
        self.agent_manager = agent_manager

    def execute(self, agent: BaseAgent) -> bool:
        """Execute human registration action."""
        try:
            # If the agent needs more accounts, create one
            if len(agent.accounts) < agent.profile.target_account_count:
                new_address, _ = agent.create_account()
                if self.collector and self.collector.current_run_id:
                    self.collector.record_agent_address(
                        agent.agent_id,
                        new_address,
                        is_primary=False
                    )

            # Find any unregistered addresses
            unregistered = [
                addr for addr in agent.accounts.keys()
                if not self.rings_client.is_human(addr)
            ]

            if not unregistered:
                return False

            address = random.choice(unregistered)

            # Default to no inviter for direct registration
            inviter = "0x0000000000000000000000000000000000000000"
            metadata = HexBytes(0)

            success = self.rings_client.register_human(
                address,
                inviter,
                metadata
            )

            if success and self.collector:
                self.collector.record_human_registration(
                    address=address,
                    block_number=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
                    inviter_address=inviter,
                    welcome_bonus=200.0
                )
                self.logger.info(f"Successfully registered human account {address}")

            return success

        except Exception as e:
            self.logger.error(f"Human registration failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False
