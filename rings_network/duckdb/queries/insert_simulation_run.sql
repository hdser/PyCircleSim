INSERT INTO simulation_runs (
    run_id,
    start_timestamp,
    parameters,
    description
) VALUES (
    (SELECT COALESCE(MAX(run_id), 0) + 1 FROM simulation_runs),
    ?,
    ?,
    ?
)
RETURNING run_id;