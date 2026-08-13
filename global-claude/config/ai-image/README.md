# ai-image configuration

`defaults.json` and `models.json` define the portable shared configuration.

The installer creates/updates `.dist` copies and initializes the active files
only when they do not already exist. Existing active files are preserved.

Machine-specific overrides belong in `local.json`, which is intentionally not
provided by the package and should not contain credentials. It may override
backend executable paths, model paths, command argument templates, and role
settings.

Configuration merge order:

1. `defaults.json`
2. `models.json`
3. `local.json` when present

The next MLX/MFLUX setup task should populate actual backend executable/argv
configuration and approved model/license data. Do not place model weights here.

Backend argv templates are arrays, never shell strings. Supported placeholders
include `{model}`, `{prompt}`, `{brief}`, `{output}`, `{input}`, `{width}`,
`{height}`, `{seed}`, `{quality}`, and keys from a role's `parameters` object.

## DotFiles and machine-local overrides

The installer backs up the active portable `defaults.json` and `models.json` to
`~/git/DotFiles/global-claude/config/ai-image/`. Package defaults are retained
there as `*.dist.json` for comparison and upgrades.

`local.json` is deliberately excluded from DotFiles because it may contain
machine-specific executable/model paths or other local-only settings. Keep
credentials out of all ai-image configuration files.
