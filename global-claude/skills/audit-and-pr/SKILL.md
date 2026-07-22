---
name: audit-and-pr
description: Run lightweight deterministic preflight, perform an independent risk-adaptive parallel audit, remediate only eligible P0/P1 blockers, defer every confirmed P2/P3 to GitHub tracking, validate the final committed HEAD with the repository ship gate, then execute the existing PR, CI, merge, and safe post-merge cleanup policies.
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

This skill owns orchestration, Repository Verification V1 integration,
dependency-aware parallel audit execution, bounded remediation, audit
eligibility, Git/GitHub operations, CI waiting, merge gating, cleanup, and final
reporting.

## Required supporting files

Read:

- `repository-verification-policy.md`
- `parallel-audit-policy.md`
- `remediation-policy.md`
- `shipping-gate.md`
- `github-and-pr-policy.md`
- `ci-and-merge-policy.md`
- `report-format.md`

Executable references when helpers are supported:

- `scripts/repository_verification.py` — safe `doctor`, `fast`, and final `ship`
  invocation and evidence capture;
- `scripts/workflow_plan.py` — required verification-stage ordering;
- `scripts/audit_parallelism.py` — automatic read-only lane selection;
- `scripts/shipping_decision.py` — separation of testing confidence, CI
  enforcement confidence, deferred-finding tracking, and merge eligibility;
- `scripts/finding_disposition.py` — severity-driven remediation and mandatory
  GitHub tracking decisions for confirmed P2/P3 findings.

## Core guarantees

Never:

- imply Repository Verification exit `0` equals audit approval;
- run the full `ship` profile before the independent audit merely as a default;
- run `ship` after every remediation edit for ceremony;
- continue after a required deterministic preflight or final gate fails, is
  invalid, times out, is interrupted, mutates the repository, or contradicts its
  own success output;
- fall back to legacy validation unless `./scripts/verify` is genuinely absent;
- ship without a completed independent audit;
- treat unsupported test claims as evidence;
- allow concurrent remediation writers or concurrent Git/PR mutations;
- auto-fix security, architecture, migration, authorization, tenancy, or design
  decisions;
- modify code to remediate a P2 or P3 finding, even when the change appears
  mechanical or low risk;
- defer an unresolved P0/P1 to a backlog issue;
- merge while any confirmed P2/P3 implementation finding lacks an equivalent
  open GitHub issue;
- downgrade a finding to P2/P3 merely to avoid current-scope remediation;
- ship with P0, P1, or Low testing confidence;
- lower testing confidence solely because of a documented accepted
  repository-wide CI coverage limitation;
- collapse testing confidence, CI enforcement confidence, and merge eligibility
  into one status;
- turn audit-process notes into repository issues;
- push or create/update a PR before the final exact committed HEAD satisfies the
  applicable repository-verification or legacy shipping gate;
- merge through failed, cancelled, unresolved, or bypassed checks;
- bypass branch protection or approval;
- conceal auto-fixes;
- include unrelated work;
- use destructive Git cleanup;
- force-delete an unmerged branch.

## Progress updates

Provide concise milestone updates:

1. Objective, repository safety, scope, and canonical base established.
2. Adapter state and deterministic preflight established, or legacy mode
   confirmed.
3. Risk, evidence plan, and parallel lane plan established.
4. Independent initial audit synthesized.
5. Severity disposition completed: P0/P1 remediation candidates and deferred
   P2/P3 tracking records established.
6. P0/P1 remediation validation and re-audit completed.
7. Audit eligibility gate cleared or blocked.
8. Final exact-HEAD ship or legacy verification passed or failed.
9. Deferred P2/P3 GitHub tracking completed or blocked.
10. PR, CI, merge, and cleanup outcome determined.

Do not narrate every checklist item.

## Audit model

The initial audit and every re-audit use a pinned model and pinned reasoning
effort.

- Invocation argument wins for model choice.
- Otherwise default to Opus.
- Effort defaults to xhigh.
- Use the same model and effort for every lane and synthesis round.
- If the named model is unavailable, fall back to Opus and report it.
- If xhigh is unavailable, use the selected model's highest available effort and
  report it.
- Do not silently substitute model or effort.

## Remediation model

All eligible P0/P1 remediation work, including Implementation-mode work
delegated to `minimal-sufficient-testing`, uses its own pinned model and effort.
P2/P3 findings never enter the remediation writer.

