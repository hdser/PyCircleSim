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


class BalancerV2LBPClient:
    """Generic client interface for BalancerV2LBP contract"""

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
            logger.debug(f"Successfully loaded BalancerV2LBP ABI from {abi_path}")
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

    def allowance(self, contract_address: str, owner: str, spender: str) -> int:
        """allowance implementation
        Args:
            contract_address: Contract address to call

            owner: address - Contract parameter

            spender: address - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.allowance(owner, spender)
        except Exception as e:
            logger.error(f"allowance failed: {e}")
            return None

    def approve(
        self,
        contract_address: str,
        spender: str,
        amount: int,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """approve implementation
        Args:
            contract_address: Contract address to call

            spender: address - Contract parameter

            amount: uint256 - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.approve(spender, amount, sender=sender, value=value)
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

    def balanceOf(self, contract_address: str, account: str) -> int:
        """balanceOf implementation
        Args:
            contract_address: Contract address to call

            account: address - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.balanceOf(account)
        except Exception as e:
            logger.error(f"balanceOf failed: {e}")
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
        spender: str,
        amount: int,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """decreaseAllowance implementation
        Args:
            contract_address: Contract address to call

            spender: address - Contract parameter

            amount: uint256 - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.decreaseAllowance(spender, amount, sender=sender, value=value)
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

    def getActionId(self, contract_address: str, selector: Any) -> bytes:
        """getActionId implementation
        Args:
            contract_address: Contract address to call

            selector: bytes4 - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.getActionId(selector)
        except Exception as e:
            logger.error(f"getActionId failed: {e}")
            return None

    def getAuthorizer(
        self,
        contract_address: str,
    ) -> str:
        """getAuthorizer implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.getAuthorizer()
        except Exception as e:
            logger.error(f"getAuthorizer failed: {e}")
            return None

    def getGradualWeightUpdateParams(
        self,
        contract_address: str,
    ) -> Tuple[int, int, List[int]]:
        """getGradualWeightUpdateParams implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.getGradualWeightUpdateParams()
        except Exception as e:
            logger.error(f"getGradualWeightUpdateParams failed: {e}")
            return None

    def getInvariant(
        self,
        contract_address: str,
    ) -> int:
        """getInvariant implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.getInvariant()
        except Exception as e:
            logger.error(f"getInvariant failed: {e}")
            return None

    def getLastInvariant(
        self,
        contract_address: str,
    ) -> int:
        """getLastInvariant implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.getLastInvariant()
        except Exception as e:
            logger.error(f"getLastInvariant failed: {e}")
            return None

    def getNormalizedWeights(
        self,
        contract_address: str,
    ) -> List[int]:
        """getNormalizedWeights implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.getNormalizedWeights()
        except Exception as e:
            logger.error(f"getNormalizedWeights failed: {e}")
            return None

    def getOwner(
        self,
        contract_address: str,
    ) -> str:
        """getOwner implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.getOwner()
        except Exception as e:
            logger.error(f"getOwner failed: {e}")
            return None

    def getPausedState(
        self,
        contract_address: str,
    ) -> Tuple[bool, int, int]:
        """getPausedState implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.getPausedState()
        except Exception as e:
            logger.error(f"getPausedState failed: {e}")
            return None

    def getPoolId(
        self,
        contract_address: str,
    ) -> bytes:
        """getPoolId implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.getPoolId()
        except Exception as e:
            logger.error(f"getPoolId failed: {e}")
            return None

    def getRate(
        self,
        contract_address: str,
    ) -> int:
        """getRate implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.getRate()
        except Exception as e:
            logger.error(f"getRate failed: {e}")
            return None

    def getScalingFactors(
        self,
        contract_address: str,
    ) -> List[int]:
        """getScalingFactors implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.getScalingFactors()
        except Exception as e:
            logger.error(f"getScalingFactors failed: {e}")
            return None

    def getSwapEnabled(
        self,
        contract_address: str,
    ) -> bool:
        """getSwapEnabled implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.getSwapEnabled()
        except Exception as e:
            logger.error(f"getSwapEnabled failed: {e}")
            return None

    def getSwapFeePercentage(
        self,
        contract_address: str,
    ) -> int:
        """getSwapFeePercentage implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.getSwapFeePercentage()
        except Exception as e:
            logger.error(f"getSwapFeePercentage failed: {e}")
            return None

    def getVault(
        self,
        contract_address: str,
    ) -> str:
        """getVault implementation
        Args:
            contract_address: Contract address to call

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.getVault()
        except Exception as e:
            logger.error(f"getVault failed: {e}")
            return None

    def increaseAllowance(
        self,
        contract_address: str,
        spender: str,
        addedValue: int,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """increaseAllowance implementation
        Args:
            contract_address: Contract address to call

            spender: address - Contract parameter

            addedValue: uint256 - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.increaseAllowance(
                spender, addedValue, sender=sender, value=value
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

    def nonces(self, contract_address: str, owner: str) -> int:
        """nonces implementation
        Args:
            contract_address: Contract address to call

            owner: address - Contract parameter

        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return None
            return contract.nonces(owner)
        except Exception as e:
            logger.error(f"nonces failed: {e}")
            return None

    def onExitPool(
        self,
        contract_address: str,
        poolId: bytes,
        sender_account: str,
        recipient: str,
        balances: List[int],
        lastChangeBlock: int,
        param5: int,
        userData: bytes,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """onExitPool implementation
        Args:
            contract_address: Contract address to call

            poolId: bytes32 - Contract parameter

            sender: address - Contract parameter

            recipient: address - Contract parameter

            balances: uint256[] - Contract parameter

            lastChangeBlock: uint256 - Contract parameter

            : uint256 - Contract parameter

            userData: bytes - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.onExitPool(
                poolId,
                sender_account,
                recipient,
                balances,
                lastChangeBlock,
                param5,
                userData,
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
            logger.error(f"onExitPool failed: {e}")
            return False

    def onJoinPool(
        self,
        contract_address: str,
        poolId: bytes,
        sender_account: str,
        recipient: str,
        balances: List[int],
        lastChangeBlock: int,
        param5: int,
        userData: bytes,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """onJoinPool implementation
        Args:
            contract_address: Contract address to call

            poolId: bytes32 - Contract parameter

            sender: address - Contract parameter

            recipient: address - Contract parameter

            balances: uint256[] - Contract parameter

            lastChangeBlock: uint256 - Contract parameter

            : uint256 - Contract parameter

            userData: bytes - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.onJoinPool(
                poolId,
                sender_account,
                recipient,
                balances,
                lastChangeBlock,
                param5,
                userData,
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
            logger.error(f"onJoinPool failed: {e}")
            return False

    def onSwap(
        self,
        contract_address: str,
        request: Any,
        balanceTokenIn: int,
        balanceTokenOut: int,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """onSwap implementation
        Args:
            contract_address: Contract address to call

            request: tuple - Contract parameter

            balanceTokenIn: uint256 - Contract parameter

            balanceTokenOut: uint256 - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.onSwap(
                request, balanceTokenIn, balanceTokenOut, sender=sender, value=value
            )
            success = bool(tx and tx.status == 1)

            if success:
                if self.data_collector:
                    self.data_collector.record_transaction_events(tx)
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success

        except Exception as e:
            logger.error(f"onSwap failed: {e}")
            return False

    def permit(
        self,
        contract_address: str,
        owner: str,
        spender: str,
        value_amount: int,
        deadline: int,
        v: Any,
        r: bytes,
        s: bytes,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """permit implementation
        Args:
            contract_address: Contract address to call

            owner: address - Contract parameter

            spender: address - Contract parameter

            value: uint256 - Contract parameter

            deadline: uint256 - Contract parameter

            v: uint8 - Contract parameter

            r: bytes32 - Contract parameter

            s: bytes32 - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.permit(
                owner,
                spender,
                value_amount,
                deadline,
                v,
                r,
                s,
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

    def queryExit(
        self,
        contract_address: str,
        poolId: bytes,
        sender_account: str,
        recipient: str,
        balances: List[int],
        lastChangeBlock: int,
        protocolSwapFeePercentage: int,
        userData: bytes,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """queryExit implementation
        Args:
            contract_address: Contract address to call

            poolId: bytes32 - Contract parameter

            sender: address - Contract parameter

            recipient: address - Contract parameter

            balances: uint256[] - Contract parameter

            lastChangeBlock: uint256 - Contract parameter

            protocolSwapFeePercentage: uint256 - Contract parameter

            userData: bytes - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.queryExit(
                poolId,
                sender_account,
                recipient,
                balances,
                lastChangeBlock,
                protocolSwapFeePercentage,
                userData,
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
            logger.error(f"queryExit failed: {e}")
            return False

    def queryJoin(
        self,
        contract_address: str,
        poolId: bytes,
        sender_account: str,
        recipient: str,
        balances: List[int],
        lastChangeBlock: int,
        protocolSwapFeePercentage: int,
        userData: bytes,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """queryJoin implementation
        Args:
            contract_address: Contract address to call

            poolId: bytes32 - Contract parameter

            sender: address - Contract parameter

            recipient: address - Contract parameter

            balances: uint256[] - Contract parameter

            lastChangeBlock: uint256 - Contract parameter

            protocolSwapFeePercentage: uint256 - Contract parameter

            userData: bytes - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.queryJoin(
                poolId,
                sender_account,
                recipient,
                balances,
                lastChangeBlock,
                protocolSwapFeePercentage,
                userData,
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
            logger.error(f"queryJoin failed: {e}")
            return False

    def setAssetManagerPoolConfig(
        self,
        contract_address: str,
        token: str,
        poolConfig: bytes,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """setAssetManagerPoolConfig implementation
        Args:
            contract_address: Contract address to call

            token: address - Contract parameter

            poolConfig: bytes - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.setAssetManagerPoolConfig(
                token, poolConfig, sender=sender, value=value
            )
            success = bool(tx and tx.status == 1)

            if success:
                if self.data_collector:
                    self.data_collector.record_transaction_events(tx)
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success

        except Exception as e:
            logger.error(f"setAssetManagerPoolConfig failed: {e}")
            return False

    def setPaused(
        self,
        contract_address: str,
        paused: bool,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """setPaused implementation
        Args:
            contract_address: Contract address to call

            paused: bool - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.setPaused(paused, sender=sender, value=value)
            success = bool(tx and tx.status == 1)

            if success:
                if self.data_collector:
                    self.data_collector.record_transaction_events(tx)
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success

        except Exception as e:
            logger.error(f"setPaused failed: {e}")
            return False

    def setSwapEnabled(
        self,
        contract_address: str,
        swapEnabled: bool,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """setSwapEnabled implementation
        Args:
            contract_address: Contract address to call

            swapEnabled: bool - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.setSwapEnabled(swapEnabled, sender=sender, value=value)
            success = bool(tx and tx.status == 1)

            if success:
                if self.data_collector:
                    self.data_collector.record_transaction_events(tx)
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success

        except Exception as e:
            logger.error(f"setSwapEnabled failed: {e}")
            return False

    def setSwapFeePercentage(
        self,
        contract_address: str,
        swapFeePercentage: int,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """setSwapFeePercentage implementation
        Args:
            contract_address: Contract address to call

            swapFeePercentage: uint256 - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.setSwapFeePercentage(
                swapFeePercentage, sender=sender, value=value
            )
            success = bool(tx and tx.status == 1)

            if success:
                if self.data_collector:
                    self.data_collector.record_transaction_events(tx)
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success

        except Exception as e:
            logger.error(f"setSwapFeePercentage failed: {e}")
            return False

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
        recipient: str,
        amount: int,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """transfer implementation
        Args:
            contract_address: Contract address to call

            recipient: address - Contract parameter

            amount: uint256 - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.transfer(recipient, amount, sender=sender, value=value)
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
        sender_account: str,
        recipient: str,
        amount: int,
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """transferFrom implementation
        Args:
            contract_address: Contract address to call

            sender: address - Contract parameter

            recipient: address - Contract parameter

            amount: uint256 - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.transferFrom(
                sender_account, recipient, amount, sender=sender, value=value
            )
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

    def updateWeightsGradually(
        self,
        contract_address: str,
        startTime: int,
        endTime: int,
        endWeights: List[int],
        sender: str,
        value: int = 0,
        context: Optional["SimulationContext"] = None,
    ) -> bool:
        """updateWeightsGradually implementation
        Args:
            contract_address: Contract address to call

            startTime: uint256 - Contract parameter

            endTime: uint256 - Contract parameter

            endWeights: uint256[] - Contract parameter

            sender: Address initiating the transaction
            value: Value in wei to send with transaction
        """
        try:
            contract = self.get_contract(contract_address)
            if not contract:
                return False

            tx = contract.updateWeightsGradually(
                startTime, endTime, endWeights, sender=sender, value=value
            )
            success = bool(tx and tx.status == 1)

            if success:
                if self.data_collector:
                    self.data_collector.record_transaction_events(tx)
                if context and context.simulation:
                    context.simulation.update_state_from_transaction(tx, context)
            return success

        except Exception as e:
            logger.error(f"updateWeightsGradually failed: {e}")
            return False
