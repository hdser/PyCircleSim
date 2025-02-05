from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from ape import Contract, chain
from src.framework.data import BaseDataCollector
from src.framework.logging import get_logger
import logging
import json

logger = get_logger(__name__)


class CirclesDemurrageERC20Client:
    """Generic client interface for CirclesDemurrageERC20 contract"""

    def __init__(
        self,
        address: str,
        abi_path: str,
        gas_limits: Optional[Dict[str, int]] = None,
        data_collector: Optional["BaseDataCollector"] = None,
    ):
        self.address = address
        self.abi_path = abi_path
        self.data_collector = data_collector
        self.gas_limits = gas_limits or {}
        self._contracts: Dict[str, Contract] = {}

        # Load ABI from file
        try:
            with open(abi_path) as f:
                self.abi = json.load(f)
            logger.debug(
                f"Successfully loaded CirclesDemurrageERC20 ABI from {abi_path}"
            )
        except Exception as e:
            logger.error(f"Failed to load ABI from {abi_path}: {e}")
            raise

    def get_contract(self, contract_address: str) -> Optional[Contract]:
        """Get or create Contract instance for given address"""
        if contract_address not in self._contracts:
            try:
                logger.debug(f"Creating new contract instance for {contract_address}")
                self._contracts[contract_address] = Contract(
                    address=contract_address, abi=self.abi
                )
                logger.debug(
                    f"Successfully created contract instance for {contract_address}"
                )
            except Exception as e:
                logger.error(f"Failed to create contract for {contract_address}: {e}")
                return None
        return self._contracts[contract_address]

    def DOMAIN_SEPARATOR(
        self,
        contract_address: str,
    ) -> bytes:
        """DOMAIN_SEPARATOR implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.DOMAIN_SEPARATOR()
        except Exception as e:
            logger.error(f"DOMAIN_SEPARATOR failed: {e}")
            return None

    def allowance(self, contract_address: str, _owner: str, _spender: str) -> int:
        """allowance implementation
        Args:
            contract_address: Contract address to call

            _owner: address - Contract parameter

            _spender: address - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.allowance(_owner, _spender)
        except Exception as e:
            logger.error(f"allowance failed: {e}")
            return None

    def approve(
        self,
        contract_address: str,
        _spender: str,
        _amount: int,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """approve implementation
        Args:
            contract_address: Contract address to call

            _spender: address - Contract parameter

            _amount: uint256 - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.approve(_spender, _amount, sender=sender, value=value)
            success = bool(tx and tx.status == 1)

            if success:
                if self.data_collector:
                    self.data_collector.record_transaction_events(tx)
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success

        except Exception as e:
            logger.error(f"approve failed: {e}")
            return False

    def avatar(
        self,
        contract_address: str,
    ) -> str:
        """avatar implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.avatar()
        except Exception as e:
            logger.error(f"avatar failed: {e}")
            return None

    def balanceOf(self, contract_address: str, _account: str) -> int:
        """balanceOf implementation
        Args:
            contract_address: Contract address to call

            _account: address - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.balanceOf(_account)
        except Exception as e:
            logger.error(f"balanceOf failed: {e}")
            return None

    def balanceOfOnDay(
        self, contract_address: str, _account: str, _day: int
    ) -> Tuple[int, int]:
        """balanceOfOnDay implementation
        Args:
            contract_address: Contract address to call

            _account: address - Contract parameter

            _day: uint64 - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.balanceOfOnDay(_account, _day)
        except Exception as e:
            logger.error(f"balanceOfOnDay failed: {e}")
            return None

    def circlesIdentifier(
        self,
        contract_address: str,
    ) -> int:
        """circlesIdentifier implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.circlesIdentifier()
        except Exception as e:
            logger.error(f"circlesIdentifier failed: {e}")
            return None

    def convertBatchDemurrageToInflationaryValues(
        self, contract_address: str, _demurrageValues: List[int], _dayUpdated: int
    ) -> List[int]:
        """convertBatchDemurrageToInflationaryValues implementation
        Args:
            contract_address: Contract address to call

            _demurrageValues: uint256[] - Contract parameter

            _dayUpdated: uint64 - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.convertBatchDemurrageToInflationaryValues(
                _demurrageValues, _dayUpdated
            )
        except Exception as e:
            logger.error(f"convertBatchDemurrageToInflationaryValues failed: {e}")
            return None

    def convertBatchInflationaryToDemurrageValues(
        self, contract_address: str, _inflationaryValues: List[int], _day: int
    ) -> List[int]:
        """convertBatchInflationaryToDemurrageValues implementation
        Args:
            contract_address: Contract address to call

            _inflationaryValues: uint256[] - Contract parameter

            _day: uint64 - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.convertBatchInflationaryToDemurrageValues(
                _inflationaryValues, _day
            )
        except Exception as e:
            logger.error(f"convertBatchInflationaryToDemurrageValues failed: {e}")
            return None

    def convertDemurrageToInflationaryValue(
        self, contract_address: str, _demurrageValue: int, _dayUpdated: int
    ) -> int:
        """convertDemurrageToInflationaryValue implementation
        Args:
            contract_address: Contract address to call

            _demurrageValue: uint256 - Contract parameter

            _dayUpdated: uint64 - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.convertDemurrageToInflationaryValue(
                _demurrageValue, _dayUpdated
            )
        except Exception as e:
            logger.error(f"convertDemurrageToInflationaryValue failed: {e}")
            return None

    def convertInflationaryToDemurrageValue(
        self, contract_address: str, _inflationaryValue: int, _day: int
    ) -> int:
        """convertInflationaryToDemurrageValue implementation
        Args:
            contract_address: Contract address to call

            _inflationaryValue: uint256 - Contract parameter

            _day: uint64 - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.convertInflationaryToDemurrageValue(
                _inflationaryValue, _day
            )
        except Exception as e:
            logger.error(f"convertInflationaryToDemurrageValue failed: {e}")
            return None

    def day(self, contract_address: str, _timestamp: int) -> int:
        """day implementation
        Args:
            contract_address: Contract address to call

            _timestamp: uint256 - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.day(_timestamp)
        except Exception as e:
            logger.error(f"day failed: {e}")
            return None

    def decimals(
        self,
        contract_address: str,
    ) -> Any:
        """decimals implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.decimals()
        except Exception as e:
            logger.error(f"decimals failed: {e}")
            return None

    def decreaseAllowance(
        self,
        contract_address: str,
        _spender: str,
        _subtractedValue: int,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """decreaseAllowance implementation
        Args:
            contract_address: Contract address to call

            _spender: address - Contract parameter

            _subtractedValue: uint256 - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.decreaseAllowance(
                _spender, _subtractedValue, sender=sender, value=value
            )
            success = bool(tx and tx.status == 1)

            if success:
                if self.data_collector:
                    self.data_collector.record_transaction_events(tx)
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success

        except Exception as e:
            logger.error(f"decreaseAllowance failed: {e}")
            return False

    def discountedBalances(self, contract_address: str, param0: str) -> Tuple[Any, int]:
        """discountedBalances implementation
        Args:
            contract_address: Contract address to call

            : address - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.discountedBalances(param0)
        except Exception as e:
            logger.error(f"discountedBalances failed: {e}")
            return None

    def eip712Domain(
        self,
        contract_address: str,
    ) -> Tuple[Any, str, str, int, str, bytes, List[int]]:
        """eip712Domain implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.eip712Domain()
        except Exception as e:
            logger.error(f"eip712Domain failed: {e}")
            return None

    def hub(
        self,
        contract_address: str,
    ) -> str:
        """hub implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.hub()
        except Exception as e:
            logger.error(f"hub failed: {e}")
            return None

    def increaseAllowance(
        self,
        contract_address: str,
        _spender: str,
        _addedValue: int,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """increaseAllowance implementation
        Args:
            contract_address: Contract address to call

            _spender: address - Contract parameter

            _addedValue: uint256 - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.increaseAllowance(
                _spender, _addedValue, sender=sender, value=value
            )
            success = bool(tx and tx.status == 1)

            if success:
                if self.data_collector:
                    self.data_collector.record_transaction_events(tx)
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success

        except Exception as e:
            logger.error(f"increaseAllowance failed: {e}")
            return False

    def inflationDayZero(
        self,
        contract_address: str,
    ) -> int:
        """inflationDayZero implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.inflationDayZero()
        except Exception as e:
            logger.error(f"inflationDayZero failed: {e}")
            return None

    def name(
        self,
        contract_address: str,
    ) -> str:
        """name implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.name()
        except Exception as e:
            logger.error(f"name failed: {e}")
            return None

    def nameRegistry(
        self,
        contract_address: str,
    ) -> str:
        """nameRegistry implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.nameRegistry()
        except Exception as e:
            logger.error(f"nameRegistry failed: {e}")
            return None

    def nonces(self, contract_address: str, _owner: str) -> int:
        """nonces implementation
        Args:
            contract_address: Contract address to call

            _owner: address - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.nonces(_owner)
        except Exception as e:
            logger.error(f"nonces failed: {e}")
            return None

    def onERC1155BatchReceived(
        self,
        contract_address: str,
        param0: str,
        param1: str,
        param2: List[int],
        param3: List[int],
        param4: bytes,
    ) -> Any:
        """onERC1155BatchReceived implementation
        Args:
            contract_address: Contract address to call

            : address - Contract parameter

            : address - Contract parameter

            : uint256[] - Contract parameter

            : uint256[] - Contract parameter

            : bytes - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.onERC1155BatchReceived(
                param0, param1, param2, param3, param4
            )
        except Exception as e:
            logger.error(f"onERC1155BatchReceived failed: {e}")
            return None

    def onERC1155Received(
        self,
        contract_address: str,
        param0: str,
        _from: str,
        _id: int,
        _amount: int,
        param4: bytes,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """onERC1155Received implementation
        Args:
            contract_address: Contract address to call

            : address - Contract parameter

            _from: address - Contract parameter

            _id: uint256 - Contract parameter

            _amount: uint256 - Contract parameter

            : bytes - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.onERC1155Received(
                param0, _from, _id, _amount, param4, sender=sender, value=value
            )
            success = bool(tx and tx.status == 1)

            if success:
                if self.data_collector:
                    self.data_collector.record_transaction_events(tx)
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success

        except Exception as e:
            logger.error(f"onERC1155Received failed: {e}")
            return False

    def permit(
        self,
        contract_address: str,
        _owner: str,
        _spender: str,
        _value: int,
        _deadline: int,
        _v: Any,
        _r: bytes,
        _s: bytes,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """permit implementation
        Args:
            contract_address: Contract address to call

            _owner: address - Contract parameter

            _spender: address - Contract parameter

            _value: uint256 - Contract parameter

            _deadline: uint256 - Contract parameter

            _v: uint8 - Contract parameter

            _r: bytes32 - Contract parameter

            _s: bytes32 - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.permit(
                _owner,
                _spender,
                _value,
                _deadline,
                _v,
                _r,
                _s,
                sender=sender,
                value=value,
            )
            success = bool(tx and tx.status == 1)

            if success:
                if self.data_collector:
                    self.data_collector.record_transaction_events(tx)
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success

        except Exception as e:
            logger.error(f"permit failed: {e}")
            return False

    def setup(
        self,
        contract_address: str,
        _hub: str,
        _nameRegistry: str,
        _avatar: str,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """setup implementation
        Args:
            contract_address: Contract address to call

            _hub: address - Contract parameter

            _nameRegistry: address - Contract parameter

            _avatar: address - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.setup(
                _hub, _nameRegistry, _avatar, sender=sender, value=value
            )
            success = bool(tx and tx.status == 1)

            if success:
                if self.data_collector:
                    self.data_collector.record_transaction_events(tx)
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success

        except Exception as e:
            logger.error(f"setup failed: {e}")
            return False

    def supportsInterface(self, contract_address: str, interfaceId: Any) -> bool:
        """supportsInterface implementation
        Args:
            contract_address: Contract address to call

            interfaceId: bytes4 - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.supportsInterface(interfaceId)
        except Exception as e:
            logger.error(f"supportsInterface failed: {e}")
            return None

    def symbol(
        self,
        contract_address: str,
    ) -> str:
        """symbol implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.symbol()
        except Exception as e:
            logger.error(f"symbol failed: {e}")
            return None

    def toTokenId(self, contract_address: str, _avatar: str) -> int:
        """toTokenId implementation
        Args:
            contract_address: Contract address to call

            _avatar: address - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.toTokenId(_avatar)
        except Exception as e:
            logger.error(f"toTokenId failed: {e}")
            return None

    def totalSupply(
        self,
        contract_address: str,
    ) -> int:
        """totalSupply implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.totalSupply()
        except Exception as e:
            logger.error(f"totalSupply failed: {e}")
            return None

    def transfer(
        self,
        contract_address: str,
        _to: str,
        _amount: int,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """transfer implementation
        Args:
            contract_address: Contract address to call

            _to: address - Contract parameter

            _amount: uint256 - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.transfer(_to, _amount, sender=sender, value=value)
            success = bool(tx and tx.status == 1)

            if success:
                if self.data_collector:
                    self.data_collector.record_transaction_events(tx)
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success

        except Exception as e:
            logger.error(f"transfer failed: {e}")
            return False

    def transferFrom(
        self,
        contract_address: str,
        _from: str,
        _to: str,
        _amount: int,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """transferFrom implementation
        Args:
            contract_address: Contract address to call

            _from: address - Contract parameter

            _to: address - Contract parameter

            _amount: uint256 - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.transferFrom(_from, _to, _amount, sender=sender, value=value)
            success = bool(tx and tx.status == 1)

            if success:
                if self.data_collector:
                    self.data_collector.record_transaction_events(tx)
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success

        except Exception as e:
            logger.error(f"transferFrom failed: {e}")
            return False

    def unwrap(
        self,
        contract_address: str,
        _amount: int,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """unwrap implementation
        Args:
            contract_address: Contract address to call

            _amount: uint256 - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.unwrap(_amount, sender=sender, value=value)
            success = bool(tx and tx.status == 1)

            if success:
                if self.data_collector:
                    self.data_collector.record_transaction_events(tx)
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success

        except Exception as e:
            logger.error(f"unwrap failed: {e}")
            return False
