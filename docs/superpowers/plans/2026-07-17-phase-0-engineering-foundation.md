# Time Phase 0 Engineering Foundation Implementation Plan

状态：已批准

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立可重复安装、可测试、可审查和可由 GitHub Actions 验证的 Time 工程基础，并打通后端存活探针、前端状态页、OpenAPI 契约和容器构建的第一条生产形态交付链路。

**Architecture:** 前后端保持独立构建：Python `time_agent` 包提供 FastAPI，React 单页应用只通过版本化 HTTP 契约访问后端。根目录的无第三方 Python 命令入口统一驱动格式、静态检查、类型检查、测试、契约、E2E 和构建；GitHub Actions 调用同一入口。阶段 0 不创建业务表、不接入外部供应商，也不实现任何演示业务功能。

**Tech Stack:** Python 3.13.14、uv 0.11.29、FastAPI 0.139.2、Pydantic Settings 2.14.2、Uvicorn 0.51.0、pytest 9.1.1、Ruff 0.15.22、mypy 2.3.0；Node.js 24.18.0 LTS、pnpm 11.13.1、React 19.2.7、React Router 8.2.0、TanStack Query 5.101.2、TypeScript 5.9.3、Vite 8.1.5、Vitest 4.1.10、Playwright 1.61.1。

## Global Constraints

- 产品展示名必须是 `Time`；Python 顶层包必须是 `time_agent`，不得创建名为 `time` 的本地包。
- Git remote 必须保持 `git@github.com:zdjc445/EL26.git`；CI 文件必须使用 GitHub Actions。
- 后端开发和 CI 运行时固定 `Python 3.13.14`，包元数据兼容范围为 `Python >=3.13,<3.14`；Node.js 固定 `24.18.0`；pnpm 固定 `11.13.1`；uv 固定 `0.11.29`。
- Python 和 npm 直接依赖使用本计划中的精确版本，并提交 `backend/uv.lock` 与 `frontend/pnpm-lock.yaml`。
- TypeScript 固定为 `5.9.3`，因为本计划锁定的 `openapi-typescript@7.13.0` 要求 TypeScript `^5.x`，`typescript-eslint@8.64.0` 要求 TypeScript `<6.1.0`；不得升级到 6 或 7 后跳过 peer compatibility 检查。
- 阶段 0 只实现系统存活能力和工程链路，不实现 `AUTH`、`CAL`、`LEARN`、`KB`、`CHAT` 或 `RAG` 产品行为。
- 不添加 LangGraph、LangChain、Celery、SQLAlchemy、Qdrant、RabbitMQ、Valkey 或对象存储客户端；这些依赖在首次实际使用的阶段加入。
- 不添加 OCR、图片上传、扫描 PDF、外部日历、课表导入、微服务或 Kubernetes 代码。
- API 路径固定为 `/api/v1`；存活探针固定为 `GET /api/v1/health/live`。
- 环境变量前缀固定为 `TIME_`；本阶段只定义 `TIME_ENVIRONMENT` 与 `TIME_BUILD_SHA`。
- 前端开发服务器通过 Vite 代理访问 `/api`；浏览器代码不得硬编码后端主机名。
- 生成的 OpenAPI JSON 和 TypeScript 类型必须提交，并由可重复命令检查漂移。
- GitHub Actions 和容器基础镜像必须固定到不可变提交或 manifest digest。
- 实施分支固定为 `phase/p0-engineering-foundation`，并在隔离 worktree 中执行；每个任务以独立提交结束，提交格式遵循 `<type>(<scope>): <summary>`。
- 本计划的状态变为 `已批准` 前不得执行。

---

## File Responsibility Map

| 路径 | 单一职责 |
|---|---|
| `tools/project.py` | 无第三方依赖的仓库级命令编排，不承载业务逻辑 |
| `tools/tests/test_project.py` | 验证命令名称、顺序、工作目录和失败传播 |
| `backend/pyproject.toml` | Python 包、直接依赖和工具规则的权威清单 |
| `backend/uv.lock` | Python 完整依赖锁 |
| `backend/src/time_agent/config.py` | `TIME_` 环境配置解析 |
| `backend/src/time_agent/bootstrap/app.py` | FastAPI 组合根和应用工厂 |
| `backend/src/time_agent/modules/system/api.py` | 系统探针 HTTP 接口 |
| `backend/src/time_agent/modules/system/schemas.py` | 系统探针公开响应 Schema |
| `backend/src/time_agent/main.py` | Uvicorn 导入入口 |
| `backend/scripts/export_openapi.py` | 确定性导出和检查 OpenAPI JSON |
| `backend/tests/unit/system/test_live.py` | 存活探针公开行为 |
| `backend/tests/integration/system/test_openapi.py` | HTTP/OpenAPI 集成契约 |
| `frontend/package.json` | 前端直接依赖、脚本和包管理器版本 |
| `frontend/pnpm-lock.yaml` | 前端完整依赖锁 |
| `frontend/src/app/App.tsx` | 路由定义，不承载页面业务 |
| `frontend/src/app/AppProviders.tsx` | React Query 与 Router 组合 |
| `frontend/src/features/system/api.ts` | 类型化系统探针客户端 |
| `frontend/src/features/system/SystemStatusPage.tsx` | 生产运维状态页 |
| `frontend/src/features/system/SystemStatusPage.test.tsx` | 状态页组件行为 |
| `frontend/tests/e2e/system-status.spec.ts` | 后端到浏览器的第一条 E2E |
| `contracts/openapi.json` | 后端公开 HTTP 契约快照 |
| `frontend/src/shared/api/schema.d.ts` | 从 OpenAPI 生成的 TypeScript 类型 |
| `tools/check_contract.py` | 检查 OpenAPI 和生成类型是否漂移 |
| `docker/backend.Dockerfile` | 后端不可变运行镜像 |
| `docker/frontend.Dockerfile` | 前端不可变静态站点镜像 |
| `docker/nginx.conf` | 前端静态站点、SPA fallback 和容器探针 |
| `.github/workflows/ci.yml` | PR 与 `main` 的必需验证 |
| `.github/branch-protection.json` | `main` 分支保护的可审查 REST API 请求体 |

## Execution Preflight

The repository inspection on 2026-07-17 returned `main...origin/main [gone]`: the configured remote exists, but remote `main` does not. After this plan is approved and committed, initialize the documentation baseline before creating the Phase 0 worktree:

Run: `git status --short`

Expected: no output.

Run: `git branch --show-current`

Expected: exactly `main`.

Run: `git remote get-url origin`

Expected: exactly `git@github.com:zdjc445/EL26.git`.

Run: `git push --set-upstream origin main`

Expected: remote branch `main` is created from the locally approved documentation baseline.

Then use `superpowers:using-git-worktrees` to create branch `phase/p0-engineering-foundation` from `main`. Do not implement Phase 0 in the documentation worktree.

### Task 1: Repository governance and command contract

**Files:**
- Create: `.editorconfig`
- Create: `.gitattributes`
- Create: `.python-version`
- Create: `.node-version`
- Create: `CODEOWNERS`
- Create: `README.md`
- Create: `CONTRIBUTING.md`
- Create: `SECURITY.md`
- Create: `.github/pull_request_template.md`
- Create: `tools/__init__.py`
- Create: `tools/project.py`
- Create: `tools/tests/__init__.py`
- Create: `tools/tests/test_project.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: repository root `D:/EL26`; GitHub owner `zdjc445`; product identifiers from Global Constraints.
- Produces: `python tools/project.py <command>` where `<command>` is exactly `format`, `format-check`, `lint`, `typecheck`, `test-unit`, `test-integration`, `test-e2e`, `contract-generate`, `contract-check`, `security`, `build`, or `verify`.

- [ ] **Step 1: Write the failing command-runner test**

Create empty `tools/__init__.py` and `tools/tests/__init__.py`, then create `tools/tests/test_project.py`:

```python
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
```

- [ ] **Step 2: Run the test and verify the intended failure**

Run: `python -m unittest tools.tests.test_project -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'tools.project'`.

- [ ] **Step 3: Implement the repository command runner**

Create `tools/project.py`:

```python
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
```

- [ ] **Step 4: Run the command-runner tests**

Run: `python -m unittest tools.tests.test_project -v`

Expected: 2 tests PASS.

- [ ] **Step 5: Add repository governance files**

Create `.editorconfig`:

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

[*.py]
indent_size = 4

[*.md]
trim_trailing_whitespace = false
```

Create `.gitattributes`:

```gitattributes
* text=auto eol=lf
*.png binary
*.jpg binary
*.jpeg binary
*.pdf binary
*.docx binary
```

Create `.python-version`:

```text
3.13.14
```

Create `.node-version`:

```text
24.18.0
```

Create `CODEOWNERS`:

