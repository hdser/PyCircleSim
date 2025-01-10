CREATE TABLE IF NOT EXISTS agents (
    agent_id VARCHAR PRIMARY KEY,            -- Unique UUID identifier for the agent
    simulation_run_id INTEGER NOT NULL,      -- Context of the simulation run
    
    -- Core Agent Identification
    name VARCHAR,                            -- Profile name
    description TEXT,                        -- Profile description
    
    -- Account Management
    total_accounts INTEGER NOT NULL,         -- Number of controlled addresses
    
    -- Action Tracking
    max_daily_actions INTEGER NOT NULL,      -- Maximum daily action limit
    risk_tolerance FLOAT NOT NULL,           -- Agent's risk tolerance
    
    -- Detailed Action Configuration
    FOREIGN KEY(simulation_run_id) REFERENCES simulation_runs(run_id)
);