#!/usr/bin/env python3
"""Lint a GitHub issue draft against an execution-readiness rubric."""
import argparse
import json
import re
from pathlib import Path

REQUIRED_HEADINGS = [
    "Summary",
    "Affected Areas",
    "Non-goals",
    "Acceptance Criteria",
    "Verification",
]

TITLE_BAD = {"update stuff", "fix issue", "improve code", "cleanup", "misc"}


def read_body(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def heading_present(body: str, heading: str) -> bool:
    return re.search(rf"^##\s+{re.escape(heading)}\s*$", body, flags=re.M) is not None


def count_checkboxes(body: str) -> int:
    return len(re.findall(r"^\s*-\s+\[[ xX]\]\s+", body, flags=re.M))


def has_code_paths(body: str) -> bool:
    patterns = [
        r"`[^`\n]+/[^`\n]+`",
        r"`\.github/[^`\n]+`",
        r"`[^`\n]+\.(ts|tsx|js|jsx|py|go|rs|java|kt|rb|yml|yaml|json|toml|md|sol)`",
    ]
    return any(re.search(p, body) for p in patterns)


def has_verification_command(body: str) -> bool:
    if re.search(r"```(?:bash|sh)[\s\S]*?```", body):
        return True
    return bool(re.search(
        r"^\s*(npm|pnpm|yarn|pytest|cargo|go test|make|uv|poetry|python|forge|npx hardhat)\b",
        body, flags=re.M,
    ))


def lint(title: str, body: str) -> dict:
    errors = []
    warnings = []

    normalized_title = title.strip().lower()
    if len(title.strip()) < 12:
        errors.append("Title is too short to be useful.")
    if normalized_title in TITLE_BAD:
        errors.append("Title is too generic.")
    if (not re.search(r"(feat|fix|refactor|ci|docs|chore|perf|test):", title.lower())
            and len(title.split()) < 4):
        warnings.append("Title does not use a conventional prefix and may be weak.")

    for heading in REQUIRED_HEADINGS:
        if not heading_present(body, heading):
            errors.append(f"Missing required heading: {heading}")

    if count_checkboxes(body) == 0:
        errors.append("Acceptance criteria must contain at least one checkbox.")

    if not has_code_paths(body):
        errors.append("Issue body does not name any concrete file paths or modules.")

    if not has_verification_command(body):
        errors.append("Verification section does not appear to include executable commands.")

    if re.search(r"\b(clean up|improve|support|make better|handle properly)\b", body, flags=re.I):
        warnings.append("Body uses vague verbs; tighten acceptance criteria.")

    if not heading_present(body, "Problem") and not heading_present(body, "Current State"):
        warnings.append("No Problem / Current State section found; consider adding one.")

    score = 10 - (2 * len(errors)) - len(warnings)
    return {
        "ok": len(errors) == 0,
        "score": max(score, 0),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Lint a GitHub issue draft against an execution-readiness rubric.")
    ap.add_argument("--title", required=True)
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--format", choices=["json", "pretty"], default="pretty")
    args = ap.parse_args()

    body = read_body(Path(args.body_file))
    result = lint(args.title, body)

    if args.format == "json":
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["ok"] else 1)

    print(f"Score: {result['score']}/10")
    if result["errors"]:
        print("Blocking errors:")
        for e in result["errors"]:
            print(f"  [ERR] {e}")
    if result["warnings"]:
        print("Warnings:")
        for w in result["warnings"]:
            print(f"  [WARN] {w}")
    if result["ok"]:
        print("OK — issue passes all required checks.")
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
