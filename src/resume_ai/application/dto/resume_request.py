"""Data transfer objects for resume processing."""

from dataclasses import dataclass, field
from typing import List

from resume_ai.domain.value_objects.uploaded_file import UploadedFile


@dataclass(frozen=True)
class ProcessResumesRequest:
    """Represents the payload for the resume processing workflow."""

    request_id: str
    user_id: str
    query: str | None
    files: List[UploadedFile] = field(default_factory=list)


@dataclass(frozen=True)
class ResumeSummaryResponse:
    """Resume summary returned to the client."""

    resume_id: str
    filename: str
    summary: str
    highlights: list[str]


@dataclass(frozen=True)
class QueryAnswerResponse:
    """Query answer returned when the user submits a question."""

    request_id: str
    answer: str
    justifications: list[str]
    referenced_resumes: list[str]


@dataclass(frozen=True)
class ProcessResumesResponse:
    """Aggregate response containing either summaries or answers."""

    request_id: str
    summaries: list[ResumeSummaryResponse]
    query_answer: QueryAnswerResponse | None = None

