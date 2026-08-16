# ai-image v2 — local image runtime

A stable local-first command layer over the validated Apple Silicon/MFLUX image stack.

## Validated routes

| Purpose | Default model | Role |
|---|---|---|
| Editorial hero / art direction | Krea 2 Turbo | `editorial` |
| Straight photorealism / fast generation | FLUX.2 Klein 4B Q8 | `photorealistic`, `fast-draft` |
| Conceptual editorial artwork | Krea 2 Turbo | `conceptual` |
| Complex spatial/semantic precision | Qwen-Image-2512-8bit | `precision` |
| Explicit visible typography | Qwen-Image-2512-8bit | `typography` |
| Image-conditioned edit / references | FLUX.2 Klein 4B Q8 | `editing` |
| Finishing / restoration | SeedVR2 3B | `upscale` |

`conceptual` intentionally defaults to Krea after local benchmark evidence showed Qwen could turn conceptual editorial prompts into unwanted infographic/magazine layouts. Use `--use-fallback` on `conceptual` when the brief needs Qwen's stronger spatial/semantic precision.

## Install / upgrade

```bash
unzip ai-image-runtime-v2.zip
cd ai-image-runtime-v2
./verify.sh
./install.sh
```

The installer:

- backs up the existing `~/.local/bin/ai-image` and active configs under `~/.ai-image-backups/<timestamp>/`
- installs the new executable to `~/.local/bin/ai-image`
- installs portable config to `~/.config/ai-image/`
- **preserves `~/.config/ai-image/local.json` unchanged** if present
- copies the runtime to `~/git/DotFiles/global-claude/bin/ai-image`
- copies portable config/docs to `~/git/DotFiles/global-claude/config/ai-image/`
- does **not** commit or push the DotFiles repository
- does not touch model weights, Hugging Face caches, generated assets, or credentials

Use `./install.sh --no-dotfiles` only if you deliberately do not want the backup copy.

## Verify the installed runtime

```bash
ai-image version
ai-image doctor
ai-image config --json
ai-image policy --purpose editorial --json
```

A healthy installation on the validated Mac should report all eight roles ready, including `editing` and `upscale`.

## Generate

```bash
cat > /tmp/hero.md <<'EOF'
High-end editorial hero photograph about modern technology leadership.
A single executive in a dramatic contemporary architectural interior with
sculptural daylight and useful negative space.
EOF

ai-image generate \
  --brief /tmp/hero.md \
  --purpose editorial \
  --aspect 16:9 \
  --quality high \
  --seed 42 \
  --output "$HOME/ai-image/outputs/hero.png"
```

The wrapper injects the role's image-only policy before the brief. It stores only prompt/brief hashes in the sidecar; dry-run command output redacts the prompt content.

## Bounded visual-quality loop

The binary does **not** claim to visually judge an image. Claude Code or another vision-capable caller should inspect the candidate using the policy criteria:

```bash
ai-image policy --purpose editorial --json
```

If attempt 1 is rejected, generate attempt 2 using the same requested output path:

```bash
ai-image generate \
  --brief /tmp/hero.md \
  --purpose editorial \
  --aspect 16:9 \
  --quality high \
  --quality-attempt 2 \
  --output "$HOME/ai-image/outputs/hero.png"
```

The actual file becomes:

```text
hero.attempt-02.png
```

Record the external review result:

```bash
ai-image review \
  --input "$HOME/ai-image/outputs/hero.attempt-02.png" \
  --decision rejected \
  --reason "unwanted typography" \
  --reviewer claude-code
```

After the bounded quality loop, an explicit fallback route can be selected:

```bash
ai-image generate \
  --brief /tmp/hero.md \
  --purpose editorial \
  --use-fallback \
  --aspect 16:9 \
  --quality high \
  --quality-attempt 3 \
  --output "$HOME/ai-image/outputs/hero.png"
```

There is no silent model switch.

## Precision route

For difficult object counts, spatial relationships, or knowledge-heavy scenes:

```bash
ai-image generate \
  --brief /tmp/precise-scene.md \
  --purpose precision \
  --aspect 16:9 \
  --quality high \
  --output "$HOME/ai-image/outputs/precise.png"
```

## Edit with one or more references

MFLUX FLUX.2 supports image-conditioned editing with one or more reference images. The wrapper exposes that directly:

```bash
cat > /tmp/edit.md <<'EOF'
Put the eyeglasses from the reference image on the person. Preserve the person's
identity, pose, background, lighting, suit, and all unrelated regions.
EOF

ai-image edit \
  --input person.png \
  --reference glasses.png \
  --brief /tmp/edit.md \
  --seed 42 \
  --output edited.png
```

Repeat `--reference` for multiple references:

```bash
ai-image edit \
  --input person.png \
  --reference glasses.png \
  --reference jacket.png \
  --brief /tmp/edit.md \
  --output edited.png
```

The sidecar records SHA-256 hashes of the source and each reference.

## Upscale only after acceptance

```bash
ai-image upscale \
  --input accepted.png \
  --output accepted@2x.png
```

Defaults are SeedVR2 3B, `2x`, softness `0.5`. Override when warranted:

```bash
ai-image upscale \
  --input accepted.png \
  --resolution 2160 \
  --softness 0.25 \
  --output accepted-2160.png
```

Do not upscale automatically just because the command exists; preserve the accepted source when SeedVR2 invents unwanted detail.

## Metadata sidecar

Successful operations create `<image>.ai-image.json`. v2 records:

- ai-image and detectable MFLUX versions
- requested/effective role and explicit fallback state
- backend + resolved executable
- model and license note
- acceptance policy / retry guidance
- seed, dimensions, generation parameters
- quality attempt vs technical retry attempt
- brief SHA-256 and effective-prompt SHA-256, not raw brief text
- source/reference SHA-256 for edit/upscale
- duration, output dimensions, and safe cache locations
- external review decision when `ai-image review` is used

## Exit codes

- `0` success
- `3` configuration/request error
- `4` runtime/readiness/license error
- `5` backend process failure or timeout

All operational commands support `--json` where structured agent consumption is useful.

## Configuration layout

```text
~/.config/ai-image/
  defaults.json
  defaults.dist.json
  models.json
  models.dist.json
  local.json          # optional; preserved on upgrade and excluded from DotFiles copy
```

Merge order remains:

1. `defaults.json`
2. `models.json`
3. `local.json`

No model weights belong in this directory.
