
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

try:
    import tomllib
except Exception:  # pragma: no cover
    tomllib = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect repository stack and candidate CI commands.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--format", choices=["json", "pretty", "markdown"], default="json")
    return parser.parse_args()


def load_json(path: Path) -> Dict[str, object]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_toml(path: Path) -> Dict[str, object]:
    if tomllib is None:
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def detect(root: Path) -> Dict[str, object]:
    files = {p.name: p for p in root.iterdir()} if root.exists() else {}
    payload: Dict[str, object] = {
        "stacks": [],
        "package_managers": [],
        "lockfiles": [],
        "manifests": [],
        "commands": defaultdict(list),
        "recommended_template": None,
    }

    def add_stack(name: str) -> None:
        if name not in payload["stacks"]:
            payload["stacks"].append(name)

    def add_pm(name: str) -> None:
        if name not in payload["package_managers"]:
            payload["package_managers"].append(name)

    def add_lock(name: str) -> None:
        if name not in payload["lockfiles"]:
            payload["lockfiles"].append(name)

    def add_manifest(name: str) -> None:
        if name not in payload["manifests"]:
            payload["manifests"].append(name)

    commands: Dict[str, List[str]] = payload["commands"]  # type: ignore[assignment]

    # Node / TS
    pkg = root / "package.json"
    if pkg.exists():
        add_stack("node")
        add_manifest("package.json")
        pkg_data = load_json(pkg)
        scripts = pkg_data.get("scripts") or {}
        if isinstance(scripts, dict):
            for key in ("lint", "typecheck", "test", "build", "check", "test:ci", "lint:ci"):
                if key in scripts:
                    commands[key].append(f"npm run {key}")
        if (root / "pnpm-lock.yaml").exists():
            add_pm("pnpm")
            add_lock("pnpm-lock.yaml")
            commands["install"].append("pnpm install --frozen-lockfile")
        elif (root / "yarn.lock").exists():
            add_pm("yarn")
            add_lock("yarn.lock")
            commands["install"].append("yarn --immutable")
        elif (root / "package-lock.json").exists():
            add_pm("npm")
            add_lock("package-lock.json")
            commands["install"].append("npm ci")
        else:
            add_pm("npm")
            commands["install"].append("npm install")

        workspaces = pkg_data.get("workspaces")
        if workspaces:
            payload["recommended_template"] = "node-monorepo.yml"
        else:
            payload["recommended_template"] = "node.yml"

    # Python
    pyproject = root / "pyproject.toml"
    if pyproject.exists() or (root / "requirements.txt").exists():
        add_stack("python")
        if pyproject.exists():
            add_manifest("pyproject.toml")
            py = load_toml(pyproject)
            tool = py.get("tool") or {}
            if isinstance(tool, dict):
                if "poetry" in tool:
                    add_pm("poetry")
                if "uv" in tool:
                    add_pm("uv")
                if "pytest" in tool:
                    commands["test"].append("pytest")
                if "ruff" in tool:
                    commands["lint"].append("ruff check .")
                if "mypy" in tool:
                    commands["typecheck"].append("mypy .")
        if (root / "uv.lock").exists():
            add_lock("uv.lock")
            add_pm("uv")
            commands["install"].append("uv sync --frozen")
        elif (root / "poetry.lock").exists():
            add_lock("poetry.lock")
            add_pm("poetry")
            commands["install"].append("poetry install --no-interaction --sync")
        elif (root / "requirements.txt").exists():
            add_manifest("requirements.txt")
            commands["install"].append("python -m pip install -r requirements.txt")
        else:
            commands["install"].append("python -m pip install -e .")
        payload["recommended_template"] = payload["recommended_template"] or "python.yml"

    # Go
    if (root / "go.mod").exists():
        add_stack("go")
        add_manifest("go.mod")
        commands["lint"].append("go vet ./...")
        commands["test"].append("go test ./...")
        commands["build"].append("go build ./...")
        payload["recommended_template"] = payload["recommended_template"] or "go.yml"

    # Rust
    if (root / "Cargo.toml").exists():
        add_stack("rust")
        add_manifest("Cargo.toml")
        commands["format"].append("cargo fmt --all --check")
        commands["lint"].append("cargo clippy --workspace --all-targets -- -D warnings")
        commands["test"].append("cargo test --all-targets")
        commands["build"].append("cargo build --workspace")
        payload["recommended_template"] = payload["recommended_template"] or "rust.yml"

    # Java
    if (root / "pom.xml").exists():
        add_stack("java-maven")
        add_manifest("pom.xml")
        commands["test"].append("mvn -B test")
        commands["build"].append("mvn -B verify")
        payload["recommended_template"] = payload["recommended_template"] or "java-maven.yml"
    if (root / "build.gradle").exists() or (root / "build.gradle.kts").exists():
        add_stack("java-gradle")
        add_manifest("build.gradle(.kts)")
        commands["test"].append("./gradlew test")
        commands["build"].append("./gradlew build")
        payload["recommended_template"] = payload["recommended_template"] or "java-gradle.yml"

    # .NET
    if any(root.glob("*.sln")) or any(root.rglob("*.csproj")):
        add_stack(".net")
        add_manifest("solution / csproj")
        commands["restore"].append("dotnet restore")
        commands["build"].append("dotnet build --no-restore")
        commands["test"].append("dotnet test --no-build")
        payload["recommended_template"] = payload["recommended_template"] or "dotnet.yml"

    # Ruby
    if (root / "Gemfile").exists() or (root / "gems.rb").exists():
        add_stack("ruby")
        add_manifest("Gemfile")
        commands["install"].append("bundle install --jobs 4 --retry 3")
        commands["test"].append("bundle exec rspec")
        payload["recommended_template"] = payload["recommended_template"] or "ruby.yml"

    # React / Vite / Next.js
    if pkg.exists():
        pkg_data_cached = load_json(pkg)
        deps = {**pkg_data_cached.get("dependencies", {}), **pkg_data_cached.get("devDependencies", {})}
        if any(k in deps for k in ("react", "react-dom", "next", "@remix-run/react", "@preact/preset-vite")):
            add_stack("react")
            bundler = "vite" if "vite" in deps else "cra" if "react-scripts" in deps else "next" if "next" in deps else "unknown"
            payload["bundler"] = bundler
            if bundler == "vite":
                commands["build"].append("npm run build")
                commands["typecheck"].append("npx tsc --noEmit")
            elif bundler == "next":
                commands["build"].append("npm run build")
                commands["lint"].append("npm run lint")
            payload["recommended_template"] = "react-ci.yml"

    # Solidity / Hardhat / Foundry
    foundry_toml = root / "foundry.toml"
    hardhat_config_ts = root / "hardhat.config.ts"
    hardhat_config_js = root / "hardhat.config.js"
    sol_files = list(root.rglob("*.sol"))
    if sol_files or foundry_toml.exists() or hardhat_config_ts.exists() or hardhat_config_js.exists():
        add_stack("solidity")
        if foundry_toml.exists() or (sol_files and not hardhat_config_ts.exists() and not hardhat_config_js.exists()):
            payload["solidity_toolchain"] = "foundry"
            commands["format"].append("forge fmt --check")
            commands["build"].append("forge build")
            commands["test"].append("forge test -vvv")
            commands["coverage"].append("forge coverage")
            payload["recommended_template"] = "solidity-foundry-ci.yml"
        else:
            payload["solidity_toolchain"] = "hardhat"
            commands["build"].append("npx hardhat compile")
            commands["test"].append("npx hardhat test")
            commands["coverage"].append("npx hardhat coverage")
            payload["recommended_template"] = "solidity-hardhat-ci.yml"

    # Make / just can override or supplement
    makefile = root / "Makefile"
    justfile = root / "justfile"
    if makefile.exists():
        add_manifest("Makefile")
        text = makefile.read_text(encoding="utf-8", errors="ignore")
        for target in ("install", "setup", "lint", "typecheck", "test", "build", "check", "ci"):
            if re.search(rf"(?m)^{re.escape(target)}\s*:(?![=])", text):
                commands[target].append(f"make {target}")
        payload["recommended_template"] = payload["recommended_template"] or "generic-make.yml"

    if justfile.exists():
        add_manifest("justfile")
        text = justfile.read_text(encoding="utf-8", errors="ignore")
        for target in ("install", "setup", "lint", "typecheck", "test", "build", "check", "ci"):
            if re.search(rf"(?m)^{re.escape(target)}\s*:", text):
                commands[target].append(f"just {target}")
        payload["recommended_template"] = payload["recommended_template"] or "generic-make.yml"

    deduped = {}
    for key, values in commands.items():
        seen = []
        for value in values:
            if value not in seen:
                seen.append(value)
        deduped[key] = seen
    payload["commands"] = deduped
    return payload


