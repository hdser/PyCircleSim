INSERT INTO events (
    simulation_run_id, event_name, block_number, block_timestamp,
    transaction_hash, tx_from, tx_to, tx_index, log_index,
    contract_address, topics, event_data, raw_data,
    indexed_values, decoded_values
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);