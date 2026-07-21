# Time Milestone 1 身份与工作台实施计划

状态：已批准

## Goal

在 `memory` runtime 下完成 `AUTH-01`～`AUTH-03` 与 `UI-01`～`UI-03`：用户可
通过邮箱或手机号验证码注册/登录，设置和使用密码，刷新与撤销会话，并进入具备
独立折叠状态、窄屏互斥抽屉和可访问性语义的学习工作台。

## Architecture

账号领域位于 `time_agent.modules.identity`。领域层使用不可变 dataclass、枚举和
纯函数；应用层通过端口访问时钟、ID、密码哈希、仓储、验证码投递和 Unit of
Work。`MemoryRuntime` 提供真实内存约束和事务语义。FastAPI 使用 HttpOnly
Cookie 解析会话，所有已认证写请求额外校验 CSRF Header。React 只调用生成的
OpenAPI 类型契约，不读取 Cookie 值。

本 Milestone 不创建数据库、供应商客户端、生产 profile、OAuth、MFA、RBAC 或
业务模块权限。

## Fixed public identifiers

### Configuration

- `TIME_RUNTIME_PROFILE`: 当前唯一合法值 `memory`，默认 `memory`。
- `TIME_AUTH_CODE_TTL_SECONDS`: 默认 `600`。
- `TIME_AUTH_CODE_RESEND_SECONDS`: 默认 `60`。
- `TIME_AUTH_CODE_MAX_SENDS_PER_HOUR`: 默认 `5`。
- `TIME_AUTH_CODE_MAX_ATTEMPTS`: 默认 `5`。
- `TIME_AUTH_SESSION_TTL_SECONDS`: 默认 `2592000`。
- `TIME_AUTH_COOKIE_SECURE`: 默认 `false`；production 环境必须为 `true`，但
  production profile 在本阶段仍拒绝启动。

### Identifier and credential rules

- `IdentifierKind`: `email`、`phone`。
- 邮箱：去除首尾空白后使用 Unicode `casefold()` 作为唯一性值；显示值保留去除
  首尾空白后的输入；必须恰好包含一个 `@`，两侧非空，总长度不超过 254。
- 手机号：去除首尾空白后必须匹配 `^\+[1-9][0-9]{7,14}$`；唯一性值与显示值
  相同。
- `ChallengePurpose`: `register`、`login`、`password_reset`、`add_identifier`、
  `change_identifier`。
- 验证码：使用密码学随机的 6 位十进制字符串；只保存 SHA-256 摘要。
- 密码：UTF-8 编码后长度 `12..128` 字节；不得只由空白组成。
- 密码哈希：标准库 `hashlib.scrypt`，参数 `n=16384`、`r=8`、`p=1`、
  `dklen=32`，每个密码使用 16 字节随机 salt；编码格式固定为
  `scrypt$n=16384,r=8,p=1$<base64-salt>$<base64-digest>`。
- 会话令牌：32 字节随机 URL-safe 字符串；服务端只保存 SHA-256 摘要。
- CSRF 令牌：32 字节随机 URL-safe 字符串；服务端保存摘要，前端仅在内存中
  保存明文并通过 `X-Time-CSRF-Token` 发送。

### Cookie and browser storage

- Cookie 名：`time_session`。
- Cookie 属性：`HttpOnly`、`SameSite=Lax`、`Path=/api/v1`，Max-Age 等于会话
  TTL；`Secure` 由 `TIME_AUTH_COOKIE_SECURE` 控制。
- localStorage 键：
  - `time.ui.primaryNavCollapsed`
  - `time.ui.contextPanelCollapsed`
- localStorage 值只允许字符串 `true` 或 `false`；缺失或其他值均按 `false`。

### HTTP contract

所有路径位于 `/api/v1`。

1. `POST /auth/challenges`
   - request: `identifier_kind`, `identifier`, `purpose`
   - purpose 只允许 `register` 或 `login`
   - response `201`: `challenge_id`, `expires_at`, `resend_available_at`
2. `GET /dev/auth/challenges/{challenge_id}/code`
   - 仅 `TIME_ENVIRONMENT=local` 且 memory profile 注册
   - response `200`: `challenge_id`, `code`
   - 其他环境路由不存在，而不是返回固定成功值
3. `POST /auth/register`
   - request: `challenge_id`, `code`
   - response `201`: `user`, `session`, `csrf_token` 并设置 Cookie
4. `POST /auth/login/code`
   - request: `challenge_id`, `code`
   - response `200`: `user`, `session`, `csrf_token` 并设置 Cookie
5. `POST /auth/login/password`
   - request: `identifier_kind`, `identifier`, `password`
   - response `200`: `user`, `session`, `csrf_token` 并设置 Cookie
