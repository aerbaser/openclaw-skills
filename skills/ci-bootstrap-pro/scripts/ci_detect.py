#!/usr/bin/env python3
"""Detect repository stack and suggest CI commands/templates."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    import tomllib  # py311+
except Exception:  # pragma: no cover
    tomllib = None  # type: ignore


def run(cmd: list[str], cwd: Path | None = None) -> str:
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd) if cwd else None,
            capture_output=True, text=True, check=True,
        )
        return proc.stdout.strip()
    except Exception:
        return ""


def repo_root(start: Path) -> Path:
    out = run(["git", "rev-parse", "--show-toplevel"], cwd=start)
    return Path(out) if out else start.resolve()


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        if tomllib:
            return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {}


def detect_node(root: Path) -> dict | None:
    package = root / "package.json"
    if not package.exists():
        return None
    data = read_json(package)
    scripts = data.get("scripts", {}) if isinstance(data.get("scripts"), dict) else {}
    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

    pm = "npm"
    if (root / "pnpm-lock.yaml").exists():
        pm = "pnpm"
    elif (root / "yarn.lock").exists():
        pm = "yarn"
    elif (root / "bun.lockb").exists() or (root / "bun.lock").exists():
        pm = "bun"
    elif (root / "package-lock.json").exists():
        pm = "npm"

    install = {
        "npm": "npm ci",
        "pnpm": "pnpm install --frozen-lockfile",
        "yarn": "yarn --immutable",
        "bun": "bun install --frozen-lockfile",
    }[pm]

    commands = {}
    for key in ["lint", "typecheck", "check", "build"]:
        if key in scripts:
            commands[key] = f"{pm} run {key}"
    if "test:ci" in scripts:
        commands["test"] = f"{pm} run test:ci"
    elif "test" in scripts:
        commands["test"] = "npm test -- --runInBand" if pm == "npm" else f"{pm} run test"

    # React detection
    is_react = "react" in deps or "react-dom" in deps
    has_vitest = "vitest" in deps

    # Solidity detection
    has_hardhat = "hardhat" in deps
    has_foundry = (root / "foundry.toml").exists()

    # Choose template
    if has_hardhat:
        template = "assets/workflows/solidity-hardhat-ci.yml"
    elif is_react:
        template = "assets/workflows/react-ci.yml"
        if has_vitest:
            commands["test"] = f"{pm} run test" if "test" in scripts else "npx vitest run"
        if "test" in scripts and pm == "npm" and not has_vitest:
            commands["test"] = "npm test -- --runInBand"
    else:
        template = "assets/workflows/node-ci.yml"

    result = {
        "ecosystem": "node",
        "package_manager": pm,
        "install": install,
        "scripts": scripts,
        "commands": commands,
        "template": template,
    }
    if is_react:
        result["react"] = True
        result["bundler"] = "vite" if ("vite" in deps or "@vitejs/plugin-react" in deps) else "cra"
    if has_hardhat:
        result["solidity_toolchain"] = "hardhat"

    return result


def detect_foundry(root: Path) -> dict | None:
    """Foundry-only Solidity repos (no package.json or no hardhat dep)."""
    if (root / "foundry.toml").exists():
        return {
            "ecosystem": "solidity-foundry",
            "package_manager": "forge",
            "install": "foundry-rs/foundry-toolchain@v1",
            "commands": {
                "fmt": "forge fmt --check",
                "build": "forge build --sizes",
                "test": "forge test -vvv",
                "coverage": "forge coverage --report summary",
            },
            "template": "assets/workflows/solidity-foundry-ci.yml",
        }
    # Check for .sol files without hardhat
    if any(root.glob("src/**/*.sol")) and not (root / "package.json").exists():
        return {
            "ecosystem": "solidity-foundry",
            "package_manager": "forge",
            "install": "foundry-rs/foundry-toolchain@v1",
            "commands": {
                "build": "forge build --sizes",
                "test": "forge test -vvv",
            },
            "template": "assets/workflows/solidity-foundry-ci.yml",
        }
    return None


def detect_python(root: Path) -> dict | None:
    pyproject = root / "pyproject.toml"
    req = root / "requirements.txt"
    if not pyproject.exists() and not req.exists() and not list(root.glob("requirements*.txt")):
        return None

    data = read_toml(pyproject) if pyproject.exists() else {}
    manager = "pip"
    if (root / "uv.lock").exists():
        manager = "uv"
    elif (root / "poetry.lock").exists():
        manager = "poetry"
    elif (root / "pdm.lock").exists():
        manager = "pdm"

    install = {
        "uv": "uv sync --frozen",
        "poetry": "poetry install --no-interaction --sync",
        "pdm": "pdm install --frozen-lockfile",
        "pip": "python -m pip install -r requirements.txt",
    }[manager]

    tool = data.get("tool", {}) if isinstance(data.get("tool"), dict) else {}
    commands = {}
    if "ruff" in tool or (root / "ruff.toml").exists() or (root / ".ruff.toml").exists():
        commands["lint"] = "ruff check ."
    if "mypy" in tool or (root / "mypy.ini").exists() or (root / ".mypy.ini").exists():
        commands["typecheck"] = "mypy ."
    if (root / "pytest.ini").exists() or (root / "conftest.py").exists() or (root / "tests").exists():
        commands["test"] = "pytest"
    if "test" not in commands:
        commands["test"] = "pytest"

    return {
        "ecosystem": "python",
        "package_manager": manager,
        "install": install,
        "commands": commands,
        "template": "assets/workflows/python-ci.yml",
    }


def detect_go(root: Path) -> dict | None:
    if not (root / "go.mod").exists():
        return None
    return {
        "ecosystem": "go",
        "package_manager": "go",
        "install": "go mod download",
        "commands": {
            "lint": "test -z \"$(gofmt -l .)\"",
            "vet": "go vet ./...",
            "test": "go test ./...",
            "build": "go build ./...",
        },
        "template": "assets/workflows/go-ci.yml",
    }


def detect_rust(root: Path) -> dict | None:
    if not (root / "Cargo.toml").exists():
        return None
    return {
        "ecosystem": "rust",
        "package_manager": "cargo",
        "install": "cargo fetch",
        "commands": {
            "fmt": "cargo fmt --all --check",
            "lint": "cargo clippy --all-targets --all-features -- -D warnings",
            "test": "cargo test --all-features",
            "build": "cargo build --all-features --locked",
        },
        "template": "assets/workflows/rust-ci.yml",
    }


def detect_java(root: Path) -> dict | None:
    if (root / "pom.xml").exists():
        return {
            "ecosystem": "java-maven",
            "package_manager": "maven",
            "install": "mvn -B -ntp dependency:go-offline",
            "commands": {
                "test": "mvn -B -ntp test",
                "build": "mvn -B -ntp verify",
            },
            "template": "assets/workflows/java-maven-ci.yml",
        }
    if (root / "build.gradle").exists() or (root / "build.gradle.kts").exists() or (root / "gradlew").exists():
        return {
            "ecosystem": "java-gradle",
            "package_manager": "gradle",
            "install": "./gradlew dependencies",
            "commands": {
                "test": "./gradlew test",
                "build": "./gradlew build",
            },
            "template": "assets/workflows/java-gradle-ci.yml",
        }
    return None


def detect_dotnet(root: Path) -> dict | None:
    if list(root.glob("*.sln")) or list(root.glob("**/*.csproj")):
        return {
            "ecosystem": "dotnet",
            "package_manager": "nuget",
            "install": "dotnet restore",
            "commands": {
                "build": "dotnet build --no-restore",
                "test": "dotnet test --no-build --verbosity normal",
            },
            "template": "assets/workflows/dotnet-ci.yml",
        }
    return None


def detect_ruby(root: Path) -> dict | None:
    if not (root / "Gemfile").exists():
        return None
    cmds = {}
    if (root / "spec").exists():
        cmds["test"] = "bundle exec rspec"
    if (root / ".rubocop.yml").exists():
        cmds["lint"] = "bundle exec rubocop"
    if "test" not in cmds:
        cmds["test"] = "bundle exec rake test"
    return {
        "ecosystem": "ruby",
        "package_manager": "bundler",
        "install": "bundle install --jobs 4 --retry 3",
        "commands": cmds,
        "template": "assets/workflows/ruby-ci.yml",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect stack and suggest GitHub Actions CI commands/templates.")
    parser.add_argument("--repo-root", "--root", default=".", help="Repository root or child path.")
    parser.add_argument("--format", choices=["json", "pretty", "markdown"], default="json")
    args = parser.parse_args()

    root = repo_root(Path(args.repo_root).resolve())
    detections = []
    for detector in [detect_node, detect_foundry, detect_python, detect_go,
                     detect_rust, detect_java, detect_dotnet, detect_ruby]:
        result = detector(root)
        if result:
            # Skip foundry if already got node+hardhat
            if result["ecosystem"] == "solidity-foundry":
                already_hardhat = any(d.get("solidity_toolchain") == "hardhat" for d in detections)
                if already_hardhat:
                    continue
            detections.append(result)

    default_branch = run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], cwd=root).removeprefix("refs/remotes/origin/")
    if not default_branch:
        default_branch = run(["git", "branch", "--show-current"], cwd=root) or "main"

    monorepo = any((root / name).exists() for name in ["pnpm-workspace.yaml", "turbo.json", "nx.json", "packages"])
    output = {
        "repo_root": str(root),
        "default_branch": default_branch,
        "monorepo": monorepo,
        "detections": detections,
        "recommended_primary": detections[0]["template"] if detections else None,
        "notes": [
            "Prefer top-level permissions: contents: read",
            "Add workflow concurrency to cancel stale runs",
            "Use push + pull_request for default CI",
            "Avoid pull_request_target for building untrusted PR code",
        ],
    }

    if args.format == "json":
        json.dump(output, sys.stdout, indent=2)
        sys.stdout.write("\n")
    elif args.format in ("pretty", "markdown"):
        print(f"Repo root:         {output['repo_root']}")
        print(f"Default branch:    {output['default_branch']}")
        print(f"Monorepo:          {output['monorepo']}")
        print(f"Primary template:  {output['recommended_primary']}")
        if not detections:
            print("No supported stack detected.")
        for item in detections:
            print("")
            print(f"[{item['ecosystem']}]")
            print(f"  package manager: {item['package_manager']}")
            print(f"  install:         {item['install']}")
            print(f"  template:        {item['template']}")
            for name, cmd in item["commands"].items():
                print(f"  {name:14} {cmd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
