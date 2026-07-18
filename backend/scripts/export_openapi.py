from __future__ import annotations

import argparse
import json
from pathlib import Path

from time_agent.bootstrap.app import create_app
from time_agent.config import Settings

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "contracts" / "openapi.json"


def render_openapi() -> str:
    app = create_app(Settings(environment="ci", build_sha="contract"))
    return json.dumps(app.openapi(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render_openapi()

    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print("contracts/openapi.json is stale; run contract-generate")
            return 1
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
