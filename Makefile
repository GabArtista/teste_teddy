POETRY ?= poetry
PYTHON ?= $(POETRY) run python

.PHONY: bootstrap
bootstrap:
	$(POETRY) install --no-root

.PHONY: lint
lint:
	$(POETRY) run ruff check src tests
	$(POETRY) run mypy src

.PHONY: test
test:
	$(POETRY) run pytest --cov=resume_ai --cov-report=term-missing

.PHONY: run
run:
	$(POETRY) run uvicorn resume_ai.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: compose
compose:
	docker compose up --build

.PHONY: down
down:
	docker compose down -v

.PHONY: format
format:
	$(POETRY) run ruff check --select I --fix src tests
	$(POETRY) run ruff format src tests

