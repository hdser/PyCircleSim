from typing import Optional, Dict, Any, List, Tuple
from abc import ABC, abstractmethod
from datetime import datetime

class BaseDataCollector(ABC):
    """Abstract base class defining data collection interface"""
   
    @abstractmethod
    def start_simulation_run(self, parameters: Optional[Dict] = None, 
                            description: Optional[str] = None) -> int:
        """Start new simulation run"""
        pass
        
    @abstractmethod 
    def end_simulation_run(self):
        """End current simulation run"""
        pass

    @abstractmethod
    def record_agent(self, agent: Any):
        """Record agent details"""
        pass

    @abstractmethod
    def record_agent_address(self, agent_id: str, address: str, 
                            is_primary: bool = False):
        """Record agent address"""
        pass

    @property
    @abstractmethod
    def current_run_id(self) -> Optional[int]:
        """Get current simulation run ID"""
        pass

    @abstractmethod
    def close(self):
        """Close collector resources"""
        pass
   
    @abstractmethod
    def record_network_statistics(self, block_number: int, timestamp: datetime):
        """Record network statistics"""
        pass

    @abstractmethod
    def record_transaction_events(self, tx):
        """Record transaction events"""
        pass

    @abstractmethod
    def get_events(self, event_name: Optional[str] = None,
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  limit: int = 1000) -> List[Dict]:
        """Get events"""
        pass

    @abstractmethod 
    def get_event_statistics(self) -> List[Dict]:
        """Get event statistics"""
        pass

    @abstractmethod
    def get_simulation_results(self, run_id: int) -> Dict:
        """Get simulation results"""
        pass


    @abstractmethod
    def get_agent_history(self, agent_id: str, run_id: Optional[int] = None) -> Dict:
        """Get agent history"""
        pass

    @abstractmethod
    def get_network_graph(self, run_id: Optional[int] = None) -> Tuple[List, List]:
        """Get network graph data"""
        pass

    @abstractmethod
    def record_state(self, block_number: int, block_timestamp: datetime, state_data: Dict[str, Any]):
        """Record simulation state at a given block"""
        pass

    @abstractmethod
    def get_state_history(self, run_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get state history for a simulation run"""
        pass


    @abstractmethod 
    def export_to_csv(self, output_dir: str = "analysis_results"):
        """Export data to CSV"""
        pass

    @abstractmethod
    def setup_contract_listeners(self, contracts: Dict[str, Any]):
        """Set up contract event listeners"""
        pass

    @abstractmethod
    def _validate_ethereum_address(self, address: str) -> bool:
        """Validate Ethereum address format"""
        pass

    @abstractmethod
    def _get_unique_timestamp(self, base_timestamp: datetime, table_name: str) -> datetime:
        """Get unique timestamp for database operations"""
        pass

