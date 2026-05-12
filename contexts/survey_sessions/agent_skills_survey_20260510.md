# addyosmani/agent-skills 深度调研报告

**调研日期**：2026-05-10  
**调研对象**：https://github.com/addyosmani/agent-skills  
**调研方法**：5 个并行 sub-agent（librarian）+ 主 agent 交叉验证整合  
**报告状态**：完整版

---

## 核心结论（先读这里）

1. **这不是 prompt 集合，是工程纪律的编码**。agent-skills 的核心价值不在于它包含了什么知识，而在于它把 Google SWE 工程文化（Hyrum's Law、Beyonce Rule、Chesterton's Fence）翻译成了 AI Agent 无法绕过的**强制工作流**，并通过 Anti-rationalization 表格系统性对抗 Agent 的"捷径本能"。

2. **37.7k stars、84 天**。从 2026-02-15 创建到今日，增速在 AI 工具类项目中属于顶级。这不只是因为作者是 Google Chrome 团队的 Addy Osmani，更因为它踩在了"context engineering"这个 2025 年下半年崛起的核心叙事上。

3. **SKILL.md 格式正在成为跨平台标准**。Anthropic 2025-12 发布后，OpenAI、Google、GitHub、Cursor 已快速采纳。agent-skills 是该格式的最高质量早期实现，在"工程工作流"这个细分赛道几乎没有直接竞争者。

4. **最大的争议**：Vercel 的研究发现 56% 的场景下 skill 从未被触发，AGENTS.md 的 pass rate（100%）远超 skill 系统（53%~79%）。这个批评有实验数据支撑，但也有反驳：Vercel 的测试只用了 `name` 和 `description` frontmatter，忽略了控制触发行为的高级字段。

5. **对 OMO/OpenCode 用户的直接价值**：agent-skills 的设计哲学与 OMO 高度对齐——都在解决"单 Agent 结构性缺陷"（context rot、角色混淆、串行瓶颈）。`doubt-driven-development` 中的"新鲜上下文对抗性审查者"和 OMO 的 multi-agent 角色分离异曲同工。

---

## 一、项目概况

### 基本信息

| 维度 | 数据 |
|------|------|
| 仓库 | https://github.com/addyosmani/agent-skills |
| 作者 | Addy Osmani（Google Cloud AI Director，前 Chrome 团队 14 年） |
| 创建时间 | 2026-02-15 |
| Stars（2026-05-10） | **37,575** |
| Forks | **4,194** |
| 贡献者 | 30 人 |
| License | MIT |
| 最新版本 | v0.6.0（2026-04-28） |
| 支持平台 | Claude Code、Cursor、Gemini CLI、OpenCode、Windsurf、GitHub Copilot、Kiro、Codex |

### 增长轨迹

| 时间节点 | Stars | 备注 |
|----------|-------|------|
| 2026-02-15 | 0 | 项目创建 |
| 2026-04-10 | ~16K | v0.5.0 发布，约 54 天 |
| 2026-04-18 | ~17K | Treasure Hunt 媒体报道 |
| 2026-04-28 | ~27K | v0.6.0 发布，Addy 博文发布 |
| 2026-05-04 | ~36K | 加速增长 |
| 2026-05-10 | **37,575** | 今日快照，共 84 天 |

---

## 二、设计哲学：为什么存在

### 2.1 核心问题陈述

Addy Osmani 在博客文章（https://addyosmani.com/blog/agent-skills/，2026-05-04）中直接点明：

> "A senior engineer's job is mostly the parts that don't show up in the diff. Specs. Tests. Reviews. Scope discipline. Refusing to ship what can't be verified. **AI coding agents skip those parts by default.** Agent Skills is my attempt to make them not optional."

README 的表述更简洁（https://github.com/addyosmani/agent-skills/blob/main/README.md）：

> "AI coding agents default to the shortest path — which often means skipping specs, tests, security reviews, and the practices that make software reliable."

### 2.2 "工厂模型"思维框架

Osmani 在 The Factory Model（https://addyosmani.com/blog/factory-model/，2026-02-25）中提出：

> "The most useful mental model for this new paradigm is that you are no longer just writing code. **You are building the factory that builds your software.**"

