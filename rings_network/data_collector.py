import duckdb
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
import pandas as pd
import logging
import json
import os
from collections import defaultdict

logger = logging.getLogger(__name__)

class CirclesDataCollector:
    """
    Enhanced data collection system for the Circles network that maintains SQL queries
    in external files while providing improved data handling and validation.
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
        
        if sql_dir is None:
            module_dir = Path(__file__).parent
            self.sql_dir = module_dir / "duckdb"
        else:
            self.sql_dir = Path(sql_dir)
            
        if not self.sql_dir.exists():
            raise FileNotFoundError(
                f"SQL directory not found at {self.sql_dir}. "
                "Please ensure the duckdb directory exists and contains the SQL files."
            )
            
        # Initialize database connection and tracking data
        self.con = duckdb.connect(db_path)
        self._last_timestamp = defaultdict(lambda: datetime.min)
        self.sequence_number = defaultdict(int)
        
        # Set up database schema
        self._initialize_database()
        logger.info(f"Initialized CirclesDataCollector with database at {db_path}")

    def _get_unique_timestamp(self, base_timestamp: datetime, table_name: str) -> datetime:
        """Generate a unique timestamp for database operations."""
        if base_timestamp <= self._last_timestamp[table_name]:
            self.sequence_number[table_name] += 1
            unique_timestamp = self._last_timestamp[table_name] + timedelta(microseconds=self.sequence_number[table_name])
        else:
            self.sequence_number[table_name] = 0
            unique_timestamp = base_timestamp
            
        self._last_timestamp[table_name] = unique_timestamp
        return unique_timestamp

    def _read_sql_file(self, filename: str) -> str:
        """Read SQL query from the file system."""
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
        """Initialize database using SQL files from the schema directory."""
        try:
            # Execute table creation scripts
            tables = [
                "humans.up.sql",
                "trusts.up.sql", 
                "balance_changes.up.sql",
                "network_stats.up.sql"
            ]
            
            for table_file in tables:
                sql = self._read_sql_file('schema/' + table_file)
                self.con.execute(sql)
                logger.info(f"Created table from {table_file}")
                
            # Execute view creation scripts    
            views = [
                "current_balances.view.sql",
                "active_trusts.view.sql"
            ]
            
            for view_file in views:
                sql = self._read_sql_file('views/' + view_file)
                self.con.execute(sql)
                logger.info(f"Created view from {view_file}")
                
            self.con.commit()
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def _validate_ethereum_address(self, address: str) -> bool:
        """Validate Ethereum address format."""
        if not address:
            return False
        return (
            address.startswith('0x') and 
            len(address) == 42 and 
            all(c in '0123456789abcdefABCDEF' for c in address[2:])
        )

    def record_human_registration(
        self,
        address: str,
        block_number: int,
        timestamp: datetime,
        inviter_address: Optional[str] = None,
        welcome_bonus: Optional[float] = None
    ):
        """Record a new human registration with validation."""
        try:
            if not self._validate_ethereum_address(address):
                raise ValueError(f"Invalid address format: {address}")
                
            if inviter_address and not self._validate_ethereum_address(inviter_address):
                raise ValueError(f"Invalid inviter address format: {inviter_address}")
                
            unique_timestamp = self._get_unique_timestamp(timestamp, 'humans')
            
            sql = self._read_sql_file("queries/insert_humans.sql")
            self.con.execute(sql, [
                address, unique_timestamp, block_number,
                inviter_address, welcome_bonus
            ])
            self.con.commit()
            
            logger.info(f"Recorded new human registration: {address}")
            
        except Exception as e:
            logger.error(f"Failed to record human registration: {e}")
            self.con.rollback()
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
        """Record a trust relationship with validation."""
        try:
            if not self._validate_ethereum_address(truster):
                raise ValueError(f"Invalid truster address: {truster}")
                
            if not self._validate_ethereum_address(trustee):
                raise ValueError(f"Invalid trustee address: {trustee}")
                
            unique_timestamp = self._get_unique_timestamp(timestamp, 'trusts')
            
            sql = self._read_sql_file("queries/insert_trust.sql")
            self.con.execute(sql, [
                truster, trustee, unique_timestamp, block_number,
                trust_limit, expiry_time
            ])
            self.con.commit()
            
            logger.info(f"Recorded trust relationship: {truster} -> {trustee}")
            
        except Exception as e:
            logger.error(f"Failed to record trust relationship: {e}")
            self.con.rollback()
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
        """Record a balance change with proper scaling."""
        try:
            if not self._validate_ethereum_address(account):
                raise ValueError(f"Invalid account address: {account}")
                
            scale = 10**18  # Full 18 decimal places
            previous_balance_scaled = previous_balance / scale
            new_balance_scaled = new_balance / scale
            change_amount = new_balance_scaled - previous_balance_scaled
            
            unique_timestamp = self._get_unique_timestamp(timestamp, 'balance_changes')
            
            sql = self._read_sql_file("queries/insert_balance_change.sql")
            self.con.execute(sql, [
                account, token_id, block_number, unique_timestamp,
                previous_balance_scaled, new_balance_scaled, change_amount,
                tx_hash, event_type
            ])
            self.con.commit()
            
            logger.info(f"Recorded {event_type} balance change for {account}: {change_amount}")
            
        except Exception as e:
            logger.error(f"Failed to record balance change: {e}")
            self.con.rollback()
            raise

    def record_network_statistics(
        self,
        block_number: int,
        timestamp: datetime
    ):
        """Record network-wide statistics with unique timestamp handling."""
        try:
            # Get unique timestamp for this statistic record
            unique_timestamp = self._get_unique_timestamp(timestamp, 'network_stats')
            
            # Calculate statistics using the external SQL file
            calc_sql = self._read_sql_file("analysis/calculate_network_stats.sql")
            stats = self.con.execute(calc_sql).fetchone()
            
            if not stats:
                raise ValueError("Failed to calculate network statistics")
                
            # Insert using the external SQL file
            insert_sql = self._read_sql_file("queries/insert_network_stats.sql")
            self.con.execute(insert_sql, [unique_timestamp, block_number, *stats])
            self.con.commit()
            
            logger.info(f"Recorded network statistics for block {block_number}")
            
        except Exception as e:
            logger.error(f"Failed to record network statistics: {e}")
            self.con.rollback()
            raise

    def get_analysis_queries(self) -> Dict[str, str]:
        """Load analysis queries from files."""
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
        """Export all tables to CSV files with metadata."""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            tables = ["humans", "trusts", "balance_changes", "network_stats"]
            
            metadata = {
                "export_timestamp": datetime.now().isoformat(),
                "database_path": str(self.db_path),
                "table_statistics": {}
            }
            
            for table in tables:
                df = self.con.execute(f"SELECT * FROM {table}").df()
                csv_path = output_path / f"{table}.csv"
                df.to_csv(csv_path, index=False)
                
                metadata["table_statistics"][table] = {
                    "row_count": len(df),
                    "columns": list(df.columns),
                    "export_path": str(csv_path)
                }
                
            # Save metadata
            with open(output_path / "export_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
                
            logger.info(f"Exported all tables to CSV in {output_dir}")
            
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            raise

    def close(self):
        """Safely close the database connection."""
        try:
            self.con.close()
            logger.info("Closed database connection")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
            raise