from typing import List
from datetime import datetime
from ape import Contract
from ethpm_types.abi import EventABI
from .event_logger import ContractEvent, EventLogger
from src.framework.logging import get_logger
import json
from pathlib import Path

logger = get_logger(__name__)

class ContractEventHandler:
    """Handles contract event processing and logging"""
    
    def __init__(self, event_logger: EventLogger, simulation_run_id: int):
        self.logger = event_logger
        self.simulation_run_id = simulation_run_id
        self._event_processors = {}
        self.abis = self._load_all_abis()

    def _load_all_abis(self) -> List[EventABI]:
        """Load all ABI files from the ABI directory"""
        try:
            # Use resolve() to simplify the path resolution
            project_root = Path(__file__).resolve().parents[4]
            abis_dir = project_root / "src" / "protocols" / "abis"
            
            all_abis = []
            excluded_dirs = {'__pycache__'}
            
            # Walk through all subdirectories except excluded ones
            for subdir in abis_dir.iterdir():
                if not subdir.is_dir() or subdir.name in excluded_dirs:
                    continue
                    
                # Load each .json file in the directory
                for file_path in subdir.glob('*.json'):
                    try:
                        with open(file_path) as f:
                            abi_content = json.load(f)
                            event_abis = [
                                EventABI(
                                    name=item['name'],
                                    inputs=item.get('inputs', []),
                                    anonymous=item.get('anonymous', False)
                                )
                                for item in abi_content 
                                if item.get('type') == 'event'
                            ]
                            all_abis.extend(event_abis)
                    except Exception as e:
                        logger.warning(f"Failed to load ABI from {file_path}: {e}")
                        continue
                        
            logger.info(f"Loaded {len(all_abis)} event ABIs from {abis_dir}")
            return all_abis
            
        except Exception as e:
            logger.error(f"Failed to load ABIs: {e}")
            return []


    def handle_transaction_events(self, tx) -> None:
        """Process and log all events from a transaction"""
        if not tx:
            return
            
        try:
            decoded_logs = tx.decode_logs(abi=self.abis)

            for i, decoded_log in enumerate(decoded_logs):
                log = tx.logs[i]

                # Convert HexBytes and complex types to strings
                topics = [str(topic) for topic in log.get('topics', [])]
                event_data = str(decoded_log.event_arguments)
                raw_data = str(log.get('data', ''))

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
                    topics=topics,
                    event_data=event_data,
                    raw_data=raw_data,
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