```text
* @zdjc445
```

Create `README.md`:

```markdown
# Time

Time 是面向大学生的学习驱动型日程与知识 Agent。

产品规格、架构和工程治理从 [docs/README.md](docs/README.md) 开始阅读。开发环境、验证命令和贡献流程见 [CONTRIBUTING.md](CONTRIBUTING.md)。
```

Create `CONTRIBUTING.md`:

````markdown
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
````

Create `SECURITY.md`:

```markdown
# Security Policy

Do not open a public issue for a suspected vulnerability. Use the private security-advisory flow of `zdjc445/EL26` and include affected commit, reproducible evidence, impact, and any known containment. Never attach real credentials, verification codes, user documents, or unredacted production logs.
```

Create `.github/pull_request_template.md`:

```markdown
## Spec and plan

- Requirement IDs:
- Approved plan:
- ADR impact:

## Change

- User-visible result:
- Out of scope:
- Migration and rollback:

## Verification evidence

- Failing test before implementation:
- Passing focused tests:
- `python tools/project.py verify`:

## Review checklist

- [ ] Tenant isolation and authorization checked
- [ ] Idempotency, concurrency, retry, deletion, and recovery checked where applicable
- [ ] OpenAPI, migrations, generated files, docs, and lockfiles reviewed
- [ ] No secrets, verification codes, user documents, or unredacted logs
- [ ] Independent reviewer assigned
```

Append these exact entries to `.gitignore` while retaining `.superpowers/`:

```gitignore
.venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.pyc
backend/dist/
frontend/node_modules/
frontend/dist/
frontend/playwright-report/
frontend/test-results/
.env
.env.*
!.env.example
```

- [ ] **Step 6: Validate repository text policy**

Run: `git diff --check`

Expected: exit 0 with no trailing-whitespace or EOF errors.

Run: `python -m unittest tools.tests.test_project -v`

Expected: 2 tests PASS.

- [ ] **Step 7: Commit the governance contract**

```bash
git add .editorconfig .gitattributes .python-version .node-version .gitignore CODEOWNERS README.md CONTRIBUTING.md SECURITY.md .github/pull_request_template.md tools
git commit -m "chore(repo): establish governance and command contract"
```

### Task 2: Backend toolchain and locked package

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/uv.lock`
- Create: `backend/src/time_agent/__init__.py`
- Create: `backend/tests/unit/.gitkeep`
- Create: `backend/tests/integration/.gitkeep`
- Create: `backend/tests/architecture/.gitkeep`
- Modify: `tools/project.py`
- Modify: `tools/tests/test_project.py`

**Interfaces:**
- Consumes: Python 3.13.14 and uv 0.11.29 from Task 1.
- Produces: installable distribution `time-agent-backend`; import package `time_agent`; locked `uv sync --project backend --all-groups --frozen` environment.

- [ ] **Step 1: Prove the backend project is absent**

Run: `uv lock --project backend --check`

Expected: FAIL because `backend/pyproject.toml` does not exist.

- [ ] **Step 2: Create the exact Python project configuration**

Create `backend/pyproject.toml`:

```toml
[project]
name = "time-agent-backend"
version = "0.1.0"
description = "Time learning and scheduling agent API"
requires-python = ">=3.13,<3.14"
dependencies = [
  "fastapi==0.139.2",
  "pydantic==2.13.4",
  "pydantic-settings==2.14.2",
  "uvicorn[standard]==0.51.0",
]

[build-system]
requires = ["hatchling==1.31.0"]
build-backend = "hatchling.build"

[dependency-groups]
dev = [
  "httpx2==2.7.0",
  "mypy==2.3.0",
  "pytest==9.1.1",
  "pytest-asyncio==1.4.0",
  "pytest-cov==7.1.0",
  "licensecheck==2026.0.8",
  "pip-audit==2.10.1",
  "ruff==0.15.22",
]

[tool.hatch.build.targets.wheel]
packages = ["src/time_agent"]

[tool.pytest.ini_options]
addopts = "--strict-config --strict-markers"
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
  "integration: tests that cross an application or protocol boundary",
]

[tool.ruff]
target-version = "py313"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "ASYNC", "S", "RUF"]

[tool.ruff.lint.per-file-ignores]
"backend/tests/**/*.py" = ["S101"]

[tool.mypy]
python_version = "3.13"
strict = true
warn_unreachable = true
mypy_path = "$MYPY_CONFIG_FILE_DIR/src"
```

Create `backend/src/time_agent/__init__.py`:

```python
__version__ = "0.1.0"
```

Create the three `.gitkeep` files as empty files so all test-level directories exist before their first test.

- [ ] **Step 3: Generate and validate the Python lock**

Run: `uv lock --project backend`

Expected: creates `backend/uv.lock` and resolves only versions compatible with Python 3.13.14.

Run: `uv sync --project backend --all-groups --frozen`

Expected: exit 0 and install `time-agent-backend==0.1.0` plus the exact direct dependency versions.

Run: `uv lock --project backend --check`

Expected: exit 0 and report that the lock is current.

- [ ] **Step 4: Validate the package and toolchain**

Run: `uv run --project backend python -c "import time_agent; assert time_agent.__version__ == '0.1.0'"`

Expected: exit 0.

Run: `uv run --project backend ruff check --config backend/pyproject.toml backend tools`

Expected: exit 0.

Run: `uv run --project backend mypy --config-file backend/pyproject.toml backend/src tools`

Expected: exit 0 with no issues.

- [ ] **Step 4A: Resolve the approved Task 1 lint-baseline conflict**

Decision date: 2026-07-18. The user approved this correction after Task 2 first made the
locked Ruff policy executable. The initial required Ruff run is the RED evidence: it
reports eleven `E501` findings and one `S603` finding in the committed Task 1 `tools/`
files.

Modify only formatting in `tools/project.py` and `tools/tests/test_project.py` so every
line satisfies the configured 100-character limit. On the fixed internal command runner,
add a narrowly scoped `# noqa: S603`; `GROUPS` is a source-controlled constant and no
user input reaches `subprocess.run`. Do not change command values, order, `cwd`, or
failure propagation.

Run: `python -m unittest tools.tests.test_project -v`

Expected: 2 tests PASS.

Run: `uv run --project backend ruff format --config backend/pyproject.toml --check backend tools`

Expected: exit 0.

Run: `uv run --project backend ruff check --config backend/pyproject.toml backend tools`

Expected: exit 0.

Commit the approved correction separately:

```bash
git add tools docs/superpowers/plans/2026-07-17-phase-0-engineering-foundation.md
git commit -m "fix(repo): satisfy backend quality policy"
```

- [ ] **Step 5: Commit the locked backend toolchain**

```bash
git add backend
git commit -m "build(backend): establish locked Python toolchain"
```

### Task 3: FastAPI application factory and liveness contract

**Files:**
- Create: `backend/src/time_agent/config.py`
- Create: `backend/src/time_agent/bootstrap/__init__.py`
- Create: `backend/src/time_agent/bootstrap/app.py`
- Create: `backend/src/time_agent/modules/__init__.py`
- Create: `backend/src/time_agent/modules/system/__init__.py`
- Create: `backend/src/time_agent/modules/system/api.py`
- Create: `backend/src/time_agent/modules/system/schemas.py`
- Create: `backend/src/time_agent/main.py`
- Create: `backend/tests/unit/system/__init__.py`
- Create: `backend/tests/unit/system/test_live.py`
- Delete: `backend/tests/unit/.gitkeep`
- Modify: `backend/pyproject.toml`
- Modify: `backend/uv.lock`

**Interfaces:**
- Consumes: `time_agent.__version__` and locked FastAPI/Pydantic dependencies from Task 2.
- Produces: `create_app(settings: Settings | None = None) -> FastAPI`; `GET /api/v1/health/live`; Uvicorn target `time_agent.main:app`.

- [ ] **Step 1: Write the failing liveness test**

Create only the empty `__init__.py` files listed above, then create `backend/tests/unit/system/test_live.py`:

```python
from fastapi.testclient import TestClient
from time_agent.bootstrap.app import create_app
from time_agent.config import Settings


def test_live_returns_versioned_service_identity() -> None:
    app = create_app(Settings(environment="test", build_sha="test-sha"))

    response = TestClient(app).get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "time-api",
        "version": "0.1.0",
        "build_sha": "test-sha",
    }


def test_openapi_uses_the_product_name_and_versioned_path() -> None:
    app = create_app(Settings(environment="test", build_sha="test-sha"))

    schema = app.openapi()

    assert schema["info"]["title"] == "Time API"
    assert schema["info"]["version"] == "0.1.0"
    assert "/api/v1/health/live" in schema["paths"]
```

- [ ] **Step 2: Run the test and verify the intended failure**

