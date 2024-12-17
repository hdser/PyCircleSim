INSERT INTO trusts (
    truster_address,
    trustee_address,
    simulation_run_id,
    trust_timestamp,
    trust_block,
    trust_limit,
    expiry_time
) VALUES (?, ?, ?, ?, ?, ?, ?);