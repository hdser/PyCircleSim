-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_events_simulation_event 
ON contract_events (simulation_run_id, event_name);

CREATE INDEX IF NOT EXISTS idx_events_block_timestamp 
ON contract_events (block_timestamp);

CREATE INDEX IF NOT EXISTS idx_events_tx_hash 
ON contract_events (transaction_hash);

-- Compound index for filtered time-based queries
CREATE INDEX IF NOT EXISTS idx_events_combo 
ON contract_events (
    simulation_run_id, 
    event_name, 
    block_timestamp
);