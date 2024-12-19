from typing import Optional, Dict, List, Tuple
from ape import chain, Contract
from datetime import datetime, timedelta
import logging
import random
from eth_account import Account
from src.framework.agents.agent_manager import AgentManager
from src.framework.agents.base_agent import BaseAgent, ActionType
from src.framework.data.data_collector import CirclesDataCollector
from eth_pydantic_types import HexBytes
from src.protocols.common.uint256_handler import UINT256Handler

logger = logging.getLogger(__name__)

class NetworkEvolver:
    """
    Enhanced NetworkEvolver that simulates agent-driven network evolution,
    actually performing on-chain contract calls for each action.
    """
    
    def __init__(
        self, 
        contract_address: str, 
        abi_path: str, 
        agent_manager: AgentManager, 
        collector: Optional[CirclesDataCollector] = None,
        gas_limits: Optional[Dict[str, int]] = None
    ):
        """
        Initialize the NetworkEvolver with contract and agent management.
        
        Args:
            contract_address: Address of the Rings contract
            abi_path: Path to the contract ABI file
            agent_manager: AgentManager instance
            collector: Optional CirclesDataCollector
            gas_limits: Optional dictionary of gas limits for different operations
        """
        self.contract = Contract(contract_address, abi=abi_path)
        self.agent_manager = agent_manager
        self.collector = collector

        # Initialize default gas limits
        self.gas_limits = gas_limits or {
            'mint': 300000,
            'trust': 200000,
            'transfer': 200000,
            'create_group': 1000000
        }

        # Event callbacks
        self.on_mint_performed = None
        self.on_transfer_performed = None
        self.on_group_created = None
        
    def advance_time(self, blocks: int, block_time: int = 5) -> bool:
        """Advance the chain by mining new blocks."""
        try:
            # In fast mode, mine blocks in larger batches
            batch_size = 10
            for i in range(0, blocks, batch_size):
                current_batch = min(batch_size, blocks - i)
                chain.mine(current_batch)
                chain.pending_timestamp = chain.pending_timestamp + (current_batch * block_time)
            return True
        except Exception as e:
            logger.error(f"Failed to advance time: {e}", exc_info=True)
            return False

    def evolve_network(self, iteration: int) -> Dict[str, int]:
        """Evolve the network with minimal state tracking in fast mode."""
        stats = {
            'total_actions': 0
        }
        
        try:
            all_agents = list(self.agent_manager.agents.values())
            random.shuffle(all_agents)

            # Simplified state tracking
            chain_state = {
                'current_block': chain.blocks.head.number
            }

            for agent in all_agents:
                action_type, acting_address, params = agent.select_action(
                    current_block=chain_state['current_block'],
                    state=chain_state
                )
                
                if action_type is None:
                    continue
                    
                success = self._perform_agent_action(agent, action_type, params)
                if success:
                    stats[action_type.name.lower()] = stats.get(action_type.name.lower(), 0) + 1
                    stats['total_actions'] += 1

            logger.info(f"Iteration {iteration} stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to evolve network: {e}", exc_info=True)
            return stats        

    def _perform_agent_action(self, agent: BaseAgent, action: ActionType, params: Dict) -> bool:
        """Execute a specific on-chain action for an agent."""
        try:
            if action == ActionType.REGISTER_HUMAN:
                return self._handle_human_registration(agent)
            elif action == ActionType.MINT:
                return self._handle_mint_action(agent)
            elif action == ActionType.TRUST:
                return self._handle_trust_action(agent)
            elif action == ActionType.TRANSFER:
                return self._handle_transfer_action(agent)
            elif action == ActionType.CREATE_GROUP:
                return self._handle_group_creation(agent)
            else:
                logger.warning(f"Unknown action type: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to perform {action} for agent {agent.agent_id}: {e}", exc_info=True)
            return False

    def _handle_human_registration(self, agent: BaseAgent) -> bool:
        """
        Execute human registration for an agent.
        
        Args:
            agent: BaseAgent instance attempting registration
            
        Returns:
            bool: True if registration was successful
        """
        try:
            # If the agent doesn't have enough accounts yet, create a new one
            if len(agent.accounts) < agent.profile.target_account_count:
                new_address, _ = agent.create_account()
                logger.debug(f"Agent {agent.agent_id} created a new account {new_address}")
                if self.collector and self.collector.current_run_id:
                    self.collector.record_agent_address(agent.agent_id, new_address, is_primary=False)
            
            if not agent.accounts:
                logger.debug(f"Agent {agent.agent_id} has no accounts to register")
                return False

            # Select random unregistered account
            unregistered_accounts = [
                addr for addr in agent.accounts.keys()
                if not self.contract.isHuman(addr)
            ]
            
            if not unregistered_accounts:
                logger.debug(f"Agent {agent.agent_id} has no unregistered accounts")
                return False
            
            address = random.choice(unregistered_accounts)
            private_key = agent.accounts[address]
            account = Account.from_key(private_key)
            
            inviter = "0x0000000000000000000000000000000000000000"
            metadata = HexBytes(0)
            
            receipt = self.contract.registerHuman(
                inviter,
                metadata,
                sender=account.address,
                gas_limit=self.gas_limits.get('register_human', 500000)
            )

            
            success = bool(receipt and receipt.status == 1)
            if success and self.collector:
                self.collector.record_human_registration(
                    address=address,
                    block_number=chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp),
                    inviter_address=inviter,
                    welcome_bonus=200.0
                )

            if success:
                logger.info(f"Successfully registered human account {address}")
            else:
                logger.warning(f"Failed to register human account {address}")

            return success

        except Exception as e:
            logger.error(f"Human registration failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False

    def _handle_mint_action(self, agent: BaseAgent) -> bool:
        """Execute a mint action for an agent."""
        try:
            if not agent.accounts:
                logger.debug(f"Agent {agent.agent_id} has no accounts")
                return False
                
            # Get mint configuration from agent profile
            mint_config = agent.profile.action_configs.get(ActionType.MINT)
            if not mint_config:
                return False
            
            # Select random account
            address = random.choice(list(agent.accounts.keys()))
            
            # Check if address is registered as human
            if not self.contract.isHuman(address):
                logger.debug(f"Address {address} is not registered as human")
                return False
                
            # Record initial balance
            token_id = int(str(address), 16)
            prev_balance = self.contract.balanceOf(address, token_id)
            
            # Execute mint using configured parameters
            private_key = agent.accounts[address]
            account = Account.from_key(private_key)
            
            receipt = self.contract.personalMint(
                sender=account.address,
                gas_limit=mint_config.gas_limit
            )
            
            if not receipt or receipt.status != 1:
                logger.debug(f"Mint transaction failed for {address}")
                return False
                
            # Get minted amount from events
            minted_amount = 0
            for log in receipt.decode_logs():
                if log.event_name == "PersonalMint":
                    minted_amount = log.amount
                    break
                    
            if minted_amount == 0:
                return False
                
            # Record mint event if handler exists
            if self.on_mint_performed:
                self.on_mint_performed(
                    address=address,
                    amount=minted_amount,
                    block=chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp)
                )
                
            # Record balance change if collector exists
            if self.collector:
                self.collector.record_balance_change(
                    account=address,
                    token_id=address,
                    block_number=chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp),
                    previous_balance=prev_balance,
                    new_balance=prev_balance + minted_amount,
                    tx_hash=receipt.txn_hash,
                    event_type="MINT"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Mint action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False


    def _handle_trust_action(self, agent: BaseAgent) -> bool:
        try:
            if not agent.accounts:
                logger.debug("Trust action skipped: No accounts for agent")
                return False
            
            # Get all registered addresses
            all_registered_addresses = set()
            for addr in list(self.agent_manager.address_to_agent.keys()):
                # Use contract methods to validate registration
                try:
                    # Check if address is a registered human or organization
                    if self.contract.isHuman(addr) or self.contract.isOrganization(addr):
                        all_registered_addresses.add(addr)
                except Exception as validation_err:
                    logger.debug(f"Address validation error for {addr}: {validation_err}")
            
            # Filter out already trusted and unregistered addresses
            already_trusted = agent.trusted_addresses or set()
            potential_trustees = list(
                all_registered_addresses - 
                already_trusted - 
                set(agent.accounts.keys())  # Prevent trusting own addresses
            )
            
            if not potential_trustees:
                logger.debug("Trust action skipped: No potential trustees available")
                return False
            
            # Random selection with probability check
            if random.random() > 0.5:  # Adjusted probability
                return False
            
            # Select truster and trustee addresses
            truster_address = random.choice(list(agent.accounts.keys()))
            trustee_address = random.choice(potential_trustees)
            
            # Validate addresses
            if not self._validate_address_for_trust(truster_address, trustee_address):
                return False
            
            private_key = agent.accounts[truster_address]
            account = Account.from_key(private_key)
            
            # Calculate expiry using block time (current + 1 year in seconds)
            current_block_time = chain.blocks.head.timestamp
            expiry_timestamp = current_block_time + (365 * 24 * 60 * 60)
            
            receipt = self.contract.trust(
                trustee_address,
                expiry_timestamp,
                sender=account.address
            )
            
            if self.collector:
                self.collector.record_trust_relationship(
                    truster=truster_address,
                    trustee=trustee_address,
                    block_number=chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(current_block_time),
                    expiry_time=datetime.fromtimestamp(expiry_timestamp)
                )
            
            # Record trusted relationship
            agent.trusted_addresses = agent.trusted_addresses or set()
            agent.trusted_addresses.add(trustee_address)
            
            return True
            
        except Exception as e:
            logger.error(f"Trust action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False

    def _validate_address_for_trust(self, truster: str, trustee: str) -> bool:
        """
        Validate trust relationship before attempting to create it.
        
        Additional checks can be added here based on contract requirements.
        """
        try:
            # Check if addresses are not the same
            if truster.lower() == trustee.lower():
                logger.debug(f"Trust validation failed: Cannot trust self ({truster})")
                return False
            
            # Use contract methods to validate
            is_truster_valid = self.contract.isHuman(truster) or self.contract.isOrganization(truster)
            is_trustee_valid = self.contract.isHuman(trustee) or self.contract.isOrganization(trustee)
            
            if not (is_truster_valid and is_trustee_valid):
                logger.debug(
                    f"Trust validation failed: "
                    f"Invalid addresses. Truster valid: {is_truster_valid}, "
                    f"Trustee valid: {is_trustee_valid}"
                )
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Trust validation error: {e}")
            return False

    def _handle_transfer_action(self, agent: BaseAgent) -> bool:
        try:
            if not agent.accounts or not agent.trusted_addresses:
                return False
                
            source_address = random.choice(list(agent.accounts.keys()))
            recipient_address = random.choice(list(agent.trusted_addresses))
            
            token_id = int(str(source_address), 16)
            
            # Record balances before transfer
            source_balance = self.contract.balanceOf(source_address, token_id)
            recipient_prev_balance = self.contract.balanceOf(recipient_address, token_id)
            
            if source_balance == 0:
                return False
                
            transfer_amount = int(source_balance * random.uniform(0.1, 0.3))
            if transfer_amount == 0:
                return False
                
            account = Account.from_key(agent.accounts[source_address])
            
            receipt = self.contract.safeTransferFrom(
                source_address,
                recipient_address,
                token_id,
                transfer_amount,
                b"",
                sender=account.address
            )
            
            if self.on_transfer_performed:
                self.on_transfer_performed(
                    from_address=source_address,
                    to_address=recipient_address,
                    amount=transfer_amount,
                    block=chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp)
                )
            
            if self.collector:
                # Record sender's balance change
                self.collector.record_balance_change(
                    account=source_address,
                    token_id=str(token_id),
                    block_number=chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp),
                    previous_balance=source_balance,
                    new_balance=source_balance - transfer_amount,
                    tx_hash=receipt.txn_hash,
                    event_type="TRANSFER_SEND"
                )
                
                # Record recipient's balance change
                self.collector.record_balance_change(
                    account=recipient_address,
                    token_id=str(token_id),
                    block_number=chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp),
                    previous_balance=recipient_prev_balance,
                    new_balance=recipient_prev_balance + transfer_amount,
                    tx_hash=receipt.txn_hash,
                    event_type="TRANSFER_RECEIVE"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Transfer action failed for agent {agent.agent_id}: {e}", exc_info=True)
            return False

    def _handle_group_creation(self, agent: BaseAgent) -> bool:
        """Execute group creation for an agent."""
        try:
            if not agent.accounts:
                return False
                
            creator_address, _ = agent.create_account()
            logger.debug(f"Agent {agent.agent_id} created a new account {creator_address}")
            if self.collector and self.collector.current_run_id:
                self.collector.record_agent_address(agent.agent_id, creator_address, is_primary=False)
            
            private_key = agent.accounts[creator_address]
            creator_account = Account.from_key(private_key)
            
            # Generate valid alphanumeric name and symbol
            group_number = getattr(agent, 'group_count', 0) + 1
            group_name = f"RingsGroup{creator_address[:4]}{group_number}"
            group_symbol = f"RG{creator_address[:2]}{group_number}"

            # Get mint policy from configuration
            mint_policy = self.agent_manager.config.get('mint_policy_address', 
                "0x79Cbc9C7077dF161b92a745345A6Ade3fC626A60")  # Default as fallback

            try:
                receipt = self.contract.registerGroup(
                    mint_policy,
                    group_name,
                    group_symbol,
                    HexBytes(0),
                    sender=creator_account.address
                )
                
                # Update group count on successful creation
                agent.group_count = group_number

                # Record in data collector if available
                if self.collector:
                    self.collector.record_group_registration(
                        address=creator_address,
                        creator=agent.agent_id,
                        block_number=chain.blocks.head.number,
                        timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp),
                        name=group_name,
                        symbol=group_symbol,
                        mint_policy=mint_policy
                    )

                # Fire event callback if registered
                if self.on_group_created:
                    self.on_group_created(
                        creator=creator_account.address,
                        group_address=creator_address,
                        name=group_name,
                        block=chain.blocks.head.number,
                        timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp)
                    )

                logger.info(f"Successfully created group {group_name} for agent {agent.agent_id}")
                return True

            except Exception as e:
                error_msg = str(e)
                if '0x80' in error_msg or 'CirclesHubAvatarAlreadyRegistered' in error_msg:
                    logger.debug(f"Address {creator_address} is already registered")
                    return False
                if '0x02' in error_msg:
                    logger.debug(f"Invalid name or symbol format")
                    return False
                if '0x00' in error_msg:
                    logger.debug(f"Invalid mint policy address")
                    return False
                raise

        except Exception as e:
            logger.error(f"Group creation failed for agent {agent.agent_id}: {str(e)}")
            return False
        
    def _handle_group_creation2(self, agent: BaseAgent) -> bool:
        """Execute group creation for an agent."""
        try:
            if not agent.accounts:
                return False
            
            creator_address, _ = agent.create_account()
            logger.debug(f"Agent {agent.agent_id} created a new account {creator_address}")
            if self.collector and self.collector.current_run_id:
                self.collector.record_agent_address(agent.agent_id, creator_address, is_primary=False)
                
            private_key = agent.accounts[creator_address]
            creator_account = Account.from_key(private_key)
            
            # Generate unique group name and symbol
            group_number = getattr(agent, 'group_count', 0) + 1
            group_name = f"Group{group_number}"  
            group_symbol = f"G{group_number}"   

            StandardTreasury = '0x3545955Bc3900bda704261e4991f239BBd99ecE5'
            BaseGroupMintPolicy = '0x79Cbc9C7077dF161b92a745345A6Ade3fC626A60'
            try:
                # Match exact function signature:
                # registerGroup(address _mint, string _name, string _symbol, bytes32 _metadataDigest)
                receipt = self.contract.registerGroup(
                    BaseGroupMintPolicy,
                    group_name,
                    group_symbol,
                    HexBytes(0),  # 32 zero bytes
                    sender=creator_account.address
                )
                
                # Update group count on successful creation
                agent.group_count = group_number

                # Process receipt and emit events...
                if self.collector and False:
                    self.collector.record_group_registration(
                        address=creator_address,
                        creator=creator_account.address,
                        block_number=chain.blocks.head.number,
                        timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp),
                        name=group_name,
                        symbol=group_symbol
                    )

                if self.on_group_created:
                    self.on_group_created(
                        creator=creator_account.address,
                        group_address=creator_address,
                        name=group_name,
                        block=chain.blocks.head.number,
                        timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp)
                    )

                return True

            except Exception as e:
                if 'CirclesErrorOneAddressArg' in str(e):
                    logger.debug(f"Group registration failed - validation error for {creator_address}")
                    return False
                raise

        except Exception as e:
            logger.error(f"Group creation failed for agent {agent.agent_id}: {str(e)}")
            return False