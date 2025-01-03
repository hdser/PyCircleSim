from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from ape import Contract, chain
from src.framework.data import CirclesDataCollector
from src.framework.logging import get_logger

logger = get_logger(__name__)


class RingsHubClient:
    """Client interface for RingsHub contract"""

    def __init__(
        self,
        contract_address: str,
        abi_path: str,
        gas_limits: Optional[Dict] = None,
        cache_config: Optional[Dict] = None,
        data_collector: Optional["CirclesDataCollector"] = None,
    ):
        self.contract = Contract(contract_address, abi=abi_path)
        self.collector = data_collector

        # Default gas limits
        self.gas_limits = gas_limits or {
            "advancedUsageFlags": 300000,
            "avatars": 300000,
            "balanceOf": 300000,
            "balanceOfBatch": 300000,
            "balanceOfOnDay": 300000,
            "burn": 300000,
            "calculateIssuance": 300000,
            "calculateIssuanceWithCheck": 300000,
            "convertDemurrageToInflationaryValue": 300000,
            "convertInflationaryToDemurrageValue": 300000,
            "day": 300000,
            "groupMint": 300000,
            "inflationDayZero": 300000,
            "invitationOnlyTime": 300000,
            "isApprovedForAll": 300000,
            "isGroup": 300000,
            "isHuman": 300000,
            "isOrganization": 300000,
            "isPermittedFlow": 300000,
            "isTrusted": 300000,
            "migrate": 300000,
            "mintPolicies": 300000,
            "name": 300000,
            "operateFlowMatrix": 300000,
            "personalMint": 300000,
            "registerCustomGroup": 300000,
            "registerGroup": 300000,
            "registerHuman": 300000,
            "registerOrganization": 300000,
            "safeBatchTransferFrom": 300000,
            "safeTransferFrom": 300000,
            "setAdvancedUsageFlag": 300000,
            "setApprovalForAll": 300000,
            "stop": 300000,
            "stopped": 300000,
            "supportsInterface": 300000,
            "symbol": 300000,
            "toTokenId": 300000,
            "totalSupply": 300000,
            "treasuries": 300000,
            "trust": 300000,
            "trustMarkers": 300000,
            "uri": 300000,
            "wrap": 300000,
        }

        # Optional caching
        self.cache_enabled = cache_config.get("enabled", True) if cache_config else True
        self.cache_ttl = cache_config.get("ttl", 100) if cache_config else 100
        self.cache = {"last_update": datetime.min, "current_block": 0}

        # Initialize event handlers for all events and non-view functions

        self.on_ApprovalForAll = None

        self.on_DiscountCost = None

        self.on_FlowEdgesScopeLastEnded = None

        self.on_FlowEdgesScopeSingleStarted = None

        self.on_GroupMint = None

        self.on_PersonalMint = None

        self.on_RegisterGroup = None

        self.on_RegisterHuman = None

        self.on_RegisterOrganization = None

        self.on_SetAdvancedUsageFlag = None

        self.on_Stopped = None

        self.on_StreamCompleted = None

        self.on_TransferBatch = None

        self.on_TransferSingle = None

        self.on_Trust = None

        self.on_URI = None

        self.on_burn = None

        self.on_calculateIssuanceWithCheck = None

        self.on_groupMint = None

        self.on_migrate = None

        self.on_operateFlowMatrix = None

        self.on_personalMint = None

        self.on_registerCustomGroup = None

        self.on_registerGroup = None

        self.on_registerHuman = None

        self.on_registerOrganization = None

        self.on_safeBatchTransferFrom = None

        self.on_safeTransferFrom = None

        self.on_setAdvancedUsageFlag = None

        self.on_setApprovalForAll = None

        self.on_stop = None

        self.on_trust = None

        self.on_wrap = None

    def advancedUsageFlags(self, param0: str) -> bytes:
        """advancedUsageFlags implementation"""
        try:
            return self.contract.advancedUsageFlags(
                param0,
            )
        except Exception as e:
            logger.error(f"advancedUsageFlags failed: {e}")
            return None

    def avatars(self, param0: str) -> str:
        """avatars implementation"""
        try:
            return self.contract.avatars(
                param0,
            )
        except Exception as e:
            logger.error(f"avatars failed: {e}")
            return None

    def balanceOf(self, _account: str, _id: int) -> int:
        """balanceOf implementation"""
        try:
            return self.contract.balanceOf(
                _account,
                _id,
            )
        except Exception as e:
            logger.error(f"balanceOf failed: {e}")
            return None

    def balanceOfBatch(self, _accounts: List[str], _ids: List[int]) -> List[int]:
        """balanceOfBatch implementation"""
        try:
            return self.contract.balanceOfBatch(
                _accounts,
                _ids,
            )
        except Exception as e:
            logger.error(f"balanceOfBatch failed: {e}")
            return None

    def balanceOfOnDay(self, _account: str, _id: int, _day: int) -> Tuple[int, int]:
        """balanceOfOnDay implementation"""
        try:
            return self.contract.balanceOfOnDay(
                _account,
                _id,
                _day,
            )
        except Exception as e:
            logger.error(f"balanceOfOnDay failed: {e}")
            return None

    def burn(self, sender: str, _id: int, _amount: int, _data: bytes) -> bool:
        """burn implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.burn(_id, _amount, _data, sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_burn:
                    self.on_burn(
                        _id=_id, _amount=_amount, _data=_data, tx_hash=tx.txn_hash
                    )
            return success

        except Exception as e:
            logger.error(f"burn failed: {e}")
            return False

    def calculateIssuance(self, _human: str) -> Tuple[int, int, int]:
        """calculateIssuance implementation"""
        try:
            return self.contract.calculateIssuance(
                _human,
            )
        except Exception as e:
            logger.error(f"calculateIssuance failed: {e}")
            return None

    def calculateIssuanceWithCheck(self, sender: str, _human: str) -> bool:
        """calculateIssuanceWithCheck implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.calculateIssuanceWithCheck(_human, sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_calculateIssuanceWithCheck:
                    self.on_calculateIssuanceWithCheck(
                        _human=_human, tx_hash=tx.txn_hash
                    )
            return success

        except Exception as e:
            logger.error(f"calculateIssuanceWithCheck failed: {e}")
            return False

    def convertDemurrageToInflationaryValue(
        self, _demurrageValue: int, _dayUpdated: int
    ) -> int:
        """convertDemurrageToInflationaryValue implementation"""
        try:
            return self.contract.convertDemurrageToInflationaryValue(
                _demurrageValue,
                _dayUpdated,
            )
        except Exception as e:
            logger.error(f"convertDemurrageToInflationaryValue failed: {e}")
            return None

    def convertInflationaryToDemurrageValue(
        self, _inflationaryValue: int, _day: int
    ) -> int:
        """convertInflationaryToDemurrageValue implementation"""
        try:
            return self.contract.convertInflationaryToDemurrageValue(
                _inflationaryValue,
                _day,
            )
        except Exception as e:
            logger.error(f"convertInflationaryToDemurrageValue failed: {e}")
            return None

    def day(self, _timestamp: int) -> int:
        """day implementation"""
        try:
            return self.contract.day(
                _timestamp,
            )
        except Exception as e:
            logger.error(f"day failed: {e}")
            return None

    def groupMint(
        self,
        sender: str,
        _group: str,
        _collateralAvatars: List[str],
        _amounts: List[int],
        _data: bytes,
    ) -> bool:
        """groupMint implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.groupMint(
                _group, _collateralAvatars, _amounts, _data, sender=sender
            )

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_groupMint:
                    self.on_groupMint(
                        _group=_group,
                        _collateralAvatars=_collateralAvatars,
                        _amounts=_amounts,
                        _data=_data,
                        tx_hash=tx.txn_hash,
                    )
            return success

        except Exception as e:
            logger.error(f"groupMint failed: {e}")
            return False

    def inflationDayZero(
        self,
    ) -> int:
        """inflationDayZero implementation"""
        try:
            return self.contract.inflationDayZero()
        except Exception as e:
            logger.error(f"inflationDayZero failed: {e}")
            return None

    def invitationOnlyTime(
        self,
    ) -> int:
        """invitationOnlyTime implementation"""
        try:
            return self.contract.invitationOnlyTime()
        except Exception as e:
            logger.error(f"invitationOnlyTime failed: {e}")
            return None

    def isApprovedForAll(self, _account: str, _operator: str) -> bool:
        """isApprovedForAll implementation"""
        try:
            return self.contract.isApprovedForAll(
                _account,
                _operator,
            )
        except Exception as e:
            logger.error(f"isApprovedForAll failed: {e}")
            return None

    def isGroup(self, _group: str) -> bool:
        """isGroup implementation"""
        try:
            return self.contract.isGroup(
                _group,
            )
        except Exception as e:
            logger.error(f"isGroup failed: {e}")
            return None

    def isHuman(self, _human: str) -> bool:
        """isHuman implementation"""
        try:
            return self.contract.isHuman(
                _human,
            )
        except Exception as e:
            logger.error(f"isHuman failed: {e}")
            return None

    def isOrganization(self, _organization: str) -> bool:
        """isOrganization implementation"""
        try:
            return self.contract.isOrganization(
                _organization,
            )
        except Exception as e:
            logger.error(f"isOrganization failed: {e}")
            return None

    def isPermittedFlow(self, _from: str, _to: str, _circlesAvatar: str) -> bool:
        """isPermittedFlow implementation"""
        try:
            return self.contract.isPermittedFlow(
                _from,
                _to,
                _circlesAvatar,
            )
        except Exception as e:
            logger.error(f"isPermittedFlow failed: {e}")
            return None

    def isTrusted(self, _truster: str, _trustee: str) -> bool:
        """isTrusted implementation"""
        try:
            return self.contract.isTrusted(
                _truster,
                _trustee,
            )
        except Exception as e:
            logger.error(f"isTrusted failed: {e}")
            return None

    def migrate(
        self, sender: str, _owner: str, _avatars: List[str], _amounts: List[int]
    ) -> bool:
        """migrate implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.migrate(_owner, _avatars, _amounts, sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_migrate:
                    self.on_migrate(
                        _owner=_owner,
                        _avatars=_avatars,
                        _amounts=_amounts,
                        tx_hash=tx.txn_hash,
                    )
            return success

        except Exception as e:
            logger.error(f"migrate failed: {e}")
            return False

    def mintPolicies(self, param0: str) -> str:
        """mintPolicies implementation"""
        try:
            return self.contract.mintPolicies(
                param0,
            )
        except Exception as e:
            logger.error(f"mintPolicies failed: {e}")
            return None

    def name(
        self,
    ) -> str:
        """name implementation"""
        try:
            return self.contract.name()
        except Exception as e:
            logger.error(f"name failed: {e}")
            return None

    def operateFlowMatrix(
        self,
        sender: str,
        _flowVertices: List[str],
        _flow: List[Any],
        _streams: List[Any],
        _packedCoordinates: bytes,
    ) -> bool:
        """operateFlowMatrix implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.operateFlowMatrix(
                _flowVertices, _flow, _streams, _packedCoordinates, sender=sender
            )

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_operateFlowMatrix:
                    self.on_operateFlowMatrix(
                        _flowVertices=_flowVertices,
                        _flow=_flow,
                        _streams=_streams,
                        _packedCoordinates=_packedCoordinates,
                        tx_hash=tx.txn_hash,
                    )
            return success

        except Exception as e:
            logger.error(f"operateFlowMatrix failed: {e}")
            return False

    def personalMint(
        self,
        sender: str,
    ) -> bool:
        """personalMint implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.personalMint(sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_personalMint:
                    self.on_personalMint(tx_hash=tx.txn_hash)
            return success

        except Exception as e:
            logger.error(f"personalMint failed: {e}")
            return False

    def registerCustomGroup(
        self,
        sender: str,
        _mint: str,
        _treasury: str,
        _name: str,
        _symbol: str,
        _metadataDigest: bytes,
    ) -> bool:
        """registerCustomGroup implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.registerCustomGroup(
                _mint, _treasury, _name, _symbol, _metadataDigest, sender=sender
            )

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_registerCustomGroup:
                    self.on_registerCustomGroup(
                        _mint=_mint,
                        _treasury=_treasury,
                        _name=_name,
                        _symbol=_symbol,
                        _metadataDigest=_metadataDigest,
                        tx_hash=tx.txn_hash,
                    )
            return success

        except Exception as e:
            logger.error(f"registerCustomGroup failed: {e}")
            return False

    def registerGroup(
        self, sender: str, _mint: str, _name: str, _symbol: str, _metadataDigest: bytes
    ) -> bool:
        """registerGroup implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.registerGroup(
                _mint, _name, _symbol, _metadataDigest, sender=sender
            )

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_registerGroup:
                    self.on_registerGroup(
                        _mint=_mint,
                        _name=_name,
                        _symbol=_symbol,
                        _metadataDigest=_metadataDigest,
                        tx_hash=tx.txn_hash,
                    )
            return success

        except Exception as e:
            logger.error(f"registerGroup failed: {e}")
            return False

    def registerHuman(self, sender: str, _inviter: str, _metadataDigest: bytes) -> bool:
        """registerHuman implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.registerHuman(_inviter, _metadataDigest, sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_registerHuman:
                    self.on_registerHuman(
                        _inviter=_inviter,
                        _metadataDigest=_metadataDigest,
                        tx_hash=tx.txn_hash,
                    )
            return success

        except Exception as e:
            logger.error(f"registerHuman failed: {e}")
            return False

    def registerOrganization(
        self, sender: str, _name: str, _metadataDigest: bytes
    ) -> bool:
        """registerOrganization implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.registerOrganization(
                _name, _metadataDigest, sender=sender
            )

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_registerOrganization:
                    self.on_registerOrganization(
                        _name=_name,
                        _metadataDigest=_metadataDigest,
                        tx_hash=tx.txn_hash,
                    )
            return success

        except Exception as e:
            logger.error(f"registerOrganization failed: {e}")
            return False

    def safeBatchTransferFrom(
        self,
        sender: str,
        _from: str,
        _to: str,
        _ids: List[int],
        _values: List[int],
        _data: bytes,
    ) -> bool:
        """safeBatchTransferFrom implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.safeBatchTransferFrom(
                _from, _to, _ids, _values, _data, sender=sender
            )

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_safeBatchTransferFrom:
                    self.on_safeBatchTransferFrom(
                        _from=_from,
                        _to=_to,
                        _ids=_ids,
                        _values=_values,
                        _data=_data,
                        tx_hash=tx.txn_hash,
                    )
            return success

        except Exception as e:
            logger.error(f"safeBatchTransferFrom failed: {e}")
            return False

    def safeTransferFrom(
        self, sender: str, _from: str, _to: str, _id: int, _value: int, _data: bytes
    ) -> bool:
        """safeTransferFrom implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.safeTransferFrom(
                _from, _to, _id, _value, _data, sender=sender
            )

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_safeTransferFrom:
                    self.on_safeTransferFrom(
                        _from=_from,
                        _to=_to,
                        _id=_id,
                        _value=_value,
                        _data=_data,
                        tx_hash=tx.txn_hash,
                    )
            return success

        except Exception as e:
            logger.error(f"safeTransferFrom failed: {e}")
            return False

    def setAdvancedUsageFlag(self, sender: str, _flag: bytes) -> bool:
        """setAdvancedUsageFlag implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.setAdvancedUsageFlag(_flag, sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_setAdvancedUsageFlag:
                    self.on_setAdvancedUsageFlag(_flag=_flag, tx_hash=tx.txn_hash)
            return success

        except Exception as e:
            logger.error(f"setAdvancedUsageFlag failed: {e}")
            return False

    def setApprovalForAll(self, sender: str, _operator: str, _approved: bool) -> bool:
        """setApprovalForAll implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.setApprovalForAll(_operator, _approved, sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_setApprovalForAll:
                    self.on_setApprovalForAll(
                        _operator=_operator, _approved=_approved, tx_hash=tx.txn_hash
                    )
            return success

        except Exception as e:
            logger.error(f"setApprovalForAll failed: {e}")
            return False

    def stop(
        self,
        sender: str,
    ) -> bool:
        """stop implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.stop(sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_stop:
                    self.on_stop(tx_hash=tx.txn_hash)
            return success

        except Exception as e:
            logger.error(f"stop failed: {e}")
            return False

    def stopped(self, _human: str) -> bool:
        """stopped implementation"""
        try:
            return self.contract.stopped(
                _human,
            )
        except Exception as e:
            logger.error(f"stopped failed: {e}")
            return None

    def supportsInterface(self, _interfaceId: Any) -> bool:
        """supportsInterface implementation"""
        try:
            return self.contract.supportsInterface(
                _interfaceId,
            )
        except Exception as e:
            logger.error(f"supportsInterface failed: {e}")
            return None

    def symbol(
        self,
    ) -> str:
        """symbol implementation"""
        try:
            return self.contract.symbol()
        except Exception as e:
            logger.error(f"symbol failed: {e}")
            return None

    def toTokenId(self, _avatar: str) -> int:
        """toTokenId implementation"""
        try:
            return self.contract.toTokenId(
                _avatar,
            )
        except Exception as e:
            logger.error(f"toTokenId failed: {e}")
            return None

    def totalSupply(self, _id: int) -> int:
        """totalSupply implementation"""
        try:
            return self.contract.totalSupply(
                _id,
            )
        except Exception as e:
            logger.error(f"totalSupply failed: {e}")
            return None

    def treasuries(self, param0: str) -> str:
        """treasuries implementation"""
        try:
            return self.contract.treasuries(
                param0,
            )
        except Exception as e:
            logger.error(f"treasuries failed: {e}")
            return None

    def trust(self, sender: str, _trustReceiver: str, _expiry: int) -> bool:
        """trust implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.trust(_trustReceiver, _expiry, sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_trust:
                    self.on_trust(
                        _trustReceiver=_trustReceiver,
                        _expiry=_expiry,
                        tx_hash=tx.txn_hash,
                    )
            return success

        except Exception as e:
            logger.error(f"trust failed: {e}")
            return False

    def trustMarkers(self, param0: str, param1: str) -> Tuple[str, int]:
        """trustMarkers implementation"""
        try:
            return self.contract.trustMarkers(
                param0,
                param1,
            )
        except Exception as e:
            logger.error(f"trustMarkers failed: {e}")
            return None

    def uri(self, param0: int) -> str:
        """uri implementation"""
        try:
            return self.contract.uri(
                param0,
            )
        except Exception as e:
            logger.error(f"uri failed: {e}")
            return None

    def wrap(self, sender: str, _avatar: str, _amount: int, _type: Any) -> bool:
        """wrap implementation"""
        try:
            # Base arguments for contract call
            tx = self.contract.wrap(_avatar, _amount, _type, sender=sender)

            success = bool(tx and tx.status == 1)
            if success:
                if self.collector:
                    self.collector.record_transaction_events(tx)

                if self.on_wrap:
                    self.on_wrap(
                        _avatar=_avatar,
                        _amount=_amount,
                        _type=_type,
                        tx_hash=tx.txn_hash,
                    )
            return success

        except Exception as e:
            logger.error(f"wrap failed: {e}")
            return False
