# ADR 0003: Persistence and Audit Logging

## Status
Accepted – 2025-11-05

## Context
The platform must register audit events for every request without storing full résumé documents. Requirements include queryable logs, flexible schema, and future portability to AWS-managed services.

## Decision
Store audit logs in **MongoDB** using a dedicated collection with schema validation and TTL indices. Each log entry contains `request_id`, `user_id`, `timestamp`, `query`, `result`, and metadata essential for traceability. Binary files remain transient and are not persisted.

## Rationale
- Document database handles semi-structured audit records cleanly.
- MongoDB aligns with modern backend stacks and mirrors DynamoDB document patterns, easing future migration.
- Native TTL indices simplify retention policies without batch jobs.

## Consequences
- Need to manage MongoDB connectivity and migrations (using JSON schema + migration scripts).
- Integration tests will rely on ephemeral MongoDB containers (via Docker Compose or Testcontainers).
- Consider eventual consistency when integrating with message queues or streaming audits to data lakes.