Run: `uv run --project backend pytest backend/tests/unit/system/test_live.py -v`

Expected: FAIL because `time_agent.bootstrap.app`, `time_agent.config`, or `create_app` is not implemented.

- [ ] **Step 3: Implement configuration and the public response schema**

Create `backend/src/time_agent/config.py`:

```python
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TIME_", extra="forbid")

    environment: Literal["local", "test", "ci", "staging", "production"] = "local"
    build_sha: str = "development"
```

Create `backend/src/time_agent/modules/system/schemas.py`:

```python
from typing import Literal

from pydantic import BaseModel, ConfigDict


class LiveStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
    service: Literal["time-api"]
    version: str
    build_sha: str
```

- [ ] **Step 4: Implement the system router and composition root**

Create `backend/src/time_agent/modules/system/api.py`:

```python
from fastapi import APIRouter, Request

from time_agent import __version__
from time_agent.modules.system.schemas import LiveStatus

router = APIRouter(prefix="/health", tags=["system"])


@router.get("/live", response_model=LiveStatus, operation_id="getLiveStatus")
def get_live_status(request: Request) -> LiveStatus:
    return LiveStatus(
        status="ok",
        service="time-api",
        version=__version__,
        build_sha=request.app.state.settings.build_sha,
    )
```

Create `backend/src/time_agent/bootstrap/app.py`:

```python
from fastapi import FastAPI

from time_agent import __version__
from time_agent.config import Settings
from time_agent.modules.system.api import router as system_router


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings()
    app = FastAPI(title="Time API", version=__version__)
    app.state.settings = resolved_settings
    app.include_router(system_router, prefix="/api/v1")
    return app
```

Create `backend/src/time_agent/main.py`:

```python
from time_agent.bootstrap.app import create_app

app = create_app()
```

- [ ] **Step 4A: Resolve the approved test-toolchain contract conflict**

Decision date: 2026-07-18. The user approved this correction after Task 3 made the
Task 2 test configuration executable. The RED evidence consists of one `I001`, five
`S101` findings, and a `StarletteDeprecationWarning` that directs the test environment
from `httpx` to `httpx2`.

Change the Task 2 dev dependency from `httpx==0.28.1` to `httpx2==2.7.0`. Change the
Ruff per-file pattern from `"tests/**/*.py"` to the repository-root-relative
`"backend/tests/**/*.py"`, retaining only the `S101` exception. Apply Ruff's safe
`I001` fix to the test import block; do not ignore `I001`.

Run: `uv lock --project backend`

Expected: updates `backend/uv.lock`, removes the direct `httpx` dependency, and locks
`httpx2==2.7.0` as the direct test-client dependency.

Run: `uv sync --project backend --all-groups --frozen`

Expected: exit 0.

Commit the approved dependency and configuration correction separately:

```bash
git add backend/pyproject.toml backend/uv.lock docs/superpowers/plans/2026-07-17-phase-0-engineering-foundation.md
git commit -m "fix(backend): align test toolchain contracts"
```

- [ ] **Step 5: Run focused and static verification**

Run: `uv run --project backend pytest backend/tests/unit/system/test_live.py -v`

Expected: 2 tests PASS with no warnings.

Run: `uv run --project backend ruff format --config backend/pyproject.toml --check backend tools`

Expected: exit 0.

Run: `uv run --project backend ruff check --config backend/pyproject.toml backend tools`

Expected: exit 0.

Run: `uv run --project backend mypy --config-file backend/pyproject.toml backend/src backend/tests tools`

Expected: exit 0 with no issues.

- [ ] **Step 6: Commit the backend liveness slice**

```bash
git add backend/src backend/tests
git commit -m "feat(system): add API liveness contract"
```

### Task 4: Frontend toolchain and locked package

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/pnpm-lock.yaml`
- Create: `frontend/index.html`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.app.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/eslint.config.js`
- Create: `frontend/.prettierignore`
- Create: `frontend/src/test/setup.ts`
- Modify: `docs/superpowers/plans/2026-07-17-phase-0-engineering-foundation.md`

**Interfaces:**
- Consumes: Node.js 24.18.0 and pnpm 11.13.1 from Task 1.
- Produces: locked `frontend` package and exact scripts `dev`, `build`, `typecheck`, `lint`, `format`, `format:check`, `test:unit`, `test:e2e`, and `contract:generate`.

- [ ] **Step 1: Prove the frontend package is absent**

Run: `pnpm --dir frontend install --frozen-lockfile`

Expected: FAIL because `frontend/package.json` and `frontend/pnpm-lock.yaml` do not exist.

- [ ] **Step 2: Create the exact frontend manifest**

Create `frontend/package.json`:

```json
{
  "name": "time-web",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "packageManager": "pnpm@11.13.1",
  "engines": {
    "node": "24.18.0",
    "pnpm": "11.13.1"
  },
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "typecheck": "tsc -b --pretty false",
    "lint": "eslint . --max-warnings 0",
    "format": "prettier --write . --ignore-unknown",
    "format:check": "prettier --check . --ignore-unknown",
    "test:unit": "vitest run",
    "test:e2e": "playwright test",
    "contract:generate": "openapi-typescript ../contracts/openapi.json -o src/shared/api/schema.d.ts"
  },
  "dependencies": {
    "@tanstack/react-query": "5.101.2",
    "react": "19.2.7",
    "react-dom": "19.2.7",
    "react-router": "8.2.0"
  },
  "devDependencies": {
    "@eslint/js": "10.0.1",
    "@playwright/test": "1.61.1",
    "@testing-library/dom": "10.4.1",
    "@testing-library/jest-dom": "6.9.1",
    "@testing-library/react": "16.3.2",
    "@testing-library/user-event": "14.6.1",
    "@types/node": "24.13.3",
    "@types/react": "19.2.17",
    "@types/react-dom": "19.2.3",
    "@vitejs/plugin-react": "6.0.3",
    "eslint": "10.7.0",
    "eslint-plugin-react-hooks": "7.1.1",
    "eslint-plugin-react-refresh": "0.5.3",
    "globals": "17.7.0",
    "jsdom": "29.1.1",
    "license-checker-rseidelsohn": "5.0.1",
    "openapi-typescript": "7.13.0",
    "prettier": "3.9.5",
    "typescript": "5.9.3",
    "typescript-eslint": "8.64.0",
    "vite": "8.1.5",
    "vitest": "4.1.10"
  }
}
```

Create `frontend/index.html`:

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#f7f8fb" />
    <title>Time</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Create `frontend/tsconfig.json`:

```json
{
  "files": [],
  "references": [{ "path": "./tsconfig.app.json" }, { "path": "./tsconfig.node.json" }]
}
```

Create `frontend/tsconfig.app.json`:

```json
{
  "compilerOptions": {
    "target": "ES2023",
    "useDefineForClassFields": true,
    "lib": ["ES2023", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": false,
    "moduleResolution": "Bundler",
    "allowImportingTsExtensions": false,
    "verbatimModuleSyntax": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "tsBuildInfoFile": "./node_modules/.cache/tsconfig.app.tsbuildinfo",
    "jsx": "react-jsx",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noFallthroughCasesInSwitch": true,
    "types": ["vitest/globals", "@testing-library/jest-dom/vitest"]
  },
  "include": ["src"]
}
```

