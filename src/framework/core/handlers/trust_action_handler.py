import random
from datetime import datetime, timedelta
import logging
from typing import Optional

from ape import chain
from src.framework.agents import BaseAgent, AgentManager
#from src.framework.data import CirclesDataCollector
from src.protocols.rings import RingsClient

class TrustActionHandler:
    """Encapsulates the logic to execute a TRUST action."""

    def __init__(
        self,
        rings_client: RingsClient,
        chain,
        logger: logging.Logger,
    #    collector: Optional[CirclesDataCollector],
        agent_manager: AgentManager
    ):
        self.rings_client = rings_client
        self.chain = chain
        self.logger = logger
    #    self.collector = collector
        self.agent_manager = agent_manager

    def execute(self, agent: BaseAgent) -> bool:
        """Execute trust action."""
        try:
            if not agent.accounts:
                return False

            all_registered = set()
            # We iterate over known addresses and see if they're humans or orgs
            for addr in self.agent_manager.address_to_agent.keys():
                if self.rings_client.is_human(addr) or self.rings_client.is_organization(addr):
                    all_registered.add(addr)

            already_trusted = agent.trusted_addresses or set()
            potential_trustees = list(
                all_registered
                - already_trusted
                - set(agent.accounts.keys())
            )

            if not potential_trustees:
                return False

            truster = random.choice(list(agent.accounts.keys()))
            trustee = random.choice(potential_trustees)
            expiry = int((datetime.now() + timedelta(days=365)).timestamp())

            success = self.rings_client.trust(truster, trustee, expiry)
            #if success:
            #    agent.trusted_addresses.add(trustee)
            #    if self.collector:
            #        self.collector.record_trust_relationship(
            #            truster=truster,
            #            trustee=trustee,
            #            block_number=self.chain.blocks.head.number,
            #            timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
            #            expiry_time=datetime.fromtimestamp(expiry)
            #        )
            return success

        except Exception as e:
            self.logger.error(f"Trust action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False
