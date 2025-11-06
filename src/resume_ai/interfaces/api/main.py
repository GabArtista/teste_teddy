"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from resume_ai.infrastructure.config.settings import get_settings
from resume_ai.infrastructure.logging.logger import configure_logging, get_logger
from resume_ai.interfaces.api.routers import audit_router, resume_router

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Resume intelligence backend leveraging OCR and LLM reasoning.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("application_startup", env=settings.app_env)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


app.include_router(resume_router.router)
app.include_router(audit_router.router)
