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
        on_burn_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_burn_performed = on_burn_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        return {}

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False

            success = self.client.burn(
                sender=execution_params.get("sender"),
                _id=execution_params.get("_id"),
                _amount=execution_params.get("_amount"),
                _data=execution_params.get("_data"),
            )

            if success and self.on_burn_performed:
                self.on_burn_performed(
                    sender=execution_params.get("sender"),
                    _id=execution_params.get("_id"),
                    _amount=execution_params.get("_amount"),
                    _data=execution_params.get("_data"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
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
        on_calculateissuancewithcheck_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_calculateissuancewithcheck_performed = (
            on_calculateissuancewithcheck_performed
        )

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        return {}

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False

            success = self.client.calculateIssuanceWithCheck(
                sender=execution_params.get("sender"),
                _human=execution_params.get("_human"),
            )

            if success and self.on_calculateissuancewithcheck_performed:
                self.on_calculateissuancewithcheck_performed(
                    sender=execution_params.get("sender"),
                    _human=execution_params.get("_human"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
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
        on_groupmint_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_groupmint_performed = on_groupmint_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        return {}

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False

            success = self.client.groupMint(
                sender=execution_params.get("sender"),
                _group=execution_params.get("_group"),
                _collateralAvatars=execution_params.get("_collateralAvatars"),
                _amounts=execution_params.get("_amounts"),
                _data=execution_params.get("_data"),
            )

            if success and self.on_groupmint_performed:
                self.on_groupmint_performed(
                    sender=execution_params.get("sender"),
                    _group=execution_params.get("_group"),
                    _collateralAvatars=execution_params.get("_collateralAvatars"),
                    _amounts=execution_params.get("_amounts"),
                    _data=execution_params.get("_data"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
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
        on_migrate_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_migrate_performed = on_migrate_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        return {}

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False

            success = self.client.migrate(
                sender=execution_params.get("sender"),
                _owner=execution_params.get("_owner"),
                _avatars=execution_params.get("_avatars"),
                _amounts=execution_params.get("_amounts"),
            )

            if success and self.on_migrate_performed:
                self.on_migrate_performed(
                    sender=execution_params.get("sender"),
                    _owner=execution_params.get("_owner"),
                    _avatars=execution_params.get("_avatars"),
                    _amounts=execution_params.get("_amounts"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
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
        on_operateflowmatrix_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_operateflowmatrix_performed = on_operateflowmatrix_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        return {}

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False

            success = self.client.operateFlowMatrix(
                sender=execution_params.get("sender"),
                _flowVertices=execution_params.get("_flowVertices"),
                _flow=execution_params.get("_flow"),
                _streams=execution_params.get("_streams"),
                _packedCoordinates=execution_params.get("_packedCoordinates"),
            )

            if success and self.on_operateflowmatrix_performed:
                self.on_operateflowmatrix_performed(
                    sender=execution_params.get("sender"),
                    _flowVertices=execution_params.get("_flowVertices"),
                    _flow=execution_params.get("_flow"),
                    _streams=execution_params.get("_streams"),
                    _packedCoordinates=execution_params.get("_packedCoordinates"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
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
        on_personalmint_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_personalmint_performed = on_personalmint_performed

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

            if success and self.on_personalmint_performed:
                self.on_personalmint_performed(
                    sender=execution_params.get("sender"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
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
        on_registercustomgroup_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_registercustomgroup_performed = on_registercustomgroup_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        return {}

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False

            success = self.client.registerCustomGroup(
                sender=execution_params.get("sender"),
                _mint=execution_params.get("_mint"),
                _treasury=execution_params.get("_treasury"),
                _name=execution_params.get("_name"),
                _symbol=execution_params.get("_symbol"),
                _metadataDigest=execution_params.get("_metadataDigest"),
            )

            if success and self.on_registercustomgroup_performed:
                self.on_registercustomgroup_performed(
                    sender=execution_params.get("sender"),
                    _mint=execution_params.get("_mint"),
                    _treasury=execution_params.get("_treasury"),
                    _name=execution_params.get("_name"),
                    _symbol=execution_params.get("_symbol"),
                    _metadataDigest=execution_params.get("_metadataDigest"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
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
        on_registergroup_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_registergroup_performed = on_registergroup_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""
                        
        group_number = getattr(agent, 'group_count', 0) + 1
        creator_address, _ = agent.create_account()

        group_name = f"RingsGroup{creator_address[:4]}{group_number}"
        group_symbol = f"RG{creator_address[:2]}{group_number}"

        mint_policy = "0x79Cbc9C7077dF161b92a745345A6Ade3fC626A60"
        metadata_digest = HexBytes(0)

        return {
            '_name': group_name,
            '_symbol': group_symbol,
            '_mint': mint_policy,
            '_metadataDigest': metadata_digest,
            'sender': creator_address,
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
                sender=execution_params.get("sender"),
                _mint=execution_params.get("_mint"),
                _name=execution_params.get("_name"),
                _symbol=execution_params.get("_symbol"),
                _metadataDigest=execution_params.get("_metadataDigest"),
            )

            if success and self.on_registergroup_performed:
                self.on_registergroup_performed(
                    sender=execution_params.get("sender"),
                    _mint=execution_params.get("_mint"),
                    _name=execution_params.get("_name"),
                    _symbol=execution_params.get("_symbol"),
                    _metadataDigest=execution_params.get("_metadataDigest"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
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
        on_registerhuman_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_registerhuman_performed = on_registerhuman_performed

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
                sender=execution_params.get("sender"),
                _inviter=execution_params.get("_inviter"),
                _metadataDigest=execution_params.get("_metadataDigest"),
            )

            if success and self.on_registerhuman_performed:
                self.on_registerhuman_performed(
                    sender=execution_params.get("sender"),
                    _inviter=execution_params.get("_inviter"),
                    _metadataDigest=execution_params.get("_metadataDigest"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
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
        on_registerorganization_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_registerorganization_performed = on_registerorganization_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        return {}

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False

            success = self.client.registerOrganization(
                sender=execution_params.get("sender"),
                _name=execution_params.get("_name"),
                _metadataDigest=execution_params.get("_metadataDigest"),
            )

            if success and self.on_registerorganization_performed:
                self.on_registerorganization_performed(
                    sender=execution_params.get("sender"),
                    _name=execution_params.get("_name"),
                    _metadataDigest=execution_params.get("_metadataDigest"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
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
        on_safebatchtransferfrom_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_safebatchtransferfrom_performed = on_safebatchtransferfrom_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        return {}

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False

            success = self.client.safeBatchTransferFrom(
                sender=execution_params.get("sender"),
                _from=execution_params.get("_from"),
                _to=execution_params.get("_to"),
                _ids=execution_params.get("_ids"),
                _values=execution_params.get("_values"),
                _data=execution_params.get("_data"),
            )

            if success and self.on_safebatchtransferfrom_performed:
                self.on_safebatchtransferfrom_performed(
                    sender=execution_params.get("sender"),
                    _from=execution_params.get("_from"),
                    _to=execution_params.get("_to"),
                    _ids=execution_params.get("_ids"),
                    _values=execution_params.get("_values"),
                    _data=execution_params.get("_data"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
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
        on_safetransferfrom_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_safetransferfrom_performed = on_safetransferfrom_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        sender = random.choice(list(agent.accounts.keys()))
        receiver = random.choice(list(agent.trusted_addresses))
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

            if success and self.on_safetransferfrom_performed:
                self.on_safetransferfrom_performed(
                    sender=execution_params.get("sender"),
                    _from=execution_params.get("_from"),
                    _to=execution_params.get("_to"),
                    _id=execution_params.get("_id"),
                    _value=execution_params.get("_value"),
                    _data=execution_params.get("_data"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
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
        on_setadvancedusageflag_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_setadvancedusageflag_performed = on_setadvancedusageflag_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        return {}

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False

            success = self.client.setAdvancedUsageFlag(
                sender=execution_params.get("sender"),
                _flag=execution_params.get("_flag"),
            )

            if success and self.on_setadvancedusageflag_performed:
                self.on_setadvancedusageflag_performed(
                    sender=execution_params.get("sender"),
                    _flag=execution_params.get("_flag"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
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
        on_setapprovalforall_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_setapprovalforall_performed = on_setapprovalforall_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        return {}

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False

            success = self.client.setApprovalForAll(
                sender=execution_params.get("sender"),
                _operator=execution_params.get("_operator"),
                _approved=execution_params.get("_approved"),
            )

            if success and self.on_setapprovalforall_performed:
                self.on_setapprovalforall_performed(
                    sender=execution_params.get("sender"),
                    _operator=execution_params.get("_operator"),
                    _approved=execution_params.get("_approved"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
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
        on_stop_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_stop_performed = on_stop_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        return {}

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

            if success and self.on_stop_performed:
                self.on_stop_performed(
                    sender=execution_params.get("sender"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
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
        on_trust_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_trust_performed = on_trust_performed

    def _get_params(self, agent: BaseAgent, agent_manager: AgentManager) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        all_registered = set()
        # We iterate over known addresses and see if they're humans or orgs
        for addr in agent_manager.address_to_agent.keys():
            if self.client.isHuman(addr) or self.client.isOrganization(addr):
                all_registered.add(addr)

        already_trusted = agent.trusted_addresses or set()
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
        self, agent: BaseAgent, agent_manager:  Optional[AgentManager]= None, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent,agent_manager)
            if not execution_params:
                return False

            success = self.client.trust(
                sender=execution_params.get("sender"),
                _trustReceiver=execution_params.get("_trustReceiver"),
                _expiry=execution_params.get("_expiry"),
            )

            if success and self.on_trust_performed:
                self.on_trust_performed(
                    sender=execution_params.get("sender"),
                    _trustReceiver=execution_params.get("_trustReceiver"),
                    _expiry=execution_params.get("_expiry"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
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
        on_wrap_performed=None,
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        self.on_wrap_performed = on_wrap_performed

    def _get_params(self, agent: BaseAgent) -> Dict[str, Any]:
        """Get internally computed parameters if needed"""

        return {}

    def execute(
        self, agent: BaseAgent, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # Get internal params if no external params provided
            execution_params = params if params else self._get_params(agent)
            if not execution_params:
                return False

            success = self.client.wrap(
                sender=execution_params.get("sender"),
                _avatar=execution_params.get("_avatar"),
                _amount=execution_params.get("_amount"),
                _type=execution_params.get("_type"),
            )

            if success and self.on_wrap_performed:
                self.on_wrap_performed(
                    sender=execution_params.get("sender"),
                    _avatar=execution_params.get("_avatar"),
                    _amount=execution_params.get("_amount"),
                    _type=execution_params.get("_type"),
                    block=self.chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(self.chain.blocks.head.timestamp),
                )

            return success

        except Exception as e:
            self.logger.error(
                f"wrap action failed for agent {agent.agent_id}: {e}", exc_info=True
            )
            return False
