#!/usr/bin/env bash
set -euo pipefail

# ship.sh — take the current branch from "edited" to "merged and gone".
#
#   commit  -> push  -> pull request  -> merge  -> delete branch (local + remote)
#
# Every step checks whether it has already happened and skips when it has, so
# the script can be re-run after any failure and picks up where it stopped.
#
# Usage:
#   ship.sh [-m <commit message>] [-t <PR title>] [-b <PR body file>]
#           [--branch <name>] [--method merge|squash|rebase] [--base <branch>]
#
#   -m        Commit message. Required only when the working tree is dirty.
#   -t / -b   PR title and body file. Used only when no PR exists yet;
#             without them the PR is filled from the commits (gh --fill).
#   --branch  Branch to create when the script starts on the default branch.
#   --method  Merge method. Default: the first of merge, squash, rebase the
#             repository allows.
#   --base    Base branch. Default: the repository's default branch.
#
# Needs: git, gh (logged in). Never bypasses required checks or reviews: when
# GitHub refuses the merge, the script stops and leaves the branch in place.

msg="" title="" body_file="" new_branch="" method="" base=""
while [ $# -gt 0 ]; do
  case "$1" in
    -m) msg="$2"; shift 2 ;;
    -t) title="$2"; shift 2 ;;
    -b) body_file="$2"; shift 2 ;;
    --branch) new_branch="$2"; shift 2 ;;
    --method) method="$2"; shift 2 ;;
    --base) base="$2"; shift 2 ;;
    -h|--help) sed -n '3,25p' "$0"; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; exit 2 ;;
  esac
done

