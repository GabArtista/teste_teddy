# Resume Intelligence Platform

Backend service that ingests résumés, runs OCR, builds retrieval-augmented context, and answers hiring queries with explainable justifications. Built with Clean Architecture, Domain-Driven Design, and the universal standards provided in the assignment brief.

## 1. Capabilities at a Glance
- Process multiple PDFs or images per request.
- Extract text with PaddleOCR and generate structured summaries.
- Answer recruiting questions using OpenAI GPT-4.1 + vector retrieval.
- Persist audit logs (`request_id`, `user_id`, `timestamp`, `query`, `result`) in MongoDB; no raw documents stored.
- Provide full OpenAPI/Swagger docs, ADRs, diagrams, and Postman collection (`docs/endpoint-json.json`).

## 2. Prerequisites
- Python 3.10+
- Docker + Docker Compose
- OpenAI API key (set in `.env`)
- Internet access for dependency/model downloads

## 3. Installation Options
Choose one path; both produce the same environment.

### Option A – Poetry (recommended)
```bash
curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
poetry install --no-root
```

### Option B – Virtualenv + pip
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## 4. Configuration
```bash
cp .env.example .env
# edit .env to include OPENAI_API_KEY and other secrets
```

## 5. Run the Stack
```bash
docker compose up --build
```

Services exposed:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- MongoDB: mongodb://localhost:27017 (via container)
- Qdrant: http://localhost:6333

## 6. Common Commands
```bash
make run      # FastAPI with autoreload (requires Poetry)
make lint     # Ruff + mypy
make test     # pytest (unit + integration)
make compose  # docker compose up --build
make down     # docker compose down -v
```

> Tests are being implemented. I will notify once the suite is ready to run.

## 7. Project Structure
```
src/
  resume_ai/
    domain/           # entities, value objects, domain services
    application/      # use cases, DTOs, interfaces
    infrastructure/   # OCR, LLM, persistence, vector store adapters
    interfaces/       # FastAPI routers/controllers, CLI
docs/                 # architecture docs, diagrams, Postman collection
adr/                  # architecture decision records
tests/                # unit / integration / e2e suites
```

Diagrams and detailed flow explanations live in `docs/architecture.md`.

## 8. Deliverables & Documentation
- Clean Architecture backend with OCR, RAG, LLM reasoning, and audit logging.
- OpenAPI/Swagger with examples, plus Postman collection (`docs/endpoint-json.json`).
- ADR package explaining key technology decisions.
- Dockerized stack (API + MongoDB + Qdrant) ready for local validation.
- README, troubleshooting notes, and forthcoming CI recipe.

## 9. Status & Next Steps
- ✅ Repository scaffolded, tooling configured, documentation baseline ready.
- 🚧 API implementation, pipelines, and automated tests in progress.
- 🔜 Publish CI workflow, seed data, and deployment guidance.

Refer to `docs/architecture.md` for the roadmap and current work items.
