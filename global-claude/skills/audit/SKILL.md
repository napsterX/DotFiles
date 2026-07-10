---
name: audit
description: Audit the most recent implementation against its original request without making any code changes - inspects changed files, tests, docs, and behavior, then reports PASS / PASS WITH GAPS / FAIL with prioritized findings. Use when the user asks to audit, verify, sanity-check, or double-check a completed implementation against what was originally asked, wants a second opinion before merging, or invokes /audit.
user-invocable: true
---

# Audit

Audit the last implementation against the original task/request.
This is a read-only sanity check, not a code-review-and-fix loop: inspect,
judge, report. Never assume the implementation is correct because it exists,
because tests were reportedly run, or because a prior turn claimed success.

## Ground rules

- **Do not make code changes.** Read-only, end to end. If you spot a fix,
  name it as a finding - do not apply it.
- **Do not assume the implementation is correct.** Verify claims made in
  commit messages, PR descriptions, or prior conversation turns by reading
  the actual diff and running the actual checks yourself, rather than taking
  them at face value.
- Inspect the changed files, the tests, the docs, and the actual runtime
  behavior where feasible - not just the diff in isolation.

## 1. Establish the original objective

Find what was actually asked, in this order:

1. The conversation context, if this skill is invoked in the same session
   that did the work.
2. The PR description or linked issue, if the change is already on a branch
   with a PR open.
3. The most recent commit message(s) on the branch, if neither of the above
   is available.
4. If none of these give a clear objective, ask the user directly rather
   than guessing - an audit against a guessed objective is worthless.

## 2. Establish what changed

Default to `git diff` against the merge-base with the repo's default branch
(detect whether it's `main` or `master`). If the user names a specific
commit range, PR, or file set, use that instead. Read the full diff, not
just the file list - a summary built from filenames alone misses behavior
changes.

## 3. Work the checklist

1. What was the original objective?
2. What changed?
3. Does the implementation actually satisfy the objective?
4. Are there missing requirements?
5. Are there unintended behavior changes?
6. Are there duplicated patterns, dead code, or shortcuts?
7. Are security/privacy/auth/data-boundary concerns still respected?
8. Are tests sufficient for the changed behavior?
9. Are docs/contracts updated if needed?
10. Are there regressions or risky assumptions?

## 4. Run validation, if appropriate

Detect what this repo actually has before running anything - check
`package.json` scripts, a `Makefile`, or the project's own contributing docs,
rather than assuming a fixed command set. Typical categories, run whichever
exist:

- typecheck
- lint
- unit tests
- static tests
- build
- a targeted browser/e2e test, only if the change affects UI or workflow
  behavior

Mark a category `NOT APPLICABLE` when the repo has no such check at all, not
`NOT RUN` - `NOT RUN` is reserved for a check that exists but was skipped or
could not be executed.

## 5. Report

Output in exactly this format, nothing above or below it except a one-line
flag if something blocked the audit itself (e.g. the original objective
couldn't be determined and the user didn't answer):

```
IMPLEMENTATION AUDIT RESULT

Verdict:
PASS / PASS WITH GAPS / FAIL

Original Objective:
<one paragraph>

Implemented Changes:
<bullet list>

Requirement Coverage:
- Requirement 1: PASS / GAP / FAIL
- Requirement 2: PASS / GAP / FAIL
- Requirement 3: PASS / GAP / FAIL

Findings:
P0:
- <must-fix blocker, if any>

P1:
- <must fix before merge/launch, if any>

P2:
- <should fix soon, if any>

P3:
- <polish/docs/follow-up, if any>

Tests / Validation:
- typecheck: PASS / FAIL / NOT RUN / NOT APPLICABLE
- lint: PASS / FAIL / NOT RUN / NOT APPLICABLE
- unit: PASS / FAIL / NOT RUN / NOT APPLICABLE
- static: PASS / FAIL / NOT RUN / NOT APPLICABLE
- build: PASS / FAIL / NOT RUN / NOT APPLICABLE
- browser/e2e: PASS / FAIL / NOT RUN / NOT APPLICABLE

Risk Assessment:
<low / medium / high, with reason>

Recommended Action:
MERGE / FIX FIRST / SPLIT FOLLOW-UP / REVERT
```

List only the requirements that actually apply to this change under
Requirement Coverage - do not pad to three if there are two, and do not
merge distinct requirements together just to hit a count.
Omit a Findings priority section entirely (not "- none") when it has nothing
in it.

If fixes are needed, end the report with the smallest safe follow-up prompt
that addresses only the gaps - not a rewrite of the whole task.
