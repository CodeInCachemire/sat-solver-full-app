UPSERT_INTO_FORMULAS = """
INSERT INTO formulas (normalized_input, hash, notation)
VALUES (%s, %s, %s)
ON CONFLICT (hash) 
DO UPDATE SET 
    hash = EXCLUDED.hash
RETURNING id;
"""
GET_EXISTING_ID = "SELECT id FROM formulas WHERE hash = %s;"
INSERT_INTO_RUNS = "INSERT INTO runs (formula_id,status,timeout_s,mode) VALUES (%s,%s,%s,%s) RETURNING id;"

"""
Update run status will update the status always, also started at is set when job starts and 
completed at is set only once the job finishes in success or fail.
"""
UPDATE_RUN_STATUS = """
UPDATE RUNS
SET status = %s, 
    started_at = CASE 
        WHEN %s ='PROCESSING' THEN NOW() 
        ELSE started_at 
    END,
    finished_at = CASE 
        WHEN %s IN ('COMPLETED', 'FAILED', 'TIMEOUT', 'CANCELLED') THEN NOW() 
        ELSE finished_at 
    END
WHERE id = %s;
"""

GET_FORMULA_BY_ID = """
SELECT normalized_input
FROM formulas
WHERE id = %s;
"""
GET_RUN_BY_ID = """
SELECT runs.id, runs.formula_id, runs.status, runs.created_at,
        runs.started_at, runs.finished_at , runs.timeout_s, mode
FROM runs
WHERE id = %s;
"""

INSERT_RESULT = """
INSERT INTO results (run_id, result, assignment, stdout, stderr, error_type, error_message, runtime_s)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (run_id) DO NOTHING;
"""

GET_RESULT_BY_RUN_ID = """
SELECT result, assignment, stdout, stderr, error_type, error_message, runtime_s
FROM results 
WHERE run_id = %s;
"""

GET_PENDING_RUN_BY_FORMULA = """
SELECT id, status from runs
WHERE formula_id = %s AND status IN ('CREATED', 'PROCESSING', 'QUEUED')
"""

GET_COMPLETED_RUN_BY_FORMULA = """
SELECT id, status from runs
WHERE formula_id = %s AND status = 'COMPLETED'
ORDER BY finished_at DESC
LIMIT 1;
"""

GET_RUN_STATUS_BY_ID = """
SELECT runs.id, runs.status 
FROM runs
WHERE id = %s;
"""