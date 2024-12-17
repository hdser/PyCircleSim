SELECT 
    a.agent_id,
    a.personality,
    a.economic_status,
    a.trust_threshold,
    a.max_connections,
    a.activity_level,
    a.risk_tolerance
FROM agents a
WHERE a.agent_id = ? AND a.simulation_run_id = ?;