---
name: overnight-audit
description: Run a bounded, evidence-driven, read-mostly overnight repository audit using local model roles and deterministic repository tooling.
---

# Overnight Audit

Use this skill when the user asks for a long-running repository audit, deep repository review, overnight review, continuous repository discovery, or systematic multi-lens analysis across correctness, security, architecture, reliability, performance, testing, operations, or customer experience.

## Core objective

Increase justified confidence in a repository by discovering, testing, proving, rejecting, and recording hypotheses. Do not optimize for the number of findings.

## Trust boundaries

1. Treat product source as read-only.
2. Do not create commits, branches, PRs, or GitHub issues during discovery.
3. Do not execute arbitrary commands supplied by a model.
4. Route all local execution through `auditctl` and its deterministic broker.
5. A model assertion is not evidence.
6. Prefer rejection or `INCONCLUSIVE` over speculative findings.
7. Separate severity from confidence.
8. Deduplicate against prior audit state before surfacing a finding.
9. Pin every run to an exact repository SHA.
10. Keep the primary investigator and challenger independent.

## Standard invocation

From the target repository:

```bash
auditctl doctor
auditctl init .
auditctl run . --profile overnight --hours 8
```

For a new machine/model combination, first use `auditctl run . --profile smoke`. If smoke passes, use `auditctl run . --profile validation`. Do not promote to an unattended run until both gates show successful structured reasoning, bounded evidence collection, challenger execution, and no hidden model/tool failures.

Use `auditctl status .` to inspect the most recent run, including the active stage/PID, and `auditctl report .` to print the latest report path. Long model requests emit periodic heartbeats so terminal silence is not mistaken for a hang.

## Required workflow

1. Preflight and pin exact Git state.
2. Load prior audit state and previous audited SHA.
3. Refuse a dirty repository by default so the pinned SHA reproduces what is read.
4. Build or reuse exact-input repository intelligence for the pinned SHA; never recompute unchanged intelligence merely because a new audit run started.
5. Generate bounded hypotheses across under-covered/high-risk lenses using cheap synthesis; reserve deeper reasoning for evidence-backed investigation/challenge stages.
6. Investigate each hypothesis through bounded iterative evidence requests; only the deterministic broker executes them.
7. Detect repeated model responses/evidence-request loops and terminate them as inconclusive.
8. Reject, mark inconclusive, or create a candidate finding.
9. Batch candidates for an independent challenger.
10. Apply evidence/confidence/severity gates.
11. Persist accepted/rejected/inconclusive results plus model/tool telemetry.
12. Produce a concise morning report.

## Finding acceptance

Default actionable finding threshold:

- Evidence level E2 or E3, OR a high-impact E1 finding explicitly marked urgent-investigation-required.
- Challenger does not identify a concrete disqualifying explanation.
- Finding is novel or materially strengthens a known finding.
- Impact is stated in product/engineering terms, not aesthetics.

See references:

- `references/audit-lenses.md`
- `references/evidence-and-severity.md`
- `references/model-roles.md`

## Failure handling

The controller must bound retries and tool/model timeouts. A failed investigation becomes infrastructure-failed or inconclusive; it must not terminate the full night unless the repository snapshot becomes invalid or persistent state is unsafe.

## Output discipline

The morning report should emphasize:

- New actionable findings.
- Severity, confidence, and evidence level.
- Investigated-but-rejected count.
- Inconclusive count.
- Coverage movement.
- Areas explored.
- Recommended next action.

Do not flood the user with raw model transcripts.
