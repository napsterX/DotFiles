# Fidem Verification Baseline

Repository: `fidem` (Next.js / Supabase / Postgres), audited read-only at branch `feat/62-evaluation-runtime-cutover` with a clean tree.
Method: file reading and read-only shell only; no build, test, install, or generator was executed against the repository, which is byte-for-byte unchanged.
Evidence tags: FACT, INTERP, REC, OPEN.

This baseline informs `../v1-specification.md` and proposes no change to Fidem.
Fidem is the richest of the three pilots and the strongest evidence that the local-first, github-minimal architecture is sound.

## 1. Repository architecture and toolchain summary

FACT.
Next.js 16 (App Router, webpack build) + React 19 + TypeScript 5.8, with two tsconfigs (frontend `noEmit`; `tsconfig.backend.json` emits `dist/` under stricter flags such as `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes`).
Data layer is Supabase/Postgres with 165 migrations, heavy RLS, and a private storage bucket (`public = false`, 11 MiB limit).
Providers: AWS Textract (extraction), Stripe (billing), Resend (email), Sharp (HEIC/HEVC), Sentry + Axiom (observability), Zod v4.
Package manager is npm; `apps/internal-docs/` is a separate npm package (Docusaurus + LikeC4).
The request boundary is `proxy.ts` (there is no `middleware.ts`).
Test tooling: Vitest 4 (three configs: unit, integration, golden-corpus) and Playwright 1.52 (three configs: default static+chaos, browser, smoke) with axe-core; the test surface is 652 `*.test.ts`/`*.spec.ts` files.
Documentation governance is unusually deep (contracts, canonical-ownership registry, runbooks, audits, a mandatory implementation-log).

## 2. Current validation entry points

FACT.
Composite package scripts are the real profiles:
- `validate:fast` = typecheck, lint, `test:unit`, `test:static`, `test:chaos`, `validate:migrations`, `validate:architecture`, `security:audit`, `validate:artifacts`, `validate:tracking` - a deterministic floor with no DB, browser, network, or secrets (~1 minute per CLAUDE.md).
- `validate:local:changed` = `select-local-checks.mjs --run`, the canonical pre-push risk-based gate.
- `validate:local:full` = `validate:fast` plus build, `docs:impact`, `architecture:governance`, `content:validate`, extraction-quality, verification-fixtures, golden-corpus offline, `security:secrets`, and an env-lane print.
- `validate:ci:minimal` = `validate:fast` + build (mirrors the remote sentinel).
INTERP: legacy composites (`gate:ci`, `verify`, `ready`, `test:ci`) still exist and CLAUDE.md already flags some as superseded; the standard should retire them to avoid drift.

## 3. Complete check inventory

The full field-by-field classification table is preserved in the raw audit.
Deterministic, offline, blocking floor (`fast`/`github-minimal` candidates): typecheck, `eslint .`, `test:unit`, `test:static`, `test:chaos`, `validate:migrations`, `validate:architecture`, `security:audit` (static RLS posture), `validate:artifacts`, `validate:tracking`, and `build` (with stub env).
Full-local additions (`full`): `architecture:governance` (duplicate-ownership), `docs:impact`, `content:validate`, extraction-quality, verification-fixtures, golden-corpus offline, and `security:secrets` (gitleaks).
Env-gated tier (`ship`, needs Docker/DB/browser): `test:integration`, `test:integration:rls` (the true tenant-isolation proof), `test:commercial:concurrency` (billing idempotency), `db:schema:check` (drift), `validate:security` live step, `test:e2e:smoke`, and the seeded browser CI lane.
External/manual: the live Textract corpus (AWS credentials), HEIC/HEVC (Linux-only), Axiom emitters, internal-docs CI, and operator recovery CLIs.

## 4. Existing GitHub Actions usage

