SELECT 
    date_trunc('hour', timestamp) as hour,
    COUNT(*) as total_transfers,
    SUM(ABS(change_amount)) as total_volume,
    COUNT(DISTINCT account_address) as active_accounts
FROM balance_changes
WHERE event_type = 'TRANSFER'
GROUP BY 1
ORDER BY 1;