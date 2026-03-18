#!/usr/bin/env python3
import argparse, json, subprocess, sys
from pathlib import Path

QUERY = """
query($owner: String!, $cursor: String) {
  repositoryOwner(login: $owner) {
    login
    repositories(first: 100, after: $cursor, orderBy: {field: UPDATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        nameWithOwner
        description
        url
        homepageUrl
        isArchived
        isFork
        isPrivate
        isTemplate
        hasIssuesEnabled
        hasWikiEnabled
        createdAt
        updatedAt
        pushedAt
        diskUsage
        stargazerCount
        forkCount
        primaryLanguage { name }
        defaultBranchRef { name }
        repositoryTopics(first: 30) { nodes { topic { name } } }
        issues(states: OPEN) { totalCount }
        pullRequests(states: OPEN) { totalCount }
      }
    }
  }
}
"""

def run_gh_graphql(owner: str):
    repos = []
    cursor = None
    while True:
        payload = {
            "query": QUERY,
            "variables": {"owner": owner, "cursor": cursor}
        }
        proc = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"owner={owner}"] + ([ "-F", f"cursor={cursor}"] if cursor else []),
            capture_output=True,
            text=True
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or "gh api graphql failed")
        data = json.loads(proc.stdout)
        owner_data = data["data"]["repositoryOwner"]
        page = owner_data["repositories"]
        repos.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return {"owner": owner, "repositories": repos}

def render_markdown(data):
    lines = []
    repos = data["repositories"]
    lines.append(f"# Repository inventory for `{data['owner']}`")
    lines.append("")
    lines.append(f"Total repos: **{len(repos)}**")
    lines.append("")
    lines.append("| Repo | Archived | Fork | Template | Private | Updated | Open PRs | Open Issues | Topics |")
    lines.append("|---|---:|---:|---:|---:|---|---:|---:|---|")
    for r in repos:
        topics = ", ".join(n["topic"]["name"] for n in r.get("repositoryTopics", {}).get("nodes", []))
        lines.append(
            f"| {r['nameWithOwner']} | {'yes' if r['isArchived'] else 'no'} | {'yes' if r['isFork'] else 'no'} | "
            f"{'yes' if r['isTemplate'] else 'no'} | {'yes' if r['isPrivate'] else 'no'} | {r.get('updatedAt','')} | "
            f"{r.get('pullRequests',{}).get('totalCount',0)} | {r.get('issues',{}).get('totalCount',0)} | {topics} |"
        )
    return "\n".join(lines)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--owner", required=True)
    p.add_argument("--out", help="write raw json inventory")
    p.add_argument("--format", choices=["json", "markdown", "pretty"], default="pretty")
    args = p.parse_args()

    data = run_gh_graphql(args.owner)

    if args.out:
        Path(args.out).write_text(json.dumps(data, indent=2), encoding="utf-8")

    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(render_markdown(data))

if __name__ == "__main__":
    main()
