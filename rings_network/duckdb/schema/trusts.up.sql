CREATE TABLE IF NOT EXISTS trusts (
    truster_address VARCHAR,               -- Address giving trust
    trustee_address VARCHAR,               -- Address receiving trust
    trust_timestamp TIMESTAMP,             -- When trust was established
    trust_block BIGINT,                    -- Block number of trust creation
    trust_limit DOUBLE,                    -- Maximum trust amount (in tokens)
    expiry_time TIMESTAMP,                 -- When trust relationship expires
    PRIMARY KEY (truster_address, trustee_address, trust_timestamp)
);