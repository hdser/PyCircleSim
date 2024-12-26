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
    topics VARCHAR,           -- Store topics as plain text/hex string
    event_data VARCHAR,       -- Store event data as text
    raw_data VARCHAR,        -- Store raw data as hex string
    indexed_values VARCHAR,   -- Store as text
    decoded_values VARCHAR,   -- Store as text
  --  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(simulation_run_id) REFERENCES simulation_runs(run_id)
);