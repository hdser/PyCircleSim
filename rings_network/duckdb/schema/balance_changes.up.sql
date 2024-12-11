CREATE TABLE IF NOT EXISTS balance_changes (
    account_address VARCHAR,               -- Address whose balance changed
    token_id VARCHAR,                      -- ID of token (derived from address)
    block_number BIGINT,                   -- Block where change occurred
    timestamp TIMESTAMP,                   -- When the change happened
    previous_balance DOUBLE,               -- Balance before change
    new_balance DOUBLE,                    -- Balance after change
    change_amount DOUBLE,                  -- Amount of change (can be negative)
    transaction_hash VARCHAR,              -- Transaction causing the change
    event_type VARCHAR                     -- Type of event (MINT/TRANSFER/BURN)
);