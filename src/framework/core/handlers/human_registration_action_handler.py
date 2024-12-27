import random
from datetime import datetime
import logging
from typing import Optional

from eth_pydantic_types import HexBytes
from ape import chain
from src.framework.agents import BaseAgent, AgentManager
from src.protocols.rings import RingsClient

class HumanRegistrationActionHandler:
    """Encapsulates logic to execute a REGISTER_HUMAN action."""

    def __init__(
        self,
        rings_client: RingsClient,
        chain,
        logger: logging.Logger,
        agent_manager: AgentManager
    ):
        self.rings_client = rings_client
        self.chain = chain
        self.logger = logger
        self.agent_manager = agent_manager

    def execute(self, agent: BaseAgent) -> bool:
        """Execute human registration action."""
        try:
            # If the agent needs more accounts, create one
            if len(agent.accounts) < agent.profile.target_account_count:
                agent.create_account()

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

            return success

        except Exception as e:
            self.logger.error(f"Human registration failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False
