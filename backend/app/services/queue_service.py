import json
import redis
from backend.app.core.constants import JobStatus
import time 
import logging

logger = logging.getLogger(__name__)

class QueueService:
    """Handle Redis queue operations.
        Queue has three parts: queue:Pending -> queue: Processing -> (On multiple failures, moved to dead queue) queue: Dead
        queue: Pending -> for pending jobs to be picked up by worker.
        queue: Processing -> for jobs which have been picked up by a worker and are currently being processed. For this use BRPOPLPUSH queue: Pending sends to queue: Processing.
        BRPOPLPUSH, PO
        queue: Dead -> jobs which have already been tried for a maximum amount of times and still have no been completed, dealt with later."""
    
    """Job has three parts
        job:{run_id}:payload, the actual job which needs to be executed by the solver.
        job:{run_id}:status, current status of the job
        job:{run_id}:meta (HASH)
            job:{run_id}:meta inside it store attempts, created_at, last_claimed_at
        """
    """Use redis pipeline to batch commands as that reduces amount of requests, and batches commands into a single request."""
    
    PENDING_QUEUE = "q:pending"
    PROCESSING_QUEUE = "q:processing" 
    DEAD_QUEUE ="q:dead"
    
    JOB_PAYLOAD_KEY = "job:{run_id}:payload"
    JOB_META_KEY = "job:{run_id}:meta"
    JOB_STATUS_KEY = "job:{run_id}:status"    
    
    def __init__(self, redis_client :redis.Redis, * , max_attempts = 3, job_ttl = 3600):
        self.redis = redis_client
        self.max_attempts = max_attempts
        self.job_ttl = job_ttl
    
    def enqueue(self, run_id:int, payload: dict) -> None:
        """Enqueue a new job """
        now = int(time.time())
        pipe = self.redis.pipeline(transaction=True)
        pipe.set(
            self.JOB_PAYLOAD_KEY.format(run_id = run_id),
            json.dumps(payload),
            ex = self.job_ttl,
        )
        pipe.hset(
            self.JOB_META_KEY.format(run_id=run_id),
            mapping= {
                "attempts": 0,
                "created_at":now,
                "last_claimed_at": 0,
            }
        )
        pipe.set(
            self.JOB_STATUS_KEY.format(run_id=run_id),
            JobStatus.QUEUED,
            ex=self.job_ttl,
        )
        pipe.rpush(self.PENDING_QUEUE, run_id)
        pipe.execute()
    
    def claim(self, timeout_s: int = 1):
        """
        Automatically move a job from pending -> processing using BRPOPLPUSH, 
        you get run id as it is stored as <q:pending><run_id>
        then you want the payload and metadata for said run.
        """
        try:
            run_id_str = self.redis.brpoplpush(
                self.PENDING_QUEUE,
                self.PROCESSING_QUEUE,
                timeout=timeout_s,  
            )
        except redis.RedisError:
            logger.exception("Redis error during BRPOPLPUSH")
            raise
        
        if run_id_str is None: #if there is nothing in the queue return None which allows to go continue.
            return None 
        try:
            run_id = int(run_id_str)
        except (TypeError, ValueError):
            logger.error("Claimed non-integer run_id from redis: %r", run_id_str)
            try:
                self.redis.lrem(self.PROCESSING_QUEUE, 1, run_id_str)
            except redis.RedisError:
                logger.exception("Redis error while cleaning PROCESSING_QUEUE for bad run_id")
            return None
        
        try:
            payload_json = self.redis.get(self.JOB_PAYLOAD_KEY.format(run_id = run_id))
        except redis.RedisError:
            logger.exception("Redis error during GET payload for run_id = %s", run_id)
            try:
                self.redis.lrem(self.PROCESSING_QUEUE, 1, run_id_str)
            except redis.RedisError:
                logger.exception("Redis error while cleaning PROCESSING_QUEUE after GET failure")
            raise
        if payload_json is None:
            logger.error(f"Payload does not exist, check payload for run_id: {run_id}.")
            self.redis.lrem(self.PROCESSING_QUEUE, 1, run_id_str)
            return None
        
        
        try:
            payload = json.loads(payload_json)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing job JSON, JSON error: {e}")
            try:
                self.redis.lrem(self.PROCESSING_QUEUE, 1, run_id_str)
            except redis.RedisError:
                logger.exception("Redis error while cleaning PROCESSING_QUEUE for invalid payload")
            return None
        
        now = int(time.time())

        try:
            pipe = self.redis.pipeline(transaction=True)
            pipe.hset(
                self.JOB_META_KEY.format(run_id=run_id),
                mapping={
                    "last_claimed_at": now,
                },
            )
            pipe.hincrby(
                self.JOB_META_KEY.format(run_id=run_id),
                "attempts",
                1,
            )
            pipe.execute()
        except redis.RedisError:
            # Metadata failure should not break job processing
            logger.exception(
                "Failed to update metadata for run_id=%s (non-fatal)",
                run_id,
            ) 

        return run_id, payload
    def ack(self, run_id: int) -> None:
        """
        Acknowledge successful job completion. Removes job from q, cleans up and DB status update handled by worker.
        """
        run_id_str = str(run_id)
        try:
            pipe = self.redis.pipeline(transaction=True)
            pipe.lrem(self.PROCESSING_QUEUE, 1, run_id_str)
            pipe.delete(self.JOB_PAYLOAD_KEY.format(run_id=run_id))
            pipe.delete(self.JOB_META_KEY.format(run_id=run_id))
            pipe.execute()
            logger.info("Acked job run_id=%s", run_id_str)
        except redis.RedisError:
            logger.exception("Redis error during ack for run_id=%s", run_id_str)
            # Do NOT raise — worker already completed the job
    
    def fail(self, run_id: int, reason: str) -> None:
        """
        Mark job as failed at q level, removes job from processing queue and does not requeue. 
        DB, worker must handle.
        """
        run_id_str = str(run_id)
        now = int(time.time())

        try:
            pipe = self.redis.pipeline(transaction=True)
            pipe.lrem(self.PROCESSING_QUEUE, 1, run_id_str)
            pipe.hset(
                self.JOB_META_KEY.format(run_id=run_id),
                mapping={
                    "failed_at": now,
                    "last_error": reason,
                },
            )
            pipe.execute()
            logger.warning("Failed job run_id=%s reason=%s", run_id_str, reason)
        except redis.RedisError:
            logger.exception("Redis error during fail() for run_id=%s", run_id_str)
            # Do NOT raise — failure is already being handled at DB level






