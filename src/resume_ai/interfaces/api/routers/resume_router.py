"""Resume processing routes."""

from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from resume_ai.application.dto.resume_request import ProcessResumesRequest
from resume_ai.application.use_cases.process_resumes import ProcessResumesUseCase
from resume_ai.domain.value_objects.uploaded_file import UploadedFile
from resume_ai.interfaces.api.dependencies import provide_use_case
from resume_ai.interfaces.api.schemas.resume import ProcessResumesResponseSchema

router = APIRouter(prefix="/v1/resumes", tags=["resumes"])


@router.post(
    "/process",
    response_model=ProcessResumesResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Process resumes and optionally answer a query",
)
async def process_resumes(
    request_id: str = Form(...),
    user_id: str = Form(...),
    query: str | None = Form(default=None),
    files: List[UploadFile] = File(...),
    use_case: ProcessResumesUseCase = Depends(provide_use_case),
) -> ProcessResumesResponseSchema:
    """Ingest resumes, run OCR, and optionally answer a hiring query."""

    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files provided.")

    uploads = [
        UploadedFile(
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            data=await file.read(),
        )
        for file in files
    ]
    response = await use_case.execute(
        ProcessResumesRequest(
            request_id=request_id,
            user_id=user_id,
            query=query,
            files=uploads,
        )
    )
    return ProcessResumesResponseSchema(
        request_id=response.request_id,
        summaries=[
            {
                "resume_id": summary.resume_id,
                "filename": summary.filename,
                "summary": summary.summary,
                "highlights": summary.highlights,
            }
            for summary in response.summaries
        ],
        query_answer=(
            {
                "request_id": response.query_answer.request_id,
                "answer": response.query_answer.answer,
                "justifications": response.query_answer.justifications,
                "referenced_resumes": response.query_answer.referenced_resumes,
            }
            if response.query_answer
            else None
        ),
    )