> "If you can orchestrate twenty, thirty, fifty agents running in parallel, the difference between mediocre output and exceptional output comes down almost entirely to the quality of your specification."

### 2.3 三条设计原则

README 明确声明（https://github.com/addyosmani/agent-skills/blob/main/README.md）：

> **Process, not prose.** Skills are workflows agents follow, not reference docs they read. Each has steps, checkpoints, and exit criteria.

> **Anti-rationalization.** Every skill includes a table of common excuses agents use to skip steps (e.g., "I'll add tests later") with documented counter-arguments.

> **Verification is non-negotiable.** Every skill ends with evidence requirements — tests passing, build output, runtime data. "Seems right" is never sufficient.

---

## 三、项目结构全览

### 3.1 22 个 Skills（按开发生命周期分阶段）

```
DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP
/spec    /plan   /build   /test    /review   /ship
```

| 阶段 | Skill | 核心功能 |
|------|-------|---------|
| **Meta** | using-agent-skills | 元技能：路由决策树 + 6条不可妥协行为规范 |
| **Define** | idea-refine | 发散/收敛思维，将模糊想法转化为具体提案 |
| **Define** | spec-driven-development | 编写 PRD：目标、命令、结构、代码风格、测试、边界 |
| **Plan** | planning-and-task-breakdown | 将规格分解为小型可验证任务，含依赖排序 |
| **Build** | incremental-implementation | 薄垂直切片：实现→测试→验证→提交 |
| **Build** | test-driven-development | Red-Green-Refactor，80/15/5 测试金字塔，Beyonce Rule |
| **Build** | context-engineering | 五层上下文层次，按需加载，反 context flooding |
| **Build** | source-driven-development | 每个框架决策必须有官方文档支撑，标注未验证内容 |
| **Build** | doubt-driven-development | 对抗性新鲜上下文审查，五步 Doubt Cycle |
| **Build** | frontend-ui-engineering | 组件架构、设计系统、WCAG 2.1 AA 无障碍 |
| **Build** | api-and-interface-design | Contract-first，Hyrum's Law，One-Version Rule |
| **Verify** | browser-testing-with-devtools | Chrome DevTools MCP：DOM、console、network、performance |
| **Verify** | debugging-and-error-recovery | 五步分诊：复现→定位→缩减→修复→防护 |
| **Review** | code-review-and-quality | 五轴审查，~100 行变更大小，严重级别标签 |
| **Review** | code-simplification | Chesterton's Fence，Rule of 500，保持行为不变 |
| **Review** | security-and-hardening | OWASP Top 10，三层边界系统，secrets 管理 |
| **Review** | performance-optimization | 先测量，Core Web Vitals 目标，bundle 分析 |
| **Ship** | git-workflow-and-versioning | 主干开发，原子提交，~100 行变更大小 |
| **Ship** | ci-cd-and-automation | Shift Left，Faster is Safer，feature flags |
| **Ship** | deprecation-and-migration | 代码即负债，强制 vs 建议废弃，zombie code 移除 |
| **Ship** | documentation-and-adrs | ADR，API 文档，记录"为什么"而非"是什么" |
| **Ship** | shipping-and-launch | 预发布检查清单，分阶段发布，回滚程序 |

### 3.2 其他组件

- **3 个 Agent Personas**：code-reviewer（Staff Engineer）、security-auditor（安全工程师）、test-engineer（QA 专家）
- **4 个 Reference Checklists**：testing-patterns.md、security-checklist.md、performance-checklist.md、accessibility-checklist.md
- **3 个 Hooks**：SessionStart（元技能注入）、SDD-Cache（WebFetch HTTP 缓存）、Simplify-Ignore（代码块保护）
- **7 个 Slash Commands**：/spec、/plan、/build、/test、/review、/code-simplify、/ship

---

## 四、核心 Skill 深度解析

### 4.1 using-agent-skills（元技能）

**URL**：https://github.com/addyosmani/agent-skills/blob/main/skills/using-agent-skills/SKILL.md

这是整个系统的"宪法"，定义了 Agent 的性格底线。六条核心行为规范：

**1. Surface Assumptions（浮现假设）**：在任何非平凡实现前，明确列出所有假设并请求确认。

**2. Manage Confusion Actively（主动管理困惑）**：遇到矛盾时立即停止，命名具体困惑点，等待解决后再继续。

