CREATE TABLE IF NOT EXISTS network_stats (
    timestamp TIMESTAMP,                   -- When snapshot was taken
    block_number BIGINT,                   -- Block number of snapshot
    total_humans INT,                      -- Number of registered humans
    total_active_trusts INT,               -- Count of valid trust relationships
    total_supply DOUBLE,                   -- Total tokens in circulation
    average_balance DOUBLE,                -- Average tokens per account
    trust_density DOUBLE,                  -- Measure of network connectivity
    PRIMARY KEY (timestamp)                -- One snapshot per timestamp
);