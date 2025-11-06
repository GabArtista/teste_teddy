# ADR 0001: OCR Technology Selection

## Status
Accepted – 2025-11-05

## Context
The résumé ingestion workflow requires high-quality OCR for mixed PDF/image inputs, multi-language support, and reasonable performance within Docker containers. Candidates included Tesseract, EasyOCR, and PaddleOCR.

## Decision
Adopt **PaddleOCR** as the primary OCR engine, accessed through the Python package and wrapped in an adapter so that alternatives can be swapped with minimal changes. PDF pages are rendered via PyMuPDF before executing the OCR pipeline.

## Rationale
- Superior accuracy on complex layouts and noisy scans compared to Tesseract/EasyOCR in recent benchmarks.
- GPU acceleration support and model zoo for future fine-tuning.
- Active community maintenance with multilingual models aligned to market expectations.
- Compatible with containerized deployments; dependencies manageable via slim Python images.

## Consequences
- Need to bundle PaddleOCR model weights or download on first run (configured via environment variable).
- Larger image processing footprint than Tesseract; monitor resource usage in constrained environments.
- Adapter interface must expose hooks for future switch to AWS Textract or Google Vision if required.

