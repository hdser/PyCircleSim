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
balance_sum AS (
    -- Handle large numbers by keeping them as strings
    SELECT SUM(CAST(current_balance AS DOUBLE)) as total_balance
    FROM current_balances
),
balance_avg AS (
    -- Calculate average while keeping precision
    SELECT AVG(CAST(current_balance AS DOUBLE)) as avg_balance
    FROM current_balances
)
SELECT 
    c.total_humans,
    t.total_active_trusts,
    COALESCE(t.trust_density, 0) as trust_density,
    CAST(COALESCE(s.total_balance, 0) AS VARCHAR) as total_supply,
    CAST(COALESCE(a.avg_balance, 0) AS VARCHAR) as average_balance
FROM current_stats c
CROSS JOIN trust_stats t
CROSS JOIN balance_sum s
CROSS JOIN balance_avg a;

