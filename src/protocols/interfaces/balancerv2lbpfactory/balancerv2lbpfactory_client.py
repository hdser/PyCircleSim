from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime 
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from ape import Contract, chain
from src.framework.data import DataCollector
from src.framework.logging import get_logger

logger = get_logger(__name__)

class BalancerV2LBPFactoryClient:
    """Client interface for BalancerV2LBPFactory contract"""
    
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
            
            'create': 300000,
            
            'disable': 300000,
            
            'getActionId': 300000,
            
            'getCreationCode': 300000,
            
            'getCreationCodeContracts': 300000,
            
            'getPauseConfiguration': 300000,
            
            'getVault': 300000,
            
            'isDisabled': 300000,
            
            'isPoolFromFactory': 300000,
            
        }
        
    
    
    def create(self, sender: str, value: int, name: str, symbol: str, tokens: List[str], weights: List[int], swapFeePercentage: int, owner: str, swapEnabledOnStart: bool, context: Optional['SimulationContext'] = None) -> bool:
        """create implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
            name: string - Contract parameter
            
            symbol: string - Contract parameter
            
            tokens: address[] - Contract parameter
            
            weights: uint256[] - Contract parameter
            
            swapFeePercentage: uint256 - Contract parameter
            
            owner: address - Contract parameter
            
            swapEnabledOnStart: bool - Contract parameter
            
        """
        try:
            tx = self.contract.create(
                name, symbol, tokens, weights, swapFeePercentage, owner, swapEnabledOnStart, 
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
            logger.error(f"create failed: {e}")
            return False
    
    
    
    def disable(self, sender: str, value: int, context: Optional['SimulationContext'] = None) -> bool:
        """disable implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
        """
        try:
            tx = self.contract.disable(
                
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
            logger.error(f"disable failed: {e}")
            return False
    
    
    
    def getActionId(self, selector: Any) -> bytes:
        """getActionId implementation
        
        Args:
            selector: bytes4 - Contract parameter
        
        """
        try:
            return self.contract.getActionId(selector)
        except Exception as e:
            logger.error(f"getActionId failed: {e}")
            return None
    
    
    
    def getCreationCode(self, ) -> bytes:
        """getCreationCode implementation
        
        """
        try:
            return self.contract.getCreationCode()
        except Exception as e:
            logger.error(f"getCreationCode failed: {e}")
            return None
    
    
    
    def getCreationCodeContracts(self, ) -> Tuple[str, str]:
        """getCreationCodeContracts implementation
        
        """
        try:
            return self.contract.getCreationCodeContracts()
        except Exception as e:
            logger.error(f"getCreationCodeContracts failed: {e}")
            return None
    
    
    
    def getPauseConfiguration(self, ) -> Tuple[int, int]:
        """getPauseConfiguration implementation
        
        """
        try:
            return self.contract.getPauseConfiguration()
        except Exception as e:
            logger.error(f"getPauseConfiguration failed: {e}")
            return None
    
    
    
    def getVault(self, ) -> str:
        """getVault implementation
        
        """
        try:
            return self.contract.getVault()
        except Exception as e:
            logger.error(f"getVault failed: {e}")
            return None
    
    
    
    def isDisabled(self, ) -> bool:
        """isDisabled implementation
        
        """
        try:
            return self.contract.isDisabled()
        except Exception as e:
            logger.error(f"isDisabled failed: {e}")
            return None
    
    
    
    def isPoolFromFactory(self, pool: str) -> bool:
        """isPoolFromFactory implementation
        
        Args:
            pool: address - Contract parameter
        
        """
        try:
            return self.contract.isPoolFromFactory(pool)
        except Exception as e:
            logger.error(f"isPoolFromFactory failed: {e}")
            return None
    
    