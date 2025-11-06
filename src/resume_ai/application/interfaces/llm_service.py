"""LLM orchestration interface."""

from typing import Protocol, Sequence

from resume_ai.domain.models.resume import ResumeDocument, ResumeSummary


class LLMService(Protocol):
    """Contract for LLM-based reasoning."""

    async def summarize_resume(self, resume: ResumeDocument) -> ResumeSummary:
        """Generate a structured summary for a resume."""

    async def answer_query(
        self, query: str, resumes: Sequence[ResumeDocument]
    ) -> dict:
        """Return an answer with justifications for the provided query."""

