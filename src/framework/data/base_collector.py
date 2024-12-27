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

    @abstractmethod
    def record_human_registration(self, address: str, block_number: int,
                                timestamp: datetime,
                                inviter_address: Optional[str] = None,
                                welcome_bonus: Optional[float] = None):
        """Record human registration"""
        pass

    @abstractmethod
    def record_trust_relationship(self, truster: str, trustee: str,
                                block_number: int, timestamp: datetime,
                                expiry_time: datetime):
        """Record trust relationship"""
        pass

    @abstractmethod
    def record_balance_change(self, account: str, token_id: str,
                            block_number: int, timestamp: datetime,
                            previous_balance: Any, new_balance: Any,
                            tx_hash: str, event_type: str):
        """Record balance change"""
        pass

    @abstractmethod
    def record_group_registration(self, address: str, creator: str,
                                block_number: int, timestamp: datetime,
                                name: str, symbol: str, mint_policy: str) -> bool:
        """Record group registration"""
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
    def record_contract_event(self, event_name: str, block_number: int,
                            block_timestamp: datetime, transaction_hash: str,
                            tx_from: Optional[str], tx_to: Optional[str], 
                            log_index: Optional[int], contract_address: str,
                            topics: Any, event_data: Any, raw_data: Optional[str],
                            indexed_values: Optional[Any] = None,
                            decoded_values: Optional[Any] = None):
        """Record contract event"""
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
    def compare_simulations(self, run_ids: List[int]) -> Any:
        """Compare simulations"""
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