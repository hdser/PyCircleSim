CREATE TABLE IF NOT EXISTS states (
    simulation_run_id INTEGER NOT NULL,
    block_number BIGINT NOT NULL,
    block_timestamp TIMESTAMP NOT NULL,
    state_data JSON NOT NULL,
    PRIMARY KEY(simulation_run_id, block_number),
    FOREIGN KEY(simulation_run_id) REFERENCES simulation_runs(run_id)
);