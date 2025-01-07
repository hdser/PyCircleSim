
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime 
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from ape import Contract, chain
from src.framework.data import DataCollector
from src.framework.logging import get_logger

logger = get_logger(__name__)

class WXDAIClient:
    """Client interface for WXDAI contract"""
    
    def __init__(
        self,
        contract_address: str,
        abi_path: str,
        gas_limits: Optional[Dict] = None,
        cache_config: Optional[Dict] = None,
        data_collector: Optional['DataCollector'] = None
    ):
        self.contract = Contract(contract_address, abi=abi_path)
        self.collector = data_collector
        
        # Default gas limits
        self.gas_limits = gas_limits or {
            
            'name': 300000,
            
            'approve': 300000,
            
            'totalSupply': 300000,
            
            'transferFrom': 300000,
            
            'withdraw': 300000,
            
            'decimals': 300000,
            
            'balanceOf': 300000,
            
            'symbol': 300000,
            
            'transfer': 300000,
            
            'deposit': 300000,
            
            'allowance': 300000,
            
        }
        
        # Optional caching
        self.cache_enabled = cache_config.get('enabled', True) if cache_config else True
        self.cache_ttl = cache_config.get('ttl', 100) if cache_config else 100
        self.cache = {
            'last_update': datetime.min,
            'current_block': 0
        }

        
    
    
    def name(self, ) -> str:
        """name implementation"""
        try:
            return self.contract.name(
                
            )
        except Exception as e:
            logger.error(f"name failed: {e}")
            return None
    
    
    
    def approve(self, sender: str, guy: str, wad: int) -> bool:
        """approve implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.approve(
                
                guy,
                
                wad,
                
                sender=sender
            )
                
            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)
                
            return success
                
        except Exception as e:
            logger.error(f"approve failed: {e}")
            return False
    
    
    
    def totalSupply(self, ) -> int:
        """totalSupply implementation"""
        try:
            return self.contract.totalSupply(
                
            )
        except Exception as e:
            logger.error(f"totalSupply failed: {e}")
            return None
    
    
    
    def transferFrom(self, sender: str, src: str, dst: str, wad: int) -> bool:
        """transferFrom implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.transferFrom(
                
                src,
                
                dst,
                
                wad,
                
                sender=sender
            )
                
            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)
                
            return success
                
        except Exception as e:
            logger.error(f"transferFrom failed: {e}")
            return False
    
    
    
    def withdraw(self, sender: str, wad: int) -> bool:
        """withdraw implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.withdraw(
                
                wad,
                
                sender=sender
            )
                
            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)
                
            return success
                
        except Exception as e:
            logger.error(f"withdraw failed: {e}")
            return False
    
    
    
    def decimals(self, ) -> Any:
        """decimals implementation"""
        try:
            return self.contract.decimals(
                
            )
        except Exception as e:
            logger.error(f"decimals failed: {e}")
            return None
    
    
    
    def balanceOf(self, param0: str) -> int:
        """balanceOf implementation"""
        try:
            return self.contract.balanceOf(
                param0
                ,
                
            )
        except Exception as e:
            logger.error(f"balanceOf failed: {e}")
            return None
    
    
    
    def symbol(self, ) -> str:
        """symbol implementation"""
        try:
            return self.contract.symbol(
                
            )
        except Exception as e:
            logger.error(f"symbol failed: {e}")
            return None
    
    
    
    def transfer(self, sender: str, dst: str, wad: int) -> bool:
        """transfer implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.transfer(
                
                dst,
                
                wad,
                
                sender=sender
            )
                
            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)
                
            return success
                
        except Exception as e:
            logger.error(f"transfer failed: {e}")
            return False
    
    
    
    def deposit(self, sender: str, value: int) -> bool:
        """deposit implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.deposit(
                sender=sender,
                value=value
            )
                
            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)
                
            return success
                
        except Exception as e:
            logger.error(f"deposit failed: {e}")
            return False
    
    
    
    def allowance(self, param0: str, param1: str) -> int:
        """allowance implementation"""
        try:
            return self.contract.allowance(
                param0
                ,
                param1
                ,
                
            )
        except Exception as e:
            logger.error(f"allowance failed: {e}")
            return None
    
    