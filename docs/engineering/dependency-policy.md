# Dependency Acceptance Policy

状态：已批准

本策略约束 Time 构建和运行依赖，不向仓库源代码授予开源许可证。

Python 依赖必须由 `licensecheck==2026.0.8` 识别为 MIT、Apache、BSD、ISC、MPL、Python、Unlicense、0BSD 或 CC0 类许可证。Node.js 依赖必须由 `license-checker-rseidelsohn==5.0.1` 识别为 `MIT`、`MIT-0`、`Apache-2.0`、`BSD-2-Clause`、`BSD-3-Clause`、`ISC`、`0BSD`、`Python-2.0`、`PSF-2.0`、`MPL-2.0`、`Unlicense`、`CC0-1.0`、`CC-BY-3.0`、`CC-BY-4.0` 或 `BlueOak-1.0.0`。SPDX `AND`/`OR` 表达式只有在每个组成许可证都位于上述白名单时才可接受；当前工具输出中的精确组合必须显式固定。私有根包通过 `--excludePrivatePackages` 排除，绝不把 `UNLICENSED` 加入第三方依赖白名单。

未知许可证、猜测许可证、GPL、AGPL、LGPL、SSPL、Commons Clause 或自定义限制性条款默认阻断合并。接受例外前必须保存许可证原文、法律或授权判断、影响范围、Owner 和重新评估条件；需要长期保留的架构性例外通过 ADR 审批。

漏洞扫描不允许用自动重试或忽略所有未修复问题变绿。单个漏洞例外必须引用精确漏洞 ID、受影响版本、可利用性证据、补偿控制、Owner 和到期日。
