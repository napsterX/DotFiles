# Worktree Execution Policy

`/audit-and-pr` may audit a branch that is checked out in the current checkout,
a Claude Code-managed worktree, or an externally created Git worktree. A valid
external worktree is not an error and must not be copied into a second managed
worktree merely to satisfy a Claude Code switching tool.

## Resolve and pin the audited worktree

Before reading the implementation diff or running any audit, Git, verification,
GitHub, remediation, PR, merge, or cleanup operation:

1. enumerate registered worktrees with `git worktree list --porcelain`;
2. identify the one worktree that contains the audited branch and objective;
3. verify it belongs to the expected Git common directory;
4. canonicalize its path and pin it as `TASK_ROOT`;
5. record the invocation checkout separately as `INVOCATION_ROOT`;
6. record the target branch, target HEAD, Git common directory, and execution
   mode in the audit packet.

Use `scripts/worktree_context.py` when executable helpers are available.

If the target worktree or branch is ambiguous, unregistered, belongs to another
repository family, or cannot be proven, stop with `AUDIT BLOCKED`. Never guess.

## Execution modes

### Current checkout

When `TASK_ROOT` is the current worktree, run normally while still binding every
command and file operation to the pinned root.

### Claude Code-managed worktree

A worktree below the repository's `.claude/worktrees/` directory may use the
Claude Code `EnterWorktree` tool when that is useful and supported. Switching is
optional; pinning `TASK_ROOT` and operating directly remains valid.

### External registered Git worktree

For a sibling or otherwise external registered worktree, such as:

```text
/Users/name/git/project-issue-123
```

never call `EnterWorktree`. Claude Code restricts that tool to its own managed
worktrees and the call produces a predictable, avoidable error.

Instead:

- retain the current session checkout;
- pin the external absolute path as `TASK_ROOT`;
- run Git commands with argument separation, for example
  `git -C "$TASK_ROOT" status`;
- run repository scripts with the command tool's working directory set to
  `TASK_ROOT`;
- read and write files using absolute paths below `TASK_ROOT`;
- pass `TASK_ROOT` to deterministic helpers;
- bind every audit packet, validation result, commit, push, PR head, merge, and
  cleanup assertion to the target worktree's HEAD, not the invocation checkout.

Do not use unsafe `eval`, command-string interpolation, or an unquoted shell
`cd`. Prefer tool-native working-directory parameters or argument arrays.

## Cross-worktree safety

Before any mutation, prove:

- `TASK_ROOT` remains registered;
- it still belongs to the expected Git common directory;
- the expected branch remains checked out there;
- its HEAD has not moved unexpectedly;
- unrelated worktrees and the invocation checkout remain outside the audited
  mutation boundary.

Exactly one remediation writer may mutate `TASK_ROOT`. Parallel audit lanes are
read-only and may inspect the same pinned root or immutable packet.

A baseline-restoration base reproduction may use a separate detached worktree.
Pin it independently as `BASELINE_ROOT`; never switch the active session into it
and never confuse its evidence with `TASK_ROOT` evidence.

## Cleanup

After merge, cleanup must operate on the same registered target worktree and PR
target branch that were audited. Never delete or remove the invocation checkout,
an unrelated worktree, or an external worktree merely because `EnterWorktree`
was unavailable. Remove a target worktree only when repository policy authorizes
it, it is clean, its branch is proven merged, and no user work would be lost.

## Reporting

Report:

```text
Worktree Execution:
- Invocation root:
- Task root:
- Git common directory:
- Target branch:
- Initial target HEAD:
- Worktree class: CURRENT / CLAUDE_MANAGED / EXTERNAL_REGISTERED
- Execution mode: IN_PLACE / ENTERWORKTREE / PINNED_TASK_ROOT
- EnterWorktree attempted: YES / NO
- Cross-worktree safety: PASS / BLOCKED
```