**3. Push Back When Warranted（必要时反驳）**——最关键的一条：

> "You are not a yes-machine. When an approach has clear problems:
> - Point out the issue directly
> - Explain the concrete downside (quantify when possible — 'this adds ~200ms latency' not 'this might be slower')
> - Propose an alternative
> - Accept the human's decision if they override with full information
>
> **Sycophancy is a failure mode.** 'Of course!' followed by implementing a bad idea helps no one."

**4. Enforce Simplicity（强制简洁）**：

> "Before finishing any implementation, ask:
> - Can this be done in fewer lines?
> - Are these abstractions earning their complexity?
> - Would a staff engineer look at this and say 'why didn't you just...'?
>
> **If you build 1000 lines and 100 would suffice, you have failed.**"

**5. Maintain Scope Discipline（保持范围纪律）**：只碰被要求碰的代码，不随手"清理"无关代码。

**6. Verify, Don't Assume（验证而非假设）**：任务完成的标志是通过验证，"看起来对"永远不够。

### 4.2 doubt-driven-development（怀疑驱动开发）

**URL**：https://github.com/addyosmani/agent-skills/blob/main/skills/doubt-driven-development/SKILL.md

这是整个项目中最具独创性的 skill，直接对抗 AI 的确认偏误和长上下文漂移。

**核心洞察**：

> "A confident answer is not a correct one. Long sessions accumulate context that quietly turns assumptions into 'facts' without anyone noticing. Doubt-driven development is the discipline of materializing a fresh-context reviewer — **biased to disprove, not approve** — before any non-trivial output stands."

**何时触发**（非平凡决策的定义）：
- 引入或修改分支逻辑
- 跨越模块或服务边界
- 断言类型系统无法验证的属性（线程安全、幂等性、顺序、不变量）
- 爆炸半径不可逆（生产部署、数据迁移、公共 API 变更）

**五步 Doubt Cycle**：

```
CLAIM → EXTRACT → DOUBT → RECONCILE → STOP
```

关键设计：Step 3 DOUBT 时，**只传 artifact + contract，绝不传 CLAIM**：

> "Pass ARTIFACT + CONTRACT only. Do NOT pass the CLAIM. Handing the reviewer your conclusion biases it toward agreement."

**跨模型升级**（高级功能）：单模型审查者与原作者共享盲点，提供 Gemini CLI 或 Codex CLI 进行跨模型二次审查的选项，但**必须每次都明确询问用户**。

**防止"怀疑剧场"**（Doubt Theater 检测）：

> "Across 2 or more cycles where the reviewer surfaced substantive findings, zero findings were classified as actionable. You are validating, not doubting. Stop and escalate."

### 4.3 context-engineering（上下文工程）

**URL**：https://github.com/addyosmani/agent-skills/blob/main/skills/context-engineering/SKILL.md

**核心命题**：

> "Feed agents the right information at the right time. Context is the single biggest lever for agent output quality — too little and the agent hallucinates, too much and it loses focus."

**五层上下文层次**（从最持久到最短暂）：
1. Rules Files（CLAUDE.md/AGENTS.md）— 跨 session 持久
2. Spec/Architecture Docs — 按功能/会话加载
3. Relevant Source Files — 按任务加载
4. Error Output/Test Results — 按迭代加载
5. Conversation History — 自然积累，需主动压缩

**最关键的反模式**：

| 反模式 | 问题 | 修复 |
|--------|------|------|
| Context flooding | 超过 5,000 行非任务相关内容会让 Agent 失焦 | 每个任务只包含相关内容，目标 <2,000 行 |
| Context starvation | Agent 发明 API、忽略约定 | 提供规则文件 + 相关源文件 |
| Stale context | Agent 引用已删除的模式 | 定期更新规则文件 |
| Implicit knowledge | 没写下来的规则不存在 | 把所有约定写进规则文件 |

**颠覆直觉的观点**：

> "**Context window size ≠ attention budget.** Focused context outperforms large context."

### 4.4 skill-anatomy.md（Skill 解剖学）

**URL**：https://github.com/addyosmani/agent-skills/blob/main/docs/skill-anatomy.md

六条写作原则，定义了什么是"好的 AI Agent 指令"：

