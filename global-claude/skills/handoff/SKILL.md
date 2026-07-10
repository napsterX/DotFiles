---
name: handoff
description: Capture the full context of the current session into a HANDOFF.md file in the repo so a future session can resume with complete context. Use when the user runs /handoff, asks to create a handoff, save session context, write a session summary, or prepare to continue work in a new session.
---

# Handoff

Write a complete, self-contained handoff of the **current session** to a file in the repo so a brand-new session (which has zero memory of this conversation) can resume with full context.

The reader of this file is a future Claude session with **no access to this conversation**. Assume it knows nothing. Every fact it needs to continue must be written down explicitly. Err heavily toward over-including context - a handoff that is too detailed costs a few extra tokens; one that is too thin loses the session.

## Step 1: Gather the objective repo state

Run these to capture ground truth (don't rely on memory for git state):

```bash
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
echo "ROOT=$ROOT"
git -C "$ROOT" branch --show-current 2>/dev/null
git -C "$ROOT" status --short 2>/dev/null
git -C "$ROOT" log --oneline -10 2>/dev/null
git -C "$ROOT" diff --stat 2>/dev/null
```

If not in a git repo, use the current working directory as `ROOT` and note that it's not a git repo.

## Step 2: Reconstruct the session context

Look back over the **entire current conversation** and extract everything a successor would need. Be thorough and specific - name real files, real paths, real commands, real function/symbol names. Cover at least:

- **The objective** - what the user is ultimately trying to accomplish (the goal behind the tasks, not just the last request).
- **What was done this session** - concrete changes, in order: files created/edited, what changed in each and why.
- **Current state** - what works and is verified, what is half-done, what is broken or untested.
- **Key decisions and their rationale** - choices made and the reasoning/tradeoffs, so they aren't relitigated or accidentally reversed.
- **Open items / next steps** - the ordered TODO list to pick up next, as concrete actions.
- **Gotchas** - environment quirks, non-obvious commands, things that failed and why, dead ends already ruled out, pitfalls to avoid.
- **User preferences expressed this session** - anything about how the user wants things done that came up in conversation.
- **Anything in flight** - partially applied edits, pending validations, unanswered questions for the user.

## Step 3: Write the handoff file

Write to **`$ROOT/HANDOFF.md`** (repo root). Overwrite any existing `HANDOFF.md` - it always represents the latest handoff. Use the current date from the environment context for the heading (do not run a date command; the conversation context provides today's date).

Follow the user's global Markdown style: put each full sentence on its own line, and never use the em dash character (use a plain dash).

Use exactly this structure, filled with real content (not placeholders). Omit a section only if it genuinely has nothing:

```markdown
# Session Handoff - <YYYY-MM-DD>

## Resume Here
<Two or three sentences: where things stand right now and the single most important next action. This is what the next session reads first.>

## Objective
<The overarching goal this work serves.>

## Current State
- Repo root: <path>
- Branch: <branch>
- Working tree: <clean, or summary of uncommitted changes>
- Verified working: <what has been confirmed to work>
- Not yet done / broken: <what is incomplete or failing>

## Work Completed This Session
<Ordered list of concrete changes, each with the file path and what/why.>

## Key Files and Locations
<Bulleted map of the files that matter, each with a one-line description of its role.>

## Decisions and Rationale
<Each significant decision and why it was made, including tradeoffs and rejected alternatives.>

## Open Items / Next Steps
<Ordered, concrete TODO list for the next session.>

## Gotchas and Notes
<Environment quirks, exact commands to run, things that failed and why, dead ends already ruled out.>

## How to Resume in a New Session
Paste this into the new session:

> Read HANDOFF.md at the repo root and load the context from the previous session.
> Do not resume, continue, or start implementing any task yet - just confirm you've read it and give me a short summary of where things stand.
> I will tell you what to work on next.
```

## Step 4: Confirm

Tell the user:
- The path that was written (`$ROOT/HANDOFF.md`).
- The exact resume prompt they can paste into the next session (the "How to Resume" block).
- A note that `HANDOFF.md` is tracked by git status - if they don't want it committed, they can add it to `.gitignore` (offer to do this, don't do it unprompted).

## Notes

- Do not commit or push anything. Just write the file.
- This is a snapshot of the current session only. It is not meant to accumulate history - each run overwrites the previous handoff.
- **The resume prompt is context-only by default - never an instruction to act.** A new session has no memory of this one, so any wording like "continue where the previous session left off" or a bundled "next task" reads as a command to immediately resume implementation, not as a request to load context. The whole point of this skill is capturing context for the user to decide what happens next - the new session should read the file, confirm it understood, summarize the state back, and then wait. Do not restore the old pattern of folding "continue with <task>" into the resume prompt, even if it seems convenient for a specific handoff - that regresses this exact bug.
- If the user asks for a differently named or located file (for example a timestamped archive under `.claude/`), honor that instead of the default.
