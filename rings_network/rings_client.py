from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from ape import Contract, accounts, chain
import logging
import yaml
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

class RingsClient:
    """
    Client for interacting with the Rings smart contract.
    Provides high-level interface for all contract operations.
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
            'create_group': 1000000
        }
        
        # Initialize cache with provided config or defaults
        self.cache_enabled = cache_config.get('enabled', True) if cache_config else True
        self.cache_ttl = cache_config.get('ttl', 100) if cache_config else 100
        
        # Initialize cache storage
        self.cache = {
            'trust_network': {},
            'groups': set(),
            'balances': {},
            'last_update': datetime.min,
            'current_block': 0
        }
        
        # Event handlers
        self.on_transfer = None
        self.on_trust = None
        self.on_mint = None
        self.on_group_created = None

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

    def register_human(self, address: str, 
                      inviter: Optional[str] = None,
                      metadata_digest: Optional[bytes] = None) -> bool:
        """Register a new human account"""
        try:
            inviter = inviter or "0x0000000000000000000000000000000000000000"
            metadata = metadata_digest or HexBytes(0)
            
            # Get gas limit from config or use default
            gas_limit = self.config.get('gas_limits', {}).get('register_human', 500000)
            
            tx = self.contract.registerHuman(
                inviter,
                metadata,
                sender=address,
                gas_limit=gas_limit
            )
            
            success = bool(tx and tx.status == 1)
            if success:
                if self.config.get('cache_enabled', True):
                    self._update_cache('humans', {address: True})
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to register human {address}: {e}")
            return False

    def trust(self, truster: str, trustee: str, 
             expiry: Optional[datetime] = None) -> bool:
        """Establish trust relationship between accounts"""
        try:
            if not expiry:
                # Get trust duration from config or use default
                days = self.config.get('trust_duration_days', 365)
                expiry = datetime.now() + timedelta(days=days)
                
            expiry_timestamp = int(expiry.timestamp())
            gas_limit = self.config.get('gas_limits', {}).get('trust', 300000)
            
            tx = self.contract.trust(
                trustee,
                expiry_timestamp,
                sender=truster,
                gas_limit=gas_limit
            )
            
            success = bool(tx and tx.status == 1)
            if success:
                if self.config.get('cache_enabled', True):
                    self._update_trust_cache(truster, trustee, expiry_timestamp)
                if self.on_trust:
                    self.on_trust(truster, trustee, expiry_timestamp)
                    
            return success
            
        except Exception as e:
            logger.error(f"Failed to establish trust {truster} -> {trustee}: {e}")
            return False

    def personal_mint(self, address: str) -> bool:
        """Perform personal token minting"""
        try:
            prev_balance = self.get_balance(address)
            gas_limit = self.config.get('gas_limits', {}).get('mint', 300000)
            
            tx = self.contract.personalMint(
                sender=address,
                gas_limit=gas_limit
            )
            
            success = bool(tx and tx.status == 1)
            if success:
                new_balance = self.get_balance(address)
                minted_amount = new_balance - prev_balance
                
                if self.config.get('cache_enabled', True):
                    self._update_cache('balances', {address: new_balance})
                
                if self.on_mint:
                    self.on_mint(address, minted_amount)
                    
            return success
            
        except Exception as e:
            logger.error(f"Failed personal mint for {address}: {e}")
            return False

    def transfer(self, from_address: str, to_address: str, 
                amount: int, data: bytes = b"") -> bool:
        """Transfer tokens between accounts"""
        try:
            token_id = int(from_address, 16)  # Convert address to token ID
            gas_limit = self.config.get('gas_limits', {}).get('transfer', 300000)
            
            tx = self.contract.safeTransferFrom(
                from_address,
                to_address,
                token_id,
                amount,
                data,
                sender=from_address,
                gas_limit=gas_limit
            )
            
            success = bool(tx and tx.status == 1)
            if success:
                if self.config.get('cache_enabled', True):
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

    def get_balance(self, address: str) -> int:
        """Get token balance for address"""
        try:
            if self.config.get('cache_enabled', True):
                cached_balance = self.cache['balances'].get(address)
                if cached_balance is not None:
                    return cached_balance
                    
            token_id = int(address, 16)
            balance = self.contract.balanceOf(address, token_id)
            
            if self.config.get('cache_enabled', True):
                self.cache['balances'][address] = balance
                
            return balance
            
        except Exception as e:
            logger.error(f"Failed to get balance for {address}: {e}")
            return self.cache['balances'].get(address, 0)

    def _update_cache(self, cache_type: str, data: Dict):
        """Update specific cache with new data"""
        if not self.config.get('cache_enabled', True):
            return
            
        if cache_type == 'balances':
            self.cache['balances'].update(data)
        elif cache_type == 'humans':
            self.cache['humans'] = self.cache.get('humans', set()) | set(data.keys())
            
        self.cache['last_update'] = datetime.now()
        self.cache['current_block'] = chain.blocks.head.number

    def _update_trust_cache(self, truster: str, trustee: str, expiry: int):
        """Update trust network cache"""
        if not self.config.get('cache_enabled', True):
            return
            
        if truster not in self.cache['trust_network']:
            self.cache['trust_network'][truster] = {}
            
        self.cache['trust_network'][truster][trustee] = expiry

    # Helper methods for simulation
    def get_trust_network(self) -> Dict[str, Set[str]]:
        """Get current trust network state"""
        return self.cache['trust_network']

    def get_groups(self) -> Set[str]:
        """Get set of group addresses"""
        return self.cache['groups']

    def is_human(self, address: str) -> bool:
        """Check if address is registered as human"""
        try:
            return self.contract.isHuman(address)
        except Exception as e:
            logger.error(f"Failed to check human status for {address}: {e}")
            return False