from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime 
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from ape import Contract, chain
from src.framework.data import DataCollector
from src.framework.logging import get_logger

logger = get_logger(__name__)

class BalancerV2VaultClient:
    """Client interface for BalancerV2Vault contract"""
    
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
            
            'WETH': 300000,
            
            'batchSwap': 300000,
            
            'deregisterTokens': 300000,
            
            'exitPool': 300000,
            
            'flashLoan': 300000,
            
            'getActionId': 300000,
            
            'getAuthorizer': 300000,
            
            'getDomainSeparator': 300000,
            
            'getInternalBalance': 300000,
            
            'getNextNonce': 300000,
            
            'getPausedState': 300000,
            
            'getPool': 300000,
            
            'getPoolTokenInfo': 300000,
            
            'getPoolTokens': 300000,
            
            'getProtocolFeesCollector': 300000,
            
            'hasApprovedRelayer': 300000,
            
            'joinPool': 300000,
            
            'managePoolBalance': 300000,
            
            'manageUserBalance': 300000,
            
            'queryBatchSwap': 300000,
            
            'registerPool': 300000,
            
            'registerTokens': 300000,
            
            'setAuthorizer': 300000,
            
            'setPaused': 300000,
            
            'setRelayerApproval': 300000,
            
            'swap': 300000,
            
        }
        
    
    
    def WETH(self, ) -> str:
        """WETH implementation
        
        """
        try:
            return self.contract.WETH()
        except Exception as e:
            logger.error(f"WETH failed: {e}")
            return None
    
    
    
    def batchSwap(self, sender: str, value: int, kind: Any, swaps: List[Any], assets: List[str], funds: Any, limits: List[int], deadline: int, context: Optional['SimulationContext'] = None) -> bool:
        """batchSwap implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
            kind: uint8 - Contract parameter
            
            swaps: tuple[] - Contract parameter
            
            assets: address[] - Contract parameter
            
            funds: tuple - Contract parameter
            
            limits: int256[] - Contract parameter
            
            deadline: uint256 - Contract parameter
            
        """
        try:
            tx = self.contract.batchSwap(
                kind, swaps, assets, funds, limits, deadline, 
                sender=sender,
                value=value
            )
            success = bool(tx and tx.status == 1)
            if success:
                # Record events if collector exists
                if self.collector:
                    self.collector.record_transaction_events(tx, context)
                
                # Get simulation from context if it exists
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success
        except Exception as e:
            logger.error(f"batchSwap failed: {e}")
            return False
    
    
    
    def deregisterTokens(self, sender: str, value: int, poolId: bytes, tokens: List[str], context: Optional['SimulationContext'] = None) -> bool:
        """deregisterTokens implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
            poolId: bytes32 - Contract parameter
            
            tokens: address[] - Contract parameter
            
        """
        try:
            tx = self.contract.deregisterTokens(
                poolId, tokens, 
                sender=sender,
                value=value
            )
            success = bool(tx and tx.status == 1)
            if success:
                # Record events if collector exists
                if self.collector:
                    self.collector.record_transaction_events(tx, context)
                
                # Get simulation from context if it exists
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success
        except Exception as e:
            logger.error(f"deregisterTokens failed: {e}")
            return False
    
    
    
    def exitPool(self, sender: str, value: int, poolId: bytes, sender_account: str, recipient: str, request: Any, context: Optional['SimulationContext'] = None) -> bool:
        """exitPool implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
            poolId: bytes32 - Contract parameter
            
            account: address - Contract parameter
            
            recipient: address - Contract parameter
            
            request: tuple - Contract parameter
            
        """
        try:
            tx = self.contract.exitPool(
                poolId, sender_account, recipient, request, 
                sender=sender,
                value=value
            )
            success = bool(tx and tx.status == 1)
            if success:
                # Record events if collector exists
                if self.collector:
                    self.collector.record_transaction_events(tx, context)
                
                # Get simulation from context if it exists
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success
        except Exception as e:
            logger.error(f"exitPool failed: {e}")
            return False
    
    
    
    def flashLoan(self, sender: str, value: int, recipient: str, tokens: List[str], amounts: List[int], userData: bytes, context: Optional['SimulationContext'] = None) -> bool:
        """flashLoan implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
            recipient: address - Contract parameter
            
            tokens: address[] - Contract parameter
            
            amounts: uint256[] - Contract parameter
            
            userData: bytes - Contract parameter
            
        """
        try:
            tx = self.contract.flashLoan(
                recipient, tokens, amounts, userData, 
                sender=sender,
                value=value
            )
            success = bool(tx and tx.status == 1)
            if success:
                # Record events if collector exists
                if self.collector:
                    self.collector.record_transaction_events(tx, context)
                
                # Get simulation from context if it exists
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success
        except Exception as e:
            logger.error(f"flashLoan failed: {e}")
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
    
    
    
    def getAuthorizer(self, ) -> str:
        """getAuthorizer implementation
        
        """
        try:
            return self.contract.getAuthorizer()
        except Exception as e:
            logger.error(f"getAuthorizer failed: {e}")
            return None
    
    
    
    def getDomainSeparator(self, ) -> bytes:
        """getDomainSeparator implementation
        
        """
        try:
            return self.contract.getDomainSeparator()
        except Exception as e:
            logger.error(f"getDomainSeparator failed: {e}")
            return None
    
    
    
    def getInternalBalance(self, user: str, tokens: List[str]) -> List[int]:
        """getInternalBalance implementation
        
        Args:
            user: address - Contract parameter
        
        Args:
            tokens: address[] - Contract parameter
        
        """
        try:
            return self.contract.getInternalBalance(user, tokens)
        except Exception as e:
            logger.error(f"getInternalBalance failed: {e}")
            return None
    
    
    
    def getNextNonce(self, user: str) -> int:
        """getNextNonce implementation
        
        Args:
            user: address - Contract parameter
        
        """
        try:
            return self.contract.getNextNonce(user)
        except Exception as e:
            logger.error(f"getNextNonce failed: {e}")
            return None
    
    
    
    def getPausedState(self, ) -> Tuple[bool, int, int]:
        """getPausedState implementation
        
        """
        try:
            return self.contract.getPausedState()
        except Exception as e:
            logger.error(f"getPausedState failed: {e}")
            return None
    
    
    
    def getPool(self, poolId: bytes) -> Tuple[str, Any]:
        """getPool implementation
        
        Args:
            poolId: bytes32 - Contract parameter
        
        """
        try:
            return self.contract.getPool(poolId)
        except Exception as e:
            logger.error(f"getPool failed: {e}")
            return None
    
    
    
    def getPoolTokenInfo(self, poolId: bytes, token: str) -> Tuple[int, int, int, str]:
        """getPoolTokenInfo implementation
        
        Args:
            poolId: bytes32 - Contract parameter
        
        Args:
            token: address - Contract parameter
        
        """
        try:
            return self.contract.getPoolTokenInfo(poolId, token)
        except Exception as e:
            logger.error(f"getPoolTokenInfo failed: {e}")
            return None
    
    
    
    def getPoolTokens(self, poolId: bytes) -> Tuple[List[str], List[int], int]:
        """getPoolTokens implementation
        
        Args:
            poolId: bytes32 - Contract parameter
        
        """
        try:
            return self.contract.getPoolTokens(poolId)
        except Exception as e:
            logger.error(f"getPoolTokens failed: {e}")
            return None
    
    
    
    def getProtocolFeesCollector(self, ) -> str:
        """getProtocolFeesCollector implementation
        
        """
        try:
            return self.contract.getProtocolFeesCollector()
        except Exception as e:
            logger.error(f"getProtocolFeesCollector failed: {e}")
            return None
    
    
    
    def hasApprovedRelayer(self, user: str, relayer: str) -> bool:
        """hasApprovedRelayer implementation
        
        Args:
            user: address - Contract parameter
        
        Args:
            relayer: address - Contract parameter
        
        """
        try:
            return self.contract.hasApprovedRelayer(user, relayer)
        except Exception as e:
            logger.error(f"hasApprovedRelayer failed: {e}")
            return None
    
    
    
    def joinPool(self, sender: str, value: int, poolId: bytes, sender_account: str, recipient: str, request: Any, context: Optional['SimulationContext'] = None) -> bool:
        """joinPool implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
            poolId: bytes32 - Contract parameter
            
            account: address - Contract parameter
            
            recipient: address - Contract parameter
            
            request: tuple - Contract parameter
            
        """
        try:
            tx = self.contract.joinPool(
                poolId, sender_account, recipient, request, 
                sender=sender,
                value=value
            )
            success = bool(tx and tx.status == 1)
            if success:
                # Record events if collector exists
                if self.collector:
                    self.collector.record_transaction_events(tx, context)
                
                # Get simulation from context if it exists
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success
        except Exception as e:
            logger.error(f"joinPool failed: {e}")
            return False
    
    
    
    def managePoolBalance(self, sender: str, value: int, ops: List[Any], context: Optional['SimulationContext'] = None) -> bool:
        """managePoolBalance implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
            ops: tuple[] - Contract parameter
            
        """
        try:
            tx = self.contract.managePoolBalance(
                ops, 
                sender=sender,
                value=value
            )
            success = bool(tx and tx.status == 1)
            if success:
                # Record events if collector exists
                if self.collector:
                    self.collector.record_transaction_events(tx, context)
                
                # Get simulation from context if it exists
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success
        except Exception as e:
            logger.error(f"managePoolBalance failed: {e}")
            return False
    
    
    
    def manageUserBalance(self, sender: str, value: int, ops: List[Any], context: Optional['SimulationContext'] = None) -> bool:
        """manageUserBalance implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
            ops: tuple[] - Contract parameter
            
        """
        try:
            tx = self.contract.manageUserBalance(
                ops, 
                sender=sender,
                value=value
            )
            success = bool(tx and tx.status == 1)
            if success:
                # Record events if collector exists
                if self.collector:
                    self.collector.record_transaction_events(tx, context)
                
                # Get simulation from context if it exists
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success
        except Exception as e:
            logger.error(f"manageUserBalance failed: {e}")
            return False
    
    
    
    def queryBatchSwap(self, sender: str, value: int, kind: Any, swaps: List[Any], assets: List[str], funds: Any, context: Optional['SimulationContext'] = None) -> bool:
        """queryBatchSwap implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
            kind: uint8 - Contract parameter
            
            swaps: tuple[] - Contract parameter
            
            assets: address[] - Contract parameter
            
            funds: tuple - Contract parameter
            
        """
        try:
            tx = self.contract.queryBatchSwap(
                kind, swaps, assets, funds, 
                sender=sender,
                value=value
            )
            success = bool(tx and tx.status == 1)
            if success:
                # Record events if collector exists
                if self.collector:
                    self.collector.record_transaction_events(tx, context)
                
                # Get simulation from context if it exists
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success
        except Exception as e:
            logger.error(f"queryBatchSwap failed: {e}")
            return False
    
    
    
    def registerPool(self, sender: str, value: int, specialization: Any, context: Optional['SimulationContext'] = None) -> bool:
        """registerPool implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
            specialization: uint8 - Contract parameter
            
        """
        try:
            tx = self.contract.registerPool(
                specialization, 
                sender=sender,
                value=value
            )
            success = bool(tx and tx.status == 1)
            if success:
                # Record events if collector exists
                if self.collector:
                    self.collector.record_transaction_events(tx, context)
                
                # Get simulation from context if it exists
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success
        except Exception as e:
            logger.error(f"registerPool failed: {e}")
            return False
    
    
    
    def registerTokens(self, sender: str, value: int, poolId: bytes, tokens: List[str], assetManagers: List[str], context: Optional['SimulationContext'] = None) -> bool:
        """registerTokens implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
            poolId: bytes32 - Contract parameter
            
            tokens: address[] - Contract parameter
            
            assetManagers: address[] - Contract parameter
            
        """
        try:
            tx = self.contract.registerTokens(
                poolId, tokens, assetManagers, 
                sender=sender,
                value=value
            )
            success = bool(tx and tx.status == 1)
            if success:
                # Record events if collector exists
                if self.collector:
                    self.collector.record_transaction_events(tx, context)
                
                # Get simulation from context if it exists
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success
        except Exception as e:
            logger.error(f"registerTokens failed: {e}")
            return False
    
    
    
    def setAuthorizer(self, sender: str, value: int, newAuthorizer: str, context: Optional['SimulationContext'] = None) -> bool:
        """setAuthorizer implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
            newAuthorizer: address - Contract parameter
            
        """
        try:
            tx = self.contract.setAuthorizer(
                newAuthorizer, 
                sender=sender,
                value=value
            )
            success = bool(tx and tx.status == 1)
            if success:
                # Record events if collector exists
                if self.collector:
                    self.collector.record_transaction_events(tx, context)
                
                # Get simulation from context if it exists
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success
        except Exception as e:
            logger.error(f"setAuthorizer failed: {e}")
            return False
    
    
    
    def setPaused(self, sender: str, value: int, paused: bool, context: Optional['SimulationContext'] = None) -> bool:
        """setPaused implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
            paused: bool - Contract parameter
            
        """
        try:
            tx = self.contract.setPaused(
                paused, 
                sender=sender,
                value=value
            )
            success = bool(tx and tx.status == 1)
            if success:
                # Record events if collector exists
                if self.collector:
                    self.collector.record_transaction_events(tx, context)
                
                # Get simulation from context if it exists
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success
        except Exception as e:
            logger.error(f"setPaused failed: {e}")
            return False
    
    
    
    def setRelayerApproval(self, sender: str, value: int, sender_account: str, relayer: str, approved: bool, context: Optional['SimulationContext'] = None) -> bool:
        """setRelayerApproval implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
            account: address - Contract parameter
            
            relayer: address - Contract parameter
            
            approved: bool - Contract parameter
            
        """
        try:
            tx = self.contract.setRelayerApproval(
                sender_account, relayer, approved, 
                sender=sender,
                value=value
            )
            success = bool(tx and tx.status == 1)
            if success:
                # Record events if collector exists
                if self.collector:
                    self.collector.record_transaction_events(tx, context)
                
                # Get simulation from context if it exists
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success
        except Exception as e:
            logger.error(f"setRelayerApproval failed: {e}")
            return False
    
    
    
    def swap(self, sender: str, value: int, singleSwap: Any, funds: Any, limit: int, deadline: int, context: Optional['SimulationContext'] = None) -> bool:
        """swap implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction
            
            singleSwap: tuple - Contract parameter
            
            funds: tuple - Contract parameter
            
            limit: uint256 - Contract parameter
            
            deadline: uint256 - Contract parameter
            
        """
        try:
            tx = self.contract.swap(
                singleSwap, funds, limit, deadline, 
                sender=sender,
                value=value
            )
            success = bool(tx and tx.status == 1)
            if success:
                # Record events if collector exists
                if self.collector:
                    self.collector.record_transaction_events(tx, context)
                
                # Get simulation from context if it exists
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success
        except Exception as e:
            logger.error(f"swap failed: {e}")
            return False
    
    