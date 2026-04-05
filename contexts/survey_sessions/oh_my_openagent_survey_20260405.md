# Oh My OpenAgent (OMO) 深度调研报告

**调研日期**: 2026-04-05  
**调研方法**: 3 个并行 sub-agent 交叉验证 + 初步扫描  
**主要来源**: 官方文档、GitHub 仓库代码、社区讨论、第三方评测

---

## 核心结论

Oh My OpenAgent（简称 OMO，原名 oh-my-opencode）是一个运行在 OpenCode 上的**多模型 agent 编排 harness**。它把一个单一 AI 助手扩展成一个"能实际落地交付代码的协同开发团队"。

> "Oh My OpenAgent is a multi-model agent orchestration harness for OpenCode. It transforms a single AI agent into a coordinated development team that actually ships code."  
> — [overview.md](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/overview.md)

核心哲学：**不锁定任何模型提供方**。不是 Claude-only，不是 OpenAI-only，而是按任务类型自动路由到最合适的模型。

---

## 一、整体架构

### 与原生 OpenCode 的区别

原生 OpenCode 是一个 AI 编码工具（类 Claude Code 的 CLI），单模型、单线程。OMO 在其上加了一层**多模型编排层**：

```
用户请求
  ↓
[Intent Gate] — 分类真实意图
  ↓
[Sisyphus] — 主 orchestrator，计划 + 派发
  ↓
┌─────────────────────────────────────────────┐
│ Prometheus  Atlas  Oracle  Librarian  Explore │
│     Category-based agents（按类别路由）        │
└─────────────────────────────────────────────┘
```

> "The Architecture: User Request → Intent Gate → Sisyphus → Prometheus / Atlas / Oracle / Librarian / Explore / Category-based agents"  
> — [overview.md](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/overview.md)

> "When Sisyphus delegates to a subagent, it doesn't pick a model name. It picks a category — visual-engineering, ultrabrain, quick, deep. The category automatically maps to the right model."  
> — [overview.md](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/overview.md)

**三层架构**：
- **Planning Layer**：Prometheus（规划）+ Metis（gap 分析）+ Momus（计划审核）
- **Execution Layer**：Atlas（任务分发 + learnings 汇总）
- **Worker Layer**：Explore / Librarian / Oracle / Category-based agents

> "The orchestration system uses a three-layer architecture that solves context overload, cognitive drift, and verification gaps through specialization and delegation."  
> — [orchestration.md](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/orchestration.md)

---

## 二、10 个专化 Agent

来源：[overview.md — Meet the Agents](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/overview.md)

| Agent | 角色 | 职责 | 何时用 |
|-------|------|------|--------|
| **Sisyphus** | Discipline Agent（主控） | 主 orchestrator，计划、派发、驱动任务完成，aggressive 并行执行 | 每次请求的入口 |
| **Hephaestus** | Legitimate Craftsman | 运行 GPT-5.4，给目标不给配方，自主探索代码库、调研模式、端到端实现 | 需要深度架构推理的大任务 |
| **Prometheus** | Strategic Planner | 像真实工程师一样采访你，澄清需求，识别边界，在写一行代码前先做详细计划 | 复杂任务的规划阶段 |
| **Atlas** | Conductor | 执行 Prometheus 的计划，分配任务给子代理，积累 learnings，独立验证完成情况 | 计划执行与任务分发 |
| **Oracle** | Consultant | 只读的高智商架构顾问，处理架构决策和复杂调试 | 遇到陌生模式、安全问题、多系统权衡时 |
| **Metis** | Gap Analyzer | 抓住 Prometheus 遗漏的东西，在计划定稿前做缺口分析 | 计划审核前 |
| **Momus** | Ruthless Reviewer | 严格审核计划，对照清晰度、可验证性、上下文完整性打分 | 计划提交前的最终把关 |
| **Explore** | Fast Codebase Grep | 用速度优先的模型做模式发现，快速搜索代码库 | 内部代码库搜索 |
| **Librarian** | Documentation & OSS Search | 文档检索、开源库 API 查找，跟踪最新最佳实践 | 外部文档、库 API、开源代码搜索 |
| **Multimodal Looker** | Vision & Screenshot Analysis | 视觉和截图分析 | UI/前端相关的视觉任务 |

---

## 三、Category → Model 路由

来源：[orchestration.md — Built-in Categories](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/orchestration.md) + [agent-model-matching.md](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/agent-model-matching.md)

| Category | 默认模型 | 适用场景 |
|----------|---------|---------|
| `visual-engineering` | Gemini 3.1 Pro | UI、CSS、动画、前端组件 |
| `ultrabrain` | GPT-5.4 (xhigh) | 硬逻辑、架构决策、算法 |
| `artistry` | Gemini 3.1 Pro (high) | 创意、brainstorm、非常规思路 |
| `deep` | GPT-5.4 (medium) | 自主深度调研 + 端到端实现 |
| `quick` | GPT-5.4 Mini | 单文件改动、简单修改 |
| `unspecified-low` | Claude Sonnet 4.6 | 低复杂度杂项任务 |
| `unspecified-high` | Claude Opus 4.6 (max) | 高复杂度杂项任务 |

