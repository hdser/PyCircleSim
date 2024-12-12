SELECT 
    bc.timestamp,
    bc.previous_balance,
    bc.new_balance,
    bc.change_amount,
    bc.event_type
FROM balance_changes bc
JOIN agent_addresses aa ON bc.account_address = aa.address
WHERE aa.agent_id = ? 
AND bc.simulation_run_id = ?
ORDER BY bc.timestamp;