#!/usr/bin/env python3
"""
scaffold_security_baseline.py

Copies security baseline files into the target repo.
Detects the repo's package ecosystem and generates a matching dependabot.yml.
"""
import argparse, shutil, re
from pathlib import Path

ECOSYSTEM_MARKERS = {
    "npm":    ["package.json", "pnpm-lock.yaml", "yarn.lock", "package-lock.json"],
    "pip":    ["requirements.txt", "pyproject.toml", "poetry.lock", "uv.lock"],
    "gomod":  ["go.mod"],
    "cargo":  ["Cargo.toml"],
    "maven":  ["pom.xml"],
    "gradle": ["build.gradle", "build.gradle.kts"],
    "bundler":["Gemfile"],
    "nuget":  ["*.sln", "*.csproj"],
}

SOLIDITY_MARKERS = ["foundry.toml", "hardhat.config.js", "hardhat.config.ts"]

STATIC_FILES = {
    "codeql.yml":           ".github/workflows/codeql.yml",
    "dependency-review.yml":".github/workflows/dependency-review.yml",
}


def detect_ecosystems(root: Path) -> list[str]:
    found = []
    for eco, markers in ECOSYSTEM_MARKERS.items():
        for marker in markers:
            if "*" in marker:
                if any(root.glob(marker)):
                    found.append(eco)
                    break
            elif (root / marker).exists():
                found.append(eco)
                break
    return found or ["npm"]  # fallback


def is_solidity_repo(root: Path) -> bool:
    for marker in SOLIDITY_MARKERS:
        if (root / marker).exists():
            return True
    # Also check for .sol files in common dirs
    for pattern in ["src/**/*.sol", "contracts/**/*.sol"]:
        if any(root.glob(pattern)):
            return True
    return False


def build_dependabot(ecosystems: list[str]) -> str:
    lines = ["version: 2", "updates:"]
    # Always include github-actions
    lines += [
        "  - package-ecosystem: \"github-actions\"",
        "    directory: \"/\"",
        "    schedule:",
        "      interval: \"weekly\"",
        "",
    ]
    for eco in ecosystems:
        lines += [
            f"  - package-ecosystem: \"{eco}\"",
            "    directory: \"/\"",
            "    schedule:",
            "      interval: \"weekly\"",
            "    open-pull-requests-limit: 10",
            "",
        ]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dest", default=".")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    base = Path(__file__).resolve().parent.parent / "templates"
    dest_root = Path(args.dest)

    # Copy static files (codeql, dependency-review)
    for src_name, rel_dst in STATIC_FILES.items():
        src = base / src_name
        dst = dest_root / rel_dst
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and not args.force:
            print(f"skip (exists) {rel_dst}")
            continue
        shutil.copyfile(src, dst)
        print(f"copied {rel_dst}")

    # Generate dependabot.yml based on detected ecosystems
    ecosystems = detect_ecosystems(dest_root)
    print(f"detected ecosystems: {ecosystems}")

    dep_dst = dest_root / ".github" / "dependabot.yml"
    dep_dst.parent.mkdir(parents=True, exist_ok=True)
    if dep_dst.exists() and not args.force:
        print("skip (exists) .github/dependabot.yml")
    else:
        dep_dst.write_text(build_dependabot(ecosystems), encoding="utf-8")
        print(f"generated .github/dependabot.yml (ecosystems: {', '.join(ecosystems)})")

    # Scaffold Slither for Solidity repos
    if is_solidity_repo(dest_root):
        slither_src = base / "slither.yml"
        slither_dst = dest_root / ".github" / "workflows" / "slither.yml"
        slither_dst.parent.mkdir(parents=True, exist_ok=True)
        if slither_dst.exists() and not args.force:
            print("skip (exists) .github/workflows/slither.yml")
        else:
            shutil.copyfile(slither_src, slither_dst)
            print("scaffolded .github/workflows/slither.yml (Solidity detected)")
    else:
        print("no Solidity detected — skipping slither.yml")


if __name__ == "__main__":
    main()
