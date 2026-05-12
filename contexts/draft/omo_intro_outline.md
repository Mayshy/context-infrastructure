# OMO 介绍大纲（非正式讨论版）

> 受众：组内同事，资深程序员，AI 使用深度参差不齐
> 形式：非正式讨论，学城文档
> 目标：建立 multi-agent 认知基础，介绍 OMO 解决的真实问题

---

## 一、从一个大家都遇到过的问题开始

**你用 AI 写代码时，有没有遇到过这些：**

- 任务做到一半，AI 突然"忘了"你之前说的约束
- 让 AI 改 A 模块，它顺手把 B 也改了
- AI 说"已完成"，但你 review 发现根本没做对
- 任务越复杂，越需要你盯着，反而比自己写更累

这不是模型不够聪明的问题。这是**单 agent 的结构性缺陷**。

---

## 二、单 agent 的三个结构性缺陷

### 2.1 Context Rot（上下文腐烂）
- 随着对话变长，早期的约束被"稀释"
- AI 开始做出和 session 开头矛盾的决策，但它不自知
- 本质：**记忆是有限的，但任务是累积的**

### 2.2 角色混淆：既是设计者又是实现者
- 同一个 agent 既做规划、又写代码、又做 review
- 就像让同一个人既写代码又 review 自己的 PR
- 结果：confirmation bias，发现不了自己的问题

### 2.3 无法并行，线性执行
- 单 agent 只能串行处理
- 调研文档、写代码、跑测试——全部排队
- 复杂任务的瓶颈不是智力，是**吞吐量**

---

## 三、Multi-Agent 的核心思路：角色分离 + 并行执行

**类比：软件工程团队**

| 工程团队 | Multi-Agent |
|---------|-------------|
| 架构师 | Oracle（只读顾问，不写代码）|
| 产品/需求 | Prometheus（规划，采访式澄清需求）|
| QA | Momus（审核计划，找漏洞）|
| 开发 | Sisyphus-Junior（并行执行）|
| 项目经理 | Atlas（分配任务，独立验证）|

**关键洞察**：角色分离不只是"分工"，更是**质量保证机制**。
- Oracle 只读 → 结构上保证它不会乱改代码
- Metis 不能调 task() → 结构上保证它只分析不执行
- 这不是功能阉割，是**用架构约束代替 prompt 约束**

---

## 四、OMO 是什么

**一句话**：运行在 OpenCode 上的多模型 agent 编排层。

**它做了什么**：
- 把 10 个专化 agent 组织成一个协作系统
- 按任务类型自动路由到最合适的模型（category 路由）
- 通过 Skills 系统让能力可复用、可积累
- 通过 Hooks 系统在关键节点注入约束和提醒

**它不是什么**：
- 不是一个更聪明的 AI
- 不是 Cursor/Claude Code 的替代品（它运行在 OpenCode 之上）
- 不是开箱即用的工具（需要配置和调试）

---

## 五、OMO 原理深入

### 5.1 官方决策树：用什么路径做任务？

```
这是简单任务/快速修复？
  └─ 是 → 直接 prompt（普通 Sisyphus）
  └─ 否 → 解释完整上下文很麻烦？
              └─ 是 → 输入 ulw（并行 agent + 自动规划 + Oracle 验证）
              └─ 否 → 需要精确可验证的执行？
                         └─ 是 → @plan → /start-work（Prometheus 规划 + Atlas 执行）
                         └─ 否 → 还是用 ulw
```

**五种路径对比**：

| 路径 | 适合场景 | 触发方式 | 自动规划 | 并行 agent | 持续循环 | 人工介入 |
|------|---------|---------|---------|-----------|---------|---------|
| 普通 Sisyphus | 简单/单文件/快速修复 | 直接输入 | ❌ | 按需 | ❌ | 正常对话 |
| Sisyphus + ulw | 复杂但懒得解释 | 输入 `ulw` | ✅ 自动生成 | ✅ 激进并行 | ✅ 跑完为止 | 极少 |
| `/ralph-loop` | 多步骤、需多轮跑完 | `/ralph-loop "任务"` | ❌ | 按需 | ✅ 最多100轮 | 极少 |
| Prometheus + Atlas | 复杂且需精确可验证 | Tab→Prometheus→`/start-work` | ✅ 采访式 | ✅ Atlas分配 | ✅ 独立验证 | 规划阶段 |
| Hephaestus | 深度架构推理（GPT-only）| Tab 切换 | ✅ 内部规划 | ❌ | ✅ 内部verify | 极少 |

**核心判断逻辑**：
- 任务简单 → 直接 prompt，不要过度设计
- 任务复杂但你懒得解释 → `ulw`，让系统自己决定怎么拆
- 任务复杂且你需要精确控制 → Prometheus 规划链，每步可审查

---

### 5.2 10 个专化 Agent：分类与职责

**手动触发（需要明确切换）**：

