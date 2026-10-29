#!/usr/bin/env bash
set -euo pipefail

# Dev-only script for maintainers of this repo; not a supported installer.
#
# Links every skill in the repository into the local skill directories used by
# each agent harness:
#   - ~/.claude/skills  — Claude Code
#   - ~/.agents/skills  — Codex and other Agent Skills-compatible harnesses
# Each entry is a symlink into this repo, so a `git pull` is all that's needed
# to keep installed skills up to date. Re-run after adding, removing, or
# renaming a skill.

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DESTS=("$HOME/.claude/skills" "$HOME/.agents/skills")

names=()
srcs=()
while IFS= read -r -d '' skill_md; do
  src="$(dirname "$skill_md")"
  names+=("$(basename "$src")")
  srcs+=("$src")
done < <(find "$REPO/skills" -name SKILL.md -not -path '*/node_modules/*' -not -path '*/deprecated/*' -print0)

for DEST in "${DESTS[@]}"; do
  # If $DEST is a symlink that resolves into this repo, the per-skill symlinks
  # would land inside the repo's own skills/ tree. Bail out instead.
  if [ -L "$DEST" ]; then
    resolved="$(readlink -f "$DEST")"
    case "$resolved" in
      "$REPO"|"$REPO"/*)
        echo "error: $DEST is a symlink into this repo ($resolved)." >&2
        echo "Remove it (rm \"$DEST\") and re-run; the script will recreate it as a real dir." >&2
        exit 1
        ;;
    esac
  fi

  mkdir -p "$DEST"

  for i in "${!names[@]}"; do
    name="${names[$i]}"
    src="${srcs[$i]}"
    target="$DEST/$name"

    if [ -e "$target" ] && [ ! -L "$target" ]; then
      rm -rf "$target"
    fi

    ln -sfn "$src" "$target"
    echo "linked $name -> $src ($DEST)"
  done
done
