from typing import Optional, Dict

from pydantic import BaseModel, Field, field_validator

MAX_FORMULA_LENGTH = 300_000
MAX_TOKENS = 85_000
class SolveResponseCached(BaseModel):
    mode : str = Field(
        ...,
        description="Operation mode: CNF or RPN",
        json_schema_extra={"example": "SATSOLVER"},
        min_length=3,
        max_length=3,
    )
    notation : str = Field(
        ...,
        description="Notation in RPN(maybe add INFIX LATER)",
        json_schema_extra={"notation": "RPN"},
        min_length=3,
    )
    
    @field_validator('mode')
    @classmethod
    def validate_mode(cls,mode):
        if mode.upper() not in {"CNF","RPN"}:
            raise ValueError('Mode must be CNF or RPN')
        return mode.upper()
    @field_validator('notation')
    @classmethod
    def validate_notation(cls,notation):
        if notation != 'RPN':
            raise ValueError('Notation needs to be in RPN.')
        return notation
    
class SolveResponseCached(BaseModel):
    msg: str
    formula: str
    result: str
    return_code: int
    cached: bool

class SolveResponseFresh(BaseModel):
    msg: str
    formula : str
    result : str
    assignment : Optional[Dict[str,bool]]
    return_code : int 
    runtime : float
    cached : bool

class HistoryEntry(BaseModel):
    id: int
    formula: str
    formula_hash: str
    result: str
    return_code: int
    runtime: float

class HistoryResponse(BaseModel):
    entries: list[HistoryEntry]