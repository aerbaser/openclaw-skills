#!/usr/bin/env python3
import argparse, shutil
from pathlib import Path

def copy_if_missing(src: Path, dst: Path, force: bool):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not force:
        return
    shutil.copyfile(src, dst)
    print(f"copied {dst}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dest", default=".")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    base = Path(__file__).resolve().parent.parent / "templates"
    dest = Path(args.dest)

    copy_if_missing(base / "CODEOWNERS", dest / ".github" / "CODEOWNERS", args.force)
    copy_if_missing(base / "PULL_REQUEST_TEMPLATE.md", dest / ".github" / "PULL_REQUEST_TEMPLATE.md", args.force)

if __name__ == "__main__":
    main()