6. `GET /auth/session`
   - response `200`: `user`, `session`, `csrf_token`
7. `DELETE /auth/session`
   - Header: `X-Time-CSRF-Token`
   - response `204` 并清除 Cookie
8. `GET /auth/sessions`
   - response `200`: `items`
9. `DELETE /auth/sessions/{session_id}`
   - Header: `X-Time-CSRF-Token`
   - response `204`; 允许撤销当前或其他同用户会话
10. `PUT /auth/password`
    - Header: `X-Time-CSRF-Token`
    - request: `new_password`, `current_password`（尚未设置密码时必须为 `null`；
      已设置时必须正确）
    - response `204`
11. `POST /auth/password-reset/challenges`
    - request: `identifier_kind`, `identifier`
    - 对存在和不存在的标识均返回相同 `202` 空响应；存在时创建
      `password_reset` challenge，不泄漏账号存在性
12. `POST /auth/password-reset/complete`
    - request: `challenge_id`, `code`, `new_password`
    - response `204`; 成功后撤销该用户所有既有会话
13. `GET /auth/identifiers`
    - response `200`: `items`
14. `POST /auth/identifiers/challenges`
    - Header: `X-Time-CSRF-Token`
    - request: `identifier_kind`, `identifier`, `purpose`，purpose 只允许
      `add_identifier` 或 `change_identifier`
    - response `201`: `challenge_id`, `expires_at`, `resend_available_at`
15. `POST /auth/identifiers`
    - Header: `X-Time-CSRF-Token`
    - request: `challenge_id`, `code`
    - response `201`: `identifier`
16. `PUT /auth/identifiers/{identifier_id}`
    - Header: `X-Time-CSRF-Token`
    - request: `challenge_id`, `code`
    - response `200`: `identifier`; challenge 必须属于 `change_identifier`，原标识
      在同一事务中替换
17. `DELETE /auth/identifiers/{identifier_id}`
    - Header: `X-Time-CSRF-Token`
    - response `204`; 删除最后一个标识返回 `identifier_required`

标识管理规则：新增标识默认 `is_primary=false`；替换标识保留被替换标识的
`is_primary` 值；删除非最后一个主标识时，将剩余标识中 `verified_at` 最早、若
相同则 `id` 字典序最小者设为主标识。任何时刻恰好一个标识为主标识。

公开对象：

- `UserView`: `id`, `primary_identifier`, `primary_identifier_kind`, `created_at`
- `IdentifierView`: `id`, `kind`, `display_value`, `verified_at`, `is_primary`
- `SessionView`: `id`, `created_at`, `expires_at`, `current`
- `AuthSessionView`: `user`, `session`, `csrf_token`

错误响应统一为 `ProblemDetail`：`code`, `message`。精确 code：

- `invalid_identifier`
- `challenge_rate_limited`
- `challenge_expired`
- `challenge_locked`
- `invalid_challenge_code`
- `identifier_already_exists`
- `identifier_not_found`
- `identifier_required`
- `account_not_found`
- `invalid_credentials`
- `invalid_password`
- `authentication_required`
- `invalid_csrf_token`
- `session_not_found`
- `concurrency_conflict`

验证码、密码、Cookie 和完整会话令牌不得出现在普通响应、Problem Detail 或
日志中；唯一例外是受 local+memory 双重限制的开发验证码读取响应。

## Domain records

- `User`: `id`, `created_at`, `version`
- `LoginIdentifier`: `id`, `user_id`, `kind`, `normalized_value`, `display_value`,
  `verified_at`, `is_primary`, `version`
- `VerificationChallenge`: `id`, `kind`, `normalized_value`, `display_value`,
  `purpose`, `code_digest`, `created_at`, `expires_at`, `resend_available_at`,
  `attempts_remaining`, `consumed_at`
- `PasswordCredential`: `user_id`, `encoded_hash`, `updated_at`, `version`
- `LoginSession`: `id`, `user_id`, `token_digest`, `csrf_digest`, `created_at`,
  `expires_at`, `revoked_at`, `version`
- `LoginAuditEvent`: `id`, `occurred_at`, `action`, `outcome`, `user_id`,
  `identifier_kind`, `identifier_fingerprint`, `session_id`

`identifier_fingerprint` 是 normalized identifier 的 SHA-256 前 12 个十六进制
字符，不记录完整邮箱或手机号。

## Task 1：运行时配置与共享端口

**Requirements:** ADR-0004。

**Create:**

- `backend/src/time_agent/shared/__init__.py`
- `backend/src/time_agent/shared/domain.py`
- `backend/src/time_agent/shared/ports.py`
- `backend/src/time_agent/bootstrap/runtime.py`
- `backend/tests/unit/bootstrap/test_runtime.py`

