INSERT INTO agents (
    agent_id,
    simulation_run_id,
    personality,
    economic_status,
    trust_threshold,
    max_connections,
    activity_level,
    risk_tolerance
) VALUES (?, ?, ?, ?, ?, ?, ?, ?);