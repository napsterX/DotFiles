#!/usr/bin/env bash
set -Eeuo pipefail

CLAUDE_ROOT="${CLAUDE_ROOT:-$HOME/.claude}"
EDITORIAL_CONFIG_ROOT="${EDITORIAL_CONFIG_ROOT:-$CLAUDE_ROOT/editorial}"
PURGE_CONFIG=false

usage() {
  cat <<'USAGE'
Usage: ./uninstall.sh [--purge-config]

Removes the editorial-engine, local-image-generation, and article compatibility
shim from the local Claude installation. It intentionally leaves the DotFiles
backup untouched.

The ai-image executable and all ai-image configuration are externally managed
and are NEVER modified, removed, backed up, or otherwise touched by this script.

Options:
  --purge-config  Also remove ~/.claude/editorial.
                  Without this flag, user-editable editorial configuration is kept.
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

if [[ "$PURGE_CONFIG" == true ]]; then
  rm -rf "$EDITORIAL_CONFIG_ROOT"
else
  rm -f "$EDITORIAL_CONFIG_ROOT/visual-style.dist.md"
fi

printf 'Removed editorial-engine, local-image-generation, and compatibility article shim.\n'
printf 'ai-image runtime/configuration was not touched.\n'
if [[ "$PURGE_CONFIG" == true ]]; then
  printf 'Removed editorial configuration: %s\n' "$EDITORIAL_CONFIG_ROOT"
else
  printf 'Preserved editorial visual style: %s/visual-style.md\n' "$EDITORIAL_CONFIG_ROOT"
fi
printf 'DotFiles backup was not modified.\n'
