# Git and GitHub Policy

## Git safety

The batch requires a clean task worktree at start and between issues.

For each issue, compare:

- issue starting HEAD;
- candidate HEAD, which must remain unchanged before commit;
- accepted commit SHA;
- `git log`;
- `git diff-tree`;
- current working-tree state.

Reject unrelated files, more than one retained issue commit, unexpected HEAD
movement, or contamination by prior work.

Never stash, broad-clean, force-checkout, or discard user changes. Current-issue
cleanup is allowed only under the exact checkpoint rules in
`verification-and-retry-policy.md`.

## One retained commit per fixed issue

One verified issue maps to one retained logical commit. Attempts remain
uncommitted until accepted. Do not keep failed-attempt commits, cleanup commits,
or one commit per tiny edit.

Multiple issue commits are expected across the batch because they preserve
isolation, rollback, GitHub traceability, and final audit evidence. Do not squash
them inside `/fix-issues`.

## GitHub issue updates

For a successful candidate after commit, add a concise comment containing root
cause, fix summary, verification evidence, commit SHA, and that final
`/audit-and-pr` review is pending when repository policy permits.

For a blocked issue, comment with investigation, blocker, exact decision or
information required, and recommended next action when policy permits.

Do not close issues unless explicit repository policy grants that authority.
The final PR and post-merge issue disposition belong to `/audit-and-pr`.

## Newly discovered issues

Do not fix unrelated gaps in the current issue candidate. Search GitHub first.
Create a new issue only when repository rules permit. Assign priority only when
evidence supports it. Return the issue number and resume the original issue.

## Push and PR policy

Do not create or update a PR, merge, squash, force-push, or rewrite history.

Default to local commits until finalization. Push before `/audit-and-pr` only
when repository-specific instructions explicitly authorize this exact workflow.
A configured remote is not authorization.

Final push, PR generation, CI, merge disposition, issue reconciliation, and
branch cleanup are owned exclusively by `/audit-and-pr`.
