# Skill Audit

## Scope

This audit covers argument parsing, queue bounds, model routing, worker isolation,
commit integrity, dirty-tree protection, GitHub behavior, interruption and
partial failure, repository verification integration, untrusted issue content,
shell safety, credential exposure, PR/merge prohibitions, loop bounds, and honest
reporting.

## Findings and controls

- **Prompt injection through issue content:** mitigated by treating issue bodies,
  comments, labels, logs, links, and screenshots as untrusted data that cannot
  override skill or repository authority.
- **Silent model fallback:** mitigated by explicit per-issue routing records,
  per-invocation Agent model parameters, environment-override checks, mismatch
  rejection, and honest reporting when runtime identity is not exposed.
- **Parent implementation fallback:** prohibited. The orchestrator may inspect,
  select, route, verify, and report but must not edit source code.
- **Unbounded processing:** positive integer validation, hard cap `10`, and
  selected-issue slot accounting prevent quota drift.
- **Cross-issue contamination:** one issue per worker, one fixed issue per commit,
  queue refresh after each slot, and diff-tree validation.
- **Dirty work contamination:** proceed only with clearly unrelated changes;
  overlapping or ambiguous ownership blocks.
- **Shell injection:** issue-controlled values must be passed as data or separated
  arguments; `eval` and unsafe interpolation are prohibited.
- **Credential exposure:** do not print the full environment or secret values.
- **PR/merge side effects:** explicitly prohibited; push requires repository-
  specific authorization.
- **Verification weakening:** test deletion, blanket skips, threshold lowering,
  broad allowlists, and advisory reclassification are prohibited as green-making
  tactics.

## Accepted platform limitation

Claude Code supports a per-invocation model parameter for subagents, but an
administrator allowlist or `CLAUDE_CODE_SUBAGENT_MODEL` can affect resolution.
Some host surfaces may not expose deterministic resolved-model metadata to the
calling skill. The skill therefore distinguishes the requested model from
runtime confirmation and never claims proof when the platform does not provide
it.
