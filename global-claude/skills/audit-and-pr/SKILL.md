---
name: audit-and-pr
description: Run deterministic preflight, an independent risk-adaptive parallel audit, bounded P0/P1 remediation, P2/P3 tracking, final exact-HEAD verification, controlled BASELINE_RESTORATION comparison, PR generation, CI, merge gating, and cleanup. Accept direct user invocation or a validated fix-issues finalization manifest.
user-invocable: true
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

- `delegated-invocation-policy.md`
- `worktree-execution-policy.md`
- `repository-verification-policy.md`
- `baseline-restoration-policy.md`
- `parallel-audit-policy.md`
- `remediation-policy.md`
- `shipping-gate.md`
- `github-and-pr-policy.md`
- `pr-change-summary-policy.md`
- `ci-and-merge-policy.md`
- `report-format.md`

Executable references when helpers are supported:

- `scripts/delegated_invocation.py` — validation of trusted `/fix-issues` finalization manifests before model-initiated invocation;
- `scripts/worktree_context.py` — registered-worktree resolution, repository-family validation, and safe execution-mode classification;
- `scripts/repository_verification.py` — safe `doctor`, `fast`, and final `ship`
  invocation and evidence capture;
- `scripts/baseline_restoration.py` — exact failure-ledger classification and
  controlled `FAILED_PRE_EXISTING_BASELINE` eligibility;
- `scripts/workflow_plan.py` — required verification-stage ordering;
- `scripts/audit_parallelism.py` — automatic read-only lane selection;
- `scripts/shipping_decision.py` — separation of testing confidence, CI
  enforcement confidence, deferred-finding tracking, and merge eligibility;
- `scripts/finding_disposition.py` — severity-driven remediation and mandatory
  GitHub tracking decisions for confirmed P2/P3 findings;
- `scripts/pr_change_summary.py` — deterministic managed PR-summary rendering,
  safe existing-body replacement, and permanent-changelog action decisions.

## Invocation authorization

Direct user invocation is authorized through `/audit-and-pr` and the existing
`baseline-restoration` argument.

Model-initiated invocation is permitted only for finalization delegated by
`/fix-issues`. It must include a manifest satisfying
`delegated-invocation-policy.md`. Validate the manifest against live `TASK_ROOT`,
branch, and exact HEAD before deterministic preflight or any side effect.

Any other model-initiated invocation must stop as
`DELEGATED_INVOCATION_REJECTED`. Do not infer authorization merely because a
branch contains several issue commits or appears ready for review.

## Core guarantees

Never:

- imply Repository Verification exit `0` equals audit approval;
- run the full `ship` profile before the independent audit merely as a default;
- run `ship` after every remediation edit for ceremony;
- continue after a required deterministic preflight or final gate fails, is
  invalid, times out, is interrupted, mutates the repository, or contradicts its
  own success output, except that final `ship` exit `1` may enter the separate
  `baseline-restoration-policy.md` decision and only when every requirement is
  proven;
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
- generate a PR change summary from an earlier or unaudited HEAD;
- list deferred P2/P3 findings as fixed or omit their open issue links;
- overwrite user-authored PR content outside the managed change-summary block;
- invent or automatically introduce a permanent repository changelog convention;
- expose secrets, private service details, customer data, or sensitive exploit
  instructions in the PR summary;
- push or create/update a PR before the final exact committed HEAD either passes
  the normal repository-verification or legacy gate, or receives a complete
  `FAILED_PRE_EXISTING_BASELINE` classification under the narrow restoration
  policy;
- call a nonzero aggregate ship result green;
- infer baseline restoration merely because a check is red;
- use baseline restoration to bypass a new, unattributed, security, authorization,
  tenancy, migration, data-integrity, payment, destructive-operation, or privacy
  failure;
- auto-merge a baseline-restoration PR;
- merge through failed, cancelled, unresolved, or bypassed checks;
- bypass branch protection or approval;
- conceal auto-fixes;
- include unrelated work;
- use destructive Git cleanup;
- call `EnterWorktree` for an external registered Git worktree;
- create a duplicate Claude-managed worktree merely to bypass a switching-tool limitation;
- force-delete an unmerged branch.

## Progress updates

Provide concise milestone updates:

1. Objective, repository safety, scope, canonical base, and operating mode
   established.
2. Adapter state and deterministic preflight established, or legacy mode
   confirmed. For a restoration candidate, canonical-base reproduction and the
   preliminary failure ledger are established.
