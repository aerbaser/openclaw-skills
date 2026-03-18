
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check repo-local GitHub security baseline files.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--format", choices=["json", "pretty"], default="json")
    return parser.parse_args()


def check(root: Path) -> Dict[str, object]:
    workflows_dir = root / ".github" / "workflows"
    dep_review = False
    codeql = False
    if workflows_dir.exists():
        dep_review = any(workflows_dir.glob("*dependency*review*.yml")) or any(workflows_dir.glob("*dependency*review*.yaml"))
        codeql = any(workflows_dir.glob("*codeql*.yml")) or any(workflows_dir.glob("*codeql*.yaml"))

    checks = {
        "dependabot": (root / ".github" / "dependabot.yml").exists(),
        "dependency_review": dep_review,
        "codeql_workflow": codeql,
        "security_md": (root / "SECURITY.md").exists() or (root / ".github" / "SECURITY.md").exists() or (root / "docs" / "SECURITY.md").exists(),
        "workflows_dir": workflows_dir.exists(),
    }
    missing = [key for key, value in checks.items() if not value and key != "codeql_workflow"]
    if not checks["codeql_workflow"]:
        missing.append("code_scanning_path_explicit")
    return {"root": str(root.resolve()), "checks": checks, "missing": missing}


def render_pretty(payload: Dict[str, object]) -> str:
    lines = ["Security Baseline Check", "=======================", ""]
    lines.append(f"root: {payload['root']}")
    lines.append("")
    for key, value in payload["checks"].items():
        lines.append(f"- {key}: {'yes' if value else 'no'}")
    lines.append("")
    lines.append("missing:")
    if payload["missing"]:
        for item in payload["missing"]:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("note: 'code_scanning_path_explicit' can be satisfied by GitHub default setup even if no workflow file exists.")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    payload = check(Path(args.root))
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(render_pretty(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
