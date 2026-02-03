import psycopg2
import os

def check_db_connectivity():
    try:
        conn = get_connection()
        conn.close()
    except Exception as error:
        raise RuntimeError(f"Database connection failed: {error}")
    
def get_connection():
    return psycopg2.connect(
            host = os.environ.get("DB_HOST"),
            port = os.environ.get("DB_PORT"),
            dbname = os.environ.get("DB_NAME"),
            user = os.environ.get("DB_USER"),
            password = os.environ.get("DB_PASSWORD"),
            connect_timeout =5,
        )