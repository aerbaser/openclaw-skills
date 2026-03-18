
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

REQUIRED_HEADINGS = [
    "summary",
    "problem",
    "desired outcome",
    "affected areas",
    "constraints / notes",
    "non-goals",
    "acceptance criteria",
    "verification",
    "related context",
]

VAGUE_TERMS = {
    "improve", "support", "cleanup", "clean up", "make better", "fix things", "various",
    "misc", "stuff", "etc",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint a GitHub issue body for execution-grade quality.")
    parser.add_argument("--title", required=True, help="Issue title.")
    parser.add_argument("--body-file", required=True, help="Path to Markdown file.")
    parser.add_argument("--format", choices=["json", "pretty"], default="json")
    return parser.parse_args()


def load_body(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section_map(body: str) -> Dict[str, str]:
    sections: Dict[str, List[str]] = {}
    current = None
    for line in body.splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line.strip())
        if heading:
            current = heading.group(1).strip().lower()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def find_missing_headings(sections: Dict[str, str]) -> List[str]:
    missing = []
    for heading in REQUIRED_HEADINGS:
        if heading not in sections:
            missing.append(heading)
    return missing


def section_has_paths(text: str) -> bool:
    if re.search(r"`[^`\n]+[/\\][^`\n]+`", text):
        return True
    if re.search(r"(?m)^\s*-\s+`[^`\n]+`", text):
        return True
    if re.search(r"(?m)^\s*-\s+[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+", text):
        return True
    return False


def section_has_checkboxes(text: str) -> bool:
    return len(re.findall(r"(?m)^\s*-\s+\[[ xX]\]\s+", text)) >= 2


def verification_has_commands(text: str) -> bool:
    if "```" in text and re.search(r"```[a-zA-Z0-9_-]*\n.+?\n```", text, re.DOTALL):
        return True
    if re.search(r"(?m)^\s*-\s+`[^`\n]+`", text):
        return True
    if re.search(r"(?m)^\s{0,4}(npm|pnpm|yarn|pytest|python|go|cargo|mvn|./gradlew|dotnet|bundle|make|just)\b", text):
        return True
    return False


def vague_phrases(text: str) -> List[str]:
    lowered = text.lower()
    found = [term for term in VAGUE_TERMS if term in lowered]
    return sorted(found)


def lint(title: str, body: str) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    if len(title.strip()) < 8:
        errors.append("Title is too short to be routing-meaningful.")
    if re.fullmatch(r"[A-Za-z0-9 _-]+", title.strip()) and len(title.strip().split()) < 2:
        warnings.append("Title looks generic; consider repository-native wording.")
    if len(body.strip()) < 400:
        errors.append("Body is too short; likely missing operational context.")

    sections = section_map(body)
    missing = find_missing_headings(sections)
    if missing:
        errors.append("Missing required sections: " + ", ".join(missing))

    affected = sections.get("affected areas", "")
    if affected and not section_has_paths(affected):
        errors.append("Affected Areas does not name exact paths or modules.")

    acceptance = sections.get("acceptance criteria", "")
    if acceptance and not section_has_checkboxes(acceptance):
        errors.append("Acceptance Criteria must include at least two checkboxes.")

    verification = sections.get("verification", "")
    if verification and not verification_has_commands(verification):
        errors.append("Verification section must include concrete commands or fenced command blocks.")

    non_goals = sections.get("non-goals", "")
    if non_goals and len(non_goals.strip()) < 20:
        warnings.append("Non-Goals section is very thin; scope may still sprawl.")

    constraints = sections.get("constraints / notes", "")
    if constraints and "assumption" not in constraints.lower():
        warnings.append("If any facts are inferred, label them explicitly as assumptions.")

    for section_name in ("summary", "problem", "desired outcome", "non-goals", "acceptance criteria"):
        text = sections.get(section_name, "")
        found = vague_phrases(text)
        if found:
            warnings.append(f"Section '{section_name}' contains vague terms: {', '.join(found)}")

    if "related context" in sections and len(sections["related context"]) < 10:
        warnings.append("Related Context section is extremely short; link adjacent work if it exists.")

    return errors, warnings


def render_pretty(errors: List[str], warnings: List[str]) -> str:
    lines = ["Issue Lint", "==========", ""]
    lines.append("Blocking errors")
    lines.append("---------------")
    if errors:
        for item in errors:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("Warnings")
    lines.append("--------")
    if warnings:
        for item in warnings:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("Result")
    lines.append("------")
    lines.append("PASS" if not errors else "FAIL")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    body = load_body(Path(args.body_file))
    errors, warnings = lint(args.title, body)
    payload = {"ok": not errors, "errors": errors, "warnings": warnings}
    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(render_pretty(errors, warnings))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
