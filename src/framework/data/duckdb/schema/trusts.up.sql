CREATE TABLE IF NOT EXISTS trusts (
    truster_address VARCHAR NOT NULL,        -- Address giving trust
    trustee_address VARCHAR NOT NULL,        -- Address receiving trust
    simulation_run_id INTEGER NOT NULL,      -- Reference to simulation run
    trust_timestamp TIMESTAMP NOT NULL,      -- When trust was established
    trust_block BIGINT NOT NULL,             -- Block number of trust creation
    --trust_limit VARCHAR NOT NULL,            -- Maximum trust amount as decimal string
    expiry_time TIMESTAMP NOT NULL,          -- When trust relationship expires
    PRIMARY KEY(truster_address, trustee_address, trust_timestamp, simulation_run_id),
    FOREIGN KEY(simulation_run_id) REFERENCES simulation_runs(run_id)
);