INSERT INTO network_stats (
    simulation_run_id,
    timestamp,
    block_number,
    total_humans,
    total_active_trusts,
    total_supply,
    average_balance,
    trust_density
) VALUES (?, ?, ?, ?, ?, ?, ?, ?);