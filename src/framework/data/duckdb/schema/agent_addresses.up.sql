CREATE TABLE IF NOT EXISTS agent_addresses (
    agent_id VARCHAR NOT NULL,               -- Reference to agent
    address VARCHAR NOT NULL,                -- Blockchain address
    is_primary BOOLEAN NOT NULL,             -- Whether this is the primary address
    simulation_run_id INTEGER NOT NULL,      -- Reference to simulation run
    PRIMARY KEY(agent_id, address),
    FOREIGN KEY(agent_id) REFERENCES agents(agent_id),
    FOREIGN KEY(simulation_run_id) REFERENCES simulation_runs(run_id)
);