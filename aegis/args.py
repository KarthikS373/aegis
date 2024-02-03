from pydantic import BaseModel, Field
from typing import Optional


class CompileArguments(BaseModel):
    """Compile arguments for the compiler"""
    path: str = Field(
        names=("-p", "--path"),
        description="Path to the contract file"
    )

    output: Optional[str] = Field(
        names=("-o", "--output"),
        description="Output directory"
    )

    optimize: Optional[bool] = Field(
        names=("-O", "--optimize"),
        description="Enable optimization",
        default=False
    )


class ScanArguments (CompileArguments):
    """Scan arguments for the scanner"""
    pass


class GenerateReportArguments (BaseModel):
    """Generate report arguments for the report generator"""
    path: str = Field(
        names=("-p", "--path"),
        description="Path to the contract file"
    )

    output: Optional[str] = Field(
        names=("-pp", "--pdf-path"),
        description="Path to the PDF report",
        default="report.pdf"
    )