Create `frontend/tsconfig.node.json`:

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": false,
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "noEmit": true,
    "tsBuildInfoFile": "./node_modules/.cache/tsconfig.node.tsbuildinfo",
    "types": ["node"]
  },
  "include": ["vite.config.ts", "playwright.config.ts", "tests/e2e/**/*.ts", "eslint.config.js"]
}
```

Create `frontend/vite.config.ts`:

```typescript
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
  test: {
    dir: "./src",
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    restoreMocks: true,
  },
});
```

Create `frontend/eslint.config.js`:

```javascript
import js from "@eslint/js";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist", "playwright-report", "test-results", "src/shared/api/schema.d.ts"] },
  js.configs.recommended,
  ...tseslint.configs.recommendedTypeChecked,
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      globals: { ...globals.browser, ...globals.node },
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    rules: {
      ...reactHooks.configs.flat.recommended.rules,
      "react-refresh/only-export-components": ["error", { allowConstantExport: true }],
    },
  },
  {
    files: ["**/*.js"],
    extends: [tseslint.configs.disableTypeChecked],
  },
);
```

Create `frontend/.prettierignore`:

```text
dist
node_modules
playwright-report
test-results
src/shared/api/schema.d.ts
```

Create `frontend/src/test/setup.ts`:

```typescript
import "@testing-library/jest-dom/vitest";
```

- [ ] **Step 3: Generate and validate the frontend lock**

Run: `pnpm --dir frontend install --lockfile-only`

Expected: creates `frontend/pnpm-lock.yaml` with package manager `pnpm@11.13.1`.

Run: `pnpm --dir frontend install --frozen-lockfile`

Expected: exit 0 without modifying `frontend/pnpm-lock.yaml`.

- [ ] **Step 3A: Resolve the approved Vitest and ESLint contract conflict**

Decision date: 2026-07-18. The user approved this correction after the first exact
Task 4 validation. The RED evidence is `TS2688` from the Jest-oriented root type entry
and a typed `@typescript-eslint/await-thenable` rule applied to `eslint.config.js`
without parser type information.

Use `@testing-library/jest-dom/vitest` in `tsconfig.app.json`; do not install Jest or
`@types/jest`. Keep `recommendedTypeChecked` and `projectService` for TypeScript and
TSX. Add the official `tseslint.configs.disableTypeChecked` override only for
`**/*.js`; JavaScript remains covered by `js.configs.recommended`.

Commit this approved plan correction separately before the frontend implementation:

```bash
git add docs/superpowers/plans/2026-07-17-phase-0-engineering-foundation.md
git commit -m "docs(plan): correct frontend toolchain contracts"
```

- [ ] **Step 4: Validate the frontend configuration**

Run: `pnpm --dir frontend typecheck`

Expected: exit 0; no application source is present yet.

Run: `pnpm --dir frontend lint`

Expected: exit 0 with zero warnings.

Run: `pnpm --dir frontend format:check`

Expected: exit 0.

- [ ] **Step 4A: Keep TypeScript build metadata out of the source tree**

Decision date: 2026-07-18. The user approved this correction after controller
verification showed that a successful `tsc -b` created untracked
`frontend/tsconfig.app.tsbuildinfo` and `frontend/tsconfig.node.tsbuildinfo` files.

Set `tsBuildInfoFile` in `tsconfig.app.json` to
`./node_modules/.cache/tsconfig.app.tsbuildinfo` and in `tsconfig.node.json` to
`./node_modules/.cache/tsconfig.node.tsbuildinfo`. Remove only the two generated
root-level `.tsbuildinfo` files after verifying their exact paths. Do not add a broad
`.gitignore` exception.

Run `pnpm --dir frontend typecheck` twice. Both runs must exit 0, and
`git status --short --untracked-files=all` must show no generated `.tsbuildinfo` file.

Commit the correction separately:

```bash
git add frontend/tsconfig.app.json frontend/tsconfig.node.json docs/superpowers/plans/2026-07-17-phase-0-engineering-foundation.md
git commit -m "fix(frontend): isolate TypeScript build metadata"
```

- [ ] **Step 5: Commit the locked frontend toolchain**

```bash
git add frontend
git commit -m "build(frontend): establish locked TypeScript toolchain"
```

### Task 5: Production-shaped frontend status slice

**Files:**
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/app/App.tsx`
- Create: `frontend/src/app/AppProviders.tsx`
- Create: `frontend/src/features/system/api.ts`
- Create: `frontend/src/features/system/SystemStatusPage.tsx`
- Create: `frontend/src/features/system/SystemStatusPage.test.tsx`
- Create: `frontend/src/styles/index.css`
- Create: `frontend/playwright.config.ts`
- Create: `frontend/tests/e2e/system-status.spec.ts`
- Modify: `frontend/src/test/setup.ts`
- Modify: `frontend/vite.config.ts`
- Modify: `docs/superpowers/plans/2026-07-17-phase-0-engineering-foundation.md`

**Interfaces:**
- Consumes: `GET /api/v1/health/live` from Task 3 and the Vite proxy from Task 4.
- Produces: `getLiveStatus(signal?: AbortSignal) -> Promise<LiveStatus>`; route `/`; accessible operational status page; full backend-to-browser E2E.

- [ ] **Step 1: Write the failing component and browser tests**

Create `frontend/src/features/system/SystemStatusPage.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "../../app/App";
import { AppProviders } from "../../app/AppProviders";

const livePayload = {
  status: "ok",
  service: "time-api",
  version: "0.1.0",
  build_sha: "test-sha",
};

describe("SystemStatusPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows the product identity and confirmed API status", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify(livePayload), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    render(
      <AppProviders>
        <App />
      </AppProviders>,
    );

    expect(screen.getByRole("heading", { name: "Time" })).toBeInTheDocument();
    expect(await screen.findByText("服务正常")).toBeInTheDocument();
    expect(screen.getByText("API 0.1.0")).toBeInTheDocument();
    const fetchMock = vi.mocked(fetch);
    expect(fetchMock).toHaveBeenCalledOnce();
    const firstCall = fetchMock.mock.calls[0];
    expect(firstCall?.[0]).toBe("/api/v1/health/live");
    expect(firstCall?.[1]?.signal).toBeInstanceOf(AbortSignal);
  });

  it("does not claim health when the API request fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(null, { status: 503 })));

    render(
      <AppProviders>
        <App />
      </AppProviders>,
    );

    expect(await screen.findByRole("alert")).toHaveTextContent("无法确认服务状态");
    expect(screen.queryByText("服务正常")).not.toBeInTheDocument();
  });
});
```

Create `frontend/playwright.config.ts`:

```typescript
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: "http://127.0.0.1:5173",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command:
        "uv run --project ../backend uvicorn time_agent.main:app --host 127.0.0.1 --port 8000",
      url: "http://127.0.0.1:8000/api/v1/health/live",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
    {
      command: "pnpm dev",
      url: "http://127.0.0.1:5173",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
  ],
});
```

Create `frontend/tests/e2e/system-status.spec.ts`:

```typescript
import { expect, test } from "@playwright/test";

test("renders Time and confirms the real API liveness endpoint", async ({ page }) => {
  const liveResponse = page.waitForResponse(
    (response) => response.url().endsWith("/api/v1/health/live") && response.status() === 200,
  );

  await page.goto("/");

  await liveResponse;
  await expect(page.getByRole("heading", { name: "Time" })).toBeVisible();
  await expect(page.getByText("服务正常")).toBeVisible();
  await expect(page.getByText("API 0.1.0")).toBeVisible();
});
```

- [ ] **Step 2: Run the unit test and verify the intended failure**

Run: `pnpm --dir frontend test:unit`

Expected: FAIL because `App` and `AppProviders` do not exist.

- [ ] **Step 2A: Resolve the approved unit-test discovery conflict**

Decision date: 2026-07-18. The user approved this correction after the initial RED run
showed Vitest 4 collecting `frontend/tests/e2e/system-status.spec.ts` in addition to the
intended component test. Configure `test.dir` as `"./src"` in `vite.config.ts`. Do not
maintain an E2E exclude list; Vitest retains its default `*.test.*` and `*.spec.*`
patterns inside `src`, while Playwright owns `tests/e2e`.

Run: `pnpm --dir frontend test:unit`

Expected: FAIL only because `App` and `AppProviders` do not exist; the output must not
contain a Playwright runner error.

Commit the discovery correction separately:

```bash
git add frontend/vite.config.ts docs/superpowers/plans/2026-07-17-phase-0-engineering-foundation.md
git commit -m "fix(frontend): isolate unit test discovery"
```

- [ ] **Step 2B: Register the approved centralized React test cleanup**

Decision date: 2026-07-18. The user approved this correction after the first GREEN
suite run showed that the first component render remained in the DOM for the second
test. The second test passed when run alone. Because this project imports Vitest APIs
explicitly and does not enable `test.globals`, register React Testing Library cleanup
in the existing setup file instead of enabling globals or adding per-test cleanup.

Update `frontend/src/test/setup.ts`:

```typescript
import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(() => {
  cleanup();
});
```

Run: `pnpm --dir frontend test:unit`

Expected: both component tests PASS with no retained DOM from the preceding test.

Commit the cleanup correction separately:

```bash
git add frontend/src/test/setup.ts docs/superpowers/plans/2026-07-17-phase-0-engineering-foundation.md
git commit -m "fix(frontend): enforce component test cleanup"
```

- [ ] **Step 2C: Use the approved type-safe fetch assertion**

Decision date: 2026-07-18. The user approved this correction after the GREEN unit
suite and typecheck passed but the locked `@typescript-eslint/no-unsafe-assignment`
rule rejected Vitest's `expect.any(AbortSignal)` return type. Keep the rule enabled
with no inline or configuration exemption. Assert the typed mock call count, URL, and
`AbortSignal` instance separately, as shown in the Step 1 test. The controller
validated the candidate test through the current ESLint configuration with zero
errors and zero warnings before approval.

Commit this plan correction separately; keep the corrected test in the Task 5 feature
commit because the test file is part of the new status slice:

```bash
git add docs/superpowers/plans/2026-07-17-phase-0-engineering-foundation.md
git commit -m "docs(plan): approve type-safe fetch assertion"
```

- [ ] **Step 3: Implement the typed API boundary**

Create `frontend/src/features/system/api.ts`:

```typescript
export interface LiveStatus {
  status: "ok";
  service: "time-api";
  version: string;
  build_sha: string;
}

function isLiveStatus(value: unknown): value is LiveStatus {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const candidate = value as Record<string, unknown>;
  return (
    candidate.status === "ok" &&
    candidate.service === "time-api" &&
    typeof candidate.version === "string" &&
    typeof candidate.build_sha === "string"
  );
}

export async function getLiveStatus(signal?: AbortSignal): Promise<LiveStatus> {
  const requestInit: RequestInit = signal === undefined ? {} : { signal };
  const response = await fetch("/api/v1/health/live", requestInit);
  if (!response.ok) {
    throw new Error(`Live status request failed with HTTP ${response.status}`);
  }
  const payload: unknown = await response.json();
  if (!isLiveStatus(payload)) {
    throw new Error("Live status response did not match the public contract");
  }
  return payload;
}
```

- [ ] **Step 4: Implement providers, routing, page, and bootstrap**

Create `frontend/src/app/AppProviders.tsx`:

```tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { type PropsWithChildren, useState } from "react";
import { BrowserRouter } from "react-router";

export function AppProviders({ children }: PropsWithChildren) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { retry: false, staleTime: 30_000 },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  );
}
```

Create `frontend/src/app/App.tsx`:

```tsx
import { Route, Routes } from "react-router";

import { SystemStatusPage } from "../features/system/SystemStatusPage";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<SystemStatusPage />} />
    </Routes>
  );
}
```

Create `frontend/src/features/system/SystemStatusPage.tsx`:

```tsx
import { useQuery } from "@tanstack/react-query";

import { getLiveStatus } from "./api";

export function SystemStatusPage() {
  const status = useQuery({
    queryKey: ["system", "live"],
    queryFn: ({ signal }) => getLiveStatus(signal),
  });

  return (
    <main className="status-shell">
      <section className="status-card" aria-labelledby="product-name">
        <p className="eyebrow">学习与行动 Agent</p>
        <h1 id="product-name">Time</h1>
        <p className="summary">工程基础运行状态</p>
        {status.isPending && <p role="status">正在确认服务状态…</p>}
        {status.isError && <p role="alert">无法确认服务状态</p>}
        {status.data && (
          <div className="health" role="status">
            <span className="health-dot" aria-hidden="true" />
            <span>服务正常</span>
            <span className="version">API {status.data.version}</span>
          </div>
        )}
      </section>
    </main>
  );
}
```

Create `frontend/src/main.tsx`:

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./app/App";
import { AppProviders } from "./app/AppProviders";
import "./styles/index.css";

const root = document.getElementById("root");
if (root === null) {
  throw new Error("Missing #root application mount point");
}

createRoot(root).render(
  <StrictMode>
    <AppProviders>
      <App />
    </AppProviders>
  </StrictMode>,
);
```

Create `frontend/src/styles/index.css`:

```css
:root {
  color: #1b2430;
  background: #f7f8fb;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

* {
  box-sizing: border-box;
}

body {
  min-width: 320px;
  min-height: 100vh;
  margin: 0;
}

.status-shell {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 24px;
}

.status-card {
  width: min(100%, 520px);
  padding: 40px;
  border: 1px solid #dde3ec;
  border-radius: 20px;
  background: #ffffff;
  box-shadow: 0 18px 50px rgb(25 36 52 / 8%);
}

.eyebrow,
.summary {
  color: #5c6878;
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: clamp(48px, 10vw, 72px);
  line-height: 1;
}

.summary {
  margin: 14px 0 32px;
}

.health {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid #edf0f4;
}

.health-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #16875b;
}

.version {
  margin-left: auto;
  color: #5c6878;
  font-variant-numeric: tabular-nums;
}
```

- [ ] **Step 5: Run focused frontend verification**

Run: `pnpm --dir frontend test:unit`

Expected: 2 tests PASS.

Run: `pnpm --dir frontend typecheck`

Expected: exit 0.

Run: `pnpm --dir frontend lint`

Expected: exit 0 with zero warnings.

Run: `pnpm --dir frontend format:check`

Expected: exit 0.

- [ ] **Step 6: Run the real browser slice**

Run: `pnpm --dir frontend exec playwright install chromium`

Expected: Chromium is installed for Playwright 1.61.1.

Run: `pnpm --dir frontend test:e2e`

Expected: 1 Chromium test PASS after Playwright starts the real FastAPI and Vite processes.

- [ ] **Step 7: Commit the frontend status slice**

```bash
git add frontend
git commit -m "feat(system): add frontend service status slice"
```

### Task 6: Deterministic OpenAPI and generated TypeScript contract

**Files:**
- Create: `backend/scripts/export_openapi.py`
- Create: `backend/tests/integration/system/__init__.py`
- Create: `backend/tests/integration/system/test_openapi.py`
- Create: `contracts/openapi.json` (generated)
- Create: `frontend/src/shared/api/schema.d.ts` (generated)
- Create: `tools/check_contract.py`
- Modify: `backend/pyproject.toml`
- Modify: `frontend/src/features/system/api.ts`
- Modify: `tools/project.py`
- Modify: `tools/tests/test_project.py`
- Modify: `docs/superpowers/plans/2026-07-17-phase-0-engineering-foundation.md`
- Delete: `backend/tests/integration/.gitkeep`

**Interfaces:**
- Consumes: `create_app()` and `LiveStatus` from Task 3; `openapi-typescript` from Task 4.
- Produces: deterministic `contracts/openapi.json`; generated `components["schemas"]["LiveStatus"]`; drift check `python tools/check_contract.py`.

- [ ] **Step 1: Write the failing OpenAPI integration test**

Create empty `backend/tests/integration/system/__init__.py`, then create `backend/tests/integration/system/test_openapi.py`:

```python
import pytest
from fastapi.testclient import TestClient

from time_agent.bootstrap.app import create_app
from time_agent.config import Settings


@pytest.mark.integration
def test_live_operation_is_present_in_the_served_openapi_contract() -> None:
    app = create_app(Settings(environment="test", build_sha="contract-test"))

    response = TestClient(app).get("/openapi.json")

    assert response.status_code == 200
    operation = response.json()["paths"]["/api/v1/health/live"]["get"]
    assert operation["operationId"] == "getLiveStatus"
    assert operation["responses"]["200"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/LiveStatus"
    }
```

- [ ] **Step 2: Prove committed contracts do not exist**

Run: `uv run --project backend pytest backend/tests/integration/system/test_openapi.py -v`

Expected: 1 test PASS; this proves the served schema before snapshotting it.

Run: `python tools/check_contract.py`

Expected: FAIL because `tools/check_contract.py`, `contracts/openapi.json`, and the generated TypeScript schema do not exist.

- [ ] **Step 3: Implement deterministic OpenAPI export**

Create `backend/scripts/export_openapi.py`:

```python
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
```

- [ ] **Step 4: Implement the cross-language drift check**

Create `tools/check_contract.py`:

```python
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
```

- [ ] **Step 4A: Resolve the approved cross-platform subprocess contract**

Decision date: 2026-07-18. The user authorized continuing with the proposed
cross-platform correction after the exact `contract-generate` command created the
OpenAPI JSON and then failed before TypeScript generation. On Windows,
`shutil.which("pnpm")` resolved `D:\\nvm\\nodejs\\pnpm.CMD`; a direct Python
subprocess using `pnpm` raised `FileNotFoundError`, while the same subprocess using
`pnpm.cmd` returned the locked version `11.13.1`.

First update `tools/tests/test_project.py` to import `PNPM_EXECUTABLE` from
`tools.project` and use it for every expected pnpm command. Run the focused test before
production changes and record the expected import failure because the constant does
not exist yet.

Then update `tools/project.py`: import `os`, define
`PNPM_EXECUTABLE = "pnpm.cmd" if os.name == "nt" else "pnpm"`, and use the constant
as the executable token for every pnpm command in `GROUPS`. Keep `shell=False` through
the existing list-form `subprocess.run`; do not modify PATH.

Use the same platform selection in the new `tools/check_contract.py`, as shown in Step
4. Store each static subprocess command in a local list and retain the precise
`# noqa: S603` at the invocation; do not relax Ruff configuration. Apply Ruff's import
ordering to the new integration test without semantic changes.

Run: `uv run --project backend pytest tools/tests/test_project.py -q`

Expected: 2 tests PASS on Windows with `pnpm.cmd`; the same test expects `pnpm` on
Linux CI.

Commit the existing runner correction separately from the generated contract feature:

```bash
git add tools/project.py tools/tests/test_project.py docs/superpowers/plans/2026-07-17-phase-0-engineering-foundation.md
git commit -m "fix(repo): resolve pnpm subprocess on Windows"
```

- [ ] **Step 5: Generate both committed contracts**

Run: `python tools/project.py contract-generate`

Expected: creates `contracts/openapi.json` and `frontend/src/shared/api/schema.d.ts`.

Modify the first lines of `frontend/src/features/system/api.ts` so its public type comes from the generated contract, retaining the existing runtime guard and `getLiveStatus` implementation:

```typescript
import type { components } from "../../shared/api/schema";

export type LiveStatus = components["schemas"]["LiveStatus"];
```

Delete the handwritten `export interface LiveStatus` block only.

- [ ] **Step 6: Validate contract stability and all consumers**

Run: `python tools/check_contract.py`

Expected: exit 0 with no drift message.

Run: `uv run --project backend pytest backend/tests/integration/system/test_openapi.py -v`

Expected: 1 test PASS.

Run: `pnpm --dir frontend test:unit`

Expected: 2 tests PASS.

Run: `pnpm --dir frontend typecheck`

Expected: exit 0.

- [ ] **Step 6A: Disambiguate test namespace modules for mypy**

Decision date: 2026-07-18. The strict full-tree mypy command failed after the required
`backend/tests/integration/system/__init__.py` was added because both it and
`backend/tests/unit/system/__init__.py` were discovered as the top-level module
`system`. The existing `unit` and `integration` directories are test partitions, not
published Python packages.

Set `explicit_package_bases = true` in `[tool.mypy]` in `backend/pyproject.toml`. Do
not remove either required `system/__init__.py`, add ignore/exclude rules, or add
package markers solely to influence mypy. The current mypy executable documents this
option as using the current directory and `MYPYPATH` to determine module names. The
controller verified the same 18 source files with `--explicit-package-bases` before
this plan change and observed zero issues.

Run:
`uv run --project backend mypy --config-file backend/pyproject.toml backend/src backend/tests tools`

Expected: exit 0 with `Success: no issues found in 18 source files`.

Commit the mypy discovery correction separately:

```bash
git add backend/pyproject.toml docs/superpowers/plans/2026-07-17-phase-0-engineering-foundation.md
git commit -m "fix(backend): disambiguate mypy namespace modules"
```

- [ ] **Step 6B: Isolate pytest module imports across test partitions**

Decision date: 2026-07-18. After the Task 6 feature commit, the combined command
`uv run --project backend pytest backend/tests tools/tests -q` failed during collection
because pytest's default `prepend` import mode placed both test packages named `system`
in the same import namespace. The current pytest executable documents `prepend` as the
default. The controller reran the identical five-test collection with
`--import-mode=importlib` and all five tests passed.

Append `--import-mode=importlib` to `[tool.pytest.ini_options].addopts` in
`backend/pyproject.toml`. Do not split the complete suite to hide the collision, mutate
`sys.path`, remove required package files, or add test package markers solely for the
runner.

Run: `uv run --project backend pytest backend/tests tools/tests -q`

Expected: 5 tests PASS in one collection.

Commit the pytest import correction separately:

```bash
git add backend/pyproject.toml docs/superpowers/plans/2026-07-17-phase-0-engineering-foundation.md
git commit -m "fix(test): isolate pytest module imports"
```

- [ ] **Step 7: Commit the generated contract boundary**

```bash
git add backend/scripts backend/tests/integration contracts frontend/src/features/system/api.ts frontend/src/shared/api/schema.d.ts tools/check_contract.py
git commit -m "build(api): enforce generated OpenAPI contract"
```

### Task 7: Executable modular-boundary rule

**Files:**
- Modify: `backend/pyproject.toml`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/architecture/__init__.py`
- Create: `backend/tests/architecture/rules.py`
- Create: `backend/tests/architecture/test_module_boundaries.py`
- Delete: `backend/tests/architecture/.gitkeep`

**Interfaces:**
- Consumes: module root `backend/src/time_agent/modules` from Task 3 and ADR-0001/ADR-0002.
- Produces: `find_forbidden_imports(source: str) -> frozenset[str]`; `find_cross_module_imports(source: str, current_module: str) -> frozenset[str]`; repository check that every future `modules/*/domain/**/*.py` remains independent from frameworks and other modules' internals.

- [ ] **Step 1: Write tests for the rule engine and repository scan**

Create empty `backend/tests/__init__.py` and `backend/tests/architecture/__init__.py`, then create `backend/tests/architecture/test_module_boundaries.py`:

```python
from pathlib import Path

