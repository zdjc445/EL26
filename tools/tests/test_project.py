from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from unittest.mock import call, patch

from tools.project import ROOT, run_named


class ProjectCommandTests(unittest.TestCase):
    def test_verify_runs_every_gate_in_order(self) -> None:
        expected = [
            ["uv", "run", "--project", "backend", "ruff", "format", "--config", "backend/pyproject.toml", "--check", "backend", "tools"],
            ["pnpm", "--dir", "frontend", "format:check"],
            ["uv", "run", "--project", "backend", "ruff", "check", "--config", "backend/pyproject.toml", "backend", "tools"],
            ["pnpm", "--dir", "frontend", "lint"],
            ["uv", "run", "--project", "backend", "mypy", "--config-file", "backend/pyproject.toml", "backend/src", "backend/tests", "tools"],
            ["pnpm", "--dir", "frontend", "typecheck"],
            ["uv", "run", "--project", "backend", "pytest", "backend/tests/unit", "backend/tests/architecture", "-q"],
            ["pnpm", "--dir", "frontend", "test:unit"],
            ["uv", "run", "--project", "backend", "pytest", "backend/tests/integration", "-q"],
            ["python", "tools/check_contract.py"],
            ["uv", "run", "--project", "backend", "pip-audit", "--local"],
            ["uv", "run", "--project", "backend", "licensecheck", "--zero", "--only-licenses", "mit", "apache", "bsd", "isc", "mpl", "python", "unlicense", "0bsd", "cc0", "--requirements-paths", "backend/pyproject.toml", "--groups", "dev"],
            ["pnpm", "--dir", "frontend", "audit", "--audit-level", "high"],
            ["pnpm", "--dir", "frontend", "exec", "license-checker-rseidelsohn", "--start", ".", "--unknown", "--onlyAllow", "MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC;0BSD;Python-2.0;PSF-2.0;MPL-2.0;Unlicense;CC0-1.0;CC-BY-4.0"],
            ["python", "-m", "compileall", "-q", "backend/src"],
            ["pnpm", "--dir", "frontend", "build"],
            ["pnpm", "--dir", "frontend", "test:e2e"],
        ]

        with patch("tools.project.subprocess.run") as runner:
            run_named("verify")

        self.assertEqual(
            runner.call_args_list,
            [call(command, cwd=Path(ROOT), check=True) for command in expected],
        )

    def test_failure_stops_the_command_group(self) -> None:
        failure = subprocess.CalledProcessError(1, ["uv"])
        with patch("tools.project.subprocess.run", side_effect=failure) as runner:
            with self.assertRaises(subprocess.CalledProcessError):
                run_named("verify")
        runner.assert_called_once()


if __name__ == "__main__":
    unittest.main()
