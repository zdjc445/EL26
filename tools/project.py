from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GROUPS: dict[str, tuple[list[str], ...]] = {
    "format": (
        ["uv", "run", "--project", "backend", "ruff", "format", "--config", "backend/pyproject.toml", "backend", "tools"],
        ["pnpm", "--dir", "frontend", "format"],
    ),
    "format-check": (
        ["uv", "run", "--project", "backend", "ruff", "format", "--config", "backend/pyproject.toml", "--check", "backend", "tools"],
        ["pnpm", "--dir", "frontend", "format:check"],
    ),
    "lint": (
        ["uv", "run", "--project", "backend", "ruff", "check", "--config", "backend/pyproject.toml", "backend", "tools"],
        ["pnpm", "--dir", "frontend", "lint"],
    ),
    "typecheck": (
        ["uv", "run", "--project", "backend", "mypy", "--config-file", "backend/pyproject.toml", "backend/src", "backend/tests", "tools"],
        ["pnpm", "--dir", "frontend", "typecheck"],
    ),
    "test-unit": (
        ["uv", "run", "--project", "backend", "pytest", "backend/tests/unit", "backend/tests/architecture", "-q"],
        ["pnpm", "--dir", "frontend", "test:unit"],
    ),
    "test-integration": (
        ["uv", "run", "--project", "backend", "pytest", "backend/tests/integration", "-q"],
    ),
    "test-e2e": (["pnpm", "--dir", "frontend", "test:e2e"],),
    "contract-generate": (
        ["uv", "run", "--project", "backend", "python", "backend/scripts/export_openapi.py"],
        [
            "pnpm",
            "--dir",
            "frontend",
            "exec",
            "openapi-typescript",
            "../contracts/openapi.json",
            "-o",
            "src/shared/api/schema.d.ts",
        ],
    ),
    "contract-check": (["python", "tools/check_contract.py"],),
    "security": (
        ["uv", "run", "--project", "backend", "pip-audit", "--local"],
        [
            "uv",
            "run",
            "--project",
            "backend",
            "licensecheck",
            "--zero",
            "--only-licenses",
            "mit",
            "apache",
            "bsd",
            "isc",
            "mpl",
            "python",
            "unlicense",
            "0bsd",
            "cc0",
            "--requirements-paths",
            "backend/pyproject.toml",
            "--groups",
            "dev",
        ],
        ["pnpm", "--dir", "frontend", "audit", "--audit-level", "high"],
        [
            "pnpm",
            "--dir",
            "frontend",
            "exec",
            "license-checker-rseidelsohn",
            "--start",
            ".",
            "--unknown",
            "--onlyAllow",
            "MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC;0BSD;Python-2.0;PSF-2.0;MPL-2.0;Unlicense;CC0-1.0;CC-BY-4.0",
        ],
    ),
    "build": (
        ["python", "-m", "compileall", "-q", "backend/src"],
        ["pnpm", "--dir", "frontend", "build"],
    ),
}

GROUPS["verify"] = (
    *GROUPS["format-check"],
    *GROUPS["lint"],
    *GROUPS["typecheck"],
    *GROUPS["test-unit"],
    *GROUPS["test-integration"],
    *GROUPS["contract-check"],
    *GROUPS["security"],
    *GROUPS["build"],
    *GROUPS["test-e2e"],
)


def run_named(name: str) -> None:
    for command in GROUPS[name]:
        subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Time repository quality commands.")
    parser.add_argument("command", choices=sorted(GROUPS))
    command = parser.parse_args().command
    if not isinstance(command, str):
        raise TypeError("command must be a string")
    run_named(command)


if __name__ == "__main__":
    main()
