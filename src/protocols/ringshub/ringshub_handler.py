import random
from datetime import datetime
import logging
from typing import Optional, Dict, Any, Tuple

from ape import chain
from eth_pydantic_types import HexBytes
from src.framework.agents import BaseAgent, AgentManager
from src.protocols.ringshub import RingsHubClient


class BurnHandler:
    """Encapsulates the logic to execute a burn action."""

    def __init__(
        self,
        client: RingsHubClient,
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
            "sender": None,  # Required: address that will send the transaction
            "_id": None,  # type: uint256
            "_amount": None,  # type: uint256
            "_data": None,  # type: bytes
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

            success = self.client.burn(
                _id=execution_params.get("_id"),
                _amount=execution_params.get("_amount"),
                _data=execution_params.get("_data"),
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"burn action failed for agent {agent.agent_id}: {e}", exc_info=True
            )
            return False


class CalculateIssuanceWithCheckHandler:
    """Encapsulates the logic to execute a calculateIssuanceWithCheck action."""

    def __init__(
        self,
        client: RingsHubClient,
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
            "sender": None,  # Required: address that will send the transaction
            "_human": None,  # type: address
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

            success = self.client.calculateIssuanceWithCheck(
                _human=execution_params.get("_human"),
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"calculateIssuanceWithCheck action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class GroupMintHandler:
    """Encapsulates the logic to execute a groupMint action."""

    def __init__(
        self,
        client: RingsHubClient,
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
            "sender": None,  # Required: address that will send the transaction
            "_group": None,  # type: address
            "_collateralAvatars": None,  # type: address[]
            "_amounts": None,  # type: uint256[]
            "_data": None,  # type: bytes
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

            success = self.client.groupMint(
                _group=execution_params.get("_group"),
                _collateralAvatars=execution_params.get("_collateralAvatars"),
                _amounts=execution_params.get("_amounts"),
                _data=execution_params.get("_data"),
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"groupMint action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class MigrateHandler:
    """Encapsulates the logic to execute a migrate action."""

    def __init__(
        self,
        client: RingsHubClient,
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
            "sender": None,  # Required: address that will send the transaction
            "_owner": None,  # type: address
            "_avatars": None,  # type: address[]
            "_amounts": None,  # type: uint256[]
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

            success = self.client.migrate(
                _owner=execution_params.get("_owner"),
                _avatars=execution_params.get("_avatars"),
                _amounts=execution_params.get("_amounts"),
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"migrate action failed for agent {agent.agent_id}: {e}", exc_info=True
            )
            return False


class OperateFlowMatrixHandler:
    """Encapsulates the logic to execute a operateFlowMatrix action."""

    def __init__(
        self,
        client: RingsHubClient,
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
            "sender": None,  # Required: address that will send the transaction
            "_flowVertices": None,  # type: address[]
            "_flow": None,  # type: tuple[]
            "_streams": None,  # type: tuple[]
            "_packedCoordinates": None,  # type: bytes
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

            success = self.client.operateFlowMatrix(
                _flowVertices=execution_params.get("_flowVertices"),
                _flow=execution_params.get("_flow"),
                _streams=execution_params.get("_streams"),
                _packedCoordinates=execution_params.get("_packedCoordinates"),
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"operateFlowMatrix action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class PersonalMintHandler:
    """Encapsulates the logic to execute a personalMint action."""

    def __init__(
        self,
        client: RingsHubClient,
        chain,
        logger: logging.Logger,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""
        
        # Gather mintable accounts
        mintable_accounts = []
        for address in agent.accounts.keys():
            if self.client.isHuman(address) and not self.client.stopped(address):
                issuance, start_period, end_period = self.client.calculateIssuance(address)
                current_time = chain.blocks.head.timestamp
                if issuance != 0 and current_time >= start_period:
                    mintable_accounts.append(address)
        
        if not mintable_accounts:
            self.logger.debug(f"Agent {agent.agent_id} has no mintable accounts")
            return False

        # Pick one randomly
        address = random.choice(mintable_accounts)
        
        return {
            'sender': address,
        }

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False

            success = self.client.personalMint(
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"personalMint action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class RegisterCustomGroupHandler:
    """Encapsulates the logic to execute a registerCustomGroup action."""

    def __init__(
        self,
        client: RingsHubClient,
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
            "sender": None,  # Required: address that will send the transaction
            "_mint": None,  # type: address
            "_treasury": None,  # type: address
            "_name": None,  # type: string
            "_symbol": None,  # type: string
            "_metadataDigest": None,  # type: bytes32
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

            success = self.client.registerCustomGroup(
                _mint=execution_params.get("_mint"),
                _treasury=execution_params.get("_treasury"),
                _name=execution_params.get("_name"),
                _symbol=execution_params.get("_symbol"),
                _metadataDigest=execution_params.get("_metadataDigest"),
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"registerCustomGroup action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class RegisterGroupHandler:
    """Encapsulates the logic to execute a registerGroup action."""

    def __init__(
        self,
        client: RingsHubClient,
        chain,
        logger: logging.Logger,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""
                        
        group_number = getattr(agent, 'group_count', 0) + 1
        creator_address, _ = agent.create_account()

        group_name = f"RingsGroup{creator_address[:4]}{group_number}"
        group_symbol = f"RG{creator_address[:2]}{group_number}"

        mint_policy = "0x79Cbc9C7077dF161b92a745345A6Ade3fC626A60"
        metadata_digest = HexBytes(0)

        return {
            'sender': creator_address,
            '_name': group_name,
            '_symbol': group_symbol,
            '_mint': mint_policy,
            '_metadataDigest': metadata_digest
        }


    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False

            success = self.client.registerGroup(
                _mint=execution_params.get("_mint"),
                _name=execution_params.get("_name"),
                _symbol=execution_params.get("_symbol"),
                _metadataDigest=execution_params.get("_metadataDigest"),
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"registerGroup action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class RegisterHumanHandler:
    """Encapsulates the logic to execute a registerHuman action."""

    def __init__(
        self,
        client: RingsHubClient,
        chain,
        logger: logging.Logger,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        # If the agent needs more accounts, create one
        if len(agent.accounts) < agent.profile.target_account_count:
            agent.create_account()

        # Find any unregistered addresses
        unregistered = [
            addr for addr in agent.accounts.keys() if not self.client.isHuman(addr)
        ]

        if not unregistered:
            return {}

        address = random.choice(unregistered)
        inviter = "0x0000000000000000000000000000000000000000"
        metadata_digest = HexBytes(0)

        return {
            "sender": address,
            "_inviter": inviter,
            "_metadataDigest": metadata_digest,
        }

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False

            success = self.client.registerHuman(
                _inviter=execution_params.get("_inviter"),
                _metadataDigest=execution_params.get("_metadataDigest"),
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"registerHuman action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class RegisterOrganizationHandler:
    """Encapsulates the logic to execute a registerOrganization action."""

    def __init__(
        self,
        client: RingsHubClient,
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
            "sender": None,  # Required: address that will send the transaction
            "_name": None,  # type: string
            "_metadataDigest": None,  # type: bytes32
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

            success = self.client.registerOrganization(
                _name=execution_params.get("_name"),
                _metadataDigest=execution_params.get("_metadataDigest"),
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"registerOrganization action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class SafeBatchTransferFromHandler:
    """Encapsulates the logic to execute a safeBatchTransferFrom action."""

    def __init__(
        self,
        client: RingsHubClient,
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
            "sender": None,  # Required: address that will send the transaction
            "_from": None,  # type: address
            "_to": None,  # type: address
            "_ids": None,  # type: uint256[]
            "_values": None,  # type: uint256[]
            "_data": None,  # type: bytes
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

            success = self.client.safeBatchTransferFrom(
                _from=execution_params.get("_from"),
                _to=execution_params.get("_to"),
                _ids=execution_params.get("_ids"),
                _values=execution_params.get("_values"),
                _data=execution_params.get("_data"),
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"safeBatchTransferFrom action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class SafeTransferFromHandler:
    """Encapsulates the logic to execute a safeTransferFrom action."""

    def __init__(
        self,
        client: RingsHubClient,
        chain,
        logger: logging.Logger,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        trusted_addresses = agent.state.get('trusted_addresses', set())
        if not trusted_addresses:
            return {}  
    
        sender = random.choice(list(agent.accounts.keys()))
        receiver = random.choice(list(trusted_addresses))
        id = self.client.toTokenId(sender)
        balance = self.client.balanceOf(sender,id)

        if balance == 0:
            return {}

        amount = int(balance * random.uniform(0.1, 0.3))
        if amount == 0:
            return {}
        
        data = b""

        return {
            'sender': sender,
            '_from': sender,
            '_to': receiver,
            '_id': id,
            '_value': amount,
            '_data': data,
        }

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False

            success = self.client.safeTransferFrom(
                _from=execution_params.get("_from"),
                _to=execution_params.get("_to"),
                _id=execution_params.get("_id"),
                _value=execution_params.get("_value"),
                _data=execution_params.get("_data"),
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"safeTransferFrom action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class SetAdvancedUsageFlagHandler:
    """Encapsulates the logic to execute a setAdvancedUsageFlag action."""

    def __init__(
        self,
        client: RingsHubClient,
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
            "sender": None,  # Required: address that will send the transaction
            "_flag": None,  # type: bytes32
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

            success = self.client.setAdvancedUsageFlag(
                _flag=execution_params.get("_flag"),
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"setAdvancedUsageFlag action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class SetApprovalForAllHandler:
    """Encapsulates the logic to execute a setApprovalForAll action."""

    def __init__(
        self,
        client: RingsHubClient,
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
            "sender": None,  # Required: address that will send the transaction
            "_operator": None,  # type: address
            "_approved": None,  # type: bool
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

            success = self.client.setApprovalForAll(
                _operator=execution_params.get("_operator"),
                _approved=execution_params.get("_approved"),
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"setApprovalForAll action failed for agent {agent.agent_id}: {e}",
                exc_info=True,
            )
            return False


class StopHandler:
    """Encapsulates the logic to execute a stop action."""

    def __init__(
        self,
        client: RingsHubClient,
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

            success = self.client.stop(
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"stop action failed for agent {agent.agent_id}: {e}", exc_info=True
            )
            return False


class TrustHandler:
    """Encapsulates the logic to execute a trust action."""

    def __init__(
        self,
        client: RingsHubClient,
        chain,
        logger: logging.Logger,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        all_registered = set()
        # We iterate over known addresses and see if they're humans or orgs
        for addr in agent.accounts.keys():
            if self.client.isHuman(addr) or self.client.isOrganization(addr):
                all_registered.add(addr)

        already_trusted = agent.state['trusted_addresses'] or set()
        potential_trustees = list(
            all_registered
            - already_trusted
            - set(agent.accounts.keys())
        )

        if not potential_trustees:
            return {}

        truster = random.choice(list(agent.accounts.keys()))
        trustee = random.choice(potential_trustees)
        expiry = int(chain.blocks.head.timestamp + 365 * 24 * 60 * 60)

        return {
            'sender': truster,
            '_trustReceiver': trustee,
            '_expiry': expiry,
        }

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False

            success = self.client.trust(
                _trustReceiver=execution_params.get("_trustReceiver"),
                _expiry=execution_params.get("_expiry"),
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"trust action failed for agent {agent.agent_id}: {e}", exc_info=True
            )
            return False


class WrapHandler:
    """Encapsulates the logic to execute a wrap action."""

    def __init__(
        self,
        client: RingsHubClient,
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
        avatar = sender
        id = self.client.toTokenId(avatar)
        balance = self.client.balanceOf(avatar,id)
        if balance == 0:
            return {}
        amount = int(balance/10.0)
        type = 0
        # Template showing required parameters
        params = {
            "sender": sender,
            "_avatar": avatar,
            "_amount": amount,
            "_type": type
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

            success = self.client.wrap(
                _avatar=execution_params.get("_avatar"),
                _amount=execution_params.get("_amount"),
                _type=execution_params.get("_type"),
                sender=execution_params.get("sender"),
            )

            return success

        except Exception as e:
            self.logger.error(
                f"wrap action failed for agent {agent.agent_id}: {e}", exc_info=True
            )
            return False
