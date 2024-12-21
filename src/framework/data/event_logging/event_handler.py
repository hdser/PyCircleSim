from typing import Optional, Dict, Any
import logging
from datetime import datetime
from eth_utils import encode_hex
from ape import Contract, chain
from .event_logger import ContractEvent, EventLogger

logger = logging.getLogger(__name__)

class ContractEventHandler:
    """Handles contract event processing and logging"""
    
    def __init__(self, event_logger: EventLogger, simulation_run_id: int):
        self.logger = event_logger
        self.simulation_run_id = simulation_run_id
        self._event_processors = {}

    def handle_contract_event(self, event: Dict, contract: Contract) -> None:
        """Process and log a contract event"""
        try:
            # Extract basic event info
            block = chain.blocks.head
            
            # Create ContractEvent instance
            contract_event = ContractEvent(
                simulation_run_id=self.simulation_run_id,
                event_name=event.event_name,
                block_number=block.number,
                block_timestamp=datetime.fromtimestamp(block.timestamp),
                transaction_hash=encode_hex(event.transaction_hash),
                tx_from=event.transaction.sender,
                tx_to=event.transaction.receiver,
                tx_index=event.transaction_index,
                log_index=event.log_index,
                contract_address=contract.address,
                topics=[encode_hex(t) for t in event.topics],
                event_data=event.data,
                raw_data=encode_hex(event.raw_data),
                indexed_values=event.indexed_arguments,
                decoded_values=event.decoded_arguments
            )
            
            # Log the event
            self.logger.record_event(contract_event)
            
            # Process event with custom handler if registered
            if event.event_name in self._event_processors:
                self._event_processors[event.event_name](contract_event)
            
        except Exception as e:
            logger.error(f"Failed to handle contract event: {e}")

    def setup_event_listeners(self, contract: Contract) -> None:
        """Set up listeners for all contract events"""
        for event in contract.events:
            contract.events[event.name].subscribe(
                lambda evt: self.handle_contract_event(evt, contract)
            )
            
    def register_event_processor(self, event_name: str, processor_func):
        """Register a custom processor function for specific events"""
        self._event_processors[event_name] = processor_func