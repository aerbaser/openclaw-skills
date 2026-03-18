
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit GitHub Actions workflow sanity.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--format", choices=["json", "pretty"], default="json")
    return parser.parse_args()


def workflow_files(root: Path) -> List[Path]:
    wf_root = root / ".github" / "workflows"
    if not wf_root.exists():
        return []
    return sorted([p for p in wf_root.iterdir() if p.suffix in {".yml", ".yaml"} and p.is_file()])


def is_pinned_action(ref: str) -> bool:
    if re.fullmatch(r"[0-9a-f]{40}", ref):
        return True
    if ref.startswith("v") and re.fullmatch(r"v\d+(\.\d+){0,2}", ref):
        return True
    return False


def action_is_first_party(uses: str) -> bool:
    return uses.startswith("actions/") or uses.startswith("github/")


def audit_workflow(path: Path) -> Dict[str, object]:
    errors: List[str] = []
    warnings: List[str] = []

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return {"file": str(path), "errors": [f"YAML parse failed: {exc}"], "warnings": []}

    on_value = data.get("on", data.get(True))
    permissions = data.get("permissions")
    concurrency = data.get("concurrency")
    jobs = data.get("jobs") or {}

    pull_request_target = False
    if isinstance(on_value, str):
        pull_request_target = on_value == "pull_request_target"
    elif isinstance(on_value, list):
        pull_request_target = "pull_request_target" in on_value
    elif isinstance(on_value, dict):
        pull_request_target = "pull_request_target" in on_value

    if permissions is None:
        warnings.append("Missing top-level permissions.")
    elif permissions == "write-all":
        errors.append("permissions: write-all is too broad.")
    elif isinstance(permissions, dict):
        for key, value in permissions.items():
            if isinstance(value, str) and value.startswith("write"):
                warnings.append(f"Top-level permission '{key}: {value}' is write-capable; confirm it is required.")

    if concurrency is None:
        warnings.append("Missing top-level concurrency.")
    elif isinstance(concurrency, dict) and not concurrency.get("cancel-in-progress"):
        warnings.append("Concurrency exists but does not cancel stale runs.")

    if pull_request_target:
        for job in jobs.values():
            steps = (job or {}).get("steps") or []
            for step in steps:
                uses = str(step.get("uses", ""))
                run = str(step.get("run", ""))
                if uses.startswith("actions/checkout"):
                    errors.append("pull_request_target with checkout is risky for untrusted PR code.")
                if "github.event.pull_request.head" in run:
                    errors.append("pull_request_target workflow references attacker-controlled PR head content.")
                if uses and "@" in uses:
                    action, ref = uses.split("@", 1)
                    if not action_is_first_party(action) and not is_pinned_action(ref):
                        warnings.append(f"Third-party action not pinned safely under pull_request_target: {uses}")

    if isinstance(on_value, dict):
        if "pull_request" not in on_value and "push" not in on_value and "workflow_dispatch" not in on_value:
            warnings.append("Workflow has unusual triggers; confirm this is intentional.")

    for job_name, job in jobs.items():
        job_perms = (job or {}).get("permissions")
        if job_perms == "write-all":
            errors.append(f"Job '{job_name}' uses write-all permissions.")
        steps = (job or {}).get("steps") or []
        for step in steps:
            uses = step.get("uses")
            if not uses:
                continue
            uses = str(uses)
            if "@" not in uses:
                warnings.append(f"Action without explicit ref: {uses}")
                continue
            action, ref = uses.split("@", 1)
            if not action_is_first_party(action) and ref in {"main", "master", "latest"}:
                errors.append(f"Third-party action pinned to floating branch/tag: {uses}")
            elif not action_is_first_party(action) and not is_pinned_action(ref):
                warnings.append(f"Third-party action not pinned to SHA or stable version: {uses}")

    return {"file": str(path), "errors": errors, "warnings": warnings}


def render_pretty(results: List[Dict[str, object]]) -> str:
    lines = ["Workflow Sanity", "===============", ""]
    if not results:
        lines.append("No workflow files found.")
        return "\n".join(lines) + "\n"

    for result in results:
        lines.append(result["file"])
        lines.append("-" * len(str(result["file"])))
        errors = result["errors"]
        warnings = result["warnings"]
        if errors:
            lines.append("Errors:")
            for item in errors:
                lines.append(f"- {item}")
        else:
            lines.append("Errors: none")
        if warnings:
            lines.append("Warnings:")
            for item in warnings:
                lines.append(f"- {item}")
        else:
            lines.append("Warnings: none")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    results = [audit_workflow(path) for path in workflow_files(root)]
    ok = not any(result["errors"] for result in results)
    payload = {"ok": ok, "results": results}
    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(render_pretty(results))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
