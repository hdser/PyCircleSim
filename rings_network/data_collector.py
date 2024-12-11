import duckdb
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import pandas as pd
import logging
import json

logger = logging.getLogger(__name__)


class CirclesDataCollector:
    """
    A data collection system for the Circles network using DuckDB as the storage backend.
    Tracks network events and state changes in real-time.
    """
    
    def __init__(self, db_path: str = "circles_network.duckdb"):
        """
        Initialize the data collector with a DuckDB database connection.
        
        Args:
            db_path: Path where the DuckDB database file will be stored
        """
        self.db_path = db_path
        self.con = duckdb.connect(db_path)
        self._initialize_database()
        logger.info(f"Initialized CirclesDataCollector with database at {db_path}")
        
    def _initialize_database(self):
        """
        Set up the database schema for tracking Rings/Circles network activity.
        
        We use several key tables to track different aspects of the network:
        - humans: Records who is in the network and when they joined
        - trusts: Tracks trust relationships between participants
        - balance_changes: Logs all changes to token balances
        - network_stats: Stores periodic snapshots of overall network state
        
        All monetary values use DOUBLE precision to handle the large numbers that can
        arise from token inflation and demurrage calculations in the Rings protocol.
        """
        # Humans table: Tracks all registered participants in the network
        # Each human is uniquely identified by their blockchain address
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS humans (
                address VARCHAR PRIMARY KEY,            -- Blockchain address of the human
                registration_timestamp TIMESTAMP,       -- When they registered
                registration_block BIGINT,             -- Block number of registration
                inviter_address VARCHAR,               -- Who invited them (if anyone)
                welcome_bonus_amount DOUBLE            -- Initial tokens received
            );
        """)
        
        # Trust relationships table: Records who trusts whom and for how much
        # The combination of truster, trustee, and timestamp creates a unique trust record
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS trusts (
                truster_address VARCHAR,               -- Address giving trust
                trustee_address VARCHAR,               -- Address receiving trust
                trust_timestamp TIMESTAMP,             -- When trust was established
                trust_block BIGINT,                    -- Block number of trust creation
                trust_limit DOUBLE,                    -- Maximum trust amount (in tokens)
                expiry_time TIMESTAMP,                 -- When trust relationship expires
                PRIMARY KEY (truster_address, trustee_address, trust_timestamp)
            );
        """)
        
        # Balance changes table: Tracks every change to token balances
        # This gives us a complete history of token movements
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS balance_changes (
                account_address VARCHAR,               -- Address whose balance changed
                token_id VARCHAR,                      -- ID of token (derived from address)
                block_number BIGINT,                   -- Block where change occurred
                timestamp TIMESTAMP,                   -- When the change happened
                previous_balance DOUBLE,               -- Balance before change
                new_balance DOUBLE,                    -- Balance after change
                change_amount DOUBLE,                  -- Amount of change (can be negative)
                transaction_hash VARCHAR,              -- Transaction causing the change
                event_type VARCHAR                     -- Type of event (MINT/TRANSFER/BURN)
            );
        """)
        
        # Network statistics table: Periodic snapshots of network state
        # Helps track how the network evolves over time
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS network_stats (
                timestamp TIMESTAMP,                   -- When snapshot was taken
                block_number BIGINT,                   -- Block number of snapshot
                total_humans INT,                      -- Number of registered humans
                total_active_trusts INT,               -- Count of valid trust relationships
                total_supply DOUBLE,                   -- Total tokens in circulation
                average_balance DOUBLE,                -- Average tokens per account
                trust_density DOUBLE,                  -- Measure of network connectivity
                PRIMARY KEY (timestamp)                -- One snapshot per timestamp
            );
        """)
        
        # Views for common queries and analysis
        
        # Current balances view: Shows latest balance for each account/token pair
        # This is more efficient than querying the full history each time
        self.con.execute("""
            CREATE VIEW IF NOT EXISTS current_balances AS
            SELECT 
                account_address,
                token_id,
                new_balance as current_balance,
                max(block_number) as last_updated_block,
                max(timestamp) as last_updated_time
            FROM balance_changes
            GROUP BY account_address, token_id, new_balance;
        """)
        
        # Active trusts view: Shows currently valid trust relationships
        # Filters out expired trusts and only shows latest trust value
        self.con.execute("""
            CREATE VIEW IF NOT EXISTS active_trusts AS
            SELECT 
                truster_address,
                trustee_address,
                trust_limit,
                expiry_time
            FROM trusts t1
            WHERE trust_timestamp = (
                SELECT MAX(trust_timestamp)
                FROM trusts t2
                WHERE t1.truster_address = t2.truster_address
                AND t1.trustee_address = t2.trustee_address
            )
            AND expiry_time > CURRENT_TIMESTAMP;
        """)
        
        # Commit all changes to ensure the database is properly initialized
        self.con.commit()
        
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
        
        Args:
            address: Address of the newly registered human
            block_number: Block number when registration occurred
            timestamp: Timestamp of registration
            inviter_address: Address of the inviter (if any)
            welcome_bonus: Amount of welcome bonus received
        """
        try:
            self.con.execute("""
                INSERT INTO humans (
                    address, registration_timestamp, registration_block, 
                    inviter_address, welcome_bonus_amount
                ) VALUES (?, ?, ?, ?, ?);
            """, [address, timestamp, block_number, inviter_address, welcome_bonus])
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
        
        Args:
            truster: Address of the account giving trust
            trustee: Address of the account receiving trust
            block_number: Block number when trust was established
            timestamp: Timestamp of trust establishment
            trust_limit: Amount of trust limit set
            expiry_time: When the trust relationship expires
        """
        try:
            self.con.execute("""
                INSERT INTO trusts (
                    truster_address, trustee_address, trust_timestamp,
                    trust_block, trust_limit, expiry_time
                ) VALUES (?, ?, ?, ?, ?, ?);
            """, [truster, trustee, timestamp, block_number, trust_limit, expiry_time])
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
            # Convert to human-readable numbers by dividing by 10^15
            scale = 10**15
            previous_balance_scaled = previous_balance / scale
            new_balance_scaled = new_balance / scale
            change_amount = new_balance_scaled - previous_balance_scaled
            
            self.con.execute("""
                INSERT INTO balance_changes (
                    account_address, token_id, block_number, timestamp,
                    previous_balance, new_balance, change_amount,
                    transaction_hash, event_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, [
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
        Automatically calculates various network metrics.
        
        Args:
            block_number: Current block number
            timestamp: Current timestamp
        """
        try:
            # Calculate network statistics using SQL
            stats = self.con.execute("""
                WITH current_stats AS (
                    SELECT 
                        COUNT(DISTINCT address) as total_humans
                        FROM humans
                ),
                trust_stats AS (
                    SELECT 
                        COUNT(*) as total_active_trusts,
                        COUNT(*) * 1.0 / NULLIF(POW((SELECT total_humans FROM current_stats), 2), 0) as trust_density
                    FROM active_trusts
                ),
                balance_stats AS (
                    SELECT 
                        SUM(current_balance) as total_supply,
                        AVG(current_balance) as average_balance
                    FROM current_balances
                )
                SELECT 
                    c.total_humans,
                    t.total_active_trusts,
                    t.trust_density,
                    b.total_supply,
                    b.average_balance
                FROM current_stats c
                CROSS JOIN trust_stats t
                CROSS JOIN balance_stats b;
            """).fetchone()
            
            self.con.execute("""
                INSERT INTO network_stats (
                    timestamp, block_number, total_humans, total_active_trusts,
                    total_supply, average_balance, trust_density
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """, [timestamp, block_number, *stats])
            self.con.commit()
            logger.info(f"Recorded network statistics for block {block_number}")
        except Exception as e:
            logger.error(f"Failed to record network statistics: {e}")
            raise
            
    def get_analysis_queries(self) -> Dict[str, str]:
        """
        Returns a dictionary of useful analysis queries.
        """
        return {
            "human_growth": """
                SELECT 
                    date_trunc('day', registration_timestamp) as day,
                    COUNT(*) as new_registrations,
                    SUM(COUNT(*)) OVER (ORDER BY date_trunc('day', registration_timestamp)) as total_humans
                FROM humans
                GROUP BY 1
                ORDER BY 1;
            """,
            
            "trust_network_growth": """
                SELECT 
                    date_trunc('day', trust_timestamp) as day,
                    COUNT(*) as new_trusts,
                    COUNT(DISTINCT truster_address) as unique_trusters,
                    COUNT(DISTINCT trustee_address) as unique_trustees
                FROM trusts
                GROUP BY 1
                ORDER BY 1;
            """,
            
            "token_velocity": """
                SELECT 
                    date_trunc('hour', timestamp) as hour,
                    COUNT(*) as total_transfers,
                    SUM(ABS(change_amount)) as total_volume,
                    COUNT(DISTINCT account_address) as active_accounts
                FROM balance_changes
                WHERE event_type = 'TRANSFER'
                GROUP BY 1
                ORDER BY 1;
            """,
            
            "top_trusted_accounts": """
                SELECT 
                    trustee_address,
                    COUNT(DISTINCT truster_address) as trust_count,
                    AVG(trust_limit) as avg_trust_limit
                FROM active_trusts
                GROUP BY 1
                ORDER BY 2 DESC
                LIMIT 10;
            """
        }
    
    def export_to_csv(self, output_dir: str = "analysis_results"):
        """
        Export all tables to CSV files for external analysis.
        
        Args:
            output_dir: Directory to save CSV files
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