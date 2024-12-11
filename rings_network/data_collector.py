import duckdb
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import pandas as pd
import logging
import json
import os

logger = logging.getLogger(__name__)


class CirclesDataCollector:
    """
    A data collection system for the Circles network using DuckDB as the storage backend.
    Tracks network events and state changes in real-time.
    """
    
    def __init__(self, db_path: str = "circles_network.duckdb", sql_dir: Optional[str] = None):
        """
        Initialize the data collector with a DuckDB database connection.
        
        Args:
            db_path: Path where the DuckDB database file will be stored
            sql_dir: Directory containing SQL query files. If None, defaults to 
                    'duckdb' directory next to this module
        """
        self.db_path = db_path
        
        # If sql_dir is not provided, use the duckdb directory next to this module
        if sql_dir is None:
            # Get the directory where this module is located
            module_dir = Path(__file__).parent
            self.sql_dir = module_dir / "duckdb"
        else:
            self.sql_dir = Path(sql_dir)
            
        # Ensure the SQL directory exists
        if not self.sql_dir.exists():
            raise FileNotFoundError(
                f"SQL directory not found at {self.sql_dir}. "
                "Please ensure the duckdb directory exists and contains the SQL files."
            )
            
        self.con = duckdb.connect(db_path)
        self._initialize_database()
        logger.info(f"Initialized CirclesDataCollector with database at {db_path}")
        
    def _read_sql_file(self, filename: str) -> str:
        """
        Read SQL query from a file in the SQL directory.
        
        Args:
            filename: Name of the SQL file to read
            
        Returns:
            str: Contents of the SQL file
            
        Raises:
            FileNotFoundError: If the SQL file doesn't exist
        """
        sql_file = self.sql_dir / filename
        if not sql_file.exists():
            raise FileNotFoundError(
                f"SQL file '{filename}' not found at {sql_file}. "
                f"Please ensure the file exists in the {self.sql_dir} directory."
            )
            
        try:
            with open(sql_file, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading SQL file {filename}: {e}")
            raise
        
    def _initialize_database(self):
        """
        Set up the database schema by executing SQL files from the duckdb directory.
        Each table has its own .up.sql file for creation.
        """
        # Create tables using SQL files
        tables = [
            "humans.up.sql",
            "trusts.up.sql", 
            "balance_changes.up.sql",
            "network_stats.up.sql"
        ]
        
        # Create views using SQL files
        views = [
            "current_balances.view.sql",
            "active_trusts.view.sql"
        ]
        
        try:
            # Execute table creation scripts
            for table_file in tables:
                sql = self._read_sql_file('schema/' + table_file)
                self.con.execute(sql)
                logger.info(f"Created table from {table_file}")
                
            # Execute view creation scripts    
            for view_file in views:
                sql = self._read_sql_file('views/' + view_file)
                self.con.execute(sql)
                logger.info(f"Created view from {view_file}")
                
            self.con.commit()
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
        
    def record_human_registration(
        self,
        address: str,
        block_number: int,
        timestamp: datetime,
        inviter_address: Optional[str] = None,
        welcome_bonus: Optional[float] = None
    ):
        """
        Record a new human registration in the network.
        """
        try:
            sql = self._read_sql_file("queries/insert_human.sql")
            self.con.execute(sql, [
                address, timestamp, block_number, inviter_address, welcome_bonus
            ])
            self.con.commit()
            logger.info(f"Recorded new human registration: {address}")
        except Exception as e:
            logger.error(f"Failed to record human registration: {e}")
            raise
            
    def record_trust_relationship(
        self,
        truster: str,
        trustee: str,
        block_number: int,
        timestamp: datetime,
        trust_limit: float,
        expiry_time: datetime
    ):
        """
        Record a new or updated trust relationship.
        """
        try:
            sql = self._read_sql_file("queries/insert_trust.sql")
            self.con.execute(sql, [
                truster, trustee, timestamp, block_number, trust_limit, expiry_time
            ])
            self.con.commit()
            logger.info(f"Recorded trust relationship: {truster} -> {trustee}")
        except Exception as e:
            logger.error(f"Failed to record trust relationship: {e}")
            raise
            
    def record_balance_change(
        self,
        account: str,
        token_id: str,
        block_number: int,
        timestamp: datetime,
        previous_balance: int,
        new_balance: int,
        tx_hash: str,
        event_type: str
    ):
        """
        Record a balance change event, handling the conversion from blockchain's
        18-decimal integer representation to human-readable numbers.
        """
        try:
            # Convert to human-readable numbers
            scale = 10**15
            previous_balance_scaled = previous_balance / scale
            new_balance_scaled = new_balance / scale
            change_amount = new_balance_scaled - previous_balance_scaled
            
            sql = self._read_sql_file("queries/insert_balance_change.sql")
            self.con.execute(sql, [
                account, token_id, block_number, timestamp,
                previous_balance_scaled, new_balance_scaled, change_amount,
                tx_hash, event_type
            ])
            self.con.commit()
            logger.info(f"Recorded {event_type} balance change for {account}: {change_amount}")
        except Exception as e:
            logger.error(f"Failed to record balance change: {e}")
            raise
            
    def record_network_statistics(
        self,
        block_number: int,
        timestamp: datetime
    ):
        """
        Record network-wide statistics at a given point in time.
        """
        try:
            # Calculate statistics using the stats calculation query
            calc_sql = self._read_sql_file("analysis/calculate_network_stats.sql")
            stats = self.con.execute(calc_sql).fetchone()
            
            # Insert the calculated statistics
            insert_sql = self._read_sql_file("queries/insert_network_stats.sql")
            self.con.execute(insert_sql, [timestamp, block_number, *stats])
            self.con.commit()
            logger.info(f"Recorded network statistics for block {block_number}")
        except Exception as e:
            logger.error(f"Failed to record network statistics: {e}")
            raise
            
    def get_analysis_queries(self) -> Dict[str, str]:
        """
        Returns a dictionary of analysis queries read from SQL files.
        """
        analysis_queries = {
            "human_growth": "analyze_human_growth.sql",
            "trust_network_growth": "analyze_trust_growth.sql",
            "token_velocity": "analyze_token_velocity.sql",
            "top_trusted_accounts": "analyze_top_trusted.sql"
        }
        
        return {
            name: self._read_sql_file('analysis/' + filename)
            for name, filename in analysis_queries.items()
        }
    
    def export_to_csv(self, output_dir: str = "analysis_results"):
        """
        Export all tables to CSV files for external analysis.
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        tables = ["humans", "trusts", "balance_changes", "network_stats"]
        for table in tables:
            df = self.con.execute(f"SELECT * FROM {table}").df()
            df.to_csv(f"{output_dir}/{table}.csv", index=False)
            
        logger.info(f"Exported all tables to CSV in {output_dir}")
        
    def close(self):
        """
        Close the database connection.
        """
        self.con.close()
        logger.info("Closed database connection")

# Example usage
if __name__ == "__main__":
    # Initialize collector
    collector = CirclesDataCollector()
    
    # Record some test data
    test_timestamp = datetime.now()
    
    # Record a new human
    collector.record_human_registration(
        "0x123...",
        block_number=1000,
        timestamp=test_timestamp,
        welcome_bonus=100.0
    )
    
    # Record a trust relationship
    collector.record_trust_relationship(
        "0x123...",
        "0x456...",
        block_number=1001,
        timestamp=test_timestamp,
        trust_limit=1000.0,
        expiry_time=test_timestamp
    )
    
    # Record a balance change
    collector.record_balance_change(
        "0x123...",
        "0x789...",
        block_number=1002,
        timestamp=test_timestamp,
        previous_balance=0.0,
        new_balance=100.0,
        tx_hash="0xabc...",
        event_type="MINT"
    )
    
    # Record network statistics
    collector.record_network_statistics(
        block_number=1002,
        timestamp=test_timestamp
    )
    
    # Export data
    collector.export_to_csv()
    
    # Close connection
    collector.close()