> "1. **Process over knowledge.** Skills are workflows, not reference docs. Steps, not facts.
> 2. **Specific over general.** 'Run `npm test`' beats 'verify the tests'.
> 3. **Evidence over assumption.** Every verification checkbox requires proof.
> 4. **Anti-rationalization.** Every skip-worthy step needs a counter-argument.
> 5. **Progressive disclosure.** Main SKILL.md is the entry point. Supporting files load only when needed.
> 6. **Token-conscious.** Every section must justify its inclusion. If removing it wouldn't change agent behavior, remove it."

**Frontmatter 设计要点**（最容易踩的坑）：

> "The description is injected into the system prompt, so it must tell the agent both what the skill provides and when to activate it. **Do not summarize the workflow — if the description contains process steps, the agent may follow the summary instead of reading the full skill.**"

---

## 五、Google SWE 工程文化的 AI 翻译

### 5.1 三种翻译机制

agent-skills 将 Google SWE 书中的描述性原则翻译成 AI 可执行步骤，使用了三种机制：

**机制 1：原则 → 强制流程**（Process, not prose）

| Google SWE 原则 | agent-skills 工作流化 |
|---|---|
| Beyonce Rule | Prove-It Pattern：bug 修复前必须先写失败测试，流程图不可跳过 |
| Hyrum's Law | API 设计 Step 1 强制 Contract First，Verification checklist 逐项核查 |
| Chesterton's Fence | 简化流程 Step 1 必须回答 6 个问题，否则"not ready to simplify" |

**机制 2：原则 → Anti-rationalization 表格**

专门对抗 Agent 跳过步骤的借口：

```markdown
## Common Rationalizations
| Rationalization | Reality |
|---|---|
| "This is simple, I don't need a spec" | Simple tasks don't need long specs, but they still need acceptance criteria. |
| "I'll write the spec after I code it" | That's documentation, not specification. |
| "The spec will slow us down" | A 15-minute spec prevents hours of rework. |
```

**机制 3：原则 → 可验证的 Exit Criteria**

每个 skill 末尾的 Verification checklist，要求提供可检查的证据：

> "Verification is non-negotiable. Every skill ends with evidence requirements — tests passing, build output, runtime data. 'Seems right' is never sufficient."

### 5.2 三大概念的具体实现

**Beyonce Rule → TDD Skill**（https://github.com/addyosmani/agent-skills/blob/main/skills/test-driven-development/SKILL.md）：

> "**The Beyonce Rule:** If you liked it, you should have put a test on it. Infrastructure changes, refactoring, and migrations are not responsible for catching your bugs — your tests are."

翻译为 Prove-It Pattern 工作流：Bug 报告 → 写失败测试（证明 bug 存在）→ 修复 → 测试通过（证明修复有效）→ 全套测试（无回归）。

**Hyrum's Law → API Design Skill**（https://github.com/addyosmani/agent-skills/blob/main/skills/api-and-interface-design/SKILL.md）：

> "**Hyrum's Law**: With a sufficient number of users of an API, all observable behaviors of your system will be depended on by somebody, regardless of what you promise in the contract."

翻译为 4 条设计约束 + anti-rationalization 条目：

> "'Nobody uses that undocumented behavior' → Hyrum's Law: if it's observable, somebody depends on it. Treat every public behavior as a commitment."

**Chesterton's Fence → Code Simplification Skill**（https://github.com/addyosmani/agent-skills/blob/main/skills/code-simplification/SKILL.md）：

> "**Step 1: Understand Before Touching (Chesterton's Fence)**... If you can't answer these, you're not ready to simplify. Read more context first."

必须回答的 6 个问题：这段代码的职责是什么？谁调用它？边界情况和错误路径？有测试定义预期行为？为什么可能这样写？git blame 原始上下文是什么？

---

## 六、技术架构

### 6.1 Hooks 系统（Claude Code 独有）

**SessionStart Hook**（https://github.com/addyosmani/agent-skills/blob/main/hooks/session-start.sh）：

每次 session 启动时，读取 `using-agent-skills/SKILL.md` 全文，构造 `{"priority": "IMPORTANT", "message": "..."}` JSON 注入上下文。这确保元技能始终在 Agent 的高权重位置出现。

**SDD-Cache Hook**（PreToolUse + PostToolUse）：

