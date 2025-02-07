from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from ape import Contract, chain
from src.framework.data import DataCollector
from src.framework.logging import get_logger
from src.protocols.implementations import IMPLEMENTATIONS
#from src.protocols.implementations.base import Implementation
import logging

logger = get_logger(__name__,logging.INFO)

class MasterClient:
    """
    Single entry point for all contract interactions.
    Replaces individual contract clients with a unified interface.
    """
    
    def __init__(
        self,
        clients: Dict[str, Any],
        abi_path: Optional[str] = None,
        gas_limits: Optional[Dict] = None,
        data_collector: Optional['DataCollector'] = None
    ):
        self.clients = clients
        self.collector = data_collector
        self.gas_limits = gas_limits or {}
        
        # Cache for implementations
        self._impl_cache: Dict = {}
        self.contract_states = {}

        # Load all implementations
        from src.protocols.implementations.registry import IMPLEMENTATIONS
        self._impl_cache = IMPLEMENTATIONS
        logger.info(f"Loaded implementations: {list(self._impl_cache.keys())}")

    @property
    def available_implementations(self) -> List[str]:
        """Get list of available implementation names"""
        return list(self._impl_cache.keys())

    def validate_implementation(self, name: str) -> bool:
        """Check if implementation exists"""
        return name in self._impl_cache

    def _get_implementation(self, name: str) -> Dict:
        """Get implementation instance"""
        if name not in self._impl_cache:
            raise ValueError(f"Unknown implementation: {name}")
        return self._impl_cache[name]
    
    def execute(self, implementation_name: str, context: 'SimulationContext', **kwargs) -> Tuple[bool, Optional[str]]:
        """Execute an implementation."""
        try:
            logger.info(f"Executing implementation {implementation_name}")
            
            # Get implementation
            implementation = self._get_implementation(implementation_name)
            if not implementation:
                return False, "Implementation not found"

            # Get calls from implementation
            calls = implementation.get_calls(context)
            if not calls:
                return False, "No calls generated"

            logger.info(f"Executing {len(calls)} calls")
            
            # Track all transactions for state updates
            all_receipts = []
            
            # Execute all calls
            success=True
            for call in calls:
                client = context.get_client(call.client_name)
                if not client:
                    continue

                # Execute method
                try:
                    if hasattr(client, call.method):
                        method = getattr(client, call.method)
                        result = method(**call.params, context=context)
                        
                        # If result is a transaction receipt, store it
                        if hasattr(result, 'status') and hasattr(result, 'decode_logs'):
                            all_receipts.append(result)
                            # Update state immediately after each successful call
                            if context and context.simulation:
                                context.simulation.update_state_from_transaction(result, context)
                        elif not result:
                            success=False
                                
                except Exception as e:
                    logger.error(f"Call failed: {e}")
                    success=False
                    continue

            logger.info(f"Implementation completed with success={success}")
            return success, None

        except Exception as e:
            error_msg = f"Error executing {implementation_name}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
            
    def estimate_gas(
        self, 
        implementation_name: str,
        context: 'SimulationContext',
        **kwargs
    ) -> int:
        """
        Estimate gas for an implementation execution.
        
        Args:
            implementation_name: Name of implementation to estimate
            context: Current simulation context
            **kwargs: Parameters for the implementation
            
        Returns:
            Estimated gas cost
        """
        implementation = self._get_implementation(implementation_name)
        calls = implementation.get_calls(context, **kwargs)
        
        total_gas = 0
        for call in calls:
            client = self.clients[call['client_name']]
            method = getattr(client, call['method'])
            
            # Add gas estimation logic here
            # This will depend on your specific needs
            gas_limit = self.gas_limits.get(
                f"{call['client_name']}_{call['method']}", 
                300000
            )
            total_gas += gas_limit
            
        return total_gas
    
    def update_contract_state(self, contract_id: str, state_data: Dict[str, Any]):
        """Update contract state data for tracking."""
        logger.info(f"Updating state for contract {contract_id}: {list(state_data.keys())}")
        # You can implement storage logic here if needed, for example:
        self.contract_states[contract_id] = state_data