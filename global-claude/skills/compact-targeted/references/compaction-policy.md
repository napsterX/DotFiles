# Compaction Policy

## When targeted compaction is appropriate

Use targeted compaction when all of these are true:

- the same coherent task will continue;
- the current reasoning direction remains valid;
- repository state can be summarized precisely;
- no major independent-review boundary is being crossed;
- the session has not accumulated severe contradiction or repeated lossy
  compactions.

Use `/handoff` followed by `/clear` instead when:

- changing tasks or tickets;
- changing from implementation to independent review;
- changing major architecture phases;
- the conversation contains contradictory instructions;
- several compactions have already occurred;
- resuming after a long interruption;
- clean reconstruction is safer than continuity.

## Preservation priority

Preserve in this order:

1. Objective and observable definition of done
2. Current user requirements and constraints
3. Current repository state and relevant files
4. Decisions, invariants, and boundaries
5. Unresolved failures and blockers
6. Validation evidence still applicable to the current tree
7. Rejected approaches likely to be repeated
8. Exact next action

## Discard priority

Discard:

- repeated explanations;
- completed exploration;
- raw logs already reduced to a result;
- full diffs when file paths and behavior are enough;
- superseded plans;
- unrelated side questions;
- generic background knowledge available in project docs;
- implementation details that no longer affect a decision.

## Loss controls

- Keep permanent standards in `CLAUDE.md` or tracked contracts rather than the
  anchor.
- Keep active-task state in the anchor rather than expanding permanent memory.
- Mark stale validation instead of preserving it as passing evidence.
- Preserve exact error text only when it is needed to identify the unresolved
  failure; otherwise preserve a concise diagnosis and reproduction command.
- After compaction, verify branch, HEAD, changed files, and next action before
  editing.
