# GitHub and PR Policy

## Branch

Run only after the audit eligibility gate clears.

- Reuse a suitable existing non-default branch.
- If changes are on the default branch, create a new branch.
- Follow repository branch conventions.
- Otherwise use a concise `feature/`, `fix/`, `refactor/`, `test/`, `docs/`, or
  `chore/` name.

## Commit

Commit only audited scope. Exclude unrelated changes and match repository commit
style.

### Original implementation uncommitted

Commit the final audited implementation coherently. Retained `FIX_NOW` repairs
may be included when separating them would require risky patch reconstruction.
Disclose all remediation.

### Original implementation committed

Commit retained `FIX_NOW` remediation separately. Do not rewrite history unless
explicitly required.

Never include code changes for findings dispositioned `DEFER_TO_ISSUE`,
`ADD_TO_EXISTING_ISSUE`, `BATCH_INTO_CLEANUP_ISSUE`, `ACCEPT_AS_LOW_VALUE`, or
`DISMISS`.

## Final verification boundary

After the scoped commit:

- verify the working tree is clean;
- record the exact committed SHA;
- for a valid adapter, run `./scripts/verify ship --base <resolved-base>`;
- for an absent adapter, preserve the legacy final validation workflow;
- in normal mode, stop on invalid adapter, failure, contradiction, timeout,
  interruption, HEAD change, or post-run tree change;
- for a `BASELINE_RESTORATION` candidate, permit final exit `1` only after the
  complete exact-HEAD ledger proves `FAILED_PRE_EXISTING_BASELINE`.

Push, issue tracking, PR summary, PR mutation, and merge are forbidden until the
exact current `HEAD` is `NORMAL_GREEN`, successful legacy `NOT_APPLICABLE`, or a
fully eligible `FAILED_PRE_EXISTING_BASELINE`.

## Push

Push without force. A `FAILED_PRE_EXISTING_BASELINE` classification permits push
only for the exact audited commit represented by the complete ledger.

If push fails, report and stop. Do not create tracking issues that claim a pushed
branch state when the push did not succeed.

## Finding disposition and issue-tracking gate

Only confirmed implementation findings participate. Never create issues for:

- audit-process notes;
- unconfirmed or unsupported speculation;
- a failed repository ship-gate attempt;
- repository-wide accepted limitations that are not per-change findings;
- findings dispositioned `ACCEPT_AS_LOW_VALUE` or `DISMISS`.

P0/P1 cannot satisfy acceptance through issue creation. They must be resolved or
remain `BLOCK_ACCEPTANCE`.

Only these dispositions require an equivalent open GitHub issue:

- `DEFER_TO_ISSUE`;
- `ADD_TO_EXISTING_ISSUE`;
- `BATCH_INTO_CLEANUP_ISSUE`.

A P2 or P3 with `FIX_NOW`, `ACCEPT_AS_LOW_VALUE`, or `DISMISS` does not require a
new issue merely because of severity.

Perform GitHub tracking only after authoritative synthesis. Parallel lanes must
not search, create, update, or label issues independently.

### Mandatory issue-creation gate

Before creating any new issue, prove:

1. the finding is actionable;
2. impact is material enough for permanent backlog;
3. open and relevant closed issues were searched;
4. the issue is one coherent outcome or shared root cause;
5. acceptance criteria are meaningful and verifiable;
6. the work is realistically likely to be scheduled;
7. deferral is safer or more efficient than bounded current remediation.

If any condition fails, do not create a new issue. Reconsider `FIX_NOW`,
`ADD_TO_EXISTING_ISSUE`, `BATCH_INTO_CLEANUP_ISSUE`, `ACCEPT_AS_LOW_VALUE`, or
`DISMISS` and explain the result.

### Equivalence and deduplication

For each issue-required finding:

1. Search open and relevant closed issues using normalized title, behavior,
   component, root-cause evidence, and acceptance outcome.
2. Reuse an open issue only when it objectively closes the same finding.
3. Do not reuse a broad epic or umbrella unless it contains an explicit,
   independently closeable child outcome.
4. Treat a closed issue as historical context, not active ownership.
5. Add evidence to an equivalent open issue rather than creating a duplicate.
6. Group repeated manifestations of one root cause into one issue.
7. Do not create one issue per file, line, typo, test gap, or cosmetic
   inconsistency when one shared remediation is appropriate.

`BATCH_INTO_CLEANUP_ISSUE` requires multiple related findings and one coherent,
prioritizable, objectively closeable outcome. List every grouped finding in the
issue and audit ledger.

