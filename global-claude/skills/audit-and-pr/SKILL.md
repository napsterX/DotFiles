---
name: audit-and-pr
description: Audit the last implementation against its original request, then - only if the audit is clean enough to ship - file a GitHub issue for every unfixed P2/P3 finding, create a well-named branch, commit, push, and open a PR with the audit results (linked to those tracking issues) filled into the description, then wait for CI and merge automatically once checks are green (or report back for manual review if any check fails). The audit itself always runs on Opus regardless of the session's own model, unless an argument names a different model (e.g. "/audit-and-pr fable"). Use when the user asks to audit and ship, wants an audited PR, says "audit and PR this", or invokes /audit-and-pr.
user-invocable: true
---

# Audit and PR

Run the same audit the `audit` skill does, then act on the result: ship a PR if
the change is clean, or stop and report if it isn't. The review and testing
work narrates as it happens - what's being looked at, which checks are
running, whether new tests are being written and why, and which prior test
evidence is being reused rather than rerun - rather than disappearing into a
silent block and surfacing only as a final verdict. Any P2/P3 finding that
ships unfixed gets its own GitHub issue first, so it stays visible after the
PR merges instead of quietly disappearing into a description no one re-reads.
Once the PR is open, wait for CI and merge it automatically the moment every
check is green - deleting the branch and cleaning up locally - or, if any
check fails, stop short of merging and hand it back for manual review. This
skill is the `audit` skill plus a gated shipping step plus a gated merge step
- it never skips the audit, never ships something the audit flagged as
unsafe, never lets a shipped gap go untracked, and never merges past a red
check.

## 1. Testing policy

This skill's testing strategy is risk-weighted and evidence-reusing, not
exhaustive and not reflexively rerun-everything. The goal is the smallest
credible body of evidence that would catch most realistic defects introduced
by the change - high confidence in normal production use, the critical path,
the dominant failure modes, and the highest-risk regression surfaces - not
100% coverage, not a raw test count, and not re-executing something already
proven valid just to produce a fresh copy of the same result.

This section governs testing across every phase below: what the audit
subagent treats as evidence in step 2, what the auto-fix phase writes in
step 3, what the PR body and final report say about tests in steps 8 and 10.
`~/.claude/skills/audit/SKILL.md`'s checklist item 8 and "Tests / Validation"
table stay the entry point, but this policy replaces how that item and that
table get filled in for this skill's runs - richer than the base audit's
"run whichever exist" pass. `~/.claude/skills/minimal-sufficient-testing/SKILL.md`
stays the authority for *how* to decide what a new test should be (type,
risk level, location, positive/negative case) once this policy has
established that a gap needs closing - do not re-derive that decision
framework here, invoke it.

### Build the evidence ledger first

Before the audit subagent runs anything, assemble a **test evidence
ledger**: every formatting/lint check, typecheck, build, unit/integration/
API/component/e2e/browser test, migration validation, security/authorization
check, manual functional validation, defect reproduction-and-fix
confirmation, and regression test that already ran during planning,
implementation, debugging, or finalization. For each entry, record the
command/procedure, the result, the code state it ran against, and which
requirement or risk it covers.

You (the orchestrating session) have the conversation transcript the audit
subagent doesn't inherit - build the ledger's first draft from that before
dispatching, and hand it to the subagent as part of its brief, the same way
step 2 already hands over the objective. The subagent then verifies and
extends it: re-checks each entry against the reuse rules below given the
code state it's actually auditing, and looks for anything the transcript
missed in commit messages, the PR description, CI logs, or repo state. A
claim like "tests were run" with no identifiable command or result is not a
ledger entry.

### Reuse rules

An entry counts as valid, reusable evidence - **do not rerun it** - only
when all of these hold:

1. The exact command/test/procedure is identifiable.
2. The result is clearly recorded as passed/validated.
3. It ran against the current code state (or a materially equivalent tree).
4. Nothing since has changed the behavior or files it covered.
5. It used the relevant config, environment, dependencies, and database
   state.
6. It completed - not interrupted, partial, skipped, or inferred.
7. It's actually appropriate evidence for the requirement/risk in question.

