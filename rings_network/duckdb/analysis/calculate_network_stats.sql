WITH current_stats AS (
    SELECT 
        COUNT(DISTINCT address) as total_humans
    FROM humans
),
trust_stats AS (
    SELECT 
        COUNT(*) as total_active_trusts,
        COUNT(*) * 1.0 / NULLIF(POW((SELECT total_humans FROM current_stats), 2), 0) as trust_density
    FROM active_trusts
),
balance_stats AS (
    SELECT 
        COALESCE(SUM(current_balance), 0) as total_supply,
        COALESCE(AVG(current_balance), 0) as average_balance
    FROM current_balances
)
SELECT 
    c.total_humans,
    t.total_active_trusts,
    COALESCE(t.trust_density, 0) as trust_density,
    b.total_supply,
    b.average_balance
FROM current_stats c
CROSS JOIN trust_stats t
CROSS JOIN balance_stats b;