- Model: Sonnet.
- Effort: xhigh.
- Use the same model and effort for every remediation round.
- If unavailable, fall back to the orchestrating session model and report it.
- Do not silently substitute model or effort.

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
- existing PR and target branch;
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

Identify audited files and changes. Exclude unrelated work from audits, fixes,
commits, PRs, and cleanup.

Never use destructive reset, clean, forced checkout, force-push, or branch
deletion outside the bounded post-merge cleanup explicitly permitted by
`ci-and-merge-policy.md`.

## Deterministic preflight

Follow `repository-verification-policy.md` and `shipping-gate.md`.

1. Detect `./scripts/verify` without modifying it.
2. If the path is invalid, block before the deep audit. Do not repair it and do
   not fall back.
3. If valid, run `./scripts/verify doctor` safely.
4. Run `./scripts/verify fast --base <resolved-base>` when useful: code or
   configuration changed, risk is Medium or High, repository policy requires
   it, or no reusable exact-HEAD fast evidence exists. A documentation-only or
   trivially low-risk change may skip `fast` with an explicit reason.
5. Stop before the deep audit on any required preflight failure, contradiction,
   timeout, interruption, HEAD change, or working-tree change.
6. If the adapter is genuinely absent, record legacy mode and preserve existing
   repository-native validation discovery and behavior.

Do **not** run `./scripts/verify ship` in this pre-audit stage. The authoritative
ship profile is reserved for the final committed audited HEAD.

When concurrency is available, `fast` may overlap only with read-only audit
packet preparation as defined by `parallel-audit-policy.md`.

## Establish the evidence plan

After preflight permits the audit, use `minimal-sufficient-testing` to define the
minimum change-relevant evidence obligations before remediation begins.

The plan identifies:

- behavior or boundary being proven;
- risk addressed;
- command or procedure;
- expected result;
- required or advisory classification;
- exact code-state binding.

Preflight evidence may satisfy repository-declared obligations, but the
independent audit must add material checks omitted by the repository contract.
After validation, reconcile every item as `PASS`, `FAIL`, `UNAVAILABLE`, `NOT
RUN`, or `NOT APPLICABLE`. A required `UNAVAILABLE` or `NOT RUN` item blocks
completion.

## Seed prior evidence

Build an evidence seed from exact current-session outputs when available:

- `doctor` and `fast` preflight evidence or legacy mode;
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
and source. Do not classify evidence as reusable yourself; the testing skill
owns that decision.

The testing result returns three independent decisions:

- `testing_confidence`;
- `ci_enforcement_confidence`;
- provisional `merge_eligibility`.

A documented repository-wide CI limitation must not reduce testing confidence
when the final exact audited commit passes the applicable ship gate, the tree
stays clean, no later commit appears, all change-relevant high-risk checks run,
and planned versus executed evidence reconciles. Report CI enforcement and
repository-policy merge impact separately.

## Independent audit with risk-adaptive parallelism

Follow `parallel-audit-policy.md`.

1. Build one immutable audit packet bound to the exact HEAD, base, merge-base,
   diff, objective, guidance, evidence, risk, and unrelated-work boundary.
2. Use `scripts/audit_parallelism.py` or equivalent logic to select one to four
   read-only lanes.
3. Dispatch lanes concurrently only when the host supports it.
4. Every lane uses the pinned audit model and effort, receives the same packet,
   and returns structured findings without modifying the worktree.
5. Centralize test execution through `minimal-sufficient-testing`; lanes do not
   run duplicate broad suites.
6. One authoritative lead rejects stale results, deduplicates findings, resolves
   conflicts, directly verifies proposed P0/P1 findings, reconciles evidence,
   and produces one verdict.

When parallel execution is unavailable or would be slower for a small change,
run one integrated audit sequentially. The safety and coverage standard does not
change.

Flag verification-governance-sensitive diffs and add the dedicated governance
lane when parallel mode is used.

## Severity disposition and bounded remediation

Follow `remediation-policy.md` and use `scripts/finding_disposition.py` or
equivalent logic before any edit. Severity is determined by the independent
audit, not by remediation convenience.

- Only confirmed P0/P1 findings may enter remediation.
- A P0/P1 that is not safely remediable remains a shipment blocker; do not defer
  it to backlog tracking.
