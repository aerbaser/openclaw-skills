#!/usr/bin/env python3
import argparse, csv, json, sys
from datetime import datetime, timezone
from pathlib import Path

NOW = datetime.now(timezone.utc)

def days_since(ts):
    if not ts:
        return 99999
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return 99999
    return (NOW - dt).days

def has_topics(repo):
    return bool(repo.get("repositoryTopics", {}).get("nodes"))

def classify(repo):
    updated_days = days_since(repo.get("pushedAt") or repo.get("updatedAt"))
    name = repo["name"].lower()
    open_prs = repo.get("pullRequests", {}).get("totalCount", 0)
    open_issues = repo.get("issues", {}).get("totalCount", 0)
    weak_meta = not repo.get("description") and not has_topics(repo)

    suspicious_name = any(token in name for token in [
        "tmp", "temp", "copy", "clone", "backup", "old", "sandbox", "playground", "test", "draft", "agent"
    ])

    if repo.get("isArchived"):
        return "archive", "keep_archived", "already archived"

    if repo.get("isTemplate"):
        return "template", "convert_to_template", "marked as template repository"

    if repo.get("isFork"):
        if updated_days > 365 and open_prs == 0:
            return "fork", "archive_candidate", "fork looks inactive"
        return "fork", "keep_fork", "fork retained"

    if repo.get("diskUsage", 0) == 0 and weak_meta:
        return "parking", "delete_candidate", "empty or near-empty and undefined"

    if updated_days > 365 and open_prs == 0 and open_issues == 0 and weak_meta:
        return "archive", "archive_candidate", "inactive and weakly defined"

    if suspicious_name and updated_days > 180 and open_prs == 0:
        return "lab", "archive_candidate", "looks like experiment or duplicate"

    if weak_meta:
        return "parking", "promote_or_retire", "needs definition or retirement"

    if updated_days > 180 and open_prs == 0:
        return "managed", "harden_baseline", "looks real but needs baseline review"

    return "managed", "keep_managed", "active repo"

def render_markdown(rows):
    lines = []
    lines.append("# Repository classification")
    lines.append("")
    lines.append("| Repo | Class | Action | Reason |")
    lines.append("|---|---|---|---|")
    for row in rows:
        lines.append(f"| {row['nameWithOwner']} | {row['class']} | {row['action']} | {row['reason']} |")
    return "\n".join(lines)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--inventory", required=True)
    p.add_argument("--out", help="write CSV plan")
    p.add_argument("--format", choices=["markdown", "json", "pretty"], default="pretty")
    args = p.parse_args()

    data = json.loads(Path(args.inventory).read_text(encoding="utf-8"))
    rows = []
    for repo in data["repositories"]:
        cls, action, reason = classify(repo)
        rows.append({
            "nameWithOwner": repo["nameWithOwner"],
            "class": cls,
            "action": action,
            "reason": reason,
            "updatedAt": repo.get("updatedAt") or "",
            "pushedAt": repo.get("pushedAt") or "",
            "isPrivate": str(repo.get("isPrivate", False)).lower(),
        })

    if args.out:
        with open(args.out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    if args.format == "json":
        print(json.dumps(rows, indent=2))
    else:
        print(render_markdown(rows))

if __name__ == "__main__":
    main()
