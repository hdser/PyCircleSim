INSERT INTO agents (
    agent_id, 
    simulation_run_id, 
    name, 
    description, 
    total_accounts, 
    max_daily_actions, 
    risk_tolerance, 
    preferred_contracts
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
