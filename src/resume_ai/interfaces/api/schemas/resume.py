"""API schemas for resume processing."""

from typing import List, Optional

from pydantic import BaseModel, Field


class ResumeSummarySchema(BaseModel):
    """Summary payload returned to clients."""

    resume_id: str = Field(..., example="01HP5D3F3PZX2N6Q4D1R0V7M8H")
    filename: str = Field(..., example="candidate.pdf")
    summary: str = Field(..., example="Senior backend engineer with 10+ years experience.")
    highlights: List[str] = Field(
        default_factory=list,
        example=["Python", "AWS", "Team leadership"],
    )


class QueryAnswerSchema(BaseModel):
    """Question answering payload."""

    request_id: str
    answer: str
    justifications: List[str]
    referenced_resumes: List[str]


class ProcessResumesResponseSchema(BaseModel):
    """Full response returned by the processing endpoint."""

    request_id: str
    summaries: List[ResumeSummarySchema]
    query_answer: Optional[QueryAnswerSchema] = None