FACT.
Fidem is in a declared "reduced mode" (2026-07-15): Actions billing is exhausted and there is no branch protection, so no remote check blocks merges; local validation is the declared primary gate.
- `ci-minimal.yml` is the only auto-running workflow (PR + push to staging/main). It runs `validate:ci:minimal` (`validate:fast` + build) with build-time stub env, no Supabase/browser/secrets, and is advisory.
- `ci.yml` ("CI Full") is dispatch-only now: a `validate` job (typecheck, lint, build, unit, static, chaos, extraction-quality, verification-fixtures, migrations, architecture, security:audit, and a no-generated-artifacts git check), a `test-live` job (local Supabase, schema-drift, RLS, commercial concurrency, smoke, a seeded browser lane), plus path-filtered targeted e2e.
- `browser-full.yml`, `e2e-targeted.yml`, `live-tests.yml`, `docs-secret-scan.yml` (gitleaks), and `internal-docs-ci.yml` are all dispatch-only.

INTERP.
Fidem's reduced mode is the strongest available evidence for the standard's core thesis: with no enforced remote gate, correctness rests on a disciplined local gate, and CI is a cheap backstop.
The CI anti-cheat patterns are worth codifying: minimum-executed-count floors on browser lanes (to prevent a silently-green all-skip), hard-fail on missing environment, secret masking, and explicit skip notices for gated lanes.

## 5. Security coverage

FACT.
Secret scanning is present but fail-open locally: `security:secrets` runs `gitleaks protect` but exits 0 if gitleaks is not installed, and the referenced `.gitleaks.toml` allowlist is not committed; the remote `docs-secret-scan.yml` is dispatch-only.
SAST is effectively absent: no semgrep/CodeQL/Snyk; the "SAST-like" coverage is bespoke (typescript-eslint plus custom `no-restricted-imports` and the architecture/migration/ownership validators), which are structural allow/deny scans, not taint analysis.
SCA/dependency scanning is absent: no dependabot, renovate, or `npm audit` anywhere.
Performance/bundle budgets are absent (only Vercel RUM).

Strong, runtime-proven security invariants (FACT):
- Tenant isolation: `tests/integration/rls/` (38 files, real Postgres) asserts cross-tenant SELECT/INSERT/UPDATE denial, unfiltered-enumeration denial, suspended/removed-member denial, a deliberate `service-role-bypass` regression guard, and report immutability.
- Static RLS posture: `security:audit` statically parses all migrations to assert RLS enabled on every canonical table, no FORCE RLS, deny-all templates, and no `GRANT ... TO anon` - cheap, deterministic, no DB.
- Upload/MIME/storage: `upload-security.spec.ts` (UP-S-1..16) and runtime `storage-validation.test.ts` assert MIME allowlist, magic-byte re-check, size limits, expired-slot rejection, storage-key/org cross-tenant binding, admin-only signed URLs, and a non-public bucket.
- Webhook replay/signature: `webhook-replay-auth-security.spec.ts` and runtime `test:commercial:concurrency` assert the replay window, 200-not-500 responses, `23505` idempotency, and server-side org derivation from the session (never client input).

INTERP.
Many "security" static specs are source-string scans (`assertContains` on source): they prove a guard is present in source, not that it behaves correctly at runtime.
The behavioral proof lives in the env-gated integration and browser suites.
The standard should classify the static scans as quality-structural and treat the env-gated runtime suites as the true security gate.

## 6. Quality coverage

FACT.
Lint (`eslint .`) and typecheck (dual tsconfig).
The full build (`tsc --project tsconfig.backend.json && next build`) is the exact Vercel command.
~600 unit test files, plus static invariant suites (`test:static`, Playwright-as-runner with no browser) covering forbidden-language scans, presentation invariants, a Textract contract, legal-launch gates, and security headers.
Accessibility via axe-core in the browser suite.
A residual `.eslintrc.json` coexists with the flat `eslint.config.mjs`; `lint` uses the flat config.

## 7. Architecture and data checks

FACT.
`validate:architecture` enforces invariants A-1..A-9 (`server-only` in actions, facade-only imports, no provider SDKs in `app/`/`components/`, INSERT-only extraction/audit runtime, forbidden schema field names).
`architecture:governance` reads the canonical-ownership registry and fails on duplicate business-logic/read-model/presenter implementations outside canonical owners.
`validate:migrations` enforces filename pattern, strictly-increasing timestamps (no backdating), non-empty, no unguarded DROP/TRUNCATE, and no forbidden column names.
`db:schema:check` regenerates a deterministic Markdown schema snapshot from a live DB and diffs it against the committed snapshot (needs a live DB; soft until the snapshot exists).
`validate:artifacts` fails if build outputs (`dist/`, `.next/`, coverage, reports, `.validation/`) are git-tracked.

