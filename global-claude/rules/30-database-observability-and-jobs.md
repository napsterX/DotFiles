# Database, Observability, and Jobs

## Database changes

- Inspect the authoritative schema and migration history before writing SQL or data-access code. Never guess table, column, constraint, or enum names from memory.
- Use the data model that best represents the domain. Do not create complex code workarounds merely to avoid a legitimate, safe schema change.
- Prefer explicit typed columns and constraints for business-critical state. Avoid catch-all JSON, metadata, payload, temporary-status, or flag fields that hide durable domain behavior unless the content is genuinely schemaless and bounded.
- Safe additive changes may proceed as part of an authorized implementation when they are backward-compatible and include migration, compatibility, security, deployment-order, rollback, and test considerations.
- Obtain explicit approval before destructive changes, broad backfills, access-broadening policy changes, incompatible type or key changes, large locking operations, retention changes, or storage of a new sensitive-data category. If risk is unclear, treat it as approval-required.
- Make migrations repeatable where appropriate, preserve existing data, define constraints and indexes deliberately, and keep application code compatible across the deployment sequence.
- Validate migrations against a representative database and update generated schema or client types when the repository uses them.

## Observability and asynchronous work

- Critical workflows must be diagnosable without reconstructing behavior from source code. Emit structured, machine-queryable events with applicable request, correlation, tenant, resource, job, and provider identifiers.
- Use severity accurately: expected validation or business outcomes are not system errors; unexpected infrastructure, dependency, consistency, or processing failures are.
- Never emit secrets, tokens, signed URLs, raw sensitive payloads, or unsanitized provider errors to logs, traces, metrics, or error-reporting systems.
- Design background jobs as explicit lifecycle objects when reliability matters: idempotent, bounded, observable, retry-safe, and recoverable. Distinguish user-correctable, transient, configuration, and permanent failures.
- Prevent duplicate processing with durable idempotency or concurrency controls. Preserve enough execution history to investigate retries and terminal failures.
- Do not perform expensive, failure-prone, or long-running work inside request/response paths when asynchronous execution is the safer design.
- Provide an operator recovery path for stuck or terminal work when automatic recovery is insufficient.
