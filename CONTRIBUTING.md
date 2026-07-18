# Contributing

## Required toolchain

- Python 3.13.14
- uv 0.11.29
- Node.js 24.18.0 LTS
- pnpm 11.13.1

## Install

```bash
uv sync --project backend --all-groups --frozen
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend exec playwright install chromium
```

## Repository commands

```bash
python tools/project.py format
python tools/project.py verify
```

All changes follow the approved Spec → Tests → Diff → Review lifecycle in `docs/engineering/development-lifecycle.md`.
