# GitHub and PR Policy

## Branch

Run only after the audit eligibility gate clears.

- Reuse a suitable existing non-default branch.
- If changes are on the default branch, create a new branch.
- Follow repository branch conventions.
- Otherwise use a concise `feature/`, `fix/`, `refactor/`, `test/`, `docs/`, or
  `chore/` name.

## Commit

Commit only audited scope.

Exclude unrelated changes.

Match repository commit style.

### Original implementation uncommitted

Commit the final audited implementation coherently. Retained eligible P0/P1
fixes may be included when separating them would require risky patch
reconstruction.

Disclose all remediation changes.

### Original implementation committed

Commit retained P0/P1 remediation separately.

Do not rewrite history unless explicitly required.

Never include code changes made solely to address P2/P3 findings. Those findings
must remain deferred and tracked.

## Final verification boundary

After the scoped commit:

- verify the working tree is clean;
- record the exact committed SHA;
- for a valid adapter, run `./scripts/verify ship --base <resolved-base>` as
  defined in `repository-verification-policy.md` and `shipping-gate.md`;
- for an absent adapter, preserve the legacy final validation workflow;
- stop on any invalid adapter, failure, contradiction, timeout, interruption,
  HEAD change, or post-run tree change.

The Push, Track deferred findings, Existing PR, and New PR sections below are
forbidden until the applicable final gate passes for the exact current `HEAD`.

## Push

Push without force.

If push fails, report and stop. Do not create tracking issues that claim a pushed
branch state when the push did not succeed.

## Mandatory deferred-finding tracking gate

Only confirmed implementation findings participate. Never create issues for:

- audit-process notes;
- unconfirmed speculation;
- a failed repository ship-gate attempt;
- repository-wide accepted limitations that are not per-change implementation
  findings.

P0/P1 findings cannot satisfy this gate through issue creation. They must already
be resolved or shipment remains blocked.

Every confirmed P2/P3 finding must map to an equivalent open GitHub issue before
PR creation/update or merge. There is no PR-only exception for confirmed P3
findings.

Perform tracking only after authoritative audit synthesis. Parallel audit lanes
must not search, create, or mutate issues independently.

### Equivalence and deduplication

For each confirmed P2/P3:

1. Search open issues using the normalized finding title, affected component,
   evidence terms, and acceptance criteria.
2. Reuse an open issue only when it represents the same defect or root cause and
   its acceptance criteria would objectively close the finding.
3. Do not reuse a broad epic, umbrella backlog, or vaguely related issue as the
   finding's tracking record unless it contains an explicit child task that
   closes the finding.
4. A closed issue is historical context, not active tracking. Create a new issue
   and reference the closed issue when the gap reappears.
5. Otherwise create a new issue.

Each P2 normally receives its own issue. Multiple P2 findings may share one issue
only when they are the same root cause and one atomic remediation unit.

Closely related P3 findings may share one issue only when they form one coherent,
independently prioritizable, objectively closeable scope. Every grouped finding
must be listed explicitly in the issue and in the audit tracking ledger.

### Issue body

Include:

- stable audit finding identifier;
- priority;
- concise observed gap;
- risk and why shipment is temporarily acceptable;
- evidence and affected paths/components;
- audited branch and exact commit SHA;
- acceptance criteria;
- minimum validation plan;
- audit and PR origin when available;
- related or superseded issue references.

Follow existing repository labels and ticket conventions. Do not invent a new
label taxonomy. If no matching severity label exists, record priority in the
title/body rather than blocking issue creation solely on labels.

### Tracking completion

Use `scripts/finding_disposition.py` or equivalent logic to reconcile:

- confirmed deferred finding count;
- findings linked to equivalent open issues;
- issue URLs;
- reused versus newly created issues;
- grouped-finding mappings.

Tracking is complete only when every confirmed P2/P3 maps to an open issue.

If GitHub is unavailable, issue search fails materially, issue creation fails, or
any confirmed P2/P3 remains without an open issue link:

- set status to `TRACKING BLOCKED`;
- do not create or update the PR;
- do not merge;
- preserve the pushed branch if already pushed;
- report exactly which findings remain untracked and why.

Do not change code merely because issue creation is unavailable.

## Existing PR

Do not create a duplicate.

Update the body only after the deferred-finding tracking gate completes. Preserve
useful existing context.

## New PR

Read the real template field by field.

Populate actual values.

Use `N/A — <reason>` when genuinely inapplicable.

Never leave unresolved placeholders.

Create the PR only after the deferred-finding tracking gate completes.

## Required PR content

Include:

- summary of behavioral changes;
- motivation;
- requirement coverage;
- impact and risk;
- tests and validation;
- reused versus rerun evidence;
- testing confidence;
- CI enforcement confidence and any documented repository-wide limitation;
- merge eligibility and repository-policy reason;
- planned-versus-executed evidence reconciliation;
- deterministic preflight summary, including any deliberate `fast` skip;
- parallel audit mode, lane count, and authoritative synthesis result;
- audit verdict;
- retained P0/P1 remediation;
- explicit statement that P2/P3 findings were not modified;
- final Repository Verification adapter/mode, explicit base, command, and result;
- exact committed SHA validated by the final gate;
- each deferred P2/P3 finding and its open GitHub issue link;
- rollback;
- repository-specific metadata.

Do not imply reused evidence was freshly rerun.

## Rollback

State whether rollback is:

- commit revert;
- config rollback;
- migration reversal;
- data repair;
- constrained by irreversible side effects.
