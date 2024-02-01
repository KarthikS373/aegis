from pydantic import BaseModel
from typing import Optional


class CompileArguments(BaseModel):
    """Compile arguments for the compiler"""
    path: str
    output: Optional[str]
    optimize: Optional[bool] = False