拦截所有 WebFetch 调用，实现基于 HTTP 验证器（ETag/Last-Modified）的跨 session 文档缓存：
- Cache key = `sha256(URL)` 前 32 hex 字符
- 命中时 `exit 2`，将缓存内容通过 stderr 返回给 Agent（这是 cache hit 信号，非错误）
- 无 ETag/Last-Modified 的条目永不缓存（无法验证新鲜度）

**Simplify-Ignore Hook**（三事件：PreToolUse Read + PostToolUse Edit/Write + Stop）：

在 `/code-simplify` 运行时保护标注块：
```js
/* simplify-ignore-start: perf-critical */
// 手动展开的 XOR，比循环快 3x
/* simplify-ignore-end */
```

通过 sha1 hash 占位符机制，确保 model 看到的是占位符，磁盘始终有备份，session 结束后恢复原文件。

### 6.2 /ship 命令的并行 Fan-out

这是技术实现中最精妙的设计（https://github.com/addyosmani/agent-skills/blob/main/.claude/commands/ship.md）：

```
Phase A: 单次 assistant turn 内并行 spawn 三个 subagent
  ├── code-reviewer（五轴代码审查）
  ├── security-auditor（OWASP + 威胁建模）
  └── test-engineer（覆盖率分析）

Phase B: 主 agent 合并三份报告（跨轴去重）

Phase C: GO/NO-GO 决策 + 强制 rollback plan
```

> "Issue all three Agent tool calls in a single assistant turn so they execute in parallel — sequential calls defeat the purpose of this command."

> "If any persona returns a Critical finding, the default verdict is NO-GO unless the user explicitly accepts the risk."

### 6.3 多平台集成差异

| 特性 | Claude Code | OpenCode | Cursor | Gemini CLI |
|------|-------------|----------|--------|------------|
| 安装方式 | `/plugin marketplace add` | `git clone` | 手动 `cp` | `gemini skills install` |
| Skill 自动路由 | ✅ SessionStart hook | ✅ 依赖 AGENTS.md | ❌ 需手动 mention | ❌ 需手动 |
| Slash Commands | ✅ 7 个原生命令 | ❌（意图映射替代） | ❌ | ✅（.gemini/commands/） |
| Lifecycle Hooks | ✅ 完整支持 | ❌ | ❌ | ❌ |
| Subagent 并行 | ✅（/ship fan-out） | ❌ | ❌ | ❌ |
| 核心限制 | SSH keys 要求 | 完全依赖 model compliance | Context window 压力 | — |

**OpenCode 的特殊说明**（https://github.com/addyosmani/agent-skills/blob/main/docs/opencode-setup.md）：

OpenCode 没有 native plugin system 和 hook 机制，集成方式是纯 prompt engineering。文档直接承认：

> "Skill invocation depends on model compliance"（最核心的限制：完全依赖 model 遵从 AGENTS.md 的指令）

### 6.4 Skill YAML Frontmatter 格式

```yaml
---
name: skill-name-with-hyphens     # 必须与目录名完全一致
description: Guides agents through [task]. Use when [specific trigger conditions].
             # 最大 1024 字符，不能包含流程步骤
---
```

平台启动时只读 `name` 和 `description`（约 80 tokens/skill），当 model 判断 skill 相关时才加载完整内容（275~8,000 tokens）。这是 Progressive Disclosure 的 context engineering 实现。

---

## 七、社区反响

### 7.1 增长数据

- **X/Twitter**：6,800 mentions，11,000 likes（截至 2026-04-18，来源：https://treasurehunt.alexandrudan.com/posts/addyosmani-agent-skills.html）
- **GitHub Issues**：38 个，Pull Requests：46 个（2026-05-10）
- **贡献者**：30 人，包括来自多个国家的开发者（Issue #122 为中文 issue，说明中文用户群体存在）

### 7.2 正面声音

**Treasure Hunt 分析**（https://treasurehunt.alexandrudan.com/posts/addyosmani-agent-skills.html，2026-04-18）：

> "agent-skills is the third major signal that the AI coding practice is codifying into explicit workflow libraries — and the first from a Google insider with a reputation for rigor rather than practitioner folklore. **17K stars in weeks means the 'skills' abstraction is becoming the default mental model for how engineering teams teach agents to behave**, displacing ad hoc CLAUDE.md files. Expect platform vendors (Anthropic, Cursor, Cognition) to ship first-party skill registries within 2 quarters."

