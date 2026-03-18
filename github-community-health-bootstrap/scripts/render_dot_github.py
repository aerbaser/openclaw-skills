
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

TOKENS = [
    "OWNER_NAME",
    "SUPPORT_URL",
    "SECURITY_EMAIL",
    "DISCUSSIONS_URL",
    "PROJECT_NAME",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render shared .github templates with placeholder replacements.")
    parser.add_argument("--src", required=True, help="Template source directory")
    parser.add_argument("--dest", required=True, help="Destination directory")
    parser.add_argument("--owner-name", default="{{OWNER_NAME}}")
    parser.add_argument("--support-url", default="{{SUPPORT_URL}}")
    parser.add_argument("--security-email", default="{{SECURITY_EMAIL}}")
    parser.add_argument("--discussions-url", default="{{DISCUSSIONS_URL}}")
    parser.add_argument("--project-name", default="{{PROJECT_NAME}}")
    return parser.parse_args()


def replace_tokens(text: str, args: argparse.Namespace) -> str:
    mapping = {
        "{{OWNER_NAME}}": args.owner_name,
        "{{SUPPORT_URL}}": args.support_url,
        "{{SECURITY_EMAIL}}": args.security_email,
        "{{DISCUSSIONS_URL}}": args.discussions_url,
        "{{PROJECT_NAME}}": args.project_name,
    }
    for old, new in mapping.items():
        text = text.replace(old, new)
    return text


def main() -> int:
    args = parse_args()
    src = Path(args.src)
    dest = Path(args.dest)
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    for path in src.rglob("*"):
        relative = path.relative_to(src)
        target = dest / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() in {".md", ".yml", ".yaml", ".txt"}:
            content = path.read_text(encoding="utf-8")
            target.write_text(replace_tokens(content, args), encoding="utf-8")
        else:
            shutil.copy2(path, target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
