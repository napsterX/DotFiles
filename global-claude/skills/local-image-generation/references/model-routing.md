# Model routing

Callers select semantic roles. Model names and backend details live in
configuration so they can change without rewriting skills.

## Roles

### editorial

General publication-quality conceptual/editorial illustration. Prefer strong
composition, controllable abstraction, and visual sophistication.

### photorealistic

Realistic physical scenes or products when generation is appropriate. Do not use
for evidentiary/historical authenticity that requires a real photograph.

### conceptual

Abstract systems, relationships, metaphor, and ideas that cannot literally be
photographed.

### fast-draft

Rapid composition exploration. Lower generation cost/time is acceptable because
output is not assumed publication-ready.

### typography

Only use a model explicitly documented as capable of reliable text rendering.
Otherwise route text-heavy graphics to deterministic rendering outside the
generative image system.

### editing

Image-to-image editing, inpainting, or other transformations when a configured
backend supports them.

### upscale

Resolution enhancement or restoration using a configured upscaler.

## Routing rules

1. Use the requested semantic role when configured and licensed.
2. Do not guess a model when the role has no configured model.
3. Do not route evidence, charts, or diagrams to generative imagery merely
   because a model exists.
4. Prefer quality over minimum memory usage on high-memory Apple Silicon unless
   the caller explicitly requests speed/draft mode.
5. A role's `license_approved` flag must be true for production use.
6. Machine-specific model paths belong in local overrides, not skill text.
7. Record the actual configured model/backend in result metadata.

## Updating models

Edit the externally managed `ai-image` model-routing configuration/local
override rather than `SKILL.md`. This package must not install, replace, or back
up that configuration. Document
for each model:

- role strengths;
- weaknesses;
- expected speed/memory;
- supported operations;
- licensing/source;
- commercial-use status;
- model-specific prompt caveats.
