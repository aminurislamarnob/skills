"""Count one person's share of the work in one or more git repositories.

Run: python3 -I git_stats.py --repo PATH [--repo PATH ...] --author PATTERN [--author PATTERN ...]
                             [--ref develop] [--since 2026-06-01] [--until 2026-11-07]
                             [--tz Asia/Dhaka] [--coauthor 'claude'] [--decisions 'docs/adr/*.md']
                             [--github] [--login GITHUB_LOGIN] [--exclude-base 'project/']
                             --out WORK_DIR

Writes two files into WORK_DIR:

  stats.json    totals, per-repo counts, a chart series, and (with --github) PR and issue counts
  subjects.txt  every matching commit of the person, oldest first: "YYYY-MM-DD HH:MM  repo  subject"

--author is a case-insensitive regular expression matched against the author's email and name;
pass one per identity the person has committed under. --ref defaults to each repo's default
branch (origin/HEAD, then HEAD). Merge commits are left out. Dates are the author date, in --tz
when given, else the machine's zone.

--coauthor counts the person's commits whose Co-authored-by trailer matches the pattern (for
"N of my commits were pair-written with an AI agent"). --decisions counts files matching the
glob, per repo, by who added them (decision records, RFCs). --github asks the gh CLI for merged
pull requests and issues of each repo's GitHub remote; --login names the person there, and
--exclude-base drops PRs whose base branch matches the pattern (a client branch, say).

stats.json "series" picks its own granularity: days for a window of two weeks or less, weeks
(starting Monday) up to 40 weeks, months beyond that. build_page.py draws it as the timeline.
"""
import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import subprocess
import sys

SEP, END = "\x1f", "\x1e"


def git(repo, *args, env=None):
    out = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, env=env)
    if out.returncode:
        raise SystemExit(f"git {' '.join(args)} failed in {repo}:\n{out.stderr.strip()}")
    return out.stdout


