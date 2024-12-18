INSERT INTO agent_action_configs (
    agent_id, 
    action_type, 
    probability, 
    cooldown_blocks, 
    gas_limit, 
    min_balance,
    max_value, 
    constraints
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)