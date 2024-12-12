CREATE TABLE IF NOT EXISTS network_stats (
    simulation_run_id INTEGER NOT NULL,      -- Reference to simulation run
    timestamp TIMESTAMP NOT NULL,            -- When snapshot was taken
    block_number BIGINT NOT NULL,            -- Block number of snapshot
    total_humans INTEGER NOT NULL,           -- Number of registered humans
    total_active_trusts INTEGER NOT NULL,    -- Count of valid trust relationships
    total_supply DOUBLE NOT NULL,            -- Total tokens in circulation
    average_balance DOUBLE NOT NULL,         -- Average tokens per account
    trust_density DOUBLE NOT NULL,           -- Measure of network connectivity
    PRIMARY KEY(simulation_run_id, timestamp),
    FOREIGN KEY(simulation_run_id) REFERENCES simulation_runs(run_id)
);