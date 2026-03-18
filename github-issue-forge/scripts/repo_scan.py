
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

try:
    import tomllib  # py3.11+
except Exception:  # pragma: no cover
    tomllib = None

IGNORE_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "vendor", "dist", "build", "coverage",
    ".next", ".nuxt", ".turbo", ".cache", ".venv", "venv", "__pycache__", ".pytest_cache",
    ".mypy_cache", "target", "out", "bin", "obj",
}

DOC_HINTS = ("readme", "adr", "architecture", "design", "decision", "contributing", "security")
TEST_HINTS = ("test", "tests", "__tests__", "spec", "e2e", "integration")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan a repository to support issue drafting.")
    parser.add_argument("--root", default=".", help="Repository path (default: current directory).")
    parser.add_argument("--focus", action="append", default=[], help="Focus keywords. Can be repeated.")
    parser.add_argument("--format", choices=["json", "pretty", "markdown"], default="json")
    parser.add_argument("--max-files", type=int, default=3000, help="Maximum files to inspect.")
    parser.add_argument("--max-focus-hits", type=int, default=25, help="Maximum focus matches to return.")
    return parser.parse_args()


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current] + list(current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def safe_read_text(path: Path, limit: int = 8192) -> str:
    try:
        with path.open("rb") as f:
            chunk = f.read(limit)
        return chunk.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def run_git(args: Sequence[str], cwd: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode == 0:
            return completed.stdout.strip()
    except Exception:
        pass
    return ""


def walk_files(root: Path, max_files: int) -> List[Path]:
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.is_symlink():
                continue
            files.append(path)
            if len(files) >= max_files:
                return files
    return files


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except Exception:
        return str(path)


def detect_manifests(files: Sequence[Path], root: Path) -> Dict[str, List[str]]:
    patterns = {
        "package_json": "package.json",
        "pnpm_lock": "pnpm-lock.yaml",
        "yarn_lock": "yarn.lock",
        "npm_lock": "package-lock.json",
        "pyproject": "pyproject.toml",
        "requirements": "requirements.txt",
        "poetry_lock": "poetry.lock",
        "uv_lock": "uv.lock",
        "cargo": "Cargo.toml",
        "go_mod": "go.mod",
        "maven": "pom.xml",
        "gradle": ("build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"),
        "dotnet": (".sln", ".csproj"),
        "ruby": ("Gemfile", "gems.rb"),
        "make": ("Makefile", "makefile"),
        "just": "justfile",
    }
    found: Dict[str, List[str]] = defaultdict(list)
    for path in files:
        name = path.name
        for key, matcher in patterns.items():
            if isinstance(matcher, tuple):
                if name in matcher or any(name.endswith(suffix) for suffix in matcher if suffix.startswith(".")):
                    found[key].append(rel(path, root))
            else:
                if name == matcher:
                    found[key].append(rel(path, root))
    return {k: v[:20] for k, v in found.items() if v}


def parse_package_json(path: Path) -> Dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    scripts = data.get("scripts") or {}
    if not isinstance(scripts, dict):
        return {}
    return {str(k): str(v) for k, v in scripts.items()}


def parse_pyproject(path: Path) -> Dict[str, object]:
    if tomllib is None:
        return {}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    result: Dict[str, object] = {}
    project = data.get("project") or {}
    scripts = project.get("scripts") or {}
    if isinstance(scripts, dict):
        result["project_scripts"] = sorted(map(str, scripts.keys()))
    tool = data.get("tool") or {}
    if "poetry" in tool:
        result["poetry"] = True
    if "pytest" in tool:
        result["pytest"] = True
    if "ruff" in tool:
        result["ruff"] = True
    if "mypy" in tool:
        result["mypy"] = True
    return result


def parse_make_targets(path: Path) -> List[str]:
    targets: List[str] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("\t") or line.startswith(" "):
                continue
            match = re.match(r"^([A-Za-z0-9_.-]+)\s*:(?![=])", line)
            if match:
                target = match.group(1)
                if not target.startswith("."):
                    targets.append(target)
    except Exception:
        return []
    return targets[:50]


def detect_commands(root: Path, manifests: Dict[str, List[str]]) -> Dict[str, List[str]]:
    commands: Dict[str, List[str]] = defaultdict(list)

    # JavaScript / TypeScript
    for pkg_path in manifests.get("package_json", []):
        scripts = parse_package_json(root / pkg_path)
        if scripts:
            for key in ("lint", "typecheck", "test", "build", "check", "test:ci", "lint:ci"):
                if key in scripts:
                    commands[key].append(f"npm run {key}")
            if any("pnpm_lock" == k for k in manifests):
                commands["install"].append("pnpm install --frozen-lockfile")
            elif any("yarn_lock" == k for k in manifests):
                commands["install"].append("yarn --immutable")
            else:
                commands["install"].append("npm ci")
            if "test" not in scripts and "test:ci" in scripts:
                commands["test"].append("npm run test:ci")

    # Python
    if "pyproject" in manifests or "requirements" in manifests:
        if "uv_lock" in manifests:
            commands["install"].append("uv sync --frozen")
        elif "poetry_lock" in manifests:
            commands["install"].append("poetry install --no-interaction --sync")
        elif "requirements" in manifests:
            req = manifests["requirements"][0]
            commands["install"].append(f"python -m pip install -r {req}")
        else:
            commands["install"].append("python -m pip install -e .")
        pyproject_path = manifests.get("pyproject", [None])[0]
        if pyproject_path:
            info = parse_pyproject(root / pyproject_path)
            if info.get("pytest"):
                commands["test"].append("pytest")
            if info.get("ruff"):
                commands["lint"].append("ruff check .")
            if info.get("mypy"):
                commands["typecheck"].append("mypy .")

    # Go
    if "go_mod" in manifests:
        commands["test"].append("go test ./...")
        commands["build"].append("go build ./...")
        commands["lint"].append("go vet ./...")

    # Rust
    if "cargo" in manifests:
        commands["test"].append("cargo test --all-targets")
        commands["build"].append("cargo build --workspace")
        commands["lint"].append("cargo clippy --workspace --all-targets -- -D warnings")
        commands["format"].append("cargo fmt --all --check")

    # Java
    if "maven" in manifests:
        commands["test"].append("mvn -B test")
        commands["build"].append("mvn -B verify")
    if "gradle" in manifests:
        commands["test"].append("./gradlew test")
        commands["build"].append("./gradlew build")

    # .NET
    if "dotnet" in manifests:
        commands["restore"].append("dotnet restore")
        commands["build"].append("dotnet build --no-restore")
        commands["test"].append("dotnet test --no-build")

    # Ruby
    if "ruby" in manifests:
        commands["install"].append("bundle install --jobs 4 --retry 3")
        commands["test"].append("bundle exec rspec")

    # Make / just
    for make_path in manifests.get("make", []):
        targets = parse_make_targets(root / make_path)
        for target in ("setup", "install", "lint", "typecheck", "test", "build", "check", "ci"):
            if target in targets:
                commands[target].append(f"make {target}")

    for just_path in manifests.get("just", []):
        try:
            text = (root / just_path).read_text(encoding="utf-8", errors="ignore")
            for target in ("setup", "install", "lint", "typecheck", "test", "build", "check", "ci"):
                if re.search(rf"(?m)^{re.escape(target)}\s*:", text):
                    commands[target].append(f"just {target}")
        except Exception:
            pass

    deduped = {}
    for key, values in commands.items():
        seen = []
        for item in values:
            if item not in seen:
                seen.append(item)
        deduped[key] = seen
    return deduped


def categorize_files(files: Sequence[Path], root: Path) -> Dict[str, List[str]]:
    docs: List[str] = []
    tests: List[str] = []
    workflows: List[str] = []
    configs: List[str] = []
    sources: List[str] = []

    for path in files:
        rp = rel(path, root)
        lower = rp.lower()
        name = path.name.lower()

        if lower.startswith(".github/workflows/") and (name.endswith(".yml") or name.endswith(".yaml")):
            workflows.append(rp)
            continue

        if any(hint in lower for hint in DOC_HINTS) or lower.startswith("docs/"):
            docs.append(rp)
            continue

        if any(hint in lower for hint in TEST_HINTS) or re.search(r"(_test\.go|\.spec\.[A-Za-z0-9]+|\.test\.[A-Za-z0-9]+)$", lower):
            tests.append(rp)
            continue

        if name.endswith((".json", ".toml", ".yaml", ".yml", ".ini", ".cfg")) or name in {"Dockerfile", "Makefile", "justfile"}:
            configs.append(rp)
            continue

        if name.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".kt", ".cs", ".rb", ".php")):
            sources.append(rp)

    return {
        "docs": docs[:80],
        "tests": tests[:80],
        "workflows": workflows[:80],
        "configs": configs[:80],
        "sources": sources[:120],
    }


