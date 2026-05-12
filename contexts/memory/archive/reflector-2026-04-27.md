# Reflector Summary — 2026-04-27

## 晋升内容

### → SOUL.md
**单 Agent 三大结构性缺陷（已验证）**（来源：2026-04-20 🔴 × 2）
- Context Rot：注意力机制在长序列下质量退化（Lost in the Middle），冗余 context 加速退化
- 角色混淆：同一 agent 既执行又审查，confirmation bias 结构性存在，无法靠 prompt 修复
- 串行瓶颈：agentic loop 单线程
- 核心判断：架构约束优于 prompt 约束

**OMO 运行原理（OpenCode Plugin 模式）**（来源：2026-04-20 🔴，2026-04-22 🟡）
- OMO 不依赖 ACP 协议，通过 Plugin Hook 系统在进程内拦截 LLM 调用参数
- `task()` 每个子 agent 是独立 OpenCode session
- `category` 是启动 Sisyphus-Junior 的唯一入口

### → USER.md
**当前项目关注点补充**（来源：2026-04-20~22 🟡）
- OMO 分享文档撰写（km.sankuai.com/collabpage/2757179530）
- DataMatrix 迁移自动化 + Pontos BatchUpdatePackage Crane Job

## GC 结果

OBSERVATIONS.md 从 **167 行**减少到 **112 行**（含文件头注释）。

删除的条目类型：
- 全部 🟢 Low 条目（8 条）：任务流水，已完成
- 已完结的 🟡 Medium 条目（17 条）：KB 初始化完成、工具建设完成、observer bug 修复、KB 待办逾期已清零等
- 已晋升到 SOUL.md 的 🔴 条目（3 条）：OMO 架构洞察、单 Agent 缺陷、observer.py bug 修复
- 已完结的工具升级记录（1 条）：opencode 升级到 1.14.20

保留的条目：
- 所有仍活跃的技术约束（Jackson 版本、hermes HTTPS、Blade Lion meta 等）
- 所有仍活跃的项目状态（Q2/Q3 方向、ES 可观测性、dish-cserver、Athena bug 待修复等）
- 所有未解决的 KB 待办
- 新增的 2026-04-26 条目（Notes 知识库重组，Karpathy LLM Wiki 模式）

## Skill 草稿

生成 1 个草稿：
- `DRAFT_20260427_omo-multiagent-architecture.md` — OMO Multi-agent 架构选择指南（单 Agent 三大缺陷、task() 原理、职责划分方式、何时拆分为 multi-agent）

跳过（已有 skill 覆盖）：
- DataMatrix 积压诊断 → 已有 `datamatrix-lag-check` skill
- KB 维护 → 已有 `kb-curator` skill
- Python cron venv → 已有 `python-cron-venv-isolation` skill

无候选（仅出现一次，不满足重复性条件）：
- ES Sniffer 诊断框架（2026-04-21 单次出现）
- Athena CuratorCache 根因（2026-04-23 单次出现）
- Karpathy LLM Wiki 模式（2026-04-26 单次出现）

## 备注

- 本次 OBSERVATIONS.md 在 Reflector 运行期间有新内容写入（2026-04-26 条目），已正确合并保留
- 2026-04-26 的 Karpathy LLM Wiki 🔴 条目（方法论）仅出现一次，暂不生成 skill 草稿，下次 Reflector 若再次出现则升级
- Athena CuratorCache bug 仍待修复（🔴 条目保留），修复完成后可归档
- Blade Lion meta `cluster` 字段补充（🔴 部署前置条件）已 11 天未处理，接近 14 天逾期阈值
