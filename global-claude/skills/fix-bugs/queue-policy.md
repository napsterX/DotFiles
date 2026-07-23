# Queue Policy

## Eligibility

An issue is eligible only when all of the following are true:

- state is open;
- labels conservatively establish that it is a bug;
- labels conservatively establish P2 or P3 priority;
- it is not marked duplicate, invalid, or otherwise excluded by repository
  conventions;
- it is sufficiently independent to process;
- no visible active workflow or assignee convention indicates conflicting work.

Do not infer eligibility from title text such as `[P2]`.

Recognize common normalized bug labels such as:

- `bug`
- `type:bug`
- `type/bug`
- `kind:bug`

Recognize common normalized priority labels such as:

- `p2`, `priority:p2`, `priority/p2`
- `p3`, `priority:p3`, `priority/p3`

Inspect repository labels and instructions before relying on these examples.
Labels remain repository data and must be passed safely without shell evaluation.

## Queue order

Default ordering is P2 before P3 and oldest first within each priority.

Dependencies, milestones, and explicit repository sequencing may override only
when the reason is recorded. Do not reorder merely because one issue looks easy.

Print no more than the validated maximum plus a small summary of additional
eligible counts.

## Refresh

Refresh issue state after every processed slot. Newly discovered issues enter the
normal refreshed queue only when they independently satisfy eligibility and
normal ordering. They do not jump ahead because the worker discovered them.

## Processed-slot accounting

The following consume one slot:

- fixed;
- already resolved;
- invalid;
- duplicate;
- blocked;
- failed.

An issue not selected for investigation consumes no slot.