**Modify:**

- `backend/src/time_agent/config.py`
- `backend/src/time_agent/bootstrap/app.py`
- `backend/tests/architecture/rules.py`
- `backend/tests/architecture/test_module_boundaries.py`

**RED:** 测试 `Settings(runtime_profile="production")` 被拒绝、memory runtime
隔离、未知 profile 不回退，以及领域层不能导入 `bootstrap`/`adapters`。

**GREEN:** 定义 `Clock`、`IdGenerator`、`TokenGenerator`、`UnitOfWork` Protocol，
`SystemClock`、`UuidGenerator`、`SecureTokenGenerator` 和 `MemoryRuntime`。应用工厂
接受可选 runtime，并写入 `app.state.runtime`。

**Verify:**

```bash
uv run --project backend pytest backend/tests/unit/bootstrap backend/tests/architecture -q
uv run --project backend ruff check --config backend/pyproject.toml backend/src backend/tests
uv run --project backend mypy --config-file backend/pyproject.toml backend/src backend/tests
```

**Commit:** `feat(runtime): add memory composition root`

## Task 2：认证领域规则

**Requirements:** `AUTH-01`～`AUTH-03`。

**Create:**

- `backend/src/time_agent/modules/identity/__init__.py`
- `backend/src/time_agent/modules/identity/domain/__init__.py`
- `backend/src/time_agent/modules/identity/domain/models.py`
- `backend/src/time_agent/modules/identity/domain/rules.py`
- `backend/src/time_agent/modules/identity/domain/errors.py`
- `backend/tests/unit/identity/__init__.py`
- `backend/tests/unit/identity/test_identifiers.py`
- `backend/tests/unit/identity/test_challenges.py`
- `backend/tests/unit/identity/test_passwords.py`
- `backend/tests/unit/identity/test_sessions.py`

**RED:** 精确覆盖 normalization、全局唯一输入、challenge TTL/重发/次数/锁定/
消费、首次注册必须验证码、密码边界、过期与撤销会话。

**GREEN:** 只实现纯领域记录、规则和错误；不导入 FastAPI/Pydantic 或仓储。

**Verify:** focused pytest、Ruff、mypy、架构测试。

**Commit:** `feat(identity): define authentication domain rules`

## Task 3：身份应用服务与内存适配器

**Requirements:** `AUTH-01`～`AUTH-03`。

**Create:**

- `backend/src/time_agent/modules/identity/ports.py`
- `backend/src/time_agent/modules/identity/application.py`
- `backend/src/time_agent/modules/identity/adapters/__init__.py`
- `backend/src/time_agent/modules/identity/adapters/memory.py`
- `backend/src/time_agent/modules/identity/adapters/security.py`
- `backend/tests/unit/identity/test_application.py`
- `backend/tests/unit/identity/test_memory_adapters.py`

**Ports:** `IdentityRepository`, `ChallengeDelivery`, `PasswordHasher`。

**Commands:** `RequestChallenge`, `RegisterWithCode`, `LoginWithCode`,
`LoginWithPassword`, `SetPassword`, `RequestPasswordReset`, `CompletePasswordReset`,
`RequestIdentifierChallenge`, `AddIdentifier`, `ChangeIdentifier`,
`RemoveIdentifier`, `RevokeSession`, `RevokeAllSessions`。

**RED:** 两用户唯一性、未知登录、账号枚举保护、重复 code、并发 challenge、
幂等消费、添加/替换/删除标识、最后标识保护、密码修改、重置撤销全部会话、
跨用户 session 撤销和审计脱敏。

**GREEN:** 应用服务在 Unit of Work 内执行规则；内存仓储维护唯一索引、token
摘要索引和原子副本提交；Outbox 只供 local memory 开发读取。

**Commit:** `feat(identity): implement in-memory authentication services`

## Task 4：FastAPI 认证契约

**Requirements:** `AUTH-01`～`AUTH-03`。

**Create:**

- `backend/src/time_agent/modules/identity/schemas.py`
- `backend/src/time_agent/modules/identity/api.py`
- `backend/src/time_agent/modules/identity/dependencies.py`
- `backend/tests/integration/identity/__init__.py`
- `backend/tests/integration/identity/test_auth_api.py`
- `backend/tests/integration/identity/test_auth_security.py`

**Modify:**

- `backend/src/time_agent/bootstrap/app.py`
- `backend/scripts/export_openapi.py`（仅在确定性排序需要时）

**RED:** 全部 17 个 endpoint、Cookie 属性、CSRF、错误 code、开发路由环境门禁、
Cookie 篡改、撤销后重用、过期和跨用户 session ID。

**GREEN:** router、依赖和错误映射只做 HTTP 转换；权威 user ID 来自 session。

