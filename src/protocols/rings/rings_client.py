# src/protocols/rings/rings_client.py

from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from ape import Contract, chain
import logging
import yaml
from dataclasses import dataclass
from src.framework.data import CirclesDataCollector

logger = logging.getLogger(__name__)

class RingsClient:
    """
    Enhanced client for interacting with the Rings smart contract.
    Provides a comprehensive interface for contract operations including
    human registration, trust relationships, token operations, group creation, etc.
    """

    def __init__(
        self,
        contract_address: str,
        abi_path: str,
        gas_limits: Optional[Dict] = None,
        cache_config: Optional[Dict] = None,
        data_collector: Optional['CirclesDataCollector'] = None  # Add collector
    ):
        """Initialize Rings client with event logging"""
        print(f"RingsClient init - collector received: {data_collector is not None}")  # Debug
        self.contract = Contract(contract_address, abi=abi_path)
        self.collector = data_collector
        print(f"RingsClient init - self.collector set: {self.collector is not None}")  # Debug

        
        # Default gas limits
        self.gas_limits = gas_limits or {
            'register_human': 500000,
            'trust': 300000,
            'mint': 300000,
            'transfer': 300000,
            'create_group': 1000000,
            'register_organization': 800000,
            'wrap_token': 400000,
            'operate_flow': 1000000
        }
        
        # Optional caching
        self.cache_enabled = cache_config.get('enabled', True) if cache_config else True
        self.cache_ttl = cache_config.get('ttl', 100) if cache_config else 100
        self.cache = {
            'trust_network': {},
            'groups': set(),
            'balances': {},
            'humans': set(),
            'organizations': set(),
            'last_update': datetime.min,
            'current_block': 0
        }

        # Configuration dict
        self.config = {
            'trust_duration_days': 365
        }

        # Event handler callbacks
        self.on_transfer = None
        self.on_trust = None
        self.on_mint = None
        self.on_group_created = None
        self.on_organization_registered = None
        self.on_human_registered = None
        self.on_advanced_flag_set = None

    def _record_transaction_events(self, tx) -> None:
        """Record all events from a transaction"""
        if not (self.collector and tx):
            return
            
        try:
            print('---------------------')
            # Record each event in the transaction logs
            for i in range(len(tx.decode_logs())):
                decoded_log = tx.decode_logs()[i]
                log = tx.logs[i]
                print(decoded_log)
                self.collector.record_contract_event(
                    event_name=decoded_log.event_name,
                    block_number=tx.block_number,
                    block_timestamp=datetime.fromtimestamp(tx.timestamp),
                    transaction_hash=str(tx.txn_hash),
                    tx_from=str(tx.sender),
                    tx_to=str(tx.receiver),
                    log_index=log.get('logIndex'),
                    contract_address=str(decoded_log.contract_address),
                    topics=str(log.get('topics', [])),
                    event_data=str(decoded_log.event_arguments),
                    raw_data=str(log.get('data')),
                    indexed_values=str(decoded_log.indexed_arguments if hasattr(decoded_log, 'indexed_arguments') else None),
                    decoded_values=str(decoded_log.decoded_arguments if hasattr(decoded_log, 'decoded_arguments') else None)
                )
        except Exception as e:
            logger.error(f"Failed to record transaction events: {e}")

    def register_human(
        self,
        address: str, 
        inviter: Optional[str] = None,
        metadata_digest: Optional[bytes] = None
    ) -> bool:
        """Register a new human account"""
        try:
            inviter = inviter or "0x0000000000000000000000000000000000000000"
            metadata = metadata_digest or HexBytes(0)

            tx = self.contract.registerHuman(
                inviter,
                metadata,
                sender=address,
                gas_limit=self.gas_limits['register_human']
            )
            
            success = bool(tx and tx.status == 1)
            if success:
                # Cache update
                if self.cache_enabled:
                    self._update_cache('humans', {address: True})
                    
                # Record events
                print("About to record transaction events...")  # Debug
                self._record_transaction_events(tx)
                print("Finished recording transaction events") 

                # Callback
                if self.on_human_registered:
                    self.on_human_registered(
                        address=address,
                        inviter=inviter,
                        tx_hash=tx.txn_hash
                    )
            return success

        except Exception as e:
            logger.error(f"Failed to register human {address}: {e}")
            return False

    def register_organization(
        self,
        address: str,
        name: str,
        metadata_digest: Optional[bytes] = None
    ) -> bool:
        """Register an organization"""
        try:
            metadata = metadata_digest or HexBytes(0)
            tx = self.contract.registerOrganization(
                name,
                metadata,
                sender=address,
                gas_limit=self.gas_limits['register_organization']
            )
            success = bool(tx and tx.status == 1)
            if success:
                if self.cache_enabled:
                    self._update_cache('organizations', {address: True})
                    
                self._record_transaction_events(tx)

                if self.on_organization_registered:
                    self.on_organization_registered(address=address, name=name)
            return success
        except Exception as e:
            logger.error(f"Failed to register organization {address}: {e}")
            return False

    def register_group(
        self,
        address: str,
        mint_policy: str,
        name: str,
        symbol: str,
        metadata_digest: Optional[bytes] = None
    ) -> bool:
        """Register a new group"""
        try:
            metadata = metadata_digest or HexBytes(0)
            tx = self.contract.registerGroup(
                mint_policy,
                name,
                symbol,
                metadata,
                sender=address,
                gas_limit=self.gas_limits['create_group']
            )
            success = bool(tx and tx.status == 1)
            if success:
                if self.cache_enabled:
                    self._update_cache('groups', {address: True})
                    
                self._record_transaction_events(tx)

                if self.on_group_created:
                    self.on_group_created(
                        creator=address,
                        group_addr=address,
                        name=name,
                        tx_hash=tx.txn_hash
                    )
            return success
        except Exception as e:
            logger.error(f"Failed to register group {address}: {e}")
            return False

    def trust(
        self,
        truster: str,
        trustee: str,
        expiry: Optional[int] = None
    ) -> bool:
        """Establish trust relationship"""
        try:
            if not expiry:
                days = self.config.get('trust_duration_days', 365)
                expiry = int(chain.blocks.head.timestamp + days * 86400)
            
            tx = self.contract.trust(
                trustee,
                expiry,
                sender=truster,
                gas_limit=self.gas_limits['trust']
            )
            success = bool(tx and tx.status == 1)
            if success:
                if self.cache_enabled:
                    self._update_trust_cache(truster, trustee, expiry)
                    
                self._record_transaction_events(tx)

                if self.on_trust:
                    self.on_trust(
                        truster=truster,
                        trustee=trustee,
                        expiry=expiry,
                        tx_hash=tx.txn_hash
                    )
            return success
        except Exception as e:
            logger.error(f"Trust establishment failed: {e}")
            return False

    def personal_mint(self, address: str) -> bool:
        """Mint tokens"""
        try:
            issuance, start_period, end_period = self.calculate_issuance(address)
            if issuance == 0:
                return False

            can_mint, reason = self._check_mint_eligibility(address)
            if not can_mint:
                return False

            tx = self.contract.personalMint(
                sender=address,
                gas_limit=self.gas_limits['mint']
            )
            
            if not tx or tx.status != 1:
                return False

            self._record_transaction_events(tx)

            if self.on_mint:
                self.on_mint(
                    address=address,
                    amount=issuance,
                    tx_hash=tx.txn_hash
                )
            return True

        except Exception as e:
            logger.error(f"Mint failed: {e}")
            return False

    def transfer(
        self,
        from_address: str,
        to_address: str,
        amount: int,
        data: bytes = b""
    ) -> bool:
        """Transfer tokens"""
        try:
            token_id = int(from_address, 16)
            tx = self.contract.safeTransferFrom(
                from_address,
                to_address,
                token_id,
                amount,
                data,
                sender=from_address,
                gas_limit=self.gas_limits['transfer']
            )
            success = bool(tx and tx.status == 1)
            if success:
                if self.cache_enabled:
                    self._invalidate_balance_cache(from_address)
                    self._invalidate_balance_cache(to_address)
                    
                self._record_transaction_events(tx)

                if self.on_transfer:
                    self.on_transfer(
                        from_address,
                        to_address,
                        amount,
                        tx_hash=tx.txn_hash
                    )
            return success
        except Exception as e:
            logger.error(f"Transfer failed: {e}")
            return False

    def batch_transfer(
        self,
        from_address: str,
        to_address: str,
        token_ids: List[int],
        amounts: List[int],
        data: bytes = b""
    ) -> bool:
        """Batch token transfer"""
        try:
            tx = self.contract.safeBatchTransferFrom(
                from_address,
                to_address,
                token_ids,
                amounts,
                data,
                sender=from_address,
                gas_limit=self.gas_limits['transfer']
            )
            success = bool(tx and tx.status == 1)
            if success:
                if self.cache_enabled:
                    self._invalidate_balance_cache(from_address)
                    self._invalidate_balance_cache(to_address)
                    
                self._record_transaction_events(tx)
                
            return success
        except Exception as e:
            logger.error(f"Batch transfer failed: {e}")
            return False

    def group_mint(
        self,
        group: str,
        collateral_avatars: List[str],
        amounts: List[int],
        data: bytes = b""
    ) -> bool:
        """Mint group tokens"""
        try:
            tx = self.contract.groupMint(
                group,
                collateral_avatars,
                amounts,
                data,
                sender=group,
                gas_limit=self.gas_limits['mint']
            )
            success = bool(tx and tx.status == 1)
            if success:
                self._record_transaction_events(tx)
            return success
        except Exception as e:
            logger.error(f"Group mint failed: {e}")
            return False

    def operate_flow_matrix(
        self,
        vertices: List[str],
        flow_edges: List[Dict],
        streams: List[Dict],
        coordinates: bytes
    ) -> bool:
        """Execute flow matrix operation"""
        try:
            tx = self.contract.operateFlowMatrix(
                vertices,
                flow_edges,
                streams,
                coordinates,
                sender=vertices[0],
                gas_limit=self.gas_limits['operate_flow']
            )
            success = bool(tx and tx.status == 1)
            if success:
                self._record_transaction_events(tx)
            return success
        except Exception as e:
            logger.error(f"Flow matrix operation failed: {e}")
            return False

    # Status checking methods
    def is_human(self, address: str) -> bool:
        try:
            if self.cache_enabled and address in self.cache['humans']:
                return True
            return self.contract.isHuman(address)
        except Exception as e:
            logger.error(f"Failed to check human status: {e}")
            return False

    def is_trusted(self, truster: str, trustee: str) -> bool:
        try:
            cached_trust_expiry = self.cache['trust_network'].get(truster, {}).get(trustee)
            if cached_trust_expiry is not None:
                return cached_trust_expiry >= int(chain.blocks.head.timestamp)
            return self.contract.isTrusted(truster, trustee)
        except Exception as e:
            logger.error(f"Failed to check trust status: {e}")
            return False

    def is_group(self, address: str) -> bool:
        try:
            if self.cache_enabled and address in self.cache['groups']:
                return True
            return self.contract.isGroup(address)
        except Exception as e:
            logger.error(f"Failed to check group status: {e}")
            return False

    def is_organization(self, address: str) -> bool:
        try:
            if self.cache_enabled and address in self.cache['organizations']:
                return True
            return self.contract.isOrganization(address)
        except Exception as e:
            logger.error(f"Failed to check organization status: {e}")
            return False

    def is_stopped(self, address: str) -> bool:
        try:
            return self.contract.stopped(address)
        except Exception as e:
            logger.error(f"Failed to check stopped status: {e}")
            return False

    # Balance and issuance methods
    def get_balance(self, address: str) -> int:
        try:
            if self.cache_enabled:
                cached_balance = self.cache['balances'].get(address)
                if cached_balance is not None:
                    return cached_balance
            
            token_id = int(address, 16)
            balance = self.contract.balanceOf(address, token_id)
            
            if self.cache_enabled:
                self.cache['balances'][address] = balance
            
            return balance
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return 0

    def calculate_issuance(self, address: str) -> Tuple[int, int, int]:
        try:
            return self.contract.calculateIssuance(address)
        except Exception as e:
            logger.error(f"Failed to calculate issuance: {e}")
            return (0, 0, 0)

    # Advanced features
    def stop(self, address: str) -> bool:
        """Stop future minting from address"""
        try:
            tx = self.contract.stop(
                sender=address,
                gas_limit=self.gas_limits['transfer']
            )
            success = bool(tx and tx.status == 1)
            if success:
                self._record_transaction_events(tx)
            return success
        except Exception as e:
            logger.error(f"Failed to stop minting: {e}")
            return False

    def set_advanced_usage_flag(self, address: str, flag: bytes) -> bool:
        """Set advanced usage flags"""
        try:
            tx = self.contract.setAdvancedUsageFlag(
                flag,
                sender=address,
                gas_limit=self.gas_limits['transfer']
            )
            success = bool(tx and tx.status == 1)
            if success:
                self._record_transaction_events(tx)
                if self.on_advanced_flag_set:
                    self.on_advanced_flag_set(address, flag)
            return success
        except Exception as e:
            logger.error(f"Failed to set advanced flag: {e}")
            return False

    # Helper methods
    def _check_mint_eligibility(self, address: str) -> Tuple[bool, str]:
        """Check if address can mint"""
        try:
            if not self.is_human(address):
                return False, "Address not registered as human"
            if self.is_stopped(address):
                return False, "Minting is stopped for this address"

            issuance, start_period, end_period = self.calculate_issuance(address)
            if issuance == 0:
                return False, "No issuance available"
            
            current_time = chain.blocks.head.timestamp
            if current_time < start_period:
                return False, "Not yet eligible to mint"
            return True, ""
        except Exception as e:
            return False, str(e)

    # Cache management methods
    def _update_cache(self, cache_type: str, data: Dict):
        """Update cache entries"""
        if not self.cache_enabled:
            return
        if cache_type == 'balances':
            self.cache['balances'].update(data)
        elif cache_type == 'humans':
            self.cache['humans'] = self.cache['humans'] | set(data.keys())
        elif cache_type == 'organizations':
            self.cache['organizations'] = self.cache['organizations'] | set(data.keys())
        elif cache_type == 'groups':
            self.cache['groups'] = self.cache['groups'] | set(data.keys())
        
        self.cache['last_update'] = chain.blocks.head.timestamp
        self.cache['current_block'] = chain.blocks.head.number

    def _update_trust_cache(self, truster: str, trustee: str, expiry: int):
        """Update trust relationship cache"""
        if not self.cache_enabled:
            return
        if truster not in self.cache['trust_network']:
            self.cache['trust_network'][truster] = {}
        self.cache['trust_network'][truster][trustee] = expiry

    def _invalidate_balance_cache(self, address: str):
        """Remove cached balance"""
        if self.cache_enabled:
            self.cache['balances'].pop(address, None)

    def _should_refresh_cache(self) -> bool:
        """Check if cache needs refresh"""
        if not self.cache_enabled:
            return False
        age = chain.blocks.head.timestamp - self.cache['last_update']
        return age.total_seconds() > self.cache_ttl

    def refresh_cache(self):
        """Force refresh all cached data"""
        if not self.cache_enabled:
            return
            
        try:
            # Reset cache
            self.cache = {
                'trust_network': {},
                'groups': set(),
                'balances': {},
                'humans': set(),
                'organizations': set(),
                'last_update': chain.blocks.head.timestamp,
                'current_block': chain.blocks.head.number
            }
        except Exception as e:
            logger.error(f"Failed to refresh cache: {e}")

    def wrap_token(
        self, 
        avatar: str, 
        amount: int, 
        token_type: int,
        data: bytes = b""
    ) -> Optional[str]:
        """Wrap tokens as ERC20"""
        try:
            tx = self.contract.wrap(
                avatar,
                amount,
                token_type,
                sender=avatar,
                gas_limit=self.gas_limits['wrap_token']
            )
            
            success = bool(tx and tx.status == 1)
            if success:
                self._record_transaction_events(tx)
                if tx.return_value:
                    return tx.return_value  # Returns wrapped token address
            return None
            
        except Exception as e:
            logger.error(f"Failed to wrap tokens: {e}")
            return None

    # Utility methods
    def estimate_gas(self, method: str, **kwargs) -> int:
        """Estimate gas for operation"""
        try:
            if method in self.gas_limits:
                return self.gas_limits[method]
            return max(self.gas_limits.values())
        except Exception as e:
            logger.error(f"Failed to estimate gas: {e}")
            return 500000  # Safe default

    def update_gas_limits(self, new_limits: Dict[str, int]):
        """Update gas limits"""
        self.gas_limits.update(new_limits)

    def update_config(self, new_config: Dict):
        """Update configuration"""
        self.config.update(new_config)