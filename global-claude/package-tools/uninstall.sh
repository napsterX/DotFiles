#!/usr/bin/env bash
set -Eeuo pipefail

CLAUDE_ROOT="${CLAUDE_ROOT:-$HOME/.claude}"
LOCAL_BIN_ROOT="${LOCAL_BIN_ROOT:-$HOME/.local/bin}"
AI_IMAGE_CONFIG_ROOT="${AI_IMAGE_CONFIG_ROOT:-$HOME/.config/ai-image}"
EDITORIAL_CONFIG_ROOT="${EDITORIAL_CONFIG_ROOT:-$CLAUDE_ROOT/editorial}"
PURGE_CONFIG=false

usage() {
  cat <<'USAGE'
Usage: ./uninstall.sh [--purge-config]

Removes the editorial-engine, local-image-generation, article compatibility shim,
and ai-image CLI from the local Claude installation. It intentionally leaves the
DotFiles backup untouched.

Options:
  --purge-config  Also remove ~/.config/ai-image and ~/.claude/editorial.
                  Without this flag, user-editable configuration is kept.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --purge-config) PURGE_CONFIG=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'ERROR: unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done

rm -rf "$CLAUDE_ROOT/skills/editorial-engine" "$CLAUDE_ROOT/skills/local-image-generation"
if [[ -f "$CLAUDE_ROOT/skills/article/SKILL.md" ]] && \
   grep -q 'Compatibility entry point for the editorial-engine skill' "$CLAUDE_ROOT/skills/article/SKILL.md"; then
  rm -rf "$CLAUDE_ROOT/skills/article"
fi
if [[ -f "$LOCAL_BIN_ROOT/ai-image" ]] && grep -q 'Stable local-first image generation wrapper' "$LOCAL_BIN_ROOT/ai-image"; then
  rm -f "$LOCAL_BIN_ROOT/ai-image"
fi
if [[ "$PURGE_CONFIG" == true ]]; then
  rm -rf "$AI_IMAGE_CONFIG_ROOT" "$EDITORIAL_CONFIG_ROOT"
else
  rm -f "$AI_IMAGE_CONFIG_ROOT/defaults.dist.json" "$AI_IMAGE_CONFIG_ROOT/models.dist.json"
  rm -f "$EDITORIAL_CONFIG_ROOT/visual-style.dist.md"
fi

printf 'Removed editorial-engine, local-image-generation, compatibility article shim, and ai-image where package-owned.\n'
if [[ "$PURGE_CONFIG" == true ]]; then
  printf 'Removed ai-image configuration: %s\n' "$AI_IMAGE_CONFIG_ROOT"
  printf 'Removed editorial configuration: %s\n' "$EDITORIAL_CONFIG_ROOT"
else
  printf 'Preserved active ai-image configuration: %s\n' "$AI_IMAGE_CONFIG_ROOT"
  printf 'Preserved editorial visual style: %s/visual-style.md\n' "$EDITORIAL_CONFIG_ROOT"
fi
printf 'DotFiles backup was not modified.\n'