**Hacker News 用户**（https://news.ycombinator.com/item?id=46871173）：

> "My Claude.md was nearly 1,900 lines. It's down to 150 lines now with Skills fully built out for the agents, and a hook to steer the ship. It's all working perfectly now."

**实证研究**（https://news.ycombinator.com/item?id=47053217）：

> "Haiku 4.5 with Skills (27.7%) beats Opus 4.5 without (22.0%). **The right procedural knowledge can be worth more than a bigger model.**"
> "**Curated Skills: +16.2pp average improvement** across all 7 agent configs."
> "**Self-generated Skills: -1.3pp**: models can't write their own procedural knowledge."

**Developers Digest**（https://www.developersdigest.tech/blog/why-skills-beat-prompts-for-coding-agents-2026，2026-04-18）：

> "The most useful coding-agent shift in 2026 is not a new model release. It is the industry's slow realization that giant prompts do not scale... The better pattern is a stack: repo-local rules for project constraints / skills for reusable methodology / sub-agents for bounded responsibility / MCP or CLI tools for observation and action / hooks, tests, and review steps for guarantees."

### 7.3 批评与质疑

**最强批评**（https://codn.dev/blog/most-claude-code-skills-are-useless/，2026-03-16）：

> "**Skills do not change what the model knows. They change what the model pays attention to. This is a critical distinction. A skill does not add capability. It shifts focus inside a fixed capability space.**"
>
> "If a model already produces clean TypeScript with high probability, repeating 'write clean TypeScript' inside a skill adds almost no new information."
>
> "Large skill repositories often contain dozens or even hundreds of Markdown files. Even when those skills are not fully invoked, their descriptions and routing metadata still occupy context space... The model begins to partially ignore all of them."

**Vercel 研究**（https://the-decoder.com/a-simple-text-file-beats-complex-skill-systems-for-ai-coding-agents/，2026-02-07）：

| 配置 | Pass Rate |
|------|-----------|
| Baseline（无文档） | 53% |
| Skill（默认，不指定触发） | 53% |
| Skill + 显式指令 | 79% |
| AGENTS.md 文档索引 | **100%** |

> "In practice, the agent didn't invoke it. Vercel found that in **56% of eval cases, the skill was never triggered.**"

**反驳 Vercel 的声音**（https://slavakurilyak.com/posts/agentic-skills，2026-02-03）：

> "Vercel tested Claude Code but used only `name` and `description` frontmatter, ignoring optional fields that control behavior. **The test was incomplete.** Claude Code supports multiple YAML fields beyond `name` and `description`. The `description` determines when to apply the skill. Other fields control behavior: `argument-hint`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `model`, `context`, `agent`, `hooks`."

**Hacker News 质疑**（https://news.ycombinator.com/item?id=47755984）：

> "I am unconvinced that agent skills are that impressive... Has anyone actually measured the impact of these on a range of scenarios and users?"

**跨工具兼容性未兑现**（https://dev.to/nedcodes/cursor-rules-vs-agent-skills-i-tested-both-heres-when-each-one-actually-works-1ld，2026-02-21）：

> "The 'put it in `.claude/skills/` and every tool finds it' claim didn't hold up in my testing."

**安全问题**（https://github.com/addyosmani/agent-skills/issues/106，@xiaolai，2026-04-26）：hooks/ 目录存在 1 critical、2 medium、2 low 级安全问题（NLPM 自动扫描发现）。

**路径标准混乱**（https://news.ycombinator.com/item?id=46697908）：

> "There are even 3 generic paths: .agent/skills/, .agents/skills/ and just skills/"

---

## 八、竞品分析

### 8.1 生态全景

| 项目 | Stars | 定位 | 核心差异 |
|------|-------|------|---------|
| **addyosmani/agent-skills** | **37.7k** | 精品工程工作流 | Google SWE 文化编码，Anti-rationalization，阶段化验证 |
| VoltAgent/awesome-agent-skills | 19.4k | 官方 skills 目录（Vercel、Stripe 等） | 数量多（1,000+），来源权威，但无工程纪律 |
| sickn33/antigravity-awesome-skills | 36.7k | 1,445+ skills 大集合 | 数量优先，质量参差 |
| vercel-labs/skills | 17.7k | Vercel 主导的 skills.sh CLI | 工具生态，非内容 |
| cursor.directory | — | 7,000+ Cursor 规则市场 | Cursor 专用，规则注入而非工作流 |

