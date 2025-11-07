"""Integration tests for FastAPI layer."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from resume_ai.application.dto.resume_request import (
    ProcessResumesResponse,
    QueryAnswerResponse,
    ResumeSummaryResponse,
)
from resume_ai.interfaces.api import dependencies
from resume_ai.interfaces.api.main import app


class StubUseCase:
    async def execute(self, request):
        return ProcessResumesResponse(
            request_id=request.request_id,
            summaries=[
                ResumeSummaryResponse(
                    resume_id="ABC123",
                    filename="resume.pdf",
                    summary="Experienced engineer.",
                    highlights=["Python", "Leadership"],
                )
            ],
            query_answer=QueryAnswerResponse(
                request_id=request.request_id,
                answer="Candidate matches.",
                justifications=["Has leadership experience"],
                referenced_resumes=["ABC123"],
            ),
        )


class StubAuditRepository:
    def __init__(self) -> None:
        self.items: list[Any] = []

    async def save(self, log) -> None:
        self.items.append(log)

    async def list_logs(self, limit: int = 50):
        return self.items[:limit]


@pytest.fixture()
def test_client():
    app.dependency_overrides[dependencies.provide_use_case] = lambda: StubUseCase()
    stub_audit = StubAuditRepository()
    app.dependency_overrides[dependencies.provide_audit_repository] = lambda: stub_audit
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.pop(dependencies.provide_use_case, None)
    app.dependency_overrides.pop(dependencies.provide_audit_repository, None)


def test_process_resumes_endpoint_returns_payload(test_client: TestClient) -> None:
    files = [
        ("files", ("resume.pdf", b"dummy", "application/pdf")),
    ]
    payload = {
        "request_id": "req-1",
        "user_id": "fabio",
        "query": "Who is best?",
    }

    response = test_client.post("/v1/resumes/process", data=payload, files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["request_id"] == "req-1"
    assert body["summaries"][0]["filename"] == "resume.pdf"
    assert body["query_answer"]["answer"] == "Candidate matches."


def test_list_logs_endpoint_returns_items(test_client: TestClient) -> None:
    response = test_client.get("/v1/logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