- Every confirmed P2/P3 is excluded from remediation, even when a mechanical fix
  appears obvious.
- If a P2/P3 is actually required to satisfy the current objective or acceptance
  criteria, stop for classification review: reclassify it as blocking or mark
  the objective unsatisfied.
- Normalize every legitimate deferred P2/P3 into an issue-ready tracking record
  after authoritative synthesis.
- At most three remediation rounds.
- Exactly one remediation writer.
- Do not commit during remediation.

After every retained round that changes tracked files:

1. restate the remediation evidence plan;
2. run targeted validation selected by `minimal-sufficient-testing`;
3. reconcile planned versus executed evidence;
4. rerun `fast --base <resolved-base>` only when remediation invalidates the
   prior preflight, repository policy requires it, or verification machinery
   changed;
5. run focused conformance evidence for verification-governance changes;
6. create a fresh immutable packet for the new code state;
7. rerun the applicable audit lanes and authoritative synthesis.

Do not run the full `ship` profile after each remediation round. An earlier ship
result, if one exists from outside this workflow, never authorizes the final
state.

## Audit eligibility gate

Follow Gate 1 in `shipping-gate.md`.

If blocked, leave retained safe P0/P1 local fixes uncommitted, report them, and
stop before branch, commit, push, issue, PR, merge, or cleanup operations.

Gate 1 may clear with confirmed P2/P3 findings only when each is genuinely
non-blocking, independently closeable, and represented by a complete issue-ready
record. Actual GitHub tracking is mandatory after final verification and before
PR mutation or merge.

## Commit the audited scope

After audit eligibility clears, follow the Branch and Commit sections of
`github-and-pr-policy.md`.

1. Create or reuse the shipping branch.
2. Commit only the final audited scope.
3. Confirm no unrelated changes entered the commit.
4. Confirm the working tree is clean.
5. Record the exact `HEAD` SHA.

Do not push yet.

## Final exact-HEAD ship gate

Follow Gate 2 in `shipping-gate.md`.

For a valid adapter, run exactly:

```text
./scripts/verify ship --base <resolved-base>
```

Require exit `0`, no contradictory output, unchanged `HEAD`, and an unchanged
clean working tree for the exact committed SHA. For an absent adapter, use the
preserved legacy final validation behavior.

This is the mandatory authoritative repository gate. It normally runs once per
final committed candidate. Any corrective edit after it fails or any later
commit invalidates the result and requires targeted validation, independent
re-audit, recommit, and another final ship run.

If the final gate fails:

- do not push;
- do not create or update a PR;
- do not file tracking issues;
- do not merge;
- retain the local commit and report the failure.

Read-only PR-body and report drafting may overlap with the final ship command,
but no remote or repository mutation may occur until the gate passes.

## Deferred-finding tracking, GitHub, and PR

Only after the final gate passes, follow the remaining sections of
`github-and-pr-policy.md`. After the branch is pushed, complete the mandatory
tracking gate before creating or updating a PR or merging:

1. For every confirmed P2/P3, search for an actually equivalent open issue.
2. Reuse the open issue or create a new issue; a closed issue is context, not
   active tracking.
3. Link every finding to an open issue. Closely related P3s may share one issue
   only when they form one root cause and one objectively closeable scope.
4. If GitHub is unavailable, issue creation fails, or any confirmed P2/P3 lacks
   an open issue link, stop with `TRACKING BLOCKED`. Do not mutate the PR or
   merge.

Do not let individual parallel lanes create issues. The authoritative synthesis
owns deduplication, issue equivalence, and the final tracking ledger.

## CI, merge, and cleanup

Follow `ci-and-merge-policy.md` without changing repository-specific merge
exceptions or authorizations.

Determine and report separately:

- testing confidence;
- CI enforcement confidence;
- final merge eligibility.

A documented accepted repository-wide CI architecture limitation may leave
testing confidence High while CI enforcement confidence is Moderate. Apply the
repository's merge policy; do not globalize another repository's exception.

Automatic merge is stricter than repository verification or PR eligibility.
After GitHub confirms merge, cleanup is mandatory: update the default branch,
prove the feature branch is merged, delete only safely merged branches, and
preserve unrelated work.

## Final report

Use `report-format.md`. Keep preflight, parallel audit execution, evidence
reconciliation, final Repository Verification, independent audit, testing, CI,
PR, merge, and cleanup as separate sections.
