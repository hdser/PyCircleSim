import random
from datetime import datetime
import logging
from typing import Optional, Dict, Any, Tuple

from ape import chain
from eth_pydantic_types import HexBytes
from src.framework.agents import BaseAgent
from src.protocols.fjordlbpproxyv6 import FjordLbpProxyV6Client


class AddFundTokenOptionsHandler:
    """Encapsulates the logic to execute a addFundTokenOptions action."""

    def __init__(
        self,
        client: FjordLbpProxyV6Client,
        chain,
        logger: logging.Logger,
        on_addfundtokenoptions_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_addfundtokenoptions_performed = on_addfundtokenoptions_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            "sender": None,  # Required: address that will send the transaction
            "tokens": None,  # type: address[]
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

            success = self.client.addFundTokenOptions(
                tokens=execution_params.get("tokens"),
                sender=execution_params.get("sender"),
            )

            if success and self.on_addfundtokenoptions_performed:
                self.on_addfundtokenoptions_performed(
                    tokens=execution_params.get("tokens"),
                    sender=execution_params.get("sender"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
                )

            return success

        except Exception as e:
            self.logger.error(
                f"addFundTokenOptions action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class CreateLBPHandler:
    """Encapsulates the logic to execute a createLBP action."""

    def __init__(
        self,
        client: FjordLbpProxyV6Client,
        chain,
        logger: logging.Logger,
        on_createlbp_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_createlbp_performed = on_createlbp_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            "sender": None,  # Required: address that will send the transaction
            # Struct definition for poolConfig
            "poolConfig": {
                "name": None,  # type: string
                "symbol": None,  # type: string
                "tokens": None,  # type: address[]
                "amounts": None,  # type: uint256[]
                "weights": None,  # type: uint256[]
                "endWeights": None,  # type: uint256[]
                "swapFeePercentage": None,  # type: uint256
                "startTime": None,  # type: uint256
                "endTime": None,  # type: uint256
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

            success = self.client.createLBP(
                poolConfig=execution_params.get("poolConfig"),
                sender=execution_params.get("sender"),
            )

            if success and self.on_createlbp_performed:
                self.on_createlbp_performed(
                    poolConfig=execution_params.get("poolConfig"),
                    sender=execution_params.get("sender"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
                )

            return success

        except Exception as e:
            self.logger.error(
                f"createLBP action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class CreateWeightedPoolForLBPHandler:
    """Encapsulates the logic to execute a createWeightedPoolForLBP action."""

    def __init__(
        self,
        client: FjordLbpProxyV6Client,
        chain,
        logger: logging.Logger,
        on_createweightedpoolforlbp_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_createweightedpoolforlbp_performed = (
            on_createweightedpoolforlbp_performed
        )

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            "sender": None,  # Required: address that will send the transaction
            "lbpPool": None,  # type: address
            # Struct definition for weightedPoolConfig
            "weightedPoolConfig": {
                "name": None,  # type: string
                "symbol": None,  # type: string
                "tokens": None,  # type: address[]
                "amounts": None,  # type: uint256[]
                "weights": None,  # type: uint256[]
                "swapFeePercentage": None,  # type: uint256
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

            success = self.client.createWeightedPoolForLBP(
                lbpPool=execution_params.get("lbpPool"),
                weightedPoolConfig=execution_params.get("weightedPoolConfig"),
                sender=execution_params.get("sender"),
            )

            if success and self.on_createweightedpoolforlbp_performed:
                self.on_createweightedpoolforlbp_performed(
                    lbpPool=execution_params.get("lbpPool"),
                    weightedPoolConfig=execution_params.get("weightedPoolConfig"),
                    sender=execution_params.get("sender"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
                )

            return success

        except Exception as e:
            self.logger.error(
                f"createWeightedPoolForLBP action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class ExitPoolHandler:
    """Encapsulates the logic to execute a exitPool action."""

    def __init__(
        self,
        client: FjordLbpProxyV6Client,
        chain,
        logger: logging.Logger,
        on_exitpool_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_exitpool_performed = on_exitpool_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            "sender": None,  # Required: address that will send the transaction
            "pool": None,  # type: address
            "maxBPTTokenOut": None,  # type: uint256
            "isStandardFee": None,  # type: bool
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

            success = self.client.exitPool(
                pool=execution_params.get("pool"),
                maxBPTTokenOut=execution_params.get("maxBPTTokenOut"),
                isStandardFee=execution_params.get("isStandardFee"),
                sender=execution_params.get("sender"),
            )

            if success and self.on_exitpool_performed:
                self.on_exitpool_performed(
                    pool=execution_params.get("pool"),
                    maxBPTTokenOut=execution_params.get("maxBPTTokenOut"),
                    isStandardFee=execution_params.get("isStandardFee"),
                    sender=execution_params.get("sender"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
                )

            return success

        except Exception as e:
            self.logger.error(
                f"exitPool action failed for agent {agent.agent_id}: {e}", exc_info=True
            )
            return False


class RenounceOwnershipHandler:
    """Encapsulates the logic to execute a renounceOwnership action."""

    def __init__(
        self,
        client: FjordLbpProxyV6Client,
        chain,
        logger: logging.Logger,
        on_renounceownership_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_renounceownership_performed = on_renounceownership_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            "sender": None,  # Required: address that will send the transaction
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

            success = self.client.renounceOwnership(
                sender=execution_params.get("sender"),
            )

            if success and self.on_renounceownership_performed:
                self.on_renounceownership_performed(
                    sender=execution_params.get("sender"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
                )

            return success

        except Exception as e:
            self.logger.error(
                f"renounceOwnership action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class SetSwapEnabledHandler:
    """Encapsulates the logic to execute a setSwapEnabled action."""

    def __init__(
        self,
        client: FjordLbpProxyV6Client,
        chain,
        logger: logging.Logger,
        on_setswapenabled_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_setswapenabled_performed = on_setswapenabled_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            "sender": None,  # Required: address that will send the transaction
            "pool": None,  # type: address
            "swapEnabled": None,  # type: bool
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

            success = self.client.setSwapEnabled(
                pool=execution_params.get("pool"),
                swapEnabled=execution_params.get("swapEnabled"),
                sender=execution_params.get("sender"),
            )

            if success and self.on_setswapenabled_performed:
                self.on_setswapenabled_performed(
                    pool=execution_params.get("pool"),
                    swapEnabled=execution_params.get("swapEnabled"),
                    sender=execution_params.get("sender"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
                )

            return success

        except Exception as e:
            self.logger.error(
                f"setSwapEnabled action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class SkimHandler:
    """Encapsulates the logic to execute a skim action."""

    def __init__(
        self,
        client: FjordLbpProxyV6Client,
        chain,
        logger: logging.Logger,
        on_skim_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_skim_performed = on_skim_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            "sender": None,  # Required: address that will send the transaction
            "token": None,  # type: address
            "recipient": None,  # type: address
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

            success = self.client.skim(
                token=execution_params.get("token"),
                recipient=execution_params.get("recipient"),
                sender=execution_params.get("sender"),
            )

            if success and self.on_skim_performed:
                self.on_skim_performed(
                    token=execution_params.get("token"),
                    recipient=execution_params.get("recipient"),
                    sender=execution_params.get("sender"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
                )

            return success

        except Exception as e:
            self.logger.error(
                f"skim action failed for agent {agent.agent_id}: {e}", exc_info=True
            )
            return False


class TransferOwnershipHandler:
    """Encapsulates the logic to execute a transferOwnership action."""

    def __init__(
        self,
        client: FjordLbpProxyV6Client,
        chain,
        logger: logging.Logger,
        on_transferownership_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_transferownership_performed = on_transferownership_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            "sender": None,  # Required: address that will send the transaction
            "newOwner": None,  # type: address
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

            success = self.client.transferOwnership(
                newOwner=execution_params.get("newOwner"),
                sender=execution_params.get("sender"),
            )

            if success and self.on_transferownership_performed:
                self.on_transferownership_performed(
                    newOwner=execution_params.get("newOwner"),
                    sender=execution_params.get("sender"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
                )

            return success

        except Exception as e:
            self.logger.error(
                f"transferOwnership action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class TransferPoolOwnershipHandler:
    """Encapsulates the logic to execute a transferPoolOwnership action."""

    def __init__(
        self,
        client: FjordLbpProxyV6Client,
        chain,
        logger: logging.Logger,
        on_transferpoolownership_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_transferpoolownership_performed = on_transferpoolownership_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            "sender": None,  # Required: address that will send the transaction
            "pool": None,  # type: address
            "newOwner": None,  # type: address
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

            success = self.client.transferPoolOwnership(
                pool=execution_params.get("pool"),
                newOwner=execution_params.get("newOwner"),
                sender=execution_params.get("sender"),
            )

            if success and self.on_transferpoolownership_performed:
                self.on_transferpoolownership_performed(
                    pool=execution_params.get("pool"),
                    newOwner=execution_params.get("newOwner"),
                    sender=execution_params.get("sender"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
                )

            return success

        except Exception as e:
            self.logger.error(
                f"transferPoolOwnership action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class UpdateRecipientsHandler:
    """Encapsulates the logic to execute a updateRecipients action."""

    def __init__(
        self,
        client: FjordLbpProxyV6Client,
        chain,
        logger: logging.Logger,
        on_updaterecipients_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_updaterecipients_performed = on_updaterecipients_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Get parameter template showing expected structure.
        Returns a dict with all required parameters as empty placeholders.
        """
        # Template showing required parameters
        params = {
            "sender": None,  # Required: address that will send the transaction
            "recipients": None,  # type: address[]
            "recipientShareBPS": None,  # type: uint256[]
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

            success = self.client.updateRecipients(
                recipients=execution_params.get("recipients"),
                recipientShareBPS=execution_params.get("recipientShareBPS"),
                sender=execution_params.get("sender"),
            )

            if success and self.on_updaterecipients_performed:
                self.on_updaterecipients_performed(
                    recipients=execution_params.get("recipients"),
                    recipientShareBPS=execution_params.get("recipientShareBPS"),
                    sender=execution_params.get("sender"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
                )

            return success

        except Exception as e:
            self.logger.error(
                f"updateRecipients action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False
