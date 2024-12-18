SELECT 
    trustee_address,
    COUNT(DISTINCT truster_address) as trust_count
    --AVG(trust_limit) as avg_trust_limit
FROM active_trusts
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10;