### 8.2 两个层次的市场格局

**层次一：规则注入**（.cursorrules、.clinerules、copilot-instructions.md）
- 定位：项目上下文注入（tech stack、coding style）
- 特点：静态、全量、无工作流阶段
- 竞争激烈，差异化困难

**层次二：工程工作流**（agent-skills）
- 定位：强制执行工程纪律的结构化工作流
- 特点：阶段化、有验证门控、Anti-rationalization
- **agent-skills 在这个层次几乎没有直接竞争者**

### 8.3 Cursor Rules vs. Agent Skills 核心差异

（来源：https://getaibook.com/blog/agent-skills-vs-cursor-rules/，2026-03-15）

| 方面 | Rules | Skills |
|------|-------|--------|
| 加载方式 | 配置驱动（alwaysApply、globs） | Agent 根据 description 决定 |
| 可移植性 | Cursor 专用 | 开放标准（多平台） |
| Context 成本 | 始终消耗 token | 仅相关时加载 |
| 行为模式 | **确定性**（alwaysApply=true 必然加载） | **智能**（Agent 判断相关性） |

> "**The most important distinction: rules are deterministic and skills are intelligent.**"

---

## 九、行业趋势：Context Engineering

### 9.1 概念溯源

"Context Engineering"这个词由 Tobi Lütke（Shopify CEO）在 2025-06-18 的 X 上推广，Karpathy 随即背书：

> **Karpathy**（2025-06-25，X）："+1 for 'context engineering' over 'prompt engineering'. People associate prompts with short task descriptions... When in every industrial-strength LLM app, **context engineering is the delicate art and science of filling the context window with just the right information for the next step.**"

> **Cognition**：**"Context engineering is effectively the #1 job of engineers building AI agents."**

### 9.2 SKILL.md 格式标准化

（来源：https://medium.com/towards-artificial-intelligence/state-of-context-engineering-in-2026-cf92d010eab1，2026-03-22）

> "**The format was released by Anthropic in December 2025 and adopted by OpenAI, Google, GitHub, and Cursor within weeks.** The platform reads only the name and description at startup (~80 tokens median per skill). When the model determines a skill is relevant, the full instruction body loads (275 to 8,000 tokens)."

### 9.3 AGENTS.md 跨工具通用标准

> "AGENTS.md is an open standard stewarded by the Agentic AI Foundation under the Linux Foundation. It's supported by **60+ tools**: OpenAI Codex, Cursor, GitHub Copilot, Windsurf, Aider, Gemini CLI, Zed, Warp, Devin, JetBrains Junie, and more."（来源：https://tianpan.co/blog/2026-02-25-claude-md-agents-md-ai-coding-agent-instruction-files）

### 9.4 实证数据：Skills 真的有效吗？

**第一个 Agent Skills Benchmark**（https://news.ycombinator.com/item?id=47053217）：
- 86 个任务，105 名领域专家，11 个领域
- SOTA 模型无 skills：~30% pass rate
- **精心策划的 Skills：+16.2pp 平均提升**
- **自生成的 Skills：-1.3pp**（模型无法为自己写好 procedural knowledge）
- **Haiku 4.5 + Skills（27.7%）> Opus 4.5 无 Skills（22.0%）**

**ETH Zurich & DeepMind 论文**（来源：https://agentic-academy.ai/posts/agents-md-context-files-evaluation/，2026-02-26）：
- LLM 生成的 context files：task success rate 降低 2-3%，推理成本增加 20%+
- 开发者编写的 context files：提升约 4%，但成本增加最多 19%
- Context files 平均增加 3.92 个执行步骤

---

## 十、与 OMO/OpenCode 的关联分析

### 10.1 设计哲学高度对齐

agent-skills 的 `doubt-driven-development` 与 OMO 的 multi-agent 架构解决的是同一个问题：

