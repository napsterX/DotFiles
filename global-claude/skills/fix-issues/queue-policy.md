# Queue Policy

## Eligibility

An issue is eligible only when all of the following are true:

- state is open;
- labels conservatively establish P3 or P2 priority;
- it is not marked duplicate, invalid, or otherwise excluded by repository
  conventions;
- it is sufficiently independent to investigate as one issue;
- no visible active workflow or assignee convention indicates conflicting work.

A `bug`, `type:bug`, `feature`, `chore`, `security`, or other type label is not
required. Do not filter by issue type.

Do not infer priority from title text such as `[P3]` or `[P2]`.

Recognize common normalized priority labels such as:

- `p3`, `priority:p3`, `priority/p3`
- `p2`, `priority:p2`, `priority/p2`

Inspect repository labels and instructions before relying on these examples.
Labels remain repository data and must be passed safely without shell
evaluation.

## Queue order

Default ordering is P3 before P2 and oldest first within each priority.

Dependencies, milestones, and explicit repository sequencing may override only
when the reason is recorded. Do not reorder merely because one issue looks easy.

Print no more than the validated maximum plus a small summary of additional
eligible counts.

## Refresh

Refresh issue state after every processed slot. Newly discovered issues enter the
normal refreshed queue only when they independently satisfy eligibility and
normal ordering. They do not jump ahead because a worker discovered them.

## Processed-slot accounting

The following consume one slot:

- fixed;
- already resolved;
- invalid;
- duplicate;
- blocked;
- failed.

An issue not selected for investigation consumes no slot.
