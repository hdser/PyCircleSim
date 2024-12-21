# src/protocols/rings/rings_client.py

from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from ape import Contract, chain
import logging
import yaml
from dataclasses import dataclass

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
        cache_config: Optional[Dict] = None
    ):
        """
        Initialize the Rings client
        
        Args:
            contract_address: Address of deployed Rings contract
            abi_path: Path (str) to the contract ABI file or an actual ABI JSON
            gas_limits: Optional gas limits for different operations
            cache_config: Optional cache configuration
        """
        # Instantiate the contract
        self.contract = Contract(contract_address, abi=abi_path)
        
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

        # Configuration dict (e.g. for trust_duration_days) can be updated externally
        self.config = {
            'trust_duration_days': 365
        }


        # Event handler callbacks (set externally by simulation code)
        self.on_transfer = None
        self.on_trust = None
        self.on_mint = None
        self.on_group_created = None
        self.on_organization_registered = None
        self.on_human_registered = None
        self.on_advanced_flag_set = None

    def update_config(self, cli_params: Dict):
        """
        Update config with external parameters, e.g. trust_duration_days
        """
        for k, v in cli_params.items():
            if v is not None:
                self.config[k] = v

    # -------------------------------------------------------------------------
    # Registration Functions
    # -------------------------------------------------------------------------
    def register_human(
        self,
        address: str, 
        inviter: Optional[str] = None,
        metadata_digest: Optional[bytes] = None
    ) -> bool:
        """
        Register a new human account via the contract.
        """
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
                # Cache
                if self.cache_enabled:
                    self._update_cache('humans', {address: True})

       
                #if self.collector:
                for i in range(0, len(tx.decode_logs())):
                    decodes_log = tx.decode_logs()[i]
                    log = tx.logs[i]
        
                    topics_list = log['topics']
                    event_data_dict = decodes_log.event_arguments
                    event_name = decodes_log.event_name
                    contract_address = decodes_log.contract_address
                    print(topics_list, event_data_dict, event_name, contract_address)
                """
                    self.collector.record_contract_event(
                        event_name=event_name,
                        block_number=tx.block_number,
                        block_timestamp=tx.block_timestamp,
                        transaction_hash=tx.txn_hash,
                        tx_from=tx.sender,
                        tx_to=tx.receiver,
                        tx_index=tx.txn_index,
                        log_index=tx.log_index,
                        contract_address=contract_address,
                        topics=topics_list,          
                        event_data=event_data_dict,   
                        raw_data=None,              
                        indexed_values=None,         
                        decoded_values=None          
                    )
                """
                # Fire event callback
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
        """
        Register an organization address with a name.
        """
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
                if self.on_organization_registered:
                    self.on_organization_registered(
                        address=address,
                        name=name
                    )
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
        """
        Register a new group
        """
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

    # -------------------------------------------------------------------------
    # Trust & Flow
    # -------------------------------------------------------------------------
    def trust(
        self,
        truster: str,
        trustee: str,
        expiry: Optional[int] = None
    ) -> bool:
        """
        Establish a trust relationship from `truster` to `trustee`.
        """
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
                if self.on_trust:
                    self.on_trust(
                        truster=truster,
                        trustee=trustee,
                        expiry=expiry,
                        tx_hash=tx.txn_hash
                    )
            return success
        except Exception as e:
            logger.error(f"Failed to establish trust {truster} -> {trustee}: {e}", exc_info=True)
            return False

    def operate_flow_matrix(
        self,
        vertices: List[str],
        flow_edges: List[Dict],
        streams: List[Dict],
        coordinates: bytes
    ) -> bool:
        """
        Execute a flow matrix operation in the contract.
        """
        try:
            tx = self.contract.operateFlowMatrix(
                vertices,
                flow_edges,
                streams,
                coordinates,
                sender=vertices[0],
                gas_limit=self.gas_limits['operate_flow']
            )
            return bool(tx and tx.status == 1)
        except Exception as e:
            logger.error(f"Failed to operate flow matrix: {e}")
            return False

    # -------------------------------------------------------------------------
    # Minting
    # -------------------------------------------------------------------------
    def personal_mint(self, address: str) -> bool:
        """
        Attempt personalMint() for a human address.
        Verifies success by checking issuance amount matches.
        """
        try:
            # Get expected issuance first
            issuance, start_period, end_period = self.calculate_issuance(address)
            if issuance == 0:
                logger.debug(f"No issuance available for {address}")
                return False

            # Check eligibility
            can_mint, reason = self._check_mint_eligibility(address)
            if not can_mint:
                logger.error(f"Mint eligibility check failed for {address}: {reason}")
                return False

            # Execute mint
            tx = self.contract.personalMint(
                sender=address,
                gas_limit=self.gas_limits['mint']
            )
            
            if not tx or tx.status != 1:
                logger.error(f"Mint transaction failed for {address}")
                return False

            # Check transaction logs for PersonalMint event to verify amount
            for log in tx.decode_logs():
                print(log)
                if log.event_name == 'PersonalMint':
                    minted_amount = log.amount
                    if minted_amount == issuance:
                        # Fire callback with verified amount
                        if self.on_mint:
                            self.on_mint(
                                address=address,
                                amount=minted_amount,
                                tx_hash=tx.txn_hash
                            )
                        return True
                    else:
                        logger.error(
                            f"Mint amount mismatch for {address}\n"
                            f"Expected issuance: {issuance}\n"
                            f"Actual mint amount: {minted_amount}"
                        )
                        return False

            # If we get here, we didn't find the PersonalMint event
            logger.error(f"No PersonalMint event found in transaction logs for {address}")
            return False

        except Exception as e:
            logger.error(f"Mint failed for {address}: {e}")
            return False

    # -------------------------------------------------------------------------
    # Transfer
    # -------------------------------------------------------------------------
    def transfer(
        self,
        from_address: str,
        to_address: str,
        amount: int,
        data: bytes = b""
    ) -> bool:
        """
        Transfer tokens from `from_address` to `to_address`.
        """
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
                # Update local cache
                if self.cache_enabled:
                    from_balance = self.get_balance(from_address)
                    to_balance = self.get_balance(to_address)
                    self._update_cache('balances', {
                        from_address: from_balance,
                        to_address: to_balance
                    })
                # Fire callback
                if self.on_transfer:
                    self.on_transfer(
                        from_address,
                        to_address,
                        amount,
                        tx_hash=tx.txn_hash
                    )
            return success
        except Exception as e:
            logger.error(f"Failed transfer {from_address} -> {to_address}: {e}")
            return False

    # -------------------------------------------------------------------------
    # Additional Functions (batch_transfer, group_mint, wrap_token, etc.)
    # -------------------------------------------------------------------------
    def batch_transfer(
        self,
        from_address: str,
        to_address: str,
        token_ids: List[int],
        amounts: List[int],
        data: bytes = b""
    ) -> bool:
        """
        Perform a batch token transfer from one address to another.
        """
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
            if success and self.cache_enabled:
                self._invalidate_balance_cache(from_address)
                self._invalidate_balance_cache(to_address)
            return success
        except Exception as e:
            logger.error(f"Failed batch transfer {from_address} -> {to_address}: {e}")
            return False

    def group_mint(
        self,
        group: str,
        collateral_avatars: List[str],
        amounts: List[int],
        data: bytes = b""
    ) -> bool:
        """
        Mint group tokens using collateral from multiple avatars.
        """
        try:
            tx = self.contract.groupMint(
                group,
                collateral_avatars,
                amounts,
                data,
                sender=group,
                gas_limit=self.gas_limits['mint']
            )
            return bool(tx and tx.status == 1)
        except Exception as e:
            logger.error(f"Failed group mint for {group}: {e}")
            return False

    # -------------------------------------------------------------------------
    # Status Checking
    # -------------------------------------------------------------------------
    def is_human(self, address: str) -> bool:
        """
        Check if address is a registered human
        """
        try:
            if self.cache_enabled and address in self.cache['humans']:
                return True
            return self.contract.isHuman(address)
        except Exception as e:
            logger.error(f"Failed to check human status for {address}: {e}")
            return False

    def is_trusted(self, truster: str, trustee: str) -> bool:
        """
        Check if `truster` has an active trust relationship toward `trustee`.
        """
        try:
            # First check local cache
            cached_trust_expiry = self.cache['trust_network'].get(truster, {}).get(trustee)
            if cached_trust_expiry is not None:
                # If cached expiry is still in future, consider it trusted
                return cached_trust_expiry >= int(chain.blocks.head.timestamp)
            # Otherwise, call the contract
            return self.contract.isTrusted(truster, trustee)
        except Exception as e:
            logger.error(f"Failed to check trust status {truster} -> {trustee}: {e}")
            return False

    def is_group(self, address: str) -> bool:
        try:
            if self.cache_enabled and address in self.cache['groups']:
                return True
            return self.contract.isGroup(address)
        except Exception as e:
            logger.error(f"Failed to check group status for {address}: {e}")
            return False

    def is_organization(self, address: str) -> bool:
        try:
            if self.cache_enabled and address in self.cache['organizations']:
                return True
            return self.contract.isOrganization(address)
        except Exception as e:
            logger.error(f"Failed to check org status for {address}: {e}")
            return False

    def is_stopped(self, address: str) -> bool:
        """
        Check if address is "stopped" from future minting.
        """
        try:
            return self.contract.stopped(address)
        except Exception as e:
            logger.error(f"Failed to check stopped status for {address}: {e}")
            return False

    # -------------------------------------------------------------------------
    # Balances & Issuance
    # -------------------------------------------------------------------------
    def get_balance(self, address: str) -> int:
        """
        Return the user’s Circles balance in an ERC1155 sense (tokenId = address).
        """
        try:
            # Check cache
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
            logger.error(f"Failed to get balance for {address}: {e}")
            return 0

    def calculate_issuance(self, address: str) -> Tuple[int, int, int]:
        """
        get issuance, start_period, end_period from the contract
        """
        try:
            return self.contract.calculateIssuance(address)
        except Exception as e:
            logger.error(f"Failed to calculate issuance for {address}: {e}")
            return (0, 0, 0)

    # -------------------------------------------------------------------------
    # Advanced Features
    # -------------------------------------------------------------------------
    def stop(self, address: str) -> bool:
        """
        Prevent future minting from address
        """
        try:
            tx = self.contract.stop(
                sender=address,
                gas_limit=self.gas_limits['transfer']
            )
            return bool(tx and tx.status == 1)
        except Exception as e:
            logger.error(f"Failed to stop minting for {address}: {e}")
            return False

    def set_advanced_usage_flag(self, address: str, flag: bytes) -> bool:
        """
        Set advanced usage flags for an address
        """
        try:
            tx = self.contract.setAdvancedUsageFlag(
                flag,
                sender=address,
                gas_limit=self.gas_limits['transfer']
            )
            success = bool(tx and tx.status == 1)
            if success and self.on_advanced_flag_set:
                self.on_advanced_flag_set(address, flag)
            return success
        except Exception as e:
            logger.error(f"Failed to set advanced flag for {address}: {e}")
            return False

    # -------------------------------------------------------------------------
    # Helper: Check Mint Eligibility
    # -------------------------------------------------------------------------
    def _check_mint_eligibility(self, address: str) -> Tuple[bool, str]:
        """
        Basic check that user is human, not stopped, and issuance is nonzero.
        """
        try:
            if not self.is_human(address):
                return False, "Address not registered as human"
            if self.is_stopped(address):
                return False, "Minting is stopped for this address"

            issuance, start_period, end_period = self.calculate_issuance(address)
            if issuance == 0:
                return False, "No issuance available at this time"
            
            current_time = chain.blocks.head.timestamp
            if current_time < start_period:
                return False, "Not yet eligible to mint"
            # Optionally check end_period if your contract uses that logic
            return True, ""
        except Exception as e:
            return False, str(e)

    # -------------------------------------------------------------------------
    # Cache Management
    # -------------------------------------------------------------------------
    def _update_cache(self, cache_type: str, data: Dict):
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
        if not self.cache_enabled:
            return
        if truster not in self.cache['trust_network']:
            self.cache['trust_network'][truster] = {}
        self.cache['trust_network'][truster][trustee] = expiry

    def _invalidate_balance_cache(self, address: str):
        if self.cache_enabled:
            self.cache['balances'].pop(address, None)

    def _should_refresh_cache(self) -> bool:
        """
        If implementing advanced caching refresh logic, return True if we
        should re-pull data from the chain. 
        """
        if not self.cache_enabled:
            return False
        age = chain.blocks.head.timestamp - self.cache['last_update']
        # If more than self.cache_ttl seconds have passed, refresh
        return age.total_seconds() > self.cache_ttl
