# ai-image stable CLI contract

The caller should depend on this interface, not backend flags.

## Commands

### doctor

`ai-image doctor [--json]`

Checks configuration, role completeness, selected backend executables, and
license approval. It does not download models or mutate configuration.

### generate

`ai-image generate --brief PATH --purpose ROLE --aspect RATIO --quality LEVEL --output PATH [--allow-cloud] [--seed N] [--json] [--dry-run]`

The wrapper reads the brief, selects the configured role/backend/model, maps the
aspect ratio to dimensions, safely constructs the configured backend argv, runs
without shell evaluation, validates output existence, and writes metadata.

### upscale

`ai-image upscale --input PATH --output PATH [--json] [--dry-run]`

Uses the configured `upscale` role.

### config

`ai-image config [--json]`

Shows safe, non-secret effective configuration metadata.

### version

`ai-image version`

## Result schema

Success JSON includes:

```json
{
  "status": "success",
  "operation": "generate",
  "output": "/absolute/path/image.png",
  "backend": "mflux",
  "role": "editorial",
  "model": "configured-model",
  "width": 1536,
  "height": 864,
  "seed": 12345,
  "attempt": 1,
  "upscaled": false,
  "metadata": "/absolute/path/image.png.ai-image.json",
  "warnings": []
}
```

Failures use a non-zero exit code and may emit JSON with `status = error`, a
stable error code, and a safe diagnostic. Do not include secrets.