say()  { printf '%s\n' "$*"; }
step() { printf '\n== %s\n' "$*"; }
die()  { printf 'error: %s\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------- preflight
git rev-parse --show-toplevel >/dev/null 2>&1 || die "not inside a git repository"
command -v gh >/dev/null || die "gh (GitHub CLI) is not installed"
gh auth status >/dev/null 2>&1 || die "gh is not logged in; run: gh auth login"
git remote get-url origin >/dev/null 2>&1 || die "no 'origin' remote"

if [ -z "$base" ]; then
  base="$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || true)"
  [ -n "$base" ] || base="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##' || true)"
  [ -n "$base" ] || die "could not determine the default branch; pass --base"
fi

branch="$(git branch --show-current)"
[ -n "$branch" ] || die "detached HEAD; check out a branch first"

git fetch --quiet origin

# ------------------------------------------------------- leave the base branch
if [ "$branch" = "$base" ]; then
  step "branch"
  dirty="$(git status --porcelain)"
  ahead="$(git rev-list --count "origin/$base..HEAD" 2>/dev/null || echo 0)"
  if [ -z "$dirty" ] && [ "$ahead" = "0" ]; then
    say "nothing to ship: on $base with a clean tree and no unpushed commits"
    exit 0
  fi
  [ -n "$new_branch" ] || die "on $base; pass --branch <name> to create a branch for these changes"
  git show-ref --verify --quiet "refs/heads/$new_branch" && die "branch $new_branch already exists; check it out and re-run"
  git switch -c "$new_branch" >/dev/null
  if [ "$ahead" != "0" ]; then
    # The unpushed commits now live on the new branch; put local base back on origin.
    git branch -f "$base" "origin/$base"
    say "moved $ahead unpushed commit(s) from $base to $new_branch"
  fi
  branch="$new_branch"
  say "created $branch"
fi

# ------------------------------------------------------------------- commit
step "commit"
if [ -n "$(git status --porcelain)" ]; then
  [ -n "$msg" ] || die "working tree has changes; pass -m <commit message>"
  git add -A
  git commit --quiet -m "$msg"
  say "committed: $(git log -1 --format=%s)"
else
  say "skipped: working tree clean"
fi

# --------------------------------------------------------------------- push
step "push"
if git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
  behind="$(git rev-list --count 'HEAD..@{u}')"
  [ "$behind" = "0" ] || die "origin/$branch has $behind commit(s) you don't have; pull first"
  ahead="$(git rev-list --count '@{u}..HEAD')"
  if [ "$ahead" = "0" ]; then
    say "skipped: origin/$branch already has every commit"
  else
    git push --quiet origin HEAD
    say "pushed $ahead commit(s)"
  fi
elif git ls-remote --exit-code --heads origin "$branch" >/dev/null 2>&1; then
  git branch --set-upstream-to "origin/$branch" >/dev/null
  ahead="$(git rev-list --count '@{u}..HEAD')"
  if [ "$ahead" = "0" ]; then say "skipped: origin/$branch already has every commit"; else git push --quiet origin HEAD; say "pushed $ahead commit(s)"; fi
else
  git push --quiet -u origin HEAD
  say "pushed new branch origin/$branch"
fi

# ------------------------------------------------------------- pull request
step "pull request"
pr_json="$(gh pr list --head "$branch" --base "$base" --state all --json number,state,url --limit 20)"
pr_number="$(printf '%s' "$pr_json" | jq -r '[.[] | select(.state=="OPEN")][0].number // empty')"
pr_state="OPEN"
if [ -z "$pr_number" ]; then
  pr_number="$(printf '%s' "$pr_json" | jq -r '[.[] | select(.state=="MERGED")][0].number // empty')"
  [ -n "$pr_number" ] && pr_state="MERGED"
fi
if [ -z "$pr_number" ]; then
  args=(--base "$base" --head "$branch")
  if [ -n "$title" ]; then
    args+=(--title "$title")
    if [ -n "$body_file" ]; then args+=(--body-file "$body_file"); else args+=(--body ""); fi
  else
    args+=(--fill)
  fi
  pr_url="$(gh pr create "${args[@]}")"
  pr_number="${pr_url##*/}"
  say "created #$pr_number $pr_url"
else
  say "skipped: #$pr_number already exists ($pr_state) $(printf '%s' "$pr_json" | jq -r --argjson n "$pr_number" '.[] | select(.number==$n) | .url')"
fi

# -------------------------------------------------------------------- merge
step "merge"
if [ "$pr_state" = "MERGED" ]; then
  say "skipped: #$pr_number is already merged"
else
  if [ -z "$method" ]; then
    method="$(gh repo view --json mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed \
      -q 'if .mergeCommitAllowed then "merge" elif .squashMergeAllowed then "squash" elif .rebaseMergeAllowed then "rebase" else "" end')"
    [ -n "$method" ] || die "the repository allows no merge method"
  fi
  if ! gh pr merge "$pr_number" "--$method"; then
    die "GitHub refused to merge #$pr_number (checks, reviews or conflicts). Fix that and re-run; nothing was deleted."
  fi
  for _ in 1 2 3 4 5 6 7 8 9 10; do
    [ "$(gh pr view "$pr_number" --json state -q .state)" = "MERGED" ] && break
    sleep 2
  done
  [ "$(gh pr view "$pr_number" --json state -q .state)" = "MERGED" ] || die "#$pr_number is not reported as merged yet; re-run in a moment"
  say "merged #$pr_number ($method)"
fi

# ---------------------------------------------------------- delete branch
step "delete branch"
git switch --quiet "$base"
git pull --quiet --ff-only origin "$base"
say "on $base, up to date with origin"

if git show-ref --verify --quiet "refs/heads/$branch"; then
  git branch -D "$branch" >/dev/null   # -D: safe here, the PR is confirmed merged
  say "deleted local $branch"
else
  say "skipped local: $branch already gone"
fi

if git ls-remote --exit-code --heads origin "$branch" >/dev/null 2>&1; then
  git push --quiet origin --delete "$branch"
  say "deleted origin/$branch"
else
  say "skipped remote: origin/$branch already gone"
fi
git fetch --quiet --prune origin

printf '\nshipped: #%s merged into %s, branch %s removed\n' "$pr_number" "$base" "$branch"
