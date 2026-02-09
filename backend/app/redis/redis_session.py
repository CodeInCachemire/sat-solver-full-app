import logging 
import redis
from typing import Optional
from redis import Redis
from redis.connection import ConnectionPool
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

rpool: Optional[ConnectionPool] = None
def init_redis_pool() -> None:
    global rpool
    if rpool is None:
        logger.info(
        "Initializing Redis pool (host=%s port=%s db=%s max=%s)",
        settings.REDIS_HOST,
        settings.REDIS_PORT,
        settings.REDIS_DB,
        settings.REDIS_POOL_MAX_CONN,
    )
    
    rpool = redis.ConnectionPool(
        host = settings.REDIS_HOST,
        port = settings.REDIS_PORT,
        db = settings.REDIS_DB,
        password=getattr(settings, "REDIS_PASSWORD", None),
        max_connections=settings.REDIS_POOL_MAX_CONN,
        decode_responses = True,
        socket_connect_timeout = 3,
        socket_timeout = 15,  # Must be higher than worker poll_timeout_s (5s) to avoid race condition
        health_check_interval = 30,
        retry_on_timeout = True
    )
    
def get_redis() -> Redis: 
    if rpool is None:
        raise RuntimeError("Redis pool not initialized. Call init at startup.")
    logger.debug("Redis active.")
    return redis.Redis(connection_pool=rpool)

# Alias for compatibility with existing code
get_redis_client = get_redis

def close_redis_pool() -> None:
    """Close Redis connection pool and cleanup connections."""
    if rpool is not None:
        logger.info("Closing Redis connection pool.")
        rpool.disconnect()

def check_redis_connectivity() -> bool:
    """
    Health check for redis.
    """
    r = get_redis()
    try:
        return r.ping()
    except redis.RedisError as e:
        logger.error("Redis connectivity check failed: %s", e)
        return False