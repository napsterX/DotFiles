# ai-image v2 stable CLI contract

The skill and its callers depend on this interface, not backend-specific flags.

Expected runtime: `ai-image` schema version 2 with the v2 command surface,
including `promote` from runtime `2026.08.14-ai-image-v2.1` onward.

## `doctor`

```text
ai-image doctor [--json]
```

Read-only preflight. Confirms config schema, role readiness, backend executable
availability, MFLUX compatibility, and license approval. Does not download or
mutate models/config.

Require `status = ready` before normal execution.

## `policy`

```text
ai-image policy --purpose ROLE [--use-fallback] [--json]
```

Returns the caller-visible policy associated with the effective route, including
acceptance criteria and retry guidance. Use this before judging generated output.

## `generate`

```text
ai-image generate \
  --brief PATH \
  --purpose editorial|photorealistic|conceptual|precision|fast-draft|typography \
  --aspect RATIO \
  [--quality draft|standard|high] \
  [--seed N] \
  [--use-fallback] \
  --output PATH \
  [--quality-attempt N] \
  [--exact-output] \
  [--overwrite] \
  [--json] [--dry-run]
```

Normal skill operation should not use `--overwrite`. For attempts 2+, use
`--quality-attempt N`; the runtime derives deterministic `.attempt-NN` output
filenames.

`--use-fallback` is explicit. It selects the configured fallback route and must
never be added silently.

## `edit`

```text
ai-image edit \
  --input PATH \
  [--reference PATH ...] \
  --brief PATH \
  [--seed N] \
  --output PATH \
  [--quality-attempt N] \
  [--exact-output] \
  [--overwrite] \
  [--json] [--dry-run]
```

`--reference` is repeatable. Editing uses the runtime's configured editing role.
The source plus references are recorded/hashes persisted in metadata.

## `review`

```text
ai-image review \
  --input PATH \
  --decision accepted|rejected \
  [--reason TEXT] \
  [--reviewer TEXT] \
  [--json]
```

Persists an external visual review into the image's sidecar. This is how the
skill records its actual image inspection. A process exit code alone is never a
visual acceptance decision.

## `upscale`

```text
ai-image upscale \
  --input PATH \
  [--resolution 2x|3x|TARGET] \
  [--softness FLOAT] \
  --output PATH \
  [--quality-attempt N] \
  [--exact-output] \
  [--overwrite] \
  [--json] [--dry-run]
```

Uses the configured upscale role. In a generation workflow, call only after the
source candidate has been visually accepted.

## `promote`

```text
ai-image promote \
  --input PATH \
  --output PATH \
  [--overwrite] \
  [--json] [--dry-run]
```

Publishes an already-accepted candidate to a final delivery path by copying
bytes. No image model runs.

Preconditions the runtime enforces:

- the candidate image exists and has an `ai-image` sidecar;
- the sidecar records `review.decision = accepted`, otherwise
  `CANDIDATE_NOT_ACCEPTED`;
- the destination does not already exist, otherwise `OUTPUT_EXISTS` unless
  `--overwrite` is passed explicitly;
- the destination differs from the candidate, otherwise
  `PROMOTION_SOURCE_IS_DESTINATION`.

Guarantees:

- the destination is written atomically and its SHA-256 is verified against the
  candidate, otherwise `PROMOTION_HASH_MISMATCH`;
- the candidate image and its sidecar are left untouched;
- the final sidecar preserves the candidate's generation/edit provenance, its
  original `quality_attempt`, and its original `review`, adding only
  `promoted_from`, `promoted_from_sha256`, and `promoted_at_utc`.

This is the only supported way to write the caller's requested delivery path.

## `config`

```text
ai-image config [--json]
```

Shows safe effective configuration metadata. Do not treat it as a secret dump.

## `version`

```text
ai-image version
```

## Important result fields

Exact fields may grow, but the skill should consume these when present:

```json
{
  "status": "success",
  "operation": "generate",
  "output": "/absolute/path/hero.png",
  "requested_role": "editorial",
  "effective_role": "editorial",
  "backend": "mflux-krea2",
  "model": "krea/Krea-2-Turbo",
  "seed": 42,
  "width": 1536,
  "height": 864,
  "quality_attempt": 1,
  "technical_attempt": 1,
  "fallback_used": false,
  "metadata": "/absolute/path/hero.png.ai-image.json",
  "warnings": []
}
```

Do not hard-fail merely because newer runtimes add safe extra JSON keys.

## Exit/error contract

Failures use non-zero exit codes and, with `--json`, a stable error object such
as:

```json
{
  "status": "error",
  "code": "OUTPUT_EXISTS",
  "message": "..."
}
```

Surface the stable code and safe message. Never echo secrets or entire
environment dumps.
