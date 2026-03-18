#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path

WORKFLOW_GLOBS = [".github/workflows/*.yml", ".github/workflows/*.yaml"]

def find_workflows(root: Path):
    files = []
    for pattern in WORKFLOW_GLOBS:
        files.extend(root.glob(pattern))
    return sorted(set(files))

def audit_workflow(path: Path):
    text = path.read_text(encoding="utf-8")
    findings = []
    if "permissions:" not in text:
        findings.append("missing permissions")
    if "write-all" in text:
        findings.append("uses write-all")
    if re.search(r"pull_request_target\s*:", text) or re.search(r"pull_request_target\b", text):
        findings.append("uses pull_request_target")
    if "concurrency:" not in text:
        findings.append("missing concurrency")
    return findings

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", default=".")
    args = p.parse_args()
    root = Path(args.repo_root)

    result = {
        "dependabot": (root / ".github" / "dependabot.yml").exists(),
        "codeql": (root / ".github" / "workflows" / "codeql.yml").exists(),
        "dependency_review": (root / ".github" / "workflows" / "dependency-review.yml").exists(),
        "workflows": {}
    }
    for wf in find_workflows(root):
        result["workflows"][str(wf.relative_to(root))] = audit_workflow(wf)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
