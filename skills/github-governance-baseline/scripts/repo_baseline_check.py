
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check repo-local governance baseline files.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--format", choices=["json", "pretty"], default="json")
    return parser.parse_args()


def check(root: Path) -> Dict[str, object]:
    checks = {
        "readme": (root / "README.md").exists() or (root / "README").exists(),
        "codeowners": (root / ".github" / "CODEOWNERS").exists() or (root / "CODEOWNERS").exists() or (root / "docs" / "CODEOWNERS").exists(),
        "workflows": (root / ".github" / "workflows").exists(),
        "issue_templates": (root / ".github" / "ISSUE_TEMPLATE").exists(),
        "pull_request_template": (root / ".github" / "pull_request_template.md").exists() or (root / "pull_request_template.md").exists() or (root / "PULL_REQUEST_TEMPLATE.md").exists(),
        "security": (root / "SECURITY.md").exists() or (root / ".github" / "SECURITY.md").exists() or (root / "docs" / "SECURITY.md").exists(),
        "contributing": (root / "CONTRIBUTING.md").exists() or (root / ".github" / "CONTRIBUTING.md").exists() or (root / "docs" / "CONTRIBUTING.md").exists(),
    }
    missing = [key for key, ok in checks.items() if not ok]
    return {"root": str(root.resolve()), "checks": checks, "missing": missing}


def render_pretty(payload: Dict[str, object]) -> str:
    lines = ["Repo Baseline Check", "===================", ""]
    lines.append(f"root: {payload['root']}")
    lines.append("")
    for key, ok in payload["checks"].items():
        lines.append(f"- {key}: {'yes' if ok else 'no'}")
    lines.append("")
    lines.append("missing:")
    if payload["missing"]:
        for key in payload["missing"]:
            lines.append(f"- {key}")
    else:
        lines.append("- none")
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
