
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit GitHub Actions workflow risk patterns.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--format", choices=["json", "pretty"], default="json")
    return parser.parse_args()


def workflow_files(root: Path) -> List[Path]:
    wf_root = root / ".github" / "workflows"
    if not wf_root.exists():
        return []
    return sorted([p for p in wf_root.iterdir() if p.suffix in {".yml", ".yaml"} and p.is_file()])


def audit(path: Path) -> Dict[str, object]:
    findings: List[Dict[str, str]] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return {"file": str(path), "findings": [{"severity": "error", "message": f"YAML parse failed: {exc}"}]}

    on_value = data.get("on", data.get(True))
    permissions = data.get("permissions")
    jobs = data.get("jobs") or {}

    def add(severity: str, message: str) -> None:
        findings.append({"severity": severity, "message": message})

    pull_request_target = False
    if isinstance(on_value, str):
        pull_request_target = on_value == "pull_request_target"
    elif isinstance(on_value, list):
        pull_request_target = "pull_request_target" in on_value
    elif isinstance(on_value, dict):
        pull_request_target = "pull_request_target" in on_value

    if permissions is None:
        add("warn", "Missing top-level permissions.")
    elif permissions == "write-all":
        add("error", "permissions: write-all is too broad.")
    elif isinstance(permissions, dict):
        for key, value in permissions.items():
            if value == "write":
                add("warn", f"Top-level permission '{key}: write' should be justified.")

    if pull_request_target:
        add("warn", "pull_request_target is present; inspect trust boundary carefully.")

    for job_name, job in jobs.items():
        steps = (job or {}).get("steps") or []
        job_permissions = (job or {}).get("permissions")
        if job_permissions == "write-all":
            add("error", f"Job '{job_name}' uses write-all.")
        for step in steps:
            uses = str(step.get("uses", ""))
            run = str(step.get("run", ""))
            if pull_request_target and uses.startswith("actions/checkout"):
                add("error", f"Job '{job_name}' checks out code under pull_request_target.")
            if pull_request_target and "github.event.pull_request.head" in run:
                add("error", f"Job '{job_name}' references PR head content under pull_request_target.")
            if uses:
                if "@" not in uses:
                    add("warn", f"Action without explicit ref: {uses}")
                else:
                    action, ref = uses.split("@", 1)
                    if not action.startswith(("actions/", "github/")) and ref in {"main", "master", "latest"}:
                        add("error", f"Third-party action uses floating ref: {uses}")
                    elif not action.startswith(("actions/", "github/")) and not re.fullmatch(r"(v\d+(\.\d+){0,2}|[0-9a-f]{40})", ref):
                        add("warn", f"Third-party action is not pinned to SHA or stable version: {uses}")

    return {"file": str(path), "findings": findings}


def render_pretty(results: List[Dict[str, object]]) -> str:
    lines = ["Actions Audit", "=============", ""]
    if not results:
        lines.append("No workflow files found.")
        return "\n".join(lines) + "\n"
    for result in results:
        lines.append(result["file"])
        lines.append("-" * len(str(result["file"])))
        findings = result["findings"]
        if not findings:
            lines.append("No findings.")
        else:
            for finding in findings:
                lines.append(f"- [{finding['severity']}] {finding['message']}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    results = [audit(path) for path in workflow_files(Path(args.root).resolve())]
    ok = not any(f["severity"] == "error" for r in results for f in r["findings"])
    payload = {"ok": ok, "results": results}
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(render_pretty(results))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
