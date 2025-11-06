"""Dependency providers for FastAPI routes."""

from functools import lru_cache

from resume_ai.application.interfaces.clock import SystemClock
from resume_ai.application.use_cases.process_resumes import ProcessResumesUseCase
from resume_ai.infrastructure.config.settings import AppSettings, get_settings
from resume_ai.infrastructure.llm.openai_embedding_service import OpenAIEmbeddingService
from resume_ai.infrastructure.llm.openai_llm_service import OpenAILLMService
from resume_ai.infrastructure.ocr.paddle_ocr_service import PaddleOCRService
from resume_ai.infrastructure.persistence.mongo_audit_repository import MongoAuditRepository
from resume_ai.infrastructure.vectorstore.qdrant_store import QdrantVectorStore


@lru_cache(maxsize=1)
def provide_settings() -> AppSettings:
    """Return cached settings."""

    return get_settings()


@lru_cache(maxsize=1)
def provide_ocr_service() -> PaddleOCRService:
    settings = provide_settings()
    return PaddleOCRService(
        language=settings.ocr_language,
        use_gpu=settings.ocr_use_gpu,
        model_dir=settings.ocr_model_dir,
    )


@lru_cache(maxsize=1)
def provide_embedding_service() -> OpenAIEmbeddingService:
    settings = provide_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required.")
    return OpenAIEmbeddingService(
        api_key=settings.openai_api_key, model=settings.openai_embedding_model
    )


@lru_cache(maxsize=1)
def provide_vector_store() -> QdrantVectorStore:
    settings = provide_settings()
    return QdrantVectorStore(
        url=str(settings.qdrant_url),
        collection_name=settings.vector_collection,
        vector_size=settings.vector_size,
        similarity=settings.vector_similarity,
        embedding_service=provide_embedding_service(),
    )


@lru_cache(maxsize=1)
def provide_llm_service() -> OpenAILLMService:
    settings = provide_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required.")
    return OpenAILLMService(api_key=settings.openai_api_key, model=settings.openai_model)


@lru_cache(maxsize=1)
def provide_audit_repository() -> MongoAuditRepository:
    settings = provide_settings()
    return MongoAuditRepository(mongo_uri=settings.mongodb_uri)


@lru_cache(maxsize=1)
def provide_clock() -> SystemClock:
    return SystemClock()


def provide_use_case() -> ProcessResumesUseCase:
    """Return fully wired use case."""

    return ProcessResumesUseCase(
        ocr_service=provide_ocr_service(),
        llm_service=provide_llm_service(),
        vector_store=provide_vector_store(),
        audit_repository=provide_audit_repository(),
        clock=provide_clock(),
    )

