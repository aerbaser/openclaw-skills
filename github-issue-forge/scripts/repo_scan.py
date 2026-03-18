#!/usr/bin/env python3
"""Scan a repository and emit an agent-friendly summary for issue authoring."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable


COMMON_DOCS = [
    "README.md",
    "CONTRIBUTING.md",
    "ARCHITECTURE.md",
    "CLAUDE.md",
    "docs",
]
MANIFESTS = [
    "package.json",
    "pnpm-workspace.yaml",
    "turbo.json",
    "nx.json",
    "pyproject.toml",
    "requirements.txt",
    "uv.lock",
    "poetry.lock",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "gradlew",
    "Gemfile",
    "composer.json",
]
CI_GLOBS = [
    ".github/workflows",
    ".circleci",
    ".gitlab-ci.yml",
    "azure-pipelines.yml",
    "Jenkinsfile",
]

LANG_EXTENSIONS = {
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".py": "python",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".kt": "kotlin",
    ".cs": "dotnet",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
}

SOURCE_HINT_DIRS = [
    "src",
    "app",
    "lib",
    "packages",
    "services",
    "crates",
    "cmd",
    "internal",
    "server",
    "client",
    "web",
    "api",
    "tests",
    "test",
    "__tests__",
]

def run(cmd: list[str], cwd: Path | None = None) -> str:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            check=True,
        )
        return proc.stdout.strip()
    except Exception:
        return ""


def find_repo_root(start: Path) -> Path:
    out = run(["git", "rev-parse", "--show-toplevel"], cwd=start)
    return Path(out) if out else start.resolve()


def safe_ls_files(root: Path) -> list[Path]:
    out = run(["git", "ls-files"], cwd=root)
    if out:
        return [root / line for line in out.splitlines() if line.strip()]
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            files.append(path)
    return files


def detect_languages(files: Iterable[Path]) -> list[str]:
    counter = Counter()
    for file in files:
        ext = file.suffix.lower()
        if ext in LANG_EXTENSIONS:
            counter[LANG_EXTENSIONS[ext]] += 1
    return [name for name, _count in counter.most_common(8)]


def relative(paths: Iterable[Path], root: Path) -> list[str]:
    return [str(p.relative_to(root)) for p in paths]


def top_entries(root: Path) -> list[str]:
    items = []
    try:
        for p in sorted(root.iterdir(), key=lambda x: x.name.lower()):
            if p.name == ".git":
                continue
            items.append(p.name + ("/" if p.is_dir() else ""))
            if len(items) >= 25:
                break
    except Exception:
        pass
    return items


def focus_hits(root: Path, focus: str) -> list[str]:
    terms = [t for t in re.split(r"\s+", focus.strip()) if len(t) >= 3]
    if not terms:
        return []
    query = "|".join(re.escape(t) for t in terms)
    out = run(["rg", "-i", "-l", query, str(root)], cwd=root)
    hits = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            hits.append(str(Path(line).resolve().relative_to(root.resolve())))
        except Exception:
            try:
                hits.append(str(Path(line).relative_to(root)))
            except Exception:
                hits.append(line)
        if len(hits) >= 25:
            break
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan a repo for issue-authoring context.")
    parser.add_argument("--root", default=".", help="Repository root or any child path.")
    parser.add_argument("--focus", default="", help="Optional focus keywords to rank relevant files.")
    parser.add_argument("--format", choices=["json", "pretty"], default="json")
    args = parser.parse_args()

    start = Path(args.root).resolve()
    root = find_repo_root(start)
    files = safe_ls_files(root)

    docs = [root / p for p in COMMON_DOCS if (root / p).exists()]
    manifests = [root / p for p in MANIFESTS if (root / p).exists()]
    ci = [root / p for p in CI_GLOBS if (root / p).exists()]
    hints = [root / p for p in SOURCE_HINT_DIRS if (root / p).exists()]

    default_branch = run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], cwd=root).removeprefix("refs/remotes/origin/")
    if not default_branch:
        default_branch = run(["git", "branch", "--show-current"], cwd=root) or "main"

    summary = {
        "repo_root": str(root),
        "default_branch": default_branch,
        "current_branch": run(["git", "branch", "--show-current"], cwd=root) or None,
        "top_entries": top_entries(root),
        "languages": detect_languages(files),
        "docs": relative(docs, root),
        "manifests": relative(manifests, root),
        "ci_files": relative(ci, root),
        "source_hint_dirs": relative(hints, root),
        "test_dirs": [str(p.relative_to(root)) for p in [root / "tests", root / "test", root / "__tests__"] if p.exists()],
        "focus_hits": focus_hits(root, args.focus) if args.focus else [],
        "file_count": len(files),
    }

    if args.format == "json":
        json.dump(summary, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"Repo root:        {summary['repo_root']}")
        print(f"Default branch:   {summary['default_branch']}")
        print(f"Current branch:   {summary['current_branch']}")
        print(f"Languages:        {', '.join(summary['languages']) or 'unknown'}")
        print(f"Docs:             {', '.join(summary['docs']) or 'none'}")
        print(f"Manifests:        {', '.join(summary['manifests']) or 'none'}")
        print(f"CI files:         {', '.join(summary['ci_files']) or 'none'}")
        print(f"Source dirs:      {', '.join(summary['source_hint_dirs']) or 'none'}")
        print(f"Test dirs:        {', '.join(summary['test_dirs']) or 'none'}")
        if summary["focus_hits"]:
            print("Focus hits:")
            for hit in summary["focus_hits"]:
                print(f"  - {hit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
