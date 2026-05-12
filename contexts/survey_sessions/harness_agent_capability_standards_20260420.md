# Harness Agent 能力标准竞品分析报告

**调研日期**: 2026-04-20  
**调研目的**: 了解行业对 AI 编码/工作 Agent（harness agent）的能力标准、评测框架和 benchmark，为个人 opencode+omo 系统的竞品定位提供参考  
**来源**: 4 个并行 librarian sub-agent 交叉验证，覆盖 benchmark 数据、评测框架、记忆/多 Agent 架构、行业标准四个维度

---

## 核心结论（TL;DR）

1. **SWE-bench Verified 是核心 benchmark**，顶级 agent 2026 年初已达 80-88%；但 SWE-bench Pro（更难）顶级仅 46%，差距巨大
2. **能力维度已高度标准化**：工具使用、规划/推理、记忆、多步骤/长视野、错误恢复是五大核心维度
3. **记忆架构**：三层（情节/语义/程序）+ 分级存储（热/温/冷）是 2026 年生产级标准
4. **多 Agent 编排**：LangGraph（复杂控制流）、CrewAI（快速原型）、AutoGen（对话协作）三足鼎立
5. **自我纠错盲点**：LLMs 纠正外部错误可靠，但内部错误纠正失败率高达 64.5%
6. **个人 opencode+omo 系统**的 memory、multi-agent、personalization 架构与行业标准高度对齐，但缺乏正式 benchmark 评测数据

---

## 一、Benchmark 数据：各评测的 SOTA 分数

### 1.1 SWE-bench 系列（最重要的 coding agent benchmark）

**衡量内容**: 解决真实 GitHub issue，端到端软件工程能力

| Benchmark | 说明 | 顶级分数 | 顶级模型/Agent |
|-----------|------|---------|--------------|
| **SWE-bench Verified** | 500 人工筛选任务 | **87.6%** | Claude Opus 4.7 |
| **SWE-bench Pro** | 1865 任务，更难 | **45.9%** | Claude Opus 4.5 |
| **SWE-bench Multimodal** | 517 含视觉任务 | **59.0%** | Claude Mythos Preview |
| **SWE-bench Multilingual** | 9 种语言 | ~65% | Claude Sonnet 4.5 |

**关键洞察**:
- SWE-bench Verified 顶级已达 87.6%，但这是 mini-SWE-agent 100 轮 scaffold 下的结果
- SWE-bench Pro 顶级仅 45.9%，与 Verified 差距 40+%，说明 Verified 已被"刷榜"
- 开源模型（MiniMax M2.5）已达 80.2%，与闭源差距缩小

**来源**: https://swebench.com/, https://morphllm.com/swe-bench-pro, https://live-swe-agent.github.io/

### 1.2 其他 Coding Benchmarks

| Benchmark | 衡量内容 | 顶级分数 | 顶级模型 | 来源 |
|-----------|---------|---------|---------|------|
| **HumanEval** | 164 Python 编程题（已饱和） | 97.6% | o3-mini (high) | https://llm-stats.com/benchmarks/humaneval |
| **LiveCodeBench** | 竞技编程（防污染，持续更新） | 91.7% | Gemini 3 Pro Preview | https://livecodebench.github.io/ |
| **Aider Polyglot** | 6 语言代码编辑，225 题 | 93.3% (agent) | Refact.ai + Claude 3.7 | https://aider.chat/docs/leaderboards/edit.html |
| **BigCodeBench (Hard)** | 1140 函数级任务 | 72.1% | Claude Opus 4.6 | https://bigcode-bench.github.io/ |

**关键洞察**:
- HumanEval 已饱和（97.6%），不再有区分度，只作最低门槛
- LiveCodeBench 持续更新防污染，是更可靠的代码能力指标
- Aider Polyglot 中 **agent 系统（93.3%）比基础模型（88%）高 5%+**，说明 scaffold 质量至关重要

