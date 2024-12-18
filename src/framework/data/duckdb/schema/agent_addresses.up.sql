CREATE TABLE IF NOT EXISTS agent_addresses (
    agent_id VARCHAR NOT NULL,
    address VARCHAR NOT NULL,
    is_primary BOOLEAN NOT NULL,
    simulation_run_id INTEGER NOT NULL,
    PRIMARY KEY(agent_id, address),
    FOREIGN KEY(agent_id) REFERENCES agents(agent_id),
    FOREIGN KEY(simulation_run_id) REFERENCES simulation_runs(run_id)
);