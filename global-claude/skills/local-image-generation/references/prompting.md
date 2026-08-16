# Prompt construction

Transform the caller's visual objective into a concrete brief without replacing
its idea with generic AI-art language.

## Preserve

- purpose and audience;
- actual editorial/conceptual idea;
- subjects and their relationships;
- required objects and forbidden objects;
- composition, hierarchy, crop, and negative-space requirements;
- visual medium and photographic/illustrative language;
- lighting and environment only when they matter;
- authenticity/evidence constraints;
- exact visible text only when intentionally requested;
- specific elements that must remain unchanged during edits.

## Default no-text policy

For every non-typography generation, assume the deliverable is the underlying
image only unless the caller explicitly requests visible text.

A good brief should make that concrete when useful:

```text
Image only. No headline, caption, typography, letters, numbers, logos,
watermarks, signage, magazine-cover layout, poster layout, UI chrome, or
other graphic-design overlay unless explicitly required by the scene.
```

Do not rely on prompting alone. The visual review must still reject accidental
text if it appears.

## Be visual and causal

Prefer instructions that change pixels or composition:

- `subject occupies the left third with open negative space on the right`;
- `three distinct workstreams converge on one human operator`;
- `soft side light through tall windows, no neon sci-fi glow`;
- `same person, pose, architecture, and camera angle; change only the jacket`.

Avoid adjective piles with no operational meaning.

Do not add boilerplate such as `masterpiece`, `award-winning`, `8K`,
`ultra-detailed`, `best quality`, or `trending on ArtStation` unless runtime
model guidance explicitly proves it helps.

## Retry prompts

A quality retry must encode the diagnosed failure, not simply repeat the first
brief with a new seed.

Example after accidental typography:

```text
Regenerate the same underlying photographic concept. Do not create any cover,
headline, caption, letters, words, logos, signage, or design overlay. Leave clean
negative space only; publication text will be added later outside the image.
```

Example after generic stock-photo output:

```text
Keep the business subject, but use a wider art-directed composition in which the
architecture and light carry the visual idea. Avoid centered corporate headshot
or generic stock-photo framing.
```

## Editing briefs

Use a three-part edit brief:

1. **Change** - exactly what should change.
2. **Preserve** - what must remain visually stable.
3. **Reject additions** - what must not be introduced.

Example:

```text
Change: make the suit medium charcoal grey with subtle wool texture.
Preserve: same person, face, pose, framing, camera position, architecture,
lighting, shadows, white shirt, and dark tie.
Do not add: text, logos, extra people, objects, signs, or background changes.
```

## Authenticity

Do not fabricate a real screenshot, dashboard, document, legal notice,
historical event image, news photograph, scientific evidence, or other artifact
when the request requires authenticity. Use real source material or deterministic
rendering instead.
