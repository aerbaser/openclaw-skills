
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preview or apply GitHub labels from a JSON file.")
    parser.add_argument("--repo", required=True, help="OWNER/REPO")
    parser.add_argument("--labels-file", required=True, help="Path to labels.json")
    parser.add_argument("--apply", action="store_true", help="Apply with gh label create --force")
    return parser.parse_args()


def require_gh() -> None:
    if shutil.which("gh") is None:
        raise RuntimeError("gh CLI not found in PATH.")


def preview(labels: List[dict], repo: str) -> List[str]:
    commands = []
    for label in labels:
        commands.append(
            "gh label create {name} --repo {repo} --color {color} --description {desc} --force".format(
                name=json.dumps(label["name"]),
                repo=repo,
                color=json.dumps(label["color"]),
                desc=json.dumps(label["description"]),
            )
        )
    return commands


def apply(labels: List[dict], repo: str) -> None:
    for label in labels:
        completed = subprocess.run(
            [
                "gh", "label", "create", label["name"],
                "--repo", repo,
                "--color", label["color"],
                "--description", label["description"],
                "--force",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or f"Failed syncing label {label['name']}")


def main() -> int:
    args = parse_args()
    labels = json.loads(Path(args.labels_file).read_text(encoding="utf-8"))
    if not args.apply:
        print(json.dumps({"mode": "preview", "repo": args.repo, "commands": preview(labels, args.repo)}, indent=2))
        return 0
    try:
        require_gh()
        apply(labels, args.repo)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, "repo": args.repo, "labelsSynced": len(labels)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
