# Engineering Core

- Read the relevant code, tests, repository instructions, and documented contracts before editing. Do not invent repository structure, commands, APIs, schema, or conventions.
- Prefer the smallest coherent change that fully solves the requested problem. Do not bundle unrelated refactors, cleanup, renames, dependency upgrades, or formatting churn.
- Search for the existing owner of the capability before creating code. Extend the canonical service, module, data model, or presenter instead of creating parallel business logic, state derivation, queries, or UI behavior.
- Respect existing module boundaries and public interfaces. Cross-module mutations should go through the owning module rather than writing directly to another module's state.
- When repository contracts or specifications exist, update them before or with behavior that changes their public API, lifecycle, state model, data model, or operational semantics.
- Do not preserve a materially bad design merely because it already exists. During explicit architecture work, compare alternatives, benefits, migration cost, risks, and rollback. During scoped implementation, do not perform an unrequested redesign; surface it separately.
- Use targeted search and file reads. Expand scope only when evidence shows it is necessary. Reuse current-session findings instead of repeating broad discovery.
- Avoid live external-service calls, production mutations, destructive commands, and broad automated changes unless they are required for the task and explicitly authorized.
- Repository-local instructions may specialize these rules. Flag genuine conflicts instead of silently choosing whichever instruction is convenient.
- Do not create or open pull requests unless explicitly requested. Never claim a command, test, validation, deployment, or external action was performed when it was not.
