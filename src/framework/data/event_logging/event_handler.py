from typing import List, Optional, Dict, Any
from datetime import datetime
from ape import Contract
from .event_logger import ContractEvent, EventLogger
from src.framework.logging import get_logger
import json
from pathlib import Path

logger = get_logger(__name__)

class ContractEventHandler:
    """Handles contract event processing and logging"""
    
    def __init__(
        self, 
        event_logger: EventLogger, 
        simulation_run_id: int,
        abis: Optional[List[Dict[str, Any]]] = None
    ):
        self.logger = event_logger
        self.simulation_run_id = simulation_run_id
        self.abis = abis or []
        self._event_processors = {}


    
    def handle_transaction_events(self, tx) -> None:
        """Process and log all events from a transaction"""
        if not tx:
            return
            
        try:
            print(len(tx.logs))
            print(len(self.abis))
            decoded_logs = tx.decode_logs(abi=self.abis)
            for i, decoded_log in enumerate(decoded_logs):
                log = tx.logs[i]

                topic0 = log.get('topics', [])[0]
                topic0_string = '0x' + topic0.hex().upper()
                event_data = decoded_log.event_arguments
               
                event = ContractEvent(
                    simulation_run_id=self.simulation_run_id,
                    event_name=decoded_log.event_name,
                    block_number=tx.block_number,
                    block_timestamp=datetime.fromtimestamp(tx.timestamp),
                    transaction_hash=str(tx.txn_hash),
                    tx_from=str(tx.sender),
                    tx_to=str(tx.receiver),
                    tx_index=log.get('transactionIndex'),
                    log_index=log.get('logIndex'),
                    contract_address=str(decoded_log.contract_address),
                    topic0=topic0_string,
                    event_data=event_data,
                )
               
                self.logger.record_event(event)
                 
        except Exception as e:
            logger.error(f"Failed to handle transaction events: {e}")

        
    def setup_event_listeners(self, contract: Contract) -> None:
        """Set up listeners for all contract events"""
        for event in contract.events:
            contract.events[event.name].subscribe(
                lambda evt: self.handle_contract_event(evt, contract)
            )
            
    def register_event_processor(self, event_name: str, processor_func):
        """Register a custom processor function for specific events"""
        self._event_processors[event_name] = processor_func