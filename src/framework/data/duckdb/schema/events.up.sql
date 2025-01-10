CREATE TABLE IF NOT EXISTS events (
  --  id INTEGER PRIMARY KEY,
    simulation_run_id INTEGER NOT NULL,
    event_name VARCHAR NOT NULL,
    block_number BIGINT NOT NULL,
    block_timestamp TIMESTAMP NOT NULL,
    transaction_hash VARCHAR NOT NULL,
    tx_from VARCHAR,
    tx_to VARCHAR,
    tx_index INTEGER,
    log_index INTEGER,
    contract_address VARCHAR NOT NULL,
    topic0 VARCHAR NOT NULL,           -- Store topic0 as plain text/hex string
    event_data JSON,       -- Store event data as text
    
    FOREIGN KEY(simulation_run_id) REFERENCES simulation_runs(run_id)
);