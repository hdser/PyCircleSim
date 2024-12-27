import random
from datetime import datetime
import logging
from typing import Optional

from ape import chain
from src.framework.agents import BaseAgent
from src.protocols.rings import RingsClient

class MintActionHandler:
    """Encapsulates the logic to execute a MINT action."""

    def __init__(
        self,
        rings_client: RingsClient,
        chain,
        logger: logging.Logger,
        on_mint_performed=None
    ):
        self.rings_client = rings_client
        self.chain = chain
        self.logger = logger
        self.on_mint_performed = on_mint_performed

    def execute(self, agent: BaseAgent) -> bool:
        """Execute mint action with proper eligibility checks."""
        try:
            if not agent.accounts:
                self.logger.debug(f"Agent {agent.agent_id} has no accounts")
                return False

            # Gather mintable accounts
            mintable_accounts = []
            for address in agent.accounts.keys():
                if self.rings_client.is_human(address):
                    can_mint, _ = self.rings_client._check_mint_eligibility(address)
                    if can_mint:
                        mintable_accounts.append(address)
            
            if not mintable_accounts:
                self.logger.debug(f"Agent {agent.agent_id} has no mintable accounts")
                return False

            # Pick one randomly
            address = random.choice(mintable_accounts)
            prev_balance = self.rings_client.get_balance(address)

            # Execute mint
            issuance, _, _ = self.rings_client.calculate_issuance(address)
            success = self.rings_client.personal_mint(address)
            if not success:
                self.logger.debug(f"Mint failed for {address}")
                return False

            # Check the new balance
            new_balance = self.rings_client.get_balance(address)

            # Trigger callback
            if self.on_mint_performed:
                self.on_mint_performed(
                    address=address,
                    amount=issuance,
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp)
                )

            return True

        except Exception as e:
            self.logger.error(f"Mint action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False
