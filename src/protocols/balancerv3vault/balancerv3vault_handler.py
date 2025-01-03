import random
from datetime import datetime
import logging
from typing import Optional, Dict, Any, Tuple

from ape import chain
from eth_pydantic_types import HexBytes
from src.framework.agents import BaseAgent
from src.protocols.balancerv3vault import BalancerV3VaultClient


class AddLiquidityHandler:
    """Encapsulates the logic to execute a addLiquidity action."""

    def __init__(
        self,
        client: BalancerV3VaultClient,
        chain,
        logger: logging.Logger,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            'sender': None,  # Required: address that will send the transaction
            
            
            # Struct definition for params
            'params': {
                
                'pool': None,  # type: address
                
                'to': None,  # type: address
                
                'maxAmountsIn': None,  # type: uint256[]
                
                'minBptAmountOut': None,  # type: uint256
                
                'kind': None,  # type: uint8
                
                'userData': None,  # type: bytes
                
            },
            
            
        }
        return params

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False
            
            success = self.client.addLiquidity(
                
                params=execution_params.get("params"),
                
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(f"addLiquidity action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False

class Erc4626BufferWrapOrUnwrapHandler:
    """Encapsulates the logic to execute a erc4626BufferWrapOrUnwrap action."""

    def __init__(
        self,
        client: BalancerV3VaultClient,
        chain,
        logger: logging.Logger,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            'sender': None,  # Required: address that will send the transaction
            
            
            # Struct definition for params
            'params': {
                
                'kind': None,  # type: uint8
                
                'direction': None,  # type: uint8
                
                'wrappedToken': None,  # type: address
                
                'amountGivenRaw': None,  # type: uint256
                
                'limitRaw': None,  # type: uint256
                
            },
            
            
        }
        return params

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False
            
            success = self.client.erc4626BufferWrapOrUnwrap(
                
                params=execution_params.get("params"),
                
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(f"erc4626BufferWrapOrUnwrap action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False

class RemoveLiquidityHandler:
    """Encapsulates the logic to execute a removeLiquidity action."""

    def __init__(
        self,
        client: BalancerV3VaultClient,
        chain,
        logger: logging.Logger,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            'sender': None,  # Required: address that will send the transaction
            
            
            # Struct definition for params
            'params': {
                
                'pool': None,  # type: address
                
                'from': None,  # type: address
                
                'maxBptAmountIn': None,  # type: uint256
                
                'minAmountsOut': None,  # type: uint256[]
                
                'kind': None,  # type: uint8
                
                'userData': None,  # type: bytes
                
            },
            
            
        }
        return params

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False
            
            success = self.client.removeLiquidity(
                
                params=execution_params.get("params"),
                
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(f"removeLiquidity action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False

class SendToHandler:
    """Encapsulates the logic to execute a sendTo action."""

    def __init__(
        self,
        client: BalancerV3VaultClient,
        chain,
        logger: logging.Logger,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            'sender': None,  # Required: address that will send the transaction
            
            
            'token': None,  # type: address
            
            
            
            'to_': None,  # type: address
            
            
            
            'amount': None,  # type: uint256
            
            
        }
        return params

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False
            
            success = self.client.sendTo(
                
                token=execution_params.get("token"),
                
                to_=execution_params.get("to_"),
                
                amount=execution_params.get("amount"),
                
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(f"sendTo action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False

class SettleHandler:
    """Encapsulates the logic to execute a settle action."""

    def __init__(
        self,
        client: BalancerV3VaultClient,
        chain,
        logger: logging.Logger,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            'sender': None,  # Required: address that will send the transaction
            
            
            'token': None,  # type: address
            
            
            
            'amountHint': None,  # type: uint256
            
            
        }
        return params

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False
            
            success = self.client.settle(
                
                token=execution_params.get("token"),
                
                amountHint=execution_params.get("amountHint"),
                
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(f"settle action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False

class SwapHandler:
    """Encapsulates the logic to execute a swap action."""

    def __init__(
        self,
        client: BalancerV3VaultClient,
        chain,
        logger: logging.Logger,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            'sender': None,  # Required: address that will send the transaction
            
            
            # Struct definition for vaultSwapParams
            'vaultSwapParams': {
                
                'kind': None,  # type: uint8
                
                'pool': None,  # type: address
                
                'tokenIn': None,  # type: address
                
                'tokenOut': None,  # type: address
                
                'amountGivenRaw': None,  # type: uint256
                
                'limitRaw': None,  # type: uint256
                
                'userData': None,  # type: bytes
                
            },
            
            
        }
        return params

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False
            
            success = self.client.swap(
                
                vaultSwapParams=execution_params.get("vaultSwapParams"),
                
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(f"swap action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False

class TransferHandler:
    """Encapsulates the logic to execute a transfer action."""

    def __init__(
        self,
        client: BalancerV3VaultClient,
        chain,
        logger: logging.Logger,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            'sender': None,  # Required: address that will send the transaction
            
            
            'owner': None,  # type: address
            
            
            
            'to_': None,  # type: address
            
            
            
            'amount': None,  # type: uint256
            
            
        }
        return params

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False
            
            success = self.client.transfer(
                
                owner=execution_params.get("owner"),
                
                to_=execution_params.get("to_"),
                
                amount=execution_params.get("amount"),
                
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(f"transfer action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False

class TransferFromHandler:
    """Encapsulates the logic to execute a transferFrom action."""

    def __init__(
        self,
        client: BalancerV3VaultClient,
        chain,
        logger: logging.Logger,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            'sender': None,  # Required: address that will send the transaction
            
            
            'spender': None,  # type: address
            
            
            
            'from_': None,  # type: address
            
            
            
            'to_': None,  # type: address
            
            
            
            'amount': None,  # type: uint256
            
            
        }
        return params

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False
            
            success = self.client.transferFrom(
                
                spender=execution_params.get("spender"),
                
                from_=execution_params.get("from_"),
                
                to_=execution_params.get("to_"),
                
                amount=execution_params.get("amount"),
                
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(f"transferFrom action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False

class UnlockHandler:
    """Encapsulates the logic to execute a unlock action."""

    def __init__(
        self,
        client: BalancerV3VaultClient,
        chain,
        logger: logging.Logger,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            'sender': None,  # Required: address that will send the transaction
            
            
            'data': None,  # type: bytes
            
            
        }
        return params

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False
            
            success = self.client.unlock(
                
                data=execution_params.get("data"),
                
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(f"unlock action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False
