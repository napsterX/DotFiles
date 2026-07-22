---
name: audit
description: Perform a read-only audit against the original request, separating direct testing confidence, CI enforcement confidence, and merge eligibility while preserving independent findings and verdict authority.
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
- CI enforcement confidence
- provisional merge-impact classification

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

Use when invoked by `audit-and-pr` or another orchestrator as the authoritative
integrated audit or synthesis lead.

The parent should supply repository, branch, scope, objective, prior evidence,
parallel-lane results when present, and previous findings when relevant.

Do not ask the user in this mode. Return `AUDIT BLOCKED` if essential context
remains unavailable.

### Parent-lane

Use only when `audit-and-pr` assigns one read-only parallel audit lane.

The parent must supply the immutable audit packet, exact HEAD, canonical base,
merge-base, audited scope, assigned dimensions, and evidence seed. Review only
the assigned dimensions deeply enough to detect cross-boundary defects. Do not
modify files, run broad duplicate test suites, remediate, or issue the final
audit verdict.

Return:

- exact HEAD, base, and scope reviewed;
- assigned dimensions completed;
- findings with priority and direct evidence;
- missing evidence obligations;
- uncertainties or conflicts;
- confirmation that no repository mutation was performed.

The parent synthesis lead owns deduplication, conflict resolution, P0/P1 direct
verification, evidence reconciliation, and the single authoritative verdict.

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

## Three independent decisions

Never collapse these into one confidence label:

- **Testing confidence** answers whether the audited implementation is directly
  and sufficiently proven for the exact code state.
- **CI enforcement confidence** answers whether required permanent checks are
  durably enforced by the repository's CI architecture.
- **Merge eligibility** answers whether current audit, verification, CI, review,
  protection, and repository-specific policy permit automatic merge, require a
  human merge, or block merge.

A documented repository-wide CI coverage limitation must not reduce testing
confidence when all of the following are true:

- the authoritative `./scripts/verify ship --base <resolved-base>` gate passed
  against the exact audited commit when the adapter exists;
- the working tree remained clean;
- no commit was added after that result;
- every change-relevant high-risk check was directly executed and passed;
- planned and executed evidence reconcile;
- no material testing gap or conflicting result remains.

Report the CI limitation separately. It may reduce CI enforcement confidence
and may require manual merge under repository policy, but it is not a reason to
mislabel directly proven code as Moderate or Low testing confidence.

A CI failure or local-versus-CI disagreement can still reduce testing confidence
when it creates an unresolved evidence conflict. That reduction is caused by the
conflict, not by CI architecture alone.

## Review ten dimensions

1. Original objective.
2. Implemented behavior.
3. Requirement satisfaction.
4. Missing or partial requirements.
5. Unintended behavior changes.
6. Duplication, dead code, shortcuts, weakened checks, accidental files.
7. Security, privacy, auth, tenancy, data, payments, migrations, idempotency, and external boundaries.
8. Testing sufficiency, CI enforcement confidence, and provisional merge impact through `minimal-sufficient-testing`.
9. Documentation and contract updates.
10. Regression, rollout, rollback, and assumption risk.

## Runtime validation

When required and feasible, validate actual behavior through targeted local, test, staging, mocked, or repository-supported mechanisms.

Do not perform destructive production actions.

If required validation is unavailable, preserve that limitation in the testing assessment and verdict.

## Output

Standalone and Parent-skill modes return the format defined in
`report-format.md`.

Parent-lane mode returns the lane contract above and must not emit a competing
final verdict.

Do not emit a long running monologue. A parent skill may provide concise
milestone updates.
