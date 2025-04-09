from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from ape import Contract, chain
from src.framework.data import DataCollector
from src.framework.logging import get_logger

logger = get_logger(__name__)


class CirclesBackingFactoryClient:
    """Client interface for CirclesBackingFactory contract"""

    def __init__(
        self,
        contract_address: str,
        abi_path: str,
        gas_limits: Optional[Dict] = None,
        data_collector: Optional["DataCollector"] = None,
    ):
        self.contract = Contract(contract_address, abi=abi_path)
        self.collector = data_collector

        # Default gas limits
        self.gas_limits = gas_limits or {
            "ADMIN": 300000,
            "CRC_AMOUNT": 300000,
            "GET_UID_CONTRACT": 300000,
            "HUB_V2": 300000,
            "INSTANCE_BYTECODE_HASH": 300000,
            "LBP_FACTORY": 300000,
            "LIFT_ERC20": 300000,
            "TRADE_AMOUNT": 300000,
            "USDC": 300000,
            "VALID_TO": 300000,
            "VAULT": 300000,
            "backerOf": 300000,
            "backingParameters": 300000,
            "computeAddress": 300000,
            "createLBP": 300000,
            "exitLBP": 300000,
            "getAppData": 300000,
            "getPersonalCircles": 300000,
            "isActiveLBP": 300000,
            "notifyRelease": 300000,
            "onERC1155Received": 300000,
            "postAppData": 300000,
            "preAppData": 300000,
            "releaseTimestamp": 300000,
            "setReleaseTimestamp": 300000,
            "setSupportedBackingAssetStatus": 300000,
            "supportedBackingAssets": 300000,
        }

    def ADMIN(
        self,
    ) -> str:
        """ADMIN implementation"""
        try:
            return self.contract.ADMIN()
        except Exception as e:
            logger.error(f"ADMIN failed: {e}")
            return None

    def CRC_AMOUNT(
        self,
    ) -> int:
        """CRC_AMOUNT implementation"""
        try:
            return self.contract.CRC_AMOUNT()
        except Exception as e:
            logger.error(f"CRC_AMOUNT failed: {e}")
            return None

    def GET_UID_CONTRACT(
        self,
    ) -> str:
        """GET_UID_CONTRACT implementation"""
        try:
            return self.contract.GET_UID_CONTRACT()
        except Exception as e:
            logger.error(f"GET_UID_CONTRACT failed: {e}")
            return None

    def HUB_V2(
        self,
    ) -> str:
        """HUB_V2 implementation"""
        try:
            return self.contract.HUB_V2()
        except Exception as e:
            logger.error(f"HUB_V2 failed: {e}")
            return None

    def INSTANCE_BYTECODE_HASH(
        self,
    ) -> bytes:
        """INSTANCE_BYTECODE_HASH implementation"""
        try:
            return self.contract.INSTANCE_BYTECODE_HASH()
        except Exception as e:
            logger.error(f"INSTANCE_BYTECODE_HASH failed: {e}")
            return None

    def LBP_FACTORY(
        self,
    ) -> str:
        """LBP_FACTORY implementation"""
        try:
            return self.contract.LBP_FACTORY()
        except Exception as e:
            logger.error(f"LBP_FACTORY failed: {e}")
            return None

    def LIFT_ERC20(
        self,
    ) -> str:
        """LIFT_ERC20 implementation"""
        try:
            return self.contract.LIFT_ERC20()
        except Exception as e:
            logger.error(f"LIFT_ERC20 failed: {e}")
            return None

    def TRADE_AMOUNT(
        self,
    ) -> int:
        """TRADE_AMOUNT implementation"""
        try:
            return self.contract.TRADE_AMOUNT()
        except Exception as e:
            logger.error(f"TRADE_AMOUNT failed: {e}")
            return None

    def USDC(
        self,
    ) -> str:
        """USDC implementation"""
        try:
            return self.contract.USDC()
        except Exception as e:
            logger.error(f"USDC failed: {e}")
            return None

    def VALID_TO(
        self,
    ) -> Any:
        """VALID_TO implementation"""
        try:
            return self.contract.VALID_TO()
        except Exception as e:
            logger.error(f"VALID_TO failed: {e}")
            return None

    def VAULT(
        self,
    ) -> str:
        """VAULT implementation"""
        try:
            return self.contract.VAULT()
        except Exception as e:
            logger.error(f"VAULT failed: {e}")
            return None

    def backerOf(self, circlesBacking: str) -> str:
        """backerOf implementation

        Args:
            circlesBacking: address - Contract parameter

        """
        try:
            return self.contract.backerOf(circlesBacking)
        except Exception as e:
            logger.error(f"backerOf failed: {e}")
            return None

    def backingParameters(
        self,
    ) -> Tuple[str, str, str, int]:
        """backingParameters implementation"""
        try:
            return self.contract.backingParameters()
        except Exception as e:
            logger.error(f"backingParameters failed: {e}")
            return None

    def computeAddress(self, backer: str) -> str:
        """computeAddress implementation

        Args:
            backer: address - Contract parameter

        """
        try:
            return self.contract.computeAddress(backer)
        except Exception as e:
            logger.error(f"computeAddress failed: {e}")
            return None

    def createLBP(
        self,
        sender: str,
        value: int,
        personalCRC: str,
        personalCRCAmount: int,
        backingAsset: str,
        backingAssetAmount: int,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """createLBP implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            personalCRC: address - Contract parameter

            personalCRCAmount: uint256 - Contract parameter

            backingAsset: address - Contract parameter

            backingAssetAmount: uint256 - Contract parameter

        """
        try:
            tx = self.contract.createLBP(
                personalCRC,
                personalCRCAmount,
                backingAsset,
                backingAssetAmount,
                sender=sender,
                value=value,
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
            logger.error(f"createLBP failed: {e}")
            return False

    def exitLBP(
        self,
        sender: str,
        value: int,
        lbp: str,
        bptAmount: int,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """exitLBP implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            lbp: address - Contract parameter

            bptAmount: uint256 - Contract parameter

        """
        try:
            tx = self.contract.exitLBP(lbp, bptAmount, sender=sender, value=value)
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
            logger.error(f"exitLBP failed: {e}")
            return False

    def getAppData(self, _circlesBackingInstance: str) -> Tuple[str, bytes]:
        """getAppData implementation

        Args:
            _circlesBackingInstance: address - Contract parameter

        """
        try:
            return self.contract.getAppData(_circlesBackingInstance)
        except Exception as e:
            logger.error(f"getAppData failed: {e}")
            return None

    def getPersonalCircles(
        self,
        sender: str,
        value: int,
        avatar: str,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """getPersonalCircles implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            avatar: address - Contract parameter

        """
        try:
            tx = self.contract.getPersonalCircles(avatar, sender=sender, value=value)
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
            logger.error(f"getPersonalCircles failed: {e}")
            return False

    def isActiveLBP(self, backer: str) -> bool:
        """isActiveLBP implementation

        Args:
            backer: address - Contract parameter

        """
        try:
            return self.contract.isActiveLBP(backer)
        except Exception as e:
            logger.error(f"isActiveLBP failed: {e}")
            return None

    def notifyRelease(
        self,
        sender: str,
        value: int,
        lbp: str,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """notifyRelease implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            lbp: address - Contract parameter

        """
        try:
            tx = self.contract.notifyRelease(lbp, sender=sender, value=value)
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
            logger.error(f"notifyRelease failed: {e}")
            return False

    def onERC1155Received(
        self,
        sender: str,
        value: int,
        operator: str,
        from_: str,
        id: int,
        value_amount: int,
        data: bytes,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """onERC1155Received implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            operator: address - Contract parameter

            from_: address - Contract parameter

            id: uint256 - Contract parameter

            value: uint256 - Contract parameter

            data: bytes - Contract parameter

        """
        try:
            tx = self.contract.onERC1155Received(
                operator, from_, id, value_, data, sender=sender, value=value
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
            logger.error(f"onERC1155Received failed: {e}")
            return False

    def postAppData(
        self,
    ) -> str:
        """postAppData implementation"""
        try:
            return self.contract.postAppData()
        except Exception as e:
            logger.error(f"postAppData failed: {e}")
            return None

    def preAppData(
        self,
    ) -> str:
        """preAppData implementation"""
        try:
            return self.contract.preAppData()
        except Exception as e:
            logger.error(f"preAppData failed: {e}")
            return None

    def releaseTimestamp(
        self,
    ) -> Any:
        """releaseTimestamp implementation"""
        try:
            return self.contract.releaseTimestamp()
        except Exception as e:
            logger.error(f"releaseTimestamp failed: {e}")
            return None

    def setReleaseTimestamp(
        self,
        sender: str,
        value: int,
        timestamp: Any,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """setReleaseTimestamp implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            timestamp: uint32 - Contract parameter

        """
        try:
            tx = self.contract.setReleaseTimestamp(
                timestamp, sender=sender, value=value
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
            logger.error(f"setReleaseTimestamp failed: {e}")
            return False

    def setSupportedBackingAssetStatus(
        self,
        sender: str,
        value: int,
        backingAsset: str,
        status: bool,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """setSupportedBackingAssetStatus implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            backingAsset: address - Contract parameter

            status: bool - Contract parameter

        """
        try:
            tx = self.contract.setSupportedBackingAssetStatus(
                backingAsset, status, sender=sender, value=value
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
            logger.error(f"setSupportedBackingAssetStatus failed: {e}")
            return False

    def supportedBackingAssets(self, supportedAsset: str) -> bool:
        """supportedBackingAssets implementation

        Args:
            supportedAsset: address - Contract parameter

        """
        try:
            return self.contract.supportedBackingAssets(supportedAsset)
        except Exception as e:
            logger.error(f"supportedBackingAssets failed: {e}")
            return None
