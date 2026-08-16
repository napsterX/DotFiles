---
name: local-image-generation
version: 2.1.0
summary: Generate, inspect, revise, edit, review, and optionally upscale local images through the stable ai-image v2 interface.
description: Use when the user or another workflow needs a locally generated, edited, or upscaled image on Apple Silicon. Own the local production loop from semantic routing through visual acceptance, while keeping model/backend execution behind ai-image.
argument-hint: "<brief|request> [--purpose editorial|photorealistic|conceptual|precision|fast-draft|typography|editing|upscale] [--aspect <ratio>] [--quality draft|standard|high] [--output <path>]"
user-invocable: true
disable-model-invocation: false
---

# Local Image Generation

Provide the local production layer between a caller's visual objective and the
stable `ai-image` v2 runtime.

Architecture:

`caller -> local-image-generation -> ai-image -> configured local backend -> Apple Silicon`

The caller decides whether an image is needed and what it must communicate.
This skill owns technical routing, prompt construction, actual visual inspection,
accept/reject decisions against the supplied brief, bounded local retries, edit
vs regenerate decisions, explicit fallback use, review recording, and optional
post-acceptance upscaling.

Do not call MFLUX, MLX, Hugging Face model executables, or other backend-specific
commands directly. `ai-image` is the only execution boundary.

## Required references

Read these before executing the workflow:

- [model-routing.md](references/model-routing.md)
- [prompting.md](references/prompting.md)
- [quality-guidance.md](references/quality-guidance.md)
- [licensing.md](references/licensing.md)
- [cli-contract.md](references/cli-contract.md)

## Responsibility boundary

The caller owns:

- whether an image should exist;
- editorial/factual purpose;
- intended placement and audience;
- authenticity constraints;
- any exact content that must be represented.

This skill owns:

- semantic role selection when the caller has not fixed one;
- `ai-image doctor` preflight;
- `ai-image policy` retrieval for the selected route;
- brief-to-prompt transformation;
- safe CLI invocation through `ai-image`;
- reading and visually inspecting the generated image itself;
- visual acceptance/rejection against the brief and runtime policy;
- recording every review via `ai-image review`;
- deciding edit vs regenerate after a rejected candidate;
- bounded quality attempts;
- explicit configured fallback when justified;
- optional upscaling only after acceptance in generation workflows;
- promoting the accepted candidate to the caller's final delivery path;
- returning final asset and provenance metadata.

The `ai-image` runtime owns model/backend mapping, license gates, deterministic
filenames, technical retries, process timeouts, execution safety, and metadata
sidecars.

## Hard rules

1. **Use `ai-image` only.** Never bypass it for backend-specific image commands.
2. **Inspect the image, not only JSON.** A zero exit code proves execution, not visual quality.
3. **Record review decisions.** Every candidate considered final or rejected must receive `ai-image review`.
4. **No blind quality retries.** Every retry must respond to a specific diagnosed defect.
5. **Maximum three normal visual-quality attempts.** Escalate after three instead of looping indefinitely.
6. **Fallback is explicit.** Use `--use-fallback` only after diagnosing a capability/model mismatch; never silently reroute.
7. **Prefer edit over regeneration when the composition is already good and the requested correction is local.**
8. **Upscale after acceptance.** In a generate/edit workflow, do not upscale a rejected image hoping it will become good.
9. **Text is opt-in.** For non-typography roles, reject accidental text, pseudo-headlines, logos, watermarks, signage, or magazine-cover overlays unless intentionally requested.
10. **Do not fabricate evidence.** Never create a fake screenshot, document, dashboard, historical photograph, or other evidentiary artifact when authenticity is required.
11. **Do not hide cloud spend.** No cloud provider may be used unless the caller explicitly opts in and the runtime is configured for it.
12. **Do not mutate `ai-image` runtime/config from this skill.** Runtime updates belong to the runtime maintenance workflow.
13. **Never generate, edit, or upscale directly into the caller's final delivery path.** All model output goes to derived candidate paths. The final path is written only by `ai-image promote`.
14. **Never re-run a model to obtain the requested filename.** An accepted candidate is delivered by promotion, which copies bytes. Re-rendering produces a different image than the one you inspected.
15. **Keep rejected attempts.** Rejected candidates and their review sidecars must remain on disk as the audit trail. Never use `--overwrite` to replace an earlier attempt.

