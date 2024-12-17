CREATE TABLE IF NOT EXISTS simulation_runs (
    run_id INTEGER PRIMARY KEY,              -- Unique identifier for each simulation run
    start_timestamp TIMESTAMP NOT NULL,      -- When the simulation started
    end_timestamp TIMESTAMP,                 -- When the simulation completed
    parameters JSON,                         -- JSON blob storing simulation parameters
    description TEXT                         -- Optional description of the simulation
);