def as_markdown(payload: Dict[str, object]) -> str:
    lines = ["# CI Detection", ""]
    lines.append("- stacks: " + ", ".join(f"`{s}`" for s in payload["stacks"]) if payload["stacks"] else "- stacks: none")
    lines.append("- package managers: " + ", ".join(f"`{s}`" for s in payload["package_managers"]) if payload["package_managers"] else "- package managers: none")
    lines.append("- lockfiles: " + ", ".join(f"`{s}`" for s in payload["lockfiles"]) if payload["lockfiles"] else "- lockfiles: none")
    lines.append("- manifests: " + ", ".join(f"`{s}`" for s in payload["manifests"]) if payload["manifests"] else "- manifests: none")
    if payload.get("recommended_template"):
        lines.append(f"- recommended template: `{payload['recommended_template']}`")
    lines.append("")
    lines.append("## Commands")
    for key, values in payload["commands"].items():
        for value in values:
            lines.append(f"- {key}: `{value}`")
    return "\n".join(lines).rstrip() + "\n"


def as_pretty(payload: Dict[str, object]) -> str:
    lines = ["CI Detection", "============", ""]
    lines.append("stacks: " + (", ".join(payload["stacks"]) or "none"))
    lines.append("package managers: " + (", ".join(payload["package_managers"]) or "none"))
    lines.append("lockfiles: " + (", ".join(payload["lockfiles"]) or "none"))
    lines.append("manifests: " + (", ".join(payload["manifests"]) or "none"))
    if payload.get("recommended_template"):
        lines.append(f"recommended template: {payload['recommended_template']}")
    lines.append("")
    lines.append("commands")
    lines.append("--------")
    for key, values in payload["commands"].items():
        for value in values:
            lines.append(f"- {key}: {value}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    payload = detect(Path(args.root).resolve())
    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.format == "markdown":
        print(as_markdown(payload))
    else:
        print(as_pretty(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
