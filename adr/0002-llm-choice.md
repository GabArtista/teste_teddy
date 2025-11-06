# ADR 0002: LLM Provider and Model

## Status
Accepted – 2025-11-05

## Context
The system must deliver accurate summaries and hiring recommendations with traceable reasoning. Available options include OpenAI, Anthropic, and local fine-tuned models. The team already has access to OpenAI APIs.

## Decision
Use **OpenAI GPT-4.1** through LangChain's `ChatOpenAI` wrapper as the default reasoning engine. Provide a mock implementation for offline tests and a configuration hook for alternative models.

## Rationale
- GPT-4.1 offers the best balance of reasoning depth, latency, and structured output fidelity for résumé analysis tasks.
- OpenAI's JSON mode improves deterministic parsing for audit logs and justifications.
- Aligns with company expectations for market-standard tooling and showcases ability to operate within enterprise ecosystems.

## Consequences
- Requires secure handling of `OPENAI_API_KEY` via environment variables and secret storage.
- Cost monitoring is essential; include rate limiting and caching strategies for production.
- Provide abstraction around LLM calls to simplify migration to Azure OpenAI or other vendors if procurement changes.