> 注：这是默认映射，可以在 `oh-my-openagent.json` 的 `categories` 字段中覆盖。

配置示例：
```json
{
  "$schema": "...oh-my-openagent.schema.json",
  "agents": {
    "oracle": { "model": "openai/gpt-5.4", "variant": "high" },
    "explore": { "model": "github-copilot/grok-code-fast-1" }
  },
  "categories": {
    "quick": { "model": "opencode/gpt-5-nano" },
    "visual-engineering": { "model": "google/gemini-3.1-pro" }
  }
}
```

---

## 四、Skills 系统

来源：[docs/reference/configuration.md](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/reference/configuration.md)

Skills 是可配置的领域能力单元，支持：
- 外部技能源（本地目录或 URL）
- 启用/禁用控制
- Per-skill 的模型、工具白名单、描述、模板

```json
"sources": [
  { "path": "./my-skills", "recursive": true },
  "https://example.com/skill.yaml"
],
"enable": ["my-skill"],
"disable": ["other-skill"],
"my-skill": {
  "description": "What it does",
  "template": "Custom prompt template",
  "model": "custom/model",
  "allowed-tools": ["read", "bash"]
}
```

Skills 通过 `skill` 工具在运行时被发现和调用。OMO 内置了三层 MCP 系统：
- **Built-in MCPs**：websearch、context7、grep_app
- **Claude Code `.mcp.json` 配置**
- **Skill-embedded YAML**（通过 `SKILL.md` 描述）

---

## 五、Memory / 跨 Session 记忆

来源：代码库多处实现文件

**三层记忆架构**（优先级从高到低）：

```
1. In-memory session agent（最新，由 /start-work 设置）
2. Boulder state（boulder.json，跨重启持久化）
3. Message files（fallback，无 boulder state 时使用）
```

> "Get the effective agent for the session. Priority order: 1. In-memory session agent (most recent, set by /start-work) 2. Boulder state agent (persisted across restarts, fixes #927) 3. Message files (fallback for sessions without boulder state)"  
> — [agent-resolution.ts](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/src/hooks/prometheus-md-only/agent-resolution.ts)

**Boulder State**（持久化状态）：
```typescript
export const BOULDER_DIR = ".sisyphus"
export const BOULDER_FILE = "boulder.json"
export const BOULDER_STATE_PATH = `${BOULDER_DIR}/${BOULDER_FILE}`
```
来源：[constants.ts](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/src/features/boulder-state/constants.ts)

**Draft 作为外部记忆**（Prometheus 的核心设计）：

> "Draft is your memory outside the context window. NEVER skip draft updates. Your memory is limited. The draft is your backup brain."  
> — [behavioral-summary.ts](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/src/agents/prometheus/behavioral-summary.ts)

---

## 六、Lifecycle Hooks（40+ hooks）

