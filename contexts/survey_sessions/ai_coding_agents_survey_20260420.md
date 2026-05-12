# AI Coding Agents 竞品分析报告 2025-2026

**调研日期**: 2026-04-20  
**调研范围**: Claude Code, Cursor, Devin, GitHub Copilot, Windsurf, Aider, Continue.dev, Amp, Zed AI  
**方法**: 5个并行 sub-agent 分别调研不同维度，交叉验证

---

## 核心结论（TL;DR）

1. **市场格局**: Claude Code 以 46% 市占率后来居上，Cursor 估值 $29.3B，Copilot 用户基数最大（20M+）
2. **能力基准**: Claude Code (Opus 4.6) SWE-bench 80.8% >> Copilot 56% >> Devin 13.86%（2024 数据，已过时）
3. **架构分化**: 终端 agent（Claude Code/Aider/Amp）vs AI-native IDE（Cursor/Windsurf）vs 云沙箱（Devin）vs IDE 插件（Copilot）
4. **最大共同痛点**: 跨 session 记忆丢失、context compaction 破坏指令、上下文窗口"虚标"
5. **MCP 生态**: 已成事实标准，2300+ servers，97M+ 月下载，Linux Foundation 治理
6. **定价收敛**: $20/月入门，$200/月 power user，免费层缩水，usage-based 争议持续
7. **2026 趋势**: multi-agent 成标配，computer use 整合，context 竞争白热化

---

## 目录

