from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from ape import Contract, chain
from src.framework.data import DataCollector
from src.framework.logging import get_logger

logger = get_logger(__name__)


class SuperGroupClient:
    """Client interface for SuperGroup contract"""

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
            "MAX_RATIO": 300000,
            "beforeBurnPolicy": 300000,
            "beforeMintPolicy": 300000,
            "beforeRedeemPolicy": 300000,
            "countOperators": 300000,
            "feeCollection": 300000,
            "getOperators": 300000,
            "isAuthorizedOperator": 300000,
            "launchpad": 300000,
            "mintFee": 300000,
            "onERC1155BatchReceived": 300000,
            "onERC1155Received": 300000,
            "operators": 300000,
            "owner": 300000,
            "proxyStatus": 300000,
            "redemptionBurnRatio": 300000,
            "registerOperatorRequest": 300000,
            "registerShortName": 300000,
            "registerShortNameWithNonce": 300000,
            "requireOperator": 300000,
            "returnGroupCirclesToSender": 300000,
            "safeBatchTransferFrom": 300000,
            "safeTransferFrom": 300000,
            "service": 300000,
            "setAdvancedUsageFlag": 300000,
            "setAuthorizedOperator": 300000,
            "setMintFee": 300000,
            "setRedemptionBurn": 300000,
            "setRequireOperators": 300000,
            "setReturnGroupCirclesToSender": 300000,
            "setService": 300000,
            "setup": 300000,
            "setup": 300000,
            "supportsInterface": 300000,
            "trust": 300000,
            "trustBatch": 300000,
            "updateMetadataDigest": 300000,
        }

    def MAX_RATIO(
        self,
    ) -> int:
        """MAX_RATIO implementation"""
        try:
            return self.contract.MAX_RATIO()
        except Exception as e:
            logger.error(f"MAX_RATIO failed: {e}")
            return None

    def beforeBurnPolicy(
        self,
        sender: str,
        value: int,
        param0: str,
        param1: str,
        param2: int,
        param3: bytes,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """beforeBurnPolicy implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            : address - Contract parameter

            : address - Contract parameter

            : uint256 - Contract parameter

            : bytes - Contract parameter

        """
        try:
            tx = self.contract.beforeBurnPolicy(
                param0, param1, param2, param3, sender=sender, value=value
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
            logger.error(f"beforeBurnPolicy failed: {e}")
            return False

    def beforeMintPolicy(
        self,
        sender: str,
        value: int,
        _minter: str,
        _group: str,
        _collateral: List[int],
        _amounts: List[int],
        param4: bytes,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """beforeMintPolicy implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _minter: address - Contract parameter

            _group: address - Contract parameter

            _collateral: uint256[] - Contract parameter

            _amounts: uint256[] - Contract parameter

            : bytes - Contract parameter

        """
        try:
            tx = self.contract.beforeMintPolicy(
                _minter,
                _group,
                _collateral,
                _amounts,
                param4,
                sender=sender,
                value=value,
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
            logger.error(f"beforeMintPolicy failed: {e}")
            return False

    def beforeRedeemPolicy(
        self,
        sender: str,
        value: int,
        param0: str,
        param1: str,
        _group: str,
        param3: int,
        _data: bytes,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """beforeRedeemPolicy implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            : address - Contract parameter

            : address - Contract parameter

            _group: address - Contract parameter

            : uint256 - Contract parameter

            _data: bytes - Contract parameter

        """
        try:
            tx = self.contract.beforeRedeemPolicy(
                param0, param1, _group, param3, _data, sender=sender, value=value
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
            logger.error(f"beforeRedeemPolicy failed: {e}")
            return False

    def countOperators(
        self,
    ) -> int:
        """countOperators implementation"""
        try:
            return self.contract.countOperators()
        except Exception as e:
            logger.error(f"countOperators failed: {e}")
            return None

    def feeCollection(
        self,
    ) -> str:
        """feeCollection implementation"""
        try:
            return self.contract.feeCollection()
        except Exception as e:
            logger.error(f"feeCollection failed: {e}")
            return None

    def getOperators(
        self,
    ) -> List[str]:
        """getOperators implementation"""
        try:
            return self.contract.getOperators()
        except Exception as e:
            logger.error(f"getOperators failed: {e}")
            return None

    def isAuthorizedOperator(self, _operator: str) -> bool:
        """isAuthorizedOperator implementation

        Args:
            _operator: address - Contract parameter

        """
        try:
            return self.contract.isAuthorizedOperator(_operator)
        except Exception as e:
            logger.error(f"isAuthorizedOperator failed: {e}")
            return None

    def launchpad(
        self,
    ) -> str:
        """launchpad implementation"""
        try:
            return self.contract.launchpad()
        except Exception as e:
            logger.error(f"launchpad failed: {e}")
            return None

    def mintFee(
        self,
    ) -> int:
        """mintFee implementation"""
        try:
            return self.contract.mintFee()
        except Exception as e:
            logger.error(f"mintFee failed: {e}")
            return None

    def onERC1155BatchReceived(
        self,
        sender: str,
        value: int,
        param0: str,
        _from: str,
        _ids: List[int],
        _values: List[int],
        _data: bytes,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """onERC1155BatchReceived implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            : address - Contract parameter

            _from: address - Contract parameter

            _ids: uint256[] - Contract parameter

            _values: uint256[] - Contract parameter

            _data: bytes - Contract parameter

        """
        try:
            tx = self.contract.onERC1155BatchReceived(
                param0, _from, _ids, _values, _data, sender=sender, value=value
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
            logger.error(f"onERC1155BatchReceived failed: {e}")
            return False

    def onERC1155Received(
        self,
        sender: str,
        value: int,
        param0: str,
        _from: str,
        _id: int,
        _value: int,
        _data: bytes,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """onERC1155Received implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            : address - Contract parameter

            _from: address - Contract parameter

            _id: uint256 - Contract parameter

            _value: uint256 - Contract parameter

            _data: bytes - Contract parameter

        """
        try:
            tx = self.contract.onERC1155Received(
                param0, _from, _id, _value, _data, sender=sender, value=value
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
            logger.error(f"onERC1155Received failed: {e}")
            return False

    def operators(self, param0: str) -> str:
        """operators implementation

        Args:
            : address - Contract parameter

        """
        try:
            return self.contract.operators(param0)
        except Exception as e:
            logger.error(f"operators failed: {e}")
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

    def proxyStatus(
        self,
    ) -> Any:
        """proxyStatus implementation"""
        try:
            return self.contract.proxyStatus()
        except Exception as e:
            logger.error(f"proxyStatus failed: {e}")
            return None

    def redemptionBurnRatio(
        self,
    ) -> int:
        """redemptionBurnRatio implementation"""
        try:
            return self.contract.redemptionBurnRatio()
        except Exception as e:
            logger.error(f"redemptionBurnRatio failed: {e}")
            return None

    def registerOperatorRequest(
        self,
        sender: str,
        value: int,
        _minter: str,
        _group: str,
        _collateral: List[int],
        _amounts: List[int],
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """registerOperatorRequest implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _minter: address - Contract parameter

            _group: address - Contract parameter

            _collateral: uint256[] - Contract parameter

            _amounts: uint256[] - Contract parameter

        """
        try:
            tx = self.contract.registerOperatorRequest(
                _minter, _group, _collateral, _amounts, sender=sender, value=value
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
            logger.error(f"registerOperatorRequest failed: {e}")
            return False

    def registerShortName(
        self, sender: str, value: int, context: Optional["SimulationContext"] = None
    ) -> bool:
        """registerShortName implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

        """
        try:
            tx = self.contract.registerShortName(sender=sender, value=value)
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
            logger.error(f"registerShortName failed: {e}")
            return False

    def registerShortNameWithNonce(
        self,
        sender: str,
        value: int,
        _nonce: int,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """registerShortNameWithNonce implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _nonce: uint256 - Contract parameter

        """
        try:
            tx = self.contract.registerShortNameWithNonce(
                _nonce, sender=sender, value=value
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
            logger.error(f"registerShortNameWithNonce failed: {e}")
            return False

    def requireOperator(
        self,
    ) -> bool:
        """requireOperator implementation"""
        try:
            return self.contract.requireOperator()
        except Exception as e:
            logger.error(f"requireOperator failed: {e}")
            return None

    def returnGroupCirclesToSender(
        self,
    ) -> bool:
        """returnGroupCirclesToSender implementation"""
        try:
            return self.contract.returnGroupCirclesToSender()
        except Exception as e:
            logger.error(f"returnGroupCirclesToSender failed: {e}")
            return None

    def safeBatchTransferFrom(
        self,
        sender: str,
        value: int,
        _from: str,
        _to: str,
        _ids: List[int],
        _values: List[int],
        _data: bytes,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """safeBatchTransferFrom implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _from: address - Contract parameter

            _to: address - Contract parameter

            _ids: uint256[] - Contract parameter

            _values: uint256[] - Contract parameter

            _data: bytes - Contract parameter

        """
        try:
            tx = self.contract.safeBatchTransferFrom(
                _from, _to, _ids, _values, _data, sender=sender, value=value
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
            logger.error(f"safeBatchTransferFrom failed: {e}")
            return False

    def safeTransferFrom(
        self,
        sender: str,
        value: int,
        _from: str,
        _to: str,
        _id: int,
        _value: int,
        _data: bytes,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """safeTransferFrom implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _from: address - Contract parameter

            _to: address - Contract parameter

            _id: uint256 - Contract parameter

            _value: uint256 - Contract parameter

            _data: bytes - Contract parameter

        """
        try:
            tx = self.contract.safeTransferFrom(
                _from, _to, _id, _value, _data, sender=sender, value=value
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
            logger.error(f"safeTransferFrom failed: {e}")
            return False

    def service(
        self,
    ) -> str:
        """service implementation"""
        try:
            return self.contract.service()
        except Exception as e:
            logger.error(f"service failed: {e}")
            return None

    def setAdvancedUsageFlag(
        self,
        sender: str,
        value: int,
        _flag: bytes,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """setAdvancedUsageFlag implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _flag: bytes32 - Contract parameter

        """
        try:
            tx = self.contract.setAdvancedUsageFlag(_flag, sender=sender, value=value)
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
            logger.error(f"setAdvancedUsageFlag failed: {e}")
            return False

    def setAuthorizedOperator(
        self,
        sender: str,
        value: int,
        _operator: str,
        _authorized: bool,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """setAuthorizedOperator implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _operator: address - Contract parameter

            _authorized: bool - Contract parameter

        """
        try:
            tx = self.contract.setAuthorizedOperator(
                _operator, _authorized, sender=sender, value=value
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
            logger.error(f"setAuthorizedOperator failed: {e}")
            return False

    def setMintFee(
        self,
        sender: str,
        value: int,
        _mintFee: int,
        _feeCollection: str,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """setMintFee implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _mintFee: uint256 - Contract parameter

            _feeCollection: address - Contract parameter

        """
        try:
            tx = self.contract.setMintFee(
                _mintFee, _feeCollection, sender=sender, value=value
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
            logger.error(f"setMintFee failed: {e}")
            return False

    def setRedemptionBurn(
        self,
        sender: str,
        value: int,
        _burnRedemptionRate: int,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """setRedemptionBurn implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _burnRedemptionRate: uint256 - Contract parameter

        """
        try:
            tx = self.contract.setRedemptionBurn(
                _burnRedemptionRate, sender=sender, value=value
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
            logger.error(f"setRedemptionBurn failed: {e}")
            return False

    def setRequireOperators(
        self,
        sender: str,
        value: int,
        _required: bool,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """setRequireOperators implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _required: bool - Contract parameter

        """
        try:
            tx = self.contract.setRequireOperators(
                _required, sender=sender, value=value
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
            logger.error(f"setRequireOperators failed: {e}")
            return False

    def setReturnGroupCirclesToSender(
        self,
        sender: str,
        value: int,
        _returnGroupCircles: bool,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """setReturnGroupCirclesToSender implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _returnGroupCircles: bool - Contract parameter

        """
        try:
            tx = self.contract.setReturnGroupCirclesToSender(
                _returnGroupCircles, sender=sender, value=value
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
            logger.error(f"setReturnGroupCirclesToSender failed: {e}")
            return False

    def setService(
        self,
        sender: str,
        value: int,
        _service: str,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """setService implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _service: address - Contract parameter

        """
        try:
            tx = self.contract.setService(_service, sender=sender, value=value)
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
            logger.error(f"setService failed: {e}")
            return False

    def setup(
        self,
        sender: str,
        value: int,
        _owner: str,
        _mintFee: int,
        _feeCollection: str,
        _redemptionBurnRatio: int,
        _operators: List[str],
        _name: str,
        _symbol: str,
        _metadataDigest: bytes,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """setup implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _owner: address - Contract parameter

            _mintFee: uint256 - Contract parameter

            _feeCollection: address - Contract parameter

            _redemptionBurnRatio: uint256 - Contract parameter

            _operators: address[] - Contract parameter

            _name: string - Contract parameter

            _symbol: string - Contract parameter

            _metadataDigest: bytes32 - Contract parameter

        """
        try:
            tx = self.contract.setup(
                _owner,
                _mintFee,
                _feeCollection,
                _redemptionBurnRatio,
                _operators,
                _name,
                _symbol,
                _metadataDigest,
                sender=sender,
                value=value,
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
            logger.error(f"setup failed: {e}")
            return False

    def setup(
        self,
        sender: str,
        value: int,
        _owner: str,
        _service: str,
        _mintFee: int,
        _feeCollection: str,
        _redemptionBurnRate: int,
        _operators: List[str],
        _name: str,
        _symbol: str,
        _metadataDigest: bytes,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """setup implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _owner: address - Contract parameter

            _service: address - Contract parameter

            _mintFee: uint256 - Contract parameter

            _feeCollection: address - Contract parameter

            _redemptionBurnRate: uint256 - Contract parameter

            _operators: address[] - Contract parameter

            _name: string - Contract parameter

            _symbol: string - Contract parameter

            _metadataDigest: bytes32 - Contract parameter

        """
        try:
            tx = self.contract.setup(
                _owner,
                _service,
                _mintFee,
                _feeCollection,
                _redemptionBurnRate,
                _operators,
                _name,
                _symbol,
                _metadataDigest,
                sender=sender,
                value=value,
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
            logger.error(f"setup failed: {e}")
            return False

    def supportsInterface(self, interfaceId: Any) -> bool:
        """supportsInterface implementation

        Args:
            interfaceId: bytes4 - Contract parameter

        """
        try:
            return self.contract.supportsInterface(interfaceId)
        except Exception as e:
            logger.error(f"supportsInterface failed: {e}")
            return None

    def trust(
        self,
        sender: str,
        value: int,
        _trustReceiver: str,
        _expiry: int,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """trust implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _trustReceiver: address - Contract parameter

            _expiry: uint96 - Contract parameter

        """
        try:
            tx = self.contract.trust(
                _trustReceiver, _expiry, sender=sender, value=value
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
            logger.error(f"trust failed: {e}")
            return False

    def trustBatch(
        self,
        sender: str,
        value: int,
        _backers: List[str],
        _expiry: int,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """trustBatch implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _backers: address[] - Contract parameter

            _expiry: uint96 - Contract parameter

        """
        try:
            tx = self.contract.trustBatch(_backers, _expiry, sender=sender, value=value)
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
            logger.error(f"trustBatch failed: {e}")
            return False

    def updateMetadataDigest(
        self,
        sender: str,
        value: int,
        _metadataDigest: bytes,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """updateMetadataDigest implementation

        Args:
            sender: Address initiating the transaction
            value: Value in wei to send with transaction

            _metadataDigest: bytes32 - Contract parameter

        """
        try:
            tx = self.contract.updateMetadataDigest(
                _metadataDigest, sender=sender, value=value
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
            logger.error(f"updateMetadataDigest failed: {e}")
            return False