## Candidate and delivery paths

The caller's requested path is a delivery destination, not a working path.
Derive candidate paths from it automatically.

For a requested final path of `foo.png`:

| Attempt | `--output` passed to `ai-image` | File the runtime writes |
|---|---|---|
| 1 | `foo.candidate.png` | `foo.candidate.png` |
| 2 | `foo.candidate.png` with `--quality-attempt 2` | `foo.candidate.attempt-02.png` |
| 3 | `foo.candidate.png` with `--quality-attempt 3` | `foo.candidate.attempt-03.png` |

Insert `.candidate` before the requested suffix, then let the runtime derive its
own `.attempt-NN` naming. Never pass the caller's final filename to `generate`,
`edit`, or `upscale`.

After a candidate is accepted, publish it with `ai-image promote`, which copies
the accepted bytes to `foo.png` without running any model.

## Stage 0 - Resolve the request

Classify the operation:

- new image -> `generate`;
- modify an existing image -> `edit`;
- resolution enhancement only -> `upscale`.

If the caller explicitly provided a semantic purpose, honor it unless it is
incompatible with the requested operation. Otherwise select the role using
`model-routing.md`.

Do not choose a model name. Choose a semantic purpose.

## Stage 1 - Preflight

Before the first image operation in a session, and after any runtime/config
change, run:

```text
ai-image doctor --json
```

Require `status = ready` and the required role in `ready_roles`. If not ready,
stop with the exact blocker. Do not work around a broken runtime.

For a generation role, retrieve its caller-visible acceptance policy:

```text
ai-image policy --purpose <role> --json
```

If an explicit fallback is being considered, inspect the fallback policy too:

```text
ai-image policy --purpose <role> --use-fallback --json
```

## Stage 2 - Construct the brief

Use `prompting.md`.

Preserve the caller's actual idea, composition, subject relationships,
authenticity constraints, crop/negative-space needs, and avoid list.

For ordinary non-typography output, default to an image-only visual with no
textual or graphic-design overlays. Do not add generic prompt spam such as
`masterpiece`, `8K`, `award-winning`, `ultra-detailed`, or `trending on
ArtStation`.

If the caller supplied a brief file, use it. If the request exists only in chat,
write a temporary brief file. Do not pass untrusted brief text through `eval` or
construct a shell command string.

## Stage 3A - Generate candidate

Use:

```text
ai-image generate \
  --brief <brief-path> \
  --purpose <role> \
  --aspect <ratio> \
  --quality <draft|standard|high> \
  --quality-attempt <N> \
  --output <candidate-base> \
  --json
```

`<candidate-base>` is the caller's requested path with `.candidate` inserted
before its suffix, never the requested path itself.

For attempt 1, `--quality-attempt 1` may be explicit or omitted. For attempts
2 and 3, always pass the attempt number and let `ai-image` create its
deterministic `.attempt-NN` filename. Never use `--overwrite` for normal
quality iteration.

If a configured fallback is deliberately selected after diagnosis, add:

```text
--use-fallback
```

and record in the final report why fallback was used.

## Stage 3B - Edit candidate or source

For direct editing or a rejected generation whose overall composition is worth
preserving, use:

```text
ai-image edit \
  --input <source-image> \
  [--reference <reference-image> ...] \
  --brief <edit-brief> \
  --quality-attempt <N> \
  --output <candidate-base> \
  --json
```

As with generation, `<candidate-base>` carries the `.candidate` marker. The
caller's final path is never an edit destination.

The edit brief must distinguish explicitly between:

- what must change;
- what must remain unchanged;
- any identity/composition/lighting/style constraints.

Use multiple `--reference` flags only when the references materially help the
requested edit.

## Stage 4 - Inspect the actual image

Read/open the candidate image using the host's image-capable file inspection.
Do not accept based only on command success, metadata, dimensions, or file size.

Evaluate the candidate against:

1. the caller's brief;
2. `ai-image policy` acceptance criteria;
3. the visual rubric in `quality-guidance.md`.

Classify the result:

- **ACCEPT** - publishable/useful for the stated purpose;
- **EDIT** - composition is good, but a localized correctable defect exists;
- **REGENERATE** - the concept/composition/medium is materially wrong;
- **FALLBACK** - repeated failure points to a primary-model capability mismatch;
- **STOP** - authenticity, licensing, runtime, or capability requirements cannot be met safely.

