CREATE TABLE IF NOT EXISTS agents (
    agent_id VARCHAR PRIMARY KEY,            -- Unique identifier for each agent
    simulation_run_id INTEGER NOT NULL,      -- Reference to simulation run
    personality VARCHAR NOT NULL,            -- Agent personality type
    economic_status VARCHAR NOT NULL,        -- Economic status
    trust_threshold DOUBLE NOT NULL,         -- Trust threshold parameter
    max_connections INTEGER NOT NULL,        -- Maximum allowed connections
    activity_level DOUBLE NOT NULL,          -- Activity level parameter
    risk_tolerance DOUBLE NOT NULL,          -- Risk tolerance parameter
    FOREIGN KEY(simulation_run_id) REFERENCES simulation_runs(run_id)
);