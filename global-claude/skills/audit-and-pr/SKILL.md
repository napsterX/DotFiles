---
name: audit-and-pr
description: Run repository-native deterministic verification when available, perform an independent audit with bounded remediation, validate the final committed HEAD, then execute the existing PR, CI, merge, and safe post-merge cleanup policies.
user-invocable: true
disable-model-invocation: true
---

# Audit and PR

Orchestrate an audited shipping workflow from objective reconstruction through
post-merge cleanup.

This skill delegates:

- audit judgment to `~/.claude/skills/audit/SKILL.md`;
- test evidence, test selection, CI-enforcement assessment, and confidence to
  `~/.claude/skills/minimal-sufficient-testing/SKILL.md`.

This skill owns orchestration, Repository Verification V1 integration, bounded
remediation, audit eligibility, Git/GitHub operations, CI waiting, merge
gating, cleanup, and final reporting.

## Required supporting files

Read:

- `repository-verification-policy.md`
- `remediation-policy.md`
- `shipping-gate.md`
- `github-and-pr-policy.md`
- `ci-and-merge-policy.md`
- `report-format.md`

Use `scripts/repository_verification.py` for safe adapter invocation and evidence
capture when executable helpers are supported. Use
`scripts/shipping_decision.py` as the executable reference for keeping testing
confidence, CI enforcement confidence, and merge eligibility independent.

## Core guarantees

Never:

- imply Repository Verification exit `0` equals audit approval;
- continue after a present adapter fails, is invalid, times out, or contradicts
  its own success result;
- fall back to legacy validation unless `./scripts/verify` is genuinely absent;
- ship without a completed independent audit;
- treat unsupported test claims as evidence;
- rerun everything for ceremony;
- auto-fix security, architecture, or design decisions;
- ship with P0, P1, or Low testing confidence;
- lower testing confidence solely because of a documented accepted repository-wide CI coverage limitation;
- collapse testing confidence, CI enforcement confidence, and merge eligibility into one status;
- turn audit-process notes into repository issues;
- push or create/update a PR before the final exact committed HEAD satisfies
  the applicable repository-verification or legacy shipping gate;
- merge through failed, cancelled, unresolved, or bypassed checks;
- bypass branch protection or approval;
- conceal auto-fixes;
- include unrelated work;
- use destructive Git cleanup;
- force-delete an unmerged branch.

## Progress updates

Provide concise milestone updates:

1. Objective, repository safety, scope, and canonical base established.
2. Repository Verification initial result or legacy mode established.
3. Risk and prior evidence assessed.
4. Independent initial audit completed.
5. Auto-fix decision completed.
6. Remediation revalidation and re-audit completed.
7. Audit eligibility gate cleared or blocked.
8. Final exact-HEAD verification passed or failed.
9. PR, CI, merge, and cleanup outcome determined.

Do not narrate every checklist item.

## Audit model

The initial audit and every re-audit use a pinned model and a pinned reasoning
effort.

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

## Establish repository, objective, scope, and base

Determine:

- repository;
- default branch;
- current branch;
- current commit;
- working-tree status;
- canonical audit base;
- merge-base;
- audited diff/range;
- relevant untracked implementation files;
- unrelated pre-existing changes;
- existing PR and its target branch;
- original objective;
- linked issue or ticket.

Objective source order:

1. Current conversation.
2. Explicit invocation request.
3. Linked issue or ticket.
4. Existing PR description.
5. Branch-associated issue.
6. Relevant commits.
7. Authoritative implementation document.

Do not infer objective solely from the diff.

Resolve the canonical base using `repository-verification-policy.md`. Do not
hardcode a default branch. If objective or base cannot be established, return
`AUDIT BLOCKED` and perform no modification, branch, commit, push, issue, PR,
merge, or cleanup action.

## Protect unrelated work

Identify audited files and changes.

Exclude unrelated work from audits, fixes, commits, PRs, and cleanup.

Never use destructive reset, clean, checkout, force-push, or branch deletion
outside the bounded post-merge cleanup explicitly permitted by
`ci-and-merge-policy.md`.

## Initial Repository Verification

Before the independent audit, follow `repository-verification-policy.md`:

1. detect `./scripts/verify`;
2. when valid, run `./scripts/verify ship --base <resolved-base>` safely;
3. stop immediately on a nonzero, invalid, contradictory, timed-out, interrupted,
   HEAD-changing, or tree-changing result;
4. when genuinely absent, record legacy mode and preserve the existing
   repository-native validation workflow;
5. continue independent audit only after adapter exit `0` or confirmed absence.

Flag verification-governance-sensitive diffs for heightened independent review.

## Establish the evidence plan

After the initial Repository Verification result permits the independent audit,
use `minimal-sufficient-testing` to define the minimum change-relevant evidence
obligations before any remediation work begins.