## 8. Governance checks

FACT.
`validate:tracking` guards ADR-0031 (GitHub Issues as the only tracker; archived backlog files may not grow editable ticket-state).
`docs:impact` maps changed files to required doc updates via `doc-impact-map.json`, with a `.docs-impact.md` declaration as the exception path.
The implementation-log handoff is enforced by an opt-in `.githooks/pre-commit` plus `docs/implementation-log/` (mandatory per CLAUDE.md), and by a user-global Stop guard.

## 9. Reliability checks

FACT.
Unit chaos/lifecycle suites (`tests/unit/jobs`, `lifecycle`, `reconciliation`, `escalation`) cover retry exhaustion, dead-letter taxonomy, lease/timeout, and idempotency.
Static chaos (`test:chaos`) covers billing-idempotency and state-machine structural assertions.
Runtime reliability (live DB, env-gated) covers extraction-job idempotency, evaluation-recovery sweeps, expired-lease recovery, and verification-event-ledger gap detection/reconciliation/replay.
Operator recovery CLIs (`scripts/recovery/*`) tie to Sentry alerts and runbooks and provide an explicit recovery path.

## 10. Performance checks

FACT.
No bundle-size budget, no `size-limit`/`bundlesize`, no Lighthouse or web-vitals CI gate; `@vercel/speed-insights` is runtime RUM only.
`next build` catches build-time issues but no perf budget is asserted.

INTERP.
This is a genuine gap; if a perf budget is added, it must be a measurable, deterministic threshold (for example a bundle-size ceiling), not a wall-clock or Lighthouse score subject to runner noise.

## 11. Missing or weak coverage

INTERP unless noted.
1. SCA/dependency vulnerability scanning is entirely absent (FACT) - the highest-value cheap add.
2. No true SAST (semgrep/CodeQL).
3. Secret-scan is fail-open locally when gitleaks is missing, and `.gitleaks.toml` is referenced but not committed (FACT).
4. No performance/bundle budget.
5. Many "security" chaos tests are static source-string scans, not behavioral; real proof is in the env-gated suites that do not run in the auto sentinel.
6. No enforced remote gate at all (reduced mode) - every real gate depends on developer discipline running `validate:local:changed`.
7. Schema-drift is soft until the snapshot exists and needs a live DB, so it never runs in the auto sentinel.
8. All live behavioral proof (RLS, commercial concurrency, full browser, integration, Textract) is dispatch-only or local-only right now.

## 12. Duplicate or misplaced checks

INTERP.
Overlapping composites (`validate:fast`/`validate:ci:minimal`/`gate:ci`/`verify`/`ready`/`test:ci`) should be formally reduced to the `validate:*` set; CLAUDE.md already flags some as legacy.
The generated-artifact check exists twice (script plus an inline `ci.yml` git check) - intentional local/remote parity.
The RLS posture audit runs from both `security:audit` (fast floor) and `validate:security` (full gate) - deliberate.
The residual `.eslintrc.json` is legacy config residue.

## 13. Recommended `fast` composition

REC (changed-files/package scope where possible; offline, no secrets).
`validate:fast` as it stands: typecheck, `eslint .`, `test:unit`, `test:static`, `test:chaos`, `validate:migrations`, `validate:architecture`, `security:audit`, `validate:artifacts`, `validate:tracking`.
This is already a well-designed `fast` profile; the standard should adopt it near-verbatim.
Cost target: short (~1 minute).

## 14. Recommended `full` composition

REC (repository scope, may use local Docker/DB).
`validate:local:full` as it stands (adds build, `docs:impact`, `architecture:governance`, `content:validate`, extraction-quality, verification-fixtures, golden-corpus offline, `security:secrets`), plus the env-gated runtime security suites when the local stack is up: `test:integration`, `test:integration:rls`, `test:commercial:concurrency`, and `db:schema:check`.
REC additions: SCA (`npm audit`/`osv-scanner`/dependabot), commit the `.gitleaks.toml` and make the secret scan fail-closed in `full`/`ship`, and consider a real SAST pass.

## 15. Recommended `ship` composition

