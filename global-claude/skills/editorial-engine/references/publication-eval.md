# Rendered publication evaluation

Use this evaluation only when a piece is being prepared for a rendered
publication surface (for example a website article) and the repository contract
or user request makes presentation quality material.

This verdict is **independent** from `eval.md`. A strong article can fail
publication presentation, and a beautiful page can fail editorial integrity.

## Evidence requirement

Evaluate the actual rendered result whenever the repository contract requires
rendered review. Prefer full-page captures at the declared breakpoints plus
focused inspection of figures/components when necessary.

Source markup or CSS alone is not sufficient evidence for
`PUBLICATION_READY` when rendered review is required.

If the renderer cannot be run or inspected, use `PUBLICATION_UNVERIFIED`; do not
silently promote an inferred design judgment to readiness.

## Hard gates

Every applicable gate must pass. Numeric score cannot compensate for failure.

1. The page has a clear reading path and major hierarchy is immediately
   distinguishable.
2. Body typography and prose measure are readable at required breakpoints.
3. Navigation/chrome does not materially compete with the article for attention.
4. No figure, chart, screenshot, diagram, image, caption, or callout is broken,
   misleading, illegible, badly cropped, or presented as evidence when it is not.
5. Repository-required brand, terminology, accessibility, and renderer quality
   gates pass when declared by the contract.
6. Component usage matches its semantic purpose; repeated boxes/modules do not
   create a documentation-like wall unless the selected archetype intentionally
   is deep reference.
7. No obvious generic/generated visual is accepted merely to add decoration.
8. Required desktop/mobile composition is coherent; there is no breakpoint where
   the article becomes materially harder to understand or navigate.
9. No unresolved visual or interaction defect materially damages trust,
   comprehension, or the article's intended action.

If any applicable hard gate fails, the rendered publication is not ready.

## Scoring rubric — 100 points

### 1. Reading hierarchy — 15

Evaluate distinction among title, deck/meta, H2/H3 levels, prose, captions,
callouts, and major conceptual transitions.

### 2. Typography and readability — 15

Evaluate prose measure, line height, paragraph spacing, text contrast, heading
scale, rhythm, and sustained reading comfort.

### 3. Information density and cadence — 15

Evaluate whether the page alternates density intentionally, avoids long
monotony, and gives major transitions enough visual breathing room without
wasting space.

### 4. Composition and module fit — 15

Evaluate whether prose, lists, tables, figures, checklists, callouts, related
content, and other modules are used because they improve communication rather
than because the renderer exposes them.

### 5. Visual/art-direction quality — 15

Evaluate useful visual concept, quality, consistency, factual appropriateness,
asset provenance, hierarchy, and whether visuals feel deliberately part of the
publication rather than generic attachments.

### 6. Navigation and chrome restraint — 10

Evaluate TOC depth, side rails, dividers, controls, promotional modules, and
whether ancillary UI supports rather than overwhelms reading.

### 7. Responsive composition — 10

Evaluate required breakpoints, image crops, tables, navigation changes, callout
behavior, heading wraps, and touch/interaction layout where applicable.

### 8. Brand coherence — 5

Evaluate consistency with the repository-declared visual/brand system without
rewarding decorative branding that reduces readability.

## Fresh-page challenge

Before assigning the verdict, answer internally:

1. Where does the eye go first, second, and third?
2. Which viewport is visually busiest and why?
3. Is there any long region with no meaningful hierarchy/cadence change?
4. Which component is repeated too often?
5. Is the TOC/navigation proportionate to the selected archetype?
6. Which visual materially improves understanding, and which is merely present?
7. Does the page feel like the intended publication archetype or like generic
   documentation/marketing output?
8. Would the page still feel trustworthy with the logo removed?
9. Does mobile preserve the same editorial meaning as desktop?
10. What is the smallest design/composition change with the largest quality gain?

## Verdict

- `PUBLICATION_READY`: score 85-100 and every applicable hard gate passes.
- `PUBLICATION_REVISE`: score 70-84 or a bounded, repairable hard-gate failure.
- `PUBLICATION_REBUILD`: below 70 or presentation architecture is materially
  wrong for the article/archetype.
- `PUBLICATION_UNVERIFIED`: rendered evidence required by the contract was not
  available or could not be inspected.

Use at most two publication-repair cycles by default. Re-render and re-evaluate
from fresh evidence after each retained repair. Do not claim readiness from the
pre-repair screenshot.
