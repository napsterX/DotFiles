# GitHub and PR Policy

## Branch

Run only after shipment gate clears.

- Reuse a suitable existing non-default branch.
- If changes are on the default branch, create a new branch.
- Follow repository branch conventions.
- Otherwise use a concise `feature/`, `fix/`, `refactor/`, `test/`, `docs/`, or `chore/` name.

## Commit

Commit only audited scope.

Exclude unrelated changes.

Match repository commit style.

### Original implementation uncommitted

Commit the final audited implementation coherently. Retained safe fixes may be included when separating them would require risky patch reconstruction.

Disclose all auto-fixes.

### Original implementation committed

Commit retained auto-fixes separately.

Do not rewrite history unless explicitly required.

## Push

Push without force.

If push fails, report and stop.

## Track findings

Only implementation findings participate.

Never create issues for audit-process notes.

### P2

For each actionable P2:

1. Search open issues for an equivalent.
2. Reuse an actual equivalent open issue.
3. Otherwise create a new issue.

Closed issues provide context but are not active tracking. If a gap reappeared, create a new issue and reference the old one.

### P3

Create an issue only when actionable, durable, independently prioritizable, and objectively closeable.

Group related P3s when that improves backlog quality.

Leave trivial or speculative P3s in the PR only.

### Issue body

Include:

- priority
- observed gap
- risk
- evidence
- affected branch
- acceptance criteria
- audit origin

Follow existing labels. Do not invent taxonomy.

## Existing PR

Do not create a duplicate.

Update the body when needed while preserving useful context.

## New PR

Read the real template field by field.

Populate actual values.

Use `N/A — <reason>` when genuinely inapplicable.

Never leave unresolved placeholders.

## Required PR content

Include:

- summary of behavioral changes
- motivation
- requirement coverage
- impact and risk
- tests and validation
- reused versus rerun evidence
- CI enforcement status
- audit verdict
- retained auto-fixes
- known gaps and issue links
- rollback
- repository-specific metadata

Do not imply reused evidence was freshly rerun.

## Rollback

State whether rollback is:

- commit revert
- config rollback
- migration reversal
- data repair
- constrained by irreversible side effects
