UPDATE trusts 
SET --trust_limit = ?,
    expiry_time = ?
WHERE truster_address = ?
AND trustee_address = ?
AND simulation_run_id = ?
AND trust_timestamp = ?;