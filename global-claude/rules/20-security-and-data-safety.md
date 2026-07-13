# Security and Data Safety

- Treat all client input and client-side checks as untrusted. Enforce authentication, authorization, tenancy, and role checks on the server at every protected boundary.
- Validate and normalize untrusted input before use. Use parameterized queries and safe APIs; avoid injection-prone string construction.
- Apply least privilege. Prevent cross-tenant access, insecure direct-object references, privilege escalation, and accidental broadening of data access.
- Protect secrets and credentials. Never place real secrets, tokens, signed URLs, private keys, or production credentials in source, tests, logs, documentation, examples, prompts, URLs, or client bundles.
- Minimize sensitive-data collection, exposure, retention, and logging. Do not log raw personal, financial, authentication, document, or provider payload data. Prefer identifiers, classifications, counts, and sanitized error details.
- Treat private repositories and internal documentation as potentially exposable. Use clearly synthetic examples and placeholders; never copy real customer data or live production identifiers into documentation or fixtures.
- Return safe external errors without leaking internals. Preserve detailed diagnostics only in protected telemetry, with sensitive fields removed.
- Review new endpoints, jobs, file flows, webhooks, and privileged operations for authentication, authorization, input limits, abuse, replay, rate limiting where appropriate, data exposure, and auditability.
- Sensitive or irreversible mutations should produce an immutable audit record when the system has an audit facility. Do not allow audit metadata to become a second store of sensitive payloads.
- Keep uploaded or generated sensitive files private, validate type and size server-side, and use short-lived access mechanisms where temporary sharing is required.
- Security controls must fail safely. Do not temporarily bypass authorization, access policies, certificate checks, secret scanning, or other protections to unblock implementation.
