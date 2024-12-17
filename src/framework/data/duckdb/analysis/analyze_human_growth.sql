SELECT 
    date_trunc('day', registration_timestamp) as day,
    COUNT(*) as new_registrations,
    SUM(COUNT(*)) OVER (ORDER BY date_trunc('day', registration_timestamp)) as total_humans
FROM humans
GROUP BY 1
ORDER BY 1;