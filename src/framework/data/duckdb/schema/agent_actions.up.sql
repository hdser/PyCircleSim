CREATE TABLE IF NOT EXISTS agent_action_history (
    agent_id VARCHAR NOT NULL,
    action_type VARCHAR NOT NULL,            -- Type of action performed
    block_number INTEGER NOT NULL,           -- Block when action was performed
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(agent_id) REFERENCES agents(agent_id)
);