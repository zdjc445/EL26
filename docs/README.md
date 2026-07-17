# 工程文档索引

状态：书面评审中

基线日期：2026-07-17

本目录是项目规格、架构和工程治理的权威来源。聊天记录只用于形成设计，不作为长期规范。发生冲突时，按以下优先级处理：

1. 已批准的产品规格；
2. 已接受的架构决策记录（ADR）；
3. 系统设计；
4. 工程、测试和运维规范；
5. 实施计划与任务说明。

任何代码、迁移、基础设施或供应商配置都必须能追溯到这里的已批准条目。未记录的口头约定不得直接进入实现。

## 文档地图

### 产品

- [首版产品规格](product/v1-product-spec.md)：用户、范围、业务规则、验收条件和非目标。

### 架构

- [首版系统设计](architecture/v1-system-design.md)：模块边界、数据模型、运行时、数据流和安全边界。

### 工程管理

- [开发生命周期](engineering/development-lifecycle.md)：从 Spec 到发布的工业化变更流程。
- [测试与评测策略](engineering/test-and-evaluation-strategy.md)：测试层级、RAG 评测、负载及故障验证。
- [发布与运维标准](engineering/release-and-operations.md)：环境、CI/CD、SLO、备份、恢复和事故管理。

### 架构决策

- [ADR-0001：模块化单体与运行时拆分](adr/0001-modular-monolith-runtime-split.md)
- [ADR-0002：LangGraph 编排与 LangChain 边界](adr/0002-langgraph-orchestration-boundary.md)
- [ADR-0003：纯文本 RAG 与检索架构](adr/0003-text-rag-retrieval-architecture.md)

## 生命周期

```text
需求进入
→ 产品 Spec 审批
→ ADR / 系统设计更新
→ 实施计划
→ 测试设计
→ 小步实现
→ 自动验证
→ Diff 自审
→ 独立 Review
→ 预发布验收
→ 生产发布
→ 指标观测与复盘
```

本次文档基线获批后，下一步只能是编写详细实施计划；在实施计划获批前不得开始项目脚手架或功能代码。