### 1.3 Agent 通用 Benchmarks

| Benchmark | 衡量内容 | 顶级 Agent 分数 | 人类基线 |
|-----------|---------|--------------|---------|
| **GAIA** | 多步骤真实世界任务（工具+推理） | 92.36% (testManus) | 92% |
| **WebArena** | 网页浏览 agent（812 任务） | 71.6% (OpAgent) | 78.24% |
| **OSWorld** | 桌面操作系统任务（Ubuntu/Win/macOS） | 79.6% (Claude Mythos) | 72.4% |
| **Terminal-Bench 2.0** | 终端技术任务 | 82 (Claude Mythos) | N/A |

**关键洞察**:
- GAIA 顶级 agent 已接近人类基线（92% vs 92%）
- OSWorld 顶级 agent（79.6%）已**超过**人类基线（72.4%）
- WebArena 仍有约 7% 差距

---

## 二、能力维度标准：行业共识

### 2.1 Anthropic 官方评测框架

**来源**: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents (2026年1月)

> "The capabilities that make agents useful—autonomy, intelligence, and flexibility—also make them harder to evaluate. Agents operate over many turns: calling tools, modifying state, and adapting based on intermediate results."

**Anthropic 定义的评测基础结构**:
- **Task**: 单个测试，含输入和成功标准
- **Trial**: 每次尝试（多次 trial 产生统计可信结果）
- **Grader**: 评分逻辑（代码/模型/人工）
- **Transcript**: 完整记录（输出、工具调用、推理、中间结果）
- **Evaluation harness**: 端到端运行评测的基础设施
- **Agent harness (scaffold)**: 让模型作为 agent 运行的系统

**三类 Grader**:

| 类型 | 优势 | 劣势 |
|------|------|------|
| **代码 grader** | 快、便宜、客观、可复现 | 对有效变体脆弱 |
| **模型 grader** | 灵活、可扩展、捕捉细节 | 不确定性、贵 |
| **人工 grader** | 黄金标准 | 贵、慢 |

### 2.2 行业共识的七大能力维度

综合 Anthropic、AWS、学术论文（AgentBench、GAIA、ADEPTS 等）的分析：

| 维度 | 子维度 | 评测方式 |
|------|--------|---------|
| **1. 工具使用** | 工具选择准确率、工具调用错误率、多轮函数调用准确率 | TAU-bench, AgentBench |
| **2. 规划/推理** | 任务分解、长视野规划、动态重规划 | DeepPlanning, HORIZON, GAIA |
| **3. 记忆管理** | 准确检索、测试时学习、长程理解、选择性遗忘 | MemoryAgentBench (ICLR 2026) |
| **4. 自主任务完成** | 多步骤、长视野、50% time-horizon | METR HCAST, SWE-bench Pro |
| **5. 错误恢复** | 自我纠错、从失败态恢复、不恶化现状 | Recovery-Bench, PALADIN |
| **6. 多 Agent 协作** | 任务委派、结果聚合、冲突解决 | GAIA2, AgentErrorTaxonomy |
| **7. 人机交互模式** | 何时请求确认、渐进式自主、信任度 | 5 种 HITL 模式 |

### 2.3 ADEPTS 框架（7 能力）

**来源**: https://arxiv.org/abs/2507.15885v1

**7 个维度**: Actuation（执行）、Disambiguation（消歧）、Evaluation（自评）、Personalization（个性化）、Timing（时机）、Steering（引导）、Self-monitoring（自监控）

### 2.4 "Beyond Task Completion" 框架（2025年12月）

**来源**: https://arxiv.org/abs/2512.12791

> "Evaluating agentic systems requires examining additional dimensions, including the agent ability to invoke tools, ingest and retrieve memory, collaborate with other agents, and interact effectively with its environment."

**四支柱**: LLMs 核心能力 + 记忆 + 工具 + 环境交互

---

