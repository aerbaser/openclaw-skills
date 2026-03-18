#!/usr/bin/env python3
import argparse, json, os
from pathlib import Path

IMPORTANT_FILES = [
    "package.json", "pnpm-lock.yaml", "yarn.lock", "package-lock.json",
    "pyproject.toml", "requirements.txt", "poetry.lock", "uv.lock",
    "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "build.gradle.kts",
    "Makefile", "justfile", "README.md"
]

def scan(root: Path, focus: str | None = None):
    focus_terms = [t.lower() for t in focus.split()] if focus else []
    matched = []
    important = [str((root / f).relative_to(root)) for f in IMPORTANT_FILES if (root / f).exists()]
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        rel = str(path.relative_to(root))
        if rel.startswith(".git/"):
            continue
        if focus_terms:
            hay = rel.lower()
            if any(term in hay for term in focus_terms):
                matched.append(rel)
        elif len(matched) < 200:
            matched.append(rel)
    workflows = [str(p.relative_to(root)) for p in root.glob(".github/workflows/*") if p.is_file()]
    return {
        "important_files": important,
        "workflows": workflows,
        "matched_paths": matched[:200],
    }

def render_md(data):
    lines = ["# Repo scan", ""]
    lines.append("## Important files")
    for x in data["important_files"]:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Workflows")
    for x in data["workflows"]:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Matched paths")
    for x in data["matched_paths"]:
        lines.append(f"- `{x}`")
    return "\n".join(lines)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", default=".")
    p.add_argument("--focus")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    args = p.parse_args()
    data = scan(Path(args.repo_root), args.focus)
    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(render_md(data))

if __name__ == "__main__":
    main()
