from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from ape import chain, networks
from ape.types.events import LogFilter
from datetime import datetime
from src.framework.logging import get_logger
from src.framework.data.event_logging import ContractEvent
from eth_pydantic_types import HexBytes
import logging

logger = get_logger(__name__, logging.INFO)

@dataclass
class EventConfig:
    """Configuration for event indexing"""
    name: str
    topics: Optional[List[str]] = None

class EventIndexer:
    """Indexes historical events from contracts"""
    
    def __init__(self, config: Dict[str, Any], abis: List[Dict[str, Any]]):
        """Initialize with configuration"""
        self.config = config
        self.abis = abis
        self._indexed_events: Dict[str, List[Dict]] = {}

    def _convert_to_hex(self, value: Any) -> str:
        """Safely convert a value to hex string"""
        if isinstance(value, (bytes, HexBytes)):
            return value.hex()
        if isinstance(value, str) and value.startswith('0x'):
            return value
        if isinstance(value, str):
            return f"0x{value}"
        return str(value)

    def index_contract_events(self, contract_id: str, client: Any, address: str) -> Dict[str, List[Dict]]:
        """Index events for a specific contract"""
        try:
            if contract_id not in self.config:
                logger.debug(f"No event config for contract {contract_id}")
                return {}

            event_configs = self._get_event_configs(self.config[contract_id])
            indexed_events = {}
            
            # Get current block number
            current_block = chain.blocks.head.number
            
            # Get provider
            provider = networks.provider
            
            for event in event_configs:
                logger.info(f"Indexing historical {event.name} events for {contract_id}")
                
                try:
                    # Get matching event ABI
                    event_abi = next((abi for abi in self.abis if abi.name == event.name), None)
                    if not event_abi:
                        logger.warning(f"No ABI found for event {event.name}")
                        continue

                    # Create proper LogFilter
                    log_filter = LogFilter(
                        addresses=[address],
                        events=[event_abi],
                        start_block=36873405,
                        stop_block=current_block
                    )
                    
                    indexed_events[event.name] = []
                    
                    # Get logs using provider
                    logs = provider.get_contract_logs(log_filter)
                    
                    # Process logs
                    for log in logs:
                        try:
                            # Get transaction from chain
                            block = chain.blocks[log.block_number]
                            tx = block.transactions[log.transaction_index]

                            # Create ContractEvent
                            contract_event = ContractEvent(
                                simulation_run_id=0,  # Not relevant for historical
                                event_name=event.name,
                                block_number=log.block_number,
                                block_timestamp=datetime.fromtimestamp(block.timestamp),
                                transaction_hash=self._convert_to_hex(log.transaction_hash),
                                tx_from=str(tx.sender),
                                tx_to=str(tx.receiver),
                                tx_index=log.transaction_index,
                                log_index=log.log_index,
                                contract_address=str(address),
                                topic0=None,  # Skip topic0 as we don't have access to it
                                event_data=log.event_arguments
                            )
                            
                            indexed_events[event.name].append(contract_event)
                            
                        except Exception as e:
                            logger.error(f"Failed to process log: {e}", exc_info=True)
                            continue
                        
                    logger.info(f"Indexed {len(indexed_events[event.name])} {event.name} events from block 0 to {current_block}")

                except Exception as e:
                    logger.error(f"Failed to index {event.name} events: {e}", exc_info=True)
                    continue

            return indexed_events

        except Exception as e:
            logger.error(f"Failed to index events for {contract_id}: {e}", exc_info=True)
            return {}

    def _get_event_configs(self, contract_config: Dict) -> List[EventConfig]:
        """Get event configs from contract config"""
        events = contract_config.get('events', [])
        return [
            EventConfig(name=event) if isinstance(event, str)
            else EventConfig(**event)
            for event in events
        ]