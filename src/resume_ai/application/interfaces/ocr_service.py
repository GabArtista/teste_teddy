"""OCR service interface."""

from typing import Protocol

from resume_ai.domain.value_objects.uploaded_file import UploadedFile


class OCRService(Protocol):
    """Contract for OCR adapters."""

    async def extract_text(self, file: UploadedFile) -> str:
        """Return extracted plain text from the supplied file."""

