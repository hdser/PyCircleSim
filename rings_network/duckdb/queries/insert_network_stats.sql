INSERT INTO network_stats (
    timestamp, block_number, total_humans, total_active_trusts,
    total_supply, average_balance, trust_density
) VALUES (?, ?, ?, ?, ?, ?, ?);