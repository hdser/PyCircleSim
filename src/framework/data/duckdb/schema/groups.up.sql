CREATE TABLE IF NOT EXISTS groups (
    address VARCHAR NOT NULL,                -- Group address
    creator VARCHAR NOT NULL,               -- Creator's address
    simulation_run_id INTEGER NOT NULL,     -- Reference to simulation run
    registration_timestamp TIMESTAMP NOT NULL, -- When group was registered
    registration_block BIGINT NOT NULL,     -- Block number of registration
    name VARCHAR NOT NULL,                  -- Group name
    symbol VARCHAR NOT NULL,                -- Group symbol
    mint_policy VARCHAR NOT NULL,           -- Mint policy contract address
    PRIMARY KEY(address, simulation_run_id),
    FOREIGN KEY(simulation_run_id) REFERENCES simulation_runs(run_id)
);