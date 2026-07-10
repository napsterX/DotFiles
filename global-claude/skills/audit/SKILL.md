---
name: audit
description: Perform a read-only audit of the most recent implementation against its original request. Inspect changed behavior, diff, tests, documentation, security boundaries, regression risk, and CI enforcement; use minimal-sufficient-testing to assess evidence; then report PASS, PASS WITH GAPS, FAIL, or AUDIT BLOCKED.
user-invocable: true
---

# Audit

Audit the implementation against what was actually requested.

This is read-only. Inspect, validate, judge, and report. Do not fix code.

Do not assume correctness because code exists, a previous response claimed completion, a commit message says tests passed, a PR is open, or a generic suite is green.

## Authority

This skill owns:

- original-objective determination
- audited-scope determination
- requirement coverage
- implementation findings
- finding priority
- final audit verdict

`~/.claude/skills/minimal-sufficient-testing/SKILL.md` owns:

- evidence reuse and invalidation
- risk-weighted testing
- CI-enforcement assessment
- testing stop conditions
- testing confidence

Invoke it in Validate mode for testing sufficiency.

## Required supporting files

Read:

- `finding-policy.md`
- `report-format.md`

## Modes

### Standalone

Use when directly invoked by the user.

Use conversation context as the first objective source. Ask only when the objective cannot be established from any available source.

### Parent-skill

Use when invoked by `audit-and-pr` or another orchestrator.

The parent should supply repository, branch, scope, objective, prior evidence, and previous findings when relevant.

Do not ask the user in this mode. Return `AUDIT BLOCKED` if essential context remains unavailable.

## Read-only rules

Do not intentionally modify:

- production code
- tests
- docs
- config
- migrations
- generated source
- tracked files

Validation commands selected by `minimal-sufficient-testing` may run.

If a validation command unexpectedly modifies tracked files:

- stop that validation path
- report an audit-process note
- do not broadly reset or overwrite user work

Never use destructive Git cleanup.

## Establish the original objective

Use this order:

1. Current conversation.
2. Objective supplied by a parent.
3. Linked issue or ticket.
4. PR description.
5. Branch-associated issue.
6. Relevant commits.
7. Authoritative implementation document tied to the change.

Do not infer the objective solely from the diff.

If sources conflict, prefer the most direct authoritative source and report the conflict.

If objective remains unknown:

- Standalone: ask the user.
- Parent-skill: return `AUDIT BLOCKED`.

## Establish audited scope

Determine:

- repository
- default branch
- current branch
- current commit
- working-tree status
- merge-base
- audited range or diff
- relevant untracked implementation files
- unrelated pre-existing changes
- existing PR

Default to the complete diff from the merge-base with the default branch unless a specific range, PR, or file set was provided.

Read the full diff, not only filenames or statistics.

## Read repository authority

Inspect applicable guidance:

- `AGENTS.md`
- `CLAUDE.md`
- `CONTRIBUTING.md`
- architecture docs
- implementation plans
- ticket contracts
- API contracts
- schema conventions
- security rules
- testing conventions
- module ownership
- protected zones
- generated-code policies
- CI conventions

Apply only rules that actually exist.

## Review ten dimensions

1. Original objective.
2. Implemented behavior.
3. Requirement satisfaction.
4. Missing or partial requirements.
5. Unintended behavior changes.
6. Duplication, dead code, shortcuts, weakened checks, accidental files.
7. Security, privacy, auth, tenancy, data, payments, migrations, idempotency, and external boundaries.
8. Testing sufficiency and CI enforcement through `minimal-sufficient-testing`.
9. Documentation and contract updates.
10. Regression, rollout, rollback, and assumption risk.

## Runtime validation

When required and feasible, validate actual behavior through targeted local, test, staging, mocked, or repository-supported mechanisms.

Do not perform destructive production actions.

If required validation is unavailable, preserve that limitation in the testing assessment and verdict.

## Output

Return the format defined in `report-format.md`.

Do not emit a long running monologue. A parent skill may provide concise milestone updates.
