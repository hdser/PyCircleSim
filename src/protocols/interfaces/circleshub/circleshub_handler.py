import random
import importlib
from typing import Dict, Any, Optional
from eth_pydantic_types import HexBytes
from src.framework.core.context import SimulationContext
from src.protocols.interfaces.circleshub.circleshub_client import CirclesHubClient


class BurnBaseHandler:
    """Base handler class for burn action."""

    def __init__(
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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
            "_id": None,  # type: uint256
            "_amount": None,  # type: uint256
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
                "_id": execution_params.get("_id"),
                "_amount": execution_params.get("_amount"),
                "_data": execution_params.get("_data"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.burn(**function_args)

        except Exception as e:
            self.logger.error(f"burn action failed: {e}", exc_info=True)
            return False


class BurnHandler(BurnBaseHandler):
    """Concrete handler implementation"""

    pass


class CalculateIssuanceWithCheckBaseHandler:
    """Base handler class for calculateIssuanceWithCheck action."""

    def __init__(
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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
            "_human": None,  # type: address
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
                "_human": execution_params.get("_human"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.calculateIssuanceWithCheck(**function_args)

        except Exception as e:
            self.logger.error(
                f"calculateIssuanceWithCheck action failed: {e}", exc_info=True
            )
            return False


class CalculateIssuanceWithCheckHandler(CalculateIssuanceWithCheckBaseHandler):
    """Concrete handler implementation"""

    pass


class GroupMintBaseHandler:
    """Base handler class for groupMint action."""

    def __init__(
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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
            "_group": None,  # type: address
            "_collateralAvatars": None,  # type: address[]
            "_amounts": None,  # type: uint256[]
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
                "_group": execution_params.get("_group"),
                "_collateralAvatars": execution_params.get("_collateralAvatars"),
                "_amounts": execution_params.get("_amounts"),
                "_data": execution_params.get("_data"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.groupMint(**function_args)

        except Exception as e:
            self.logger.error(f"groupMint action failed: {e}", exc_info=True)
            return False


class GroupMintHandler(GroupMintBaseHandler):
    """Concrete handler implementation"""

    pass


class MigrateBaseHandler:
    """Base handler class for migrate action."""

    def __init__(
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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
            "_avatars": None,  # type: address[]
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
                "_owner": execution_params.get("_owner"),
                "_avatars": execution_params.get("_avatars"),
                "_amounts": execution_params.get("_amounts"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.migrate(**function_args)

        except Exception as e:
            self.logger.error(f"migrate action failed: {e}", exc_info=True)
            return False


class MigrateHandler(MigrateBaseHandler):
    """Concrete handler implementation"""

    pass


class OperateFlowMatrixBaseHandler:
    """Base handler class for operateFlowMatrix action."""

    def __init__(
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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
            "_flowVertices": None,  # type: address[]
            "_flow": None,  # type: tuple[]
            "_streams": None,  # type: tuple[]
            "_packedCoordinates": None,  # type: bytes
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
                "_flowVertices": execution_params.get("_flowVertices"),
                "_flow": execution_params.get("_flow"),
                "_streams": execution_params.get("_streams"),
                "_packedCoordinates": execution_params.get("_packedCoordinates"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.operateFlowMatrix(**function_args)

        except Exception as e:
            self.logger.error(f"operateFlowMatrix action failed: {e}", exc_info=True)
            return False


class OperateFlowMatrixHandler(OperateFlowMatrixBaseHandler):
    """Concrete handler implementation"""

    pass


class PersonalMintBaseHandler:
    """Base handler class for personalMint action."""

    def __init__(
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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

            return self.client.personalMint(**function_args)

        except Exception as e:
            self.logger.error(f"personalMint action failed: {e}", exc_info=True)
            return False


class PersonalMintHandler(PersonalMintBaseHandler):
    """Concrete handler implementation"""

    pass


class RegisterCustomGroupBaseHandler:
    """Base handler class for registerCustomGroup action."""

    def __init__(
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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
            "_mint": None,  # type: address
            "_treasury": None,  # type: address
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
                "_mint": execution_params.get("_mint"),
                "_treasury": execution_params.get("_treasury"),
                "_name": execution_params.get("_name"),
                "_symbol": execution_params.get("_symbol"),
                "_metadataDigest": execution_params.get("_metadataDigest"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.registerCustomGroup(**function_args)

        except Exception as e:
            self.logger.error(f"registerCustomGroup action failed: {e}", exc_info=True)
            return False


class RegisterCustomGroupHandler(RegisterCustomGroupBaseHandler):
    """Concrete handler implementation"""

    pass


class RegisterGroupBaseHandler:
    """Base handler class for registerGroup action."""

    def __init__(
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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
            "_mint": None,  # type: address
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
                "_mint": execution_params.get("_mint"),
                "_name": execution_params.get("_name"),
                "_symbol": execution_params.get("_symbol"),
                "_metadataDigest": execution_params.get("_metadataDigest"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.registerGroup(**function_args)

        except Exception as e:
            self.logger.error(f"registerGroup action failed: {e}", exc_info=True)
            return False


class RegisterGroupHandler(RegisterGroupBaseHandler):
    """Concrete handler implementation"""

    pass


class RegisterHumanBaseHandler:
    """Base handler class for registerHuman action."""

    def __init__(
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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
            "_inviter": None,  # type: address
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
                "_inviter": execution_params.get("_inviter"),
                "_metadataDigest": execution_params.get("_metadataDigest"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.registerHuman(**function_args)

        except Exception as e:
            self.logger.error(f"registerHuman action failed: {e}", exc_info=True)
            return False


class RegisterHumanHandler(RegisterHumanBaseHandler):
    """Concrete handler implementation"""

    pass


class RegisterOrganizationBaseHandler:
    """Base handler class for registerOrganization action."""

    def __init__(
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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
            "_name": None,  # type: string
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
                "_name": execution_params.get("_name"),
                "_metadataDigest": execution_params.get("_metadataDigest"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.registerOrganization(**function_args)

        except Exception as e:
            self.logger.error(f"registerOrganization action failed: {e}", exc_info=True)
            return False


class RegisterOrganizationHandler(RegisterOrganizationBaseHandler):
    """Concrete handler implementation"""

    pass


class SafeBatchTransferFromBaseHandler:
    """Base handler class for safeBatchTransferFrom action."""

    def __init__(
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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


class SetApprovalForAllBaseHandler:
    """Base handler class for setApprovalForAll action."""

    def __init__(
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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
            "_approved": None,  # type: bool
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
                "_approved": execution_params.get("_approved"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.setApprovalForAll(**function_args)

        except Exception as e:
            self.logger.error(f"setApprovalForAll action failed: {e}", exc_info=True)
            return False


class SetApprovalForAllHandler(SetApprovalForAllBaseHandler):
    """Concrete handler implementation"""

    pass


class StopBaseHandler:
    """Base handler class for stop action."""

    def __init__(
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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

            return self.client.stop(**function_args)

        except Exception as e:
            self.logger.error(f"stop action failed: {e}", exc_info=True)
            return False


class StopHandler(StopBaseHandler):
    """Concrete handler implementation"""

    pass


class TrustBaseHandler:
    """Base handler class for trust action."""

    def __init__(
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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


class WrapBaseHandler:
    """Base handler class for wrap action."""

    def __init__(
        self, client: CirclesHubClient, chain, logger, strategy_name: str = "basic"
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
            "_avatar": None,  # type: address
            "_amount": None,  # type: uint256
            "_type": None,  # type: uint8
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
                "_avatar": execution_params.get("_avatar"),
                "_amount": execution_params.get("_amount"),
                "_type": execution_params.get("_type"),
                # Add transaction parameters
                "sender": execution_params.get("sender"),
                "value": execution_params.get("value", 0),
                "context": context,
            }

            return self.client.wrap(**function_args)

        except Exception as e:
            self.logger.error(f"wrap action failed: {e}", exc_info=True)
            return False


class WrapHandler(WrapBaseHandler):
    """Concrete handler implementation"""

    pass