## 三、记忆系统与上下文管理标准

### 3.1 三层记忆分类（行业标准）

**来源**: CoALA 框架（Princeton/CMU，2023），被后续所有主要框架采用

| 记忆类型 | 功能 | Agent 实现 |
|---------|------|-----------|
| **情节记忆 (Episodic)** | 存储过去事件，保留时间/上下文 | 对话日志、执行轨迹 |
| **语义记忆 (Semantic)** | 结构化事实和关系 | 知识图谱、向量存储 |
| **程序记忆 (Procedural)** | 技能和"如何做"知识 | 工具定义、代码片段、成功工作流 |

### 3.2 分级存储架构（生产级标准）

| 层级 | 存储 | 用途 | 延迟 |
|------|------|------|------|
| **热层** (Working Memory) | Context window | 当前任务、活跃推理 | ~0ms |
| **温层** (Short-Term) | 压缩摘要 | 运行上下文、决策日志 | ~10ms |
| **冷层** (Long-Term) | 向量 DB、知识图谱 | 完整制品，按需检索 | ~100ms |

**来源**: https://arunbaby.com/ai-agents/0052-long-context-agent-strategies/

### 3.3 主要记忆框架对比

| 框架 | 架构特点 | GitHub Stars | 核心创新 |
|------|---------|-------------|---------|
| **Mem0** | 向量+图+KV 三存储 | ~48K | 多会话跨用户持久化 |
| **Zep** | 时序知识图谱 | ~10K | 时间感知实体关系 |
| **Letta (MemGPT)** | OS 虚拟内存分页 | ~15K | 主上下文+外部存储双层 |
| **A-Mem** | Zettelkasten 风格链接 | N/A | 动态记忆关联 |

**MemGPT 核心设计**（UC Berkeley，2023）:
> "MemGPT intelligently manages different storage tiers in order to effectively provide extended context within the LLM's limited context window, and utilizes interrupts to manage control flow."

**来源**: https://arxiv.org/abs/2310.08560

### 3.4 Anthropic Claude 记忆工具（2025年10月发布）

> "The memory tool enables Claude to store and retrieve information across conversations through a memory file directory. Claude can create, read, update, and delete files that persist between sessions."

**关键数据**: 记忆工具 + 上下文编辑结合，**减少 84% token 消耗**，同时保持任务连续性

**来源**: https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/memory-tool

### 3.5 RAG vs 长上下文：何时各自占优

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 静态语料，能放入 window | 直接加载 | "看全局"优势 |
| 大型/动态语料，点查询 | RAG | 成本效率 |
| 事实问答 | RAG 持平或更优 | 选择性检索质量优势 |
| 整体理解（代码库） | 长上下文 | 全局推理模式 |
| 会话内情节分析 | 长上下文 | 多轮连贯性 |

---

## 四、多 Agent 编排标准

### 4.1 三大主流框架（2026年）

| 框架 | 范式 | 最适合 | GitHub Stars | p95 延迟 |
|------|------|-------|-------------|---------|
| **LangGraph** | 有向图状态机 | 复杂工作流、checkpointing | ~48K | 19.8s |
| **CrewAI** | 角色制团队 | 快速原型、业务流程 | ~44K | 31.2s |
| **AutoGen (AG2)** | 对话驱动 | 研究协作、代码生成循环 | ~37K | 41.5s |

**Benchmark 对比**（来源：https://agent-harness.ai/blog/multi-agent-orchestration-frameworks-benchmark-crewai-vs-langgraph-vs-autogen-performance-cost-and-integration-complexity/）:

| 平台 | 精确匹配 | 语义准确率 |
|------|---------|----------|
| **CrewAI** | 57.3% | **87.3%** |
| **SMOLAgents** | 48.0% | 80.0% |
| **AutoGen** | 43.3% | 76.7% |
| **LangGraph** | 68.7% | 68.7% |