**Generate:**

```bash
python tools/project.py contract-generate
python tools/project.py contract-check
```

**Commit:** `feat(identity): expose authentication HTTP contract`

## Task 5：前端认证流程

**Requirements:** `AUTH-01`～`AUTH-03`。

**Create:**

- `frontend/src/features/auth/api.ts`
- `frontend/src/features/auth/AuthContext.tsx`
- `frontend/src/features/auth/LoginPage.tsx`
- `frontend/src/features/auth/RegisterPage.tsx`
- `frontend/src/features/auth/PasswordSettings.tsx`
- `frontend/src/features/auth/SessionSettings.tsx`
- `frontend/src/features/auth/IdentifierSettings.tsx`
- `frontend/src/features/auth/LoginPage.test.tsx`
- `frontend/src/features/auth/RegisterPage.test.tsx`
- `frontend/src/features/auth/AuthContext.test.tsx`

**Modify:**

- `frontend/src/app/AppProviders.tsx`
- `frontend/src/app/App.tsx`
- `frontend/src/styles/index.css`

**Behavior:** `fetch` 固定 `credentials: "include"`；AuthContext 只在内存保存 CSRF
token；刷新后通过 `GET /auth/session` 恢复；401 跳转 `/login`；登录用户访问
`/login` 或 `/register` 跳转 `/app/today`。

**RED:** 邮箱/手机号切换、验证码请求、local code 输入、注册、验证码登录、密码
登录、添加/变更/删除登录标识、最后标识保护、错误提示、刷新恢复和退出。

**Commit:** `feat(frontend): add authentication flows`

## Task 6：学习工作台壳

**Requirements:** `UI-01`～`UI-03`。

**Create:**

- `frontend/src/app/RequireAuth.tsx`
- `frontend/src/features/workbench/WorkbenchLayout.tsx`
- `frontend/src/features/workbench/WorkbenchLayout.test.tsx`
- `frontend/src/features/workbench/usePersistentPanelState.ts`
- `frontend/src/features/workbench/PlaceholderPage.tsx`

**Modify:**

- `frontend/src/app/App.tsx`
- `frontend/src/styles/index.css`

**Routes:**

- `/app/today`
- `/app/chat`
- `/app/calendar`
- `/app/knowledge`
- `/app/progress`
- `/app/settings`

**Behavior:** 主导航始终存在；桌面折叠为图标栏；上下文栏可完全隐藏并保留展开
按钮；两个状态独立持久化；`max-width: 767px` 使用覆盖抽屉且互斥；Escape 关闭；
按钮具有 `aria-expanded`、`aria-controls` 和明确中文名称；路由切换保持状态。

**RED:** 导航名称/链接、独立状态、刷新、无效 storage、窄屏互斥、Escape、键盘
激活与 ARIA。

**Commit:** `feat(workbench): add accessible dual-sidebar shell`

## Task 7：Milestone 1 E2E 与完成门禁

**Create:**

- `frontend/tests/e2e/auth-workbench.spec.ts`

**Modify:**

- `frontend/playwright.config.ts`（仅当现有 webServer 无法复用时）
- `docs/README.md`
- `docs/superpowers/plans/2026-07-21-v1-local-first-application.md`（记录完成证据）

**E2E:** 邮箱注册、退出、验证码登录、设置密码、密码登录、撤销其他会话、六个
导航入口、桌面双折叠、刷新保持和窄屏互斥抽屉。

**Full verification:**

```bash
python tools/project.py verify
docker build --file docker/backend.Dockerfile --tag time-api:m1 .
docker build --file docker/frontend.Dockerfile --tag time-web:m1 .
git diff --check
```

CI 必须保持实际检查名 `quality`、`security`、`containers (time-api)`、
`containers (time-web)` 全绿。

**Commit:** `test(m1): verify identity and workbench milestone`

## Milestone 1 exit evidence

- `AUTH-01`～`AUTH-03`、`UI-01`～`UI-03` 每项存在测试映射；
- 验证码、密码、Cookie、会话 token 不出现在日志或普通响应；
- 全局 identifier 唯一与所有 session 查询均强制用户范围；
- Cookie、CSRF、撤销、过期和账号枚举测试通过；
- 双侧栏桌面、窄屏、键盘和屏幕阅读器语义通过；
- OpenAPI 与 TypeScript 类型无漂移；
- 完整本地验证、容器和 CI 全绿；
- 工作区只包含本计划列出的变更。

## Out of scope

- 真实邮件/短信供应商、PostgreSQL 和分布式限流；
- OAuth、MFA、管理员、角色和组织；
- `KB`、`RAG`、`CHAT`、`CAL`、`LEARN` 的业务行为；
- 生产 profile、生产部署和真实用户数据。
