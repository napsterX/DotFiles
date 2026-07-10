---
name: audit-and-pr
description: Audit the current implementation, reuse trustworthy prior testing, close only safe mechanical findings through a bounded remediation loop, and ship only when the audit gate clears. Prepare the branch and commits, track qualifying gaps, open or update the PR, wait for CI, and merge only when the stricter automatic-merge gate is satisfied.
user-invocable: true
disable-model-invocation: true
---

# Audit and PR

Orchestrate an audited shipping workflow.

This skill delegates:

- audit judgment to `~/.claude/skills/audit/SKILL.md`
- test evidence, test selection, CI-enforcement assessment, and confidence to `~/.claude/skills/minimal-sufficient-testing/SKILL.md`

This skill owns orchestration, bounded remediation, shipment gating, Git/GitHub operations, CI waiting, merge gating, cleanup, and final reporting.

## Required supporting files

Read:

- `remediation-policy.md`
- `shipping-gate.md`
- `github-and-pr-policy.md`
- `ci-and-merge-policy.md`
- `report-format.md`

## Core guarantees

Never:

- ship without a completed audit
- treat unsupported test claims as evidence
- rerun everything for ceremony
- auto-fix security, architecture, or design decisions
- ship with P0, P1, or Low confidence
- turn audit-process notes into repository issues
- merge through failed, cancelled, unresolved, or bypassed checks
- bypass branch protection or approval
- conceal auto-fixes
- include unrelated work
- use destructive Git cleanup

## Progress updates

Provide concise milestone updates:

1. Objective and scope established.
2. Risk and prior evidence assessed.
3. Initial audit completed.
4. Auto-fix decision completed.
5. Re-audit completed.
6. Shipment gate cleared or blocked.
7. PR and CI outcome determined.

Do not narrate every checklist item.

## Audit model

The initial audit and every re-audit use a pinned model and a pinned
reasoning effort.

- Invocation argument wins for model choice.
- Otherwise default to Opus.
- Effort defaults to xhigh, on whichever model is selected.
- Use the same model and effort for all audit rounds.
- If the named model is unavailable, fall back to Opus and report it.
- If xhigh effort is unavailable for the selected model, fall back to that
  model's highest available effort and report it.
- Do not silently substitute either the model or the effort.

## Remediation model

All remediation work - applying eligible auto-fixes, and any Implementation
mode test/CI work invoked through `minimal-sufficient-testing` - runs on its
own pinned model and reasoning effort, independent of whichever model is
orchestrating this skill.

- Model: Sonnet.
- Effort: xhigh.
- Use the same model and effort for every remediation round.
- If unavailable, fall back to the orchestrating session's own model and
  report it.
- Do not silently substitute either the model or the effort.

## Establish objective and scope

Determine:

- repository
- default branch
- current branch
- current commit
- working-tree status
- merge-base
- audited diff/range
- relevant untracked implementation files
- unrelated pre-existing changes
- existing PR
- original objective
- linked issue or ticket

Objective source order:

1. Current conversation.
2. Explicit invocation request.
3. Linked issue or ticket.
4. Existing PR description.
5. Branch-associated issue.
6. Relevant commits.
7. Authoritative implementation document.

Do not infer objective solely from the diff.

If objective cannot be established, return `AUDIT BLOCKED` and perform no modification, branch, commit, push, issue, PR, or merge action.

## Protect unrelated work

Identify audited files and changes.

Exclude unrelated work from audits, fixes, commits, PRs, and cleanup.

Never use destructive reset, clean, checkout, force-push, or branch deletion.

## Seed prior evidence

Build an initial evidence seed from exact current-session outputs when available:

- lint/format
- typecheck
- build
- automated tests
- browser validation
- migration validation
- security checks
- defect reproduction and post-fix confirmation
- manual validation
- CI

Capture command/procedure, result, code state, environment, behavior covered, and source.

Do not classify it as reusable yourself. The testing skill owns that.

## Initial audit

Dispatch the selected audit model and effort.

Invoke `audit` in Parent-skill mode with:

- repository
- branch
- scope
- objective
- repository guidance
- linked issue/ticket
- evidence seed
- known constraints

The audit invokes `minimal-sufficient-testing` in Validate mode.

Do not run a competing testing framework in the orchestrator.

## Bounded remediation

Follow `remediation-policy.md`, dispatched on the pinned remediation model
(see `## Remediation model`).

At most three rounds.

Do not commit during remediation.

After every retained round, rerun the complete audit on the pinned audit
model and effort (see `## Audit model`). Reconsider all ten dimensions, but
rerun only evidence invalidated by the changes.

## Shipment gate

Follow `shipping-gate.md`.

If blocked, leave retained safe local fixes uncommitted, report them, and stop before branch, commit, push, issue, or PR operations.

## GitHub and PR

After the gate clears, follow `github-and-pr-policy.md`.

## CI and merge

Follow `ci-and-merge-policy.md`.

Automatic merge is stricter than PR eligibility.

## Final report

Use `report-format.md`.
