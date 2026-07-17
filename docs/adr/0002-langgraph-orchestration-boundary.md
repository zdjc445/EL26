# ADR-0002：LangGraph 编排与 LangChain 边界

状态：已批准

日期：2026-07-17

## 背景

Agent 需要流式讲解、RAG、工具调用、会话状态和高影响日历操作审批。完全自研需要重复实现持久化图执行和暂停恢复；直接使用开放式 LangChain Agent 又可能让模型循环承担业务事务。

## 决策

- 使用 LangGraph 编排在线 Agent 状态图；
- 使用 LangChain 的模型、消息、工具和必要中间件组件；
- 领域服务负责权限、校验、事务、幂等、并发和审计；
- LangGraph Checkpoint 只保存执行状态；
- 原始对话、长期学习状态、日历和资料任务保存在业务数据库；
- 文档处理由 Celery 执行，不进入 Agent 图；
- 高影响操作使用 LangGraph Interrupt 等待批准，真正写入放在批准后的独立节点。

## 禁止边界

- Agent 直接执行 SQL；
- LangChain Memory 成为长期记忆唯一来源；
- LangChain VectorStore 绕过用户过滤；
- LangGraph Checkpoint 替代业务事务；
- 领域模块公开 LangChain／LangGraph 类型；
- 中断前执行非幂等副作用。

## 备选方案

### LangChain `create_agent` 掌管全部流程

拒绝原因：日历审批、批量原子写入和业务恢复需要明确状态机与确定性服务，不能只依赖模型工具循环。

### 完全自研编排

拒绝原因：需要重复实现持久化、流式、暂停、恢复和图调试，首版收益不足。

## 后果

正面：

- 人工审批和恢复路径明确；
- 保留模型供应商适配；
- 图节点和领域逻辑可独立测试；
- 能追踪执行过程。

负面：

- 存在业务数据和 Checkpoint 两类状态，需要清晰关联；
- LangGraph 升级需要 Checkpoint 兼容测试；
- 节点重跑要求所有外部副作用幂等。

## 重新评估触发条件

- Agent 图退化为单一模型调用且无暂停恢复需求；
- LangGraph 无法满足供应商流式或部署要求；
- Checkpoint 运维成本超过自研显式状态机；
- 新框架经过评测能降低复杂度且不侵入领域边界。

## 参考

- [LangGraph 概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
