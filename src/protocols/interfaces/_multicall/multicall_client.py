from typing import Dict, Any, Optional
from ape_ethereum.multicall import Transaction
from src.framework.data import DataCollector
from src.framework.logging import get_logger

logger = get_logger(__name__)

class MultiCallClient:
    """Client for handling multicall transactions across multiple contracts"""
    
    def __init__(self, contracts: Dict[str, Any], collector: Optional['DataCollector'] = None):
        """
        Initialize with mapping of available contracts
        
        Args:
            contracts: Dict mapping contract_id to contract client instance
            collector: Optional data collector for recording events
        """
        self.contracts = contracts
        self.collector = collector


    def multiCall_execute(self, all_calls: Dict[str, Dict[str, Any]], context: Optional['SimulationContext'] = None) -> bool:
        """
        Execute multicall transaction across multiple contracts.
        """
        if not all_calls:
            logger.warning("No calls provided for multicall")
            return False

        # Extract transaction parameters
        tx_params = all_calls.pop("tx_params", {})
        sender = tx_params.get("sender")
        tx_value = tx_params.get("value", 0)

        if not sender:
            logger.error("No 'sender' specified in tx_params")
            return False

        # Create multicall transaction
        txn = Transaction()

        # Add deposit call first with full value
        processed_calls = 0
        for action_name, call_params in all_calls.items():
            try:
                # Split into contract_id and method 
                contract_id, method_name = action_name.split('_')[:2]

                # Get contract client
                contract_client = self.contracts.get(contract_id)
                if not contract_client:
                    logger.error(f"Contract {contract_id} not found")
                    continue
                    
                # Get contract method
                method = getattr(contract_client.contract, method_name, None)
                if not method or not callable(method):
                    logger.error(f"Method {method_name} not found in contract {contract_id}")
                    continue

                # Build argument list
                arglist = []
                for k, v in call_params.items():
                    if k not in ("sender", "value"):
                        arglist.append(v)

                logger.info(
                    f"Adding multicall: {action_name} with args={arglist}"
                )

                subcall_value = call_params.get("value", 0)
                # Add call without value parameter
                txn.add(method, *arglist, allowFailure=True)
                processed_calls += 1

            except Exception as e:
                logger.error(f"Error processing call {action_name}: {e}")
                continue

        if processed_calls == 0:
            logger.error("No valid calls to process")
            return False

        # Execute the multicall transaction with the total value
        try:
            receipt = txn(sender=sender, value=tx_value)
            
            # Process results
            results = receipt.return_value
            for i, result in enumerate(results):
                if result.success:
                    logger.info(f"Subcall #{i} succeeded")
                else:
                    logger.warning(f"Subcall #{i} failed: {result.returnData.hex()}")

            # Record transaction events
            if self.collector:
                self.collector.record_transaction_events(receipt)

            # Update simulation state if context provided
            if context and context.simulation:
                context.simulation.update_state_from_transaction(receipt, context)

            logger.info(
                f"Multicall completed with {processed_calls} subcalls, " 
                f"block={receipt.block_number}"
            )
            return True

        except Exception as e:
            logger.error(f"Multicall transaction failed: {e}")
            return False