from psycopg2 import OperationalError
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extensions import connection as PGConnection
from backend.app.core.config import settings
import os
import logging

logger = logging.getLogger(__name__)
pool : ThreadedConnectionPool | None = None
def init_db_pool() -> None:
    global pool
    if pool is None:
        logger.info(
            "Initializing DB pool with host(%s), port(%s), dbname (%s), user(%s), min(%s),max(%s).",
            settings.DB_HOST,
            settings.DB_PORT,
            settings.DB_NAME,
            settings.DB_USER,
            settings.DB_POOL_MIN,
            settings.DB_POOL_MAX,
        )
        pool = ThreadedConnectionPool(
            minconn=settings.DB_POOL_MIN,
            maxconn=settings.DB_POOL_MAX,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            connect_timeout=5,            
        )
    
def get_connection():
    if pool is None:
        raise RuntimeError("DB pool not initialized.")
    logger.debug("Borrowing DB connection from pool.")
    return pool.getconn()

def release_connection(conn) -> None:
    if pool is not None:
        logger.debug("Returning connection to the pool.")
        pool.putconn(conn)

def close_pool() -> None:
    if pool is not None:
        logger.info("Closing DB connection pool.")
        pool.closeall()
        
def check_db_connectivity() -> bool: 
    """
    Check db connectivity.
    """
    if pool is None:
        logger.error("DB pool not initialized.")
        return False
    conn = None
    try:
        conn: PGConnection = pool.getconn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        return True
    except OperationalError as error:
        logger.error("Database Connectivity check failed: %s", error)
        raise error
    finally:
        if conn is not None:
            pool.putconn(conn)