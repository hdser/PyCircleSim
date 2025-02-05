import random
import importlib
from typing import Dict, Any, Optional
from eth_pydantic_types import HexBytes
from src.framework.core.context import SimulationContext
from src.protocols.interfaces.supergroup.supergroup_client import SuperGroupClient


class BeforeBurnPolicyBaseHandler:
    """Base handler class for beforeBurnPolicy action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "": None,  # type: address
            "": None,  # type: address
            "": None,  # type: uint256
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "": execution_params.get(""),
                "": execution_params.get(""),
                "": execution_params.get(""),
                "": execution_params.get(""),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.beforeBurnPolicy(**function_args)

        except Exception as e:
            self.logger.error(f"beforeBurnPolicy action failed: {e}", exc_info=True)
            return False


class BeforeBurnPolicyHandler(BeforeBurnPolicyBaseHandler):
    """Concrete handler implementation"""

    pass


class BeforeMintPolicyBaseHandler:
    """Base handler class for beforeMintPolicy action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_minter": None,  # type: address
            "_group": None,  # type: address
            "_collateral": None,  # type: uint256[]
            "_amounts": None,  # type: uint256[]
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_minter": execution_params.get("_minter"),
                "_group": execution_params.get("_group"),
                "_collateral": execution_params.get("_collateral"),
                "_amounts": execution_params.get("_amounts"),
                "": execution_params.get(""),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.beforeMintPolicy(**function_args)

        except Exception as e:
            self.logger.error(f"beforeMintPolicy action failed: {e}", exc_info=True)
            return False


class BeforeMintPolicyHandler(BeforeMintPolicyBaseHandler):
    """Concrete handler implementation"""

    pass


