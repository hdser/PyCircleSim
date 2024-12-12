SELECT 
    a.agent_id,
    a.personality,
    a.economic_status,
    COUNT(DISTINCT t.trustee_address) as outgoing_trusts,
    COUNT(DISTINCT t2.truster_address) as incoming_trusts
FROM agents a
LEFT JOIN agent_addresses aa ON a.agent_id = aa.agent_id
LEFT JOIN trusts t ON aa.address = t.truster_address
LEFT JOIN trusts t2 ON aa.address = t2.trustee_address
WHERE a.simulation_run_id = ?
GROUP BY a.agent_id, a.personality, a.economic_status;