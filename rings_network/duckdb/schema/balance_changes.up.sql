CREATE TABLE IF NOT EXISTS balance_changes (
    account_address VARCHAR NOT NULL,        -- Address whose balance changed
    token_id VARCHAR NOT NULL,               -- ID of token (derived from address)
    simulation_run_id INTEGER NOT NULL,      -- Reference to simulation run
    block_number BIGINT NOT NULL,            -- Block where change occurred
    timestamp TIMESTAMP NOT NULL,            -- When the change happened
    previous_balance VARCHAR NOT NULL,        -- Balance before change as decimal string
    new_balance VARCHAR NOT NULL,            -- Balance after change as decimal string
    change_amount VARCHAR NOT NULL,          -- Amount of change as decimal string
    transaction_hash VARCHAR NOT NULL,       -- Transaction causing the change
    event_type VARCHAR NOT NULL,             -- Type of event (MINT/TRANSFER/BURN)
    FOREIGN KEY(simulation_run_id) REFERENCES simulation_runs(run_id)
);