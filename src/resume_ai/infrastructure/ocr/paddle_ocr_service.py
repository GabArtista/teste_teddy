"""PaddleOCR adapter."""

from __future__ import annotations

import asyncio
from io import BytesIO
from typing import Iterable

import numpy as np

from resume_ai.domain.value_objects.uploaded_file import UploadedFile
from resume_ai.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class PaddleOCRService:
    """Performs OCR using PaddleOCR."""

    def __init__(self, language: str = "en", use_gpu: bool = False, model_dir: str | None = None):
        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise RuntimeError(
                "PaddleOCR is not installed. Ensure paddleocr dependency is available."
            ) from exc

        self._ocr = PaddleOCR(
            use_angle_cls=True,
            lang=language,
            use_gpu=use_gpu,
            det_db_box_thresh=0.3,
            det_db_unclip_ratio=1.6,
            show_log=False,
            ocr_version="PP-OCRv4",
            rec=True,
            rec_char_type="en",
            rec_model_dir=model_dir,
        )

    async def extract_text(self, file: UploadedFile) -> str:
        """Extract text asynchronously."""

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._extract_sync, file)

    def _extract_sync(self, file: UploadedFile) -> str:
        images = list(self._load_images(file))
        results: list[str] = []
        for image in images:
            ocr_result = self._ocr.ocr(image, cls=True)
            if not ocr_result:
                continue
            for line in ocr_result:
                if not line:
                    continue
                _, content = line
                text = content[0]
                results.append(text)
        combined = "\n".join(results)
        logger.info("extracted_text", filename=file.filename, length=len(combined))
        return combined

    def _load_images(self, file: UploadedFile) -> Iterable[np.ndarray]:
        if file.content_type == "application/pdf" or file.extension() == "pdf":
            yield from self._load_pdf(file.data)
        else:
            yield self._load_image(file.data)

    @staticmethod
    def _load_pdf(data: bytes) -> Iterable[np.ndarray]:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=data, filetype="pdf")
        for page in doc:
            pix = page.get_pixmap(alpha=False)
            arr = np.frombuffer(pix.samples, dtype=np.uint8)
            image = arr.reshape(pix.height, pix.width, pix.n)
            yield image

    @staticmethod
    def _load_image(data: bytes) -> np.ndarray:
        from PIL import Image

        image = Image.open(BytesIO(data))
        rgb_image = image.convert("RGB")
        return np.array(rgb_image)

