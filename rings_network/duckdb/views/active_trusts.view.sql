CREATE VIEW IF NOT EXISTS active_trusts AS
SELECT 
    truster_address,
    trustee_address,
    trust_limit,
    expiry_time
FROM trusts t1
WHERE trust_timestamp = (
    SELECT MAX(trust_timestamp)
    FROM trusts t2
    WHERE t1.truster_address = t2.truster_address
    AND t1.trustee_address = t2.trustee_address
)
AND expiry_time > CURRENT_TIMESTAMP;