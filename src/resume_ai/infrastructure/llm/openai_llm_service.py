"""LLM orchestration via OpenAI models."""

from __future__ import annotations

import json
from typing import Sequence

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from resume_ai.application.interfaces.llm_service import LLMService
from resume_ai.domain.models.resume import ResumeDocument, ResumeSummary


class OpenAILLMService(LLMService):
    """LangChain-based OpenAI integration."""

    def __init__(self, api_key: str, model: str) -> None:
        self._model = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=0.1,
            max_tokens=800,
        )
        self._parser = StrOutputParser()

        self._summary_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "You are a senior technical recruiter assistant. Summarize resumes in bullet "
                        "form capturing expertise, tech stack, experience level, and soft skills."
                        "Return JSON with keys summary and highlights (array of bullet points)."
                    ),
                ),
                (
                    "user",
                    (
                        "Resume filename: {filename}\n"
                        "Extracted text:\n{content}\n"
                        "Generate a concise summary."
                    ),
                ),
            ]
        )

        self._qa_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "You analyze resumes using the provided context chunks. Respond in JSON with "
                        "keys answer, justifications (array), and referenced_resumes (array of ids). "
                        "Ground every statement on the supplied context."
                    ),
                ),
                (
                    "user",
                    (
                        "Hiring query: {query}\n"
                        "Context:\n{context}\n"
                        "Answer the hiring manager's question."
                    ),
                ),
            ]
        )

    async def summarize_resume(self, resume: ResumeDocument) -> ResumeSummary:
        messages = self._summary_prompt.format_messages(
            filename=resume.filename, content=resume.extracted_text
        )
        raw = await self._model.ainvoke(messages)
        content = await self._parser.ainvoke(raw)
        payload = self._safe_json(content)
        return ResumeSummary(
            resume_id=resume.resume_id,
            summary=payload.get("summary", ""),
            highlights=[str(item) for item in payload.get("highlights", [])],
        )

    async def answer_query(
        self, query: str, resumes: Sequence[ResumeDocument]
    ) -> dict:
        context_lines: list[str] = []
        for resume in resumes:
            context_lines.append(f"Resume ID: {resume.resume_id} Filename: {resume.filename}")
            context_lines.append(resume.extracted_text[:2000])
        joined_context = "\n---\n".join(context_lines)
        messages = self._qa_prompt.format_messages(query=query, context=joined_context)
        raw = await self._model.ainvoke(messages)
        content = await self._parser.ainvoke(raw)
        return self._safe_json(content)

    @staticmethod
    def _safe_json(content: str) -> dict:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"summary": content, "highlights": []}

