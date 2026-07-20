# Manydoors Verification Baseline

Repository: `ManyDoors` (local directory), codename **Prism**, package `prism`, GitHub remote `napsterX/HexaGeniusAcademy`.
Audited read-only at branch `main`.
The working tree was already dirty before the audit (a modified `.claude/hooks/.impl-log-state.json` and many untracked `docs/implementation-log/*.md` files); those are pre-existing user changes and were left untouched.
Method: file reading and read-only shell only; no build, test, format, or generator was executed against the repository, which is otherwise byte-for-byte unchanged.
Evidence tags: FACT, INTERP, REC, OPEN.

Scope note: the commissioning brief described this as a "Next.js frontend, accessibility, visual correctness, performance budgets, kid-facing safety" repository.
That is the product intent.
The actual validation surface is dominated by an LLM tutoring engine, an eval harness, AI-cost instrumentation, and a deterministic "Living Atlas" art-asset pipeline, wrapped by a Next.js App Router app.
This baseline reflects what is in the tree.

## 1. Repository architecture and toolchain summary

FACT.
Next.js 16 App Router (React 19) over a headless engine (`src/engine`, `src/doors`, `src/llm`).
Database is SQLite via Drizzle ORM at `data/prism.db` (gitignored), not Postgres.
Package manager is npm (`package-lock.json`, no `packageManager` field).
TypeScript ESM, `strict: true`, `noEmit`, run through `tsx`; source authored NodeNext-style with `.js`-suffixed imports, so the build is webpack, not Turbopack.
Runtime deps are deliberately light: `@anthropic-ai/sdk`, `ajv`, `better-sqlite3`, `drizzle-orm`, `next`, `react`, `yaml`.
Content model: 124 core YAML files validated by `content/schema/core.schema.json`.
All Claude calls funnel through `src/llm/`; every live tutor turn is a billed call with no mock mode.

## 2. Current validation entry points

FACT.
npm scripts are the entry points.
The gate quartet a human would run is `typecheck` (C1), `test` (C2), `validate` (C4), and optionally `build` (C6) and `eval:evidence:verify` (C5).
There is no combined `check`/`ci`/`verify`/`lint`/`format` script, so a contributor must know to run each separately.
The deterministic Living-Atlas asset validators (C12/C13) and the visual proof (C14) exist only as standalone `npx tsx ...` invocations, wired to no npm script, hook, or CI.

## 3. Complete check inventory

The full classification table is preserved in the raw audit.
Deterministic, blockable checks:
- C1 `typecheck` (`tsc --noEmit`) - correctness; writes only gitignored `.tsbuildinfo`.
- C2 `test` (`node --test` over 130 offline unit files, includes C15) - correctness/quality.
- C4 `validate` (`tsx src/cli/validate.ts`, ajv over 124 cores + band registry + a misconception append-only git-baseline guard) - governance/architecture-data; exits 1 on error, degrades to WARN without `origin/main`.
- C5 `eval:evidence:verify` (offline, credential-free, db-free evidence-integrity check) - reliability/governance.
- C6 `build` (`next build --webpack`) - correctness; heavy.
- C12 Living-Atlas asset validators (SHA-256 byte-equality of frozen approved art, PNG dimensions, 22-locale mask reconciliation, approval records) - architecture-data/governance; deterministic and fail-closed but unwired.
- C13 `map-art-proof`, structural art-pack readiness - architecture-data.
- C15 `control-characters.test.ts` (bespoke SAST banning C0/DEL bytes in tracked source, born from a real incident) - security; runs inside C2.
- C16 AI-cost telemetry and budget suite (24 tests) - reliability/performance-of-dollar-cost.

Advisory / non-deterministic / billed:
- C3 `test:integration` (2 files, live Haiku+Opus), C7 `acceptance` (billed Opus judge), C8 `eval:*` (rubric LLM-judge harness), C9 `audit:extraction` (billed grader), C14 `la-proof` (headless-Chrome screenshot comparison), C18 `verify` skill (manual browser playbook).

Non-gates: C10 `mastery` and C11 `cache:verify` (reports), C17 impl-log Stop hook (never blocks), C19 `db:generate` (a generator).

## 4. Existing GitHub Actions usage

FACT.
Absent.
`ls .github` returns no such directory; there is no CI of any kind.
HANDOFF.md states it: a prior PR "waited for checks (repo has zero CI workflows = green)."
The `github-minimal` backstop domain has zero coverage today, and every deterministic gate runs only when a human remembers.

## 5. Existing local validation behavior

FACT.
The only hook is a Stop hook (`.claude/hooks/impl-log.mjs`, C17) that writes an implementation log per turn and never blocks.
There are no pre-commit/pre-push hooks, no husky, no `.githooks`, no lint-staged.
Local enforcement of typecheck/test/validate is entirely manual and by convention.

