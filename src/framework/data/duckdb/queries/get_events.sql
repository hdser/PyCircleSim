SELECT * 
FROM events 
WHERE simulation_run_id = ?
    AND event_name = ?
    AND block_timestamp >= ?
    AND block_timestamp <= ?
ORDER BY block_timestamp DESC
LIMIT ?;