from tests.architecture.rules import find_cross_module_imports, find_forbidden_imports

MODULES = Path(__file__).resolve().parents[2] / "src" / "time_agent" / "modules"


def test_rule_detects_framework_imports() -> None:
    source = "from fastapi import APIRouter\nimport sqlalchemy.orm\n"

    assert find_forbidden_imports(source) == frozenset({"fastapi", "sqlalchemy"})


def test_rule_allows_standard_library_and_own_domain_imports() -> None:
    source = (
        "from dataclasses import dataclass\n"
        "from time_agent.modules.calendar.domain import Event\n"
    )

    assert find_forbidden_imports(source) == frozenset()
    assert find_cross_module_imports(source, current_module="calendar") == frozenset()


def test_rule_detects_cross_module_internal_imports() -> None:
    source = "from time_agent.modules.knowledge.domain import Document\n"

    assert find_cross_module_imports(source, current_module="calendar") == frozenset({"knowledge"})


def test_repository_domain_files_respect_module_boundaries() -> None:
    violations: dict[str, dict[str, frozenset[str]]] = {}
    for module_path in (path for path in MODULES.iterdir() if path.is_dir()):
        for path in (module_path / "domain").glob("**/*.py"):
            source = path.read_text(encoding="utf-8")
            frameworks = find_forbidden_imports(source)
            cross_module = find_cross_module_imports(source, current_module=module_path.name)
            if frameworks or cross_module:
                violations[str(path.relative_to(MODULES))] = {
                    "frameworks": frameworks,
                    "cross_module": cross_module,
                }

    assert violations == {}
