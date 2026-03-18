
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preview or apply archive/delete actions from repo_score output.")
    parser.add_argument("--score-file", required=True, help="Path to repo_score JSON")
    parser.add_argument("--archive-candidates", action="store_true", help="Select all archive candidates")
    parser.add_argument("--delete-candidates", action="store_true", help="Select all delete candidates")
    parser.add_argument("--repos", nargs="*", default=[], help="Explicit OWNER/REPO names to act on")
    parser.add_argument("--apply", action="store_true", help="Execute instead of preview")
    return parser.parse_args()


def require_gh() -> None:
    if shutil.which("gh") is None:
        raise RuntimeError("gh CLI not found in PATH.")


def choose_repos(payload: Dict[str, Any], args: argparse.Namespace) -> Tuple[List[str], List[str]]:
    archive_list: List[str] = []
    delete_list: List[str] = []
    for repo in payload.get("repositories") or []:
        full = repo["nameWithOwner"]
        if args.repos and full in args.repos:
            action = repo["recommendedAction"]
            if "archive" in action:
                archive_list.append(full)
            elif "delete" in action:
                delete_list.append(full)
            continue
        if args.archive_candidates and repo["recommendedAction"] == "archive-candidate":
            archive_list.append(full)
        if args.delete_candidates and repo["recommendedAction"] == "delete-candidate":
            delete_list.append(full)
    return archive_list, delete_list


def run(cmd: List[str]) -> None:
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "command failed")


def main() -> int:
    args = parse_args()
    if not args.archive_candidates and not args.delete_candidates and not args.repos:
        print("Nothing selected. Use --archive-candidates, --delete-candidates, or --repos.", file=sys.stderr)
        return 2

    payload = json.loads(Path(args.score_file).read_text(encoding="utf-8"))
    archive_list, delete_list = choose_repos(payload, args)

    if not args.apply:
        print(json.dumps({
            "mode": "preview",
            "archive": archive_list,
            "delete": delete_list,
            "commands": (
                [f"gh repo archive {repo} --yes" for repo in archive_list] +
                [f"gh repo delete {repo} --yes" for repo in delete_list]
            ),
        }, indent=2))
        return 0

    try:
        require_gh()
        for repo in archive_list:
            run(["gh", "repo", "archive", repo, "--yes"])
        for repo in delete_list:
            run(["gh", "repo", "delete", repo, "--yes"])
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1

    print(json.dumps({"ok": True, "archived": archive_list, "deleted": delete_list}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
