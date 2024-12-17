INSERT INTO balance_changes (
    account_address,
    token_id,
    simulation_run_id,
    block_number,
    timestamp,
    previous_balance,
    new_balance,
    change_amount,
    transaction_hash,
    event_type
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);