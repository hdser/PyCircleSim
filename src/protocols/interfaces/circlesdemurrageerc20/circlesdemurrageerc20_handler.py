import random
import importlib
from typing import Dict, Any, Optional
from eth_pydantic_types import HexBytes
from src.framework.core.context import SimulationContext
from src.protocols.interfaces.circlesdemurrageerc20.circlesdemurrageerc20_client import (
    CirclesDemurrageERC20Client,
)


class ApproveBaseHandler:
    """Base handler class for approve action."""

    def __init__(
        self,
        client: CirclesDemurrageERC20Client,
        chain,
        logger,
        strategy_name: str = "basic",
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

        try:
            module_path = f"src.protocols.handler_strategies.{client.__class__.__name__.lower().replace('client', '')}.{strategy_name}_strategies"
            strategy_module = importlib.import_module(module_path)
            strategy_class = getattr(
                strategy_module,
                f"{self.__class__.__name__.replace('Handler', 'Strategy').replace('Base', '')}",
            )
            self.strategy = strategy_class()
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to load strategy {strategy_name}: {e}")
            self.strategy = self

    def get_params(self, context: SimulationContext) -> Dict[str, Any]:
        """Default parameter generation if no strategy is loaded"""
        tx_sender = (
            next(iter(context.agent.accounts.keys()))
            if context.agent.accounts
            else None
        )

        params = {
            "sender": tx_sender,
            "value": 0,
            "contract_address": None,
            "_spender": None,  # type: address
            "_amount": None,  # type: uint256
        }
        return params

    def execute(
        self, context: SimulationContext, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Execute the contract function with proper parameter handling"""
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False

            function_args = {
                "contract_address": execution_params.get("contract_address"),
                "_spender": execution_params.get("_spender"),
                "_amount": execution_params.get("_amount"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.approve(**function_args)

        except Exception as e:
            self.logger.error(f"approve action failed: {e}", exc_info=True)
            return False


class ApproveHandler(ApproveBaseHandler):
    """Concrete handler implementation"""

    pass


class DecreaseallowanceBaseHandler:
    """Base handler class for decreaseAllowance action."""

    def __init__(
        self,
        client: CirclesDemurrageERC20Client,
        chain,
        logger,
        strategy_name: str = "basic",
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

        try:
            module_path = f"src.protocols.handler_strategies.{client.__class__.__name__.lower().replace('client', '')}.{strategy_name}_strategies"
            strategy_module = importlib.import_module(module_path)
            strategy_class = getattr(
                strategy_module,
                f"{self.__class__.__name__.replace('Handler', 'Strategy').replace('Base', '')}",
            )
            self.strategy = strategy_class()
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to load strategy {strategy_name}: {e}")
            self.strategy = self

    def get_params(self, context: SimulationContext) -> Dict[str, Any]:
        """Default parameter generation if no strategy is loaded"""
        tx_sender = (
            next(iter(context.agent.accounts.keys()))
            if context.agent.accounts
            else None
        )

        params = {
            "sender": tx_sender,
            "value": 0,
            "contract_address": None,
            "_spender": None,  # type: address
            "_subtractedValue": None,  # type: uint256
        }
        return params

    def execute(
        self, context: SimulationContext, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Execute the contract function with proper parameter handling"""
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False

            function_args = {
                "contract_address": execution_params.get("contract_address"),
                "_spender": execution_params.get("_spender"),
                "_subtractedValue": execution_params.get("_subtractedValue"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.decreaseAllowance(**function_args)

        except Exception as e:
            self.logger.error(f"decreaseAllowance action failed: {e}", exc_info=True)
            return False


class DecreaseallowanceHandler(DecreaseallowanceBaseHandler):
    """Concrete handler implementation"""

    pass


class IncreaseallowanceBaseHandler:
    """Base handler class for increaseAllowance action."""

    def __init__(
        self,
        client: CirclesDemurrageERC20Client,
        chain,
        logger,
        strategy_name: str = "basic",
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

        try:
            module_path = f"src.protocols.handler_strategies.{client.__class__.__name__.lower().replace('client', '')}.{strategy_name}_strategies"
            strategy_module = importlib.import_module(module_path)
            strategy_class = getattr(
                strategy_module,
                f"{self.__class__.__name__.replace('Handler', 'Strategy').replace('Base', '')}",
            )
            self.strategy = strategy_class()
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to load strategy {strategy_name}: {e}")
            self.strategy = self

    def get_params(self, context: SimulationContext) -> Dict[str, Any]:
        """Default parameter generation if no strategy is loaded"""
        tx_sender = (
            next(iter(context.agent.accounts.keys()))
            if context.agent.accounts
            else None
        )

        params = {
            "sender": tx_sender,
            "value": 0,
            "contract_address": None,
            "_spender": None,  # type: address
            "_addedValue": None,  # type: uint256
        }
        return params

    def execute(
        self, context: SimulationContext, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Execute the contract function with proper parameter handling"""
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False

            function_args = {
                "contract_address": execution_params.get("contract_address"),
                "_spender": execution_params.get("_spender"),
                "_addedValue": execution_params.get("_addedValue"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.increaseAllowance(**function_args)

        except Exception as e:
            self.logger.error(f"increaseAllowance action failed: {e}", exc_info=True)
            return False


class IncreaseallowanceHandler(IncreaseallowanceBaseHandler):
    """Concrete handler implementation"""

    pass


class Onerc1155receivedBaseHandler:
    """Base handler class for onERC1155Received action."""

    def __init__(
        self,
        client: CirclesDemurrageERC20Client,
        chain,
        logger,
        strategy_name: str = "basic",
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

        try:
            module_path = f"src.protocols.handler_strategies.{client.__class__.__name__.lower().replace('client', '')}.{strategy_name}_strategies"
            strategy_module = importlib.import_module(module_path)
            strategy_class = getattr(
                strategy_module,
                f"{self.__class__.__name__.replace('Handler', 'Strategy').replace('Base', '')}",
            )
            self.strategy = strategy_class()
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to load strategy {strategy_name}: {e}")
            self.strategy = self

    def get_params(self, context: SimulationContext) -> Dict[str, Any]:
        """Default parameter generation if no strategy is loaded"""
        tx_sender = (
            next(iter(context.agent.accounts.keys()))
            if context.agent.accounts
            else None
        )

        params = {
            "sender": tx_sender,
            "value": 0,
            "contract_address": None,
            "": None,  # type: address
            "_from": None,  # type: address
            "_id": None,  # type: uint256
            "_amount": None,  # type: uint256
            "": None,  # type: bytes
        }
        return params

    def execute(
        self, context: SimulationContext, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Execute the contract function with proper parameter handling"""
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False

            function_args = {
                "contract_address": execution_params.get("contract_address"),
                "": execution_params.get(""),
                "_from": execution_params.get("_from"),
                "_id": execution_params.get("_id"),
                "_amount": execution_params.get("_amount"),
                "": execution_params.get(""),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.onERC1155Received(**function_args)

        except Exception as e:
            self.logger.error(f"onERC1155Received action failed: {e}", exc_info=True)
            return False


class Onerc1155receivedHandler(Onerc1155receivedBaseHandler):
    """Concrete handler implementation"""

    pass


class PermitBaseHandler:
    """Base handler class for permit action."""

    def __init__(
        self,
        client: CirclesDemurrageERC20Client,
        chain,
        logger,
        strategy_name: str = "basic",
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

        try:
            module_path = f"src.protocols.handler_strategies.{client.__class__.__name__.lower().replace('client', '')}.{strategy_name}_strategies"
            strategy_module = importlib.import_module(module_path)
            strategy_class = getattr(
                strategy_module,
                f"{self.__class__.__name__.replace('Handler', 'Strategy').replace('Base', '')}",
            )
            self.strategy = strategy_class()
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to load strategy {strategy_name}: {e}")
            self.strategy = self

    def get_params(self, context: SimulationContext) -> Dict[str, Any]:
        """Default parameter generation if no strategy is loaded"""
        tx_sender = (
            next(iter(context.agent.accounts.keys()))
            if context.agent.accounts
            else None
        )

        params = {
            "sender": tx_sender,
            "value": 0,
            "contract_address": None,
            "_owner": None,  # type: address
            "_spender": None,  # type: address
            "_value": None,  # type: uint256
            "_deadline": None,  # type: uint256
            "_v": None,  # type: uint8
            "_r": None,  # type: bytes32
            "_s": None,  # type: bytes32
        }
        return params

    def execute(
        self, context: SimulationContext, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Execute the contract function with proper parameter handling"""
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False

            function_args = {
                "contract_address": execution_params.get("contract_address"),
                "_owner": execution_params.get("_owner"),
                "_spender": execution_params.get("_spender"),
                "_value": execution_params.get("_value"),
                "_deadline": execution_params.get("_deadline"),
                "_v": execution_params.get("_v"),
                "_r": execution_params.get("_r"),
                "_s": execution_params.get("_s"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.permit(**function_args)

        except Exception as e:
            self.logger.error(f"permit action failed: {e}", exc_info=True)
            return False


class PermitHandler(PermitBaseHandler):
    """Concrete handler implementation"""

    pass


class SetupBaseHandler:
    """Base handler class for setup action."""

    def __init__(
        self,
        client: CirclesDemurrageERC20Client,
        chain,
        logger,
        strategy_name: str = "basic",
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

        try:
            module_path = f"src.protocols.handler_strategies.{client.__class__.__name__.lower().replace('client', '')}.{strategy_name}_strategies"
            strategy_module = importlib.import_module(module_path)
            strategy_class = getattr(
                strategy_module,
                f"{self.__class__.__name__.replace('Handler', 'Strategy').replace('Base', '')}",
            )
            self.strategy = strategy_class()
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to load strategy {strategy_name}: {e}")
            self.strategy = self

    def get_params(self, context: SimulationContext) -> Dict[str, Any]:
        """Default parameter generation if no strategy is loaded"""
        tx_sender = (
            next(iter(context.agent.accounts.keys()))
            if context.agent.accounts
            else None
        )

        params = {
            "sender": tx_sender,
            "value": 0,
            "contract_address": None,
            "_hub": None,  # type: address
            "_nameRegistry": None,  # type: address
            "_avatar": None,  # type: address
        }
        return params

    def execute(
        self, context: SimulationContext, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Execute the contract function with proper parameter handling"""
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False

            function_args = {
                "contract_address": execution_params.get("contract_address"),
                "_hub": execution_params.get("_hub"),
                "_nameRegistry": execution_params.get("_nameRegistry"),
                "_avatar": execution_params.get("_avatar"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.setup(**function_args)

        except Exception as e:
            self.logger.error(f"setup action failed: {e}", exc_info=True)
            return False


class SetupHandler(SetupBaseHandler):
    """Concrete handler implementation"""

    pass


class TransferBaseHandler:
    """Base handler class for transfer action."""

    def __init__(
        self,
        client: CirclesDemurrageERC20Client,
        chain,
        logger,
        strategy_name: str = "basic",
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

        try:
            module_path = f"src.protocols.handler_strategies.{client.__class__.__name__.lower().replace('client', '')}.{strategy_name}_strategies"
            strategy_module = importlib.import_module(module_path)
            strategy_class = getattr(
                strategy_module,
                f"{self.__class__.__name__.replace('Handler', 'Strategy').replace('Base', '')}",
            )
            self.strategy = strategy_class()
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to load strategy {strategy_name}: {e}")
            self.strategy = self

    def get_params(self, context: SimulationContext) -> Dict[str, Any]:
        """Default parameter generation if no strategy is loaded"""
        tx_sender = (
            next(iter(context.agent.accounts.keys()))
            if context.agent.accounts
            else None
        )

        params = {
            "sender": tx_sender,
            "value": 0,
            "contract_address": None,
            "_to": None,  # type: address
            "_amount": None,  # type: uint256
        }
        return params

    def execute(
        self, context: SimulationContext, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Execute the contract function with proper parameter handling"""
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False

            function_args = {
                "contract_address": execution_params.get("contract_address"),
                "_to": execution_params.get("_to"),
                "_amount": execution_params.get("_amount"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.transfer(**function_args)

        except Exception as e:
            self.logger.error(f"transfer action failed: {e}", exc_info=True)
            return False


class TransferHandler(TransferBaseHandler):
    """Concrete handler implementation"""

    pass


class TransferfromBaseHandler:
    """Base handler class for transferFrom action."""

    def __init__(
        self,
        client: CirclesDemurrageERC20Client,
        chain,
        logger,
        strategy_name: str = "basic",
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

        try:
            module_path = f"src.protocols.handler_strategies.{client.__class__.__name__.lower().replace('client', '')}.{strategy_name}_strategies"
            strategy_module = importlib.import_module(module_path)
            strategy_class = getattr(
                strategy_module,
                f"{self.__class__.__name__.replace('Handler', 'Strategy').replace('Base', '')}",
            )
            self.strategy = strategy_class()
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to load strategy {strategy_name}: {e}")
            self.strategy = self

    def get_params(self, context: SimulationContext) -> Dict[str, Any]:
        """Default parameter generation if no strategy is loaded"""
        tx_sender = (
            next(iter(context.agent.accounts.keys()))
            if context.agent.accounts
            else None
        )

        params = {
            "sender": tx_sender,
            "value": 0,
            "contract_address": None,
            "_from": None,  # type: address
            "_to": None,  # type: address
            "_amount": None,  # type: uint256
        }
        return params

    def execute(
        self, context: SimulationContext, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Execute the contract function with proper parameter handling"""
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False

            function_args = {
                "contract_address": execution_params.get("contract_address"),
                "_from": execution_params.get("_from"),
                "_to": execution_params.get("_to"),
                "_amount": execution_params.get("_amount"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.transferFrom(**function_args)

        except Exception as e:
            self.logger.error(f"transferFrom action failed: {e}", exc_info=True)
            return False


class TransferfromHandler(TransferfromBaseHandler):
    """Concrete handler implementation"""

    pass


class UnwrapBaseHandler:
    """Base handler class for unwrap action."""

    def __init__(
        self,
        client: CirclesDemurrageERC20Client,
        chain,
        logger,
        strategy_name: str = "basic",
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

        try:
            module_path = f"src.protocols.handler_strategies.{client.__class__.__name__.lower().replace('client', '')}.{strategy_name}_strategies"
            strategy_module = importlib.import_module(module_path)
            strategy_class = getattr(
                strategy_module,
                f"{self.__class__.__name__.replace('Handler', 'Strategy').replace('Base', '')}",
            )
            self.strategy = strategy_class()
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to load strategy {strategy_name}: {e}")
            self.strategy = self

    def get_params(self, context: SimulationContext) -> Dict[str, Any]:
        """Default parameter generation if no strategy is loaded"""
        tx_sender = (
            next(iter(context.agent.accounts.keys()))
            if context.agent.accounts
            else None
        )

        params = {
            "sender": tx_sender,
            "value": 0,
            "contract_address": None,
            "_amount": None,  # type: uint256
        }
        return params

    def execute(
        self, context: SimulationContext, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Execute the contract function with proper parameter handling"""
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False

            function_args = {
                "contract_address": execution_params.get("contract_address"),
                "_amount": execution_params.get("_amount"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.unwrap(**function_args)

        except Exception as e:
            self.logger.error(f"unwrap action failed: {e}", exc_info=True)
            return False


class UnwrapHandler(UnwrapBaseHandler):
    """Concrete handler implementation"""

    pass
