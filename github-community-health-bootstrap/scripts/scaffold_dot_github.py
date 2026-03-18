#!/usr/bin/env python3
"""
scaffold_dot_github.py

Copies default community health files into the target .github repository,
substituting placeholders for org name, contact email, and maintainer handle.

Placeholders in templates:
  {{ORG}}      — replaced with --owner value
  {{EMAIL}}    — replaced with --contact-email value
  {{MAINTAINER}} — replaced with --maintainer value (default: same as owner)
"""
import argparse, shutil
from pathlib import Path


PLACEHOLDERS = {
    "{{ORG}}":        None,   # filled from --owner
    "{{EMAIL}}":      None,   # filled from --contact-email
    "{{MAINTAINER}}": None,   # filled from --maintainer
}

TEXT_EXTS = {".md", ".yml", ".yaml", ".txt", ".json", ".toml"}


def substitute(text: str, mapping: dict) -> str:
    for placeholder, value in mapping.items():
        if value:
            text = text.replace(placeholder, value)
    return text


def copy_with_substitution(src: Path, dst: Path, mapping: dict, force: bool):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not force:
        print(f"skip (exists) {dst.name}")
        return
    if src.suffix.lower() in TEXT_EXTS:
        content = src.read_text(encoding="utf-8")
        content = substitute(content, mapping)
        dst.write_text(content, encoding="utf-8")
    else:
        shutil.copyfile(src, dst)
    print(f"copied {dst.relative_to(dst.parents[len(dst.parts) - 2]) if len(dst.parts) > 1 else dst.name}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dest", required=True, help="Path to local .github repo checkout")
    p.add_argument("--owner", default="YOUR_ORG", help="GitHub org or user name")
    p.add_argument("--contact-email", default="maintainers@example.com",
                   help="Contact email for SECURITY.md and CODE_OF_CONDUCT.md")
    p.add_argument("--maintainer", default=None,
                   help="GitHub handle of primary maintainer (default: same as --owner)")
    p.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = p.parse_args()

    maintainer = args.maintainer or args.owner

    mapping = {
        "{{ORG}}":        args.owner,
        "{{EMAIL}}":      args.contact_email,
        "{{MAINTAINER}}": maintainer,
        # Also handle common plain-text patterns left by other tools
        "YOUR_ORG":       args.owner,
        "YOUR_CONTACT@EXAMPLE.COM": args.contact_email,
    }

    src_root = Path(__file__).resolve().parent.parent / "templates" / "dot-github"
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    for item in sorted(src_root.rglob("*")):
        if item.is_dir():
            continue
        rel = item.relative_to(src_root)
        target = dest / rel
        copy_with_substitution(item, target, mapping, args.force)

    print(f"\nDone. Review and commit to {args.dest}")
    print(f"  org={args.owner}  email={args.contact_email}  maintainer={maintainer}")


if __name__ == "__main__":
    main()
