SELECT 
    a.name,
    ah.action_type,
    ah.block_number,
    ah.timestamp
FROM agent_action_history ah
JOIN agents a ON a.agent_id = ah.agent_id
ORDER BY ah.timestamp DESC
LIMIT 100