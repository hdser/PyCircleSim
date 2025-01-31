# src/protocols/interfaces/batchcall/batchcall_client.py

from typing import Dict, Any, Optional, List
from src.protocols.handler_strategies.batchcall.basic_strategies import (
    DepositOnlyStrategy,
    SetupLBPStrategy,
    available_calls
)
from src.framework.logging import get_logger

logger = get_logger(__name__)

class BatchCallClient:
    """Client for executing batch calls"""

    def __init__(self, clients: Dict[str, Any], collector: Optional['DataCollector'] = None):
        """Initialize with available clients"""
        self.clients = clients
        self.collector = collector

    def execute_batch(self, batch_calls: List[Dict[str, Any]], context: 'SimulationContext') -> bool:
        """Execute a batch of calls"""
        try:
            if not isinstance(batch_calls, list):
                logger.error(f"Expected list of batch calls, got {type(batch_calls)}")
                return False

            for call in batch_calls:
                # Validate call structure
                if not all(k in call for k in ['client_name', 'method', 'params']):
                    logger.error(f"Invalid batch call structure: {call}")
                    continue

                client_name = call['client_name']
                method_name = call['method']
                params = call['params']

                # Get client
                client = self.clients.get(client_name)
                if not client:
                    logger.error(f"Client not found: {client_name}")
                    continue

                # Get method
                method = getattr(client, method_name, None)
                if not method:
                    logger.error(f"Method {method_name} not found in client {client_name}")
                    continue

                # Execute call
                try:
                    # Add context to params if supported by method
                    if 'context' in method.__code__.co_varnames:
                        params['context'] = context

                    success = method(**params)
                    if not success:
                        logger.error(f"Failed batch call {client_name}.{method_name}")
                        return False

                except Exception as e:
                    logger.error(f"Error executing {client_name}.{method_name}: {e}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            return False