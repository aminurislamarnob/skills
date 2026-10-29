#!/bin/sh
# grab.sh <name> [shots-dir]
# Copy the newest screenshot Claude in Chrome saved (computer → screenshot/zoom with
# save_to_disk) into <shots-dir>/<name>.<ext>. shots-dir defaults to ./shots.
set -e
name="$1"
dest="${2:-shots}"
[ -n "$name" ] || { echo "usage: grab.sh <name> [shots-dir]" >&2; exit 1; }

latest="$(ls -t "${TMPDIR:-/tmp}"/claude-chrome-screenshots-*/* 2>/dev/null | head -1)"
[ -n "$latest" ] || { echo "no saved Chrome screenshot found under ${TMPDIR:-/tmp}" >&2; exit 1; }

mkdir -p "$dest"
ext="${latest##*.}"
cp "$latest" "$dest/$name.$ext"
echo "saved $dest/$name.$ext"