def default_ref(repo):
    for ref in ("origin/HEAD", "HEAD"):
        r = subprocess.run(["git", "-C", repo, "rev-parse", "--abbrev-ref", ref], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return "HEAD"


def commits(repo, ref, since, until, env):
    fmt = SEP.join(["%H", "%ad", "%ae", "%an", "%s", "%(trailers:key=Co-authored-by,valueonly,separator=%x2C)"]) + END
    args = ["log", ref, "--no-merges", "--date=format-local:%Y-%m-%d %H:%M", f"--pretty=format:{fmt}"]
    rows = []
    for chunk in git(repo, *args, env=env).split(END):
        chunk = chunk.strip("\n")
        if not chunk:
            continue
        h, date, email, name, subject, coauth = (chunk.split(SEP) + [""] * 6)[:6]
        # Filter on the author date here: git's --since/--until use the committer date, which a
        # rebase or a squash-merge moves, and stop walking history at the first older commit.
        if (since and date[:10] < since) or (until and date[:10] > until):
            continue
        rows.append({"hash": h, "date": date, "email": email, "name": name, "subject": subject, "coauthors": coauth})
    return rows


def decisions_added(repo, ref, pattern):
    """Map each file matching the glob to the author who added it."""
    out = git(repo, "log", ref, "--diff-filter=A", "--name-only", "--format=@@%an <%ae>")
    who, added = None, {}
    for line in out.splitlines():
        if line.startswith("@@"):
            who = line[2:]
        elif line.strip() and fnmatch.fnmatch(line.strip(), pattern):
            added[line.strip()] = who  # git log is newest first; the last write is the first add
    return added


def gh_json(args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode:
        print(f"warning: gh {' '.join(args[:3])} failed: {r.stderr.strip()[:200]}", file=sys.stderr)
        return []
    return json.loads(r.stdout or "[]")


def github_slug(repo):
    url = git(repo, "remote", "get-url", "origin").strip()
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", url)
    return m.group(1) if m else None


def series(dates_me, dates_team, start, end):
    span = (end - start).days + 1
    if span <= 14:
        gran, key = "day", (lambda d: d)
        buckets, cur = [], start
        while cur <= end:
            buckets.append(cur)
            cur += dt.timedelta(days=1)
    elif span <= 40 * 7:
        gran = "week"
        first = start - dt.timedelta(days=start.weekday())
        key = lambda d: d - dt.timedelta(days=d.weekday())
        buckets, cur = [], first
        while cur <= end:
            buckets.append(cur)
            cur += dt.timedelta(days=7)
    else:
        gran = "month"
        key = lambda d: d.replace(day=1)
        buckets, cur = [], start.replace(day=1)
        while cur <= end:
            buckets.append(cur)
            cur = (cur.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    rows = {b: {"start": b.isoformat(), "me": 0, "team": 0} for b in buckets}
    for d in dates_me:
        rows[key(d)]["me"] += 1
    for d in dates_team:
        rows[key(d)]["team"] += 1
    return {"granularity": gran, "first": start.isoformat(), "last": end.isoformat(), "rows": list(rows.values())}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", action="append", required=True)
    ap.add_argument("--author", action="append", required=True)
    ap.add_argument("--ref")
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--tz")
    ap.add_argument("--coauthor")
    ap.add_argument("--decisions")
    ap.add_argument("--github", action="store_true")
    ap.add_argument("--login")
    ap.add_argument("--exclude-base")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    env = dict(os.environ)
    if a.tz:
        env["TZ"] = a.tz
    who = re.compile("|".join(f"(?:{p})" for p in a.author), re.I)
    co = re.compile(a.coauthor, re.I) if a.coauthor else None
    is_me = lambda r: bool(who.search(r["email"]) or who.search(r["name"]))

    stats = {"generated": dt.date.today().isoformat(), "authors": a.author, "repos": [], "totals": {}}
    subjects, me_dates, team_dates = [], [], []
    for repo in a.repo:
        repo = os.path.abspath(os.path.expanduser(repo))
        name = os.path.basename(repo.rstrip("/"))
        ref = a.ref or default_ref(repo)
        rows = commits(repo, ref, a.since, a.until, env)
        mine = [r for r in rows if is_me(r)]
        entry = {
            "name": name, "path": repo, "ref": ref,
            "commits": len(rows), "mine": len(mine), "team": len(rows) - len(mine),
            "first_commit": rows[-1]["date"] if rows else None,
            "my_first_commit": mine[-1]["date"] if mine else None,
            "my_last_commit": mine[0]["date"] if mine else None,
            "team_authors": sorted({r["name"] for r in rows if not is_me(r)}),
        }
        if co:
            entry["mine_coauthored"] = sum(1 for r in mine if co.search(r["coauthors"]))
        if a.decisions:
            added = decisions_added(repo, ref, a.decisions)
            entry["decisions"] = {"total": len(added), "mine": sum(1 for v in added.values() if v and who.search(v)),
                                  "files": added}
        if a.github:
            slug = github_slug(repo)
            if slug:
                prs = gh_json(["pr", "list", "-R", slug, "--state", "merged", "--limit", "3000", "--json", "author,baseRefName"])
                if a.exclude_base:
                    prs = [p for p in prs if not re.search(a.exclude_base, p["baseRefName"])]
                issues = gh_json(["issue", "list", "-R", slug, "--state", "all", "--limit", "3000", "--json", "author"])
                login = (a.login or "").lower()
                entry["github"] = {
                    "slug": slug,
                    "merged_prs": len(prs), "my_merged_prs": sum(1 for p in prs if (p["author"] or {}).get("login", "").lower() == login),
                    "issues": len(issues), "my_issues": sum(1 for i in issues if (i["author"] or {}).get("login", "").lower() == login),
                }
        stats["repos"].append(entry)
        for r in rows:
            d = dt.date.fromisoformat(r["date"][:10])
            (me_dates if is_me(r) else team_dates).append(d)
        subjects += [f'{r["date"]}  {name}  {r["subject"]}' for r in mine]

    t = stats["totals"]
    for k in ("commits", "mine", "team", "mine_coauthored"):
        if any(k in r for r in stats["repos"]):
            t[k] = sum(r.get(k, 0) for r in stats["repos"])
    for k in ("merged_prs", "my_merged_prs", "issues", "my_issues"):
        if any("github" in r for r in stats["repos"]):
            t[k] = sum(r.get("github", {}).get(k, 0) for r in stats["repos"])
    if a.decisions:
        t["decisions"] = sum(r["decisions"]["total"] for r in stats["repos"])
        t["my_decisions"] = sum(r["decisions"]["mine"] for r in stats["repos"])

    all_dates = me_dates + team_dates
    if all_dates:
        start = dt.date.fromisoformat(a.since) if a.since else min(all_dates)
        end = dt.date.fromisoformat(a.until) if a.until else max(all_dates)
        stats["series"] = series([d for d in me_dates if start <= d <= end],
                                 [d for d in team_dates if start <= d <= end], start, end)

    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "stats.json"), "w") as f:
        json.dump(stats, f, indent=2)
    with open(os.path.join(a.out, "subjects.txt"), "w") as f:
        f.write("\n".join(sorted(subjects)) + "\n")
    print(json.dumps(stats["totals"]))
    print(f"wrote {a.out}/stats.json and {a.out}/subjects.txt ({len(subjects)} commits)")


if __name__ == "__main__":
    main()