**关键洞察**: 精确匹配和语义准确率之间有 30%+ 差距，评测方法选择至关重要

### 4.2 多 Agent 编排模式

1. **顺序型**: Agent A → Agent B → Agent C
2. **层级型**: 管理 agent 委派给工作 agent
3. **扇出/扇入**: 一个 agent 生成多个，结果汇总
4. **对话型**: Agents 辩论和精炼（AutoGen 模式）
5. **委派型**: 中央 agent 管理多个专业 agent

---

## 五、错误恢复与自我纠错

### 5.1 自我纠错盲点（ICLR 2026 关键发现）

**来源**: https://openreview.net/pdf?id=W1vKCYeAM1

> "LLMs fail to correct internal errors (64.5% average failure rate), but reliably correct external errors."

**盲点定义**: 模型能纠正别人指出的错误，但无法识别自己的错误

**对 Agent 设计的影响**: 不能依赖 agent 自我纠错；需要外部验证机制

### 5.2 SCoRe：强化学习训练自我纠错（ICLR 2025）

**来源**: https://proceedings.iclr.cc/paper_files/paper/2025/file/871ac99fdc5282d0301934d23945ebaa-Paper-Conference.pdf

**MATH 数据集结果**:
| 方法 | 首次准确率 | 二次准确率 | 提升 |
|------|----------|----------|------|
| 基础模型 | 52.6% | 41.4% | -11.2% |
| **SCoRe** | **60.0%** | **64.4%** | **+4.4%** |

### 5.3 错误类型分类（AgentErrorBench）

**来源**: https://arxiv.org/abs/2509.25370

| 错误类型 | 占比 |
|---------|------|
| 低效规划 (Inefficient Plan) | 48% |
| 不可能操作 (Impossible Action) | 16% |
| 进度误判 (Progress Misjudge) | 20% |
| 约束忽视 (Constraint Ignorance) | 14% |
| 格式错误 (Format Error) | 6% |

### 5.4 Recovery-Bench：在"已污染"环境中评测

> "Instead of always beginning from a clean repository or freshly started environment, agents are initialized in states that include concrete environment residues such as modified files, broken tests, and misapplied patches."

**四个核心指标**:
- **TSR** (Task Success Rate): 完成原始任务的比例
- **RR** (Recovery Rate): 从失败态恢复的比例
- **CSR** (Catastrophe Success Rate): 不把事情搞更糟的比例
- **ES** (Efficiency Score): 在步骤预算内完成

---

## 六、Human-in-the-Loop 标准

### 6.1 五种生产 HITL 模式

**来源**: https://cordum.io/blog/human-in-the-loop-ai-patterns

| 模式 | 描述 | 适用场景 |
|------|------|---------|
| **1. 执行前审批门** | Agent 提案，人工审批后执行 | 不可逆操作（财务、删除） |
| **2. 异常升级** | Agent 自主执行，异常情况升级 | 常规+偶发边缘情况 |
| **3. 渐进式自主** | 基于可靠性演示扩大自主权 | 长期工作流 |
| **4. 抽样审计** | 事后审查执行样本 | 大量、低风险操作 |
| **5. 置信度驱动** | 置信度低于阈值时升级 | 复杂推理任务 |

### 6.2 决策矩阵：可逆性 × 影响力

```
                   低影响力          高影响力
可逆        ┌──────────────┬──────────────┐
            │   自主执行   │  HITL 审查   │
            ├──────────────┼──────────────┤
不可逆      │  异步 HITL   │  同步 HITL   │
            │              │   (必须)     │
            └──────────────┴──────────────┘
```

### 6.3 渐进式自主（Trust Ladder）

> "Treat agent autonomy as a dial you turn up over time based on demonstrated reliability — not a switch you flip on day one."

**数据**: ~20% 新用户（<50 次会话）使用全自动审批，>750 次会话后提升至 >40%

---

## 七、顶级商业 Agent 能力对比