class BeforeRedeemPolicyBaseHandler:
    """Base handler class for beforeRedeemPolicy action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "": None,  # type: address
            "": None,  # type: address
            "_group": None,  # type: address
            "": None,  # type: uint256
            "_data": None,  # type: bytes
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "": execution_params.get(""),
                "": execution_params.get(""),
                "_group": execution_params.get("_group"),
                "": execution_params.get(""),
                "_data": execution_params.get("_data"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.beforeRedeemPolicy(**function_args)

        except Exception as e:
            self.logger.error(f"beforeRedeemPolicy action failed: {e}", exc_info=True)
            return False


class BeforeRedeemPolicyHandler(BeforeRedeemPolicyBaseHandler):
    """Concrete handler implementation"""

    pass


class OnERC1155BatchReceivedBaseHandler:
    """Base handler class for onERC1155BatchReceived action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "": None,  # type: address
            "_from": None,  # type: address
            "_ids": None,  # type: uint256[]
            "_values": None,  # type: uint256[]
            "_data": None,  # type: bytes
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "": execution_params.get(""),
                "_from": execution_params.get("_from"),
                "_ids": execution_params.get("_ids"),
                "_values": execution_params.get("_values"),
                "_data": execution_params.get("_data"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.onERC1155BatchReceived(**function_args)

        except Exception as e:
            self.logger.error(
                f"onERC1155BatchReceived action failed: {e}", exc_info=True
            )
            return False


class OnERC1155BatchReceivedHandler(OnERC1155BatchReceivedBaseHandler):
    """Concrete handler implementation"""

    pass


class OnERC1155ReceivedBaseHandler:
    """Base handler class for onERC1155Received action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "": None,  # type: address
            "_from": None,  # type: address
            "_id": None,  # type: uint256
            "_value": None,  # type: uint256
            "_data": None,  # type: bytes
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "": execution_params.get(""),
                "_from": execution_params.get("_from"),
                "_id": execution_params.get("_id"),
                "_value": execution_params.get("_value"),
                "_data": execution_params.get("_data"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.onERC1155Received(**function_args)

        except Exception as e:
            self.logger.error(f"onERC1155Received action failed: {e}", exc_info=True)
            return False


class OnERC1155ReceivedHandler(OnERC1155ReceivedBaseHandler):
    """Concrete handler implementation"""

    pass


class RegisterOperatorRequestBaseHandler:
    """Base handler class for registerOperatorRequest action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_minter": None,  # type: address
            "_group": None,  # type: address
            "_collateral": None,  # type: uint256[]
            "_amounts": None,  # type: uint256[]
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_minter": execution_params.get("_minter"),
                "_group": execution_params.get("_group"),
                "_collateral": execution_params.get("_collateral"),
                "_amounts": execution_params.get("_amounts"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.registerOperatorRequest(**function_args)

        except Exception as e:
            self.logger.error(
                f"registerOperatorRequest action failed: {e}", exc_info=True
            )
            return False


class RegisterOperatorRequestHandler(RegisterOperatorRequestBaseHandler):
    """Concrete handler implementation"""

    pass


class RegisterShortNameBaseHandler:
    """Base handler class for registerShortName action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.registerShortName(**function_args)

        except Exception as e:
            self.logger.error(f"registerShortName action failed: {e}", exc_info=True)
            return False


class RegisterShortNameHandler(RegisterShortNameBaseHandler):
    """Concrete handler implementation"""

    pass


class RegisterShortNameWithNonceBaseHandler:
    """Base handler class for registerShortNameWithNonce action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_nonce": None,  # type: uint256
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_nonce": execution_params.get("_nonce"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.registerShortNameWithNonce(**function_args)

        except Exception as e:
            self.logger.error(
                f"registerShortNameWithNonce action failed: {e}", exc_info=True
            )
            return False


class RegisterShortNameWithNonceHandler(RegisterShortNameWithNonceBaseHandler):
    """Concrete handler implementation"""

    pass


class SafeBatchTransferFromBaseHandler:
    """Base handler class for safeBatchTransferFrom action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_from": None,  # type: address
            "_to": None,  # type: address
            "_ids": None,  # type: uint256[]
            "_values": None,  # type: uint256[]
            "_data": None,  # type: bytes
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_from": execution_params.get("_from"),
                "_to": execution_params.get("_to"),
                "_ids": execution_params.get("_ids"),
                "_values": execution_params.get("_values"),
                "_data": execution_params.get("_data"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.safeBatchTransferFrom(**function_args)

        except Exception as e:
            self.logger.error(
                f"safeBatchTransferFrom action failed: {e}", exc_info=True
            )
            return False


class SafeBatchTransferFromHandler(SafeBatchTransferFromBaseHandler):
    """Concrete handler implementation"""

    pass


class SafeTransferFromBaseHandler:
    """Base handler class for safeTransferFrom action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_from": None,  # type: address
            "_to": None,  # type: address
            "_id": None,  # type: uint256
            "_value": None,  # type: uint256
            "_data": None,  # type: bytes
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_from": execution_params.get("_from"),
                "_to": execution_params.get("_to"),
                "_id": execution_params.get("_id"),
                "_value": execution_params.get("_value"),
                "_data": execution_params.get("_data"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.safeTransferFrom(**function_args)

        except Exception as e:
            self.logger.error(f"safeTransferFrom action failed: {e}", exc_info=True)
            return False


class SafeTransferFromHandler(SafeTransferFromBaseHandler):
    """Concrete handler implementation"""

    pass


class SetAdvancedUsageFlagBaseHandler:
    """Base handler class for setAdvancedUsageFlag action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_flag": None,  # type: bytes32
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_flag": execution_params.get("_flag"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.setAdvancedUsageFlag(**function_args)

        except Exception as e:
            self.logger.error(f"setAdvancedUsageFlag action failed: {e}", exc_info=True)
            return False


class SetAdvancedUsageFlagHandler(SetAdvancedUsageFlagBaseHandler):
    """Concrete handler implementation"""

    pass


class SetAuthorizedOperatorBaseHandler:
    """Base handler class for setAuthorizedOperator action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_operator": None,  # type: address
            "_authorized": None,  # type: bool
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_operator": execution_params.get("_operator"),
                "_authorized": execution_params.get("_authorized"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.setAuthorizedOperator(**function_args)

        except Exception as e:
            self.logger.error(
                f"setAuthorizedOperator action failed: {e}", exc_info=True
            )
            return False


class SetAuthorizedOperatorHandler(SetAuthorizedOperatorBaseHandler):
    """Concrete handler implementation"""

    pass


class SetMintFeeBaseHandler:
    """Base handler class for setMintFee action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_mintFee": None,  # type: uint256
            "_feeCollection": None,  # type: address
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_mintFee": execution_params.get("_mintFee"),
                "_feeCollection": execution_params.get("_feeCollection"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.setMintFee(**function_args)

        except Exception as e:
            self.logger.error(f"setMintFee action failed: {e}", exc_info=True)
            return False


class SetMintFeeHandler(SetMintFeeBaseHandler):
    """Concrete handler implementation"""

    pass


class SetRedemptionBurnBaseHandler:
    """Base handler class for setRedemptionBurn action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_burnRedemptionRate": None,  # type: uint256
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_burnRedemptionRate": execution_params.get("_burnRedemptionRate"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.setRedemptionBurn(**function_args)

        except Exception as e:
            self.logger.error(f"setRedemptionBurn action failed: {e}", exc_info=True)
            return False


class SetRedemptionBurnHandler(SetRedemptionBurnBaseHandler):
    """Concrete handler implementation"""

    pass


class SetRequireOperatorsBaseHandler:
    """Base handler class for setRequireOperators action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_required": None,  # type: bool
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_required": execution_params.get("_required"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.setRequireOperators(**function_args)

        except Exception as e:
            self.logger.error(f"setRequireOperators action failed: {e}", exc_info=True)
            return False


class SetRequireOperatorsHandler(SetRequireOperatorsBaseHandler):
    """Concrete handler implementation"""

    pass


class SetReturnGroupCirclesToSenderBaseHandler:
    """Base handler class for setReturnGroupCirclesToSender action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_returnGroupCircles": None,  # type: bool
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_returnGroupCircles": execution_params.get("_returnGroupCircles"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.setReturnGroupCirclesToSender(**function_args)

        except Exception as e:
            self.logger.error(
                f"setReturnGroupCirclesToSender action failed: {e}", exc_info=True
            )
            return False


class SetReturnGroupCirclesToSenderHandler(SetReturnGroupCirclesToSenderBaseHandler):
    """Concrete handler implementation"""

    pass


class SetServiceBaseHandler:
    """Base handler class for setService action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_service": None,  # type: address
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_service": execution_params.get("_service"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.setService(**function_args)

        except Exception as e:
            self.logger.error(f"setService action failed: {e}", exc_info=True)
            return False


class SetServiceHandler(SetServiceBaseHandler):
    """Concrete handler implementation"""

    pass


class SetupBaseHandler:
    """Base handler class for setup action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_owner": None,  # type: address
            "_mintFee": None,  # type: uint256
            "_feeCollection": None,  # type: address
            "_redemptionBurnRatio": None,  # type: uint256
            "_operators": None,  # type: address[]
            "_name": None,  # type: string
            "_symbol": None,  # type: string
            "_metadataDigest": None,  # type: bytes32
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_owner": execution_params.get("_owner"),
                "_mintFee": execution_params.get("_mintFee"),
                "_feeCollection": execution_params.get("_feeCollection"),
                "_redemptionBurnRatio": execution_params.get("_redemptionBurnRatio"),
                "_operators": execution_params.get("_operators"),
                "_name": execution_params.get("_name"),
                "_symbol": execution_params.get("_symbol"),
                "_metadataDigest": execution_params.get("_metadataDigest"),
                # Add transaction parameters
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


class SetupBaseHandler:
    """Base handler class for setup action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_owner": None,  # type: address
            "_service": None,  # type: address
            "_mintFee": None,  # type: uint256
            "_feeCollection": None,  # type: address
            "_redemptionBurnRate": None,  # type: uint256
            "_operators": None,  # type: address[]
            "_name": None,  # type: string
            "_symbol": None,  # type: string
            "_metadataDigest": None,  # type: bytes32
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_owner": execution_params.get("_owner"),
                "_service": execution_params.get("_service"),
                "_mintFee": execution_params.get("_mintFee"),
                "_feeCollection": execution_params.get("_feeCollection"),
                "_redemptionBurnRate": execution_params.get("_redemptionBurnRate"),
                "_operators": execution_params.get("_operators"),
                "_name": execution_params.get("_name"),
                "_symbol": execution_params.get("_symbol"),
                "_metadataDigest": execution_params.get("_metadataDigest"),
                # Add transaction parameters
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


class TrustBaseHandler:
    """Base handler class for trust action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_trustReceiver": None,  # type: address
            "_expiry": None,  # type: uint96
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_trustReceiver": execution_params.get("_trustReceiver"),
                "_expiry": execution_params.get("_expiry"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.trust(**function_args)

        except Exception as e:
            self.logger.error(f"trust action failed: {e}", exc_info=True)
            return False


class TrustHandler(TrustBaseHandler):
    """Concrete handler implementation"""

    pass


class TrustBatchBaseHandler:
    """Base handler class for trustBatch action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_backers": None,  # type: address[]
            "_expiry": None,  # type: uint96
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_backers": execution_params.get("_backers"),
                "_expiry": execution_params.get("_expiry"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.trustBatch(**function_args)

        except Exception as e:
            self.logger.error(f"trustBatch action failed: {e}", exc_info=True)
            return False


class TrustBatchHandler(TrustBatchBaseHandler):
    """Concrete handler implementation"""

    pass


class UpdateMetadataDigestBaseHandler:
    """Base handler class for updateMetadataDigest action."""

    def __init__(
        self, client: SuperGroupClient, chain, logger, strategy_name: str = "basic"
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

        # Build parameters dictionary with collision handling
        params = {
            "sender": tx_sender,  # Transaction sender
            "value": 0,  # Transaction value
            "_metadataDigest": None,  # type: bytes32
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

            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                "_metadataDigest": execution_params.get("_metadataDigest"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.updateMetadataDigest(**function_args)

        except Exception as e:
            self.logger.error(f"updateMetadataDigest action failed: {e}", exc_info=True)
            return False


class UpdateMetadataDigestHandler(UpdateMetadataDigestBaseHandler):
    """Concrete handler implementation"""

    pass