Rerun or replace an entry instead when: the covered code changed after it
ran; it predates the final fix; the command or result can't be verified; it
targeted a different branch/commit/worktree/config/environment; a
dependency, schema, migration, generated file, or runtime config changed
afterward; the run was partial, flaky, interrupted, skipped, or ambiguous;
it only exercised an implementation detail rather than the required
externally observable behavior; the audit surfaces a new risk it doesn't
cover; the repo's own gate demands a fresh aggregate run; or a cheap
critical check is worth rerunning simply because rerunning it costs less
than the uncertainty of relying on weak evidence.

### Minimum evidence set

Combined (reused + newly executed), cover what applies:

1. **Repository quality gates** - formatting/lint, typecheck, targeted
   automated tests, build. Discover the repo's real scripts (the same
   detection `audit/SKILL.md` step 4 already does); never invent commands.
   A cheap final aggregate run is a deliberate call when it buys real
   confidence that the individually-run checks still pass together, not
   automatic duplication of what was already checked piecemeal.
2. **Happy path** - the main requested behavior, proven from the caller's/
   user's perspective. One realistic end-to-end/integration/component/API
   test beats several shallow implementation-detail ones. Reuse an
   implementation-time happy-path run if it exercised the final code.
3. **Primary failure path** - the most probable or consequential failure
   this specific change could hit (bad input, missing data, unauthorized
   access, dependency failure, rejected state transition, persistence
   failure, duplicate/replay) - picked from the actual change, not a
   generic checklist. Don't stack a second test proving the same contract.
4. **Regression protection** - existing behavior most likely broken by the
   changed files, interfaces, schemas, or shared components. A change to an
   existing pathway is not covered by testing only the new behavior. Count
   regression tests already run during implementation, but confirm nothing
   since invalidated them.
5. **Boundary and security validation** - mandatory whenever the change
   touches auth/authz, tenant or org isolation, RLS/service-role behavior,
   sensitive-data exposure, payments/entitlements, migrations and rollback
   safety, destructive operations, webhook verification/idempotency, file
   validation/parsing, async job retries, or public API compatibility.
   Never skipped to save tokens. Prior evidence only satisfies this when it
   directly validated the final code at that boundary - lint, typecheck, or
   a general build is never a substitute here.

### Selection and budget

Prioritize additional testing in this order: (1) original requirements not
yet directly validated, (2) critical user journeys not covered by prior
testing, (3) security/data-integrity/tenant-boundary risks, (4) realistic
regressions from the changed surface, (5) common invalid/failure conditions,
(6) edge cases with real production likelihood or impact. Deprioritize
anything already validly covered, improbable low-impact combinations,
duplicate proofs of the same behavior at multiple layers, implementation-
detail-coupled tests, broad unrelated suites when a targeted one is enough,
cosmetic snapshots, and speculative tests outside the change's risk surface.

Start from the reused ledger, run only what's needed to close material gaps.
Expand testing when: a test just failed; a fix landed after the evidence
that covered it; the diff touches shared or high-blast-radius code; real
uncertainty remains; targeted testing is unreliable for this repo's
architecture; the change touches security, tenancy, migrations, payments, or
destructive operations; a targeted test exposes a wider possible regression;
or existing evidence turned out incomplete or untrustworthy. Do not keep
expanding to chase theoretical completeness once the stopping rule below is
met.

### Adding tests

Add or update an automated test when the behavior could realistically
regress, matters enough to block shipping if broken, isn't already
protected, can't be sufficiently validated by what's already run, and can be
tested deterministically without disproportionate cost.
`~/.claude/skills/minimal-sufficient-testing/SKILL.md` owns the decision
mechanics (test type, location, positive/negative case) once a gap is
established - this policy owns deciding *whether* a gap exists. Never add a
test just to raise a count or a coverage percentage, and never duplicate an
existing test at the same risk/contract level unless the existing one is
inadequate or unreliable. When a full automated test would be
disproportionately expensive, use the strongest practical alternative and
say so explicitly - manual validation alone never suffices for critical
security or data-integrity behavior.

### Classify every entry

At the end, classify each relevant test/gate as one of:

- **Reused** - previously completed, still valid, not rerun.
- **Rerun** - previously completed, executed again because validity was
  uncertain, the code changed, or a final aggregate check was justified.
- **Newly executed** - added this audit to cover a previously untested
  requirement or risk.
- **Omitted** - deliberately not run: redundant, low-value,
  disproportionate, or outside the change scope (say which, and why).
- **Unable to validate** - required evidence couldn't be obtained.

### Stopping rule

