---
name: local-image-generation
summary: Generate, edit, upscale, and route image work through a stable local-first ai-image interface without exposing backend-specific commands to callers.
description: Use when another workflow or the user needs a locally generated or processed image on Apple Silicon. Accept a visual objective or art brief, select an appropriate configured role/backend, invoke the constrained ai-image CLI, return machine-readable asset metadata, and diagnose technical failures. Editorial need and editorial acceptance remain the caller's responsibility.
argument-hint: "<brief|request> [--purpose editorial|photorealistic|conceptual|fast-draft|typography|editing|upscale] [--aspect <ratio>] [--quality draft|standard|high] [--output <path>]"
user-invocable: true
disable-model-invocation: false
---

# Local Image Generation

Provide a stable local-first image-generation boundary for Claude Code. The
caller specifies the visual objective; this skill chooses the configured
technical route and invokes `ai-image`. The `ai-image` executable and its
configuration are **externally managed prerequisites**. This skill package must
not install, update, replace, back up, delete, or copy them.

This skill is reusable outside articles: website assets, README images, product
concepts, editorial illustrations, design exploration, marketing assets, image
editing, and upscaling.

## Required references

Read:

- [model-routing.md](references/model-routing.md) for role-based routing;
- [prompting.md](references/prompting.md) for brief-to-prompt transformation;
- [quality-guidance.md](references/quality-guidance.md) for technical output
  checks and retry behavior;
- [licensing.md](references/licensing.md) before using a model for publishable or
  commercial work;
- [cli-contract.md](references/cli-contract.md) for the stable `ai-image`
  interface and result schema.

## Architectural boundary

Preferred stack:

`caller -> local-image-generation -> ai-image -> configured local backend -> Apple Silicon`

The current runtime is intended for MLX/MFLUX-backed local models, but callers
must not depend on those implementation details. Models and command details are
configuration, not skill API.

Do not require an MCP server or long-running API merely to call local image
generation. Prefer the constrained CLI wrapper.

## Responsibilities

This skill owns:

- technical role/backend selection;
- configured model selection;
- safe command construction through `ai-image`;
- environment/runtime diagnostics;
- aspect/dimension mapping;
- configured quality parameters;
- seed handling;
- timeout and technical failure handling;
- output-path validation;
- technical retry policy;
- optional configured upscaling;
- machine-readable metadata;
- explicit, opt-in future cloud escalation hooks.

This skill does **not** decide whether an article or page needs an image. It does
not certify editorial relevance or factual appropriateness. The calling workflow
must inspect and accept/reject the actual asset.

## Claude permissions

Grant Claude Code permission to invoke the narrow `ai-image` wrapper rather than
adding broad backend-specific shell permissions merely for image generation. The
wrapper is the controlled boundary. No MCP server or long-running daemon is
required by this skill. The package assumes the user has separately installed
and configured `ai-image`; it does not own that runtime.

## Stable invocation

Prefer:

```text
ai-image generate --brief <path> --purpose <role> --aspect <ratio> --quality <level> --output <path> --json
```

For upscaling:

```text
ai-image upscale --input <path> --output <path> --json
```

Use `ai-image doctor --json` before first runtime use or after configuration
changes. Do not bypass `ai-image` to call backend-specific commands directly.

## Routing

Callers choose a semantic purpose, not a model name:

- `editorial`
- `photorealistic`
- `conceptual`
- `fast-draft`
- `typography`
- `editing`
- `upscale`

`ai-image` maps the purpose to a configured role. Do not silently switch to an
unrelated role merely because the preferred model is unavailable.

## Prompt handling

Preserve the art brief's intent. Translate it into the selected backend/model's
prompt conventions only as needed. Do not inject generic prompt spam such as
`masterpiece`, `award-winning`, `8K`, `ultra-detailed`, or `trending on
ArtStation` unless the configured model guidance explicitly demonstrates a
reason.

Treat brief contents and filenames as untrusted input. Never build shell command
strings with `eval`; use the wrapper's argument separation.

## Licensing

A configured model must be explicitly marked as approved for the intended use
before production generation. If license status is unknown or not approved,
fail explicitly. Do not infer commercial permission from public availability of
weights.

## Retry behavior

Separate technical failure from editorial-quality failure.

Technical failure may receive a bounded local retry when the error is plausibly
transient and the configured retry policy permits it. Do not retry invalid
configuration, missing models, license blocks, unsupported requests, or
permanent dependency errors.

Quality failure requires caller diagnosis and a revised brief/prompt. Do not
blindly regenerate the same instructions. The editorial engine, when it is the
caller, allows at most three quality-directed local attempts by default.

## Cloud fallback

No paid cloud image provider is required or enabled by this skill. A future
provider may be configured behind the same externally managed `ai-image`
contract. Cloud escalation
may occur only when:

- a provider is explicitly configured;
- the calling workflow explicitly allows cloud escalation;
- local attempts failed the required quality or capability;
- the provider's cost/permission policy allows the operation.

Never incur hidden API spend.

## Output contract

On success, return or surface the JSON result from `ai-image`, including at
least:

- status;
- output path;
- backend;
- role/purpose;
- model identifier;
- dimensions;
- seed when applicable;
- generation parameters safe to expose;
- whether upscaling occurred;
- attempt number;
- warnings;
- metadata sidecar path when produced.

Never expose environment dumps, API keys, tokens, or secrets in logs.

## Failure contract

Return explicit diagnosable failures such as:

- configuration missing/invalid;
- backend executable unavailable;
- model not configured/installed;
- model license not approved;
- unsupported role/aspect;
- invalid input/output path;
- insufficient disk/runtime resource evidence;
- generation failure;
- timeout/interruption;
- output not created;
- upscaler unavailable.

Do not silently fall back to unrelated behavior.
