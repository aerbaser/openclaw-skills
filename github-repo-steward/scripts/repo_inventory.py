
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

OWNER_QUERY = """
query($login: String!, $cursor: String) {
  repositoryOwner(login: $login) {
    login
    repositories(first: 100, after: $cursor, orderBy: {field: UPDATED_AT, direction: DESC}) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        nameWithOwner
        description
        url
        homepageUrl
        isArchived
        isEmpty
        isFork
        isTemplate
        visibility
        createdAt
        updatedAt
        pushedAt
        diskUsage
        stargazerCount
        forkCount
        hasIssuesEnabled
        defaultBranchRef { name }
        primaryLanguage { name }
        repositoryTopics(first: 20) { nodes { topic { name } } }
        issues(states: OPEN) { totalCount }
        pullRequests(states: OPEN) { totalCount }
      }
    }
  }
}
"""

VIEWER_QUERY = """
query {
  viewer {
    login
  }
}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inventory repositories for a GitHub owner.")
    parser.add_argument("--owner", help="GitHub owner login. Defaults to authenticated viewer.")
    parser.add_argument("--output", help="Optional path to write raw JSON.")
    parser.add_argument("--format", choices=["json", "pretty", "markdown"], default="json")
    return parser.parse_args()


def require_gh() -> None:
    if shutil.which("gh") is None:
        raise RuntimeError("gh CLI not found in PATH.")


def run_gh(args: List[str]) -> Dict[str, Any]:
    completed = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "gh command failed")
    return json.loads(completed.stdout)


def viewer_login() -> str:
    response = run_gh(["api", "graphql", "-f", f"query={VIEWER_QUERY}"])
    return response["data"]["viewer"]["login"]


def fetch_owner_repos(login: str) -> List[Dict[str, Any]]:
    cursor: Optional[str] = None
    repos: List[Dict[str, Any]] = []
    while True:
        args = ["api", "graphql", "-f", f"query={OWNER_QUERY}", "-F", f"login={login}"]
        if cursor:
            args.extend(["-F", f"cursor={cursor}"])
        response = run_gh(args)
        owner = response["data"]["repositoryOwner"]
        if owner is None:
            raise RuntimeError(f"Owner '{login}' not found or inaccessible.")
        chunk = owner["repositories"]["nodes"]
        for node in chunk:
            repos.append({
                "name": node["name"],
                "nameWithOwner": node["nameWithOwner"],
                "description": node["description"],
                "url": node["url"],
                "homepageUrl": node["homepageUrl"],
                "isArchived": node["isArchived"],
                "isEmpty": node["isEmpty"],
                "isFork": node["isFork"],
                "isTemplate": node["isTemplate"],
                "visibility": node["visibility"],
                "createdAt": node["createdAt"],
                "updatedAt": node["updatedAt"],
                "pushedAt": node["pushedAt"],
                "diskUsage": node["diskUsage"],
                "stargazerCount": node["stargazerCount"],
                "forkCount": node["forkCount"],
                "hasIssuesEnabled": node["hasIssuesEnabled"],
                "defaultBranch": (node.get("defaultBranchRef") or {}).get("name"),
                "primaryLanguage": (node.get("primaryLanguage") or {}).get("name"),
                "topics": [item["topic"]["name"] for item in node["repositoryTopics"]["nodes"]],
                "openIssues": node["issues"]["totalCount"],
                "openPullRequests": node["pullRequests"]["totalCount"],
            })
        page = owner["repositories"]["pageInfo"]
        if not page["hasNextPage"]:
            break
        cursor = page["endCursor"]
    return repos


def as_markdown(owner: str, repos: List[Dict[str, Any]]) -> str:
    lines = [f"# Repository Inventory for `{owner}`", ""]
    lines.append(f"- total repos: `{len(repos)}`")
    lines.append("")
    lines.append("| Repo | Visibility | State | Primary language | Updated |")
    lines.append("| --- | --- | --- | --- | --- |")
    for repo in repos:
        state = []
        if repo["isArchived"]:
            state.append("archived")
        if repo["isFork"]:
            state.append("fork")
        if repo["isTemplate"]:
            state.append("template")
        if repo["isEmpty"]:
            state.append("empty")
        lines.append(
            f"| `{repo['nameWithOwner']}` | {repo['visibility'].lower()} | {', '.join(state) or 'active'} | "
            f"{repo['primaryLanguage'] or '—'} | {repo['updatedAt'][:10] if repo['updatedAt'] else '—'} |"
        )
    return "\n".join(lines) + "\n"


def as_pretty(owner: str, repos: List[Dict[str, Any]]) -> str:
    lines = ["Repository Inventory", "==================", ""]
    lines.append(f"owner: {owner}")
    lines.append(f"total repos: {len(repos)}")
    lines.append("")
    for repo in repos:
        flags = []
        if repo["isArchived"]:
            flags.append("archived")
        if repo["isFork"]:
            flags.append("fork")
        if repo["isTemplate"]:
            flags.append("template")
        if repo["isEmpty"]:
            flags.append("empty")
        lines.append(f"- {repo['nameWithOwner']}  [{repo['visibility'].lower()}]  ({', '.join(flags) or 'active'})")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    try:
        require_gh()
        owner = args.owner or viewer_login()
        repos = fetch_owner_repos(owner)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1

    payload = {"ok": True, "owner": owner, "repositories": repos}
    if args.output:
        Path(args.output).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.format == "markdown":
        print(as_markdown(owner, repos))
    else:
        print(as_pretty(owner, repos))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