REC.
The complete mandatory `full` assurance, plus shipping and governance prerequisites: a clean working tree for the shipped scope, generated-artifact consistency (`validate:artifacts` and the schema snapshot), a determinable merge-base, `validate:tracking` and `docs:impact` satisfied, and the mandatory implementation-log handoff.
The env-gated runtime security suites (RLS, commercial concurrency, storage/upload, integration) are mandatory-when-relevant for `ship` because they are the true security gate; they must report `unavailable` (exit 4) when the local stack is down rather than silently pass.
The full browser suite (20-30 minutes, flaky-prone) and the live Textract corpus (spends provider credit) should be pre-release/manual, not part of the standard `ship` path, but the seeded minimal browser lane with a minimum-executed floor belongs in `ship`.

## 16. Recommended `ship` composition - static-versus-runtime note

REC.
Because Fidem's static "security" specs can pass after a real behavioral regression, `ship` must not treat the static scans as sufficient security proof.
The env-gated runtime suites carry the blocking security assurance; the static scans are quality-structural signal.

## 17. Recommended `github-minimal` composition

REC (offline, deterministic, no secrets; a subset of `full`/`ship`).
Exactly `validate:ci:minimal` (`validate:fast` + build with stub env), which the repository already runs as its sole auto workflow.
REC add: `npm audit`/`osv-scanner` (cheap, offline, high value) and a fail-closed secret scan once `.gitleaks.toml` is committed.

## 18. Blocking versus advisory recommendations

REC.
Blocking: the entire `validate:fast` floor, build, migrations/architecture/ownership validators, `validate:artifacts`/`validate:tracking`, and the env-gated RLS/commercial/integration/storage suites when relevant and the stack is available.
Advisory: static source-scan "security" specs (reclassify as quality-structural), the full browser suite (flaky), the live Textract corpus (billed), Axiom queryability emitters, and internal-docs CI.
Conditional: `docs:impact` (exception via `.docs-impact.md`), `db:schema:check` (soft until snapshot exists), and platform-bound HEIC/HEVC (Linux-only).

## 19. Dependencies and environment constraints

FACT.
Zero external deps (offline, no secrets): typecheck, lint, `test:unit`, `test:static`, `test:chaos`, `validate:migrations`, `validate:architecture`, `security:audit`, `validate:artifacts`, `validate:tracking`, `docs:impact`, `architecture:governance`, `content:validate`, and build (with stub env); the secret scan needs the gitleaks binary or it skips.
Docker + local Supabase + `SUPABASE_*_TEST` env: `test:integration`, `test:integration:rls`, `test:commercial:concurrency`, `validate:db`, `db:schema:check`, and the `validate:security` live step.
Dev server + local Supabase + seeded user: `test:e2e:smoke`, the browser lanes.
Real credentials/network (external): the Textract corpus lane and Axiom emitters (opt-in, skip-with-notice).
Platform-bound: HEIC/HEVC decode requires Linux.

## 20. Risks and unresolved questions

OPEN / INTERP.
`doctor` can be read-only for the deterministic tier (all pure file reads) but must not auto-run the live tier: `test:integration*`, browser lanes, `db:schema:check`, and the `validate:security` live step require `supabase start` (Docker), which mutates local state and writes `.next/`/`test-results/`/reports.
A read-only `doctor` must probe environment readiness (ports 54321/3000, like the existing `print-env-lanes.mjs`) and print the live lanes, never run them - mirroring the existing detector's "envScripts are never auto-run" rule.
Open: `.gitleaks.toml` is referenced but missing (latent gap?); the whole gate currently rests on humans running `validate:local:changed` (no enforced remote gate); and the standard should confirm that only the offline golden-corpus variant is gate-eligible (the live Textract variant spends credit).

## 21. Recommended future implementation scope

REC (out of scope for this audit).
Implement `scripts/verify` as a thin adapter that composes the existing `validate:*` scripts into the standard profiles, retires the legacy composites, and adds the absent commodity checks (SCA, a committed and fail-closed secret scan, optionally SAST, and a measurable bundle-size budget) as new native tools it orchestrates rather than reimplements.
Fidem's existing `select-local-checks.mjs` risk detector and secret-free `.validation/last-run.json` manifest are a strong model for how `fast`/`full` should scope by changed files, and for reporting outcomes without storing secrets - the standard endorses that pattern but keeps evidence local and uncached (no signed or central evidence).