The plan must identify the required behavior, risk or boundary, command or
procedure, expected result, and code-state binding. Repository Verification may
satisfy repository-declared obligations, but the independent audit must add any
important check omitted by the adapter.

After validation, reconcile every planned item as `PASS`, `FAIL`, `UNAVAILABLE`,
`NOT RUN`, or `NOT APPLICABLE`. A required `UNAVAILABLE` or `NOT RUN` item blocks
completion.

## Seed prior evidence

Build an initial evidence seed from exact current-session outputs when
available:

- Repository Verification evidence;
- lint/format;
- typecheck;
- build;
- automated tests;
- browser validation;
- migration validation;
- security checks;
- defect reproduction and post-fix confirmation;
- manual validation;
- CI.

Capture command/procedure, result, code state, environment, behavior covered,
and source.

Do not classify it as reusable yourself. The testing skill owns that.
Repository Verification evidence remains distinct from independent testing
confidence.

The testing result must return three separate decisions:

- `testing_confidence`;
- `ci_enforcement_confidence`;
- provisional `merge_eligibility`.

A documented repository-wide CI coverage limitation must not reduce testing
confidence when the exact audited commit passed the applicable final ship gate,
the tree stayed clean, no commit followed, every change-relevant high-risk check
was directly executed, and planned versus executed evidence reconciles. Report
the CI gap and repository-policy merge impact separately.

## Independent initial audit

Dispatch the selected audit model and effort.

Invoke `audit` in Parent-skill mode with:

- repository;
- branch;
- scope;
- canonical base and merge-base;
- objective;
- repository guidance;
- linked issue/ticket;
- evidence seed;
- Repository Verification result or legacy mode;
- verification-governance-sensitive flag;
- known constraints.

The audit invokes `minimal-sufficient-testing` in Validate mode.

Do not run a competing testing framework in the orchestrator. Do not defer to
the repository adapter on code correctness, security, tenancy, authorization,
data, migrations, architecture, or governance sufficiency.

## Bounded remediation

Follow `remediation-policy.md`, dispatched on the pinned remediation model.

At most three rounds.

Do not commit during remediation.

After every retained round that changes tracked files:

1. restate the remediation evidence plan before validation;
2. run targeted validation selected by `minimal-sufficient-testing`;
3. reconcile planned versus executed checks;
4. rerun `./scripts/verify ship --base <resolved-base>` when the adapter is
   present, or the applicable legacy validation when absent;
5. stop on any verification or evidence blocker;
6. rerun the complete independent audit on the pinned audit model and effort.

Reconsider all ten audit dimensions, but rerun only evidence invalidated by the
changes.

## Audit eligibility gate

Follow the first gate in `shipping-gate.md`.

If blocked, leave retained safe local fixes uncommitted, report them, and stop
before branch, commit, push, issue, PR, merge, or cleanup operations.

## Commit the audited scope

After audit eligibility clears, follow the Branch and Commit sections of
`github-and-pr-policy.md`.

The final repository-verification gate validates the exact committed tree:

1. create or reuse the shipping branch;
2. commit only the final audited scope;
3. confirm no unrelated changes entered the commit;
4. confirm the working tree is clean;
5. record the exact `HEAD` SHA.

Do not push yet.

## Final exact-HEAD verification

Follow the second gate in `shipping-gate.md`.

For a valid adapter, rerun:

```text
./scripts/verify ship --base <resolved-base>
```

Require exit `0`, no contradictory output, unchanged `HEAD`, and unchanged clean
working tree for the exact committed SHA. For an absent adapter, use the
preserved legacy final validation behavior.

If the final gate fails:

- do not push;
- do not create or update a PR;
- do not file tracking issues;
- do not merge;
- retain the local commit and report the failure;
- treat any corrective edit as new implementation work requiring revalidation,
  re-audit, recommit, and a fresh final gate.

## GitHub and PR

Only after the final gate passes, follow the remaining sections of
`github-and-pr-policy.md`.

## CI, merge, and cleanup

Follow `ci-and-merge-policy.md` without changing repository-specific merge
exceptions or authorizations.

Determine and report separately:

- testing confidence;
- CI enforcement confidence;
- final merge eligibility.

A documented accepted repository-wide CI architecture limitation may leave
testing confidence High while CI enforcement confidence is Moderate. Apply the
repository's merge policy to decide whether that means manual merge. Do not
globalize one repository's exception.

Automatic merge is stricter than repository verification or PR eligibility.

After a successful merge, cleanup is mandatory. Update the default branch,
prove the feature branch is merged, delete only safely merged branches, and
preserve unrelated work.

## Final report

Use `report-format.md`. Keep Repository Verification, independent audit,
testing, CI, PR, merge, and cleanup as separate sections.