### 7.1 主流 Agent 矩阵

| Agent | SWE-bench | 核心优势 | 主要劣势 |
|-------|-----------|---------|---------|
| **Claude Code** (Opus 4.6) | 80.8% | 128K 输出 token、Agent Teams、终端原生推理 | 终端 UI（非 IDE） |
| **GitHub Copilot Workspace** | ~65% | 企业生态、SSO/IP indemnity、1500万用户 | 上下文有限 |
| **Cursor 3** | ~63-65% | 最佳 IDE 集成、Composer 多文件、视觉 diff | 复杂任务易卡住 |
| **Devin** | ~50% | 完全放手云端 Agent、Slack 集成 | benchmark 落后、价格高 |
| **Windsurf** | ~60% | $10/月高性价比、Cascade 多 Agent | 生态较小 |
| **OpenHands** (开源) | 77.6% | 71K stars、MIT license、多 Agent 架构 | 需自部署 |

### 7.2 行业 Gold Standard 能力清单（Power User 共识）

**必须具备**（来源：https://www.augmentcode.com/guides/cto-ai-coding-checklist, developer communities）:

1. ✅ 多文件编辑 + 跨文件依赖理解
2. ✅ 自主测试-修复反馈循环
3. ✅ MCP 支持（扩展生态）
4. ✅ Sub-agent 多 Agent 协作架构
5. ✅ 代码库语义索引（混合检索）
6. ✅ 长时间上下文保持（>30 分钟任务）
7. ✅ Enterprise 安全（SSO/审计日志/IP indemnity）

**仍未解决的问题**:
- 计划执行纪律（"Plan as text, not constraint" — GitHub Issue #16807，Claude Code Bug Report，2026年1月）
- 30小时+持续协作型任务
- 真实代码库理解而非统计匹配
- SWE-EVO benchmark：GPT-5 + OpenHands 仅 21%（真实软件演化场景）

### 7.3 关键引用

> "Cursor completed a full-stack web app in 18 minutes with 95% accuracy" — AIToolScope, 2026年4月

> "Claude Code uses 5.5x fewer tokens than Cursor for identical tasks" — Builder.io 测试

> "The first 90% might be easy, but the last 10% can take... someone who actually knows what they're doing." — Addy Osmani，关于"80% Problem"

> "Plans are treated as text, not constraints" — GitHub Issue #16807 (Claude Code Bug Report, 2026年1月)

---

## 八、opencode+omo 系统的竞品定位分析

### 8.1 对标行业标准的优势

| 维度 | 行业标准 | opencode+omo 实现 | 评估 |
|------|---------|-----------------|------|
| **三层记忆** | Episodic+Semantic+Procedural | OBSERVATIONS.md + skills/ + workflows/ | ✅ 对齐 |
| **分级存储** | 热/温/冷三层 | Context window + memory files + survey sessions | ✅ 对齐 |
| **多 Agent 编排** | LangGraph/CrewAI/AutoGen 范式 | oh-my-opencode 路由 + 并行 subagent | ✅ 对齐 |
| **渐进式自主** | Trust Ladder 模式 | SOUL.md 定义的边界原则 | ✅ 对齐 |
| **个性化** | PersonaAgent/Memoria 框架 | USER.md + OBSERVATIONS.md | ✅ 对齐 |
| **工具使用** | 文件读写、bash、浏览器、搜索 | 完整工具链 + MCP skills | ✅ 对齐 |
| **错误恢复** | Recovery-Bench 标准 | 无专门机制 | ⚠️ 弱项 |

### 8.2 潜在差距

1. **无正式 Benchmark 数据**: 没有 SWE-bench 或 GAIA 分数，无法客观对比
2. **错误恢复缺乏机制**: 无 Recovery-Bench 类型的失败态检测和恢复策略
3. **自我纠错盲点**: 与所有 LLM 一样存在内部错误纠正失败率 64.5% 问题
4. **记忆系统无评测**: 无 MemoryAgentBench 类指标，记忆质量依赖主观感受
5. **多 Agent 无 Benchmark**: 并行 subagent 的语义准确率未量化

