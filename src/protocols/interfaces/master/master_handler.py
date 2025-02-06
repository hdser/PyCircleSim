from typing import Dict, Any, Optional
import importlib
from src.framework.core.context import SimulationContext
from .master_client import MasterClient
from src.framework.logging import get_logger

logger = get_logger(__name__)

class MasterHandler:
    def __init__(
        self,
        client: MasterClient,
        chain,
        logger
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        
    def execute(
        self, 
        context: SimulationContext, 
        params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Execute an implementation directly."""
        try:
            if not params:
                return False
                
            implementation = params.pop('implementation', None)
            if not implementation:
                return False
                
            self.logger.info(f"Executing implementation {implementation}")
            context.current_action = implementation 
            success, error = self.client.execute(
                implementation,
                context,
                **params
            )
            
            if error:
                self.logger.error(f"Implementation failed: {error}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Execution failed: {e}")
            return False