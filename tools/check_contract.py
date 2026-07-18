from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMITTED_TYPES = ROOT / "frontend" / "src" / "shared" / "api" / "schema.d.ts"
PNPM_EXECUTABLE = "pnpm.cmd" if os.name == "nt" else "pnpm"


def main() -> int:
    openapi_command = [
        "uv",
        "run",
        "--project",
        "backend",
        "python",
        "backend/scripts/export_openapi.py",
        "--check",
    ]
    subprocess.run(  # noqa: S603
        openapi_command,
        cwd=ROOT,
        check=True,
    )

    with tempfile.TemporaryDirectory() as directory:
        generated = Path(directory) / "schema.d.ts"
        types_command = [
            PNPM_EXECUTABLE,
            "--dir",
            "frontend",
            "exec",
            "openapi-typescript",
            "../contracts/openapi.json",
            "-o",
            str(generated),
        ]
        subprocess.run(  # noqa: S603
            types_command,
            cwd=ROOT,
            check=True,
        )
        if not COMMITTED_TYPES.exists() or COMMITTED_TYPES.read_bytes() != generated.read_bytes():
            print("frontend/src/shared/api/schema.d.ts is stale; run contract-generate")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