```

- [ ] **Step 2: Run the tests and verify the intended failure**

Run: `uv run --project backend pytest backend/tests/architecture/test_module_boundaries.py -v`

Expected: FAIL because `tests.architecture.rules` does not exist.

- [ ] **Step 3: Implement the AST-based rule**

Create `backend/tests/architecture/rules.py`:

```python
from __future__ import annotations

import ast

FORBIDDEN_ROOTS = frozenset({"fastapi", "sqlalchemy", "langchain", "langgraph"})


def _imported_modules(source: str) -> frozenset[str]:
    modules: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module)
    return frozenset(modules)


def find_forbidden_imports(source: str) -> frozenset[str]:
    roots = {module.partition(".")[0] for module in _imported_modules(source)}
    return frozenset(roots & FORBIDDEN_ROOTS)


def find_cross_module_imports(source: str, current_module: str) -> frozenset[str]:
    imported_modules: set[str] = set()
    for module in _imported_modules(source):
        parts = module.split(".")
        if len(parts) >= 3 and parts[:2] == ["time_agent", "modules"]:
            imported_module = parts[2]
            if imported_module != current_module:
                imported_modules.add(imported_module)
    return frozenset(imported_modules)
```

- [ ] **Step 3A: Apply the required Ruff-safe source layout**

Decision date: 2026-07-18. The first correction misidentified the failing line. The
exact Ruff location is the 104-character `source` assignment in the standard-library
and own-domain test, not its assertion. Keep the locked 100-character policy unchanged,
split the same source value into two implicitly concatenated string literals as shown
in Step 1, and restore the already-compliant assertion to one line. The resulting test
input is byte-for-byte identical.

Commit the plan correction separately; keep the corrected test in the Task 7 feature
commit because it is a new file:

```bash
git add docs/superpowers/plans/2026-07-17-phase-0-engineering-foundation.md
git commit -m "docs(plan): correct architecture test source layout"
```

- [ ] **Step 4: Run architecture and static verification**

Run: `uv run --project backend pytest backend/tests/architecture/test_module_boundaries.py -v`

Expected: 4 tests PASS.

Run: `uv run --project backend ruff check --config backend/pyproject.toml backend/tests/architecture`

Expected: exit 0.

Run: `uv run --project backend mypy --config-file backend/pyproject.toml backend/tests/architecture`

Expected: exit 0 with no issues.

- [ ] **Step 4A: Add the test package root to mypy's explicit search path**

Decision date: 2026-07-18. Focused pytest passed 4 tests and Ruff passed, but the exact
focused mypy command could not resolve `tests.architecture.rules`. The existing
`mypy_path` contains only `backend/src`; with explicit package bases enabled, the
`tests` package also requires `backend` as a declared search root. The controller
verified this root through `MYPYPATH` and the same command passed all 3 source files.

Change `[tool.mypy].mypy_path` in `backend/pyproject.toml` to the cross-platform,
comma-separated value
`"$MYPY_CONFIG_FILE_DIR/src,$MYPY_CONFIG_FILE_DIR"`. Mypy documents comma as a
platform-independent separator for this option. Do not change the tested import or add
an ignore rule.

Run: `uv run --project backend mypy --config-file backend/pyproject.toml backend/tests/architecture`

Expected: exit 0 with `Success: no issues found in 3 source files`.

Commit the search-root correction separately:

```bash
git add backend/pyproject.toml docs/superpowers/plans/2026-07-17-phase-0-engineering-foundation.md
git commit -m "fix(backend): expose test package to mypy"
```

- [ ] **Step 5: Commit the architecture gate**

```bash
git add backend/tests
git commit -m "test(architecture): enforce domain framework boundary"
```

### Task 8: Reproducible backend and frontend containers

**Files:**
- Create: `.dockerignore`
- Create: `docker/backend.Dockerfile`
- Create: `docker/frontend.Dockerfile`
- Create: `docker/nginx.conf`

**Interfaces:**
- Consumes: backend lock and Uvicorn target from Tasks 2–3; frontend lock and build from Tasks 4–5.
- Produces: image `time-api:p0` listening on `8000`; image `time-web:p0` listening on `8080`; container probe `/healthz`.

- [ ] **Step 1: Prove container definitions are absent**

Run: `docker build --file docker/backend.Dockerfile --tag time-api:p0 .`

Expected: FAIL because `docker/backend.Dockerfile` does not exist.

Run: `docker build --file docker/frontend.Dockerfile --tag time-web:p0 .`

Expected: FAIL because `docker/frontend.Dockerfile` does not exist.

- [ ] **Step 2: Add a minimal build context policy**

Create `.dockerignore`:

```dockerignore
.git
.github
.superpowers
.venv
**/__pycache__
**/.pytest_cache
**/.mypy_cache
**/.ruff_cache
backend/dist
frontend/node_modules
frontend/dist
frontend/playwright-report
frontend/test-results
docs
```

- [ ] **Step 3: Implement the backend image**

Create `docker/backend.Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1.7
FROM python:3.13.14-slim-bookworm@sha256:9d7f287598e1a5a978c015ee176d8216435aaf335ed69ac3c38dd1bbb10e8d64 AS builder

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy
WORKDIR /workspace
RUN python -m pip install --no-cache-dir uv==0.11.29
COPY backend/pyproject.toml backend/uv.lock ./backend/
RUN uv sync --project backend --frozen --no-dev --no-install-project
COPY backend/src ./backend/src
RUN uv sync --project backend --frozen --no-dev

