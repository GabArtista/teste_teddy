"""Unit tests for ProcessResumesUseCase."""

from datetime import datetime, timezone

import pytest

from resume_ai.application.dto.resume_request import ProcessResumesRequest
from resume_ai.application.use_cases.process_resumes import ProcessResumesUseCase
from resume_ai.domain.models.audit import AuditLog
from resume_ai.domain.models.resume import ResumeDocument, ResumeSummary
from resume_ai.domain.value_objects.uploaded_file import UploadedFile


class StubOCR:
    async def extract_text(self, file: UploadedFile) -> str:
        return (
            "Gabriel is a senior backend engineer with experience in Python, AWS, and mentoring.\n"
            "He led projects with FastAPI, PostgreSQL, and event-driven architectures."
        )


class StubLLM:
    async def summarize_resume(self, resume: ResumeDocument) -> ResumeSummary:
        return ResumeSummary(
            resume_id=resume.resume_id,
            summary="Senior backend engineer with strong Python and AWS background.",
            highlights=["Python", "FastAPI", "AWS"],
        )

    async def answer_query(self, query: str, resumes):
        return {
            "answer": "Gabriel matches the requirements for backend leadership roles.",
            "justifications": ["Demonstrated leadership and Python expertise"],
            "referenced_resumes": [resumes[0].resume_id],
        }


class StubVectorStore:
    def __init__(self) -> None:
        self.chunks = []

    async def upsert_chunks(self, chunks):
        self.chunks.extend(list(chunks))

    async def query(self, text: str, limit: int = 5):
        return []


class StubAuditRepository:
    def __init__(self) -> None:
        self.saved: list[AuditLog] = []

    async def save(self, log: AuditLog) -> None:
        self.saved.append(log)

    async def list_logs(self, limit: int = 50):
        return self.saved[:limit]


class StubClock:
    def now(self) -> datetime:
        return datetime(2025, 11, 6, tzinfo=timezone.utc)


@pytest.mark.asyncio()
async def test_process_resumes_use_case_generates_summaries_and_logs() -> None:
    ocr = StubOCR()
    llm = StubLLM()
    vector_store = StubVectorStore()
    audit_repo = StubAuditRepository()
    clock = StubClock()

    use_case = ProcessResumesUseCase(
        ocr_service=ocr,
        llm_service=llm,
        vector_store=vector_store,
        audit_repository=audit_repo,
        clock=clock,
    )

    request = ProcessResumesRequest(
        request_id="1234",
        user_id="fabio",
        query="Who fits a senior backend engineer role?",
        files=[
            UploadedFile(
                filename="resume.pdf",
                content_type="application/pdf",
                data=b"%PDF-1.4 dummy",
            )
        ],
    )

    response = await use_case.execute(request)

    assert response.request_id == "1234"
    assert len(response.summaries) == 1
    assert response.query_answer is not None
    assert vector_store.chunks, "Chunks should have been stored in vector store."
    assert audit_repo.saved[0].request_id == "1234"
    assert audit_repo.saved[0].result["summaries"][0]["filename"] == "resume.pdf"

