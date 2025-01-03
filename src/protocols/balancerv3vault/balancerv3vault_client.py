
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime 
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from ape import Contract, chain
from src.framework.data import CirclesDataCollector
from src.framework.logging import get_logger

logger = get_logger(__name__)

class BalancerV3VaultClient:
    """Client interface for BalancerV3Vault contract"""
    
    def __init__(
        self,
        contract_address: str,
        abi_path: str,
        gas_limits: Optional[Dict] = None,
        cache_config: Optional[Dict] = None,
        data_collector: Optional['CirclesDataCollector'] = None
    ):
        self.contract = Contract(contract_address, abi=abi_path)
        self.collector = data_collector
        
        # Default gas limits
        self.gas_limits = gas_limits or {
            
            'addLiquidity': 300000,
            
            'erc4626BufferWrapOrUnwrap': 300000,
            
            'getPoolTokenCountAndIndexOfToken': 300000,
            
            'getVaultExtension': 300000,
            
            'reentrancyGuardEntered': 300000,
            
            'removeLiquidity': 300000,
            
            'sendTo': 300000,
            
            'settle': 300000,
            
            'swap': 300000,
            
            'transfer': 300000,
            
            'transferFrom': 300000,
            
            'unlock': 300000,
            
        }
        
        # Optional caching
        self.cache_enabled = cache_config.get('enabled', True) if cache_config else True
        self.cache_ttl = cache_config.get('ttl', 100) if cache_config else 100
        self.cache = {
            'last_update': datetime.min,
            'current_block': 0
        }

        # Initialize event handlers for all events and non-view functions
        
        self.on_AggregateSwapFeePercentageChanged = None
        
        self.on_AggregateYieldFeePercentageChanged = None
        
        self.on_Approval = None
        
        self.on_AuthorizerChanged = None
        
        self.on_BufferSharesBurned = None
        
        self.on_BufferSharesMinted = None
        
        self.on_LiquidityAdded = None
        
        self.on_LiquidityAddedToBuffer = None
        
        self.on_LiquidityRemoved = None
        
        self.on_LiquidityRemovedFromBuffer = None
        
        self.on_PoolInitialized = None
        
        self.on_PoolPausedStateChanged = None
        
        self.on_PoolRecoveryModeStateChanged = None
        
        self.on_PoolRegistered = None
        
        self.on_ProtocolFeeControllerChanged = None
        
        self.on_Swap = None
        
        self.on_SwapFeePercentageChanged = None
        
        self.on_Transfer = None
        
        self.on_Unwrap = None
        
        self.on_VaultAuxiliary = None
        
        self.on_VaultBuffersPausedStateChanged = None
        
        self.on_VaultPausedStateChanged = None
        
        self.on_VaultQueriesDisabled = None
        
        self.on_VaultQueriesEnabled = None
        
        self.on_Wrap = None
        
        
        self.on_addLiquidity = None
        
        self.on_erc4626BufferWrapOrUnwrap = None
        
        self.on_removeLiquidity = None
        
        self.on_sendTo = None
        
        self.on_settle = None
        
        self.on_swap = None
        
        self.on_transfer = None
        
        self.on_transferFrom = None
        
        self.on_unlock = None
        
        
    
    
    def addLiquidity(self, sender: str, params: Any) -> bool:
        """addLiquidity implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.addLiquidity(
                
                params,
                
                sender=sender
            )
                
            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)
                
                if self.on_addLiquidity:
                    self.on_addLiquidity(
                        
                        params_=params,
                        
                        tx_hash=tx.txn_hash
                    )
            return success
                
        except Exception as e:
            logger.error(f"addLiquidity failed: {e}")
            return False
    
    
    
    def erc4626BufferWrapOrUnwrap(self, sender: str, params: Any) -> bool:
        """erc4626BufferWrapOrUnwrap implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.erc4626BufferWrapOrUnwrap(
                
                params,
                
                sender=sender
            )
                
            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)
                
                if self.on_erc4626BufferWrapOrUnwrap:
                    self.on_erc4626BufferWrapOrUnwrap(
                        
                        params_=params,
                        
                        tx_hash=tx.txn_hash
                    )
            return success
                
        except Exception as e:
            logger.error(f"erc4626BufferWrapOrUnwrap failed: {e}")
            return False
    
    
    
    def getPoolTokenCountAndIndexOfToken(self, pool: str, token: str) -> Tuple[int, int]:
        """getPoolTokenCountAndIndexOfToken implementation"""
        try:
            return self.contract.getPoolTokenCountAndIndexOfToken(
                
                pool,
                
                token,
                
            )
        except Exception as e:
            logger.error(f"getPoolTokenCountAndIndexOfToken failed: {e}")
            return None
    
    
    
    def getVaultExtension(self, ) -> str:
        """getVaultExtension implementation"""
        try:
            return self.contract.getVaultExtension(
                
            )
        except Exception as e:
            logger.error(f"getVaultExtension failed: {e}")
            return None
    
    
    
    def reentrancyGuardEntered(self, ) -> bool:
        """reentrancyGuardEntered implementation"""
        try:
            return self.contract.reentrancyGuardEntered(
                
            )
        except Exception as e:
            logger.error(f"reentrancyGuardEntered failed: {e}")
            return None
    
    
    
    def removeLiquidity(self, sender: str, params: Any) -> bool:
        """removeLiquidity implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.removeLiquidity(
                
                params,
                
                sender=sender
            )
                
            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)
                
                if self.on_removeLiquidity:
                    self.on_removeLiquidity(
                        
                        params_=params,
                        
                        tx_hash=tx.txn_hash
                    )
            return success
                
        except Exception as e:
            logger.error(f"removeLiquidity failed: {e}")
            return False
    
    
    
    def sendTo(self, sender: str, token: str, to_: str, amount: int) -> bool:
        """sendTo implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.sendTo(
                
                token,
                
                to_,
                
                amount,
                
                sender=sender
            )
                
            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)
                
                if self.on_sendTo:
                    self.on_sendTo(
                        
                        token_=token,
                        
                        to_=to_,
                        
                        amount_=amount,
                        
                        tx_hash=tx.txn_hash
                    )
            return success
                
        except Exception as e:
            logger.error(f"sendTo failed: {e}")
            return False
    
    
    
    def settle(self, sender: str, token: str, amountHint: int) -> bool:
        """settle implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.settle(
                
                token,
                
                amountHint,
                
                sender=sender
            )
                
            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)
                
                if self.on_settle:
                    self.on_settle(
                        
                        token_=token,
                        
                        amountHint_=amountHint,
                        
                        tx_hash=tx.txn_hash
                    )
            return success
                
        except Exception as e:
            logger.error(f"settle failed: {e}")
            return False
    
    
    
    def swap(self, sender: str, vaultSwapParams: Any) -> bool:
        """swap implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.swap(
                
                vaultSwapParams,
                
                sender=sender
            )
                
            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)
                
                if self.on_swap:
                    self.on_swap(
                        
                        vaultSwapParams_=vaultSwapParams,
                        
                        tx_hash=tx.txn_hash
                    )
            return success
                
        except Exception as e:
            logger.error(f"swap failed: {e}")
            return False
    
    
    
    def transfer(self, sender: str, owner: str, to_: str, amount: int) -> bool:
        """transfer implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.transfer(
                
                owner,
                
                to_,
                
                amount,
                
                sender=sender
            )
                
            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)
                
                if self.on_transfer:
                    self.on_transfer(
                        
                        owner_=owner,
                        
                        to_=to_,
                        
                        amount_=amount,
                        
                        tx_hash=tx.txn_hash
                    )
            return success
                
        except Exception as e:
            logger.error(f"transfer failed: {e}")
            return False
    
    
    
    def transferFrom(self, sender: str, spender: str, from_: str, to_: str, amount: int) -> bool:
        """transferFrom implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.transferFrom(
                
                spender,
                
                from_,
                
                to_,
                
                amount,
                
                sender=sender
            )
                
            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)
                
                if self.on_transferFrom:
                    self.on_transferFrom(
                        
                        spender_=spender,
                        
                        from_=from_,
                        
                        to_=to_,
                        
                        amount_=amount,
                        
                        tx_hash=tx.txn_hash
                    )
            return success
                
        except Exception as e:
            logger.error(f"transferFrom failed: {e}")
            return False
    
    
    
    def unlock(self, sender: str, data: bytes) -> bool:
        """unlock implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.unlock(
                
                data,
                
                sender=sender
            )
                
            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)
                
                if self.on_unlock:
                    self.on_unlock(
                        
                        data_=data,
                        
                        tx_hash=tx.txn_hash
                    )
            return success
                
        except Exception as e:
            logger.error(f"unlock failed: {e}")
            return False
    
    