"""Use case orchestrating resume ingestion and query answering."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import List
from uuid import uuid4

from langchain.text_splitter import RecursiveCharacterTextSplitter
from ulid import ULID

from resume_ai.application.dto.resume_request import (
    ProcessResumesRequest,
    ProcessResumesResponse,
    QueryAnswerResponse,
    ResumeSummaryResponse,
)
from resume_ai.application.interfaces.audit_repository import AuditRepository
from resume_ai.application.interfaces.clock import Clock
from resume_ai.application.interfaces.llm_service import LLMService
from resume_ai.application.interfaces.ocr_service import OCRService
from resume_ai.application.interfaces.vector_store import VectorStore
from resume_ai.domain.models.audit import AuditLog
from resume_ai.domain.models.resume import ResumeChunk, ResumeDocument, ResumeSummary
from resume_ai.domain.value_objects.uploaded_file import UploadedFile


class ProcessResumesUseCase:
    """Coordinates OCR, embedding, LLM reasoning, and auditing."""

    def __init__(
        self,
        ocr_service: OCRService,
        llm_service: LLMService,
        vector_store: VectorStore,
        audit_repository: AuditRepository,
        clock: Clock,
        chunk_size: int = 800,
        chunk_overlap: int = 80,
    ) -> None:
        self._ocr_service = ocr_service
        self._llm_service = llm_service
        self._vector_store = vector_store
        self._audit_repository = audit_repository
        self._clock = clock
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " "],
        )

    async def execute(self, request: ProcessResumesRequest) -> ProcessResumesResponse:
        """Run the resume intelligence workflow."""

        if not request.files:
            raise ValueError("At least one resume file is required.")

        resumes = await self._process_files(request.files)

        all_chunks = [chunk for resume in resumes for chunk in resume.chunks]
        await self._vector_store.upsert_chunks(all_chunks)

        summaries = await self._generate_summaries(resumes)

        query_answer = None
        if request.query:
            answer_payload = await self._llm_service.answer_query(request.query, resumes)
            query_answer = QueryAnswerResponse(
                request_id=request.request_id,
                answer=answer_payload.get("answer", ""),
                justifications=answer_payload.get("justifications", []),
                referenced_resumes=answer_payload.get("referenced_resumes", []),
            )

        response = ProcessResumesResponse(
            request_id=request.request_id,
            summaries=[
                ResumeSummaryResponse(
                    resume_id=summary.resume_id,
                    filename=self._find_filename(resumes, summary.resume_id),
                    summary=summary.summary,
                    highlights=summary.highlights,
                )
                for summary in summaries
            ],
            query_answer=query_answer,
        )

        await self._persist_audit_log(request, response, resumes)
        return response

    async def _process_files(self, files: Iterable[UploadedFile]) -> List[ResumeDocument]:
        resumes: list[ResumeDocument] = []
        for file in files:
            resume_id = str(ULID())
            text = await self._ocr_service.extract_text(file)
            normalized_text = text.strip()
            chunks = self._create_chunks(resume_id, normalized_text)
            resume = ResumeDocument(
                resume_id=resume_id,
                filename=file.filename,
                content_type=file.content_type,
                language="auto",
                extracted_text=normalized_text,
                chunks=chunks,
                created_at=self._clock.now(),
            )
            resumes.append(resume)
        return resumes

    def _create_chunks(self, resume_id: str, text: str) -> list[ResumeChunk]:
        if not text:
            return []
        parts = self._splitter.split_text(text)
        chunks: list[ResumeChunk] = []
        for index, chunk_text in enumerate(parts):
            chunk = ResumeChunk(
                chunk_id=str(uuid4()),
                text=chunk_text,
                metadata={"resume_id": resume_id, "position": str(index)},
            )
            chunks.append(chunk)
        return chunks

    async def _generate_summaries(self, resumes: Iterable[ResumeDocument]) -> list[ResumeSummary]:
        summaries: list[ResumeSummary] = []
        for resume in resumes:
            summary = await self._llm_service.summarize_resume(resume)
            summaries.append(summary)
        return summaries

    async def _persist_audit_log(
        self,
        request: ProcessResumesRequest,
        response: ProcessResumesResponse,
        resumes: Iterable[ResumeDocument],
    ) -> None:
        timestamp = self._clock.now()
        result_payload = {
            "summaries": [
                {
                    "resume_id": summary.resume_id,
                    "filename": summary.filename,
                    "highlights": summary.highlights,
                }
                for summary in response.summaries
            ]
        }
        if response.query_answer:
            result_payload["query_answer"] = {
                "answer": response.query_answer.answer,
                "justifications": response.query_answer.justifications,
                "referenced_resumes": response.query_answer.referenced_resumes,
            }

        log = AuditLog(
            request_id=request.request_id,
            user_id=request.user_id,
            timestamp=timestamp,
            query=request.query,
            result=result_payload,
        )
        await self._audit_repository.save(log)

    @staticmethod
    def _find_filename(resumes: Iterable[ResumeDocument], resume_id: str) -> str:
        for resume in resumes:
            if resume.resume_id == resume_id:
                return resume.filename
        return "unknown"
