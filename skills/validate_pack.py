
#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

BASE = Path(__file__).resolve().parent
SKILL_REF_RE = re.compile(r"\{baseDir\}/([A-Za-z0-9_./-]+)")


def skill_dirs() -> List[Path]:
    return sorted([p for p in BASE.iterdir() if p.is_dir() and (p / "SKILL.md").exists()])


def check_references(skill_dir: Path) -> List[str]:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    missing = []
    for rel in sorted(set(SKILL_REF_RE.findall(text))):
        target = skill_dir / rel
        if not target.exists():
            missing.append(f"{skill_dir.name}: missing referenced path {rel}")
    return missing


def check_python(path: Path) -> str | None:
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        return None
    except SyntaxError as exc:
        return f"{path.relative_to(BASE)}: python syntax error: {exc}"


def check_yaml(path: Path) -> str | None:
    try:
        yaml.safe_load(path.read_text(encoding="utf-8"))
        return None
    except Exception as exc:
        return f"{path.relative_to(BASE)}: yaml parse error: {exc}"


def main() -> int:
    errors: List[str] = []
    warnings: List[str] = []

    skills = skill_dirs()
    if not skills:
        errors.append("No skill directories found.")

    for skill_dir in skills:
        errors.extend(check_references(skill_dir))

    for path in BASE.rglob("*.py"):
        if path.name == Path(__file__).name:
            continue
        err = check_python(path)
        if err:
            errors.append(err)

    for path in BASE.rglob("*.yml"):
        err = check_yaml(path)
        if err:
            errors.append(err)
    for path in BASE.rglob("*.yaml"):
        err = check_yaml(path)
        if err:
            errors.append(err)

    report = {
        "base": str(BASE),
        "skills": [p.name for p in skills],
        "errors": errors,
        "warnings": warnings,
        "ok": not errors,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
