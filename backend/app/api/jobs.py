from fastapi import APIRouter, Depends
from backend.app.core.dependencies import get_db
from backend.app.services.database_service import DatabaseService
from backend.app.services.queue_service import QueueService
from backend.app.services.job_service import JobService
from backend.app.redis.redis_session import get_redis_client
from backend.app.schemas.job import JobSubmitResponse, JobSubmitRequest, StatusSchema, SolverResult

jobs_router = APIRouter(prefix="/jobs", tags=["async-jobs"])

def get_job_service(db: DatabaseService = Depends(get_db)) -> JobService:
    """Dependency injection for JobService."""
    redis_client = get_redis_client()
    queue_service = QueueService(redis_client)
    return JobService(db, queue_service)

@jobs_router.post("/submit", response_model=JobSubmitResponse)
def submit_job(
    request: JobSubmitRequest,
    job_service: JobService = Depends(get_job_service)
):
    """Submit a formula for async solving."""
    return job_service.submit_job(request.formula, notation=request.notation, mode=request.mode)

@jobs_router.get("/status/{run_id}", response_model=StatusSchema)
def get_status(
    run_id: int,
    job_service: JobService = Depends(get_job_service)
):
    """Get status of a submitted job."""
    return job_service.get_run_status(run_id)

@jobs_router.get("/result/{run_id}", response_model=SolverResult)
def get_result(
    run_id: int,
    job_service: JobService = Depends(get_job_service)
):
    """Get result of a completed job."""
    return job_service.get_run_result(run_id)
    