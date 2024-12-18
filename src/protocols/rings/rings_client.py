from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from eth_account import Account
from ape import Contract, accounts, chain
import logging
import yaml
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

class RingsClient:
    """
    Enhanced client for interacting with the Rings smart contract.
    Provides comprehensive interface for all contract operations including group management,
    advanced usage flags, and token operations.
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
            abi_path: Path to contract ABI file
            gas_limits: Optional gas limits for different operations
            cache_config: Optional cache configuration
        """
        self.contract = Contract(contract_address, abi=abi_path)
        
        # Set default gas limits if none provided
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
        
        # Initialize cache with provided config or defaults
        self.cache_enabled = cache_config.get('enabled', True) if cache_config else True
        self.cache_ttl = cache_config.get('ttl', 100) if cache_config else 100
        
        # Initialize cache storage
        self.cache = {
            'trust_network': {},
            'groups': set(),
            'balances': {},
            'humans': set(),
            'organizations': set(),
            'last_update': datetime.min,
            'current_block': 0
        }
        
        # Event handlers
        self.on_transfer = None
        self.on_trust = None
        self.on_mint = None
        self.on_group_created = None
        self.on_organization_registered = None
        self.on_human_registered = None
        self.on_advanced_flag_set = None

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            return {}

    def update_config(self, cli_params: Dict):
        """Update configuration with CLI parameters"""
        # CLI parameters take precedence over YAML config
        for key, value in cli_params.items():
            if value is not None:  # Only update if parameter was provided
                self.config[key] = value

    # Core Registration Functions

    def register_human(self, address: str, 
                      inviter: Optional[str] = None,
                      metadata_digest: Optional[bytes] = None) -> bool:
        """
        Register a new human account
        
        Args:
            address: Address to register as human
            inviter: Optional inviter address
            metadata_digest: Optional metadata digest
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
                if self.cache_enabled:
                    self._update_cache('humans', {address: True})
                if self.on_human_registered:
                    self.on_human_registered(address, inviter)
                    
            return success
            
        except Exception as e:
            logger.error(f"Failed to register human {address}: {e}")
            return False

    def register_organization(self, address: str, name: str, 
                            metadata_digest: Optional[bytes] = None) -> bool:
        """
        Register an organization
        
        Args:
            address: Organization address
            name: Organization name
            metadata_digest: Optional metadata digest
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
                    self.on_organization_registered(address, name)
                    
            return success
            
        except Exception as e:
            logger.error(f"Failed to register organization {address}: {e}")
            return False

    def register_group(self, address: str, mint_policy: str, name: str, 
                      symbol: str, metadata_digest: Optional[bytes] = None) -> bool:
        """
        Register a new group
        
        Args:
            address: Group address
            mint_policy: Mint policy contract address
            name: Group name
            symbol: Group symbol
            metadata_digest: Optional metadata digest
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
                    self.on_group_created(address, mint_policy, name, symbol)
                    
            return success
            
        except Exception as e:
            logger.error(f"Failed to register group {address}: {e}")
            return False

    # Trust and Flow Functions

    def trust(self, truster: Account, trustee: str, expiry: Optional[int] = None) -> bool:
        """
        Establish trust relationship between accounts
        
        Args:
            truster: Account object giving trust (for transaction signing)
            trustee: Address receiving trust
            expiry: Optional trust expiry timestamp
        """
        try:
            if not expiry:
                days = self.config.get('trust_duration_days', 365)
                expiry = int((chain.blocks.head.timestamp + timedelta(days=days)).timestamp())
            
            # Use the account object to send the transaction
            tx = self.contract.trust(
                trustee,
                expiry,
                sender=truster  # ape will use this account to sign
            )
            
            success = bool(tx and tx.status == 1)
            if success:
                if self.cache_enabled:
                    self._update_trust_cache(truster.address, trustee, expiry)
                if self.on_trust:
                    self.on_trust(truster.address, trustee, expiry)
                    
            return success
            
        except Exception as e:
            logger.error(f"Failed to establish trust {truster.address} -> {trustee}: {e}")
            return False

    def operate_flow_matrix(self, vertices: List[str], flow_edges: List[Dict],
                          streams: List[Dict], coordinates: bytes) -> bool:
        """
        Execute a flow matrix operation
        
        Args:
            vertices: List of vertex addresses
            flow_edges: List of flow edge configurations
            streams: List of stream configurations
            coordinates: Packed coordinate bytes
        """
        try:
            tx = self.contract.operateFlowMatrix(
                vertices,
                flow_edges,
                streams,
                coordinates,
                sender=vertices[0],  # First vertex is the operator
                gas_limit=self.gas_limits['operate_flow']
            )
            
            return bool(tx and tx.status == 1)
            
        except Exception as e:
            logger.error(f"Failed to operate flow matrix: {e}")
            return False

    # Token Operations

    def personal_mint(self, address: str) -> bool:
        """
        Perform personal token minting for a registered human address.
        
        The minting process requires several steps:
        1. Pre-mint eligibility validation
        2. Initial balance recording
        3. Transaction execution with proper block waiting
        4. Post-mint balance verification
        5. Event notification and cache updates
        
        Args:
            address: The address attempting to mint tokens
            
        Returns:
            bool: True if minting was successful, False otherwise
        """
        try:
            # Record initial state for verification
            initial_block = chain.blocks.head.number
            initial_balance = self.get_balance(address)
            current_block_time = chain.blocks.head.timestamp
            
            # Perform pre-mint eligibility checks
            can_mint, reason = self._check_mint_eligibility(address)
            if not can_mint:
                logger.error(f"Mint eligibility check failed for {address}: {reason}")
                return False
            
            # Calculate issuance parameters based on blockchain time
            issuance_data = self.contract.calculateIssuance(address)
            
            if issuance_data[0] == 0:  # No issuance available
                logger.debug(f"No issuance available for {address}")
                return False

            # Execute mint transaction with proper parameters
            try:
                tx = self.contract.personalMint(
                    sender=address,
                    gas_limit=self.gas_limits['mint']
                )
                
                # Wait for transaction confirmation
                chain.mine()
                
                if not tx or not hasattr(tx, 'status') or tx.status != 1:
                    logger.error(f"Mint transaction failed for {address}")
                    return False
                    
            except Exception as contract_e:
                error_message = str(contract_e)
                if "CirclesHubMustBeHuman" in error_message:
                    logger.error(f"Mint failed: {address} must be registered as human")
                elif "CirclesERC1155MintBlocked" in error_message:
                    logger.error(f"Mint failed: minting is blocked for {address}")
                else:
                    logger.error(f"Mint failed with contract error: {error_message}")
                return False
                
            # Verify balance increase
            chain.mine()
            new_balance = self.get_balance(address)
            minted_amount = new_balance - initial_balance
            
            if minted_amount <= 0:
                logger.error(
                    f"Mint anomaly: no balance increase for {address}\n"
                    f"Initial balance: {initial_balance}\n"
                    f"New balance: {new_balance}\n"
                    f"Block: {chain.blocks.head.number}"
                )
                return False
                
            # Update cache and trigger event
            if self.cache_enabled:
                self.cache['balances'][address] = new_balance
                
            if self.on_mint:
                self.on_mint(
                    address=address,
                    amount=minted_amount,
                    block=chain.blocks.head.number,
                    timestamp=chain.blocks.head.timestamp
                )
                
            logger.info(
                f"Successfully minted {minted_amount} tokens for {address}\n"
                f"Previous balance: {initial_balance}\n"
                f"New balance: {new_balance}\n"
                f"Block: {chain.blocks.head.number}\n"
                f"Block time: {chain.blocks.head.timestamp}"
            )
            
            return True
            
        except Exception as e:
            logger.error(
                f"Unexpected error in mint operation for {address}:\n"
                f"Error: {str(e)}\n"
                f"Initial block: {initial_block}\n"
                f"Current block: {chain.blocks.head.number}",
                exc_info=True
            )
            return False


    def _check_mint_eligibility(self, address: str) -> Tuple[bool, str]:
        """
        Check if an address is eligible for personal minting.
        Uses contract storage access and blockchain time.
        
        Args:
            address: Address to check eligibility for
        
        Returns:
            Tuple[bool, str]: (is_eligible, reason_if_not)
        """
        try:
            # Validate address format
            if not address or not address.startswith('0x'):
                return False, "Invalid address format"
                
            # Check human registration
            if not self.is_human(address):
                return False, "Address not registered as human"

            # Get mint status using contract call instead of direct storage access
            try:
                # Calculate issuance to check eligibility
                issuance, start_period, end_period = self.contract.calculateIssuance(address)
                
                # No issuance means either stopped or not enough time passed
                if issuance == 0:
                    # Check if stopped
                    if self.contract.stopped(address):
                        return False, "Minting is stopped for this address"
                    return False, "No issuance available at this time"

                # Calculate blockchain-based time checks
                current_block_time = chain.blocks.head.timestamp
                
                # Check if we're within valid period
                if current_block_time < start_period:
                    return False, "Not yet eligible to mint"
                if current_block_time > end_period:
                    return False, "Mint period has passed"

                # If we got here, minting is allowed
                return True, ""
                
            except Exception as e:
                logger.error(f"Failed to check mint status: {e}")
                return False, "Failed to check mint status"

        except Exception as e:
            logger.error(f"Error checking mint eligibility: {e}")
            return False, f"Error checking eligibility: {str(e)}"


    def group_mint(self, group: str, collateral_avatars: List[str],
                  amounts: List[int], data: bytes = b"") -> bool:
        """
        Mint group tokens using collateral
        
        Args:
            group: Group address
            collateral_avatars: List of collateral avatar addresses
            amounts: List of collateral amounts
            data: Optional additional data
        """
        try:
            tx = self.contract.groupMint(
                group,
                collateral_avatars,
                amounts,
                data,
                sender=msg.sender,
                gas_limit=self.gas_limits['mint']
            )
            
            return bool(tx and tx.status == 1)
            
        except Exception as e:
            logger.error(f"Failed group mint for {group}: {e}")
            return False

    def wrap_token(self, avatar: str, amount: int, token_type: int) -> Optional[str]:
        """
        Wrap tokens into ERC20
        
        Args:
            avatar: Avatar address
            amount: Amount to wrap
            token_type: Token type (0=Demurrage, 1=Inflation)
            
        Returns:
            Address of wrapped token contract if successful
        """
        try:
            tx = self.contract.wrap(
                avatar,
                amount,
                token_type,
                sender=msg.sender,
                gas_limit=self.gas_limits['wrap_token']
            )
            
            if tx and tx.status == 1:
                return tx.return_value
            return None
            
        except Exception as e:
            logger.error(f"Failed to wrap tokens for {avatar}: {e}")
            return None

    def burn(self, address: str, token_id: int, amount: int, 
            data: bytes = b"") -> bool:
        """
        Burn tokens
        
        Args:
            address: Token holder address
            token_id: Token ID to burn
            amount: Amount to burn
            data: Optional data
        """
        try:
            tx = self.contract.burn(
                token_id,
                amount, 
                data,
                sender=address,
                gas_limit=self.gas_limits['transfer']
            )
            
            return bool(tx and tx.status == 1)
            
        except Exception as e:
            logger.error(f"Failed to burn tokens for {address}: {e}")
            return False

    # Advanced Features

    def set_advanced_usage_flag(self, address: str, flag: bytes) -> bool:
        """
        Set advanced usage flags for an address
        
        Args:
            address: Address to set flags for
            flag: Flag value as bytes32
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

    def stop(self, address: str) -> bool:
        """
        Stop future minting for an address
        
        Args:
            address: Address to stop minting for
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

    # Query Functions

    def get_balance(self, address: str) -> int:
        """Get token balance for address"""
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
            logger.error(f"Failed to get balance for {address}: {e}")
            return self.cache['balances'].get(address, 0)

    def get_balance_on_day(self, address: str, token_id: int, 
                          day: int) -> Tuple[int, int]:
        """
        Get token balance for specific day
        
        Args:
            address: Account address
            token_id: Token ID
            day: Day number since inflation day zero
            
        Returns:
            Tuple of (balance, discount cost)
        """
        try:
            return self.contract.balanceOfOnDay(address, token_id, day)
        except Exception as e:
            logger.error(f"Failed to get balance on day {day} for {address}: {e}")
            return (0, 0)

    def calculate_issuance(self, address: str) -> Tuple[int, int, int]:
        """
        Calculate issuance for an address
        
        Args:
            address: Address to calculate issuance for
            
        Returns:
            Tuple of (issuance amount, start period, end period)
        """
        try:
            return self.contract.calculateIssuance(address)
        except Exception as e:
            logger.error(f"Failed to calculate issuance for {address}: {e}")
            return (0, 0, 0)

    def convert_value(self, value: int, from_type: str, to_type: str, day: int) -> int:
        """
        Convert between inflationary and demurrage values.
        Uses blockchain time for day calculations.
        
        Args:
            value: Value to convert
            from_type: Source type ('inflationary' or 'demurrage') 
            to_type: Target type
            day: Day number for conversion
        
        Returns:
            Converted value
        """
        try:
            # Calculate current day from blockchain time
            current_day = self.contract.day(chain.blocks.head.timestamp)
            
            # Validate day parameter is not in future
            if day > current_day:
                logger.warning(f"Conversion requested for future day {day}, using current day {current_day}")
                day = current_day

            if from_type == 'inflationary' and to_type == 'demurrage':
                return self.contract.convertInflationaryToDemurrageValue(value, day)
            elif from_type == 'demurrage' and to_type == 'inflationary':
                return self.contract.convertDemurrageToInflationaryValue(value, day)
            else:
                raise ValueError("Invalid conversion types")
                
        except Exception as e:
            logger.error(f"Failed to convert value {value}: {e}")
            return 0

    # Status Check Functions

    def is_human(self, address: str) -> bool:
        """Check if address is registered as human"""
        try:
            if self.cache_enabled and address in self.cache['humans']:
                return True
            return self.contract.isHuman(address)
        except Exception as e:
            logger.error(f"Failed to check human status for {address}: {e}")
            return False

    def is_group(self, address: str) -> bool:
        """Check if address is registered as group"""
        try:
            if self.cache_enabled and address in self.cache['groups']:
                return True
            return self.contract.isGroup(address)
        except Exception as e:
            logger.error(f"Failed to check group status for {address}: {e}")
            return False

    def is_organization(self, address: str) -> bool:
        """Check if address is registered as organization"""
        try:
            if self.cache_enabled and address in self.cache['organizations']:
                return True
            return self.contract.isOrganization(address)
        except Exception as e:
            logger.error(f"Failed to check organization status for {address}: {e}")
            return False

    def is_trusted(self, truster: str, trustee: str) -> bool:
        """Check if one address trusts another"""
        try:
            cached_trust = self.cache['trust_network'].get(truster, {}).get(trustee)
            if cached_trust is not None:
                return cached_trust >= int(chain.blocks.head.timestamp)
            return self.contract.isTrusted(truster, trustee)
        except Exception as e:
            logger.error(f"Failed to check trust status {truster} -> {trustee}: {e}")
            return False

    def is_permitted_flow(self, from_addr: str, to_addr: str, 
                         circles_avatar: str) -> bool:
        """
        Check if token flow is permitted between addresses
        
        Args:
            from_addr: Source address
            to_addr: Destination address
            circles_avatar: Address of Circles avatar
        """
        try:
            return self.contract.isPermittedFlow(from_addr, to_addr, circles_avatar)
        except Exception as e:
            logger.error(f"Failed to check flow permission: {e}")
            return False

    def is_stopped(self, address: str) -> bool:
        """Check if address is stopped from minting"""
        try:
            return self.contract.stopped(address)
        except Exception as e:
            logger.error(f"Failed to check stopped status for {address}: {e}")
            return False

    # Token Transfer Functions 

    def transfer(self, from_address: str, to_address: str, amount: int, 
                data: bytes = b"") -> bool:
        """Transfer tokens between accounts"""
        try:
            token_id = int(from_address, 16)  # Convert address to token ID
            
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
                    from_balance = self.get_balance(from_address)
                    to_balance = self.get_balance(to_address)
                    self._update_cache('balances', {
                        from_address: from_balance,
                        to_address: to_balance
                    })
                
                if self.on_transfer:
                    self.on_transfer(from_address, to_address, amount)
                    
            return success
            
        except Exception as e:
            logger.error(f"Failed transfer {from_address} -> {to_address}: {e}")
            return False

    def batch_transfer(self, from_address: str, to_address: str,
                      token_ids: List[int], amounts: List[int], 
                      data: bytes = b"") -> bool:
        """
        Perform batch token transfer
        
        Args:
            from_address: Source address
            to_address: Destination address
            token_ids: List of token IDs to transfer
            amounts: List of amounts to transfer
            data: Optional additional data
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

    # Cache Management Functions

    def _update_cache(self, cache_type: str, data: Dict):
        """Update specific cache with new data"""
        if not self.cache_enabled:
            return
            
        if cache_type == 'balances':
            self.cache['balances'].update(data)
        elif cache_type == 'humans':
            self.cache['humans'] = self.cache.get('humans', set()) | set(data.keys())
        elif cache_type == 'organizations':
            self.cache['organizations'] = self.cache.get('organizations', set()) | set(data.keys())
        elif cache_type == 'groups':
            self.cache['groups'] = self.cache.get('groups', set()) | set(data.keys())
            
        self.cache['last_update'] = chain.blocks.head.timestamp
        self.cache['current_block'] = chain.blocks.head.number

    def _update_trust_cache(self, truster: str, trustee: str, expiry: int):
        """Update trust network cache"""
        if not self.cache_enabled:
            return
            
        if truster not in self.cache['trust_network']:
            self.cache['trust_network'][truster] = {}
            
        self.cache['trust_network'][truster][trustee] = expiry

    def _invalidate_balance_cache(self, address: str):
        """Remove address from balance cache"""
        if self.cache_enabled:
            self.cache['balances'].pop(address, None)

    def _should_refresh_cache(self) -> bool:
        """Check if cache should be refreshed based on TTL"""
        if not self.cache_enabled:
            return False
            
        age = chain.blocks.head.timestamp - self.cache['last_update']
        return age.total_seconds() > self.cache_ttl

    # Network Analysis Helpers

    def get_trust_network(self) -> Dict[str, Set[str]]:
        """Get current trust network state"""
        return self.cache['trust_network']

    def get_groups(self) -> Set[str]:
        """Get set of group addresses"""
        return self.cache['groups']

    def get_humans(self) -> Set[str]:
        """Get set of registered human addresses"""
        return self.cache['humans']

    def get_organizations(self) -> Set[str]:
        """Get set of registered organization addresses"""
        return self.cache['organizations']

    def get_treasury(self, group: str) -> Optional[str]:
        """Get treasury address for group"""
        try:
            return self.contract.treasuries(group)
        except Exception as e:
            logger.error(f"Failed to get treasury for group {group}: {e}")
            return None

    def get_mint_policy(self, group: str) -> Optional[str]:
        """Get mint policy address for group"""
        try:
            return self.contract.mintPolicies(group)
        except Exception as e:
            logger.error(f"Failed to get mint policy for group {group}: {e}")
            return None

    def get_advanced_usage_flags(self, address: str) -> bytes:
        """Get advanced usage flags for address"""
        try:
            return self.contract.advancedUsageFlags(address)
        except Exception as e:
            logger.error(f"Failed to get advanced flags for {address}: {e}")
            return bytes(32)  # Return empty bytes32