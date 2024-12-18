SELECT 
    t.trust_timestamp,
    t.trustee_address,
   -- t.trust_limit,
    t.expiry_time
FROM trusts t
JOIN agent_addresses aa ON t.truster_address = aa.address
WHERE aa.agent_id = ?
AND t.simulation_run_id = ?
ORDER BY t.trust_timestamp;