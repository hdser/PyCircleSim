CREATE VIEW IF NOT EXISTS current_balances AS
SELECT 
    account_address,
    token_id,
    new_balance as current_balance,
    max(block_number) as last_updated_block,
    max(timestamp) as last_updated_time
FROM balance_changes
GROUP BY account_address, token_id, new_balance;