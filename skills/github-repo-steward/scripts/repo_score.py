
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

LAB_TOKENS = {"lab", "playground", "sandbox", "poc", "spike", "scratch", "demo", "experiment", "tmp", "temp", "test"}
TEMPLATE_TOKENS = {"template", "starter", "boilerplate", "scaffold"}
PARKING_TOKENS = {"placeholder", "empty", "parking", "stub"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify GitHub repositories into a small governance taxonomy.")
    parser.add_argument("--inventory", required=True, help="Path to inventory JSON from repo_inventory.py")
    parser.add_argument("--output", help="Optional path for scored JSON")
    parser.add_argument("--format", choices=["json", "pretty", "markdown"], default="json")
    return parser.parse_args()


def iso_days_ago(value: str | None) -> int | None:
    if not value:
        return None
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - dt).days


def classify(repo: Dict[str, Any]) -> Tuple[str, str, List[str]]:
    reasons: List[str] = []
    name_l = repo["name"].lower()
    desc_l = (repo.get("description") or "").lower()
    topics = {topic.lower() for topic in repo.get("topics") or []}
    stale_days = iso_days_ago(repo.get("pushedAt"))
    open_prs = int(repo.get("openPullRequests") or 0)
    open_issues = int(repo.get("openIssues") or 0)
    disk_usage = int(repo.get("diskUsage") or 0)

    if repo.get("isArchived"):
        reasons.append("already archived")
        return "archive", "keep-archived", reasons

    if repo.get("isTemplate") or topics & TEMPLATE_TOKENS or any(token in name_l for token in TEMPLATE_TOKENS):
        reasons.append("template signal detected")
        return "template", "keep-template", reasons

    if repo.get("isFork"):
        reasons.append("repository is a fork")
        if stale_days is not None and stale_days > 180 and open_prs == 0:
            reasons.append(f"stale fork ({stale_days} days since push)")
            return "fork", "archive-candidate", reasons
        return "fork", "keep-fork-review", reasons

    if repo.get("isEmpty") or disk_usage <= 5:
        reasons.append("empty or near-empty")
        if stale_days is None or stale_days > 30:
            return "parking", "delete-candidate", reasons
        return "parking", "review-parking", reasons

    if topics & PARKING_TOKENS or any(token in name_l or token in desc_l for token in PARKING_TOKENS):
        reasons.append("parking signal detected")
        if stale_days is not None and stale_days > 30 and open_prs == 0:
            return "parking", "delete-candidate", reasons
        return "parking", "review-parking", reasons

    if topics & LAB_TOKENS or any(token in name_l or token in desc_l for token in LAB_TOKENS):
        reasons.append("lab signal detected")
        if stale_days is not None and stale_days > 180 and open_prs == 0 and open_issues == 0:
            reasons.append(f"stale lab ({stale_days} days since push)")
            return "lab", "archive-candidate", reasons
        return "lab", "keep-lab-review", reasons

    reasons.append("non-empty repository without fork/template/lab/parking signals")
    action = "keep-managed"
    if not repo.get("description"):
        reasons.append("missing description")
        action = "harden-managed"
    elif not topics:
        reasons.append("missing topics")
        action = "harden-managed"
    elif stale_days is not None and stale_days > 365 and open_prs == 0:
        reasons.append(f"managed but stale ({stale_days} days since push)")
        action = "review-managed"
    return "managed", action, reasons


def score_inventory(payload: Dict[str, Any]) -> Dict[str, Any]:
    classified = []
    summary: Dict[str, int] = {k: 0 for k in ["managed", "template", "fork", "lab", "archive", "parking"]}
    actions: Dict[str, int] = {}
    for repo in payload.get("repositories") or []:
        klass, action, reasons = classify(repo)
        summary[klass] += 1
        actions[action] = actions.get(action, 0) + 1
        classified.append({
            **repo,
            "class": klass,
            "recommendedAction": action,
            "reasons": reasons,
            "staleDays": iso_days_ago(repo.get("pushedAt")),
        })
    return {
        "owner": payload.get("owner"),
        "summary": summary,
        "actions": actions,
        "repositories": classified,
    }


def render_markdown(payload: Dict[str, Any]) -> str:
    lines = [f"# Repo Classification for `{payload['owner']}`", ""]
    lines.append("## Summary")
    for key, value in payload["summary"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("| Repo | Class | Action | Reason highlights |")
    lines.append("| --- | --- | --- | --- |")
    for repo in payload["repositories"]:
        reason = "; ".join(repo["reasons"][:3])
        lines.append(f"| `{repo['nameWithOwner']}` | {repo['class']} | {repo['recommendedAction']} | {reason} |")
    return "\n".join(lines) + "\n"


def render_pretty(payload: Dict[str, Any]) -> str:
    lines = ["Repo Classification", "===================", ""]
    lines.append(f"owner: {payload['owner']}")
    lines.append("summary:")
    for key, value in payload["summary"].items():
        lines.append(f"  - {key}: {value}")
    lines.append("")
    for repo in payload["repositories"]:
        lines.append(f"- {repo['nameWithOwner']} -> {repo['class']} / {repo['recommendedAction']}")
        for reason in repo["reasons"]:
            lines.append(f"    * {reason}")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    payload = json.loads(Path(args.inventory).read_text(encoding="utf-8"))
    scored = score_inventory(payload)
    if args.output:
        Path(args.output).write_text(json.dumps(scored, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.format == "json":
        print(json.dumps(scored, indent=2, ensure_ascii=False))
    elif args.format == "markdown":
        print(render_markdown(scored))
    else:
        print(render_pretty(scored))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
