---
name: omo-multiagent-architecture
description: |
  OMO（oh-my-opencode）Multi-agent 架构选择指南。当需要决策"是否用 Multi-agent"、"如何拆分 agent 职责"、"task() 工具的正确用法"、"category 路由原理"时使用。
  触发场景：
  - 讨论单 agent vs multi-agent 选择
  - 设计 agent 分工方案
  - 理解 task() 工具的实现原理
  - 选择 category 参数
  - 分析 Context Rot / 角色混淆 / 串行瓶颈问题
---

# OMO Multi-agent 架构选择指南

## 触发场景

- 用户询问"要不要用 multi-agent"
- 需要拆分复杂任务为多个 sub-agent
- 理解 `task()` 工具的底层机制
- 分析 agent 系统性能瓶颈（慢、质量差、自我审查失效）

## 核心知识：单 Agent 的三大结构性缺陷

这三个缺陷是结构性的，无法靠 prompt 修复：

1. **Context Rot（上下文腐烂）**：注意力机制在长序列下质量退化（Lost in the Middle 现象）。冗余 context 加速退化。解法：上下文隔离（每个 sub-agent 只拿它需要的 context）。

2. **角色混淆**：同一 agent 既执行又审查，confirmation bias 结构性存在。解法：角色分离（执行 agent 和审查 agent 独立，不共享 context）。

3. **串行瓶颈**：agentic loop 单线程，无法并行。解法：并行执行（`run_in_background=true` 的 task()）。

**核心判断：架构约束优于 prompt 约束。**

## OMO 运行原理

OMO 是标准 OpenCode Plugin，通过 Plugin Hook 系统在进程内拦截 LLM 调用参数（非 ACP 协议）。

`task()` 工具实现原理：
1. `category` 路由解析模型（每个 category 对应不同的模型配置）
2. `ctx.client.session.create()` 创建独立 session
3. `ctx.client.session.promptAsync()` 向新 session 发送 prompt
4. 每个子 agent 是独立 OpenCode session，有独立 context window 和 agent persona

关键约束：
- `category` 参数是启动 Sisyphus-Junior 的**唯一**入口，不可直接 `subagent_type="sisyphus-junior"`
- `BLOCKED_TOOLS: ["task"]` 确保 Junior 不再 delegate（防止无限递归）
- 子 agent 的 context window 是独立的，主 agent 的记忆不会自动传入

## Agent 职责划分三种方式（稳定性递减）

1. **按工具/能力划分**（最稳定）：一个 agent 只能用特定工具集（如 web agent 只有浏览器工具）
2. **按领域知识划分**（次稳定）：一个 agent 专注特定领域（如 frontend-ui-ux agent）
3. **按角色/工序划分**（最易变）：执行者/审查者/规划者分离

## 操作指南：何时拆分为 Multi-agent

**需要 multi-agent 的信号：**
- 任务需要 3+ 独立的搜索/分析维度（并行化收益大）
- 需要自我审查（执行和审查必须角色分离）
- context 已经很长，继续追加会导致质量退化
- 任务可以被明确拆分为独立子任务（无共享状态依赖）

**不需要 multi-agent 的场景：**
- 单文件修改（直接用工具）
- 已知文件位置的简单查询
- 顺序依赖强的任务（后一步依赖前一步的结果）

## 与 CC（Claude Code）的对比

| 维度 | OMO | Claude Code |
|------|-----|-------------|
| subagent 定义 | category 路由（框架侧决策） | `.claude/agents/*.md`（模型侧语义匹配） |
| 多 session 协作 | 无共享状态 | Agent Teams（实验性，Shared Task List + Mailbox） |
| 自治循环 | Ralph Loop | CC Routines（云端托管） |

## 来源条目

- Date: 2026-04-20 — 🔴 OMO 不依赖 ACP 协议，是标准 OpenCode Plugin
- Date: 2026-04-20 — 🔴 单 Agent 三大结构性缺陷
- Date: 2026-04-22 — 🟡 OMO Sisyphus-Junior 定位确认 + CC/Codex 编排对比
