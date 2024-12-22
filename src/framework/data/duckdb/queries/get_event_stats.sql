SELECT 
    event_name,
    COUNT(*) as count,
    MIN(block_timestamp) as first_seen,
    MAX(block_timestamp) as last_seen,
    COUNT(DISTINCT transaction_hash) as unique_transactions
FROM events
WHERE simulation_run_id = ?
GROUP BY event_name
ORDER BY count DESC;