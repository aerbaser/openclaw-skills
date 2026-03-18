
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a repository ruleset payload from the template.")
    parser.add_argument("--template", default=str(Path(__file__).resolve().parent.parent / "templates" / "rulesets" / "repository-ruleset.json"))
    parser.add_argument("--default-branch", default="main")
    parser.add_argument("--checks", action="append", default=["ci"], help="Required status check context. Can be repeated.")
    parser.add_argument("--format", choices=["json", "pretty"], default="json")
    return parser.parse_args()


def build_payload(template_path: Path, default_branch: str, checks: List[str]) -> Dict[str, Any]:
    payload = json.loads(template_path.read_text(encoding="utf-8"))
    payload["conditions"]["ref_name"]["include"] = [f"refs/heads/{default_branch}"]
    for rule in payload["rules"]:
        if rule["type"] == "required_status_checks":
            rule["parameters"]["required_status_checks"] = [{"context": check} for check in checks]
    return payload


def render_pretty(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, indent=2)


def main() -> int:
    args = parse_args()
    payload = build_payload(Path(args.template), args.default_branch, args.checks)
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(render_pretty(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