FROM python:3.13.14-slim-bookworm@sha256:9d7f287598e1a5a978c015ee176d8216435aaf335ed69ac3c38dd1bbb10e8d64 AS runtime
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TIME_ENVIRONMENT=production
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "time_agent.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
```

The digest is the multi-platform manifest for the official `python:3.13.14-slim-bookworm` image read on 2026-07-17. If execution occurs after that date, the implementer must verify the digest still resolves before building; changing it is a dependency update with its own diff and scan evidence.

- [ ] **Step 4: Implement the frontend image and non-root Nginx configuration**

Create `docker/frontend.Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1.7
FROM node:24.18.0-bookworm-slim@sha256:6f7b03f7c2c8e2e784dcf9295400527b9b1270fd37b7e9a7285cf83b6951452d AS builder
WORKDIR /workspace/frontend
RUN npm install --global pnpm@11.13.1
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm build

FROM nginx:1.28.0-alpine@sha256:30f1c0d78e0ad60901648be663a710bdadf19e4c10ac6782c235200619158284 AS runtime
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /workspace/frontend/dist /usr/share/nginx/html
USER nginx
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
```

Create `docker/nginx.conf`:

```nginx
pid /tmp/nginx.pid;

events {}

http {
    access_log /dev/stdout;
    error_log /dev/stderr warn;
    client_body_temp_path /tmp/client_temp;
    proxy_temp_path /tmp/proxy_temp;
    fastcgi_temp_path /tmp/fastcgi_temp;
    uwsgi_temp_path /tmp/uwsgi_temp;
    scgi_temp_path /tmp/scgi_temp;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 8080;
        server_name _;
        root /usr/share/nginx/html;
        index index.html;

        location = /healthz {
            access_log off;
            add_header Content-Type text/plain;
            return 200 "ok\n";
        }

        location / {
            try_files $uri $uri/ /index.html;
        }
    }
}
```

- [ ] **Step 5: Build both images**

Run: `docker build --file docker/backend.Dockerfile --tag time-api:p0 .`

Expected: exit 0 and create image `time-api:p0`.

Run: `docker build --file docker/frontend.Dockerfile --tag time-web:p0 .`

Expected: exit 0 and create image `time-web:p0`.

- [ ] **Step 6: Smoke-test exact containers**

Run: `docker run --detach --rm --name time-api-p0-smoke --publish 18000:8000 --env TIME_BUILD_SHA=container-smoke time-api:p0`

Run: `python -c "import json, urllib.request; data=json.load(urllib.request.urlopen('http://127.0.0.1:18000/api/v1/health/live')); assert data['build_sha']=='container-smoke'"`

Expected: Python exits 0.

Run: `docker rm --force time-api-p0-smoke`

Run: `docker run --detach --rm --name time-web-p0-smoke --publish 18080:8080 time-web:p0`

Run: `python -c "import urllib.request; assert urllib.request.urlopen('http://127.0.0.1:18080/healthz').read()==b'ok\n'"`

Expected: Python exits 0.

Run: `docker rm --force time-web-p0-smoke`

- [ ] **Step 7: Commit the image definitions**

```bash
git add .dockerignore docker
git commit -m "build(container): add reproducible application images"
```

### Task 9: GitHub Actions quality gates and phase exit

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/branch-protection.json`
- Create: `docs/engineering/ci-checks.md`
- Create: `docs/engineering/dependency-policy.md`
- Modify: `docs/README.md`

**Interfaces:**
- Consumes: every repository command and image definition from Tasks 1–8.
- Produces: GitHub workflow `CI`; required job names `quality`, `security`, `containers (time-api)`, and `containers (time-web)`; exact branch-protection contract documented for `zdjc445/EL26`.

- [ ] **Step 1: Prove the full local gate before adding CI**

Run: `python tools/project.py verify`

Expected: exit 0; backend and frontend format, lint, type, unit, integration, contract, build, and Chromium E2E all pass.

Run: `git diff --check`

Expected: exit 0.

