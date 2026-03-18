#!/usr/bin/env python3
import argparse, json
from pathlib import Path

REQUIRED = [
    "README.md",
    ".github/CODEOWNERS",
]

OPTIONAL_ANY = [
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE",
    ".github/dependabot.yml",
    ".github/workflows",
]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", default=".")
    args = p.parse_args()

    root = Path(args.repo_root)
    result = {"required_missing": [], "optional_missing": []}
    for rel in REQUIRED:
        if not (root / rel).exists():
            result["required_missing"].append(rel)
    for rel in OPTIONAL_ANY:
        if not (root / rel).exists():
            result["optional_missing"].append(rel)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
