# Handoff Policy

## Core invariant

A successful handoff is the exact latest verified recovery artifact for the
actual task worktree. Publication, selection, and repository identity must agree.

## Identity model

Record and distinguish:

1. invocation directory;
2. repository family, derived from Git's canonical common directory;
3. active task worktree, derived from its canonical top-level real path;
4. branch and full HEAD;
5. handoff ID and content digest.

Linked worktrees belong to one repository family but may have different branches
and HEADs. `$PWD` is evidence, not authority. If the active worktree is ambiguous,
stop.

## Authority order

1. Current state in the resolved task worktree
2. Current tracked contracts and task records
3. Current command output
4. Validated external execution state
5. Conversation evidence
6. Inference

## Publication contract

Publishing must atomically write matching current Markdown, current metadata,
archive Markdown, archive metadata, and latest pointer. It must then prove:

- matching handoff IDs;
- matching content hashes;
- matching repository family and active worktree;
- unchanged branch, HEAD, and status during publication;
- successful lookup through the resume discovery path.

A file-write success without this proof is a failed handoff. The helper's
`draft-path` operation must return a unique path that does not yet exist; it must
not create an empty placeholder that forces Claude Code to read before writing.

## Completeness since prior checkpoint

Before publication, compare the previous handoff state with the current task
worktree. Account for all commits, changed files, task transitions, and validation
changes since the previous checkpoint. Never publish a narrative whose central
claims already contradict the current tree.

## Evidence labels

- **VERIFIED**: confirmed from current task-worktree or filesystem state now.
- **SESSION EVIDENCE**: visible evidence from this session not rerun now.
- **INFERRED**: reasoned conclusion requiring verification.
- **UNKNOWN**: unresolved.

## Validation evidence

Record exact command/procedure, result, evidence class, code state, and coverage
limits. Prior results do not apply after relevant changes.

## Next action

The next exact action must be one bounded operation. "Continue", "finish", and
"run tests" are not acceptable.
