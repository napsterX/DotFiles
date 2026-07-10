# Manish's Agent Instructions

These are common instructions for Manish's agents across all scenarios.

## General Guidelines

- Never use the em dash character. Use a plain dash instead.
- When writing commit messages, never add yourself or any AI agent as a co-author.
- Never manually modify `CHANGELOG.md` files or any files marked as auto-generated.
- When writing or substantially editing long Markdown files, put each full sentence on its own line.
- Preserve normal Markdown structure, but avoid wrapping multiple sentences onto one physical line.
- When making technical decisions, do not give too much weight to developer convenience or short-term cost.
- Instead, prefer quality, simplicity, robustness, scalability, and long-term maintainability.
- When doing bug fixes, always start by reproducing the bug in a setting as close as possible to how an end user sees it.
- When end-to-end testing a product, be picky about the UI and care about polish, clarity, and pixel-level issues.
- If something clearly looks off, even if it is not directly related to the task, call it out and fix it when reasonable.
- If you see an obvious defect, even if it was not caused by the current task, do not silently ignore it.

## Shipping changes (no-mistakes)

- `no-mistakes` is a gate (review, tests, docs, lint, push, PR, CI) Manish runs manually when he wants to ship a feature branch. Do not run `/no-mistakes` automatically after finishing a change, and do not treat it as a required step unless he asks for it.
- Plain `git push` and opening a PR by hand are not blocked; use them directly when that is what the task calls for.
- When Manish does ask to run `no-mistakes`, it validates committed history on a feature branch, so commit the work on a non-default branch first, then run the gate; if the repository is not yet initialized, run `no-mistakes init` once.
- `no-mistakes` does not replace a repository's own mandatory commit governance. Where a repo requires its own handoff or session-close discipline before a commit (for example the Hachira implementation-log guard and session-close protocol), run those commit steps first; `no-mistakes` then owns the push, PR, and CI.

## Manish's Opinions

When you are working on something that would benefit from Manish's viewpoints, read `OPINIONS.md` to understand how he thinks.

## Voice Profile

When you are talking, posting, writing, or communicating on behalf of Manish, read `VOICE.md` to understand how he talks.
