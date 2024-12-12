SELECT 
    aa1.agent_id as source_agent,
    aa2.agent_id as target_agent,
    t.trust_limit,
    t.expiry_time
FROM trusts t
JOIN agent_addresses aa1 ON t.truster_address = aa1.address
JOIN agent_addresses aa2 ON t.trustee_address = aa2.address
WHERE t.simulation_run_id = ?
AND t.expiry_time > CURRENT_TIMESTAMP;