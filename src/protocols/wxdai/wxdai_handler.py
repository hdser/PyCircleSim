import random
from datetime import datetime
import logging
from typing import Optional, Dict, Any, Tuple

from ape import chain
from eth_pydantic_types import HexBytes
from src.framework.agents import BaseAgent
from src.protocols.wxdai import WXDAIClient


class ApproveHandler:
    """Encapsulates the logic to execute a approve action."""

    def __init__(
        self,
        client: WXDAIClient,
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
            
            
            'guy': None,  # type: address
            
            
            
            'wad': None,  # type: uint256
            
            
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
            
            success = self.client.approve(
                
                guy=execution_params.get("guy"),
                
                wad=execution_params.get("wad"),
                
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(f"approve action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False

class TransferFromHandler:
    """Encapsulates the logic to execute a transferFrom action."""

    def __init__(
        self,
        client: WXDAIClient,
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
            
            
            'src': None,  # type: address
            
            
            
            'dst': None,  # type: address
            
            
            
            'wad': None,  # type: uint256
            
            
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
                
                src=execution_params.get("src"),
                
                dst=execution_params.get("dst"),
                
                wad=execution_params.get("wad"),
                
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(f"transferFrom action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False

class WithdrawHandler:
    """Encapsulates the logic to execute a withdraw action."""

    def __init__(
        self,
        client: WXDAIClient,
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
            
            
            'wad': None,  # type: uint256
            
            
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
            
            success = self.client.withdraw(
                
                wad=execution_params.get("wad"),
                
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(f"withdraw action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False

class TransferHandler:
    """Encapsulates the logic to execute a transfer action."""

    def __init__(
        self,
        client: WXDAIClient,
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
            
            
            'dst': None,  # type: address
            
            
            
            'wad': None,  # type: uint256
            
            
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
                
                dst=execution_params.get("dst"),
                
                wad=execution_params.get("wad"),
                
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(f"transfer action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False

class DepositHandler:
    """Encapsulates the logic to execute a deposit action."""

    def __init__(
        self,
        client: WXDAIClient,
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
        
        sender = random.choice(list(agent.accounts.keys()))
        
        params = {
            'sender': sender, 
            'value': 10000000000000000000
            
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
            
            success = self.client.deposit(
                sender=execution_params.get("sender"),
                value=execution_params.get("value"),
            )

            return success

        except Exception as e:
            self.logger.error(f"deposit action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False
