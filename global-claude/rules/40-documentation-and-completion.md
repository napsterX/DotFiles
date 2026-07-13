# Documentation and Completion

- Update documentation in the same change when public behavior, APIs, configuration, architecture, ownership, lifecycle semantics, schema, security controls, operational procedures, or failure-recovery behavior changes.
- Do not force documentation churn for internal refactors that leave documented behavior and operations unchanged. State that no documentation change was needed when the reason is not obvious.
- Keep canonical information in one place and link to it rather than duplicating contracts, state machines, runbooks, terminology, or architecture descriptions across files.
- Update runbooks when a change creates a new operational failure mode, alert, recovery action, deployment dependency, or manual intervention requirement.
- Do not leave untracked promises in TODO comments, design notes, or summaries. Use the repository's existing tracker when deferred work must be recorded; do not invent a parallel backlog system.
- Before declaring implementation complete, report concisely:
  - what changed and why;
  - files or areas changed;
  - tests and validation actually run, with results;
  - documentation impact;
  - security, data, migration, or operational impact when relevant;
  - known limitations, unresolved failures, follow-up work, and rollback considerations.
- A task is not complete with a newly introduced failing required gate, an unexplained validation gap, or a claim of readiness unsupported by the validations performed.
- If environment limitations prevent a required validation, state exactly what was not verified, why, what partial evidence exists, and the specific remaining validation step. Do not fabricate success.
