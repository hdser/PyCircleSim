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
        SUM(current_balance) as total_supply,
        AVG(current_balance) as average_balance
    FROM current_balances
)
SELECT 
    c.total_humans,
    t.total_active_trusts,
    t.trust_density,
    b.total_supply,
    b.average_balance
FROM current_stats c
CROSS JOIN trust_stats t
CROSS JOIN balance_stats b;