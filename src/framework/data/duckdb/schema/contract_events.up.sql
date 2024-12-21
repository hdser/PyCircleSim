CREATE TABLE IF NOT EXISTS contract_events (
    id INTEGER PRIMARY KEY,
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
    topics JSON, -- Store event topics as JSON array
    event_data JSON, -- Store event data as JSON object
    raw_data VARCHAR, -- Store raw event data hex string
    indexed_values JSON, -- Store indexed parameters
    decoded_values JSON, -- Store decoded parameters
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(simulation_run_id) REFERENCES simulation_runs(run_id)
);