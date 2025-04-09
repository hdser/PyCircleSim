import random
import importlib
from typing import Dict, Any, Optional
from eth_pydantic_types import HexBytes
from src.framework.core.context import SimulationContext
from src.protocols.interfaces.balancerv2lbp.balancerv2lbp_client import (
    BalancerV2LBPClient,
)


class ApproveBaseHandler:
    """Base handler class for approve action."""

    def __init__(
        self, client: BalancerV2LBPClient, chain, logger, strategy_name: str = "basic"
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
            "spender": None,  # type: address
            "amount": None,  # type: uint256
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
                "spender": execution_params.get("spender"),
                "amount": execution_params.get("amount"),
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
        self, client: BalancerV2LBPClient, chain, logger, strategy_name: str = "basic"
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
            "spender": None,  # type: address
            "amount": None,  # type: uint256
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
                "spender": execution_params.get("spender"),
                "amount": execution_params.get("amount"),
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
        self, client: BalancerV2LBPClient, chain, logger, strategy_name: str = "basic"
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
            "spender": None,  # type: address
            "addedValue": None,  # type: uint256
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
                "spender": execution_params.get("spender"),
                "addedValue": execution_params.get("addedValue"),
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


class OnexitpoolBaseHandler:
    """Base handler class for onExitPool action."""

    def __init__(
        self, client: BalancerV2LBPClient, chain, logger, strategy_name: str = "basic"
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
            "poolId": None,  # type: bytes32
            "sender": None,  # type: address
            "recipient": None,  # type: address
            "balances": None,  # type: uint256[]
            "lastChangeBlock": None,  # type: uint256
            "": None,  # type: uint256
            "userData": None,  # type: bytes
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
                "poolId": execution_params.get("poolId"),
                "sender": execution_params.get("sender"),
                "recipient": execution_params.get("recipient"),
                "balances": execution_params.get("balances"),
                "lastChangeBlock": execution_params.get("lastChangeBlock"),
                "": execution_params.get(""),
                "userData": execution_params.get("userData"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.onExitPool(**function_args)

        except Exception as e:
            self.logger.error(f"onExitPool action failed: {e}", exc_info=True)
            return False


class OnexitpoolHandler(OnexitpoolBaseHandler):
    """Concrete handler implementation"""

    pass


class OnjoinpoolBaseHandler:
    """Base handler class for onJoinPool action."""

    def __init__(
        self, client: BalancerV2LBPClient, chain, logger, strategy_name: str = "basic"
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
            "poolId": None,  # type: bytes32
            "sender": None,  # type: address
            "recipient": None,  # type: address
            "balances": None,  # type: uint256[]
            "lastChangeBlock": None,  # type: uint256
            "": None,  # type: uint256
            "userData": None,  # type: bytes
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
                "poolId": execution_params.get("poolId"),
                "sender": execution_params.get("sender"),
                "recipient": execution_params.get("recipient"),
                "balances": execution_params.get("balances"),
                "lastChangeBlock": execution_params.get("lastChangeBlock"),
                "": execution_params.get(""),
                "userData": execution_params.get("userData"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.onJoinPool(**function_args)

        except Exception as e:
            self.logger.error(f"onJoinPool action failed: {e}", exc_info=True)
            return False


class OnjoinpoolHandler(OnjoinpoolBaseHandler):
    """Concrete handler implementation"""

    pass


class OnswapBaseHandler:
    """Base handler class for onSwap action."""

    def __init__(
        self, client: BalancerV2LBPClient, chain, logger, strategy_name: str = "basic"
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
            "request": None,  # type: tuple
            "balanceTokenIn": None,  # type: uint256
            "balanceTokenOut": None,  # type: uint256
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
                "request": execution_params.get("request"),
                "balanceTokenIn": execution_params.get("balanceTokenIn"),
                "balanceTokenOut": execution_params.get("balanceTokenOut"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.onSwap(**function_args)

        except Exception as e:
            self.logger.error(f"onSwap action failed: {e}", exc_info=True)
            return False


class OnswapHandler(OnswapBaseHandler):
    """Concrete handler implementation"""

    pass


class PermitBaseHandler:
    """Base handler class for permit action."""

    def __init__(
        self, client: BalancerV2LBPClient, chain, logger, strategy_name: str = "basic"
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
            "owner": None,  # type: address
            "spender": None,  # type: address
            "value": None,  # type: uint256
            "deadline": None,  # type: uint256
            "v": None,  # type: uint8
            "r": None,  # type: bytes32
            "s": None,  # type: bytes32
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
                "owner": execution_params.get("owner"),
                "spender": execution_params.get("spender"),
                "value": execution_params.get("value"),
                "deadline": execution_params.get("deadline"),
                "v": execution_params.get("v"),
                "r": execution_params.get("r"),
                "s": execution_params.get("s"),
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


class QueryexitBaseHandler:
    """Base handler class for queryExit action."""

    def __init__(
        self, client: BalancerV2LBPClient, chain, logger, strategy_name: str = "basic"
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
            "poolId": None,  # type: bytes32
            "sender": None,  # type: address
            "recipient": None,  # type: address
            "balances": None,  # type: uint256[]
            "lastChangeBlock": None,  # type: uint256
            "protocolSwapFeePercentage": None,  # type: uint256
            "userData": None,  # type: bytes
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
                "poolId": execution_params.get("poolId"),
                "sender": execution_params.get("sender"),
                "recipient": execution_params.get("recipient"),
                "balances": execution_params.get("balances"),
                "lastChangeBlock": execution_params.get("lastChangeBlock"),
                "protocolSwapFeePercentage": execution_params.get(
                    "protocolSwapFeePercentage"
                ),
                "userData": execution_params.get("userData"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.queryExit(**function_args)

        except Exception as e:
            self.logger.error(f"queryExit action failed: {e}", exc_info=True)
            return False


class QueryexitHandler(QueryexitBaseHandler):
    """Concrete handler implementation"""

    pass


class QueryjoinBaseHandler:
    """Base handler class for queryJoin action."""

    def __init__(
        self, client: BalancerV2LBPClient, chain, logger, strategy_name: str = "basic"
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
            "poolId": None,  # type: bytes32
            "sender": None,  # type: address
            "recipient": None,  # type: address
            "balances": None,  # type: uint256[]
            "lastChangeBlock": None,  # type: uint256
            "protocolSwapFeePercentage": None,  # type: uint256
            "userData": None,  # type: bytes
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
                "poolId": execution_params.get("poolId"),
                "sender": execution_params.get("sender"),
                "recipient": execution_params.get("recipient"),
                "balances": execution_params.get("balances"),
                "lastChangeBlock": execution_params.get("lastChangeBlock"),
                "protocolSwapFeePercentage": execution_params.get(
                    "protocolSwapFeePercentage"
                ),
                "userData": execution_params.get("userData"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.queryJoin(**function_args)

        except Exception as e:
            self.logger.error(f"queryJoin action failed: {e}", exc_info=True)
            return False


class QueryjoinHandler(QueryjoinBaseHandler):
    """Concrete handler implementation"""

    pass


class SetassetmanagerpoolconfigBaseHandler:
    """Base handler class for setAssetManagerPoolConfig action."""

    def __init__(
        self, client: BalancerV2LBPClient, chain, logger, strategy_name: str = "basic"
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
            "token": None,  # type: address
            "poolConfig": None,  # type: bytes
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
                "token": execution_params.get("token"),
                "poolConfig": execution_params.get("poolConfig"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.setAssetManagerPoolConfig(**function_args)

        except Exception as e:
            self.logger.error(
                f"setAssetManagerPoolConfig action failed: {e}", exc_info=True
            )
            return False


class SetassetmanagerpoolconfigHandler(SetassetmanagerpoolconfigBaseHandler):
    """Concrete handler implementation"""

    pass


class SetpausedBaseHandler:
    """Base handler class for setPaused action."""

    def __init__(
        self, client: BalancerV2LBPClient, chain, logger, strategy_name: str = "basic"
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
            "paused": None,  # type: bool
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
                "paused": execution_params.get("paused"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.setPaused(**function_args)

        except Exception as e:
            self.logger.error(f"setPaused action failed: {e}", exc_info=True)
            return False


class SetpausedHandler(SetpausedBaseHandler):
    """Concrete handler implementation"""

    pass


class SetswapenabledBaseHandler:
    """Base handler class for setSwapEnabled action."""

    def __init__(
        self, client: BalancerV2LBPClient, chain, logger, strategy_name: str = "basic"
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
            "swapEnabled": None,  # type: bool
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
                "swapEnabled": execution_params.get("swapEnabled"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.setSwapEnabled(**function_args)

        except Exception as e:
            self.logger.error(f"setSwapEnabled action failed: {e}", exc_info=True)
            return False


class SetswapenabledHandler(SetswapenabledBaseHandler):
    """Concrete handler implementation"""

    pass


class SetswapfeepercentageBaseHandler:
    """Base handler class for setSwapFeePercentage action."""

    def __init__(
        self, client: BalancerV2LBPClient, chain, logger, strategy_name: str = "basic"
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
            "swapFeePercentage": None,  # type: uint256
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
                "swapFeePercentage": execution_params.get("swapFeePercentage"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.setSwapFeePercentage(**function_args)

        except Exception as e:
            self.logger.error(f"setSwapFeePercentage action failed: {e}", exc_info=True)
            return False


class SetswapfeepercentageHandler(SetswapfeepercentageBaseHandler):
    """Concrete handler implementation"""

    pass


class TransferBaseHandler:
    """Base handler class for transfer action."""

    def __init__(
        self, client: BalancerV2LBPClient, chain, logger, strategy_name: str = "basic"
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
            "recipient": None,  # type: address
            "amount": None,  # type: uint256
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
                "recipient": execution_params.get("recipient"),
                "amount": execution_params.get("amount"),
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
        self, client: BalancerV2LBPClient, chain, logger, strategy_name: str = "basic"
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
            "sender": None,  # type: address
            "recipient": None,  # type: address
            "amount": None,  # type: uint256
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
                "sender": execution_params.get("sender"),
                "recipient": execution_params.get("recipient"),
                "amount": execution_params.get("amount"),
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


class UpdateweightsgraduallyBaseHandler:
    """Base handler class for updateWeightsGradually action."""

    def __init__(
        self, client: BalancerV2LBPClient, chain, logger, strategy_name: str = "basic"
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
            "startTime": None,  # type: uint256
            "endTime": None,  # type: uint256
            "endWeights": None,  # type: uint256[]
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
                "startTime": execution_params.get("startTime"),
                "endTime": execution_params.get("endTime"),
                "endWeights": execution_params.get("endWeights"),
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.updateWeightsGradually(**function_args)

        except Exception as e:
            self.logger.error(
                f"updateWeightsGradually action failed: {e}", exc_info=True
            )
            return False


class UpdateweightsgraduallyHandler(UpdateweightsgraduallyBaseHandler):
    """Concrete handler implementation"""

    pass
