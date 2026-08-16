# Model licensing and production gate

Publicly downloadable weights are not automatically approved for commercial
asset generation. `ai-image` configuration is the runtime source of truth and
must block roles whose `license_approved` flag is false.

The skill must not override that gate.

## Current validated local portfolio

The installed runtime used during this skill update was configured for:

- Krea 2 Turbo for editorial/conceptual work;
- FLUX.2 Klein 4B for photorealistic, fast-draft, and editing work;
- Qwen-Image-2512 8-bit for precision and typography work;
- SeedVR2 3B for upscaling.

These names document the currently validated routing, not a permanent skill API.
If runtime model configuration changes, re-review the actual licenses and update
runtime approval records rather than editing the skill to bypass them.

## Required production record

For every configured production model retain, in runtime/configuration or its
maintained licensing record:

- model/source identifier;
- license name/reference;
- commercial-use conditions;
- attribution requirements;
- restrictions on generated outputs where known;
- review date;
- `license_approved = true|false`.

Unknown means not approved.

## Krea condition

The current Krea route is intentionally allowed only because the runtime has
explicitly marked the selected model/license as approved for the user's current
usage. If the applicable Krea commercial threshold or other license condition
becomes relevant, update the runtime approval/config before further production
use. The skill must respect a future `license_approved = false` without debate.

## Legal boundary

This skill does not make legal conclusions. Its job is to enforce the configured
approval state and fail closed when approval is absent or unknown.