### Default new-issue budget

For findings below P1, normally create no more than **three new issues per audited
change**. Reusing or updating existing open issues does not consume this budget.

Exceed the default only with an explicit explanation of:

- why each finding cannot be fixed now;
- why findings cannot be grouped;
- why existing issues cannot be used;
- why each new issue has independent value.

The budget never weakens P0/P1 handling and never permits material findings to be
hidden.

### Issue body

Include:

- stable audit finding identifier;
- severity and disposition;
- observed gap and impact;
- evidence and affected paths/components;
- why it was deferred rather than fixed now;
- proposed remediation;
- acceptance criteria;
- minimum validation plan;
- dependencies;
- audited branch and exact commit SHA;
- audit and PR origin when available;
- related, duplicate, or superseded issue references;
- repository-specific agent-routing classification only when that repository or
  installed policy already defines it.

Follow existing labels and ticket conventions. Do not invent a new taxonomy.
This update does not add a local/cloud routing scheme; preserve any existing
repository-specific routing labels without silently changing them.

### Tracking completion

Use `scripts/finding_disposition.py tracking` or equivalent logic to reconcile:

- findings with issue-required dispositions;
- findings linked to equivalent open issues;
- reused versus newly created issues;
- grouped mappings;
- new-issue budget and any documented exception.

Tracking is complete only when every issue-required disposition maps to an open
issue and the issue budget is satisfied or explicitly justified.

If GitHub is unavailable, search/update/create fails, an issue-required finding
lacks an open link, or the issue budget is exceeded without justification:

- set `TRACKING BLOCKED`;
- do not create or update the PR;
- do not merge;
- preserve the pushed branch if already pushed;
- report exactly what remains incomplete.

Do not modify code merely because tracking is unavailable.

## Baseline-restoration residual ownership

Before a restoration branch is pushed or a PR is created or updated, every
`UNCHANGED_TRACKED_BASELINE` and `PRE_EXISTING_NEWLY_UNMASKED` row must link to a
canonical open issue. A newly unmasked failure without an issue blocks. This
residual ownership requirement is separate from ordinary audit-finding
budgeting and cannot be dismissed as low value.

## PR change summary

Follow `pr-change-summary-policy.md` after issue-required tracking completes or
is not applicable.

Generate the managed PR block from the final audited diff and verified HEAD.
Include concrete Added, Changed, Fixed, and Removed entries; user-facing impact;
explicit breaking changes; retained remediation; deferred issue links; and a
concise disposition summary.

Do not use commit messages alone. Do not include unsupported claims, secrets,
private service details, customer data, or sensitive exploit guidance. Never
list deferred, accepted-low-value, or dismissed work as fixed.

For `FAILED_PRE_EXISTING_BASELINE`, include exact base/branch commands, commits,
environment, target repaired failure, full failure ledger, residual owners,
truthful nonzero result, scoped-exception statement, and manual-merge
requirement.

Detect an existing permanent changelog convention but do not invent one. The
presence of `CHANGELOG.md` alone does not authorize editing it.

## Existing PR

Do not create a duplicate. Update the body only after required tracking
completes. Preserve useful existing context outside managed markers. Replace the
single existing managed block. Duplicate or unmatched markers block mutation.

## New PR

Read the real template field by field, populate actual values, and use
`N/A — <reason>` only when genuinely inapplicable. Never leave unresolved
placeholders. Create the PR only after required tracking completes.

## Required PR content

Include:

- final-diff managed change summary;
- user-facing impact and breaking/operator actions;
- motivation and requirement coverage;
- impact and risk;
- tests, reused evidence, and newly executed evidence;
- testing and CI-enforcement confidence;
- planned-versus-executed reconciliation;
- deterministic preflight and final Repository Verification;
- parallel audit plan and authoritative verdict;
- full finding disposition table;
- remediated-now findings and evidence;
- deferred issue links, reused issues, and batched mappings;
- accepted low-value and dismissed counts with concise rationale;
- new-issue budget use and exception rationale when exceeded;
- exact committed SHA validated by the final gate;
- baseline-restoration evidence when applicable;
- permanent changelog convention and artifact status;
- rollback and repository-specific metadata;
- non-default integration-branch issue-reconciliation plan.

Do not imply reused evidence was freshly rerun.

## Rollback

State whether rollback is commit revert, config rollback, migration reversal,
data repair, or constrained by irreversible side effects.
