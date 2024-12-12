from typing import Optional, Dict, List, Tuple
from ape import chain, Contract
from eth_pydantic_types import HexBytes
from datetime import datetime, timedelta
import logging
import random
from eth_account import Account
from .agent import Agent, AgentManager, AgentPersonality

logger = logging.getLogger(__name__)

class NetworkEvolver:
    """
    Enhanced NetworkEvolver that simulates agent-driven network evolution
    """
    
    def __init__(self, contract_address: str, abi_path: str, agent_manager: AgentManager, collector=None):
        """
        Initialize the NetworkEvolver with contract and agent management.
        
        Args:
            contract_address: Address of the Rings contract
            abi_path: Path to the contract ABI file
            agent_manager: AgentManager instance managing all agents
            collector: Optional CirclesDataCollector to record network changes
        """
        self.contract = Contract(contract_address, abi=abi_path)
        self.agent_manager = agent_manager
        self.collector = collector

        self.on_mint_performed = None
        self.on_transfer_performed = None
        self.on_group_created = None
        
    def advance_time(self, blocks: int, block_time: int = 12) -> bool:
        """Advance the chain by mining new blocks."""
        try:
            chain.mine(blocks)
            chain.pending_timestamp = chain.pending_timestamp + (blocks * block_time)
            return True
        except Exception as e:
            logger.error(f"Failed to advance time: {e}")
            return False

    def evolve_network(self, iteration: int) -> Dict[str, int]:
        """
        Evolve the network by having agents perform actions based on their profiles.
        
        Args:
            iteration: Current iteration number
            
        Returns:
            Dict[str, int]: Statistics about actions performed
        """
        stats = {
            'mints': 0,
            'trusts': 0,
            'transfers': 0,
            'groups_created': 0,
            'total_actions': 0
        }
        
        try:
            # Get all active agents
            all_agents = list(self.agent_manager.agents.values())
            random.shuffle(all_agents)  # Randomize order of actions
            
            logger.info(f"Processing actions for {len(all_agents)} agents in iteration {iteration}")
            
            # Process each agent's potential actions
            for agent in all_agents:
                if not agent.should_act_this_iteration():
                    continue
                    
                action, params = agent.decide_action()
                success = self._perform_agent_action(agent, action, params)
                
                if success:
                    stats[f'{action}s'] = stats.get(f'{action}s', 0) + 1
                    stats['total_actions'] += 1
                    
            logger.info(f"Iteration {iteration} stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to evolve network: {e}")
            return stats

    def _perform_agent_action(self, agent: Agent, action: str, params: Dict) -> bool:
        """Execute a specific action for an agent."""
        try:
            if action == "mint":
                return self._handle_mint_action(agent)
            elif action == "establish_trust":
                return self._handle_trust_action(agent)
            elif action == "transfer":
                return self._handle_transfer_action(agent)
            elif action == "create_group":
                return self._handle_group_creation(agent)
            else:
                logger.warning(f"Unknown action type: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to perform {action} for agent: {e}")
            return False

    def _handle_mint_action(self, agent: Agent) -> bool:
        """Handle personal minting using the proven approach from previous implementation"""
        try:
            address = random.choice(list(agent.accounts.keys()))
            private_key = agent.accounts[address]
            account = Account.from_key(private_key)
            
            previous_balance = self.contract.balanceOf(address, int(str(address), 16))
            receipt = self.contract.personalMint(sender=account.address)
            
            for log in receipt.decode_logs():
                if log.event_name == "PersonalMint":
                    minted_amount = log.amount
                    
                    # Trigger mint event
                    if self.on_mint_performed:
                        self.on_mint_performed(
                            address=address,
                            amount=minted_amount,
                            block=chain.blocks.head.number,
                            timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp)
                        )
                    
                    if self.collector:
                        self.collector.record_balance_change(
                            account=str(address),
                            token_id=str(address),
                            block_number=chain.blocks.head.number,
                            timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp),
                            previous_balance=previous_balance,
                            new_balance=previous_balance + minted_amount,
                            tx_hash=receipt.txn_hash,
                            event_type="MINT"
                        )
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Mint action failed: {e}")
            return False

    def _handle_trust_action(self, agent: Agent) -> bool:
        """Handle trust relationship creation for an agent."""
        try:
            # Find potential trustees not already trusted
            all_addresses = set(self.agent_manager.address_to_agent_id.keys())
            potential_trustees = all_addresses - agent.trusted_agents
            
            if not potential_trustees:
                return False
                
            # Select random trustee
            trustee_address = random.choice(list(potential_trustees))
            trustee_agent = self.agent_manager.get_agent_by_address(trustee_address)
            
            if not trustee_agent or not agent.should_trust(trustee_agent):
                return False
                
            # Select random account owned by the agent to establish trust
            truster_address = random.choice(list(agent.accounts.keys()))
            private_key = agent.accounts[truster_address]
            account = Account.from_key(private_key)
            
            # Create trust relationship
            trust_limit = 10000000  # Standard trust limit
            receipt = self.contract.trust(
                trustee_address,
                trust_limit,
                sender=account.address
            )
            
            # Update agent's trust set
            agent.trusted_agents.add(trustee_address)
            
            # Record trust relationship
            if self.collector:
                self.collector.record_trust_relationship(
                    truster=truster_address,
                    trustee=trustee_address,
                    block_number=chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp),
                    trust_limit=float(trust_limit),
                    expiry_time=datetime.fromtimestamp(chain.blocks.head.timestamp) + timedelta(days=365)
                )
                
            return True
            
        except Exception as e:
            logger.error(f"Trust action failed: {e}")
            return False

    def _handle_transfer_action(self, agent: Agent) -> bool:
        """Handle token transfer using similar principles to the proven mint implementation"""
        try:
            if not agent.trusted_agents:
                return False
                
            source_address = random.choice(list(agent.accounts.keys()))
            recipient_address = random.choice(list(agent.trusted_agents))
            
            token_id = int(str(source_address), 16)
            source_balance = self.contract.balanceOf(source_address, token_id)
            
            if source_balance == 0:
                return False
                
            transfer_amount = int(source_balance * random.uniform(0.1, 0.3))
            if transfer_amount == 0:
                return False
                
            account = Account.from_key(agent.accounts[source_address])
            previous_balance = source_balance
            
            receipt = self.contract.safeTransferFrom(
                source_address,
                recipient_address,
                token_id,
                transfer_amount,
                "",
                sender=account.address
            )
            
            # Trigger transfer event
            if self.on_transfer_performed:
                self.on_transfer_performed(
                    from_address=source_address,
                    to_address=recipient_address,
                    amount=transfer_amount,
                    block=chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp)
                )
            
            if self.collector:
                self.collector.record_balance_change(
                    account=str(source_address),
                    token_id=str(source_address),
                    block_number=chain.blocks.head.number,
                    timestamp=datetime.fromtimestamp(chain.blocks.head.timestamp),
                    previous_balance=previous_balance,
                    new_balance=previous_balance - transfer_amount,
                    tx_hash=receipt.txn_hash,
                    event_type="TRANSFER"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Transfer action failed: {e}")
            return False

    def _handle_group_creation(self, agent: Agent) -> bool:
        """Handle group creation for an agent."""
        # Only certain personalities create groups
        if agent.profile.personality not in [
            AgentPersonality.ENTREPRENEUR,
            AgentPersonality.COMMUNITY
        ]:
            return False
            
        try:
            # Select random account owned by the agent
            address = random.choice(list(agent.accounts.keys()))
            private_key = agent.accounts[address]
            account = Account.from_key(private_key)
            
            # Generate group name and symbol
            group_number = len(agent.groups) + 1
            name = f"Group_{address[:6]}_{group_number}"
            symbol = f"GRP{address[:4]}{group_number}"
            
            # Create group
            receipt = self.contract.registerGroup(
                address,  # mint policy address (using agent's address)
                name,
                symbol,
                HexBytes(0),  # metadata digest
                sender=account.address
            )
            
            # Add group to agent's groups
            agent.groups.add(address)
            
            return True
            
        except Exception as e:
            logger.error(f"Group creation failed: {e}")
            return False