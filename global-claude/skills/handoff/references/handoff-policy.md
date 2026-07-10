# Handoff Policy

## Purpose

A handoff is an explicit operational checkpoint that lets a new Claude Code
context reconstruct the task from evidence. It is not a transcript summary,
status update, retrospective, or permanent architecture document.

## Authority order

When sources conflict, use this order:

1. Current repository and filesystem state
2. Current authoritative tracked contracts and task records
3. Current command output
4. Validated external execution state
5. Conversation statements
6. Inference

A handoff must expose conflicts instead of silently choosing the most convenient
story.

## Required evidence discipline

### VERIFIED

Use only when the claim was confirmed from current state during this handoff.
Examples:

- current branch and HEAD;
- current changed files;
- a requirement present in a tracked task document;
- a test result rerun during handoff;
- a file that currently contains the described implementation.

### SESSION EVIDENCE

Use for identifiable evidence from the active conversation that was not rerun.
Include the command and result when known. Do not convert "Claude said tests
passed" into verified evidence unless the underlying output is visible and
specific.

### INFERRED

Use when the claim follows from evidence but was not directly checked. State the
basis and what would verify it.

### UNKNOWN

Use when the state cannot be established. Unknowns belong in blockers,
uncertainty, or next actions; never fill them with plausible guesses.

## What to preserve

Preserve only state needed to continue safely:

- objective and definition of done;
- remaining requirements;
- current implementation state;
- changed files and their role;
- decisions and invariants;
- validation evidence and limitations;
- unresolved failures and blockers;
- rejected approaches likely to be repeated accidentally;
- exact next action;
- minimum relevant files to read.

## What not to preserve

Do not preserve:

- repeated conversation;
- brainstorming that was superseded;
- generic explanations of tools;
- complete logs;
- complete diffs;
- speculative future work unrelated to the active objective;
- permanent project standards already present in `CLAUDE.md` or tracked docs;
- credentials, tokens, private keys, cookies, or secret values.

## Validation evidence rules

For each validation item record:

- exact command or procedure;
- result;
- evidence class;
- code state or commit when known;
- whether later edits may have invalidated it;
- what risk or requirement it covers.

A passing build does not prove runtime behavior. A unit suite does not prove an
external integration. A prior test result does not remain valid after relevant
code changes.

## Next-action standard

The next exact action must be one bounded operation such as:

- inspect a named file and reconcile a named contradiction;
- implement a named requirement in named files;
- reproduce a named failure with a specific command;
- rerun a named validation invalidated by later changes;
- review a named diff against a named contract.

"Continue implementation", "finish the task", and "run tests" are not exact
actions.