### 8.3 独特优势（行业稀缺）

1. **深度个性化**: USER.md + axioms + OBSERVATIONS.md 三层个人上下文，超过大多数商业产品
2. **跨会话记忆**: ai_heartbeat observer/reflector 自动积累，接近 Mem0/Zep 的功能
3. **Skill 生态**: 70+ 可复用 skills，类似 MCP 但更个人化
4. **模型路由智能**: 基于任务类型路由到最优模型，多数商业产品无此能力
5. **完全本地控制**: 无供应商锁定，可自由切换底层模型

---

## 九、关键 URL 索引

### Benchmarks
- **SWE-bench Official**: https://swebench.com/
- **SWE-bench Pro**: https://morphllm.com/swe-bench-pro
- **Live SWE-agent Leaderboard**: https://live-swe-agent.github.io/
- **LiveCodeBench**: https://livecodebench.github.io/leaderboard.html
- **Aider Polyglot**: https://aider.chat/docs/leaderboards/edit.html
- **GAIA HF Leaderboard**: https://gaia-benchmark-leaderboard.hf.space/
- **BigCodeBench**: https://bigcode-bench.github.io/
- **WebArena**: https://webarena.dev
- **OSWorld**: https://os-world.github.io/
- **BenchLM 聚合**: https://benchlm.ai/
- **Awesome Agents**: https://awesomeagents.ai/

### 评测框架
- **Anthropic Demystifying Evals**: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- **Anthropic Bloom**: https://alignment.anthropic.com/2025/bloom-auto-evals/
- **METR HCAST**: https://evaluations.metr.org/openai-o3-report/
- **AgentBench**: https://github.com/THUDM/AgentBench
- **Beyond Task Completion**: https://arxiv.org/abs/2512.12791
- **ADEPTS Framework**: https://arxiv.org/abs/2507.15885v1

### 记忆系统
- **MemGPT/Letta**: https://arxiv.org/abs/2310.08560
- **Mem0**: https://arxiv.org/abs/2504.19413
- **Zep**: https://arxiv.org/abs/2501.13956
- **Claude Memory Tool**: https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/memory-tool
- **MemoryAgentBench**: https://openreview.net/pdf/2b14e3fecd25cd9511348c6a9ad470c2a2161634.pdf

### 多 Agent 编排
- **LangGraph vs CrewAI vs AutoGen Benchmark**: https://agent-harness.ai/blog/multi-agent-orchestration-frameworks-benchmark-crewai-vs-langgraph-vs-autogen-performance-cost-and-integration-complexity/
- **OpenHands**: https://github.com/OpenHands/OpenHands

### 错误恢复
- **Self-Correction Bench**: https://openreview.net/pdf?id=W1vKCYeAM1
- **SCoRe**: https://proceedings.iclr.cc/paper_files/paper/2025/file/871ac99fdc5282d0301934d23945ebaa-Paper-Conference.pdf
- **AgentErrorBench**: https://arxiv.org/abs/2509.25370
- **PALADIN**: https://arxiv.org/pdf/2509.25238
- **Recovery-Bench**: https://openreview.net/pdf/3b7f176c50002e59438321f581063295986b269e.pdf

### 行业标准
- **CTO AI Coding Checklist**: https://www.augmentcode.com/guides/cto-ai-coding-checklist
- **HITL Patterns**: https://cordum.io/blog/human-in-the-loop-ai-patterns
- **Progressive Autonomy**: https://agentpatterns.ai/human/progressive-autonomy-model-evolution/

---

*报告生成时间: 2026-04-20 | 数据截止: 2026年4月 | 来源: 4 个并行 librarian sub-agent 交叉验证*