| Agent | 角色 | 核心约束 |
|-------|------|---------|
| **Prometheus** | 采访式规划师 | 在写代码前先澄清需求、识别边界、生成 `.sisyphus/plans/*.md` |
| **Atlas** | 计划执行调度 | 绝不写代码，只 delegate + verify，有 4-phase QA protocol |
| **Hephaestus** | 深度自主执行 | GPT-only，给目标不给配方，自主探索并端到端实现 |

**自动触发（由 Sisyphus 判断派发）**：

| Agent | 角色 | 何时自动触发 |
|-------|------|------------|
| **Explore** | 代码库搜索 | 需要了解现有实现、文件结构时 |
| **Librarian** | 外部文档/库搜索 | 遇到不熟悉的库、需要最佳实践时 |
| **Oracle** | 只读架构顾问 | 2次修复失败、复杂架构决策、安全问题时 |
| **Metis** | 需求 gap 分析 | 需求模糊、有歧义时，在规划前介入 |
| **Momus** | 计划审核 | 计划写完后的严格把关 |
| **Sisyphus-Junior** | 并行实现 worker | ulw 模式下由主 Sisyphus 并行派发 |
| **Multimodal Looker** | 视觉分析 | UI/截图相关任务 |

**工具权限隔离**（关键设计）：

```
Oracle:          只读文件，不能写，不能调 task()
Metis:           只读文件，不能写，不能调 task()
Momus:           只读文件，不能写，不能调 task()
Explore:         只能搜索，不能写文件
Atlas:           只能改 .sisyphus/plans/*.md，其余都 delegate
Sisyphus:        全权限
```

这不是功能限制，而是**结构性安全边界**——用架构约束代替 prompt 约束，前者可靠，后者会被 AI 遗忘。

---

### 5.3 Hooks 驱动机制：AI 行为的"操作系统"

**Hooks 是什么**：在 AI 操作的关键节点（发消息前/后、调用工具前/后、出错时）自动执行的逻辑注入。

**总共 45 个 hooks，分两类**：

- **32 个 always-fire hooks**（始终触发，零成本/安全关键/基础设施类）
  - 例：`session-recovery`（session 恢复）、`todo-continuation-enforcer`（强制 todo 追踪）
- **13 个 gatable hooks**（可配置触发频率）分 5 组：

| 分组 | Hooks | 作用 |
|------|-------|------|
| `tool_guidance` | agent-usage-reminder, category-skill-reminder | 提醒 AI 该用哪个 agent/skill |
| `context_injection` | rules-injector, directory-agents-injector | 自动注入 AGENTS.md、rules/ 约束 |
| `reminders` | sisyphus-junior-notepad, anthropic-effort | 提醒 notepad 使用、推理深度 |
| `error_recovery` | edit-error-recovery, json-error-recovery, delegate-task-retry | 出错时自动恢复 |

**Hooks 的本质**：
- 不依赖 AI "记住"某个规则，而是在每次相关操作时**强制注入**
- 类比：不是靠程序员记住"要写单测"，而是 CI pipeline 强制跑测试
- 这是 OMO 和"写一个好 prompt"的本质区别——**系统约束 vs 自律约束**

**实际效果举例**：
- 你调用了一个工具但没用 explore agent → `agent-usage-reminder` hook 自动提醒
- 你在 Prometheus session 里 → `rules-injector` hook 自动注入 AGENTS.md
- 你的 edit 操作失败 → `edit-error-recovery` hook 自动触发恢复逻辑

**（技术原理，可选讲）Hooks 底层是什么**：

不是 ACP，是 **OpenCode Plugin API 的事件系统**。要理解它，先要理解 AI agent 的运行循环：

```
用户输入 prompt
    ↓
LLM API 调用（生成 response）
    ↓
AI 决定调用某个 tool（比如 read_file、bash、edit）
    ↓  ← tool.execute.before / PreToolUse 在这里触发
tool 实际执行（读文件、跑命令、写文件）
    ↓  ← tool.execute.after / PostToolUse 在这里触发
执行结果返回给 LLM
    ↓
下一轮 LLM API 调用
    ↑___________（循环，直到 AI 停止调用 tool）
```

这里的 **tool = AI 的 function call**，不是你的业务代码。`read_file`、`bash`、`edit` 这些都是 tool。hooks 插入的是 tool 执行前后，不是 LLM API 调用前后——这两个是不同的节点。

OpenCode 的实现：
- 在 tool 执行前后 emit 原生事件（Node.js EventEmitter）
- Hooks 是注册在这些事件上的监听器，运行在 OpenCode 进程内
- 注入机制：`ctx.client.session.promptAsync()` 向当前 session 发一条 internal prompt，AI 收到后就像收到用户消息一样处理

最复杂的 hook 是 `todo-continuation-enforcer`：监听 `session.idle`（AI 停止响应时），检测未完成 todo，自动注入 continuation prompt——实现"AI 做完一步自动接下一步"。

**这个模式是行业共识，不是 OMO 独创**：