3. Risk, evidence plan, and parallel lane plan established.
4. Independent initial audit synthesized.
5. Severity disposition completed: P0/P1 remediation candidates and deferred
   P2/P3 tracking records established.
6. P0/P1 remediation validation and re-audit completed.
7. Audit eligibility gate cleared or blocked.
8. Final exact-HEAD ship or legacy verification passed, blocked, or was
   truthfully classified `FAILED_PRE_EXISTING_BASELINE` with a complete ledger.
9. Deferred P2/P3 and baseline-residual GitHub tracking completed or blocked.
10. Final-diff PR change summary and any required repository changelog artifact
    completed or blocked.
11. PR, CI, merge, and cleanup outcome determined.

Do not narrate every checklist item.

## Audit model

The initial audit and every re-audit use a pinned model and pinned reasoning
effort.

- Parse the reserved `baseline-restoration` token as operating mode, never as a
  model name. Any separate recognized model argument wins for audit model choice.
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

Follow `worktree-execution-policy.md` before any repository operation. Resolve
and pin one registered audited worktree as `TASK_ROOT`; record the session
checkout separately as `INVOCATION_ROOT`. Do not call Claude Code
`EnterWorktree` for an external sibling or otherwise externally managed Git
worktree. Operate directly against its absolute path using command working
directories and argument-safe `git -C` calls. A failed or unsupported switching
tool is not a reason to create a duplicate worktree.

Every read, diff, deterministic helper, audit packet, remediation edit,
validation command, commit, push, PR-head assertion, merge check, and cleanup
operation must remain bound to `TASK_ROOT`. Revalidate that registration, Git
common-directory identity, branch, and HEAD remain correct before mutations and
after asynchronous work.

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
- linked issue or ticket;
- repository PR template and permanent changelog or fragment convention.

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

## Select operating mode

Normal mode is the default. It preserves the ordinary rule that any required red
gate blocks shipment.

`BASELINE_RESTORATION` may be selected by:

```text
/audit-and-pr baseline-restoration
```

or inferred only when the canonical issue, implementation handoff, or
authoritative repository evidence clearly establishes incremental repair of an
already-red mandatory lane. A red result alone is never sufficient. State the
mode source (`EXPLICIT` or `INFERRED`), target failure, canonical base, and
authoritative lane before any remote mutation.

Selection creates only a candidate. Follow `baseline-restoration-policy.md` and
prove the complete base-versus-branch ledger before the exception can be used.
Reject unknown or multiple mode arguments.

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
5. In normal mode, stop before the deep audit on any required preflight failure,
   contradiction, timeout, interruption, HEAD change, or working-tree change.
6. In a proven restoration candidate, `doctor` must still pass. A `fast` exit `1`
   may be retained only as comparison evidence while the skill reproduces the
   same authoritative lane once on the untouched canonical base and once on the
   branch. Exit `2` through `5`, protocol defects, environment blockers, or
   repository mutation still block immediately.
7. Build the preliminary failure ledger and reject any new, unattributed,
   untracked, or protected-domain residual before spending the deep audit.
8. If the adapter is genuinely absent, record legacy mode and preserve existing
   repository-native validation discovery and behavior; the same restoration
   evidence burden still applies when a repository-native mandatory lane is used.

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
when the final exact audited commit passes the applicable ship gate, or receives
a complete `FAILED_PRE_EXISTING_BASELINE` classification, the tree stays clean,
no later commit appears, all change-relevant high-risk checks run, and planned
versus executed evidence reconciles. Report the aggregate gate truth, CI
enforcement, and repository-policy merge impact separately.

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
7. rerun the applicable audit lanes and authoritative synthesis;
8. when in `BASELINE_RESTORATION` and retained remediation changed files relevant
   to the failing lane or its verification machinery, rerun only the affected
   base/branch comparison and refresh the ledger. Do not sample intermittent
   reruns until favorable.

Do not run the full `ship` profile after each remediation round. An earlier ship
result, if one exists from outside this workflow, never authorizes the final
state.

## Audit eligibility gate

Follow Gate 1 in `shipping-gate.md`.

If blocked, leave retained safe P0/P1 local fixes uncommitted, report them, and
stop before branch, commit, push, issue, PR, merge, or cleanup operations.

Gate 1 may clear with confirmed P2/P3 findings only when each is genuinely
non-blocking, independently closeable, and represented by a complete issue-ready
record. In restoration mode, known residual gate failures are not unexplained
only when the complete ledger classifies them as
`UNCHANGED_TRACKED_BASELINE` or `PRE_EXISTING_NEWLY_UNMASKED`; every owner must be
an open canonical issue. Actual GitHub tracking is mandatory before PR mutation
or merge.

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

