# Migration audit: article -> editorial-engine

## Preserved

- senior-editor posture rather than generic content generation;
- truth/fabrication prohibitions;
- VOICE/OPINIONS/EDITORIAL profile handling;
- topic/thesis/URL/notes/file/draft inputs;
- editorial mode taxonomy;
- thesis stress-testing and counterargument;
- claim-led research and source hierarchy;
- argument-driven structure;
- drafting for meaning before style policing;
- developmental, specificity, line, cadence, opening, ending, heading,
  read-aloud, compression, fact/source, title, and independent-review passes;
- 85/100 READY threshold, hard gates, and maximum two repair cycles;
- review-only versus rewrite behavior;
- anti-AI-slop philosophy without detector gaming or fake mistakes.

## Refactored

The former monolithic SKILL.md was split into one orchestration skill plus focused
references. This reduces instruction density without maintaining multiple copies
of the same policy.

## Added

- visual-need analysis;
- explanatory/evidentiary/photographic/conceptual/infographic classification;
- deterministic-versus-generative visual choice;
- reusable art brief and editable visual identity;
- actual-image editorial review and bounded quality-directed retries;
- accepted-asset filename/alt/caption/attribution/placement metadata;
- strict delegation boundary to local-image-generation.

## Removed or avoided

- no editorial behavior was intentionally dropped;
- no raw MFLUX/MLX commands or model-specific generation policy was added;
- no duplicate full `article` skill is retained; `article` is only a compatibility
  shim to the new source of truth.
