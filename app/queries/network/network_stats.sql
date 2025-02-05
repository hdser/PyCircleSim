SELECT 
    simulation_run_id,
    timestamp,
    total_humans,
    total_active_trusts,
    trust_density
FROM network_stats 
ORDER BY timestamp DESC
LIMIT 100