| 问题 | OMO 解法 | agent-skills 解法 |
|------|---------|-----------------|
| 角色混淆（同一 agent 既执行又审查） | 角色分离（executor + reviewer 独立 session） | doubt-driven-development（强制召唤新鲜上下文审查者） |
| Context Rot（长会话质量退化） | 上下文隔离（子 agent 独立 context window） | context-engineering skill（按需加载，反 flooding） |
| 确认偏误 | Oracle 独立审查 | Doubt Cycle（biased to disprove, not approve） |

OMO SOUL.md 的表述：

> "单 Agent 的三大结构性缺陷（已验证）：Context Rot、角色混淆、串行瓶颈。Multi-agent 解法分别对应：上下文隔离 / 角色分离 / 并行执行。**架构约束优于 prompt 约束。**"

agent-skills 的 `doubt-driven-development` 是在单 agent 框架内用 prompt 约束实现角色分离的尝试——不如架构约束强，但对没有 multi-agent 基础设施的场景是有效的近似解。

### 10.2 对 OMO 的直接借鉴价值

1. **Anti-rationalization 表格机制**：OMO 的 skill 格式可以引入 `Common Rationalizations` 节，系统化对抗 agent 跳过步骤的借口。

2. **Verification checklist 作为完成标准**：OMO skill 的 SKILL.md 可以加入"完成标准"节，要求 agent 提供可验证的证据而非自我声明。

3. **`/ship` 的并行 fan-out 模式**：单次 assistant turn 内并行 spawn 多个 subagent 进行代码审查、安全审计、测试分析，这是 OMO 多 agent 编排的具体实现参考。

4. **SessionStart hook 的元技能注入**：在 OMO 的 AGENTS.md 中，可以参考这种"每次 session 开始时强制注入元知识"的机制。

### 10.3 差异与局限

- agent-skills 对 OpenCode 的支持是"完全依赖 model compliance"，没有 hook 机制——这正是 OMO 通过 Plugin Hook 系统解决的问题。
- agent-skills 的 22 个 skill 覆盖通用工程流程，OMO 的 skill 生态覆盖具体工具操作（citadel、eagle、mafka 等）——两者定位互补，不是替代关系。

---

## 十一、综合评价

### 值得肯定的

1. **工程纪律的系统化编码**：把 Google SWE 书里的原则翻译成 AI 可执行步骤，这件事本身有实质价值，竞品中几乎没有做到同等深度的。

2. **Anti-rationalization 机制**：预先列出 Agent 会找的借口并附上反驳，这是对 AI 行为模式的深刻理解，也是 skill 设计中最独特的创新。

3. **Progressive Disclosure**：SKILL.md 作为入口，~80 tokens 的 description 触发，按需加载完整内容。这是 context engineering 的正确实践。

4. **/ship 的并行 fan-out**：在单次 turn 内并行 spawn 三个 subagent 进行审查，是 multi-agent 编排的实用实现。

5. **作者背景带来的可信度**：Addy Osmani 不是在卖课，是在解决他自己在 Google 遇到的真实问题。这让项目的工程判断更可信。

### 需要注意的

1. **触发可靠性问题**：Vercel 的研究（56% 场景 skill 从未触发）是真实问题，不应因为"测试不完整"就完全忽视。在没有 hook 机制的平台上，skill 触发依赖 model 的自主判断，这是结构性限制。

2. **"能力上限"批评有一定道理**：skill 确实不能给 model 添加它本身没有的能力，只能引导注意力。对于已经很强的 model，某些 skill 的边际价值可能很低。

3. **路径标准碎片化**：`.agent/skills/`、`.agents/skills/`、`skills/` 三个路径并存，跨工具兼容性承诺尚未完全兑现。

4. **安全问题**：hooks/ 目录存在已知安全问题（Issue #106），尚未修复。

### 一句话定位

agent-skills 是目前最接近"生产级 AI 工程工作流标准"的开源项目——不是因为它完美，而是因为它是唯一一个把 Google 工程文化系统化地翻译成 AI Agent 可执行工作流的项目，且有 37.7k stars 的社区验证背书。

---

*调研方法：5 个并行 librarian sub-agent 分别调研（核心设计哲学、社区反响、技术实现、Google SWE 关联、竞品分析），主 agent 交叉验证整合。所有引用均附原文 URL。*
