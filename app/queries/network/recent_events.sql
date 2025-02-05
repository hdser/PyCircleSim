SELECT 
    simulation_run_id,
    block_timestamp,
    event_name,
    contract_address,
    json_pretty(event_data) as event_data
FROM events 
ORDER BY block_timestamp DESC 
LIMIT 100