## Stage 5 - Record the review

For every accepted or rejected candidate, persist the decision:

```text
ai-image review \
  --input <candidate> \
  --decision accepted|rejected \
  --reason "<specific visual diagnosis>" \
  --reviewer "local-image-generation" \
  --json
```

Reasons must be concrete. Good: `unintended pseudo-headline in upper-left;
otherwise composition is strong`. Bad: `doesn't look good`.

Do not mark a candidate accepted before actually inspecting it.

## Stage 6 - Repair loop

Maximum: **3 visual-quality attempts total** for a normal local task.

After rejection:

1. diagnose the exact defect;
2. record rejection with `ai-image review`;
3. choose one repair path:
   - localized issue and strong composition -> edit;
   - wrong composition/medium/subject -> regenerate with a revised brief;
   - repeated role-specific capability failure -> explicit configured fallback;
4. use the next `--quality-attempt` number;
5. inspect again.

Do not reuse the same prompt unchanged after a quality rejection.

Fallback is normally a late repair path, not an automatic second model. Use it
when the failure pattern matches the routing guidance, not because another model
exists.

After three rejected visual attempts, stop and report the best candidate,
rejection reasons, routes attempted, and the unresolved limitation. Do not keep
sampling.

## Stage 7 - Upscale accepted output when justified

For generation/edit workflows, upscale only after a candidate has been accepted
and only when final delivery needs more pixels or restoration.

Use:

```text
ai-image upscale \
  --input <accepted-image> \
  [--resolution 2x|3x|<target>] \
  [--softness <value>] \
  --output <upscaled-candidate> \
  --json
```

The upscale destination is also a candidate path, not the caller's final path.

Inspect the upscaled result too. Upscaling can hallucinate or alter fine detail.
If it damages identity, text, geometry, or other important content, keep the
accepted non-upscaled source instead.

If the user's request is only `upscale this existing image`, direct upscaling is
allowed without inventing a prior generation-review history; still inspect the
result before claiming success.

## Stage 8 - Promote the accepted candidate

Deliver the caller's requested filename by promotion, never by regeneration:

```text
ai-image promote \
  --input <accepted-candidate> \
  --output <caller-requested-path> \
  --json
```

Promotion copies the accepted bytes, so the delivered asset is provably the
artifact you inspected. It refuses any candidate whose sidecar does not record
`review.decision = accepted`, so record the acceptance with `ai-image review`
first.

Promote the artifact the caller actually asked for. When an upscaled master was
accepted and requested, promote the upscaled candidate; otherwise promote the
accepted base candidate.

The candidate and every rejected attempt stay on disk with their sidecars. Do
not delete them to tidy up, and do not pass `--overwrite` unless the caller
explicitly asked to replace an existing delivered file.

## Stage 9 - Return the final asset

Surface at least:

- final image path;
- accepted candidate path it was promoted from;
- paths of rejected attempts retained for audit;
- operation performed;
- requested/effective role;
- actual model/backend from runtime JSON;
- visual-quality attempt count;
- acceptance decision;
- fallback used or not;
- whether an edit was used;
- whether final output was upscaled;
- metadata sidecar path;
- material warnings.

Never claim delivery of an image you did not inspect. Because promotion copies
bytes rather than re-rendering, the delivered file and the reviewed candidate are
the same image; state that as verified fact rather than assumption.

Do not dump backend environment variables, raw secrets, or unnecessary command
logs.

## Failure handling

Treat technical and visual failures separately.

Technical failures are governed by `ai-image` technical retry behavior. Do not
layer an unbounded shell retry loop on top.

Stop rather than retry for:

- invalid/missing config;
- unavailable backend executable;
- unapproved license;
- unsupported role/aspect;
- missing input/reference;
- output-path safety errors;
- permanent dependency failure;
- authenticity requirements that generation cannot satisfy.

When blocked, give the stable `ai-image` error code and the smallest actionable
remediation.

## Cloud fallback

Local-first is mandatory. Cloud is not an automatic quality escape hatch.
Only use a future cloud route when all are true:

- the runtime has a configured cloud provider;
- the caller explicitly permits it;
- local attempts cannot meet the required capability/quality;
- cost and license policy permit the operation.

Never incur hidden API spend.
