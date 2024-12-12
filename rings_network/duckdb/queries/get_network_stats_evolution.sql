SELECT 
    timestamp,
    total_humans,
    total_active_trusts,
    total_supply,
    average_balance,
    trust_density
FROM network_stats
WHERE simulation_run_id = ?
ORDER BY timestamp;