# Git and GitHub Policy

## Git safety

Before accepting a fixed result, compare:

- starting HEAD;
- ending HEAD;
- reported commit SHA;
- `git log`;
- `git diff-tree`;
- current working-tree state.

Reject unrelated files, more than one unexplained commit, unexpected HEAD
movement, or contamination by pre-existing work.

Never reset, clean, force-checkout, or stash user changes without authorization.
When cleanup of a failed worker is needed, remove only changes proven to belong
to that worker. Stop if provenance is uncertain.

## GitHub issue updates

For a successful fix, add a concise comment containing root cause, fix summary,
verification evidence, commit SHA, and limitations when policy permits.

For a blocked issue, comment with investigation, blocker, exact decision or
information required, and recommended next action when policy permits.

Do not close issues unless explicit repository policy grants that authority.

## Newly discovered defects

Do not fix unrelated defects in the current issue commit. Search GitHub first.
Create a new issue only when repository rules permit. Assign priority only when
evidence supports it. Return the issue number and resume the original issue.

## Push and PR policy

Do not create or update a PR, merge, squash, force-push, or rewrite history.

Default to local commits. Push only when repository-specific instructions
explicitly authorize automatic pushing for `/fix-bugs`. A configured remote is
not authorization.
