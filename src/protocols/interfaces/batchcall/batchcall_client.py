# src/protocols/interfaces/batchcall/batchcall_client.py

from typing import Dict, Any, Optional, List
from src.protocols.handler_strategies.batchcall.basic_strategies import (
    DepositOnlyStrategy,
    DepositAndSwapStrategy,
    available_calls
)
from src.framework.logging import get_logger

logger = get_logger(__name__)

class BatchCallClient:
    """Client for handling batch calls"""

    def __init__(self, clients: Dict[str, Any], collector=None):
        self.clients = clients
        self.collector = collector
        self.available_calls = available_calls

    
    def execute_batch(self, params: Dict[str, Any],context: Optional['SimulationContext'] = None) -> bool:
        """Execute a batch of calls"""
        try:
            if not params:
                logger.error("No parameters provided for batch execution")
                return False

            logger.debug(f"Executing batch call with parameters: {params}")

            # Extract tx params and batch calls
            batch_calls = params.get('batch_calls', [])
            if not batch_calls:
                logger.error("No batch calls specified")
                return False

            # Execute each call in sequence
            for call in batch_calls:
                client_name = call.get('client_name')
                method = call.get('method')
                call_params = call.get('params', {})

                if not all([client_name, method]):
                    logger.error(f"Invalid call specification: {call}")
                    continue

                client = self.clients.get(client_name)
                if not client:
                    logger.error(f"Client not found: {client_name}")
                    continue

                method_func = getattr(client, method, None)
                if not method_func:
                    logger.error(f"Method not found: {method}")
                    continue

                # Add tx params if not present in call params
                if isinstance(call_params, dict):
                    if 'sender' not in call_params:
                        call_params['sender'] = params.get('sender')
                    if 'value' not in call_params:
                        call_params['value'] = params.get('value', 0)

                # Execute call
                try:
                    logger.debug(f"Executing {client_name}.{method} with params: {call_params}")
                    call_params['context'] = context
                    success = method_func(**call_params)
                    
                    if not success:
                        logger.error(f"Call failed: {client_name}.{method}")
                        return False
                except Exception as e:
                    logger.error(f"Error executing call {client_name}.{method}: {e}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            return False