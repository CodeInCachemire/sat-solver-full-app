from fastapi import APIRouter, HTTPException, status
from pathlib import Path
import os
from backend.app.db import session
health_router = APIRouter()

@health_router.get("/health", status_code=status.HTTP_200_OK) #liveness check
def get_health():
    return {"status" : "ok" }

@health_router.get("/ready") #readiness check
def get_readiness():
    try:
        check_solver()
        session.check_db_connectivity()
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = str(error),
        )
    return {"status": "Solver exists, is a file and is executable and DB is connectable."}

def check_solver():
    here = Path(__file__)
    project_root = here.parent.parent.parent.parent
    sat_solver_path = project_root / "bin" / "satsolver"
    if not sat_solver_path.exists():
        raise RuntimeError("Solver does not exist")
    if not sat_solver_path.is_file():
        raise RuntimeError("Solver is not a file")
    if not os.access(sat_solver_path,os.X_OK):
        raise RuntimeError("Solver is not executable")