- [ ] **Step 2: Add the pinned GitHub Actions workflow**

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  quality:
    name: quality
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - name: Checkout
        uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0
      - name: Install uv
        uses: astral-sh/setup-uv@11f9893b081a58869d3b5fccaea48c9e9e46f990 # v8.3.2
        with:
          version: 0.11.29
          enable-cache: true
      - name: Install pnpm
        uses: pnpm/action-setup@0ebf47130e4866e96fce0953f49152a61190b271 # v6.0.9
        with:
          version: 11.13.1
          run_install: false
      - name: Install Node.js
        uses: actions/setup-node@820762786026740c76f36085b0efc47a31fe5020 # v7.0.0
        with:
          node-version: 24.18.0
          cache: pnpm
          cache-dependency-path: frontend/pnpm-lock.yaml
      - name: Sync backend
        run: uv sync --project backend --all-groups --frozen
      - name: Sync frontend
        run: pnpm --dir frontend install --frozen-lockfile
      - name: Install Chromium
        run: pnpm --dir frontend exec playwright install --with-deps chromium
      - name: Verify repository
        run: python tools/project.py verify

  security:
    name: security
    runs-on: ubuntu-latest
    timeout-minutes: 30
    permissions:
      actions: read
      contents: read
      pull-requests: write
    steps:
      - name: Checkout full history
        uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0
        with:
          fetch-depth: 0
      - name: Scan committed history for secrets
        uses: gitleaks/gitleaks-action@e0c47f4f8be36e29cdc102c57e68cb5cbf0e8d1e # v3.0.0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Install uv
        uses: astral-sh/setup-uv@11f9893b081a58869d3b5fccaea48c9e9e46f990 # v8.3.2
        with:
          version: 0.11.29
          enable-cache: true
      - name: Install pnpm
        uses: pnpm/action-setup@0ebf47130e4866e96fce0953f49152a61190b271 # v6.0.9
        with:
          version: 11.13.1
          run_install: false
      - name: Install Node.js
        uses: actions/setup-node@820762786026740c76f36085b0efc47a31fe5020 # v7.0.0
        with:
          node-version: 24.18.0
          cache: pnpm
          cache-dependency-path: frontend/pnpm-lock.yaml
      - name: Sync locked dependencies
        run: |
          uv sync --project backend --all-groups --frozen
          pnpm --dir frontend install --frozen-lockfile
      - name: Audit vulnerabilities and licenses
        run: python tools/project.py security
      - name: Scan repository filesystem
        uses: aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25 # v0.36.0
        with:
          scan-type: fs
          scan-ref: .
          scanners: vuln,secret,misconfig
          format: table
          exit-code: "1"
          severity: HIGH,CRITICAL
      - name: Generate source SBOM
        uses: anchore/sbom-action@e22c389904149dbc22b58101806040fa8d37a610 # v0.24.0
        with:
          path: .
          format: spdx-json
          artifact-name: time-source-${{ github.sha }}.spdx.json
          upload-release-assets: false

  containers:
    name: containers (${{ matrix.image }})
    runs-on: ubuntu-latest
    timeout-minutes: 30
    strategy:
      fail-fast: false
      matrix:
        include:
          - image: time-api
            dockerfile: docker/backend.Dockerfile
          - image: time-web
            dockerfile: docker/frontend.Dockerfile
    steps:
      - name: Checkout
        uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0
      - name: Set up Buildx
        uses: docker/setup-buildx-action@bb05f3f5519dd87d3ba754cc423b652a5edd6d2c # v4.2.0
      - name: Build ${{ matrix.image }}
        uses: docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a # v7.3.0
        with:
          context: .
          file: ${{ matrix.dockerfile }}
          push: false
          load: true
          tags: ${{ matrix.image }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - name: Scan ${{ matrix.image }}
        uses: aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25 # v0.36.0
        with:
          image-ref: ${{ matrix.image }}:${{ github.sha }}
          format: table
          exit-code: "1"
          vuln-type: os,library
          severity: HIGH,CRITICAL
      - name: Generate ${{ matrix.image }} SBOM
        uses: anchore/sbom-action@e22c389904149dbc22b58101806040fa8d37a610 # v0.24.0
        with:
          image: ${{ matrix.image }}:${{ github.sha }}
          format: spdx-json
          artifact-name: ${{ matrix.image }}-${{ github.sha }}.spdx.json
          upload-release-assets: false
```

- [ ] **Step 3: Document the exact CI and protection contract**

Create `.github/branch-protection.json`:

```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "quality",
      "security",
      "containers (time-api)",
      "containers (time-web)"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1,
    "require_last_push_approval": true
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": true
}
```

Create `docs/engineering/ci-checks.md`:

````markdown
# GitHub CI Checks

状态：已批准

仓库：`zdjc445/EL26`

Workflow：`CI`

合并到 `main` 的必需检查名：

- `quality`
- `security`
- `containers (time-api)`
- `containers (time-web)`

工作流文件固定第三方 Action 到不可变 commit。更新 Action 时必须读取官方 release、替换 commit、检查 Diff，并重新运行工作流。

分支保护属于 GitHub 外部状态。首次工作流在远端成功运行后，Release Owner 使用具有 Administration(write) 权限的 GitHub CLI 身份执行：

```bash
gh api --method PUT -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2026-03-10" repos/zdjc445/EL26/branches/main/protection --input .github/branch-protection.json
gh api -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2026-03-10" repos/zdjc445/EL26/branches/main/protection
```

第二条命令必须返回四个 required contexts、一个批准、stale review dismissal、last-push approval、linear history、conversation resolution，并显示 force push 和 deletion 均关闭。保存输出到对应工作项；不得只凭 UI 操作口头宣称生效。
````

Create `docs/engineering/dependency-policy.md`:

```markdown
# Dependency Acceptance Policy

状态：已批准

本策略约束 Time 构建和运行依赖，不向仓库源代码授予开源许可证。

Python 依赖必须由 `licensecheck==2026.0.8` 识别为 MIT、Apache、BSD、ISC、MPL、Python、Unlicense、0BSD 或 CC0 类许可证。Node.js 依赖必须由 `license-checker-rseidelsohn==5.0.1` 识别为 `MIT`、`Apache-2.0`、`BSD-2-Clause`、`BSD-3-Clause`、`ISC`、`0BSD`、`Python-2.0`、`PSF-2.0`、`MPL-2.0`、`Unlicense`、`CC0-1.0` 或 `CC-BY-4.0`。

未知许可证、猜测许可证、GPL、AGPL、LGPL、SSPL、Commons Clause 或自定义限制性条款默认阻断合并。接受例外前必须保存许可证原文、法律或授权判断、影响范围、Owner 和重新评估条件；需要长期保留的架构性例外通过 ADR 审批。

漏洞扫描不允许用自动重试或忽略所有未修复问题变绿。单个漏洞例外必须引用精确漏洞 ID、受影响版本、可利用性证据、补偿控制、Owner 和到期日。
```

Add this link under the engineering section of `docs/README.md`; the roadmap and Phase 0 plan links already exist before implementation begins:

```markdown
- [GitHub CI 检查契约](engineering/ci-checks.md)
- [依赖接受策略](engineering/dependency-policy.md)
```

- [ ] **Step 4: Run final local verification**

Run: `python tools/project.py verify`

Expected: exit 0 with all current-scope gates passing.

Run: `docker build --file docker/backend.Dockerfile --tag time-api:p0 .`

Expected: exit 0.

Run: `docker build --file docker/frontend.Dockerfile --tag time-web:p0 .`

Expected: exit 0.

Run: `git diff --check`

Expected: exit 0.

Run: `git status --short`

Expected: only the files explicitly listed in this plan are modified or untracked.

- [ ] **Step 5: Perform independent review before the final commit**

Use `superpowers:requesting-code-review`. Reviewer must check:

- the implementation against this plan and the approved ADRs;
- package name `time_agent` and absence of a local `time` package;
- exact command names in `tools/project.py`, documentation, and CI;
- generated contract reproducibility;
- pinned dependency, Action, and image identifiers;
- no product behavior, database, external supplier, OCR, LangChain, or LangGraph scope creep;
- tests fail for the intended reason before implementation and pass afterward.

Resolve every blocking finding and rerun affected and full verification.

- [ ] **Step 6: Commit the CI gate and phase evidence**

```bash
git add .github/branch-protection.json .github/workflows/ci.yml docs
git commit -m "ci(repo): enforce phase zero quality gates"
```

- [ ] **Step 7: Push the phase branch and verify remote checks**

Run: `git branch --show-current`

Expected: exactly `phase/p0-engineering-foundation`. Any other value stops the push and requires correcting the worktree branch first.

Run: `git push --set-upstream origin phase/p0-engineering-foundation`

Expected: push succeeds to `git@github.com:zdjc445/EL26.git`.

After the workflow starts, read the actual check-run names from GitHub. They must equal `quality`, `security`, `containers (time-api)`, and `containers (time-web)`. If GitHub reports different names, update both `docs/engineering/ci-checks.md` and `.github/branch-protection.json` from the observed values before configuring branch protection; do not normalize or guess them.

Run: `gh auth status`

Expected: authenticated to `github.com` with an identity that has Administration(write) permission on `zdjc445/EL26`.

Run: `gh api --method PUT -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2026-03-10" repos/zdjc445/EL26/branches/main/protection --input .github/branch-protection.json`

Expected: HTTP 200 and a branch-protection object.

Run: `gh api -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2026-03-10" repos/zdjc445/EL26/branches/main/protection`

Expected: response values exactly match `.github/branch-protection.json`. If the GitHub plan does not support this rule on the repository's actual visibility, stop and report the exact API error; do not weaken protection silently.

## Phase 0 Exit Evidence

Phase 0 is accepted only when all of the following are attached to its PR or work item:

- `python tools/project.py verify` output with zero failures;
- both local or CI container builds with zero failures;
- `git diff --check` output;
- OpenAPI drift check output;
- independent Review record and resolved findings;
- GitHub Actions URL showing all actual required jobs green;
- branch-protection API output after external configuration is authorized and applied;
- the exact commit SHAs and image digests used by the build;
- no untracked or unrelated files in the submitted Diff.

## Explicitly Out of Scope

The following are deferred to their roadmap phases and must not appear in the Phase 0 Diff:

- authentication, email, SMS, passwords, sessions, user tables, or tenant repositories;
- calendar entities, recurrence, reminders, notifications, or Agent tools;
- document upload, PDF/DOCX parsing, object storage, folders, or organization proposals;
- conversation persistence, LangGraph, LangChain, LLM calls, Embedding, Rerank, or RAG;
- PostgreSQL models or migrations, RabbitMQ, Valkey, Qdrant, Celery, or Terraform;
- production deployment, secrets, real supplier accounts, OCR, images, or external calendar integration.
