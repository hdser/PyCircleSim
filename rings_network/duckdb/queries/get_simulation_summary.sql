SELECT 
    sr.run_id,
    EXTRACT(EPOCH FROM (sr.end_timestamp - sr.start_timestamp))/60 as duration_minutes,
    COUNT(DISTINCT h.address) as total_humans,
    COUNT(DISTINCT t.truster_address || t.trustee_address) as total_trusts,
    COUNT(DISTINCT bc.account_address) as active_accounts,
    SUM(bc.new_balance) as total_supply,
    COUNT(DISTINCT t.truster_address || t.trustee_address)::float / 
        NULLIF(COUNT(DISTINCT h.address) * COUNT(DISTINCT h.address), 0) as trust_density
FROM simulation_runs sr
LEFT JOIN humans h ON h.simulation_run_id = sr.run_id
LEFT JOIN trusts t ON t.simulation_run_id = sr.run_id
LEFT JOIN balance_changes bc ON bc.simulation_run_id = sr.run_id
WHERE sr.run_id = ?
GROUP BY sr.run_id, sr.start_timestamp, sr.end_timestamp;