import psycopg2
from backend.app.db.session import get_connection

UPSERT_INTO_FORMULAS = """
INSERT INTO formulas (raw_input, normalized_input, hash, notation)
VALUES (%s, %s, %s, %s)
ON CONFLICT (hash) DO UPDATE
SET hash = EXCLUDED.hash
RETURNING id;
"""
GET_EXISTING_ID = "SELECT id FROM formulas WHERE hash = %s;"
INSERT_INTO_RUNS = "INSERT INTO runs (formula_id,status,timeout_ms,mode) VALUES (%s,%s,%s,%s) RETURNING id;"
CREATED = "CREATED"

def get_or_create_formula(raw_input:str, normalized_input:str, hash_value:str, notation:str) -> int: 
#If formula already exists then return the id, else create a new id. 
#Will be used for not recomputing previously computed results.
        conn = get_connection()
        try:
                with conn:
                    with conn.cursor() as cursor:
                                cursor.execute(UPSERT_INTO_FORMULAS,(raw_input,normalized_input,hash_value,notation))
                                formula_id = cursor.fetchone()[0]
                                
                                return formula_id
                  
        finally:
            conn.close()
            
# Creates a run for a specified formula.             
def create_run(formula_id:int,mode:str):
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(INSERT_INTO_RUNS,(formula_id,CREATED,5000,mode))
                run_id = cursor.fetchone()[0]
                
                return run_id
    finally:
        conn.close()