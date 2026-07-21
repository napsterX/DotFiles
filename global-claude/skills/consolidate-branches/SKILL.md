---
name: consolidate-branches
description: Safely merge every other local branch into the current branch, require an explicit opt-in before snapshotting dirty work, validate the final committed tree with ./scripts/verify ship before push, then delete only local branches Git proves are fully merged.
argument-hint: "[dry-run|include-dirty]"
disable-model-invocation: true
user-invocable: true
---

# Consolidate Branches

Merge every other local branch into the branch currently checked out, validate
the resulting exact commit with the repository shipping gate, push the result
to `origin`, then delete only local branches Git proves are fully merged.

This is a personal Git-hygiene tool for repositories where the user is the sole
active author across the local branches. Do not use it in a repository with
other active contributors unless the user explicitly accepts that every local
branch will be folded into the current branch.

The skill runs autonomously after its safety gates clear. It stops rather than
guessing whenever state is ambiguous, a merge conflicts, verification fails,
or a push is rejected.

## Arguments

```text
$ARGUMENTS
```

Supported values:

- empty — require a clean working tree, then consolidate;
- `dry-run` — perform read-only inspection, print the exact plan, and stop;
- `include-dirty` — explicitly permit a scoped snapshot commit of all current
  pending changes before consolidation.

Reject any other argument.

## Non-negotiable safety rules

- Never force-push.
- Never bypass a Git hook with `--no-verify`.
- Never delete a branch with `git branch -D`; use only `git branch -d`.
- Never delete the current branch, the configured default branch, `main`,
  `master`, `develop`, or `trunk`.
- Never delete or modify a remote branch. Remote cleanup is out of scope.
- Never use `-X ours`, `-X theirs`, or another merge strategy that can silently
  discard one side.
- On the first conflict, run `git merge --abort`, stop the entire workflow, and
  report the branch and conflicted files.
- Never create a snapshot commit from a dirty tree unless the exact argument is
  `include-dirty`.
- Never snapshot likely secrets, credentials, private keys, local environment
  files, or unrelated generated artifacts merely because `include-dirty` was
  supplied.
- Do not let an automated commit carry a `Co-Authored-By` trailer. Remove it
  before any push.
- Stop when the directory is not a Git work tree or `HEAD` is detached.
- Never push before the exact final committed SHA passes
  `./scripts/verify ship` and the working tree remains clean.

## Procedure

### 1. Establish repository state

Run:

```bash
git rev-parse --is-inside-work-tree
git branch --show-current
git status --porcelain
git branch --format='%(refname:short)'
git remote get-url origin 2>/dev/null
```

Stop if this is not a Git work tree or the current branch is empty.

Record:

- `current` — the branch receiving all merges;
- `others` — every local branch except `current`;
- `dirty` — whether status printed anything;
- `has_remote` — whether `origin` resolves;
- `default_branch` — resolve from
  `git symbolic-ref refs/remotes/origin/HEAD` when possible.

If `dirty` is true and the argument is empty, stop with a precise report and
instruct the user to clean the tree or rerun with `include-dirty`.

### 2. Inspect dirty scope when explicitly included

When the argument is `include-dirty`, print every staged, unstaged, deleted, and
untracked path.

Stop instead of committing when any path or visible diff indicates likely:

- `.env` or local secret files;
- credentials, tokens, private keys, certificates, or key stores;
- machine-local configuration;
- large build output, caches, logs, or temporary artifacts;
- unrelated work that cannot be described as one coherent snapshot.

Do not use broad secret scanning as proof of safety. This is a bounded sanity
check before the explicit snapshot operation.

### 3. Print the plan

Before mutation, report:

- current branch;
- other local branches in merge order;
- dirty-tree state and snapshot decision;
- remote availability;
- protected branch names;
- required final verification command: `./scripts/verify ship`.

If the argument is `dry-run`, stop here.

### 4. Snapshot explicitly included pending work

Only when `dirty` is true and the argument is `include-dirty`, run:

```bash
git add -A
git commit -m "chore: snapshot pending work before branch consolidation (<N> files)"
```

Compute `<N>` from the pre-commit status path count.

Verify the commit contains exactly the disclosed pending paths and no
`Co-Authored-By` trailer. Amend locally before push if the trailer exists.

If the commit fails, stop.

### 5. Merge every other local branch

For each branch in alphabetical order, run:

```bash
git merge --no-edit <branch>
```

Record clean merges, fast-forwards, and already-up-to-date branches.

On conflict:

1. record conflicted paths;
2. run `git merge --abort`;
3. verify the tree returned to its pre-merge state;
4. stop without further merges, verification, push, or deletion.

### 6. Validate the exact committed result

Require a clean tree and record:

```bash
git rev-parse HEAD
git status --porcelain
```

The repository must contain executable `./scripts/verify` with a `ship`
profile. Run exactly:

```bash
./scripts/verify ship
```

Stop before push and deletion when:

- the script is missing or not executable;
- the `ship` profile is unavailable;
- the command exits non-zero, is interrupted, or cannot be established;
- `HEAD` changes;
- staged, unstaged, or untracked changes appear.

Report the retained local SHA and verification evidence. Do not repair the
repository inside this workflow.

### 7. Push the current branch

If no `origin` exists, skip push and continue to local cleanup only after the
ship gate passed.

If an upstream exists, run `git push`. Otherwise run:

```bash
git push -u origin <current>
```

If the push fails, stop and do not delete any branches.

### 8. Delete only fully merged local branches

Run:

```bash
git branch --merged <current>
```

Exclude:

- `<current>`;
- `main`, `master`, `develop`, and `trunk`;
- the resolved default branch.

Delete every remaining branch with:

```bash
git branch -d <branch>
```

If deletion of a branch is refused, leave it intact and report it. Never use
`-D`.

### 9. Final report

Report:

- current branch and final SHA;
- branches merged, already current, conflicted, or skipped;
- snapshot commit and included path count, when applicable;
- `./scripts/verify ship` result and verified SHA;
- push outcome;
- deleted and retained branches;
- final working-tree state;
- exact stopping reason when incomplete.
