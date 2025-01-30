from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime 
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from ape import Contract, chain
from src.framework.data import DataCollector
from src.framework.logging import get_logger

logger = get_logger(__name__)

class CirclesERC20LiftClient:
    """Client interface for CirclesERC20Lift contract"""
    
    def __init__(
        self,
        contract_address: str,
        abi_path: str,
        gas_limits: Optional[Dict] = None,
        data_collector: Optional['DataCollector'] = None
    ):
        self.contract = Contract(contract_address, abi=abi_path)
        self.collector = data_collector
        
        # Default gas limits
        self.gas_limits = gas_limits or {
            
            'ERC20_WRAPPER_SETUP_CALLPREFIX': 300000,
            
            'ensureERC20': 300000,
            
            'erc20Circles': 300000,
            
            'hub': 300000,
            
            'masterCopyERC20Wrapper': 300000,
            
            'nameRegistry': 300000,
            
        }
        
    
    
    def ERC20_WRAPPER_SETUP_CALLPREFIX(self, ) -> Any:
        """ERC20_WRAPPER_SETUP_CALLPREFIX implementation
        
        """
        try:
            return self.contract.ERC20_WRAPPER_SETUP_CALLPREFIX()
        except Exception as e:
            logger.error(f"ERC20_WRAPPER_SETUP_CALLPREFIX failed: {e}")
            return None
    
    
    
    def ensureERC20(self, sender: str, value: int, _avatar: str, _circlesType: Any, context: Optional['SimulationContext'] = None) -> bool:
        """ensureERC20 implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
            _avatar: address - Contract parameter
            
            _circlesType: uint8 - Contract parameter
            
        """
        try:
            tx = self.contract.ensureERC20(
                _avatar, _circlesType, 
                sender=sender,
                value=value
            )
            success = bool(tx and tx.status == 1)
            if success:
                # Record events if collector exists
                if self.collector:
                    self.collector.record_transaction_events(tx)
                
                # Get simulation from context if it exists
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success
        except Exception as e:
            logger.error(f"ensureERC20 failed: {e}")
            return False
    
    
    
    def erc20Circles(self, param0: Any, param1: str) -> str:
        """erc20Circles implementation
        
        Args:
            : uint8 - Contract parameter
        
        Args:
            : address - Contract parameter
        
        """
        try:
            return self.contract.erc20Circles(param0, param1)
        except Exception as e:
            logger.error(f"erc20Circles failed: {e}")
            return None
    
    
    
    def hub(self, ) -> str:
        """hub implementation
        
        """
        try:
            return self.contract.hub()
        except Exception as e:
            logger.error(f"hub failed: {e}")
            return None
    
    
    
    def masterCopyERC20Wrapper(self, param0: int) -> str:
        """masterCopyERC20Wrapper implementation
        
        Args:
            : uint256 - Contract parameter
        
        """
        try:
            return self.contract.masterCopyERC20Wrapper(param0)
        except Exception as e:
            logger.error(f"masterCopyERC20Wrapper failed: {e}")
            return None
    
    
    
    def nameRegistry(self, ) -> str:
        """nameRegistry implementation
        
        """
        try:
            return self.contract.nameRegistry()
        except Exception as e:
            logger.error(f"nameRegistry failed: {e}")
            return None
    
    