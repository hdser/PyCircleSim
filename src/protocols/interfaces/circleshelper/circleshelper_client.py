from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from ape import Contract, chain
from src.framework.data import DataCollector
from src.framework.logging import get_logger

logger = get_logger(__name__)


class CirclesHelperClient:
    """Client interface for CirclesHelper contract"""

    def __init__(
        self,
        contract_address: str,
        abi_path: str,
        gas_limits: Optional[Dict] = None,
        data_collector: Optional["DataCollector"] = None,
    ):
        self.contract = Contract(contract_address, abi=abi_path)
        self.collector = data_collector

        # Default gas limits
        self.gas_limits = gas_limits or {
            "getAllDataForUser": 300000,
            "v1Hub": 300000,
            "v2Hub": 300000,
        }

    def getAllDataForUser(self, user: str) -> Tuple[Any, Any, List[Any]]:
        """getAllDataForUser implementation

        Args:
            user: address - Contract parameter

        """
        try:
            return self.contract.getAllDataForUser(user)
        except Exception as e:
            logger.error(f"getAllDataForUser failed: {e}")
            return None

    def v1Hub(
        self,
    ) -> str:
        """v1Hub implementation"""
        try:
            return self.contract.v1Hub()
        except Exception as e:
            logger.error(f"v1Hub failed: {e}")
            return None

    def v2Hub(
        self,
    ) -> str:
        """v2Hub implementation"""
        try:
            return self.contract.v2Hub()
        except Exception as e:
            logger.error(f"v2Hub failed: {e}")
            return None
