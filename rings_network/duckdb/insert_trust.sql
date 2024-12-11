INSERT INTO trusts (
    truster_address, trustee_address, trust_timestamp,
    trust_block, trust_limit, expiry_time
) VALUES (?, ?, ?, ?, ?, ?);