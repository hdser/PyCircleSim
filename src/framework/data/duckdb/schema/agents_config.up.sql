CREATE TABLE IF NOT EXISTS agent_action_configs (
    agent_id VARCHAR NOT NULL,
    action_type VARCHAR NOT NULL,            -- Enum of action types
    
    probability FLOAT NOT NULL,              -- Probability of performing this action
    cooldown_blocks INTEGER NOT NULL,        -- Cooldown between similar actions
    gas_limit INTEGER NOT NULL,              -- Maximum gas limit for the action
    min_balance FLOAT NOT NULL,              -- Minimum balance required
    max_value FLOAT NOT NULL,                -- Maximum value for the action
    
    constraints JSON,                       -- Flexible constraints storage
    
    PRIMARY KEY(agent_id, action_type),
    FOREIGN KEY(agent_id) REFERENCES agents(agent_id)
);