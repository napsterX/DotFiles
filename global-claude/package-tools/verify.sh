#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_ROOT="${CLAUDE_ROOT:-$HOME/.claude}"
EDITORIAL_CONFIG_ROOT="${EDITORIAL_CONFIG_ROOT:-$CLAUDE_ROOT/editorial}"
AI_IMAGE_CMD="${AI_IMAGE_CMD:-ai-image}"
PACKAGE_ONLY=false
RUNTIME=false
SMOKE=false

usage() {
  cat <<'USAGE'
Usage: ./verify.sh [--package-only] [--runtime] [--smoke]

Default: validate package/tests and installed skill/editorial-config structure.
The ai-image executable/configuration are external user-managed prerequisites and
are not required or modified by the default package verification.

--package-only  Validate only the extracted package.
--runtime       Additionally require the externally managed `ai-image doctor` to
                report ready. Read-only with respect to ai-image configuration.
--smoke         Require runtime readiness and generate one temporary fast-draft
                1:1 image to prove end-to-end local generation. Implies --runtime.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --package-only) PACKAGE_ONLY=true; shift ;;
    --runtime) RUNTIME=true; shift ;;
    --smoke) SMOKE=true; RUNTIME=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'ERROR: unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done

python3 "$SCRIPT_DIR/scripts/validate_package.py" \
  --skills-root "$SCRIPT_DIR/skills" \
  --manifest "$SCRIPT_DIR/MANIFEST" \
  --agents-root "$SCRIPT_DIR/agents" \
  --agents-manifest "$SCRIPT_DIR/AGENTS_MANIFEST" \
  --run-tests

if [[ "$PACKAGE_ONLY" == true ]]; then
  printf 'Package verification: PASS\n'
  exit 0
fi

for skill in editorial-engine local-image-generation article; do
  [[ -f "$CLAUDE_ROOT/skills/$skill/SKILL.md" ]] || { printf 'ERROR: installed skill missing: %s\n' "$skill" >&2; exit 1; }
done
[[ ! -e "$CLAUDE_ROOT/skills/implementation-log" ]] || { printf 'ERROR: retired skill still installed: implementation-log\n' >&2; exit 1; }
[[ -f "$EDITORIAL_CONFIG_ROOT/visual-style.md" ]] || { printf 'ERROR: editorial visual-style.md missing\n' >&2; exit 1; }

printf 'Installed skill/editorial contracts: PASS\n'

if [[ "$RUNTIME" != true ]]; then
  printf 'External ai-image runtime: NOT_CHECKED (user-managed)\n'
  exit 0
fi

if ! command -v "$AI_IMAGE_CMD" >/dev/null 2>&1; then
  printf 'ERROR: externally managed ai-image is not resolvable: %s\n' "$AI_IMAGE_CMD" >&2
  exit 1
fi

set +e
DOCTOR_OUT="$("$AI_IMAGE_CMD" doctor --json 2>&1)"
DOCTOR_RC=$?
set -e
if [[ $DOCTOR_RC -ne 0 ]]; then
  printf '%s\n' "$DOCTOR_OUT" >&2
  printf 'ERROR: externally managed ai-image runtime is not ready.\n' >&2
  exit 1
fi

printf 'External ai-image runtime doctor: READY\n'

if [[ "$SMOKE" == true ]]; then
  TMP="$(mktemp -d "${TMPDIR:-/tmp}/ai-image-smoke.XXXXXX")"
  trap 'rm -rf "$TMP"' EXIT
  cat > "$TMP/brief.md" <<'BRIEF'
# Smoke test brief
A simple neutral geometric composition with no text, intended only to verify the
local image-generation pipeline. No people, brands, evidence, or factual claims.
BRIEF
  SMOKE_ROLE="$(printf '%s' "$DOCTOR_OUT" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(next((r for r in d.get("ready_roles", []) if r != "upscale"), ""))')"
  [[ -n "$SMOKE_ROLE" ]] || { printf 'ERROR: no ready generation role available for smoke test\n' >&2; exit 1; }
  "$AI_IMAGE_CMD" generate \
    --brief "$TMP/brief.md" --purpose "$SMOKE_ROLE" --aspect 1:1 --quality draft \
    --output "$TMP/smoke.png" --json >/dev/null
  [[ -s "$TMP/smoke.png" ]] || { printf 'ERROR: smoke image was not produced\n' >&2; exit 1; }
  printf 'External ai-image smoke generation: PASS\n'
fi
