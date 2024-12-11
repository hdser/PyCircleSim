CREATE TABLE IF NOT EXISTS humans (
    address VARCHAR PRIMARY KEY,            -- Blockchain address of the human
    registration_timestamp TIMESTAMP,       -- When they registered
    registration_block BIGINT,             -- Block number of registration
    inviter_address VARCHAR,               -- Who invited them (if anyone)
    welcome_bonus_amount DOUBLE            -- Initial tokens received
);