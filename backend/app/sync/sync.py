import logging
import re
import subprocess
import time
from typing import Tuple, Union

from fastapi import APIRouter, Body, HTTPException, status

from backend.app.utils.formula import normalize_and_hash
from backend.app.sync.syncdb import (
    get_result_by_hash,
    insert_result,
    get_results,
)

from backend.app.schemas.job import (
    SolveResponseCached,
    SolveResponseFresh,
    HistoryEntry,
    HistoryResponse,    
)

logger = logging.getLogger(__name__)

# Configuration
SOLVER_TIMEOUT = 5
SOLVER_PATH = "bin/satsolver_opt"
# Return codes from C solver
RETURN_CODE_SAT = 10
RETURN_CODE_UNSAT = 20
RETURN_CODE_PARSE_ERROR = 30

sync_router = APIRouter(prefix="/sync", tags=["sync-solver"])


@sync_router.post("/solve_sync", response_model=Union[SolveResponseFresh,SolveResponseCached])
def run_sync_solver(formula: str = Body(..., media_type="text/plain")):
    try:
        normalized_rpn, normalized_hash = normalize_and_hash(formula, "RPN")
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
        
    # Check cache
    db_result = get_result_by_hash(normalized_hash)
    
    if db_result is not None and db_result["rc"] in {RETURN_CODE_SAT, RETURN_CODE_UNSAT}:
        result, assignment = parse_solver_output(db_result["result"])
        return SolveResponseCached(
            msg="Formula already solved (cached).",
            formula=normalized_rpn,
            result=result,
            assignment=assignment,
            return_code=db_result["rc"],
            cached=True,
            runtime= db_result["rt"]
        )
    
    # Solve formula
    process, runtime = run_solver(normalized_rpn)
    rc = process.returncode
    stdout = process.stdout or ""
    stderr = process.stderr or ""
    
    # Parsing errors
    if rc == RETURN_CODE_PARSE_ERROR:
        insert_result(normalized_rpn, normalized_hash, stderr, rc, runtime)
        raise HTTPException(
            status_code=400,
            detail=stderr or "Formula Parsing Failed"
        )
    
    # SAT/UNSAT
    if rc in {RETURN_CODE_SAT, RETURN_CODE_UNSAT}:
        insert_result(normalized_rpn, normalized_hash, stdout, rc, runtime)
        result, assignment = parse_solver_output(stdout)
        return SolveResponseFresh(
            msg="Formula solved successfully.",
            formula=normalized_rpn,
            result=result,
            assignment=assignment,
            return_code=rc,
            runtime=runtime,
            cached=False,
        )
    
    # Anything else = Internal Error
    raise HTTPException(
        status_code=500,
        detail=f"Unexpected solver return code {rc}. stderr: {stderr}",
    ) 
        
    
        
def run_solver(formula: str) -> Tuple[subprocess.CompletedProcess, float]:
    """Execute the SAT solver on the formula.
    
    Args:
        formula: RPN formula string
        
    Returns:
        Tuple of (CompletedProcess, elapsed_time_seconds)
        
    Raises:
        HTTPException: On timeout or execution error
    """
    try:
        start = time.perf_counter()
        process = subprocess.run(
            [SOLVER_PATH],
            input=formula,
            capture_output=True,
            text=True,
            timeout=SOLVER_TIMEOUT,
            check=False,
        )
        end = time.perf_counter()
        runtime = end - start
        return process, runtime
    except subprocess.TimeoutExpired:
        logger.warning(f"Solver timed out after {SOLVER_TIMEOUT}s")
        raise HTTPException(
            status_code=504,
            detail="Solver execution timed out"
        )
    except FileNotFoundError:
        logger.error(f"Solver binary not found: {SOLVER_PATH}")
        raise HTTPException(
            status_code=500,
            detail="Solver binary not available"
        )
    except Exception as e:
        logger.error(f"Solver execution failed: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Solver execution failed"
        )
        
@sync_router.get("/solve_history", response_model=HistoryResponse)
def get_history():
    rows = get_results()
    entries = []
    for row in rows:
        entry = HistoryEntry(
            id=row[0],
            formula=row[1],
            formula_hash=row[2],
            result=row[3],
            return_code=row[4],
            runtime=row[5]
        )
        entries.append(entry)
    return HistoryResponse(entries=entries)

def parse_solver_output(stdout: str):
    stdout = stdout.strip()

    if stdout.startswith("UNSAT"):
        return "UNSAT", None

    assignment = {}
    for line in stdout.splitlines():
        line = line.strip()
        if "->" in line:
            var, val = line.split("->")
            assignment[var.strip()] = (val.strip() == "TRUE")

    return "SAT", assignment