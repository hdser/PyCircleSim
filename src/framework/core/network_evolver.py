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
        collector: Optional[CirclesDataCollector] = None
    ):
        """
        Initialize the NetworkEvolver with contract and agent management.
        
        Args:
            contract_address: Address of the Rings contract
            abi_path: Path to the contract ABI file
            agent_manager: AgentManager instance
            collector: Optional CirclesDataCollector
        """
        self.contract = Contract(contract_address, abi=abi_path)
        self.agent_manager = agent_manager
        self.collector = collector
        self.uint256_handler = UINT256Handler()

        # Event callbacks
        self.on_mint_performed = None
        self.on_transfer_performed = None
        self.on_group_created = None
        
    def advance_time(self, blocks: int, block_time: int = 5) -> bool:
        """Advance the chain by mining new blocks."""
        try:
            chain.mine(blocks)
            chain.pending_timestamp = chain.pending_timestamp + (blocks * block_time)
            return True
        except Exception as e:
            logger.error(f"Failed to advance time: {e}", exc_info=True)
            return False

    def evolve_network(self, iteration: int) -> Dict[str, int]:
        """
        Evolve the network by having agents perform actions based on their profiles.
        
        Args:
            iteration: Current iteration number
            
        Returns:
            Dict[str, int]: Stats about actions performed
        """
        stats = {
            'mints': 0,
            'trusts': 0,
            'transfers': 0,
            'groups_created': 0,
            'total_actions': 0
        }
        
        try:
            # Retrieve all agents
            all_agents = list(self.agent_manager.agents.values())
            random.shuffle(all_agents)  # Randomize order
            
            logger.info(f"Processing actions for {len(all_agents)} agents in iteration {iteration}")
            
            # Optional chain state
            chain_state = {
                'current_block': chain.blocks.head.number,
                'balances': {},
            }
            # Populate balances if needed
            # for agent in all_agents:
            #     for addr in agent.accounts:
            #         token_id = int(str(addr), 16)
            #         bal = self.contract.balanceOf(addr, token_id)
            #         chain_state['balances'][addr] = bal

            for agent in all_agents:
                action_type, acting_address, params = agent.select_action(
                    current_block=chain_state['current_block'], 
                    state=chain_state
                )
                
                if action_type is None:
                    # Agent chooses not to act
                    continue
                
                success = self._perform_agent_action(agent, action_type, params)
                if success:
                    if action_type == ActionType.MINT:
                        stats['mints'] += 1
                    elif action_type == ActionType.TRUST:
                        stats['trusts'] += 1
                    elif action_type == ActionType.TRANSFER:
                        stats['transfers'] += 1
                    elif action_type == ActionType.CREATE_GROUP:
                        stats['groups_created'] += 1
                    stats['total_actions'] += 1
                
                # Record the action outcome in the agent's log
                agent.record_action(action_type, chain_state['current_block'], success)
            
            logger.info(f"Iteration {iteration} stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to evolve network: {e}", exc_info=True)
            return stats


    def _perform_agent_action(self, agent: BaseAgent, action: ActionType, params: Dict) -> bool:
        """Execute a specific on-chain action for an agent."""
        try:
            if action == ActionType.MINT:
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


    def _handle_mint_action(self, agent: BaseAgent) -> bool:
        try:
            if not agent.accounts:
                return False
            
            address = random.choice(list(agent.accounts.keys()))
            private_key = agent.accounts[address]
            account = Account.from_key(private_key)
            
            prev_balance = self.contract.balanceOf(address, int(str(address), 16))
            receipt = self.contract.personalMint(sender=account.address)
            
            minted_amount = 0
            for log in receipt.decode_logs():
                if log.event_name == "PersonalMint":
                    minted_amount = log.amount
                    if self.on_mint_performed:
                        self.on_mint_performed(
                            address=address,
                            amount=minted_amount,
                            block=chain.blocks.head.number,
                            timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp)
                        )
                    # We collect mint event data
                    if self.collector:
                        new_balance = prev_balance + minted_amount  # Calculate new balance
                        self.collector.record_balance_change(
                            account=address,
                            token_id=address,
                            block_number=chain.blocks.head.number,
                            timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp),
                            previous_balance=prev_balance,
                            new_balance=new_balance, 
                            tx_hash=receipt.txn_hash,
                            event_type="MINT"
                        )
            return minted_amount > 0
            
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
            
            # Convert trust limit to proper wei string representation
            trust_limit = self.uint256_handler.to_wei(1_000_000)  # 1M tokens as default limit
            expiry_timestamp = int(
                datetime.now().timestamp() + 
                timedelta(days=365).total_seconds()
            )
            
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
                    timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp),
                    trust_limit=trust_limit,  # Now using string representation
                    expiry_time=datetime.fromtimestamp(expiry_timestamp)
                )
            
            # Record trusted relationship
            agent.trusted_addresses = agent.trusted_addresses or set()
            agent.trusted_addresses.add(trustee_address)
            
            # We should add balance tracking here too
            if self.collector:
                # Record both the trust relationship and any balance changes
                self.collector.record_trust_relationship(
                    truster=truster_address,
                    trustee=trustee_address,
                    block_number=chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp),
                    trust_limit=float(expiry_timestamp),
                    expiry_time=datetime.fromtimestamp(expiry_timestamp)
                )
            
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
                
            address = random.choice(list(agent.accounts.keys()))
            private_key = agent.accounts[address]
            account = Account.from_key(private_key)
            
            # Generate unique group name and symbol
            group_number = getattr(agent, 'group_count', 0) + 1
            name = f"Group_{address[:6]}_{group_number}"
            symbol = f"GRP{address[:4]}{group_number}"
            
            try:
                receipt = self.contract.registerGroup(
                    address,  # mint policy address
                    name,
                    symbol,
                    b"",     # no metadata for now
                    sender=account.address
                )
                
                # Update group count on successful creation
                agent.group_count = group_number
                
                if self.collector:
                    self.collector.record_group_registration(
                        address=address,
                        creator=account.address,
                        block_number=chain.blocks.head.number,
                        timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp),
                        name=name,
                        symbol=symbol
                    )
                return True
                
            except Exception as e:
                # Handle specific contract errors gracefully
                if 'CirclesErrorOneAddressArg' in str(e):
                    logger.debug(f"Group registration failed - contract validation error for {address}")
                    return False
                raise  # Re-raise other contract errors
                
        except Exception as e:
            logger.error(f"Group creation failed for agent {agent.agent_id}: {e}")
            return False
