# Changelog

## 2026-08-14 — ai-image v2

- Adds first-class `ai-image edit` using MFLUX FLUX.2 image-conditioned editing.
- Supports one source image plus repeated `--reference` images.
- Enables the validated FLUX.2 Klein 4B editing role.
- Adds a new `precision` role for Qwen-Image-2512-8bit.
- Routes `conceptual` to Krea 2 by default after local testing showed Qwen could drift into unwanted infographic/typography layouts; `--use-fallback` explicitly selects the precision/Qwen route.
- Adds caller-visible visual acceptance policies via `ai-image policy`.
- Adds `ai-image review` to record external visual acceptance/rejection in metadata without pretending the CLI can judge images itself.
- Adds deterministic quality-attempt filenames: attempt 2 becomes `.attempt-02`, attempt 3 `.attempt-03`, etc.
- Keeps bounded technical retries separate from visual-quality attempts.
- Adds explicit fallback routing with `--use-fallback`; no silent quality fallback occurs.
- Refuses accidental output overwrites unless `--overwrite` is supplied.
- Adds richer metadata: MFLUX version when detectable, backend executable, policy criteria, prompt/brief hashes, duration, technical attempt, quality attempt, input/reference hashes, and safe cache environment paths.
- Keeps SeedVR2 as an explicit post-acceptance operation rather than automatic upscaling.
- Installer backs up the current runtime/config, preserves `local.json`, and copies runtime + portable configs to DotFiles without committing/pushing.
- Adds 14 automated tests covering generation, edit references, upscale, retry, fallback, policy, review recording, overwrite safety, dry-run redaction, timeout, and config errors.