def focus_matches(files: Sequence[Path], root: Path, focuses: Sequence[str], max_hits: int) -> List[Dict[str, object]]:
    focus_terms = [f.strip().lower() for f in focuses if f.strip()]
    if not focus_terms:
        return []

    hits: List[Dict[str, object]] = []
    for path in files:
        rp = rel(path, root)
        lower_path = rp.lower()
        content = safe_read_text(path).lower()
        score = 0
        matched: List[str] = []
        for term in focus_terms:
            if term in lower_path:
                score += 3
                matched.append(term)
            elif term in content:
                score += 1
                matched.append(term)
        if score:
            hits.append({
                "path": rp,
                "score": score,
                "matched": sorted(set(matched)),
            })

    hits.sort(key=lambda item: (-int(item["score"]), item["path"]))
    return hits[:max_hits]


def summarize_repo(root: Path, files: Sequence[Path]) -> Dict[str, object]:
    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    origin = run_git(["config", "--get", "remote.origin.url"], root)
    tracked = run_git(["ls-files"], root)
    tracked_count = len([line for line in tracked.splitlines() if line.strip()]) if tracked else len(files)
    return {
        "root": str(root),
        "branch": branch or None,
        "origin": origin or None,
        "file_count_scanned": len(files),
        "tracked_file_count_estimate": tracked_count,
    }