Testing is sufficient once: the requested behavior is directly validated,
the primary happy path is covered, the most important failure path is
covered, likely regression surfaces are checked, applicable security/data-
integrity boundaries are tested, repository quality gates have valid passing
evidence, prior evidence has been reviewed for continued validity, and no
unexplained failures or material uncertainties remain. Stop there - do not
rerun valid tests for ceremony, and do not keep generating low-value tests
for increasingly remote edge cases.

### Confidence assessment

Rate one of:

- **High confidence** - critical behavior, dominant failure modes, and
  relevant boundaries are directly validated by current, trustworthy
  evidence.
- **Moderate confidence** - core behavior is validated, but a named
  environmental, evidence, or tooling limitation remains.
- **Low confidence** - important behavior couldn't be validated. This blocks
  the ship gate (step 4) the same as an unfixed P1.

A passing lint/build, an unverified claim of prior testing, or a generic
existing suite never earns "High confidence" on its own.

### Test report

The audit subagent's output (step 2) must include, as additional structured
output immediately after the standard `IMPLEMENTATION AUDIT RESULT` block -
not instead of it, and not folded into the narration: **Test strategy** (why
the combined evidence is sufficient for this specific change); **Prior
testing reused** (per entry: command/procedure, result, what it covers, why
it's still valid); **Tests rerun** (and why rerunning was justified); **New
tests executed** (and which gap each one closes); **Coverage by behavior**
(happy path, primary failure path, regression surface, security/boundary
checks - each tagged reused/rerun/newly-executed); **Deliberately omitted
testing** (what, and why: covered, redundant, low-risk, disproportionate, or
out of scope); and the **Confidence assessment** above.

### Findings this policy produces

Weak test selection or unsafe reliance on stale results is itself a
finding, not a footnote - fold these into the audit's normal P0-P3 findings
(checklist items 7 and 8):

- **P0/P1**: missing validation for authorization, tenancy, destructive
  migration behavior, payment correctness, or another critical boundary.
- **P1**: the main requested behavior isn't directly tested; prior results
  are being reused even though the code they covered changed afterward;
  only implementation-level tests exist for a critical externally observable
  workflow.
- **P2**: a useful but non-critical regression/failure-path test is missing;
  tests were redundantly rerun without improving confidence or covering a
  new risk.
- **P3**: additional low-risk edge-case coverage would help but isn't
  required.

## 2. Audit phase

**Pick the audit model first.** The audit itself - this initial run and
every re-audit in the auto-fix loop (step 3) - always runs on a specific
model, independent of whatever model the current session happens to be
running on. Audit judgment is the part worth pinning; the mechanical work
after it (auto-fix, branch/commit/push/PR, the merge-or-escalate step) stays
on the session's own model as normal.

- If this skill was invoked with an argument naming a model (e.g.
  `/audit-and-pr fable`, `/audit-and-pr sonnet`), use that model for every
  audit and re-audit this run.
- With no argument, default to **Opus**.
- If the named model isn't available in this environment, fall back to Opus
  and say so plainly in the final report - don't silently substitute
  something else.

Run the audit (and every re-audit) as a subagent dispatched with that model
explicitly set, rather than performing the audit inline in the current
session's own model. Give the subagent what it needs to run
`~/.claude/skills/audit/SKILL.md` on its own - which repo, branch, and diff
to audit, and, for a re-audit, what changed since the previous round. Also
give it the test evidence ledger's first draft (Testing Policy, step 1),
built from this session's own transcript, since the subagent doesn't inherit
this conversation and can't reconstruct that draft on its own. The audit
skill's own step 1 already falls back to the PR description or commit
messages when there's no shared conversation context, so a freshly
dispatched subagent can still establish the objective correctly even though
it doesn't inherit this conversation - the same fallback applies to
extending the ledger it was handed.

Follow `~/.claude/skills/audit/SKILL.md` exactly inside that subagent - same
objective-finding process, same 10-point checklist, same validation
detection, same report format - with one exception: checklist item 8 ("are
tests sufficient") and the report's "Tests / Validation" table are governed
by this skill's Testing Policy (step 1) instead of the base audit skill's
"run whichever exist" pass. Do not duplicate or re-derive any of the rest of
that logic here; have the subagent read and run it.

**Brief the subagent to narrate, not just report.** A one-line "PASS with
one P2" at the end tells you nothing about what actually got looked at.
Instruct the subagent explicitly to work out loud as it goes:

- Before reviewing each area (the diff itself, tests, docs, runtime
  behavior), state in one line what it's about to look at and why.
- Walk through the 10-point checklist commenting on each item as it's
  evaluated - what it checked and what it found - not silently, with the
  reasoning only surfacing in the final Requirement Coverage table.
- Before running each validation category (typecheck, lint, unit, static,
  build, browser/e2e), state which command it's about to run and what it
  checks, then state the result before moving to the next one. Do not batch
  all validation into one silent block and report results only at the end.
- For each test evidence ledger entry, state out loud whether it's being
  reused (and why it's still valid) or rerun/replaced (and why) before
  moving on - the classification in the Test report should never be the
  first time this decision becomes visible.

This narration is real output you relay to the user as the subagent
produces it (or immediately after it returns) - do not compress it away into
just the final verdict. The full `IMPLEMENTATION AUDIT RESULT` report and
the Testing Policy's Test report still get produced too, at the end, exactly
as those sections define - the narration comes first and alongside them, not
instead of them.

Produce both reports in full before deciding anything about shipping.

## 3. Auto-fix phase

Before deciding whether to ship, go through the audit's findings and fix the
ones you can fix with genuine confidence - then **re-run the full audit**
(not just the affected checks) to confirm the fix actually resolved the
finding and didn't introduce a new one. This is a bounded loop, not a single
pass: fix -> full re-audit -> fix what's still safely fixable -> re-audit
again, until either nothing safely-fixable remains or you hit the round cap.

**Loop mechanics:**

1. Round 1's findings are the original audit's. Later rounds use the
   previous round's full re-audit findings.
2. Each round, first update the test evidence ledger (Testing Policy, step
   1): re-check every entry against the reuse rules given what this round's
   prior-round fixes actually touched, and reclassify anything that's now
   stale. Then close only the gaps that remain, following
   `~/.claude/skills/minimal-sufficient-testing/SKILL.md` for the decision
   mechanics - read and run it, do not re-derive its logic here. It decides
   what NEW tests the changed behavior (including anything a prior round's
   fix just introduced) actually needs, proportional to risk and to what
   the ledger already covers: produce its Testing Decision, then write/
   update only the tests it requires before anything else this round. Its
   stop conditions are binding - if one fires (e.g. a security change with
   no negative access test possible, or required test infrastructure that
   doesn't exist), treat that as an unfixable finding for the ship gate
   rather than pretending coverage is adequate. Its "Tests Not Required"
   judgments are equally binding - do not add coverage it deemed
   unnecessary just to look thorough, and do not add coverage the ledger
   already counts as reused evidence.

   **Narrate this decision, don't make it silently.** State the ledger
   reclassification and the Testing Decision out loud as soon as they're
   reached: what's still valid from a prior round, what's now stale and why,
   and whether the changed behavior gets new/updated tests or existing
   coverage is judged sufficient, and why either way. When writing a new
   test, say what behavior it covers and why it's needed *before* writing
   it, not just as a diff that shows up after the fact. When judging tests
   unnecessary, say why in one line rather than silently skipping the step -
   "existing tests unnecessary" should always be a visible, reasoned line,
   never an absence.
3. Then fix everything else in the current findings that meets the
   "safe to auto-fix" bar below. Apply both the new tests and the fixes to
   the working tree; do not commit yet (see step 7).
4. Re-run the **full** audit, on the same pinned model chosen in step 2 -
   the whole 10-point checklist and the whole validation suite the audit
   identified as applicable (which now includes the tests you just wrote),
   not a narrowed subset - so a fix that broke something unrelated, or a new
   test that exposes a real bug, actually gets caught. This full re-run is
   itself a case where the Testing Policy's reuse rules say rerun, not
   reuse: this round's fixes changed the code, so evidence from before the
   fix no longer covers it. Brief this re-audit subagent to narrate exactly
   as step 2 describes - which checklist items, which validation commands,
   and which ledger entries it's reusing vs. rerunning, one at a time, not a
   silent batch collapsed into a final PASS/FAIL.
5. Compare this round's findings to the previous round's:
   - If a finding you fixed is gone and no new finding appeared in its
     place: progress - continue to the next round if anything
     safely-fixable remains, otherwise stop, you're done.
   - If a fix this round caused a **new** finding that wasn't there before
     (a regression), that fix was wrong despite looking safe. Revert just
     that round's changes in the working tree (nothing was committed, so
     this is a clean revert), stop the loop immediately, and report the
     regression plus the original unfixed finding - treat it as if no
     auto-fix was attempted for that item.
6. **Cap at 3 rounds.** If safely-fixable findings still remain after round
   3, stop looping - proceed to the ship gate with whatever's left rather
   than fixing indefinitely. An auto-fix loop that hasn't converged in 3
   rounds needs a human look anyway, not more rounds.

Record every auto-fix actually kept (across all rounds) - what, and why you
judged it safe - you'll need this list for the ship gate, the commit step,
and the PR body. Do not report reverted attempts as fixes.

**Safe to auto-fix** - mechanical, unambiguous, low-risk, no design judgment
involved:

- Formatting/lint violations with a canonical auto-fixer (`gofmt`,
  `prettier --write`, `eslint --fix`, etc.) - deterministic, nothing to
  decide.
- Dead code, unused imports, debug leftovers (`console.log`, stray prints,
  commented-out code) clearly not meant to ship.
- A stray accidentally-included file (`.DS_Store`, a scratch/temp file) -
  remove it or add it to `.gitignore`.
- Docs/comments that are factually wrong about the code they describe, when
  the correct fact is unambiguous from the code itself.
- A missing or incorrect test for behavior that is already correctly
  implemented, when you are fully confident about the right assertion.
- A trivial bug with exactly one reasonable fix (off-by-one, wrong variable,
  inverted condition) that you are fully confident about - not "probably",
  fully confident.

**Never auto-fix - always leave as a reported finding:**

- Anything touching security, auth, privacy, data residency, or
  tenant/BYOC boundaries (checklist item 7). These always need a human
  decision, no matter how obvious the fix looks.
- Anything inside a frozen/protected zone the project has flagged as such.
- Anything with more than one reasonable fix approach - pick a design and
  you've made a decision, not a fix.
- Anything that changes scope, introduces an architecture decision, or
  would need an ADR.
- Missing requirements - implementing an absent feature is real work, not a
  fix, and is not this skill's job to originate unprompted.
- Anything the audit itself isn't fully confident about. A finding you'd
  hedge on ("might be", "could be") is a finding to report, not fix.

When genuinely unsure whether something qualifies, don't fix it - report it
instead. A missed auto-fix costs a manual follow-up; a wrong auto-fix ships
a masked problem.

Apply auto-fixes to the working tree as you go; do not commit them yet - the
branch may not exist yet (see step 6). Commit them as their own separate
commit in step 7, once the branch is settled.

## 4. Ship gate

Evaluate this against what's left *after* the auto-fix phase, not the
original raw audit findings - a P1 that got auto-fixed and re-validated
clean no longer counts against the gate.

Do **not** proceed to shipping if any of these hold:

- Verdict is `FAIL` (re-assessed after auto-fixes, if any were made).
- Any `P0` finding remains unfixed.
- Any `P1` finding remains unfixed (the audit skill defines P1 as "must fix
  before merge/launch" - that includes this merge).
- The Testing Policy's confidence assessment (step 1) is **Low confidence**
  - treat this exactly like an unfixed P1, even if no single discrete
    finding names the gap.

In that case, **do not push, under any circumstances, no matter how much of
the work is otherwise done.** Stop after presenting the audit report, the
Test report, and the auto-fix summary. Do not create a branch, do not commit
anything beyond auto-fixes already made (leave those committed locally if
you already committed them - see the auto-fix phase - but do not push them),
do not open a PR. Report plainly: what was auto-fixed, what still blocks,
and the audit's own smallest-safe-follow-up-prompt suggestion so the user
can close the remaining gaps and re-run.

This is a hard stop, not a warn-and-push. A P0/P1 blocker or a Low-confidence
testing verdict is exactly the case this skill exists to catch - pushing
anyway and merely flagging it in the PR defeats the purpose and risks the
flag being missed.

Only `FAIL` clearing to `PASS`/`PASS WITH GAPS`, with no remaining P0/P1 and
at least Moderate confidence, clears the gate to ship. Remaining P2/P3
findings never block - they ship with the change, tracked as their own
issues (see step 5) and documented in the PR (see step 8).

## 5. File tracking issues for shipped gaps

Every P2/P3 finding still open after the auto-fix phase is about to ship
silently unless something outlives the PR description - a merged PR's
"Known gaps" section is easy to never look at again. File **one GitHub
issue per finding**, so each gap is independently visible, prioritizable,
and closeable later, not buried in a paragraph.

Skip this step, and say so plainly in the PR body and final report instead
of silently trying and failing, when:

- The repo has no GitHub remote at all (`gh repo view` fails to resolve
  one), or `gh` isn't authenticated. There's nothing to file issues against.
- There are no remaining P2/P3 findings this round - nothing to file.

Otherwise, for each remaining P2/P3 finding:

1. Check for an existing equivalent first - a quick `gh issue list --search
   "<distinctive keywords from the finding>"` (open and closed). If a
   matching issue already exists, do not create a duplicate - link to that
   issue instead and note in the PR that this finding is already tracked
   there.
2. Otherwise create it with `gh issue create`:
   - **Title**: a short, specific summary of the finding itself (e.g. "Map
     beacon glow can clip against region overflow near an edge"), not a
     generic "P2 finding from audit" or "Follow-up from PR #N".
   - **Body**: the finding's full text and reasoning from the audit report
     (why it's a finding, what the risk is if left unaddressed), which
     priority it carries (state `P2` or `P3` explicitly, using the audit's
     own definitions), and where it came from - the branch/PR it surfaced
     on (link the PR once it exists; if this step runs before the PR is
     open, note "found while auditing `<branch>`" and let the later PR body
     link back to the issue instead).
   - **Labels**: match the repo's existing label scheme if one is evident
     (`gh label list`) - e.g. a `priority:p2`/`priority:p3` or
     `type:*`/`area:*` convention already in use elsewhere in the repo.
     Do not invent a labeling scheme the repo doesn't already have; leave
     unlabeled rather than guessing.
3. Record the issue number - you need it for the PR body's "Known gaps"
   section (step 8) and the final report (step 10).

A finding that gets ticketed is still a finding that shipped - filing the
issue does not change the ship gate (step 4) or make the finding
retroactively fixed. It only ensures it's tracked instead of forgotten.

## 6. Branch

- If you are already on a non-default branch with the audited changes on it,
  ship there - do not create a second branch on top of it.
- If you are on the repo's default branch, create a new branch before
  committing anything.

To name it well: check whether the repo has an existing branch-naming
convention (`git branch -r`, or `gh pr list --state all --limit 20` for
recently closed PR branch names). If a clear pattern exists (e.g. ticket-ID
based, like `issue-14/...`), match it. Otherwise default to conventional
prefixes - `feature/`, `fix/`, `chore/`, `docs/`, `refactor/`, `test/` -
picked by the nature of the change, followed by a short kebab-case
description of what it does (3-6 words). Keep it concise; do not restate the
whole objective in the branch name.

## 7. Commit

Commit only the changes the audit actually covered - do not sweep in
unrelated pre-existing working-tree changes. Match the repo's existing
commit message style if one is evident from recent `git log`; otherwise use
a clear conventional-commit-style summary line (`feat: ...`, `fix: ...`,
etc.) with a body when the change needs more explanation than the summary
line gives.

If the auto-fix phase made changes, commit them separately, after the main
commit, with a clear message (e.g. `fix: address audit findings
(auto-fixed)`) - so a reviewer can see the original work and the audit's
corrections as distinct steps, not folded silently into one commit.

## 8. Push and open the PR

Push the branch, then open the PR with `gh pr create`.

The bar for the PR body: **a reader who never saw the audit or the diff
should understand what changed, why, and what it risks - without opening
the diff.** Terse one-liners per section fail this bar even if every
template field is technically filled. Pull every field below from the audit
report and Test report you already produced; do not re-derive or thin it
down.

- **What changed** - from the audit's Implemented Changes, but written as
  prose a reviewer can follow, not just a bullet list of filenames. Group
  related changes together and say what each group does.
- **Why** - the motivation. Pull this from the original objective/request
  (what problem existed, why this change addresses it), not just a restated
  summary of the diff. If the objective itself doesn't state a "why", say so
  rather than inventing one.
- **Impact / risk** - what this affects: user-facing behavior, data,
  security/privacy/auth boundaries, backward compatibility, anything the
  audit's checklist items 5-7 (unintended behavior changes, security
  concerns) surfaced. State explicitly when there is no user-facing or
  behavioral impact (e.g. "presentation-only, no backend/schema change") -
  that absence is itself useful information, not a section to skip.
- **Tests / validation** - the full table from the audit (typecheck, lint,
  unit, static, build, browser/e2e) plus the Testing Policy's classification
  (Reused / Rerun / Newly executed / Omitted / Unable to validate) and
  confidence assessment - not just "tests pass". Include real numbers when
  the audit captured them (e.g. "14,002 unit tests"), and say plainly which
  passing evidence was reused from implementation rather than freshly
  executed for this PR, so a reviewer isn't misled into thinking everything
  ran from scratch.
- **Known gaps / follow-ups** - any P2/P3 findings from the audit that
  shipped anyway. Never bury these; a reviewer should see them without
  digging. Reference the tracking issue filed for each one in step 5 (e.g.
  "P2: ... - tracked in #108"), not just a plain unlinked note - the issue
  is where this actually gets picked back up. If step 5 was skipped (no
  GitHub remote), say so here instead of implying tracking exists. If the
  template has a rollback-plan field, state one explicitly (e.g. "revert
  this commit" vs. something that needs a data migration reversal) rather
  than leaving it as boilerplate.
- Screenshots or a short reproduction note when the change is UI-facing and
  you can capture one cheaply; skip silently if not feasible, don't block
  the PR on it.

### Read the template literally, field by field

Do not treat a template as five generic buckets to pour the content above
into. Read every section header the actual template defines, and for each
one, work out what it is specifically asking for, then fill it with real,
investigated content - never a rephrase of a neighboring section, never a
placeholder, never silently blank.

Fields recur in a few types across templates you'll encounter (worked from a
concrete example - HachiraEngine's own template - but treat these as
instances of general categories, since templates vary):

- **Issue/ticket linking** (`Closes #`, a deterministic ticket ID, a
  ticket-taxonomy ID): actively look for this - the branch name (e.g.
  `issue-14/...`), `gh issue list` for a title match, or conversation
  context. A bare `Closes #` with no number is a *broken* field, not an
  empty one - either find the number or state plainly there is no linked
  issue.
- **Repo governance metadata** (phase/milestone, owning module/workstream,
  contracts referenced, residency impact, observability impact, security
  impact, and similar repo-specific structured fields): check whether the
  repo defines these concepts at all - a CONTRIBUTING.md, AGENTS.md /
  CLAUDE.md, a ticket-taxonomy or architecture doc, or prior PRs using the
  same template are all evidence. If the concept exists here, populate it
  with the real answer for this change. If the repo has no such concept
  (e.g. no data-residency model at all), write `N/A - <repo> has no
  residency model`, not a blank field or an invented plausible-sounding
  value.
- **Mechanical fields** (files changed, tests run): derive these directly
  and literally - `git diff --stat` / `--name-only` for files, the actual
  validation results for tests. Do not write prose where the field wants a
  list.
- **A log/handoff reference** (implementation log, session handoff): if this
  repo has a convention of writing implementation-log or handoff docs
  (check `docs/implementation-log/`, `docs/ai-handoff/`, or similar), link
  the actual file this change produced. If there's no such convention, say
  so.
- **Checklist / stop-condition items**: evaluate each one against what the
  audit actually found - don't check boxes reflexively. E.g. "No test was
  weakened, disabled, or bypassed" is checked only if the audit's checklist
  (items 6 and 8) support it; if a test genuinely was skipped or weakened as
  a deliberate, reasoned tradeoff, leave that box unchecked and explain why
  in the section it lives under, rather than checking it inaccurately.

This is a guide for recognizing what a field wants, not a fixed schema -
read whatever the actual template contains, and give every field this same
level of investigation, not just the ones that map easily onto the audit
report's own section names.

Then choose the container for this content:

- If the repo has its own `.github/PULL_REQUEST_TEMPLATE.md` (or the
  account-level default applies and you can read its content), fill it in
  section by section with the material above, mapped onto whatever the
  template calls each section. Leave a section that genuinely doesn't apply
  to this repo/change as `N/A` with a one-line reason, rather than deleting
  it or leaving it blank with no explanation.
- If there's no discoverable template, write a body structured as: Summary,
  Why, What changed, Impact / risk, Tests run, Known gaps / follow-ups. This
  is the same content either way - only the container differs.
- If a PR already exists for this branch (e.g. you're adding a follow-up
  commit to already-pushed work), do not open a duplicate - report the
  existing PR URL instead, and consider whether the new commit's audit
  findings belong in a comment on that PR rather than a fresh one.

## 9. Wait for checks, then merge or escalate

The ship gate (step 4) only covers the audit. CI is a second, independent
gate this skill also waits on before deciding whether the PR is actually done
- opening the PR is not the finish line.

**Poll, don't assume.** Immediately after opening the PR, checks are usually
still queued or running. Poll `gh pr checks <number>` (or
`gh pr view <number> --json statusCheckRollup`) every ~30s. Keep waiting
while any check is `pending`/`queued`/`in_progress`. Cap the wait at 20
minutes of polling - if checks still haven't reached a terminal state by
then, stop polling and treat it as **unresolved** (handled the same as "not
green" below, not as a failure, but not as a merge either): report that
checks are still running past the wait cap, give the PR URL, and stop. Don't
silently poll forever and don't guess at an outcome that hasn't landed yet.

Once every check is in a terminal state, decide:

- **All checks passed, or the repo has zero checks configured on this PR at
  all** (nothing to fail) - both count as green. Proceed to merge below.
- **Any check shows failure, error, or was cancelled** - not green. Do
  **not** merge. Report to the user: which check(s) failed, a one-line
  reason pulled from the check's own output if it's quickly available, and
  the PR URL, so they can open it and look. This is the one case this whole
  step exists to catch - do not merge past a red check under any
  circumstance, and do not "fix and retry" here (that's a new change needing
  its own audit, not this skill's job mid-flight).

**Merge (only on green):**

1. Pick a merge method: check recent merged PRs (`gh pr list --state merged
   --limit 10` and look at how they closed, or `gh api` on a couple of merge
   commits) for the repo's own convention. If none is evident, default to
   squash merge - it keeps the target branch's history one-commit-per-PR,
   matching how this skill already produces one focused commit (plus a
   separate auto-fix commit when step 3 made one).
2. Merge with `gh pr merge <number> --squash --delete-branch` (substitute
   the merge method from step 1, and adjust the flag if it's `--merge` or
   `--rebase` instead). `--delete-branch` removes the remote branch as part
   of the merge - this is what "clean up the branch" means for the remote
   side.
3. If the merge command itself fails (e.g. branch protection requires a
   human review/approval that hasn't happened, or a required check the
   rollup didn't surface), do not retry with a bypass flag and do not force
   anything - report the exact error and the PR URL, same as the "not green"
   path. A merge that only `gh` can force past a protection rule is not this
   skill's call to make.
4. On a successful merge, finish the local cleanup: switch to the repo's
   default branch, pull/fast-forward it so it includes the just-merged
   commit, then delete the local feature branch
   (`git branch -d <branch>` - the safe form, which refuses if the branch
   isn't actually merged, as a last sanity check that nothing is lost).

## 10. Report

Tell the user, concisely:

- The branch name.
- The full PR URL.
- What the auto-fix phase changed, if anything - never let an auto-fix ship
  silently even when everything else is clean.
- **Tests, as its own explicit line, not folded into "checks pass":**
  summarize using the Testing Policy's classification - what was reused from
  implementation-time evidence (with real counts, e.g. "166/166, reused from
  the pre-audit run"), what was rerun and why, and what was newly executed
  this run and which gap it closed. State the confidence assessment
  (High/Moderate/Low) plainly. If no new tests were written, say so
  explicitly ("no new tests - existing coverage was sufficient because ...")
  rather than leaving the question unanswered.
- The audit verdict and a one-line summary of any remaining P2/P3 findings
  that shipped anyway, each with its tracking issue number from step 5 (so
  they're visible and followable, not buried) - or, if step 5 was skipped,
  say plainly that no GitHub tracking was available and why.
- The outcome of step 9: merged and cleaned up (say so plainly, e.g. "merged
  and branch deleted"), checks still running past the wait cap, or checks
  failed (name which ones) and nothing was merged.

If the ship gate blocked shipping (step 4), report that instead: what the
auto-fix phase already resolved, what still blocks (the unfixed P0/P1
findings, or a Low-confidence testing verdict), and the follow-up prompt to
close the remaining gaps. Be explicit that nothing was pushed - and note
that step 5 (tracking issues) never runs in this case, since a blocked ship
gate means nothing shipped to track yet.
