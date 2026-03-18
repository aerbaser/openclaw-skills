#!/usr/bin/env python3
"""Lint a GitHub issue draft against the github-issue-forge structure."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = [
    "Summary",
    "Problem",
    "Desired Outcome",
    "Scope",
    "Out of Scope",
    "Affected Areas",
    "Acceptance Criteria",
    "Verification",
    "Related Context",
]
RECOMMENDED_HEADINGS = [
    "Constraints / Implementation Notes",
    "Risks / Edge Cases",
]


def extract_sections(text: str) -> dict[str, str]:
    pattern = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    sections: dict[str, str] = {}
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[match.group(1).strip()] = text[start:end].strip()
    return sections


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint an issue body for required sections and quality bars.")
    parser.add_argument("--title", required=True, help="Issue title")
    parser.add_argument("--body-file", required=True, help="Path to markdown body file")
    parser.add_argument("--format", choices=["json", "pretty"], default="json")
    args = parser.parse_args()

    body = Path(args.body_file).read_text(encoding="utf-8")
    sections = extract_sections(body)

    errors: list[str] = []
    warnings: list[str] = []

    title = args.title.strip()
    if len(title) < 8:
        errors.append("Title is too short.")
    if len(title) > 110:
        warnings.append("Title is long; trim if possible.")
    if title.endswith("."):
        warnings.append("Avoid a trailing period in the title.")

    for heading in REQUIRED_HEADINGS:
        if heading not in sections:
            errors.append(f"Missing required section: {heading}")
        elif not sections[heading].strip():
            errors.append(f"Section is empty: {heading}")

    for heading in RECOMMENDED_HEADINGS:
        if heading not in sections:
            warnings.append(f"Recommended section missing: {heading}")

    acceptance = sections.get("Acceptance Criteria", "")
    checkbox_count = len(re.findall(r"^\s*-\s*\[[ xX]\]", acceptance, re.MULTILINE))
    if checkbox_count < 3:
        errors.append("Acceptance Criteria should contain at least 3 checkbox items.")

    affected = sections.get("Affected Areas", "")
    if "`" not in affected and "-" not in affected:
        errors.append("Affected Areas should name concrete files, modules, or directories.")

    verification = sections.get("Verification", "")
    if "```" not in verification and not re.search(r"^\s*-\s+", verification, re.MULTILINE):
        errors.append("Verification should include concrete commands or bullet steps.")

    related = sections.get("Related Context", "")
    if "none found" not in related.lower() and "#" not in related and "http" not in related:
        warnings.append("Related Context does not appear to link issues, PRs, docs, or explicitly state none found.")

    score = 100
    score -= 18 * len(errors)
    score -= 5 * len(warnings)
    score = max(score, 0)

    result = {
        "ok": not errors,
        "score": score,
        "errors": errors,
        "warnings": warnings,
        "detected_sections": sorted(sections.keys()),
    }

    if args.format == "json":
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"OK:      {result['ok']}")
        print(f"Score:   {result['score']}")
        if errors:
            print("Errors:")
            for item in errors:
                print(f"  - {item}")
        if warnings:
            print("Warnings:")
            for item in warnings:
                print(f"  - {item}")
        print("Sections:")
        for item in result["detected_sections"]:
            print(f"  - {item}")

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
