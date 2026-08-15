# Editorial visual identity

This is the packaged **generic fallback** visual identity. Repository-specific
art direction belongs in the repository publication contract, normally
`.editorial/visual-system.md`, and takes precedence when declared authoritative.
The installer may initialize the user-editable
`~/.claude/editorial/visual-style.md` as a cross-repository fallback; keep only
preferences that should apply when a repository has not supplied its own visual
system.

## Default direction

- Prefer editorial sophistication over generic stock imagery.
- Prefer a clear visual idea over decorative complexity.
- Use abstraction when it clarifies a conceptual argument; do not abstract
  concrete evidence.
- Preserve useful negative space for responsive crops and, when required,
  headline placement.
- Avoid fake interfaces, fake dashboards, and generated evidence.
- Prefer diagrams with restrained visual hierarchy and legible labels.
- Typography inside generative images is discouraged unless typography is the
  subject and the selected model is explicitly suitable for it.

## Photography

Prefer authentic photography when real people, places, products, buildings, or
events matter to the article's truth. Generated photorealism must not be used in
a way that implies a nonexistent real event or person-specific evidence.

## Conceptual illustration

Prefer deliberate editorial metaphors, spatial relationships, material texture,
and visual restraint. Avoid generic "AI art" signifiers unless the subject
specifically requires them.

## Prohibited default clichés

- glowing AI brains;
- humanoid robots as the default symbol for AI;
- hooded hackers;
- floating padlocks;
- random binary code;
- neon cyberpunk without subject justification;
- generic corporate handshakes;
- fake dashboards;
- floating holograms with no editorial function;
- rocket ships as growth;
- generic laptop-at-desk compositions.

## User-level fallback overrides

Add only durable preferences that should apply across repositories **when no
repository-specific visual system is declared**. Keep product-specific palette,
components, typography, and publication identity in the repository contract.
Keep machine-specific model details out of this file.
