# Semantic model routing

Callers select semantic purposes. `ai-image` configuration remains the source of
truth for actual model/backend mapping. Do not hard-code backend executables into
skill commands.

The currently validated runtime is expected to map roles approximately as
follows, but always trust `ai-image doctor/config/policy` over this prose if the
runtime is later updated.

| Role | Current validated route | Use when |
|---|---|---|
| `editorial` | Krea 2 Turbo | art-directed heroes, premium editorial imagery, visual character |
| `conceptual` | Krea 2 Turbo | abstract ideas/metaphor where composition/aesthetic matters |
| `photorealistic` | FLUX.2 Klein 4B | realistic scenes, business portraits, products, clean photography |
| `fast-draft` | FLUX.2 Klein 4B | rapid composition exploration, non-final candidates |
| `precision` | Qwen-Image-2512 8-bit | difficult spatial relationships, structured/knowledge-heavy prompts |
| `typography` | Qwen-Image-2512 8-bit | visible text is intentionally part of the image |
| `editing` | FLUX.2 Klein 4B edit | source-preserving semantic edits, one or more references |
| `upscale` | SeedVR2 3B | post-acceptance resolution enhancement/restoration |

## Selection rules

1. Honor an explicit caller role when it is compatible with the operation and ready.
2. Otherwise choose the narrowest semantic role that matches the objective.
3. Never select by parameter count or model hype.
4. Never route evidence, exact charts, screenshots, documents, or factual diagrams into generative imagery when authenticity/determinism is required.
5. Treat `typography` as opt-in. Exact publication typography is usually better rendered deterministically outside the generative image layer.
6. `editing` is an operation, not a substitute for every failed generation. Use it when preserving an existing composition has value.
7. `upscale` is not a quality repair for a rejected generation.

## Explicit fallback guidance

Fallback is configured by `ai-image` and invoked only with `--use-fallback`.
Do not invent a model switch outside that contract.

Typical justified cases:

- `editorial` -> configured photorealistic fallback when Krea repeatedly produces undesirable aesthetic artifacts but the scene is fundamentally photographic;
- `conceptual` -> configured precision fallback when Krea repeatedly fails a complex relationship, layout, or knowledge-heavy instruction;
- `photorealistic` -> configured editorial fallback when FLUX output is technically correct but repeatedly too generic/stock-like for the requested art direction;
- `precision` -> configured editorial fallback when Qwen repeatedly over-designs the scene or introduces unwanted typography and precision is no longer the dominant requirement.

Fallback should normally follow a diagnosed failure, not run as an automatic
second candidate generator.

No silent fallback for typography, editing, or upscaling unless a future runtime
explicitly adds and documents one.

## When to edit instead of regenerate

Prefer edit when:

- composition, framing, and subject placement are already strong;
- the defect is localized or semantically narrow;
- preservation of identity, pose, lighting, architecture, or background matters;
- reference images can materially improve the requested change.

Prefer regeneration when:

- overall composition is wrong;
- the wrong visual medium/style was generated;
- major subject relationships are incorrect;
- the image contains broad structural corruption;
- fixing it would require effectively redrawing the whole scene.