来源：[PR #1958](https://github.com/code-yeongyu/oh-my-openagent/pull/1958)

总共 **45 个 hooks**，分两类：
- **13 个 gatable hooks**（可配置触发频率）
- **32 个 always-fire hooks**（零成本/安全关键/基础设施类，始终触发）

> "Instead of configuring each of the 45 hooks individually, users configure 5 logical groups that control 13 gatable hooks. The remaining 32 hooks always fire because they are zero-cost, reactive-safety, state-critical, or infrastructure hooks."  
> — [PR #1958](https://github.com/code-yeongyu/oh-my-openagent/pull/1958)

**5 个分组 + 13 个可控 hooks**：

| 分组 | Hooks |
|------|-------|
| `tool_guidance` | agent-usage-reminder, category-skill-reminder, atlas |
| `context_injection` | rules-injector, directory-agents-injector, directory-readme-injector, start-work |
| `reminders` | sisyphus-junior-notepad, anthropic-effort |
| `continuation` | （reserved，todo-continuation-enforcer 为复杂类型） |
| `error_recovery` | edit-error-recovery, json-error-recovery, delegate-task-retry, anthropic-context-window-limit-recovery |

不可包装的 hooks：`session-recovery`、`todo-continuation-enforcer`

---

## 七、高级技巧（非显而易见）

### 1. Ultrawork 模式
最快的工作方式：输入 `ultrawork` 或 `ulw`，系统自动探索代码库、调研模式、实现功能、验证结果，直到完成。

> "Ultrawork: Type ultrawork or just ultrawork. The agent figures everything out. Explores your codebase. Researches patterns. Implements the feature. Verifies with diagnostics. Keeps working until done."  
> — [ohmyopenagent.com](https://ohmyopenagent.com/)

### 2. Hashline Edit（防错位编辑）
开启后，每行前附带 LINE#ID 哈希值，防止模型因上下文漂移导致编辑错位。大规模重构时强烈推荐。

```json
{ "hashline_edit": true }
```

来源：[configuration.md](https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/dev/docs/reference/configuration.md)

### 3. session_id 连续性
每次 `task()` 调用返回 `session_id`。后续跟进时传入 `session_id` 可保留完整上下文，节省 70%+ tokens。

### 4. Wisdom Accumulation
Atlas 在任务完成后汇总 learnings，跨任务复用，避免重复探索。

### 5. Prometheus + Metis + Momus 三步规划
对于复杂任务，不要直接实现——先走 Prometheus（采访规划）→ Metis（gap 分析）→ Momus（严格审核）的完整规划链，再交给 Atlas 执行。

---

## 八、常见坑点

| 坑点 | 原因 | 对策 |
|------|------|------|
| 会话中断后进度丢失 | 未正确维护 boulder.json 状态 | 使用 `/start-work` 命令，依赖 boulder.json 恢复 |
| 编辑错位 | 上下文漂移导致行号不准确 | 开启 `hashline_edit: true` |
| 禁用了内置 MCP | 错误配置导致 websearch/context7/grep_app 失效 | 谨慎修改 MCPs 配置，只禁用明确不需要的 |
| 直接指定模型名而非 category | 未来切换模型时需要改所有调用 | 始终用 category 路由，在 config 里统一覆盖模型 |
| 单模型承担复杂任务 | 没有利用 Prometheus+Atlas 分层 | 复杂任务走完整规划链 |

社区反馈（Reddit）：
- [oh-my-opencode has been a gamechanger](https://www.reddit.com/r/ClaudeCode/comments/1pp2tyw/ohmyopencode_has_been_a_gamechanger/)
- [oh-my-opencode is great, just got a bit...](https://www.reddit.com/r/opencodeCLI/comments/1qdylr7/ohmyopencode_is_great_just_i_think_got_a_bit/)

---

## 九、与其他框架对比

来源：[Cursor vs OpenCode (SolomonSignal)](https://www.solomonsignal.com/launch-school/comparisons/cursor-vs-opencode) + [OpenCode vs Claude Code vs Cursor (NxCode)](https://www.nxcode.io/resources/news/opencode-vs-claude-code-vs-cursor-2026)

| 维度 | OMO/OpenCode | Cursor | Claude Code |
|------|-------------|--------|-------------|
| 开源 | ✅ | ❌ 商业 | ❌ 商业 |
| 多模型 | ✅ 无锁定 | 有限 | ❌ Claude-only |
| 并行 agent | ✅ 原生支持 | ❌ | 有限 |
| IDE 集成 | CLI | ✅ 全功能 IDE | CLI |
| 自托管 | ✅ | ❌ | ❌ |
| 上手难度 | 中（需要配置） | 低（开箱即用） | 低 |

---

## 十、如何用好 OMO（华雨视角的实践建议）

你的使用场景（AI 工作流探索、multi-agent 实验、AI-native 开发）和 OMO 的设计哲学高度契合。以下是结合你的背景的具体建议：

### 立即能用的
1. **Ultrawork 模式**：不确定怎么拆任务时，直接 `ultrawork`，让系统自己决定
2. **Category 路由**：写 prompt 时明确用 `category="deep"` / `category="artistry"` 等，不要用默认
3. **Session continuity**：每次 delegate 后保存 `session_id`，跟进时传入，省 tokens

### 深度玩法
4. **Prometheus 规划链**：对于你的 side-project，先用 Prometheus 做采访式规划，再执行，比直接实现质量高很多
5. **Skills 作为可复用知识**：把你的工作流（如深度调研流程、代码 review checklist）封装成 skill，让 agent 在合适时机自动调用
6. **Memory 系统**：你已经有三层记忆架构（OBSERVATIONS.md + heartbeat），这和 OMO 的 Boulder + Draft 设计理念完全一致，可以深度结合

### 需要警惕的
7. **别把 OMO 当聊天机器人用**：它的价值在编排，不在单轮对话。一个好问题 + 正确的 category 路由 >> 十个普通问题
8. **Hooks 配置不要乱动**：32 个 always-fire hooks 是基础设施，除非你很清楚在干什么，否则不要禁用

---

## 主要参考资源

- [官方站点](https://ohmyopenagent.com/)
- [GitHub 仓库](https://github.com/code-yeongyu/oh-my-openagent)
- [Overview 文档](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/overview.md)
- [Orchestration 文档](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/orchestration.md)
- [配置参考](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/reference/configuration.md)
- [Agent-Model Matching](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/agent-model-matching.md)
- [AGENTS.md](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/AGENTS.md)
- [官方文档站](https://ohmyopenagent.com/en/docs)
- [PR #1958 (Hook Cadence)](https://github.com/code-yeongyu/oh-my-openagent/pull/1958)
