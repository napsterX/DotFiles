# Visual quality, review, and retries

A successful backend process is only a candidate. Visual acceptance requires
inspection of the actual image.

## Technical gate

Before visual review, confirm from runtime JSON/sidecar:

- process succeeded;
- output exists and is non-empty;
- expected dimensions are plausible;
- metadata sidecar exists when configured;
- output is not a temporary path;
- no secret/environment dump was surfaced;
- technical retry count is bounded and visible.

Technical retry behavior belongs to `ai-image`. Do not add an unbounded wrapper
retry loop.

## Visual hard-reject criteria

Reject when any applies unless explicitly intended by the brief:

- accidental words, pseudo-headlines, letters, numbers, logos, watermarks, signage, or magazine/poster UI;
- broken anatomy, face, hands, limbs, object geometry, perspective, reflections, or impossible structure that is visible at delivery size;
- wrong subject, missing required subject, duplicate subject, or materially wrong relationship between subjects;
- major prompt failure in composition, hierarchy, crop, or negative space;
- wrong medium, such as infographic/cartoon output when photography was requested;
- fabricated evidence or realistic-looking fake source material when authenticity is required;
- identity drift during an edit where identity preservation was requested;
- broad background/composition drift during a local edit;
- unreadable or incorrect intentional typography when exact text matters;
- obvious generation artifacts that make the asset unprofessional at intended size.

## Soft quality criteria

Use judgment against the brief for:

- generic stock-photo appearance when the caller asked for distinctive editorial art direction;
- overprocessed/waxy/hyper-detailed skin;
- weak hierarchy or focal point;
- visually noisy backgrounds;
- unusable crop for the intended placement;
- insufficient negative space for downstream layout;
- lighting/style inconsistent with the requested mood;
- conceptual image that communicates the wrong metaphor even if technically attractive.

A soft failure can still be a rejection when it defeats the purpose of the asset.

## ACCEPT / EDIT / REGENERATE / FALLBACK

**ACCEPT** when the image satisfies the brief and no material hard-reject exists.
Record with `ai-image review --decision accepted`.

**EDIT** when the composition is good and the defect is localized/correctable
while preservation matters.

**REGENERATE** when the overall composition, visual medium, relationship, or
concept is wrong.

**FALLBACK** when repeated failure indicates a primary-route capability mismatch
and the configured fallback addresses that mismatch.

## Candidate retention

Every attempt is written to a derived candidate path, never to the caller's
requested delivery filename. Rejected candidates and their review sidecars stay
on disk. They are the evidence that a rejection happened and why, and deleting or
overwriting them destroys the audit trail.

Only `ai-image promote` writes the caller's final path, and it copies the
accepted bytes rather than re-running a model. Never re-render an accepted
candidate to obtain the requested filename: the backend is not byte-deterministic
even at a fixed seed, so a re-render delivers an image nobody inspected.

## Review recording

Every rejected candidate must be recorded with a concrete reason before the next
quality attempt. Every final candidate must be recorded as accepted.

Acceptance is also a precondition for delivery: the runtime refuses to promote a
candidate whose sidecar does not record `review.decision = accepted`.

Good rejection reason:

```text
Unintended pseudo-headline in upper-left and two UI-like labels; composition is
otherwise strong. Regenerate with stricter image-only instructions.
```

Weak rejection reason:

```text
Bad image.
```

## Bounded quality loop

Default maximum: 3 visual-quality attempts total.

Attempt 1 -> inspect -> accept or diagnose.

Attempt 2 -> revised brief/edit based on diagnosis -> inspect.

Attempt 3 -> final targeted repair or explicit configured fallback when justified
-> inspect.

After three rejections, stop. Return the best candidate and explain why it still
failed rather than continuing to sample.

## Seed behavior

Changing the seed can be part of a revised quality attempt, but never the entire
repair strategy after a diagnosed failure. The brief or route should change in a
way that addresses the defect.

## Upscaling

In a generation/edit workflow:

1. accept the base candidate first;
2. upscale only when final size/restoration justifies it;
3. inspect the upscaled result;
4. keep the original accepted image if upscaling damages identity, geometry,
   typography, or texture;
5. promote whichever accepted artifact the caller asked to receive.

Never describe generative upscaling as recovery of factual detail that was not
present in the source.
