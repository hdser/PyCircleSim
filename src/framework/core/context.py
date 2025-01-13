from dataclasses import dataclass
from typing import Dict, Any, Optional
from src.framework.agents import AgentManager, BaseAgent

@dataclass
class SimulationContext:
    """Encapsulates the context needed for simulation actions"""
    agent: BaseAgent
    agent_manager: AgentManager
    clients: Dict[str, Any]
    chain: Any   
    network_state: Dict[str, Any]
    
    def get_client(self, contract_id: str) -> Any:
        """Get client for specific contract"""
        return self.clients.get(contract_id)
    
    def get_contract_state(self, contract_id: str, var_name: str, default: Any = None) -> Any:
        """Helper to get contract state"""
        return self.network_state.get('contract_states', {}).get(contract_id, {}).get('state', {}).get(var_name, default)
        
    def get_running_state(self, key: str, default: Any = None) -> Any:
        """Helper to get running state"""
        return self.network_state.get('running_state', {}).get(key, default)
        
    def update_running_state(self, updates: Dict[str, Any]):
        """Helper to update running state"""
        if 'running_state' not in self.network_state:
            self.network_state['running_state'] = {}
        self.network_state['running_state'].update(updates)