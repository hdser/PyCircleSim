SELECT 
    date_trunc('day', trust_timestamp) as day,
    COUNT(*) as new_trusts,
    COUNT(DISTINCT truster_address) as unique_trusters,
    COUNT(DISTINCT trustee_address) as unique_trustees
FROM trusts
GROUP BY 1
ORDER BY 1;