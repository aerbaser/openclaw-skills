#!/usr/bin/env python3
import argparse, csv, subprocess, sys

def run(cmd, dry_run=False):
    print("$", " ".join(cmd))
    if not dry_run:
        proc = subprocess.run(cmd)
        if proc.returncode != 0:
            raise SystemExit(proc.returncode)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--plan", required=True, help="CSV from repo_score.py")
    p.add_argument("--apply-archive", action="store_true")
    p.add_argument("--apply-delete", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    with open(args.plan, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        repo = row["nameWithOwner"]
        action = row["action"]
        if action == "archive_candidate" and args.apply_archive:
            run(["gh", "repo", "archive", repo, "--yes"], dry_run=args.dry_run)
        elif action == "delete_candidate" and args.apply_delete:
            run(["gh", "repo", "delete", repo, "--yes"], dry_run=args.dry_run)

if __name__ == "__main__":
    main()
