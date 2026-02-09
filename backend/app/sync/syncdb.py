#for the sync version of the API
from backend.app.db.session import get_connection, release_connection

GET_RESULT_BYHASH= "SELECT result, return_code, runtime FROM sync_sat_table WHERE formula_hash = %s;"
INSERT_INTO_TABLE = """
INSERT INTO sync_sat_table (formula, formula_hash, result, return_code, runtime)
VALUES (%s,%s,%s,%s,%s)
ON CONFLICT (formula_hash)
DO UPDATE SET
    formula = EXCLUDED.formula,
    result = EXCLUDED.result,
    return_code = EXCLUDED.return_code,
    runtime = EXCLUDED.runtime;
"""
FETCH ="SELECT id, formula, formula_hash, result, return_code, runtime FROM sync_sat_table ORDER BY id ASC;"

def get_result_by_hash(formula_hash:str):
    conn = get_connection()
    
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(GET_RESULT_BYHASH,(formula_hash,))
                row = cursor.fetchone()
                if row:
                    return {"result":row[0],"rc" : row[1], "rt": row[2]}
                else:
                    return None
                
    finally:
        release_connection(conn)

def insert_result(formula:str,formula_hash:str, result:str, return_code:int, runtime:float):
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(INSERT_INTO_TABLE,(formula,formula_hash, result, return_code, runtime))
    finally:
        release_connection(conn)
        
def get_results():
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(FETCH)
                rows = cursor.fetchall()
                return rows      
    finally:
        release_connection(conn)