For normal shipment, require exit `0`, no contradictory output, unchanged
`HEAD`, and an unchanged clean working tree for the exact committed SHA. For an
absent adapter, use the preserved legacy final validation behavior.

This is the mandatory authoritative repository gate. It normally runs once per
final committed candidate. Any corrective edit or later commit invalidates the
result and requires targeted validation, independent re-audit, recommit, and
another final ship run.

When the final adapter exits `1`, do not call the gate green. In normal mode,
block exactly as before. In a restoration candidate, evaluate
`baseline-restoration-policy.md` against the exact final HEAD and complete
base-versus-branch ledger. Only a fully eligible result may be classified
`FAILED_PRE_EXISTING_BASELINE`, permitting push and PR creation while requiring
manual merge. Exit `2` through `5`, timeout, interruption, contradiction,
environment failure, HEAD change, or tree change always block.

If the final gate fails without a complete restoration classification:

- do not push;
- do not create or update a PR;
- do not merge;
- retain the local commit and report the failure;
- create no exception record that implies the gate passed.

Read-only PR-body and report drafting may overlap with the final ship command.
No push or PR mutation may occur until the final shipment classification permits
it. The only earlier remote action allowed in a restoration candidate is creating
an exact canonical issue required for a proven newly unmasked residual after the
independent audit and final exit `1`; re-evaluate eligibility immediately after.
Any draft is provisional until it is regenerated or confirmed against the final
audited HEAD and completed tracking ledgers.

## Deferred-finding tracking, GitHub, and PR

Only after the final shipment classification is `NORMAL_GREEN`,
`NOT_APPLICABLE`, or fully eligible `FAILED_PRE_EXISTING_BASELINE`, follow the
remaining sections of `github-and-pr-policy.md`. For a restoration candidate,
every baseline-residual owner must already be an open canonical issue before
push. If the final exit `1` reveals a proven newly unmasked failure without an
owner, the skill may create that exact issue after audit and before push, then
rerun the restoration decision; it may not mutate the PR or merge during that
step. After the branch is pushed, complete the normal deferred P2/P3 tracking
gate before creating or updating a PR or merging:

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

## Final-diff PR change summary

Follow `pr-change-summary-policy.md` after deferred-finding tracking is complete
or not applicable and before creating or updating the PR.

1. Generate one managed `Change summary` block from the final audited diff,
   objective, tests, retained P0/P1 remediation, and exact verified HEAD.
2. Categorize concrete changes as Added, Changed, Fixed, or Removed and omit empty
   categories.
3. State user-facing impact explicitly. Add a distinct Breaking changes section
   only when migration, deployment, configuration, API, schema, compatibility, or
   rollback action is required.
4. Include every confirmed deferred P2/P3 with its equivalent open GitHub issue
   link. Never describe deferred work as fixed.
5. Preserve repository-template and user-authored PR content outside the managed
   markers. Replace the existing managed block when updating a PR; block on
   duplicate or unmatched markers.
6. Regenerate the block whenever the final audited HEAD changes.
7. For `FAILED_PRE_EXISTING_BASELINE`, include the target repaired failure, exact
   base and branch reproduction, complete failure ledger, all residual owners,
   truthful nonzero aggregate ship result, no-new-failure statement, scoped
   exception statement, and manual-merge requirement.
8. Detect permanent changelog conventions conservatively. Use PR-body summary
   only when no repository requirement applies. Validate or create a permanent
   artifact only under explicit, deterministic repository policy; otherwise
   block with the exact manual action rather than inventing a convention.

Any required tracked changelog artifact must enter audited scope before the final
commit and ship gate. A tracked edit after final verification invalidates that
verification.

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

Automatic merge is stricter than repository verification or PR eligibility. A
`FAILED_PRE_EXISTING_BASELINE` PR is never auto-merged. When the PR target is a
non-default integration branch, reconcile issue closure manually after the user
or maintainer confirms merge; do not rely on closing keywords. After GitHub
confirms merge, cleanup is mandatory: update and verify the PR target branch,
prove the feature branch is merged into that target, delete only safely merged
branches, and preserve unrelated work. Do not substitute the GitHub default
branch when the PR targeted a non-default integration branch.

## Final report

Use `report-format.md`. Keep operating mode, preflight, baseline-restoration comparison and ledger,
parallel audit execution, evidence reconciliation, final Repository
Verification, independent audit, PR change summary and permanent changelog
handling, testing, CI, PR, merge, issue reconciliation, and cleanup as separate
sections.
