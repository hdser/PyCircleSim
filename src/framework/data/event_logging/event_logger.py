from typing import Dict, Optional, List
from datetime import datetime
import json
from dataclasses import dataclass, asdict
from pathlib import Path
import duckdb
from src.framework.logging import get_logger

logger = get_logger(__name__)

@dataclass
class ContractEvent:
    simulation_run_id: int
    event_name: str
    block_number: int 
    block_timestamp: datetime
    transaction_hash: str
    tx_from: Optional[str]
    tx_to: Optional[str]
    tx_index: Optional[int]
    log_index: Optional[int]
    contract_address: str
    topic0: str
    event_data: Dict
    action_name: Optional[str] = None

class EventLogger:
    """Efficient event logging system for contract events"""
    
    def __init__(self, connection: duckdb.DuckDBPyConnection):
        """Initialize with DuckDB connection"""
        self.con = connection
        self.sql_dir = Path(__file__).parent.parent / "duckdb"
        self._initialize_table()
        self._subscribers = []

    def subscribe(self, callback):
        """Add a subscriber callback"""
        self._subscribers.append(callback)
        
    def _initialize_table(self):
        """Ensure events table exists"""
        schema_file = self.sql_dir / "schema" / "events.up.sql"
        with open(schema_file, 'r') as f:
            self.con.execute(f.read())
            self.con.commit()

    def _read_query(self, filename: str) -> str:
        """Read SQL query from file"""
        query_file = self.sql_dir / "queries" / filename
        with open(query_file, 'r') as f:
            return f.read()

    def record_event(self, event: ContractEvent) -> bool:
        """Record a contract event to the database"""
        try:
            sql = self._read_query("insert_event.sql")
            
            # Convert dataclass to dict and serialize JSON fields
            data = asdict(event)
            data['event_data'] = {key: str(value) for key, value in data['event_data'].items()}
            
            self.con.execute(sql, [
                data['simulation_run_id'],
                data['action_name'],
                data['event_name'],
                data['block_number'],
                data['block_timestamp'],
                data['transaction_hash'],
                data['tx_from'],
                data['tx_to'],
                data['tx_index'],
                data['log_index'],
                data['contract_address'],
                data['topic0'],
                data['event_data']
            ])
            self.con.commit()
            logger.info(f"Recorded contract event '{data['event_name']}' at block {data['block_number']}")

            # Notify subscribers
            for subscriber in self._subscribers:
                try:
                    subscriber(event)
                except Exception as e:
                    logger.error(f"Error notifying subscriber: {e}")
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to record event {event.event_name}: {e}")
            return False

    def get_events(
        self,
        simulation_run_id: int,
        event_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """Query events with filters"""
        try:
            sql = self._read_query("get_events.sql")
            params = [simulation_run_id]
            
            if event_name:
                params.append(event_name)
            if start_time:
                params.append(start_time)
            if end_time:
                params.append(end_time)
            params.append(limit)
            
            result = self.con.execute(sql, params).fetchdf()
            
            # Convert JSON strings back to dicts
            for col in ['topics', 'event_data', 'indexed_values', 'decoded_values']:
                if col in result.columns:
                    result[col] = result[col].apply(json.loads)
                    
            return result.to_dict('records')
            
        except Exception as e:
            logger.error(f"Failed to query events: {e}")
            return []

    def get_event_stats(self, simulation_run_id: int) -> List[Dict]:
        """Get event statistics for a simulation run"""
        try:
            sql = self._read_query("get_event_stats.sql")
            return self.con.execute(sql, [simulation_run_id]).fetchdf().to_dict('records')
            
        except Exception as e:
            logger.error(f"Failed to get event stats: {e}")
            return []