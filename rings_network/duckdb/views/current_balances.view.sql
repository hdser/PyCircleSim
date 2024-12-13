CREATE OR REPLACE VIEW current_balances AS
SELECT 
    bc.account_address,
    bc.token_id,
    bc.new_balance as current_balance,
    bc.simulation_run_id,
    MAX(bc.block_number) as last_updated_block,
    MAX(bc.timestamp) as last_updated_time
FROM balance_changes bc
GROUP BY 
    bc.simulation_run_id,
    bc.account_address, 
    bc.token_id, 
    bc.new_balance;