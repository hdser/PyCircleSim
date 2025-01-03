from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from ape import Contract, chain
from src.framework.data import CirclesDataCollector
from src.framework.logging import get_logger

logger = get_logger(__name__)


class FjordLbpProxyV6Client:
    """Client interface for FjordLbpProxyV6 contract"""

    def __init__(
        self,
        contract_address: str,
        abi_path: str,
        gas_limits: Optional[Dict] = None,
        cache_config: Optional[Dict] = None,
        data_collector: Optional["CirclesDataCollector"] = None,
    ):
        self.contract = Contract(contract_address, abi=abi_path)
        self.collector = data_collector

        # Default gas limits
        self.gas_limits = gas_limits or {
            "LBPFactoryAddress": 300000,
            "VaultAddress": 300000,
            "WeightedPoolFactoryAddress": 300000,
            "addFundTokenOptions": 300000,
            "allowedFundTokens": 300000,
            "createLBP": 300000,
            "createWeightedPoolForLBP": 300000,
            "exitPool": 300000,
            "getBPTTokenBalance": 300000,
            "getFeeRecipients": 300000,
            "getPoolAt": 300000,
            "getPoolData": 300000,
            "getPools": 300000,
            "getRecipientShareBPS": 300000,
            "getWeightedPools": 300000,
            "getWeightedTokenBalance": 300000,
            "isAllowedFund": 300000,
            "isPool": 300000,
            "isWeightedPool": 300000,
            "lbpType": 300000,
            "owner": 300000,
            "platformAccessFeeBPS": 300000,
            "poolCount": 300000,
            "renounceOwnership": 300000,
            "setSwapEnabled": 300000,
            "skim": 300000,
            "transferOwnership": 300000,
            "transferPoolOwnership": 300000,
            "updateRecipients": 300000,
            "weightedPoolCount": 300000,
        }

        # Optional caching
        self.cache_enabled = cache_config.get("enabled", True) if cache_config else True
        self.cache_ttl = cache_config.get("ttl", 100) if cache_config else 100
        self.cache = {"last_update": datetime.min, "current_block": 0}

        # Initialize event handlers for all events and non-view functions

        self.on_GradualWeightUpdateScheduled = None

        self.on_JoinedPool = None

        self.on_JoinedWeightedPool = None

        self.on_OwnershipTransferred = None

        self.on_PoolCreated = None

        self.on_RecipientsUpdated = None

        self.on_Skimmed = None

        self.on_SwapEnabledSet = None

        self.on_TransferredFee = None

        self.on_TransferredPoolOwnership = None

        self.on_TransferredToken = None

        self.on_WeightedPoolCreated = None

        self.on_addFundTokenOptions = None

        self.on_createLBP = None

        self.on_createWeightedPoolForLBP = None

        self.on_exitPool = None

        self.on_renounceOwnership = None

        self.on_setSwapEnabled = None

        self.on_skim = None

        self.on_transferOwnership = None

        self.on_transferPoolOwnership = None

        self.on_updateRecipients = None

    # Define input type structs

    def LBPFactoryAddress(
        self,
    ) -> str:
        """LBPFactoryAddress implementation"""
        try:
            return self.contract.LBPFactoryAddress()
        except Exception as e:
            logger.error(f"LBPFactoryAddress failed: {e}")
            return None

    def VaultAddress(
        self,
    ) -> str:
        """VaultAddress implementation"""
        try:
            return self.contract.VaultAddress()
        except Exception as e:
            logger.error(f"VaultAddress failed: {e}")
            return None

    def WeightedPoolFactoryAddress(
        self,
    ) -> str:
        """WeightedPoolFactoryAddress implementation"""
        try:
            return self.contract.WeightedPoolFactoryAddress()
        except Exception as e:
            logger.error(f"WeightedPoolFactoryAddress failed: {e}")
            return None

    def addFundTokenOptions(self, sender: str, tokens: List[str]) -> bool:
        """addFundTokenOptions implementation"""
        try:
            # Handle struct parameters

            tx = self.contract.addFundTokenOptions(tokens, sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_addFundTokenOptions:
                    self.on_addFundTokenOptions(tokens=tokens, tx_hash=tx.txn_hash)
            return success

        except Exception as e:
            logger.error(f"addFundTokenOptions failed: {e}")
            return False

    def allowedFundTokens(
        self,
    ) -> List[str]:
        """allowedFundTokens implementation"""
        try:
            return self.contract.allowedFundTokens()
        except Exception as e:
            logger.error(f"allowedFundTokens failed: {e}")
            return None

    def createLBP(self, sender: str, poolConfig: Any) -> bool:
        """createLBP implementation"""
        try:
            # Handle struct parameters

            tx = self.contract.createLBP(poolConfig, sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_createLBP:
                    self.on_createLBP(poolConfig=poolConfig, tx_hash=tx.txn_hash)
            return success

        except Exception as e:
            logger.error(f"createLBP failed: {e}")
            return False

    def createWeightedPoolForLBP(
        self, sender: str, lbpPool: str, weightedPoolConfig: Any
    ) -> bool:
        """createWeightedPoolForLBP implementation"""
        try:
            # Handle struct parameters

            tx = self.contract.createWeightedPoolForLBP(
                lbpPool, weightedPoolConfig, sender=sender
            )

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_createWeightedPoolForLBP:
                    self.on_createWeightedPoolForLBP(
                        lbpPool=lbpPool,
                        weightedPoolConfig=weightedPoolConfig,
                        tx_hash=tx.txn_hash,
                    )
            return success

        except Exception as e:
            logger.error(f"createWeightedPoolForLBP failed: {e}")
            return False

    def exitPool(
        self, sender: str, pool: str, maxBPTTokenOut: int, isStandardFee: bool
    ) -> bool:
        """exitPool implementation"""
        try:
            # Handle struct parameters

            tx = self.contract.exitPool(
                pool, maxBPTTokenOut, isStandardFee, sender=sender
            )

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_exitPool:
                    self.on_exitPool(
                        pool=pool,
                        maxBPTTokenOut=maxBPTTokenOut,
                        isStandardFee=isStandardFee,
                        tx_hash=tx.txn_hash,
                    )
            return success

        except Exception as e:
            logger.error(f"exitPool failed: {e}")
            return False

    def getBPTTokenBalance(self, pool: str) -> int:
        """getBPTTokenBalance implementation"""
        try:
            return self.contract.getBPTTokenBalance(
                pool,
            )
        except Exception as e:
            logger.error(f"getBPTTokenBalance failed: {e}")
            return None

    def getFeeRecipients(
        self,
    ) -> List[str]:
        """getFeeRecipients implementation"""
        try:
            return self.contract.getFeeRecipients()
        except Exception as e:
            logger.error(f"getFeeRecipients failed: {e}")
            return None

    def getPoolAt(self, index: int) -> str:
        """getPoolAt implementation"""
        try:
            return self.contract.getPoolAt(
                index,
            )
        except Exception as e:
            logger.error(f"getPoolAt failed: {e}")
            return None

    def getPoolData(self, pool: str) -> Any:
        """getPoolData implementation"""
        try:
            return self.contract.getPoolData(
                pool,
            )
        except Exception as e:
            logger.error(f"getPoolData failed: {e}")
            return None

    def getPools(
        self,
    ) -> List[str]:
        """getPools implementation"""
        try:
            return self.contract.getPools()
        except Exception as e:
            logger.error(f"getPools failed: {e}")
            return None

    def getRecipientShareBPS(self, recipientAddress: str) -> int:
        """getRecipientShareBPS implementation"""
        try:
            return self.contract.getRecipientShareBPS(
                recipientAddress,
            )
        except Exception as e:
            logger.error(f"getRecipientShareBPS failed: {e}")
            return None

    def getWeightedPools(
        self,
    ) -> List[str]:
        """getWeightedPools implementation"""
        try:
            return self.contract.getWeightedPools()
        except Exception as e:
            logger.error(f"getWeightedPools failed: {e}")
            return None

    def getWeightedTokenBalance(self, weightedPool: str) -> int:
        """getWeightedTokenBalance implementation"""
        try:
            return self.contract.getWeightedTokenBalance(
                weightedPool,
            )
        except Exception as e:
            logger.error(f"getWeightedTokenBalance failed: {e}")
            return None

    def isAllowedFund(self, tokenAddress: str) -> bool:
        """isAllowedFund implementation"""
        try:
            return self.contract.isAllowedFund(
                tokenAddress,
            )
        except Exception as e:
            logger.error(f"isAllowedFund failed: {e}")
            return None

    def isPool(self, pool: str) -> bool:
        """isPool implementation"""
        try:
            return self.contract.isPool(
                pool,
            )
        except Exception as e:
            logger.error(f"isPool failed: {e}")
            return None

    def isWeightedPool(self, pool: str) -> bool:
        """isWeightedPool implementation"""
        try:
            return self.contract.isWeightedPool(
                pool,
            )
        except Exception as e:
            logger.error(f"isWeightedPool failed: {e}")
            return None

    def lbpType(
        self,
    ) -> Any:
        """lbpType implementation"""
        try:
            return self.contract.lbpType()
        except Exception as e:
            logger.error(f"lbpType failed: {e}")
            return None

    def owner(
        self,
    ) -> str:
        """owner implementation"""
        try:
            return self.contract.owner()
        except Exception as e:
            logger.error(f"owner failed: {e}")
            return None

    def platformAccessFeeBPS(
        self,
    ) -> int:
        """platformAccessFeeBPS implementation"""
        try:
            return self.contract.platformAccessFeeBPS()
        except Exception as e:
            logger.error(f"platformAccessFeeBPS failed: {e}")
            return None

    def poolCount(
        self,
    ) -> int:
        """poolCount implementation"""
        try:
            return self.contract.poolCount()
        except Exception as e:
            logger.error(f"poolCount failed: {e}")
            return None

    def renounceOwnership(
        self,
        sender: str,
    ) -> bool:
        """renounceOwnership implementation"""
        try:
            # Handle struct parameters

            tx = self.contract.renounceOwnership(sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_renounceOwnership:
                    self.on_renounceOwnership(tx_hash=tx.txn_hash)
            return success

        except Exception as e:
            logger.error(f"renounceOwnership failed: {e}")
            return False

    def setSwapEnabled(self, sender: str, pool: str, swapEnabled: bool) -> bool:
        """setSwapEnabled implementation"""
        try:
            # Handle struct parameters

            tx = self.contract.setSwapEnabled(pool, swapEnabled, sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_setSwapEnabled:
                    self.on_setSwapEnabled(
                        pool=pool, swapEnabled=swapEnabled, tx_hash=tx.txn_hash
                    )
            return success

        except Exception as e:
            logger.error(f"setSwapEnabled failed: {e}")
            return False

    def skim(self, sender: str, token: str, recipient: str) -> bool:
        """skim implementation"""
        try:
            # Handle struct parameters

            tx = self.contract.skim(token, recipient, sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_skim:
                    self.on_skim(token=token, recipient=recipient, tx_hash=tx.txn_hash)
            return success

        except Exception as e:
            logger.error(f"skim failed: {e}")
            return False

    def transferOwnership(self, sender: str, newOwner: str) -> bool:
        """transferOwnership implementation"""
        try:
            # Handle struct parameters

            tx = self.contract.transferOwnership(newOwner, sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_transferOwnership:
                    self.on_transferOwnership(newOwner=newOwner, tx_hash=tx.txn_hash)
            return success

        except Exception as e:
            logger.error(f"transferOwnership failed: {e}")
            return False

    def transferPoolOwnership(self, sender: str, pool: str, newOwner: str) -> bool:
        """transferPoolOwnership implementation"""
        try:
            # Handle struct parameters

            tx = self.contract.transferPoolOwnership(pool, newOwner, sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_transferPoolOwnership:
                    self.on_transferPoolOwnership(
                        pool=pool, newOwner=newOwner, tx_hash=tx.txn_hash
                    )
            return success

        except Exception as e:
            logger.error(f"transferPoolOwnership failed: {e}")
            return False

    def updateRecipients(
        self, sender: str, recipients: List[str], recipientShareBPS: List[int]
    ) -> bool:
        """updateRecipients implementation"""
        try:
            # Handle struct parameters

            tx = self.contract.updateRecipients(
                recipients, recipientShareBPS, sender=sender
            )

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_updateRecipients:
                    self.on_updateRecipients(
                        recipients=recipients,
                        recipientShareBPS=recipientShareBPS,
                        tx_hash=tx.txn_hash,
                    )
            return success

        except Exception as e:
            logger.error(f"updateRecipients failed: {e}")
            return False

    def weightedPoolCount(
        self,
    ) -> int:
        """weightedPoolCount implementation"""
        try:
            return self.contract.weightedPoolCount()
        except Exception as e:
            logger.error(f"weightedPoolCount failed: {e}")
            return None
