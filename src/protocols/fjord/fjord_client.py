from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from eth_typing import HexStr
from eth_pydantic_types import HexBytes
from ape import Contract, accounts, chain
import logging
import yaml
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PoolConfig:
    """Configuration for creating a Liquidity Bootstrapping Pool"""
    name: str
    symbol: str
    tokens: List[str]
    amounts: List[int]
    weights: List[int]
    end_weights: List[int]
    swap_fee_percentage: int
    start_time: int
    end_time: int

@dataclass
class WeightedPoolConfig:
    """Configuration for creating a Weighted Pool"""
    name: str
    symbol: str
    tokens: List[str]
    amounts: List[int]
    weights: List[int] 
    swap_fee_percentage: int

@dataclass
class PoolData:
    """Data structure for pool information"""
    owner: str
    fund_token_input_amount: int
    lbp_type: int
    weighted_pool_address: str

class FjordClient:
    """
    Client for interacting with the Fjord Liquidity Bootstrapping Pool contract.
    Provides high-level interface for pool management, token operations and configuration.
    """
    
    def __init__(
        self,
        contract_address: str,
        abi_path: str,
        gas_limits: Optional[Dict] = None,
        cache_config: Optional[Dict] = None
    ):
        """
        Initialize the Fjord client
        
        Args:
            contract_address: Address of deployed Fjord contract
            abi_path: Path to contract ABI file
            gas_limits: Optional gas limits for different operations
            cache_config: Optional cache configuration
        """
        self.contract = Contract(contract_address, abi=abi_path)
        
        # Set default gas limits if none provided
        self.gas_limits = gas_limits or {
            'create_pool': 5000000,
            'exit_pool': 2000000,
            'manage_pool': 1000000,
            'update_weights': 500000,
            'transfer': 300000
        }
        
        # Initialize cache with provided config or defaults
        self.cache_enabled = cache_config.get('enabled', True) if cache_config else True
        self.cache_ttl = cache_config.get('ttl', 100) if cache_config else 100
        
        # Initialize cache storage
        self.cache = {
            'pools': set(),
            'weighted_pools': set(),
            'pool_data': {},
            'last_update': datetime.min,
            'current_block': 0
        }
        
        # Event handlers
        self.on_pool_created = None
        self.on_weighted_pool_created = None
        self.on_pool_joined = None
        self.on_pool_exited = None
        self.on_weights_updated = None
        self.on_swap_enabled = None

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            return {}

    # Pool Creation Functions

    def create_lbp(self, config: PoolConfig) -> Optional[str]:
        """
        Create a new Liquidity Bootstrapping Pool
        
        Args:
            config: Pool configuration parameters
            
        Returns:
            Address of created pool if successful
        """
        try:
            tx = self.contract.createLBP(
                (
                    config.name,
                    config.symbol,
                    config.tokens,
                    config.amounts,
                    config.weights,
                    config.end_weights,
                    config.swap_fee_percentage,
                    config.start_time,
                    config.end_time
                ),
                gas_limit=self.gas_limits['create_pool']
            )
            
            if tx and tx.status == 1:
                pool_address = tx.return_value
                if self.cache_enabled:
                    self.cache['pools'].add(pool_address)
                if self.on_pool_created:
                    self.on_pool_created(pool_address)
                return pool_address
                
            return None
            
        except Exception as e:
            logger.error(f"Failed to create LBP: {e}")
            return None

    def create_weighted_pool(self, lbp_pool: str, config: WeightedPoolConfig) -> Optional[str]:
        """
        Create a Weighted Pool for an LBP
        
        Args:
            lbp_pool: Address of the LBP pool
            config: Weighted pool configuration
            
        Returns:
            Address of created weighted pool if successful
        """
        try:
            tx = self.contract.createWeightedPoolForLBP(
                lbp_pool,
                (
                    config.name,
                    config.symbol,
                    config.tokens,
                    config.amounts,
                    config.weights,
                    config.swap_fee_percentage
                ),
                gas_limit=self.gas_limits['create_pool']
            )
            
            if tx and tx.status == 1:
                pool_address = tx.return_value
                if self.cache_enabled:
                    self.cache['weighted_pools'].add(pool_address)
                if self.on_weighted_pool_created:
                    self.on_weighted_pool_created(pool_address)
                return pool_address
                
            return None
            
        except Exception as e:
            logger.error(f"Failed to create weighted pool: {e}")
            return None

    # Pool Operation Functions

    def exit_pool(self, pool: str, max_bpt_token_out: int, is_standard_fee: bool) -> bool:
        """
        Exit a liquidity pool
        
        Args:
            pool: Pool address
            max_bpt_token_out: Maximum BPT tokens to receive
            is_standard_fee: Whether to use standard fee
        """
        try:
            tx = self.contract.exitPool(
                pool,
                max_bpt_token_out,
                is_standard_fee,
                gas_limit=self.gas_limits['exit_pool']
            )
            
            success = bool(tx and tx.status == 1)
            if success and self.on_pool_exited:
                self.on_pool_exited(pool, max_bpt_token_out)
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to exit pool {pool}: {e}")
            return False

    def set_swap_enabled(self, pool: str, enabled: bool) -> bool:
        """
        Enable or disable swapping for a pool
        
        Args:
            pool: Pool address
            enabled: Whether to enable swaps
        """
        try:
            tx = self.contract.setSwapEnabled(
                pool,
                enabled,
                gas_limit=self.gas_limits['manage_pool']
            )
            
            success = bool(tx and tx.status == 1)
            if success and self.on_swap_enabled:
                self.on_swap_enabled(pool, enabled)
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to set swap enabled for pool {pool}: {e}")
            return False

    def transfer_pool_ownership(self, pool: str, new_owner: str) -> bool:
        """
        Transfer ownership of a pool
        
        Args:
            pool: Pool address
            new_owner: Address of new owner
        """
        try:
            tx = self.contract.transferPoolOwnership(
                pool,
                new_owner,
                gas_limit=self.gas_limits['manage_pool']
            )
            
            return bool(tx and tx.status == 1)
            
        except Exception as e:
            logger.error(f"Failed to transfer pool ownership: {e}")
            return False

    # Fund Token Management

    def add_fund_token_options(self, tokens: List[str]) -> bool:
        """
        Add tokens to allowed fund token list
        
        Args:
            tokens: List of token addresses
        """
        try:
            tx = self.contract.addFundTokenOptions(
                tokens,
                gas_limit=self.gas_limits['manage_pool']
            )
            
            return bool(tx and tx.status == 1)
            
        except Exception as e:
            logger.error(f"Failed to add fund token options: {e}")
            return False

    def update_recipients(self, recipients: List[str], shares: List[int]) -> bool:
        """
        Update fee recipient addresses and shares
        
        Args:
            recipients: List of recipient addresses
            shares: List of basis point shares
        """
        try:
            tx = self.contract.updateRecipients(
                recipients,
                shares,
                gas_limit=self.gas_limits['manage_pool']
            )
            
            return bool(tx and tx.status == 1)
            
        except Exception as e:
            logger.error(f"Failed to update recipients: {e}")
            return False

    def skim(self, token: str, recipient: str) -> bool:
        """
        Skim tokens from the contract
        
        Args:
            token: Token address to skim
            recipient: Address to receive tokens
        """
        try:
            tx = self.contract.skim(
                token,
                recipient,
                gas_limit=self.gas_limits['transfer']
            )
            
            return bool(tx and tx.status == 1)
            
        except Exception as e:
            logger.error(f"Failed to skim tokens: {e}")
            return False

    # Query Functions

    def get_pool_data(self, pool: str) -> Optional[PoolData]:
        """Get pool information"""
        try:
            if self.cache_enabled:
                cached_data = self.cache['pool_data'].get(pool)
                if cached_data:
                    return cached_data
                    
            data = self.contract.getPoolData(pool)
            pool_data = PoolData(
                owner=data[0],
                fund_token_input_amount=data[1],
                lbp_type=data[2],
                weighted_pool_address=data[3]
            )
            
            if self.cache_enabled:
                self.cache['pool_data'][pool] = pool_data
                
            return pool_data
            
        except Exception as e:
            logger.error(f"Failed to get pool data for {pool}: {e}")
            return None

    def get_bpt_token_balance(self, pool: str) -> int:
        """Get BPT token balance for pool"""
        try:
            return self.contract.getBPTTokenBalance(pool)
        except Exception as e:
            logger.error(f"Failed to get BPT balance for {pool}: {e}")
            return 0

    def get_weighted_token_balance(self, pool: str) -> int:
        """Get weighted token balance for pool"""
        try:
            return self.contract.getWeightedTokenBalance(pool)
        except Exception as e:
            logger.error(f"Failed to get weighted balance for {pool}: {e}")
            return 0

    def get_recipient_share(self, recipient: str) -> int:
        """Get basis point share for recipient"""
        try:
            return self.contract.getRecipientShareBPS(recipient)
        except Exception as e:
            logger.error(f"Failed to get recipient share for {recipient}: {e}")
            return 0

    # Pool Lists and Validation

    def get_pools(self) -> List[str]:
        """Get list of all LBP pools"""
        try:
            if self.cache_enabled and self.cache['pools']:
                return list(self.cache['pools'])
            return self.contract.getPools()
        except Exception as e:
            logger.error(f"Failed to get pools: {e}")
            return []

    def get_weighted_pools(self) -> List[str]:
        """Get list of all weighted pools"""
        try:
            if self.cache_enabled and self.cache['weighted_pools']:
                return list(self.cache['weighted_pools'])
            return self.contract.getWeightedPools()
        except Exception as e:
            logger.error(f"Failed to get weighted pools: {e}")
            return []

    def is_pool(self, pool: str) -> bool:
        """Check if address is an LBP pool"""
        try:
            if self.cache_enabled and pool in self.cache['pools']:
                return True
            return self.contract.isPool(pool)
        except Exception as e:
            logger.error(f"Failed to check pool status for {pool}: {e}")
            return False

    def is_weighted_pool(self, pool: str) -> bool:
        """Check if address is a weighted pool"""
        try:
            if self.cache_enabled and pool in self.cache['weighted_pools']:
                return True
            return self.contract.isWeightedPool(pool)
        except Exception as e:
            logger.error(f"Failed to check weighted pool status for {pool}: {e}")
            return False

    def is_allowed_fund(self, token: str) -> bool:
        """Check if token is allowed as fund token"""
        try:
            return self.contract.isAllowedFund(token)
        except Exception as e:
            logger.error(f"Failed to check allowed fund status for {token}: {e}")
            return False

    # Contract Information

    def get_factory_addresses(self) -> Tuple[str, str, str]:
        """Get factory contract addresses"""
        try:
            lbp = self.contract.LBPFactoryAddress()
            weighted = self.contract.WeightedPoolFactoryAddress()
            vault = self.contract.VaultAddress()
            return lbp, weighted, vault
        except Exception as e:
            logger.error(f"Failed to get factory addresses: {e}")
            return ("0x0", "0x0", "0x0")

    def get_fee_recipients(self) -> List[str]:
        """Get list of fee recipient addresses"""
        try:
            return self.contract.getFeeRecipients()
        except Exception as e:
            logger.error(f"Failed to get fee recipients: {e}")
            return []

    def get_platform_fee(self) -> int:
        """Get platform access fee in basis points"""
        try:
            return self.contract.platformAccessFeeBPS()
        except Exception as e:
            logger.error(f"Failed to get platform fee: {e}")
            return 0

    # Cache Management

    def _update_cache(self, cache_type: str, data: Dict):
        """Update specific cache with new data"""
        if not self.cache_enabled:
            return
            
        if cache_type == 'pools':
            self.cache['pools'] = self.cache.get('pools', set()) | set(data.keys())
        elif cache_type == 'weighted_pools':
            self.cache['weighted_pools'] = self.cache.get('weighted_pools', set()) | set(data.keys())
        elif cache_type == 'pool_data':
            self.cache['pool_data'].update(data)
            
        self.cache['last_update'] = chain.blocks.head.timestamp
        self.cache['current_block'] = chain.blocks.head.number

    def _invalidate_pool_cache(self, pool: str):
        """
        Remove pool from cache
        
        Args:
            pool: Pool address to remove from cache
        """
        if self.cache_enabled:
            self.cache['pools'].discard(pool)
            self.cache['weighted_pools'].discard(pool)
            self.cache['pool_data'].pop(pool, None)

    def _should_refresh_cache(self) -> bool:
        """
        Check if cache should be refreshed based on TTL
        
        Returns:
            bool: True if cache needs refresh
        """
        if not self.cache_enabled:
            return False
            
        age = chain.blocks.head.timestamp - self.cache['last_update']
        return age.total_seconds() > self.cache_ttl

    def refresh_cache(self):
        """
        Force refresh of all cached data
        This is useful when cache may be stale or after major state changes
        """
        try:
            if not self.cache_enabled:
                return
                
            # Refresh pool lists
            self.cache['pools'] = set(self.contract.getPools())
            self.cache['weighted_pools'] = set(self.contract.getWeightedPools())
            
            # Refresh pool data
            self.cache['pool_data'] = {}
            for pool in self.cache['pools']:
                data = self.contract.getPoolData(pool)
                self.cache['pool_data'][pool] = PoolData(
                    owner=data[0],
                    fund_token_input_amount=data[1],
                    lbp_type=data[2],
                    weighted_pool_address=data[3]
                )
                
            self.cache['last_update'] = chain.blocks.head.timestamp
            self.cache['current_block'] = chain.blocks.head.number
            
        except Exception as e:
            logger.error(f"Failed to refresh cache: {e}")

    # Helper Functions

    def validate_pool_config(self, config: PoolConfig) -> bool:
        """
        Validate pool configuration parameters
        
        Args:
            config: Pool configuration to validate
            
        Returns:
            bool: True if configuration is valid
        """
        try:
            # Check array lengths match
            if not (len(config.tokens) == len(config.amounts) == len(config.weights) == len(config.end_weights)):
                return False
                
            # Check arrays not empty
            if len(config.tokens) == 0:
                return False
                
            # Check tokens are allowed as fund tokens
            for token in config.tokens:
                if not self.is_allowed_fund(token):
                    return False
                    
            # Validate timing parameters
            if config.start_time >= config.end_time:
                return False
                
            # Validate fee is within bounds (assuming max 10%)
            if config.swap_fee_percentage > 1000:  # 10% = 1000 basis points
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate pool config: {e}")
            return False

    def estimate_pool_creation_gas(self, config: PoolConfig) -> int:
        """
        Estimate gas required for pool creation
        
        Args:
            config: Pool configuration
            
        Returns:
            int: Estimated gas amount
        """
        try:
            # Base gas cost
            gas = 500000
            
            # Add gas for each token
            gas += len(config.tokens) * 100000
            
            # Add gas for weight updates
            if any(w1 != w2 for w1, w2 in zip(config.weights, config.end_weights)):
                gas += 200000
                
            return gas
            
        except Exception as e:
            logger.error(f"Failed to estimate gas: {e}")
            return self.gas_limits['create_pool']

    def format_pool_event(self, event_data: Dict) -> Dict:
        """
        Format pool event data into standardized structure
        
        Args:
            event_data: Raw event data
            
        Returns:
            Dict: Formatted event data
        """
        try:
            return {
                'pool': event_data['pool'],
                'poolId': event_data.get('poolId', '0x0'),
                'name': event_data.get('name', ''),
                'symbol': event_data.get('symbol', ''),
                'tokens': event_data.get('tokens', []),
                'weights': event_data.get('weights', []),
                'swapFeePercentage': event_data.get('swapFeePercentage', 0),
                'owner': event_data.get('owner', '0x0'),
                'timestamp': chain.blocks.head.timestamp.isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to format pool event: {e}")
            return {}

    async def wait_for_pool_deployment(self, tx_hash: str, timeout: int = 300) -> Optional[str]:
        """
        Wait for pool deployment transaction to complete
        
        Args:
            tx_hash: Transaction hash
            timeout: Maximum wait time in seconds
            
        Returns:
            str: Deployed pool address if successful
        """
        try:
            start_time = chain.blocks.head.timestamp
            while (chain.blocks.head.timestamp - start_time).seconds < timeout:
                receipt = await chain.get_transaction_receipt(tx_hash)
                if receipt:
                    if receipt.status == 1:
                        # Look for PoolCreated event
                        for log in receipt.decode_logs():
                            if log.name in ('PoolCreated', 'WeightedPoolCreated'):
                                return log.pool
                    break
                await chain.mine(1)
            return None
            
        except Exception as e:
            logger.error(f"Failed to wait for pool deployment: {e}")
            return None

    def get_pool_tokens_and_balances(self, pool: str) -> List[Tuple[str, int]]:
        """
        Get list of tokens and their balances in a pool
        
        Args:
            pool: Pool address
            
        Returns:
            List of (token_address, balance) tuples
        """
        try:
            pool_data = self.get_pool_data(pool)
            if not pool_data:
                return []
                
            balances = []
            vault_address = self.contract.VaultAddress()
            vault = Contract(vault_address)
            
            for token in pool_data.tokens:
                balance = vault.getPoolTokenBalance(pool, token)
                balances.append((token, balance))
                
            return balances
            
        except Exception as e:
            logger.error(f"Failed to get pool tokens and balances: {e}")
            return []

    def calculate_spot_price(self, pool: str, token_in: str, token_out: str) -> Optional[float]:
        """
        Calculate current spot price between tokens in pool
        
        Args:
            pool: Pool address
            token_in: Input token address
            token_out: Output token address
            
        Returns:
            float: Spot price if calculation successful
        """
        try:
            vault_address = self.contract.VaultAddress()
            vault = Contract(vault_address)
            
            # Get pool information
            pool_data = self.get_pool_data(pool)
            if not pool_data:
                return None
                
            # Get balances and weights
            token_in_balance = vault.getPoolTokenBalance(pool, token_in)
            token_out_balance = vault.getPoolTokenBalance(pool, token_out)
            
            token_in_weight = None
            token_out_weight = None
            for i, token in enumerate(pool_data.tokens):
                if token == token_in:
                    token_in_weight = pool_data.weights[i]
                elif token == token_out:
                    token_out_weight = pool_data.weights[i]
                    
            if not (token_in_weight and token_out_weight):
                return None
                
            # Calculate spot price using weighted formula
            return (token_in_balance / token_in_weight) / (token_out_balance / token_out_weight)
            
        except Exception as e:
            logger.error(f"Failed to calculate spot price: {e}")
            return None

    def encode_pool_init_data(self, config: PoolConfig) -> bytes:
        """
        Encode pool initialization data
        
        Args:
            config: Pool configuration
            
        Returns:
            bytes: Encoded initialization data
        """
        try:
            return self.contract.interface.encodeFunctionData(
                'initialize',
                [
                    config.name,
                    config.symbol,
                    config.tokens,
                    config.amounts,
                    config.weights
                ]
            )
        except Exception as e:
            logger.error(f"Failed to encode pool init data: {e}")
            return bytes()

    def get_pool_statistics(self, pool: str) -> Dict:
        """
        Get comprehensive statistics for a pool
        
        Args:
            pool: Pool address
            
        Returns:
            Dict containing pool statistics
        """
        try:
            pool_data = self.get_pool_data(pool)
            if not pool_data:
                return {}
                
            tokens_and_balances = self.get_pool_tokens_and_balances(pool)
            
            return {
                'address': pool,
                'owner': pool_data.owner,
                'type': 'LBP' if pool in self.cache['pools'] else 'Weighted',
                'tokens': [t[0] for t in tokens_and_balances],
                'balances': [t[1] for t in tokens_and_balances],
                'weighted_pool_address': pool_data.weighted_pool_address,
                'bpt_supply': self.get_bpt_token_balance(pool),
                'weighted_balance': self.get_weighted_token_balance(pool),
                'swap_enabled': True,  # Would need separate call to check
                'created_at': None  # Would need to get from events
            }
            
        except Exception as e:
            logger.error(f"Failed to get pool statistics: {e}")
            return {}