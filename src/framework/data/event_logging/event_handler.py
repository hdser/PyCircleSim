from typing import List, Optional, Dict, Any
from datetime import datetime
from ape import Contract
from .event_logger import ContractEvent, EventLogger
from src.framework.logging import get_logger
import json
from pathlib import Path
from eth_utils import encode_hex, to_hex
from eth_abi.exceptions import DecodingError

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

    def _process_event_arg(self, arg: Any) -> Any:
        """Process event argument into a serializable format"""
        if arg is None:
            return None
            
        if isinstance(arg, (int, str, bool, float)):
            return arg
            
        if isinstance(arg, bytes):
            return encode_hex(arg)
            
        if isinstance(arg, (list, tuple)):
            return [self._process_event_arg(item) for item in arg]
            
        if isinstance(arg, dict):
            return {
                str(k): self._process_event_arg(v) 
                for k, v in arg.items()
            }
            
        # Convert anything else to string representation
        try:
            return str(arg)
        except Exception:
            return f"<unparseable-{type(arg).__name__}>"

    def _process_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process all event data arguments"""
        try:
            if not event_data:
                return {}
                
            processed_data = {}
            for key, value in event_data.items():
                try:
                    processed_data[str(key)] = self._process_event_arg(value)
                except Exception as e:
                    logger.warning(f"Failed to process event arg {key}: {e}")
                    processed_data[str(key)] = None
                    
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process event data: {e}")
            return {}
    
    def handle_transaction_events(self, tx, context: Optional['SimulationContext'] = None) -> None:
        """Process and log all events from a transaction"""
        if not tx:
            return
            
        try:
            decoded_logs = tx.decode_logs(abi=self.abis)
            for i, decoded_log in enumerate(decoded_logs):
                try:
                    log = tx.logs[i]
                    topic0 = log.get('topics', [])[0] if log.get('topics') else None
                    topic0_string = '0x' + topic0.hex().upper() if topic0 else None
                    
                    # Process event arguments
                    raw_event_data = decoded_log.event_arguments
                    processed_event_data = self._process_event_data(raw_event_data)
                    
                    # Create event record
                    event = ContractEvent(
                        simulation_run_id=self.simulation_run_id,
                        action_name=context.current_action if context else None,
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
                        event_data=processed_event_data
                    )
                    
                    # Record the event
                    self.logger.record_event(event)
                    
                    # Apply any custom processors
                    if decoded_log.event_name in self._event_processors:
                        self._event_processors[decoded_log.event_name](event)
                        
                except Exception as e:
                    logger.error(f"Failed to process log {i}: {e}")
                    continue
                 
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