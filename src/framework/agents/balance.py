import json
from ape import Contract
from src.framework.logging import get_logger

logger = get_logger(__name__)

class BalanceTracker:
    """Tracks ERC20 balances by subscribing to events"""
    
    def __init__(self, agent_manager: 'AgentManager'):
        self.agent_manager = agent_manager
        
    def subscribe(self, event_logger: 'EventLogger'):
        """Subscribe to event logger"""
        event_logger.subscribe(self.handle_event)

    def _collect_unique_addresses(self, event: 'ContractEvent') -> set:
        """Collect all unique addresses involved in the event"""
        addresses = set()
        
        # Add basic tx addresses
        if event.tx_from:
            addresses.add(event.tx_from)
        if event.tx_to:
            addresses.add(event.tx_to)
            
        # Add contract address
        addresses.add(event.contract_address)
        
        # Extract addresses from event data
        try:
            event_data = json.loads(event.event_data) if isinstance(event.event_data, str) else event.event_data
        except:
            event_data = {}
            
        def extract_addresses(value):
            if isinstance(value, str) and value.startswith('0x') and len(value) == 42:
                addresses.add(value)
            elif isinstance(value, list):
                for item in value:
                    extract_addresses(item)
            elif isinstance(value, dict):
                for v in value.values():
                    extract_addresses(v)
                    
        extract_addresses(event_data)
                            
        # Remove None and invalid addresses
        addresses = {addr for addr in addresses if addr and isinstance(addr, str) and addr.startswith('0x')}
        return addresses
        
    def handle_event(self, event: 'ContractEvent'):
        """Handle an event by updating relevant agent balances"""
        try:
            # Get all addresses involved using comprehensive helper
            addresses = self._collect_unique_addresses(event)
            
            # Try to get balances
            contract = Contract(event.contract_address, abi=[{
                "constant": True,
                "inputs": [{"name": "_owner","type": "address"}],
                "name": "balanceOf", 
                "outputs": [{"name": "","type": "uint256"}],
                "payable": False,
                "stateMutability": "view",  
                "type": "function"
            }])
            
            for address in addresses:
                try:
                    balance = contract.balanceOf(address)
                    if balance is not None:
                        # Update agent's balance if address belongs to an agent
                        agent = self.agent_manager.get_agent_by_address(address)
                        if agent:
                            agent.update_balance(
                                account=address,
                                contract=event.contract_address,
                                balance=balance,
                                timestamp=event.block_timestamp,
                                block=event.block_number
                            )
                except Exception as e:
                    logger.debug(f"Failed to get balance for {address}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to handle balance update: {e}")