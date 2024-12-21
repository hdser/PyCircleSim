import duckdb
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple, Union
import pandas as pd
import logging
import json
import os
from ape import Contract
from collections import defaultdict
from src.framework.agents.base_agent import BaseAgent
from src.protocols.common.uint256_handler import UINT256Handler
from .event_logging import EventLogger, ContractEventHandler

logger = logging.getLogger(__name__)

class CirclesDataCollector:
    """
    Enhanced data collection system for the Circles network that maintains SQL queries
    in external files while providing improved data handling and validation.
    """
    
    def __init__(self, db_path: str = "circles_network.duckdb", sql_dir: Optional[str] = None):
        """Initialize the data collector with a DuckDB database connection."""
        self.db_path = db_path
        self.uint256_handler = UINT256Handler()
        
        if sql_dir is None:
            module_dir = Path(__file__).parent
            self.sql_dir = module_dir / "duckdb"
        else:
            self.sql_dir = Path(sql_dir)
            
        if not self.sql_dir.exists():
            raise FileNotFoundError(f"SQL directory not found at {self.sql_dir}")
            
        # Initialize database connection
        self.con = duckdb.connect(db_path)
        self._last_timestamp = defaultdict(lambda: datetime.min)
        self.sequence_number = defaultdict(int)
        self.current_run_id = None
        
        # Set up database schema
        self._initialize_database()
        logger.info(f"Initialized CirclesDataCollector with database at {db_path}")

        # Initialize event logging components
        self.event_logger = EventLogger(self.con)
        self.event_handler = None  # Will be initialized when simulation run starts

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
            # Execute table creation scripts in order of dependencies
            tables = [
                # First create base tables without foreign key dependencies
                "simulation_runs.up.sql",  # Must come first as other tables reference it
                "agents.up.sql",           # Depends on simulation_runs
                "agents_config.up.sql",
                "agent_addresses.up.sql",  # Depends on agents and simulation_runs
                "humans.up.sql",           # Depends on simulation_runs
                "groups.up.sql",           # Depends on simulation_runs
                "trusts.up.sql",           # Depends on simulation_runs
                "balance_changes.up.sql",  # Depends on simulation_runs
                "network_stats.up.sql",    # Depends on simulation_runs
                "contract_events.up.sql",
                "events_indexes.up.sql"
            ]
            
            for table_file in tables:
                sql = self._read_sql_file('schema/' + table_file)
                self.con.execute(sql)
                logger.info(f"Created table from {table_file}")
                
            # Execute view creation scripts after all tables exist   
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

    def start_simulation_run(self, parameters: Dict = None, description: str = None) -> int:
        """Start a new simulation run and return its ID."""
        try:
            sql = self._read_sql_file("queries/insert_simulation_run.sql")
            result = self.con.execute(sql, [
                datetime.now(),
                json.dumps(parameters) if parameters else None,
                description
            ]).fetchone()
            
            self.current_run_id = result[0]
            
            # Initialize event handler with current run ID
            self.event_handler = ContractEventHandler(self.event_logger, self.current_run_id)
            
            self.con.commit()
            logger.info(f"Started simulation run {self.current_run_id}")
            return self.current_run_id
            
        except Exception as e:
            logger.error(f"Failed to start simulation run: {e}")
            raise

    def setup_contract_listeners(self, contracts: Dict[str, Contract]):
        """Set up event listeners for contracts"""
        if not self.event_handler:
            logger.error("Event handler not initialized - must start simulation first")
            return
            
        for name, contract in contracts.items():
            try:
                self.event_handler.setup_event_listeners(contract)
                logger.info(f"Set up event listeners for contract: {name}")
            except Exception as e:
                logger.error(f"Failed to set up listeners for {name}: {e}")

    def get_events(self, event_name: Optional[str] = None, 
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  limit: int = 1000) -> List[Dict]:
        """Get events for current simulation run"""
        if not self.current_run_id:
            logger.warning("No active simulation run")
            return []
            
        return self.event_logger.get_events(
            simulation_run_id=self.current_run_id,
            event_name=event_name,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )

    def get_event_statistics(self) -> List[Dict]:
        """Get event statistics for current simulation run"""
        if not self.current_run_id:
            logger.warning("No active simulation run")
            return []
            
        return self.event_logger.get_event_stats(self.current_run_id)

    def start_simulation_run2(self, parameters: Dict = None, description: str = None) -> int:
        """Start a new simulation run and return its ID."""
        try:
            sql = self._read_sql_file("queries/insert_simulation_run.sql")
            result = self.con.execute(sql, [
                datetime.now(),
                json.dumps(parameters) if parameters else None,
                description
            ]).fetchone()
            
            self.current_run_id = result[0]
            self.con.commit()
            logger.info(f"Started simulation run {self.current_run_id}")
            return self.current_run_id
            
        except Exception as e:
            logger.error(f"Failed to start simulation run: {e}")
            raise
            
    def end_simulation_run(self):
        """Mark the current simulation run as completed."""
        if not self.current_run_id:
            logger.warning("No active simulation run to end")
            return
            
        try:
            sql = self._read_sql_file("queries/update_simulation_run.sql")
            self.con.execute(sql, [datetime.now(), self.current_run_id])
            self.con.commit()
            logger.info(f"Ended simulation run {self.current_run_id}")
            self.current_run_id = None
            
        except Exception as e:
            logger.error(f"Failed to end simulation run: {e}")
            raise
            
    def record_agent(self, agent: BaseAgent):
        """
        Record a comprehensive representation of a BaseAgent
        
        Args:
            agent: The BaseAgent instance to record
        """
        try:
            sql = self._read_sql_file("queries/insert_agent.sql")
            self.con.execute(sql, [
                agent.agent_id,
                self.current_run_id,
                agent.profile.name,
                agent.profile.description,
                len(agent.accounts),
                agent.profile.max_daily_actions,
                agent.profile.risk_tolerance,
                agent.profile.preferred_contracts
            ])
            
            # Insert action configurations
            sql = self._read_sql_file("queries/insert_agent_config.sql")
            
            for action_type, config in agent.profile.action_configs.items():
                self.con.execute(sql, [
                    agent.agent_id,
                    action_type.name,
                    config.probability,
                    config.cooldown_blocks,
                    config.gas_limit,
                    config.min_balance,
                    config.max_value,
                    json.dumps(config.constraints)
                ])
                       
            # Insert agent addresses
            sql = self._read_sql_file("queries/insert_agent_address.sql")
            for i, (address, private_key) in enumerate(agent.accounts.items()):
                self.con.execute(sql, [
                    agent.agent_id,
                    address,
                    i == 0,  
                    self.current_run_id
                ])
            self.con.commit()
            logger.info(f"Recorded agent {agent.agent_id} with {len(agent.accounts)} addresses")
            
        except Exception as e:
            logger.error(f"Failed to record agent {agent.agent_id}: {e}")
            self.con.rollback()
            raise
            
    def record_agent_address(self, agent_id: str, address: str, is_primary: bool = False):
        """Record an address associated with an agent."""
        if not self.current_run_id:
            raise ValueError("No active simulation run")
            
        try:
            sql = self._read_sql_file("queries/insert_agent_address.sql")
            self.con.execute(sql, [
                agent_id,
                address,
                is_primary,
                self.current_run_id
            ])
            self.con.commit()
            logger.debug(f"Recorded address {address} for agent {agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to record agent address: {e}")
            raise
            
    def record_human_registration(
        self,
        address: str,
        block_number: int,
        timestamp: datetime,
        inviter_address: Optional[str] = None,
        welcome_bonus: Optional[float] = None
    ):
        """Record a new human registration."""
        if not self.current_run_id:
            raise ValueError("No active simulation run")
            
        try:
            if not self._validate_ethereum_address(address):
                raise ValueError(f"Invalid address format: {address}")
                
            if inviter_address and not self._validate_ethereum_address(inviter_address):
                raise ValueError(f"Invalid inviter address format: {inviter_address}")
                
            unique_timestamp = self._get_unique_timestamp(timestamp, 'humans')
            
            sql = self._read_sql_file("queries/insert_humans.sql")
            self.con.execute(sql, [
                address,
                self.current_run_id,
                unique_timestamp,
                block_number,
                inviter_address,
                welcome_bonus
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
      #  trust_limit: Union[int, str],
        expiry_time: datetime
    ):
        """Record a trust relationship."""
        if not self.current_run_id:
            raise ValueError("No active simulation run")
            
        try:
            unique_timestamp = self._get_unique_timestamp(timestamp, 'trusts')
           # trust_limit_str = self.uint256_handler.to_string(trust_limit)
        
            # Check existing trust using SQL file
            check_sql = self._read_sql_file("queries/check_trust.sql")
            count = self.con.execute(check_sql, [
                truster,
                trustee,
                self.current_run_id,
                unique_timestamp
            ]).fetchone()[0]
            
            if count > 0:
                # Update existing trust using SQL file
                update_sql = self._read_sql_file("queries/update_trust.sql")
                self.con.execute(update_sql, [
                 #   trust_limit_str,
                    expiry_time,
                    truster,
                    trustee,
                    self.current_run_id,
                    unique_timestamp
                ])
            else:
                # Insert new trust using SQL file
                insert_sql = self._read_sql_file("queries/insert_trust.sql")
                self.con.execute(insert_sql, [
                    truster,
                    trustee,
                    self.current_run_id,
                    unique_timestamp,
                    block_number,
                  #  trust_limit_str,
                    expiry_time
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
        previous_balance: Union[int, str],
        new_balance: Union[int, str],
        tx_hash: str,
        event_type: str
    ):
        """Record a balance change."""
        if not self.current_run_id:
            raise ValueError("No active simulation run")
            
        try:
            if not self._validate_ethereum_address(account):
                raise ValueError(f"Invalid account address: {account}")
                
            unique_timestamp = self._get_unique_timestamp(timestamp, 'balance_changes')
            # Convert balances to string representation
            prev_bal_str = self.uint256_handler.to_string(previous_balance)
            new_bal_str = self.uint256_handler.to_string(new_balance)
            
            # Calculate change amount
            change = int(new_bal_str) - int(prev_bal_str)
            change_str = str(change)
            
            sql = self._read_sql_file("queries/insert_balance_change.sql")
            self.con.execute(sql, [
                account,
                token_id,
                self.current_run_id,
                block_number,
                unique_timestamp,
                prev_bal_str,
                new_bal_str,
                change_str,
                tx_hash,
                event_type
            ])
            self.con.commit()
            logger.info(f"Recorded {event_type} balance change for {account}: {change_str}")
            
        except Exception as e:
            logger.error(f"Failed to record balance change: {e}")
            raise

    def record_group_registration(
        self,
        address: str,
        creator: str,
        block_number: int,
        timestamp: datetime,
        name: str,
        symbol: str,
        mint_policy: str
    ) -> bool:
        """
        Record a new group registration.

        Args:
            address: Group address
            creator: Address of group creator
            block_number: Block number of registration
            timestamp: Registration timestamp
            name: Group name
            symbol: Group symbol
            mint_policy: Mint policy contract address

        Returns:
            bool: True if recording was successful
        """
        if not self.current_run_id:
            raise ValueError("No active simulation run")

        try:
            if not self._validate_ethereum_address(address):
                raise ValueError(f"Invalid group address format: {address}")

            #if not self._validate_ethereum_address(creator):
            #    raise ValueError(f"Invalid creator address format: {creator}")

            if not self._validate_ethereum_address(mint_policy):
                raise ValueError(f"Invalid mint policy address format: {mint_policy}")

            unique_timestamp = self._get_unique_timestamp(timestamp, 'groups')

            sql = self._read_sql_file("queries/insert_group.sql")
            self.con.execute(sql, [
                address,
                creator,
                self.current_run_id,
                unique_timestamp,
                block_number,
                name,
                symbol,
                mint_policy
            ])
            self.con.commit()
            logger.info(f"Recorded new group registration: {address} by {creator}")
            return True

        except Exception as e:
            logger.error(f"Failed to record group registration: {e}")
            raise

    def record_network_statistics(
        self,
        block_number: int,
        timestamp: datetime
    ):
        """Record network-wide statistics for the current simulation run."""
        if not self.current_run_id:
            raise ValueError("No active simulation run")
            
        try:
            unique_timestamp = self._get_unique_timestamp(timestamp, 'network_stats')
            
            # Calculate statistics using the SQL file
            calc_sql = self._read_sql_file("analysis/calculate_network_stats.sql")
            stats = self.con.execute(calc_sql).fetchone()
            
            if not stats:
                raise ValueError("Failed to calculate network statistics")
                
            # Insert using the SQL file
            sql = self._read_sql_file("queries/insert_network_stats.sql")
            self.con.execute(sql, [
                self.current_run_id,
                unique_timestamp,
                block_number,
                stats[0],  # total_humans
                stats[1],  # total_active_trusts
                stats[2],  # total_supply
                stats[3],  # average_balance
                stats[4]   # trust_density
            ])
            self.con.commit()
            
            logger.info(f"Recorded network statistics for block {block_number}")
            
        except Exception as e:
            logger.error(f"Failed to record network statistics: {e}")
            raise


    def record_contract_event(
        self,
        event_name: str,
        block_number: int,
        block_timestamp: datetime,
        transaction_hash: str,
        tx_from: Optional[str],
        tx_to: Optional[str],
        tx_index: Optional[int],
        log_index: Optional[int],
        contract_address: str,
        topics: Any,
        event_data: Any,
        raw_data: Optional[str],
        indexed_values: Optional[Any] = None,
        decoded_values: Optional[Any] = None
    ):
        """
        Record a new contract (or simulation) event in the 'contract_events' table.

        Args:
            event_name (str): Name/type of event (e.g. "TRANSFER", "TRUST", etc.)
            block_number (int): The block number at which this event was emitted
            block_timestamp (datetime): The on-chain timestamp for that block
            transaction_hash (str): The transaction hash for the event
            tx_from (str): Sender/transaction 'from' address
            tx_to (str): Recipient/transaction 'to' address
            tx_index (int): Transaction index in the block
            log_index (int): Log index for the event within the transaction
            contract_address (str): The contract address that emitted the event
            topics (Any): Topics array/list (will be stored as JSON)
            event_data (Any): Full event data (will be stored as JSON)
            raw_data (str): Hex string of the raw event data
            indexed_values (Any): Indexed parameters if needed (JSON)
            decoded_values (Any): Decoded event parameters if needed (JSON)
        """
        if not self.current_run_id:
            raise ValueError("No active simulation run")

        try:
            # Optional: Validate the contract address
            if not self._validate_ethereum_address(contract_address):
                raise ValueError(f"Invalid contract address: {contract_address}")

            # Generate a unique timestamp, if you want consistency with your other tables.
            # If you prefer to store the event's block_timestamp exactly, you can skip this.
            unique_timestamp = self._get_unique_timestamp(block_timestamp, 'contract_events')

            # Convert Python structures to JSON strings for storage in DuckDB's JSON columns
            import json
            topics_json = json.dumps(topics) if topics is not None else '[]'
            event_data_json = json.dumps(event_data) if event_data is not None else '{}'
            indexed_values_json = json.dumps(indexed_values) if indexed_values is not None else '{}'
            decoded_values_json = json.dumps(decoded_values) if decoded_values is not None else '{}'

            # Load the SQL from file
            sql = self._read_sql_file("queries/insert_contract_event.sql")

            # Execute the SQL INSERT
            self.con.execute(sql, [
                self.current_run_id,
                event_name,
                block_number,
                unique_timestamp,       # or block_timestamp if you prefer exactly that
                transaction_hash,
                tx_from,
                tx_to,
                tx_index,
                log_index,
                contract_address,
                topics_json,
                event_data_json,
                raw_data,
                indexed_values_json,
                decoded_values_json
            ])

            # Commit transaction
            self.con.commit()

            logger.info(f"Recorded contract event '{event_name}' at block {block_number}")

        except Exception as e:
            logger.error(f"Failed to record contract event '{event_name}': {e}")
            raise



    def get_simulation_results(self, run_id: int) -> Dict:
        """
        Retrieve comprehensive results for a specific simulation run.
        
        Args:
            run_id: The ID of the simulation run to analyze
            
        Returns:
            Dict containing various metrics and statistics about the simulation run
        """
        try:
            # Get basic simulation information
            sql = self._read_sql_file("queries/get_simulation_results.sql")
            results = self.con.execute(sql, [run_id]).fetchone()
            
            if not results:
                raise ValueError(f"No simulation found with ID {run_id}")
                
            # Get agent details
            agent_sql = self._read_sql_file("queries/get_agent_details.sql")
            agents = self.con.execute(agent_sql, [run_id]).fetchall()
            
            # Get network evolution over time
            network_stats_sql = self._read_sql_file("queries/get_network_stats_evolution.sql")
            network_evolution = self.con.execute(network_stats_sql, [run_id]).fetchall()
            
            return {
                "simulation_info": {
                    "run_id": run_id,
                    "start_time": results[1],
                    "end_time": results[2],
                    "parameters": json.loads(results[3]) if results[3] else None,
                    "description": results[4]
                },
                "network_metrics": {
                    "total_humans": results[5],
                    "total_trusters": results[6],
                    "total_trustees": results[7],
                    "active_accounts": results[8]
                },
                "agents": [dict(zip(["agent_id", "personality", "addresses"], a)) for a in agents],
                "network_evolution": network_evolution
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve simulation results: {e}")
            raise

    def compare_simulations(self, run_ids: List[int]) -> pd.DataFrame:
        """
        Compare multiple simulation runs side by side.
        
        Args:
            run_ids: List of simulation run IDs to compare
            
        Returns:
            DataFrame containing comparative metrics for each run
        """
        try:
            results = []
            for run_id in run_ids:
                sql = self._read_sql_file("queries/get_simulation_summary.sql")
                summary = self.con.execute(sql, [run_id]).fetchone()
                if summary:
                    results.append(summary)
                    
            return pd.DataFrame(results, columns=[
                'run_id', 'duration_minutes', 'total_humans', 'total_trusts',
                'active_accounts', 'total_supply', 'trust_density'
            ])
            
        except Exception as e:
            logger.error(f"Failed to compare simulations: {e}")
            raise

    def get_agent_history(self, agent_id: str, run_id: Optional[int] = None) -> Dict:
        """
        Get the complete history of an agent's activities in a simulation.
        
        Args:
            agent_id: The unique identifier of the agent
            run_id: Optional specific simulation run ID (defaults to current run)
            
        Returns:
            Dict containing the agent's profile and activity history
        """
        try:
            if not run_id and not self.current_run_id:
                raise ValueError("No simulation run specified or currently active")
                
            run_id = run_id or self.current_run_id
            
            # Get agent profile
            sql = self._read_sql_file("queries/get_agent_profile.sql")
            profile = self.con.execute(sql, [agent_id, run_id]).fetchone()
            
            if not profile:
                raise ValueError(f"No agent found with ID {agent_id} in run {run_id}")
                
            # Get balance changes
            balance_sql = self._read_sql_file("queries/get_agent_balance_history.sql")
            balance_history = self.con.execute(balance_sql, [agent_id, run_id]).fetchall()
            
            # Get trust relationships
            trust_sql = self._read_sql_file("queries/get_agent_trust_history.sql")
            trust_history = self.con.execute(trust_sql, [agent_id, run_id]).fetchall()
            
            return {
                "profile": dict(zip([
                    "agent_id", "personality", "economic_status", "trust_threshold",
                    "max_connections", "activity_level", "risk_tolerance"
                ], profile)),
                "balance_history": balance_history,
                "trust_history": trust_history
            }
            
        except Exception as e:
            logger.error(f"Failed to get agent history: {e}")
            raise

    def get_network_graph(self, run_id: Optional[int] = None) -> Tuple[List, List]:
        """
        Get the trust network graph data for visualization.
        
        Args:
            run_id: Optional specific simulation run ID (defaults to current run)
            
        Returns:
            Tuple of (nodes, edges) where nodes are agents and edges are trust relationships
        """
        try:
            run_id = run_id or self.current_run_id
            if not run_id:
                raise ValueError("No simulation run specified or currently active")
                
            # Get all nodes (agents)
            node_sql = self._read_sql_file("queries/get_network_nodes.sql")
            nodes = self.con.execute(node_sql, [run_id]).fetchall()
            
            # Get all edges (trust relationships)
            edge_sql = self._read_sql_file("queries/get_network_edges.sql")
            edges = self.con.execute(edge_sql, [run_id]).fetchall()
            
            return nodes, edges
            
        except Exception as e:
            logger.error(f"Failed to get network graph: {e}")
            raise


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