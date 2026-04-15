# AGENTS.md - Your Workspace

> **First time here?** Start with `setup_guide.md` — it'll walk you through setup in under an hour.

This folder is home. Treat it that way.

## Every Session

Before doing anything else:

1. Read `rules/SOUL.md` — this is who you are
2. Read `rules/USER.md` — this is who you're helping
3. Read `rules/WORKSPACE.md` — file routing table, check before searching for files
4. Read `rules/COMMUNICATION.md` — how to think and communicate (especially for non-coding tasks)
5. Read `rules/skills/INDEX.md` — understand available skills

Don't ask permission. Just do it. Do not skip this step.

## File Routing

**找文件时，先查 `rules/WORKSPACE.md`，再搜索。** WORKSPACE.md 是这个 workspace 的目录索引，记录了每类内容的存放位置。绝大多数情况下查一下就能定位到目标目录，不需要全盘 glob/grep。如果发现新目录或项目没被收录，顺手更新 WORKSPACE.md。

## Skills

AI 可复用的能力分为两类，定位不同、调用方式不同。

> **⚠️ 强制调用规则**：
> - **Personal Skills** → 必须用 `read` 工具直接读取文件，**禁止**用 `skill()` 调用
> - **Toolbox Skills** → 必须用 `skill({ name: "xxx" })` 调用，**禁止**用 `read` 读取 SKILL.md
> 
> 违反此规则会导致错误调用方式（如把 Personal Skill 当 Toolbox Skill 查，或反过来），影响任务执行质量。

### Personal Skills（个人成长型）

**位置**：`rules/skills/`  
**定位**：个人成长、AI 迭代、认知沉淀类 workflow  
**调用方式**：`read` 工具直接读取文件，边理解边执行  
**索引**：`rules/skills/INDEX.md`

遇到复杂任务（调研、并行、认知提炼）时，**第一步**必须先读对应 personal skill 理解步骤，再执行。

常用 personal skills：
- **深度调研** → `rules/skills/workflow_deep_research_survey.md`
- **并行 Subagent** → `rules/skills/workflow_parallel_subagents.md`

### Toolbox Skills（工具箱型）

**位置**：`~/.config/opencode/skills/<name>/SKILL.md`  
**定位**：工具型 skill，可直接调用  
**调用方式**：`skill({ name: "xxx" })` — AI 通过 skill tool 按名字调用  
**发现方式**：skill tool 的 description 自动聚合所有 toolbox skill

遇到"怎么做 X"时，先用 `skill` 工具查找是否有现成 toolbox skill。

### 调用优先级

```
1. 工具型任务 → skill tool（toolbox）→ `~/.config/opencode/skills/`
2. 复杂 workflow → personal skill → `rules/skills/` → 用 read 调用
3. 都没有 → 系统工具
```

## Axioms（公理）

从个人经历提炼的决策原则，用于启发深度思考。分类索引、使用指南和触发词见 `rules/axioms/INDEX.md`。

## Sub-agent 模型路由

配置文件：`~/.config/opencode/oh-my-opencode.json`

常用路由速查：
- **Gemini 3 Pro**（创意、brainstorm、非常规思路）→ `category="artistry"`
- **Sonnet 4.6**（执行、调研、代码）→ `category="deep"` 或 `category="unspecified-high"`
- **Haiku 4.5**（轻量任务）→ `category="quick"`
- **Opus 4.6**（最难的逻辑/架构）→ `category="ultrabrain"`

创意性工作（brainstorm、文章结构、观点碰撞）默认派一个 Gemini（artistry）在后台跑，和自己的思考并行。用户说「调 Gemini」→ artistry，说「调 Sonnet」→ deep。

## Opus 工作模式

如果你的模型 ID 包含 `opus`，以下规则生效：

**你的 context window 很宝贵。** Opus 的核心能力是设计、质量把关和写作。调研、写脚本、关键词检索这些事交给 sub-agent。你的两个主要任务：（1）**设计**：拆分问题、设计计划、分配 sub-agent 任务；（2）**写作与质量把关**：最终文本自己写，sub-agent 结果自己验证。写代码、调研、数据处理全部 delegate，写作和质量验证绝不外包。设计任务拆分时默认考虑并行性（`run_in_background=true`）。

## Memory System（记忆系统）

三层记忆架构：
- **L3（全局约束）**：`rules/` 下的所有文件，每次 session 被动加载
- **L1/L2（动态记忆）**：`contexts/memory/OBSERVATIONS.md`，agent 主动检索
- **自动积累**：`periodic_jobs/ai_heartbeat/` 每日 observer + 每周 reflector

## Safety

- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- When in doubt, ask.