## 6. Security coverage

FACT.
SAST, secret scanning, and SCA are absent (no semgrep/snyk/gitleaks/trufflehog/trivy/audit-ci/dependabot).
The only SAST-like control is the bespoke `control-characters.test.ts` (C15) plus `.gitattributes`, born from a real incident where a NUL byte in a batch reconciliation join key shipped unreviewed as "Binary files differ."
A real `.env.local` secret leak occurred and was scrubbed from history (three implementation logs, 2026-07-11); nothing prevents recurrence.
App-runtime security is unit-tested inside C2: HMAC-signed session cookie, PIN-gated parent area, family-password login, and cross-learner cookie-authority (403 on another learner's session).

INTERP.
Kid-safety is enforced by architecture and human judgment, not a deterministic gate: the grounding contract (enforced at approval via `core-validation.ts` and judged per-door in acceptance), the `safety.yaml` LLM-judged eval, a `.gitignore` fixture guard, and the manual verify skill.
No automated deterministic check can prove output is kid-worthy or safe.

## 7. Quality coverage

FACT.
130 offline unit-test files (C2), concentrated in `src/cost` (24), `src/llm` (20), `src/eval` (16), `src/engine` (10), and `scripts/living-atlas` (9); live-model tests are quarantined to the `.integration.ts` glob.
There is no ESLint and no Prettier, and no `eslint-plugin-jsx-a11y` - unusual for a Next.js app, and it means there is no style/quality lint gate at all.
Tutor-output quality is LLM-judged (C7/C8/C9), which is advisory, billed, and non-deterministic.
Visual quality is manual (C18) plus a semi-deterministic screenshot proof (C14); the human "pride gates" (issues #137, #145) are decisions recorded in markdown.

## 8. Architecture and data checks

FACT.
`validate` (C4) is ajv schema validation of every core with hard errors on schema failure, duplicate core id, and duplicate misconception id, and warnings on unknown subject/prereq/band and misconception drift since the `origin/main` baseline (an append-only-by-stable-id guard).
Schema logic lives once in `src/engine/core-validation.ts`, shared by the CLI and the approval route (not duplicated).
The Living-Atlas validators (C12) reconcile the 22-locale mask set, PNG dimensions, and SHA-256 byte-equality of frozen approved art.

INTERP.
Gap: there is no generated-file-consistency check for Drizzle; `drizzle/` migrations and `meta/*_snapshot.json` can drift from `src/lib/db/schema.ts` undetected (C19).

## 9. Governance checks

FACT.
Two parallel implementation-log stores coexist: an auto Stop hook writing to `docs/implementation-log/`, and a separate manual `implementation-log` skill writing to `implementation-logs/`.
Issue-reference convention is conventional commits carrying `type(md-xxx-nnn): ... (#NNN)`, mirrored in the production roadmap with GitHub as source of truth, but there is no automated enforcement (no commit-msg hook, no CI).
The content/curriculum registry is governed by C4.

OPEN.
Which implementation-log store is canonical for the standard is unresolved.

## 10. Reliability checks

FACT.
`eval:evidence:verify` (C5) is a rot/integrity check over the durable decision-evidence archive: it re-hashes byte copies against `source-inventory.json`, re-derives every projection from archived source, and fails on drift, and is explicitly designed to pass on a bare checkout with no runs, db, or network.
The AI-cost telemetry and budget suite (C16) provides batch gates and a budget domain across 24 test files.
`db:backup` has been proven with a real restore drill.

## 11. Performance checks

FACT.
Web performance has no deterministic budget: no Lighthouse, no `@lhci`, no bundle-size budget, no web-vitals gate.
`next build` emits bundle stats but nothing asserts a threshold.
Latency targets ("opening turn appears in well under a second") are subjective observations in the verify skill, not asserted budgets.

INTERP.
The instrumented "performance" axis here is AI dollar-cost (C16), not page speed.
This is a clean example of a measurable budget (cost) versus an absent one (web performance); the standard should not invent a web-perf gate that the repository has no basis to assert deterministically.

## 12. Missing or weak coverage

INTERP.
1. Zero CI - the single largest gap; every deterministic gate is human-triggered.
2. No lint and no format (no ESLint, no Prettier, no jsx-a11y).
3. No combined gate script - poor discoverability of the intended quartet.
4. No accessibility automation - WCAG AA contrast, 44px touch targets, and reduced-motion are asserted only in the manual verify skill.
5. No web-performance budget.
6. No secret scanning, SAST, or SCA, despite a prior real secret leak.
7. No Drizzle generated-migration drift check.
8. The deterministic asset validators (C12/C13) are unwired - valuable, offline, but invisible.
9. Kid-safety and visual excellence have no automated proof, by nature.

## 13. Duplicate or misplaced checks

FACT/INTERP.
Two implementation-log systems overlap and need reconciliation.
C7 (`acceptance`) and C8 (`eval:*`) both LLM-judge tutor quality - conceptual overlap, with acceptance the lightweight form and evals the rigorous harness.
The C12 validators exist as both `.test.ts` (in C2) and standalone CLIs - intentional (unit-test the logic, apply the CLI to real assets), not a defect.
The most consequential misplacement is that the deterministic asset validators are not in any runnable gate.

## 14. Recommended `fast` composition

REC (offline, deterministic, credential-free).
C1 `typecheck`, C2 `test` (which includes C15), C4 `validate` (accepting the documented WARN degrade when history is shallow), and the C12 Living-Atlas asset validators.
Cost target: short to moderate.

## 15. Recommended `full` composition

REC (repository scope, still offline).
Everything in `fast`, plus C5 `eval:evidence:verify`, C6 `build`, C13 `map-art-proof`, and the C16 cost/budget tests (already inside C2).
REC additions to raise assurance: ESLint (with `jsx-a11y`) and Prettier as new native tools, a Drizzle migration-drift check, `npm audit`/`osv-scanner` (SCA), and a secret scan.

## 16. Recommended `ship` composition

REC.
The complete mandatory `full` assurance above, plus shipping and governance prerequisites: a clean working tree for the shipped scope, a determinable merge-base against `main`, the issue-reference convention enforced over the shipped commits, the implementation-log presence the repository mandates (once the two stores are reconciled), and the Drizzle migration-drift check.
The LLM-judged evals (C7/C8/C9), live integration (C3), the screenshot proof (C14), and the manual verify playbook (C18) remain advisory and human-gated; they MUST NOT be blocking, and `ship` MUST NOT claim they prove kid-worthiness or visual excellence.

## 17. Recommended `github-minimal` composition

REC (offline, credential-free, deterministic; the highest-value change for this repo since it has no CI today).
C1 `typecheck`, C2 `test` (includes C15 control-char SAST), C4 `validate` (fetch enough history for the misconception baseline, else accept the WARN degrade), C5 `eval:evidence:verify` (designed for a bare checkout), and the C12 Living-Atlas asset validators; optionally C6 `build` and C13.
Exclude everything billed, db-dependent, or non-deterministic (C3, C7, C8, C9, C11, C14, C18).

## 18. Blocking versus advisory recommendations

REC.
Blocking: C1, C2 (including C15), C4, C5, C12, and, in `full`/`ship`, C6 and C13; plus the new ESLint/Prettier/SCA/secret-scan/migration-drift checks once added.
Advisory (must stay non-blocking): every LLM-judge (C7/C8/C9), live integration (C3), the screenshot proof (C14, environment-sensitive), the manual verify playbook (C18), any future axe or Lighthouse run, and the human pride/kid-worthiness gates.
This objective-versus-subjective line is the central design constraint for this repository.

## 19. Dependencies and environment constraints

FACT.
npm; Node 20+; `tsx` for all TS execution.
SQLite (`better-sqlite3`, native, needs `allowScripts` approval) at `data/prism.db` (gitignored); Drizzle for migrations.
`ANTHROPIC_API_KEY` is required for every live path (integration, acceptance, evals, extraction, app runtime), all billed with no mock; `FAMILY_PASSWORD` and `PARENT_PIN` for the app.
Playwright is not installed (only transitive in the lockfile); C14 and C18 rely on ad-hoc install or a cached headless Chrome.
C4's misconception-drift guard needs `origin/main` reachable and degrades to a WARN on shallow clones, so CI must fetch history or accept degraded mode.

## 20. Risks and unresolved questions

INTERP / OPEN.
The objective/subjective line is the central constraint: no automated check can prove the product is kid-worthy, visually excellent, accessible, or that tutor output is safe; those rest on LLM judges (non-deterministic, billed) plus human decisions in markdown, and the standard must classify them advisory and must not claim automated proof.
Open: which implementation-log store is canonical; whether the C12/C13 asset validators should be promoted into npm scripts, a doctor, and CI; which CLIs are current versus vestigial; and the CI history-depth policy for C4's baseline guard.

## 21. Recommended future implementation scope

REC (out of scope for this audit).
Implement `scripts/verify` as a thin adapter (Node/`tsx` or Bash) that: wires the currently invisible deterministic asset validators (C12/C13) into runnable profiles; introduces the first CI as a `github-minimal` workflow running the offline deterministic set (the largest single improvement, given zero CI today); adds the absent commodity tools as new native tools the adapter orchestrates (ESLint with `jsx-a11y`, Prettier, `npm audit`/`osv-scanner`, a secret scan, and a Drizzle migration-drift check); reconciles the two implementation-log stores; and encodes the objective-versus-subjective boundary so that no LLM-judged or human-judged check is ever wired as blocking.