1. [Claude Code (Anthropic)](#1-claude-code)
2. [Cursor (Anysphere)](#2-cursor)
3. [Windsurf (Codeium → Cognition)](#3-windsurf)
4. [Devin (Cognition AI)](#4-devin)
5. [GitHub Copilot (Microsoft/GitHub)](#5-github-copilot)
6. [Aider](#6-aider)
7. [Continue.dev](#7-continuedev)
8. [Amp (Sourcegraph)](#8-amp)
9. [Zed AI](#9-zed-ai)
10. [其他产品](#10-其他产品)
11. [横向比较矩阵](#11-横向比较矩阵)
12. [市场趋势与差距分析](#12-市场趋势与差距分析)

---

## 1. Claude Code

**官方文档**: https://code.claude.com/docs  
**arXiv 架构论文**: https://arxiv.org/abs/2604.14228 (2026-04-17)  
**定价页**: https://code.claude.com/pricing/max

### 1.1 核心架构创新

**Agentic Loop（三阶段 while 循环）**

> "When you give Claude a task, it works through three phases: **gather context**, **take action**, and **verify results**. These phases blend together."
> — [code.claude.com/docs/en/how-claude-code-works](https://code.claude.com/docs/en/how-claude-code-works)

> "The core of the system is a simple while-loop that calls the model, runs tools, and repeats. Most of the code, however, lives in the systems around this loop: a permission system with seven modes and an ML-based classifier, a five-layer compaction pipeline for context management, four extensibility mechanisms (MCP, plugins, skills, and hooks), a subagent delegation and orchestration mechanism, and append-oriented session storage."
> — [arXiv 2604.14228](https://arxiv.org/html/2604.14228v1)

**7 个功能组件（论文分析）**:
用户 → 接口层 → Agent Loop → 权限系统 → 工具层 → 状态/持久化 → 执行环境

**Permission System（7 种模式 + ML 分类器）**:

| 模式 | 无需确认的操作 | 适用场景 |
|------|--------------|---------|
| `default` | 只读 | 敏感工作 |
| `acceptEdits` | 读 + 文件编辑 + 常见文件系统命令 | 迭代代码 |
| `plan` | 只读 | 探索代码库 |
| `auto` | 全部（背景 ML 分类器把关） | 长任务、减少确认疲劳 |
| `dontAsk` | 仅预批准工具 | CI/CD 锁定环境 |

> "Auto mode's Classifier Architecture: A two-stage classifier evaluates each tool call before execution, automatically approving safe operations and blocking risky ones."
> — [agentpatterns.ai/tools/claude/auto-mode](https://agentpatterns.ai/tools/claude/auto-mode/)

**5 层 Context Compaction Pipeline**:

```
Level 1: Tool Result Budget (50K char → disk + 2KB preview, 零成本)
Level 2: History Snip (feature-gated token release, 零成本)
Level 3: Microcompact (dual path: time-based OR cache-edit, 零成本)
Level 4: Context Collapse (projection-based folding ~90%, 零成本, 非破坏性)
Level 5: Autocompact (fork child agent 做完整摘要, 一次 API 调用, 不可逆)
```

> "Most conversations never reach Level 5. That's the point."
> — [harrisonsec.com - Claude Code Context Engineering](https://harrisonsec.com/blog/claude-code-context-engineering-compression-pipeline/)

### 1.2 Memory/Context 持久化

**双重记忆系统**:

| | CLAUDE.md | Auto Memory |
|--|--|--|
| 写入者 | 用户 | Claude 自动 |
| 加载时机 | 每次 session 开始 | 每次 session 开始（前 200 行或 25KB） |
| 适用场景 | 主动设定行为规则 | Claude 从纠正中学习 |

> "CLAUDE.md files are markdown files that give Claude persistent instructions for a project, your personal workflow, or your organization."
> — [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)

**CLAUDE.md 层级**:
- `~/.claude/CLAUDE.md` — 用户全局
- `<project>/.claude/CLAUDE.md` — 项目级
- `<project>/.claude/rules/*.md` — 规则文件（免于 compaction）
- Enterprise managed policy — 不可被用户覆盖

**Session 存储**:
> "Claude Code saves your conversation locally as you work. Each message, tool use, and result is written to a plaintext JSONL file under `~/.claude/projects/`"
> — 官方文档

**已知 Memory 缺陷**（来自 GitHub Issues）:

> "After context compaction triggers, Claude loses critical information from CLAUDE.md and MEMORY.md files. Rules like 'NEVER push to main branch' (production ERP) or 'NEVER overwrite production config' get forgotten."
> — [GitHub Issue #28469](https://github.com/anthropics/claude-code/issues/28469) (February 2026)

> "MEMORY.md is never loaded into the model's system prompt — model has no instruction to check it"
> — [GitHub Issue #25318](https://github.com/anthropics/claude-code/issues/25318)

### 1.3 Multi-agent / 并行支持

**Subagents（子代理）**:
> "Subagents are specialized AI assistants that handle specific types of tasks. Use one when a side task would flood your main conversation with search results, logs, or file contents you won't reference again."
> — [code.claude.com/docs/en/subagents](https://code.claude.com/docs/en/subagents)

内置子代理: Explore, Plan, 通用

**Agent Teams（2026 年新特性）**:

> "Agent Teams are architecturally different from subagents. Instead of lightweight workers reporting to a parent, you get full Claude Code sessions with their own context windows, a shared task board, and direct peer-to-peer messaging."
> — [charlesjones.dev - Agent Teams vs Subagents](https://charlesjones.dev/blog/claude-code-agent-teams-vs-subagents-parallel-development)

> "Anthropic shipped Agent Teams in Claude Code 2.1.32... Anthropic proved the concept by having 16 parallel Opus 4.6 instances build a 100,000-line C compiler in Rust over two days."
> — aifreeapi.com (March 2026)

| 维度 | Subagents | Agent Teams |
|------|-----------|-------------|
| 通信方式 | 只向父代理汇报 | 直接 peer-to-peer 消息 |
| 上下文 | 独立窗口，结果摘要返回 | 独立窗口，完全独立 |
| 协调方式 | 父代理全权管理 | 通过共享任务列表自协调 |
| Token 成本 | 低（结果摘要） | 高（每个 teammate 是完整实例） |

### 1.4 个性化/可定制深度

**4 种扩展机制**:

> "Extensions plug into different parts of the agentic loop: CLAUDE.md adds persistent context, Skills add reusable knowledge and invocable workflows, MCP connects Claude to external services, Subagents run their own loops, Agent teams coordinate multiple sessions, Hooks run outside the loop as deterministic scripts."
> — [docs.anthropic.com/en/docs/claude-code/features-overview](https://docs.anthropic.com/en/docs/claude-code/features-overview)

**Hooks 系统**（事件驱动自动化）:

关键事件: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `StopFailure`, `InstructionsLoaded`, `SubagentStart`, `SubagentStop`

Hook 类型:
- `type: "command"` — shell 命令
- `type: "http"` — HTTP endpoint
- `type: "prompt"` — LLM 评估
- `type: "agent"` — 生成子代理做验证

> "Agent hooks (`type: 'agent'`) spawn a subagent that can use tools like Read, Grep, and Glob to verify conditions"
> — [docs.anthropic.com/en/docs/claude-code/hooks](https://docs.anthropic.com/en/docs/claude-code/hooks)

**MCP 集成**:
> "With MCP, Claude Code can read your design docs in Google Drive, update tickets in Jira, pull data from Slack, or use your own custom tooling."
> — 官方文档

**Plugins**:
> "Plugin components include skills, agents, hooks, MCP servers, LSP servers, and monitors."
> — [code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins)

### 1.5 工具生态

- 内置工具: 文件读写、shell 执行、web 搜索、代码搜索（Grep/Glob）、子代理生成
- MCP: 2300+ servers（GitHub、Slack、Jira、数据库等）
- 官方 GitHub Actions: `anthropics/claude-code-action@v1`
- IDE 支持: VS Code 扩展、JetBrains 插件

### 1.6 已知弱点

**Context Compaction 问题**（多个高赞 GitHub Issues）:

> "When a session's context grows large and is stopped, resuming it becomes impossible if the total context exceeds the model's limit. Deadlock: Session is too large to load, but must be loaded to compact."
> — [GitHub Issue #14472](https://github.com/anthropics/claude-code/issues/14472)

> "Claude Code stores all bash output in memory causing 90GB+ memory usage and crashes."
> — [GitHub Issue #11155](https://github.com/anthropics/claude-code/issues/11155)

> "Claude Code hangs indefinitely during context compaction. Orphaned process consumes excessive resources: CPU: 277%, RAM: 11.8 GB (31% of system memory), Runtime: 26+ hours until manually killed."
> — [GitHub Issue #19567](https://github.com/anthropics/claude-code/issues/19567)

**Rate Limits 争议**:
> "Claude Code has seen unprecedented growth. At the same time, we've identified policy violations like account sharing and reselling access—and advanced usage patterns like running Claude 24/7 in the background—that are impacting system capacity for all."
> — [Hacker News discussion](https://news.ycombinator.com/item?id=44598254)

**Terminal-only 局限**: 没有内置 GUI，依赖 IDE 扩展

### 1.7 定价

| 计划 | 价格 | Claude Code 使用量 |
|------|------|------------------|
| Pro | $20/月 | 包含（~10-40 prompts/5h） |
| Max 5x | $100/月 | 5x Pro |
| Max 20x | $200/月 | 20x Pro（~800 prompts） |
| Team Standard | $20/seat/月 | 不含 |
| Team Premium | $100/seat/月 | 含（5x Standard） |

来源: [code.claude.com/pricing/max](https://code.claude.com/pricing/max)

---

## 2. Cursor

**官方文档**: https://cursor.com/docs  
**定价**: https://cursor.com/docs/models-and-pricing  
**估值**: $29.3B（2025 年 11 月）

### 2.1 核心架构创新

**Composer 2（专有 MoE 模型）**:
> "Composer 2 is a frontier-level coding model and demonstrates a process for training strong coding agents. Composer is trained by reinforcement learning on diverse software engineering tasks."
> — [Cursor arXiv paper 2603.24477](https://www.arxiv.org/pdf/2603.24477)

性能规格:
- 250 tokens/秒生成速度（4x 快于 frontier 模型）
- 最多 25 次工具调用后暂停请求用户确认
- 最多 8 个并行 agents（通过 git worktrees）

**ReAct Loop 架构**:
> "Building a system like the Cursor agent goes beyond wrapping an LLM in a chat interface. Achieving autonomy requires a layered system architecture that explicitly addresses latency, context management, and safety constraints."
> — [Medium - Designing high-performance agentic systems](https://medium.com/@khayyam.h/designing-high-performance-agentic-systems-an-architectural-case-study-of-the-cursor-agent-ab624e4a0a64)

**RAG Pipeline（5 步）**:
1. **Chunking** — Tree-sitter 解析代码为 AST 节点
2. **Merkle Tree Sync** — 文件哈希 Merkle 树，只重新索引变更文件（每 5-10 分钟）
3. **Embedding** — 使用 Cursor 专有嵌入模型
4. **Vector Storage** — Turbopuffer 存储 100B+ 向量，跨 10M+ 命名空间

来源: [openagenthub.io/real-world/cursor](https://openagenthub.io/real-world/cursor/)

### 2.2 Memory/Context 持久化

**Rules 系统（4 种类型）**:

| 类型 | 位置 | 作用域 |
|------|------|-------|
| Team Rules | Dashboard | 组织全局 |
| Project Rules | `.cursor/rules/` | 每个代码库 |
| User Rules | Cursor 设置 | 用户全局 |
| AGENTS.md | 项目根目录 | 每个项目 |

优先级（低→高）: Team Rules → Project Rules → User Rules

> "Large language models don't retain memory between completions. Rules provide persistent, reusable context at the prompt level."
> — [cursor.com/docs/context/rules](https://www.cursor.com/docs/context/rules)

**Notepads（团队知识库）**:
> "Cursor Notepads are persistent markdown documents injected into AI context via @notepad-name. They solve the 'cold start' problem — the AI knows your standards, schema, and decisions without re-explanation."
> — [markaicode.com - Cursor Notepads](https://markaicode.com/cursor-notepads-team-knowledge-base-ai-context/)

Notepads vs Rules 区别:
- Rules: 自动应用于每次 AI 交互
- Notepads: 按需引用（`@notepad-name`），opt-in

**Memory 功能**（需禁用隐私模式）:
> "Memory requires disabling privacy mode, which means your code gets sent to Cursor's servers. 'Keep that in mind' syntax works but feels weird."
> — [toolstac.com](https://toolstac.com/howto/configure-cursor-ai-custom-prompts/complete-configuration-guide)

设置路径: `Settings → Privacy → Disable Privacy Mode` 然后 `Settings → Rules → Generate Memories`

**@ 符号上下文系统**:

| 命令 | 功能 |
|------|------|
| `@Files` | 引用本地源文件 |
| `@Codebase` | 跨仓库语义搜索 |
| `@Git` | Diff 和提交历史 |
| `@Terminal` | 最近终端输出 |
| `@Docs` | 外部文档 |
| `@Notepads` | 可复用命名上下文块 |

### 2.3 Multi-agent / 并行支持

**Background Agents（云代理）**:
> "Because they have access to their own virtual machine, cloud agents can build, test, and interact with the changed software. They can also use computers to control the desktop and browser."
> — [cursor.com/docs/cloud-agent](https://cursor.com/docs/cloud-agent)

工作流程:
1. 从 GitHub/GitLab 克隆仓库
2. 在独立分支上工作
3. 自主执行任务
4. Push 变更，创建 PR 供审查

访问入口: Cursor Web、Cursor Desktop、**Slack**（@cursor）、**GitHub**（PR/Issue 评论）、**Linear**、API

**Subagent 架构**:
> "Agent can spin up specialized subagents to handle research, shell commands, or browser interactions in parallel. Each subagent runs in its own context window and returns a result to the main conversation."
> — [cursor.com/help/ai-features/agent](https://cursor.com/help/ai-features/agent)

内置 subagents: Explore（并行代码库搜索）、Bash（隔离命令执行）、Browser（MCP via DOM 过滤）

### 2.4 个性化/可定制深度

**4 种 Rule 应用类型**:

| 类型 | 行为 |
|------|------|
| Always Apply | 每次 chat session |
| Apply Intelligently | Agent 根据描述决定 |
| Apply to Specific Files | 文件匹配 glob 时 |
| Apply Manually | @-mentioned 时 |

**MCP 支持**:

| 传输方式 | 执行位置 | 部署 | 用户数 |
|---------|---------|------|-------|
| `stdio` | 本地 | Cursor 管理 | 单用户 |
| `SSE` | 本地/远程 | 部署为 server | 多用户 |
| `Streamable HTTP` | 本地/远程 | 部署为 server | 多用户 |

支持协议能力: Tools, Prompts, Resources, Roots, Elicitation, Apps（交互式 UI 视图）

### 2.5 已知弱点

**代码回滚 Bug（2026 年 3 月）**:
> "The March 2026 code reversion bug – where Cursor silently undid your changes – was confirmed by the team and affected users. Root causes: 1. Agent Review conflict 2. Checkpoint restoration overwriting changes 3. Background process interference"
> — [vibecoding.app/blog/cursor-problems-2026](https://vibecoding.app/blog/cursor-problems-2026)

**定价争议**:
> "A December 2025 Reddit post titled 'Burned through my entire monthly quota in 3 hours' described a user who ran 109 requests on Claude Opus and consumed roughly $57 of API value in one evening."
> — [everydayaiblog.com - Cursor Pricing Problems](https://everydayaiblog.com/cursor-ai-pricing-20-dollar-plan-trap/)

> "One HN user reported $1,400/mo equivalent" for Cursor
> — SpectrumAI Lab (April 2026)

**大代码库限制**:
> "Cursor hits a wall around 15,000 lines when full indexing degrades."
> — [browse-ai.tools](https://www.browse-ai.tools/blog/cursor-vs-windsurf-best-ai-coding-assistant-2026)

**稳定性问题**:
> "Cursor is 100% unusable for past 3 days. Now @ version 0.46.8 (Silicon Mac)." — Jeff White
> — [Cursor Forum](https://forum.cursor.com/t/cursor-ai-agents-slow-crashing/58252)

### 2.6 定价

| 计划 | 价格 | API 额度 |
|------|------|---------|
| Pro | $20/月 | $20 |
| Pro Plus | $60/月 | $70 |
| Ultra | $200/月 | $400 |
| Teams | $40/user/月 | 共享池 |
| Enterprise | 定制 | 定制 |

Token 定价（Auto + Composer Pool）:
- 输入 + Cache Write: $1.25/1M tokens
- 输出: $6.00/1M tokens
- Cache Read: $0.25/1M tokens

来源: [cursor.com/docs/models-and-pricing](https://cursor.com/docs/models-and-pricing)

---

## 3. Windsurf (Codeium → Cognition)

**官方文档**: https://docs.windsurf.com  
**定价**: https://windsurf.com/pricing  
**收购**: Cognition AI 于 2025 年 7 月以约 $2.5 亿收购

### 3.1 核心架构创新

**Cascade 架构**:
> "Cascade is Windsurf's agentic AI assistant with Code/Chat modes, tool calling, voice input, checkpoints, real-time awareness, and linter integration. Windsurf's Cascade unlocks a new level of collaboration between human and AI."
> — [docs.windsurf.com/windsurf/cascade/cascade](https://docs.windsurf.com/windsurf/cascade/cascade)

**"Agentic Awareness" 概念**:
> "Cascade tracks all your actions—edits, commands, conversation history, clipboard, terminal commands etc —to infer intent and adapt in real-time, helping you stay in flow without repeating yourself."
> — [windsurf.ai/cascade](https://windsurf.ai/cascade)

Cascade 执行循环:
1. **Planning Module** — 将高层请求分解为序列化操作
2. **Execution** — 读文件、写代码、运行终端命令
3. **Validation** — 解析结果，自主修复错误（60% 自动修复率）

与 Cursor 的关键区别:
> "Cursor's Composer typically stops and asks 'Should I proceed?' Windsurf's Cascade defaults to more autonomous execution."
> — [morphllm.com/comparisons/windsurf-vs-cursor](https://www.morphllm.com/comparisons/windsurf-vs-cursor)

**专有模型 SWE-1.5**:
> "SWE-1.5 reimagines the entire stack — model, inference, and agent harness — as a unified system optimized for both speed and quality... runs at up to 950 tokens/second—6x faster than Haiku 4.5 and 13x faster than Sonnet 4.5"
> — [cognition.ai/blog/swe-1-5](https://cognition.ai/blog/swe-1-5)

### 3.2 Memory/Context 持久化

**Memories 功能**:
> "Cascade will autonomously generate memories to remember important context between conversations."
> — [windsurf.ai/cascade](https://windsurf.ai/cascade)

**.windsurfrules 文件**:
> "Windsurf offers its own .windsurfrules setup. Cascade reads your Windsurf rules at the start of every session and uses them throughout execution."
> — [localskills.sh/blog/windsurf-cascade-workflows](https://localskills.sh/blog/windsurf-cascade-workflows)

**RAG-based 索引**:
> "Windsurf uses a hybrid indexing approach: native AST parsing extracts symbol graphs and dependency structure, while semantic embeddings and retrieval-augmented generation (RAG) supply contextual snippets."
> — [createaiagent.net/tools/windsurf](https://createaiagent.net/tools/windsurf/)

**Supercomplete 功能**:
> "Supercomplete uses edit trajectory, cursor intent, and lightweight AST parsing — not just cursor context — to generate proactive suggestions."
> — [markaicode.com - Windsurf Supercomplete](https://markaicode.com/windsurf-supercomplete-beyond-autocomplete-ai-coding/)

### 3.3 Multi-agent / 并行支持

- 最多 5 个并行 Cascade agents（Wave 13 版本）
- Arena Mode — 两个模型并排对比
- Devin 集成（2026 年 4 月）: 本地 Windsurf 规划 → 一键发送给 Devin 执行

> "With Windsurf 2.0, you work locally in Windsurf to understand the codebase and put together a plan. With a single click, you send it to Devin for implementation. Devin spins up its own machine and gets to work."
> — [cognition.ai/blog/devin-in-windsurf](https://cognition.ai/blog/devin-in-windsurf)

**注意**: 无云端 Background Agents（不同于 Cursor）

### 3.4 个性化/可定制深度

**两种主要模式**:

| 模式 | 行为 | 适用场景 |
|------|------|---------|
| Write Mode | 自主执行，创建/修改文件 | 构建功能、重构 |
| Chat Mode | Q&A，提议代码供批准 | 学习、调试、探索 |

**自动执行级别**:

| 级别 | 行为 |
|------|------|
| Off | 从不自动执行 |
| Auto | 模型根据安全评估决定 |
| Turbo | 完全自主执行 |

### 3.5 Cognition 收购影响

**收购时间线**:

| 日期 | 事件 |
|------|------|
| 2025 年 5 月 | OpenAI 宣布 $3B 收购协议 |
| 2025 年 7 月 | OpenAI 交易告吹（微软 IP 问题） |
| 2025 年 7 月 | Google 签署 $2.4B 授权协议，招募 CEO + 研究负责人 |
| 2025 年 7 月 | Cognition 收购剩余 Windsurf 产品/IP（约 $2.5 亿） |

收购时: $82M ARR，210 名员工，企业 ARR 季度环比翻倍

> "With this acquisition, Cognition will be able to move even faster on our mission of building the future of software engineering."
> — [cognition.ai/blog/windsurf](https://cognition.ai/blog/windsurf)

**产品路线图**:
- 2026 年 Phase 2: 合并推理引擎，创建统一 AI "coding brain"
- Windsurf 现可访问最新 Claude 模型

### 3.6 已知弱点

- 公司不稳定性（三方收购混乱）
- 无云端 Background Agents
- Context window 较小（100K vs Cursor 200K）
- 企业客户对 Cognition 长期承诺存疑

### 3.7 定价

| 计划 | 价格 | 功能 |
|------|------|------|
| Free | $0 | 2,000 次补全，轻量使用 |
| Pro | $20/月 | 无限制，所有高级模型，SWE-1.5 |
| Max | $200/月 | 重度使用，优先支持 |
| Teams | $40/user/月 | 管理面板，SSO，RBAC |
| Enterprise | 定制 | 混合部署，批量折扣 |

注: 2026 年 3 月 Pro 从 $15 涨至 $20（从积分制改为配额制）

---

## 4. Devin (Cognition AI)

**官方文档**: https://docs.devin.ai  
**定价**: https://devin.ai/pricing  
**SWE-bench 技术报告**: https://www.cognition.ai/post/swe-bench-technical-report

### 4.1 核心架构创新

**完全自主云沙箱**:
> "Devin AI functions as the first fully autonomous AI software engineer. Devin AI plans high-level tasks, executes them in a sandboxed environment with shell, browser and code editor tools."
> — [aitoolranked.com/blog/devin-ai-review](https://aitoolranked.com/blog/devin-ai-review)

**专有模型**:
- **SWE-1.5**: 950 tokens/秒，6x 快于 Haiku 4.5
- **SWE-grep / SWE-grep-mini**: 专门用于高度并行上下文检索的子代理

> "We trained SWE-grep and SWE-grep-mini, fast agentic models specialized in highly parallel context retrieval... Traditional agents spend more than 60% of their first turn just retrieving context—often taking 20+ seconds before making a single edit."
> — [cognition.ai/blog/swe-grep](https://cognition.ai/blog/swe-grep)

**架构特点**:
- 每个 session 加载 VM 快照
- 完整开发工具链（shell + 代码编辑器 + 浏览器）
- 长程规划 + 子代理编排（规划/执行/验证）

### 4.2 State Management

**持久沙箱 Sessions**:
> "Devin operates by loading a snapshot of a virtual machine at the start of each session. For Devin to be most effective, this snapshot should include all the repositories you want Devin to work on, as well as any tools or dependencies Devin might need to work on your codebase."
> — [docs.devin.ai/onboard-devin/repo-setup](https://docs.devin.ai/onboard-devin/repo-setup)

**Knowledge 系统**:
> "Knowledge is a collection of tips, documentation, and instructions Devin 'knows' across all future sessions."
> — [docs.devin.ai/release-notes/2024](https://docs.devin.ai/release-notes/2024)

**交互式规划（Devin 2.0）**:
> "Devin 2.0 proactively researches your codebase and develops a detailed plan. Each time you start a session, Devin responds in seconds with relevant files, findings, and a preliminary plan."
> — [cognition.ai/blog/devin-2](https://cognition.ai/blog/devin-2)

### 4.3 Devin 2.0+ 功能（2025 年 4 月）

> "Today, we're excited to announce Devin 2.0: Spin up multiple parallel Devins, each equipped with its own interactive, cloud-based IDE. Collaborate with Devin. Review and edit Devin's work easily within the Devin IDE itself."
> — [cognition.ai/blog/devin-2](https://cognition.ai/blog/devin-2)

**新功能**:
- **Interactive Planning**: 主动研究代码库，秒级生成计划
- **Devin Search**: 带引用的代码库问答
- **Devin Wiki**: 自动索引仓库，生成架构图
- **并行 Sessions**: "Managed Devins" 并行工作

**Managed Devins（并行代理）**:
> "Starting today, Devin can break down large tasks and delegate them to a team of managed Devins that work in parallel. Each managed Devin is a full Devin, running in its own isolated virtual machine with its own terminal, browser, and development environment."
> — [cognition.ai/blog/devin-can-now-manage-devins](https://cognition.ai/blog/devin-can-now-manage-devins)

**Confidence Scores（Devin 2.1）**:
> "Devin now reports its confidence that it can complete tasks using 🟢 🟡 🔴... We've found that Confidence Scores are highly correlated with task success, with 🟢 scores resulting in twice the likelihood of a merged PR compared to 🔴."
> — [cognition.ai/blog/devin-2-1](https://cognition.ai/blog/devin-2-1)

### 4.4 实际性能 vs 营销

**SWE-bench 基准**:
> "Devin successfully resolved 79 of the 570 issues, giving a 13.86% success rate. This is significantly higher than the previous best assisted system (Claude 2) of 4.80%."
> — [cognition-labs.com/blog/swe-bench-technical-report](https://www.cognition-labs.com/blog/swe-bench-technical-report)

⚠️ 重要背景: 这是 2024 年数据。Claude Code (Opus 4.6) 2026 年已达 80.8%，Devin 未更新基准测试。

**PR 合并率改善**:
> "Over the past year, Devin has become a faster and better junior engineer - it's 4x faster at problem solving and 2x more efficient in resource consumption, and 67% of its PRs are now merged vs 34% last year."
> — [cognition.ai/blog/devin-annual-performance-review-2025](https://cognition.ai/blog/devin-annual-performance-review-2025)

**独立评估（Answer.AI，2025 年 1 月）**:
> "Out of 20 tasks, we had 14 failures, 3 successes (including our 2 initial ones), and 3 inconclusive results."
> — [answer.ai/posts/2025-01-08-devin](https://answer.ai/posts/2025-01-08-devin)

### 4.5 企业功能

- VPC 部署: 在客户 VPC 内托管 Devin VM
- SSO: Okta, Entra (Azure AD), SAML, OIDC
- 不用客户代码训练模型
- 企业客户: Goldman Sachs、Santander、Nubank、Infosys、Cognizant

> "Goldman Sachs just hired Devin... The company also has plans to potentially unleash it by the thousands and expand workers' productivity with AI tools by over four times."
> — [Fortune, July 2025](https://fortune.com/2025/07/14/goldman-sachs-ai-powered-software-engineer-devin-new-employee-increase-productivity-fears-of-job-replacement/)

### 4.6 已知弱点

> "Complex tasks fail roughly 85% of the time without human intervention."
> — [awesomeagents.ai/reviews/review-devin](https://awesomeagents.ai/reviews/review-devin/)

> "Devin does not reliably flag when it is uncertain or when a proposed action carries high risk."
> — [openaitoolshub.org - Devin AI Review](https://openaitoolshub.org/en/blog/devin-ai-review)

> "Because Devin operates asynchronously as a remote agent, the feedback loop is slower than IDE tools like Cursor or Claude Code."
> — 同上

> "ACU consumption varies wildly by task. A 'simple' refactor that requires reading 20 files can burn through ACUs faster than a complex but well-scoped bug fix."
> — [toolhalla.ai](https://toolhalla.ai/blog/devin-vs-openhands-vs-swe-agent-2026)

> "You can't swap in Claude 4 or GPT-5 when they outperform Devin's model. You're stuck with Cognition's proprietary models."
> — 同上

Trustpilot 评分: 3.0/5（截至 2026 年 3 月）

### 4.7 定价

| 计划 | 价格 | 包含 ACUs | 额外 ACU 成本 |
|------|------|----------|-------------|
| Core | $20/月（按需付费） | 有限 | $2.25/ACU |
| Team | $500/月 | 250 ACUs | $2.00/ACU |
| Enterprise | 定制 | 定制 | 定制 |

注: 原价 $500/月，2026 年 1 月迫于市场压力推出 $20 Core 计划

---

## 5. GitHub Copilot

**官方文档**: https://docs.github.com/copilot  
**定价**: https://github.com/features/copilot/plans  
**用户数**: 20M+，4.7M 付费用户

### 5.1 核心架构

**三种模式分工**:

| 模式 | 本质 | 特点 |
|------|------|------|
| Code Completion | 自动补全 | 内联建议，最低自主性 |
| Agent Mode | 同步协作代理 | 多步骤执行，自动应用编辑 |
| Cloud Agent | 异步自主代理 | 后台工作，创建 PR |

> "Agent mode is a mode where Copilot is capable of iterating on its own code, recognizing errors, and fixing them automatically."
> — [github.blog/ai-and-ml/github-copilot/agent-mode-101](https://github.blog/ai-and-ml/github-copilot/agent-mode-101-all-about-github-copilots-powerful-mode/)

**Agent Mode 工作原理**:
> "When you send a natural-language prompt to Copilot agent mode, it's augmented by our backend system prompt. Agent mode works as an orchestrator of several different tools and variables."
> — 同上

**模型支持**:
> "Agent mode is powered by your choice of Claude 3.5 and 3.7 Sonnet, Google Gemini 2.0 Flash, and OpenAI GPT-4o."
> — [github.blog - Agent Mode Activated](https://github.blog/news-insights/product-news/github-copilot-agent-mode-activated)

**SWE-bench 性能**:
> "Currently, agent mode achieves a pass rate of 56.0% on SWE-bench Verified with Claude 3.7 Sonnet."
> — 同上

### 5.2 Copilot Workspace（已停止技术预览）

> "GitHub Copilot Workspace is a Copilot-native development environment designed to help you with everyday tasks, from idea to implementation."
> — [github.blog - Copilot Workspace](https://github.blog/news-insights/product-news/github-copilot-workspace/)

**任务流**: 任务 → 规格 → 计划 → 实现

⚠️ 重要: **技术预览于 2025 年 5 月 30 日结束**，功能已整合进 Agent Mode

### 5.3 Memory/Context 持久化

**Repository Indexing**:
> "When you add #codebase to your Copilot Chat query, Copilot leverages advanced code search to find relevant context across your repository."
> — 官方文档

**Semantic Code Search（2025 年 3 月）**:
> "Copilot coding agent works faster with semantic code search"
> — [github.blog/changelog/2025-03-17](https://github.blog/changelog/2025-03-17-copilot-coding-agent-works-faster-with-semantic-code-search/)

**Virtual Tool Groups（2025 年 11 月）**:
核心工具集精简为 13 个，其余分组为: Jupyter Notebook Tools、Web Interaction Tools、VS Code Workspace Tools、Testing Tools

无跨 session 记忆机制（最大弱点之一）

### 5.4 Multi-agent / 并行支持

- Custom Agents（自定义角色）
- Cloud Agent 可异步工作
- 无 Claude Code 级别的 Agent Teams

**GitHub Actions 集成**:
> "You can assign Copilot cloud agent to straightforward issues on your backlog by selecting 'Copilot' as the assignee in GitHub Issues."
> — [docs.github.com - About Copilot cloud agent](https://docs.github.com/en/enterprise-cloud@latest/copilot/concepts/coding-agent/about-copilot-coding-agent)

**自定义 CI 环境**:
> "You can customize Copilot's environment by creating a special GitHub Actions workflow file, located at `.github/copilot/setup-steps.yml`."
> — 官方文档

### 5.5 MCP 生态

> "Model Context Protocol (MCP) is a protocol that allows you to extend the capabilities of GitHub Copilot by integrating with a wide range of existing tools and services."
> — [docs.github.com - About MCP](https://docs.github.com/en/copilot/how-tos/use-copilot-extensions)

内置 MCP Servers: GitHub（内置）、Sentry、Notion、Azure、Cloudflare、Azure DevOps、Atlassian (Jira/Confluence)

**MCP Registry**: GitHub 维护的 MCP server 策划列表

### 5.6 已知弱点

- 无跨 session 持久记忆
- Agent Mode 仍需监督（vs Claude Code 的完全自主）
- Premium request 限制 + $0.04/超额
- 被批评为"自动补全升级版"而非真正 agent
- Context window 128K（最小）

> "Copilot's agent is useful for bounded tasks; Claude Code handles the unbounded ones."
> — [devtoolsreview.com](https://devtoolsreview.com/comparisons/copilot-vs-claude-code-2026)

### 5.7 定价

| 计划 | 价格 | Premium 请求 |
|------|------|-------------|
| Free | $0 | 2,000 次补全/月，50 次 |
| Pro | $10/月 | 无限补全，300 次/月 |
| Pro+ | $39/月 | 1,500 次/月，所有模型 |
| Business | $19/user/月 | 300 次/user/月，SSO |
| Enterprise | $39/user/月 | 1,000 次/user/月 |

注: 2025 年将个人计划从 $19/月降至 $10/月

---

## 6. Aider

**官方网站**: https://aider.chat  
**GitHub**: https://github.com/Aider-AI/aider（42K stars）  
**许可**: 开源（免费）

### 6.1 核心架构创新

**终端 + Git 深度集成**:
> "Aider is AI pair programming in your terminal. Aider lets you pair program with LLMs to start a new project or build on your existing codebase."
> — [aider.chat](https://aider.chat/)

**Architect + Editor 双模型模式**:
- Architect 模型负责高层架构/规划
- Editor 模型负责具体代码编辑
- 可以用不同 LLM 分别承担两个角色

### 6.2 REPOMAP 上下文系统

> "Aider uses a **concise map of your whole git repository** that includes the most important classes and functions along with their types and call signatures. This helps aider understand the code it's editing and how it relates to the other parts of the codebase."
> — [aider.chat/docs/repomap.html](https://aider.chat/docs/repomap.html)

> "Aider sends a **repo map** to the LLM along with each change request from the user. The repo map contains a list of the files in the repo, along with the key symbols which are defined in each file."
> — 同上

- 使用图排名算法优化 repo map
- 根据 token 预算选择最重要的代码库部分
- `--map-tokens` 参数控制（默认 1k tokens）

### 6.3 模型无关性

> "Aider works best with Claude 3.7 Sonnet, DeepSeek R1 & Chat V3, OpenAI o1, o3-mini & GPT-4o, but can connect to almost any LLM."
> — [aider.chat](https://aider.chat/)

支持: OpenAI、Anthropic、Gemini、DeepSeek、Ollama 及更多

### 6.4 独特功能

- **语音编程**: 语音输入请求，Aider 自动编辑代码
- **图像支持**: 添加截图、参考文档等视觉上下文
- **Linting 集成**: `/lint` 命令
- **LLM 排行榜**: 发布代码编辑能力基准测试

### 6.5 定价

完全开源免费，只需支付 LLM API 费用

### 6.6 已知弱点

- 纯终端界面（无 GUI）
- 需手动管理上下文文件
- 无内置编辑器
- 无云端代理/后台任务功能

---

## 7. Continue.dev

**官方文档**: https://docs.continue.dev  
**许可**: 开源（Apache 2.0）

### 7.1 核心架构

VS Code 和 JetBrains 扩展，提供 4 核心功能:
- **Autocomplete**: 内联代码建议
- **Edit**: AI 快速修改
- **Chat**: IDE 侧边栏对话
- **Agent Mode**: 自主编码助手（读文件、改代码、运行命令）

> "Agent Mode equips the Chat model with the tools needed to handle a wide range of coding tasks"
> — [docs.continue.dev](https://docs.continue.dev/ide-extensions/quick-start)

### 7.2 Context Providers

使用 `@` 符号引用上下文:
- `@Files` — 引用特定文件
- `@Terminal` — 包含终端输出
- `@Codebase` — 代码库搜索
- 可扩展的 context provider 系统

### 7.3 模型灵活性

> "Use any model, including GPT-4, DeepSeek Coder, Claude 2, Code LLama, Gemini Pro, and more"
> "Deploy locally (Ollama, LM Studio, etc), in your cloud (vLLM, TGI, etc), or with SaaS (Together, OpenAI API, etc)"
> — [s3.continue.dev](https://s3.continue.dev/)

### 7.4 定价

- 核心扩展: 免费开源
- Mission Control 云服务: 团队功能（定价未公开）

### 7.5 已知弱点

- 自主性低于专用 agent（需更多手动引导）
- 无内置长任务能力
- Context providers 需要配置

---

## 8. Amp (Sourcegraph)

**官方网站**: https://ampcode.com  
**前身**: Sourcegraph Cody  
**重大变化**: 2026 年 3 月 5 日停止 VS Code/Cursor 扩展，转为纯 CLI

### 8.1 核心架构创新

**"Coding Agent Is Dead" 转型**:
> "The Coding Agent Is Dead — We're killing the Amp editor extension to step into the future."
> — [ampcode.com/news/the-coding-agent-is-dead](https://ampcode.com/news/the-coding-agent-is-dead)

**多模型编排**（最大差异化）:

> "**Multi-Model:** Opus 4.6, GPT-5.4, fast models—Amp uses them all, for what each model is best at."
> — [ampcode.com](https://ampcode.com/)

**三种 Agent 模式**:
- `smart` — 无约束的最先进模型使用（Claude Opus 4.6）
- `rush` — 更快、更便宜，适合小型明确任务
- `deep` — GPT-5.4 深度推理，适合复杂问题

### 8.2 Context / Sourcegraph 集成

**Librarian 子代理**（独特功能）:
> "Amp can search remote codebases with the use of the Librarian subagent. The Librarian can search and read all public code on GitHub as well as your private GitHub repositories."
> — [ampcode.com/manual](https://ampcode.com/manual)

**Oracle**: 调用 GPT-5.4 作为"第二意见"  
**Painter**: 通过 Gemini 3 Pro Image 生成图像

### 8.3 定价

> "Pay as you go, with no markup for individuals."
> — [ampcode.com](https://ampcode.com/)

- 免费层: $10/天积分（广告支持）
- 付费: 按量付费，无溢价

### 8.4 已知弱点

- 2026 年 3 月后纯 CLI（学习曲线陡峭）
- 无可视化编辑器集成
- Windows 需要 WSL
- 快速演进中，"无向后兼容"

---

## 9. Zed AI

**官方网站**: https://zed.dev  
**架构**: Rust 原生 + GPU 加速

### 9.1 核心架构创新

> "Zed is a free, open-source, high-performance code editor written in Rust. It's built from the ground up with GPU acceleration and designed for collaboration and AI-driven development."
> — [graphite.dev/guides/zed-editor](https://graphite.dev/guides/zed-editor-next-gen-vs-code-alternative)

**性能优势**:
> "Pure performance — Zed is not Electron. It's a native app with GPU-accelerated rendering. On large files (10,000+ lines), Zed is significantly faster than VS Code-based editors."
> — [devplaybook.cc](https://devplaybook.cc/blog/vscode-vs-cursor-vs-zed-ai-editor-comparison-2024)

**实时协作**（独特功能）:
> "Zed has first-class multiplayer built in. Not a screen share — actual real-time collaborative editing with presence indicators, like Google Docs for code."
> — 同上

### 9.2 AI 功能现状

> "Zed's AI approach is refreshingly honest — it supports multiple providers including OpenAI, Anthropic, and local models."
> — [toolstac.com](https://toolstac.com/compare/visual-studio-code/zed/cursor/ai-editor-comparison-2025)

⚠️ 局限:
> "Zed AI currently focuses on an AI panel for chat and inline editing assistance. It does not yet have an equivalent to Cursor Composer."
> — [f22labs.com](https://www.f22labs.com/blogs/zed-vs-cursor-ai-the-ultimate-2025-comparison-guide/)

### 9.3 定价

- 个人使用: 免费
- Zed Channels 协作功能: 付费

### 9.4 已知弱点

> "Zed's extension ecosystem is small. If your workflow depends on specific VS Code extensions, Zed may not work for you."
> — [devplaybook.cc](https://devplaybook.cc/blog/vscode-vs-cursor-vs-zed-ai-editor-comparison-2024)

> "AI features less capable than Cursor (no codebase indexing, no Composer)"
> — 同上

> "Windows support is still in development as of late 2025"
> — [toolstac.com](https://toolstac.com/compare/visual-studio-code/zed/cursor/ai-editor-comparison-2025)

---

## 10. 其他产品

### Bolt.new (StackBlitz)

**网站**: https://bolt.new  
**核心差异**: 浏览器内完整开发环境，零本地安装

> "Bolt.new is an AI-powered web development agent that allows you to prompt, run, edit, and deploy full-stack applications directly from your browser—no local setup required."
> — [github.com/stackblitz/bolt.new](https://github.com/stackblitz/bolt.new)

使用 WebContainers 技术（浏览器内 Node.js 运行时）

**定价**: 免费层（每日 token 限制）+ $20/月

### v0.dev (Vercel) → v0.app

**网站**: https://v0.dev  
**2026 年演进**: 从 UI 生成工具 → 完整 coding agent

> "v0 is an AI-powered development platform that turns ideas into production-ready, full-stack web apps."
> — [v0.dev/faq](https://v0.dev/faq)

新增: Git 集成、完整编辑器（VS Code 风格）、数据库连接、自主调试

**定价**: Free ($5 积分/月) → Premium ($20/月) → Pro ($30/月)

### Replit Agent

**当前版本**: Agent 4（2026 年 3 月）  
**特点**: 200 分钟自主 sessions，子代理生成，可视化 Design Canvas

> "Replit's annualized revenue rose to $150 million from $2.8 million in less than a year"
> — [replstack.com](https://replstack.com/blog/how-to-use-replit-agent-3)

**定价**: Starter (免费) → Core ($20/月) → Teams ($100/月)

---

## 11. 横向比较矩阵

### 11.1 核心维度对比

| 产品 | 架构类型 | Context Window | SWE-bench | 定价起点 | 公司状态 |
|------|---------|---------------|-----------|---------|---------|
| **Claude Code** | 终端 agent | 1M tokens | 80.8% | $20/月 | 独立（Anthropic）|
| **Cursor** | AI-native IDE | 200K tokens | N/A（专有）| $20/月 | 独立，$29.3B 估值 |
| **Windsurf** | AI-native IDE | 100K tokens | N/A | $20/月 | Cognition 旗下 |
| **Devin** | 云沙箱 agent | ~200K | 13.86%（2024）| $20/月 | Cognition 旗下 |
| **GitHub Copilot** | IDE 扩展 | 128K tokens | 56% | $10/月 | GitHub/Microsoft |
| **Aider** | 终端 | 模型决定 | 发布排行榜 | 免费 | 开源 |
| **Continue.dev** | IDE 扩展 | 模型决定 | N/A | 免费 | 开源 |
| **Amp** | 终端 CLI | 模型决定 | N/A | 按量付费 | Sourcegraph |
| **Zed AI** | 原生编辑器 | 模型决定 | N/A | 免费 | 独立 |

### 11.2 Memory/Context 持久化对比

| 产品 | 跨 session 记忆 | 项目级指令 | 自动学习 | 代码库索引 |
|------|---------------|----------|---------|---------|
| Claude Code | CLAUDE.md + Auto Memory（MEMORY.md）| ✅ 多层级 | ✅ | 按需文件读取 |
| Cursor | Rules (.cursor/rules/) + Notepads | ✅ 4 种类型 | ✅（需禁隐私模式）| ✅ RAG + Merkle Tree |
| Windsurf | .windsurfrules + Memories | ✅ | ✅ 自动 | ✅ RAG + AST |
| Devin | Knowledge 系统 + VM 快照 | ✅ | 有限 | ✅ Devin Wiki |
| GitHub Copilot | ❌ 无 | 有限 | ❌ | ✅ 语义搜索 |
| Aider | ❌ | ❌（需手动加文件）| ❌ | REPOMAP（图算法）|
| Continue.dev | ❌ | 有限 | ❌ | ✅ context providers |
| Amp | ❌ | ❌ | ❌ | ✅ Librarian（GitHub）|

### 11.3 Multi-agent 并行支持

| 产品 | 并行 agent | 通信方式 | 云端 agent | 最大并行数 |
|------|-----------|---------|----------|---------|
| Claude Code | ✅ Agent Teams | Peer-to-peer | ❌（本地）| 理论无限 |
| Cursor | ✅ Background Agents | 独立 VM | ✅ | 8（git worktrees）|
| Windsurf | ✅ 有限 | 独立 Cascade | ❌ | 5 |
| Devin | ✅ Managed Devins | 独立 VM | ✅ | 10（Core）|
| GitHub Copilot | 有限 | N/A | ✅（有限）| 未公开 |

### 11.4 自主性谱系

```
完全监督 ←————————————————————————————→ 完全自主
  │                                           │
Copilot    Continue    Aider    Cursor    Claude Code    Windsurf    Devin
(补全)     (扩展)      (终端)   (guardrails) (supervise)  (autonomous) (fire-and-forget)
```

### 11.5 定价对比（2026 年 4 月）

| 产品 | 入门价 | Power User | 企业 | 计费方式 |
|------|-------|-----------|------|---------|
| Claude Code | $20/月 | $200/月 | $100/seat/月 | 固定层级 |
| Cursor | $20/月 | $200/月 | 定制 | 固定 + 计算超额 |
| Windsurf | $20/月 | $200/月 | $40/user/月 | 配额制 |
| Devin | $20/月 | $500/月 | 定制 | ACU 计量 |
| GitHub Copilot | $10/月 | $39/月 | $39/user/月 | 固定 + premium 请求 |
| Aider | 免费 | 免费 | 免费 | 只付 API 费 |
| Amp | 免费起 | 按量付费 | N/A | 按量付费 |

---

## 12. 市场趋势与差距分析

### 12.1 市场格局（2026 年）

**规模**:
- 全球 AI 编程助手市场: $8.5B（2026），预计 2030 年达 $52.62B（CAGR 46.3%）
- 85% 开发者定期使用 AI 编程工具
- 90% 财富 100 强公司使用 AI 编程工具

来源: MachineLearningMastery (January 2026), JetBrains State of Developer Ecosystem 2025

**市场份额**（Pragmatic Engineer 调研，906 名开发者）:
- Claude Code: **46%**（从零到第一，8 个月内）
- GitHub Copilot: **~42%**（付费工具中）
- Cursor: 估值 $29.3B，ARR $500M+

**收入里程碑**:
- Claude Code: 6 个月内达 $1B 年化收入
- Cursor: 破 $100M ARR（史上最快）
- Replit: 年化收入从 $2.8M 飙升至 $150M

来源: Effloow (April 2026), Agents Squads (March 2026)

### 12.2 架构趋势：收敛 vs 分化

**收敛点**（所有工具都在做）:
- MCP 集成（事实标准）
- Agentic loops（多步骤自主执行）
- Rules/config 文件（.claude/rules/, .cursor/rules/, AGENTS.md）
- Context compaction/压缩

**真正的差异化维度**:

| 维度 | 差异化程度 | 领先者 |
|------|-----------|-------|
| 上下文窗口大小 | 高 | Claude Code（1M） |
| 代码库索引方式 | 中 | Cursor（RAG+Merkle）|
| 自主性程度 | 高 | Devin（完全自主）|
| 多模型支持 | 高 | Cursor/Amp |
| 云端 agent | 中 | Cursor/Devin |
| 实时协作 | 高 | Zed（唯一）|
| 模型无关性 | 高 | Aider/Continue/Amp |

> "The seven tools in this post all qualify as real agents, though some clear it more cleanly than others. Cursor 3 and Claude Code are the strongest autonomous executors."
> — RawPickAI (April 2026)

### 12.3 最大共同痛点（用户真实反馈）

**1. 跨 session 记忆丢失**（最高频投诉）:
> "Claude Code loses context without any warning, creating a severely disruptive experience especially for non-developer 'Vibe Coding' users who depend entirely on Claude's contextual memory for project continuity."
> — [GitHub Issue #13171](https://github.com/anthropics/claude-code/issues/13171) (December 2025, marked "not_planned")

> "I'm Opus 4.5 right now, but I'm not always the one responding in your sessions. There are multiple Claude models - Haiku, Sonnet, Opus - and the system can switch without telling you."
> — GitHub Issue #20158

**2. Context Compaction 破坏指令遵循**:
> "After context compaction triggers, Claude loses critical information from CLAUDE.md and MEMORY.md files. Rules like 'NEVER push to main branch' get forgotten."
> — [GitHub Issue #28469](https://github.com/anthropics/claude-code/issues/28469)

> "Compaction is the biggest weak-point as of current. The current implementation is suboptimal in many regards. It wastes a huge amount of tokens re-auditing, and then when you get 'caught up' to the actual task, you've already burned through half the context window just to proceed."
> — GitHub Issue #11315 评论者

**3. 上下文窗口"虚标"**:
> "The context window is a lie. What's actually usable is much smaller once you account for system prompts, conversation history, and tool outputs."
> — Reddit 用户（广泛引用）

有效上下文 vs 标称对比（Zylos Research, January 2026）:
- Claude Code: 标称 1M，有效 ~500K-800K
- Cursor: 标称 200K，有效 ~70K-150K
- Devin: 标称 200K，有效 ~100K

**4. 定价不可预测**:
> "Four AI coding tools. Four different pricing models. The pricing page says $10-20/mo for all of them. The reality ranges from $10 to $1,400 depending on which one you pick and how heavily you use it."
> — SpectrumAI Lab (April 2026)

### 12.4 MCP 生态成熟度

**采用状况**:
- 2300+ MCP servers（公共目录）
- 97M+ 月 SDK 下载量
- 28% 财富 500 强已部署 MCP
- 2025 年 12 月: Anthropic 将 MCP 捐赠给 Linux Foundation

> "Over 2,300+ MCP servers in public directories... 97 million+ MCP SDK downloads per month"
> — BuildFastWithAI (April 2026)

**治理**: Linux Foundation 旗下 Agentic AI Foundation，Block + OpenAI 共同创立，Google/Microsoft/AWS/Cloudflare 支持

**2026 MCP 路线图优先级**:
1. Transport 可扩展性（HTTP/SSE 优化）
2. Agent-to-Agent 通信
3. 企业治理成熟
4. 安全实践追赶快速采用

### 12.5 第三方记忆解决方案涌现（行业空白信号）

由于所有主流工具的记忆系统都不完善，大量第三方方案出现:
- **MemNexus**: 跨 sessions、跨 Boomerang chains、跨项目的持久记忆
- **ContextStream**: 跨 Cursor/Claude/任何 MCP 工具
- **OMEGA**: 跨模型本地优先记忆
- **Beam**: Claude Code 专用记忆管理
- **claude-mem**: 开源，自动捕获编程 session，AI 压缩，注入未来 session

这些工具的涌现说明: **跨 session 持久记忆是整个行业尚未解决的核心问题**。

### 12.6 2026 年趋势预测

**已发生**:
- 2026 年 2 月: 所有主要玩家在两周内同时发布 multi-agent 功能
- Multi-agent 从实验性变为标配
- $20/月 成为新的入门价格标准

**正在发生**:
- Computer use 集成（GUI 控制）
- Voice coding 兴起
- IDE-first vs CLI-first 市场分化加速

**预测（来源: Agents Squads, March 2026）**:
1. "OpenCode reaches 1M users"
2. "Context compression becomes standard feature (not differentiator)"
3. "At least one major framework pivots to enterprise (CrewAI, AutoGen)"
4. "60% of new code will be AI-generated by end of 2026"
5. "40% of enterprise applications will include task-specific AI agents by year's end"

> "The agent landscape will consolidate. Expect: Fewer, more capable agents. The 'thousand flowers blooming' phase is ending. Winners will absorb losers."
> — Neosignal (January 2026)

> "Specialized beats general. The best coding agent won't be the best research agent. Specialization compounds."
> — 同上

---

## 附录：主要来源索引

### 官方文档
- Claude Code: https://code.claude.com/docs
- Claude Code Hooks: https://docs.anthropic.com/en/docs/claude-code/hooks
- Cursor Docs: https://cursor.com/docs
- Windsurf Docs: https://docs.windsurf.com
- Devin Docs: https://docs.devin.ai
- GitHub Copilot: https://docs.github.com/copilot
- Aider: https://aider.chat/docs
- Continue.dev: https://docs.continue.dev
- Amp: https://ampcode.com/manual

### 架构分析
- arXiv 2604.14228 (Claude Code 架构论文): https://arxiv.org/abs/2604.14228
- arXiv 2603.24477 (Cursor Composer 2 论文): https://www.arxiv.org/pdf/2603.24477
- OpenAgentHub Cursor 架构: https://openagenthub.io/real-world/cursor/
- HarrisonSec Claude Code Context Engineering: https://harrisonsec.com/blog/claude-code-context-engineering-compression-pipeline/

### 独立评测
- Answer.AI Devin 月度测试: https://answer.ai/posts/2025-01-08-devin
- VibeCoding Cursor Problems 2026: https://vibecoding.app/blog/cursor-problems-2026
- Paperclipped AI Coding Assistants 2026: https://www.paperclipped.de/en/blog/ai-coding-assistants-compared-2026/
- Toolhalla Devin vs OpenHands: https://toolhalla.ai/blog/devin-vs-openhands-vs-swe-agent-2026

### 市场分析
- Agents Squads March 2026: https://agentssquads.com (March 2026)
- Effloow April 2026: https://effloow.com (April 2026)
- SpectrumAI Lab Pricing: https://spectrumai.lab (April 2026)
- MorphLLM Windsurf vs Cursor: https://www.morphllm.com/comparisons/windsurf-vs-cursor

### 收购/商业新闻
- Cognition 收购 Windsurf: https://cognition.ai/blog/windsurf
- Cognition Devin in Windsurf: https://cognition.ai/blog/devin-in-windsurf
- TechCrunch Windsurf 收购: https://techcrunch.com/2025/07/14/cognition-maker-of-the-ai-coding-agent-devin-acquires-windsurf/
- Fortune Goldman Sachs Devin: https://fortune.com/2025/07/14/goldman-sachs-ai-powered-software-engineer-devin

### GitHub Issues（真实用户问题）
- Claude Code #14472（context 死锁）: https://github.com/anthropics/claude-code/issues/14472
- Claude Code #11155（内存 90GB+）: https://github.com/anthropics/claude-code/issues/11155
- Claude Code #28469（compaction 遗忘规则）: https://github.com/anthropics/claude-code/issues/28469
- Claude Code #25318（MEMORY.md 未加载）: https://github.com/anthropics/claude-code/issues/25318
- Claude Code #13171（记忆丢失）: https://github.com/anthropics/claude-code/issues/13171

---

*报告生成时间: 2026-04-20 | 调研方法: 5 个并行 sub-agent 交叉验证 | 覆盖 9 个产品 + 3 个补充产品*

