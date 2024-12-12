CREATE TABLE IF NOT EXISTS humans (
    address VARCHAR NOT NULL,                -- Blockchain address of the human
    simulation_run_id INTEGER NOT NULL,      -- Reference to simulation run
    registration_timestamp TIMESTAMP NOT NULL,-- When they registered
    registration_block BIGINT NOT NULL,      -- Block number of registration
    inviter_address VARCHAR,                 -- Who invited them (if anyone)
    welcome_bonus DOUBLE,                    -- Initial tokens received
    PRIMARY KEY(address, simulation_run_id),
    FOREIGN KEY(simulation_run_id) REFERENCES simulation_runs(run_id)
);