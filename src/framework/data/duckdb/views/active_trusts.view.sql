CREATE VIEW IF NOT EXISTS active_trusts AS
SELECT 
    t.simulation_run_id,
    t.truster_address,
    t.trustee_address,
    --t.trust_limit,
    t.expiry_time
FROM trusts t
INNER JOIN (
    SELECT 
        simulation_run_id,
        truster_address,
        trustee_address,
        MAX(trust_timestamp) as latest_trust
    FROM trusts 
    GROUP BY 
        simulation_run_id,
        truster_address,
        trustee_address
) latest ON 
    t.simulation_run_id = latest.simulation_run_id AND
    t.truster_address = latest.truster_address AND 
    t.trustee_address = latest.trustee_address AND
    t.trust_timestamp = latest.latest_trust
WHERE t.expiry_time > CURRENT_TIMESTAMP;