| | OpenCode (OMO) | Claude Code | OpenAI Codex |
|--|---------------|-------------|--------------|
| Tool 执行前后 | `tool.execute.before/after` | `PreToolUse` / `PostToolUse` | `PreToolUse` / `PostToolUse` |
| Session 生命周期 | `session.idle` | `SessionStart` / `SessionEnd` | `SessionStart` / `Stop` |
| 用户 prompt 时 | `message.updated` | `UserPromptSubmit` | `UserPromptSubmit` |
| 能否阻断 tool | 不确定 | ✅ 可 deny | ✅ 可 deny |
| 注入方式 | `promptAsync()`（发 internal message） | shell / HTTP / prompt / agent | command / prompt / agent |

三家独立设计出了几乎相同的事件节点。说明 PreToolUse / PostToolUse / SessionStart 这几个节点是 agent 行为控制的"自然边界"——在 agentic loop 里，这些是唯一有意义的拦截点。

---

## 六、一个真实案例：observer 的静默日 bug

> 用来展示：AI 系统的 bug 不是"AI 不够聪明"，而是"系统没有约束 AI 的行为边界"

**背景**：我有一个每日 10:30 自动运行的 observer，扫描当天工作并写入记忆。

**问题**：4月16日被错误标记为"静默日"（全天无工作），但实际上我做了大量工作。

**根因链**（5 层叠加）：
1. cron 10:30 跑，`target_date` 默认是**今天**
2. 当天工作 session 下午 16:26 才开始
3. 10:30 扫描时 DB 里没有当天 session → `session_digest = "(当日无工作记录)"`
4. AI 拿到空信息，**自由发挥**写了"静默日"
5. Reflector（另一个 agent）越权写了当日条目，幂等锁锁死，后续无法覆盖

**修复**：`target_date` 改为昨天（一行代码）+ 修复 KeyError + 删除错误条目重跑

**启示**：
- AI 的"自由发挥"是系统设计的漏洞，不是模型的问题
- 幂等性保护了正确条目，但也保护了错误条目——设计时要想清楚"谁有权写"
- 这类 bug 在纯 prompt 工程里是隐形的，在系统工程里是可测试的

---

## 七、深水区：为什么 Harness 是技术债温床

> 适合有 AI 系统建设经验的同事

**Anthropic 工程博客的洞察**（来自 managed_agents_survey）：

- 针对模型弱点写的 workaround，会随着模型迭代变成负担
- 例：Claude Sonnet 4.5 有"context anxiety"，工程师加了 context reset。Opus 4.5 上这个问题消失了，reset 变成死重
- 问题：**你很难知道哪些 harness 逻辑是必要的，哪些已经是负担**

**OMO 的应对**：
- Category 路由：你写的是"这是 visual-engineering 任务"，不是"用 claude-sonnet-4-6"
- 模型换了，只改配置，不改业务逻辑
- 本质：**接口稳定，实现可变**

---

## 八、Skills 系统：让经验可积累

**问题**：每次开新对话，AI 都不记得你上次的决策和约束。

**Skills 的思路**：
- 把可复用的知识封装成 SKILL.md
- AI 在合适时机自动加载（通过 description 触发）
- 知识不再依附于某个 session，而是沉淀为团队资产

**我们的实践**：
- `kb-curator`：KB 维护操作手册
- `python-cron-venv-isolation`：cron 任务 .venv 隔离指南（从踩坑到 skill 的完整路径）
- `release-notes-updater`：从 git commit range 更新学城 release notes

**关键认知**：Skills 不只是"提示词模板"，而是**把隐性知识显性化、把经验变成可执行的约束**。

---

## 九、讨论：你们现在的工作流是什么

> 开放讨论，了解大家的痛点

- 现在主要用什么 AI 工具？
- 最大的痛点是什么？（上下文丢失？验证困难？重复劳动？）
- 有没有尝试过让 AI 做超过 30 分钟的任务？发生了什么？

---

## 十、如果你想上手

**最低门槛**：
1. 安装 OpenCode + oh-my-openagent
2. 写一个 AGENTS.md（告诉 AI 你的工作区是什么）
3. 用 `ulw`（ultrawork）模式跑一个复杂任务，观察它怎么拆解

**进阶**：
- 把一个常用工作流封装成 Skill
- 配置 category 路由，让不同任务用不同模型
- 建立项目 KB，让 AI 的知识在 session 间积累

---

## 附：关键概念速查

| 概念 | 一句话 |
|------|--------|
| **Context Rot** | 对话越长，早期约束被稀释，AI 开始自相矛盾 |
| **Category 路由** | 按任务类型选模型，不写死模型名 |
| **Skills** | 把可复用知识封装成 AI 可自动调用的指令包 |
| **Boulder State** | 跨 session 的任务进度持久化（.sisyphus/boulder.json）|
| **Hooks** | 在 AI 操作的关键节点自动注入约束和提醒 |
| **ulw / ultrawork** | 激活并行 agent + 自动规划 + Oracle 验证的增强模式 |
| **Prometheus + Atlas** | 规划（采访式）→ 执行（独立验证）的完整链路 |