def to_markdown(payload: Dict[str, object]) -> str:
    lines: List[str] = []
    lines.append("# Repo Scan")
    lines.append("")
    repo = payload["repo"]
    lines.append(f"- root: `{repo['root']}`")
    if repo.get("branch"):
        lines.append(f"- branch: `{repo['branch']}`")
    if repo.get("origin"):
        lines.append(f"- origin: `{repo['origin']}`")
    lines.append(f"- files scanned: `{repo['file_count_scanned']}`")
    lines.append("")

    manifests = payload["manifests"]
    if manifests:
        lines.append("## Manifests")
        for key, values in manifests.items():
            joined = ", ".join(f"`{v}`" for v in values)
            lines.append(f"- {key}: {joined}")
        lines.append("")

    commands = payload["commands"]
    if commands:
        lines.append("## Candidate Commands")
        for key, values in commands.items():
            for value in values:
                lines.append(f"- {key}: `{value}`")
        lines.append("")

    categorized = payload["files"]
    for section in ("docs", "tests", "workflows", "configs", "sources"):
        values = categorized.get(section) or []
        if values:
            lines.append(f"## {section.title()}")
            for value in values[:20]:
                lines.append(f"- `{value}`")
            if len(values) > 20:
                lines.append(f"- … {len(values) - 20} more")
            lines.append("")

    focus_hits = payload.get("focus_hits") or []
    if focus_hits:
        lines.append("## Focus Hits")
        for hit in focus_hits:
            joined = ", ".join(f"`{term}`" for term in hit["matched"])
            lines.append(f"- `{hit['path']}` (score {hit['score']}; matched: {joined})")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def to_pretty(payload: Dict[str, object]) -> str:
    repo = payload["repo"]
    out: List[str] = []
    out.append("Repo Scan")
    out.append("=========")
    out.append(f"root: {repo['root']}")
    if repo.get("branch"):
        out.append(f"branch: {repo['branch']}")
    if repo.get("origin"):
        out.append(f"origin: {repo['origin']}")
    out.append(f"files scanned: {repo['file_count_scanned']}")
    out.append("")

    if payload["manifests"]:
        out.append("Manifests")
        out.append("---------")
        for key, values in payload["manifests"].items():
            out.append(f"- {key}: {', '.join(values)}")
        out.append("")

    if payload["commands"]:
        out.append("Candidate commands")
        out.append("------------------")
        for key, values in payload["commands"].items():
            for value in values:
                out.append(f"- {key}: {value}")
        out.append("")

    for section in ("docs", "tests", "workflows", "configs", "sources"):
        values = payload["files"].get(section) or []
        if values:
            out.append(section.title())
            out.append("-" * len(section))
            for value in values[:15]:
                out.append(f"- {value}")
            if len(values) > 15:
                out.append(f"- ... {len(values) - 15} more")
            out.append("")

    if payload.get("focus_hits"):
        out.append("Focus hits")
        out.append("----------")
        for hit in payload["focus_hits"]:
            out.append(f"- {hit['path']}  (score={hit['score']}; matched={', '.join(hit['matched'])})")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    root = find_repo_root(Path(args.root))
    files = walk_files(root, args.max_files)
    manifests = detect_manifests(files, root)
    commands = detect_commands(root, manifests)
    categorized = categorize_files(files, root)
    focus_hits = focus_matches(files, root, args.focus, args.max_focus_hits)
    payload = {
        "repo": summarize_repo(root, files),
        "manifests": manifests,
        "commands": commands,
        "files": categorized,
        "focus_hits": focus_hits,
    }

    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.format == "markdown":
        print(to_markdown(payload))
    else:
        print(to_pretty(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
