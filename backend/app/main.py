import subprocess
from fastapi import FastAPI
from pydantic import BaseModel, Field
from backend.app.api import health
from backend.app.api import sync
app = FastAPI()

app.include_router(health.health_router)
app.include_router(sync.sync_router)

class Reques(BaseModel):
    formula: str = Field(
        ...,
        description= "Formula in RPN format",
        example = "A B &&"
    )

@app.post("/run")
def run(req:Reques):
    formula = req.formula
    process = subprocess.run(
    ["bin/satsolver","-v"],  # flags work normally
    input=formula,                      # this is the "pipe"
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    encoding="utf-8",
)
    return {"rc":process.returncode,"stdout": process.stdout ,"stderr":process.stderr,}


    








