"""
Actual C sat solver caller.
The solver takes rpn from endpoint and calls the sat solver, it has two modes one is normal sat solving and other is sudoko    
"""

import subprocess
import time
from backend.app.core.config import settings
from typing import Tuple
import logging 

logger = logging.getLogger(__name__)


def run_solver(formula: str,  run_id: int, formula_id: int, timeout_s: int = 5) -> Tuple[subprocess.CompletedProcess, float]:
    """Execute the SAT solver on the formula.
    
    Args:
        formula: RPN formula string
        run_id: Run ID for logging
        formula_id: Formula ID for logging
        timeout_s: Timeout in seconds
        
    Returns:
        Tuple of (CompletedProcess, elapsed_time_seconds)
        
    Raises:
        subprocess.TimeoutExpired: On timeout
        FileNotFoundError: If solver binary not found
        RuntimeError: On other execution errors
    """
    path = settings.SOLVER_PATH_FAST
    try:
        start = time.perf_counter()
        logger.info(f"Subprocess is running run_id = {run_id} for formula_id:{formula_id} and formula = {formula}")
        process = subprocess.run(
            [path],
            input=formula,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
        end = time.perf_counter()
        runtime = end - start
        logger.info(f"Runtime is {runtime} for run_id{run_id} and formula_id{formula_id}.")
        return process, runtime
    except subprocess.TimeoutExpired as e:
        logger.warning(f"Solver timed out after {timeout_s}s for run_id={run_id}")
        raise
    except FileNotFoundError as e:
        logger.error(f"Solver binary not found: {path}")
        raise
    except Exception as e:
        logger.error(f"Solver execution failed: {type(e).__name__}: {e}")
        raise RuntimeError(f"Solver execution failed: {e}") from e

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