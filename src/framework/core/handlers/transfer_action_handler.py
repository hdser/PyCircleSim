import random
from datetime import datetime
import logging
from typing import Optional

from ape import chain
from src.framework.agents import BaseAgent
from src.framework.data import CirclesDataCollector
from src.protocols.rings import RingsClient

class TransferActionHandler:
    """Encapsulates the logic to execute a TRANSFER action."""

    def __init__(
        self,
        rings_client: RingsClient,
        chain,
        logger: logging.Logger,
        collector: Optional[CirclesDataCollector],
        on_transfer_performed=None
    ):
        self.rings_client = rings_client
        self.chain = chain
        self.logger = logger
        self.collector = collector
        self.on_transfer_performed = on_transfer_performed

    def execute(self, agent: BaseAgent) -> bool:
        """Execute transfer action."""
        try:
            if not agent.accounts or not agent.trusted_addresses:
                return False

            sender = random.choice(list(agent.accounts.keys()))
            receiver = random.choice(list(agent.trusted_addresses))

            balance = self.rings_client.get_balance(sender)
            if balance == 0:
                return False

            amount = int(balance * random.uniform(0.1, 0.3))
            if amount == 0:
                return False

            success = self.rings_client.transfer(
                sender,
                receiver,
                amount,
                b""
            )

            if success:
                current_time = datetime.fromtimestamp(self.chain.blocks.head.timestamp)

                # Record in collector
                if self.collector:
                    # Sender
                    self.collector.record_balance_change(
                        account=sender,
                        token_id=str(int(sender, 16)),
                        block_number=self.chain.blocks.head.number,
                        timestamp=current_time,
                        previous_balance=balance,
                        new_balance=balance - amount,
                        tx_hash="0x0",
                        event_type="TRANSFER_SEND"
                    )

                    # Receiver
                    receiver_prev_balance = self.rings_client.get_balance(receiver)
                    self.collector.record_balance_change(
                        account=receiver,
                        token_id=str(int(receiver, 16)),  # or referencing the same token?
                        block_number=self.chain.blocks.head.number,
                        timestamp=current_time,
                        previous_balance=receiver_prev_balance,
                        new_balance=receiver_prev_balance + amount,
                        tx_hash="0x0",
                        event_type="TRANSFER_RECEIVE"
                    )

                # Optional callback
                if self.on_transfer_performed:
                    self.on_transfer_performed(
                        sender=sender,
                        receiver=receiver,
                        amount=amount,
                        block=self.chain.blocks.head.number,
                        timestamp=current_time
                    )

            return success

        except Exception as e:
            self.logger.error(f"Transfer action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False
