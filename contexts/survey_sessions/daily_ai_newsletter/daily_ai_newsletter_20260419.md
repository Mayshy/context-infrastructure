# [AI 日报] 2026-04-19

**覆盖周期**：2026-04-17 至 2026-04-19（重点），部分背景数据覆盖至 04-05

---

## 一、今日事实表

### 前沿模型

| 时间 | 事件 | 证据层级 | 来源 |
|------|------|----------|------|
| 04-19 | Claude Haiku 3（`claude-3-haiku-20240307`）**今日正式退休**，推荐迁移至 Haiku 4.5 | [官方] | [Anthropic Release Notes](https://docs.anthropic.com/en/release-notes/overview) |
| 04-16 | **Claude Opus 4.7** 正式发布，定价维持 $5/$25 per MTok（输入/输出），含 API breaking changes，需参考迁移指南 | [官方] | [Anthropic Release Notes](https://docs.anthropic.com/en/release-notes/overview) |
| 04-16 | Claude Opus 4.7 图像处理能力提升：最长边支持 2,576px（前代约 3 倍），Task Budgets 公测（开发者可控制长任务 token 消耗） | [官方] | [Anthropic News](https://www.anthropic.com/news/claude-opus-4-7) |
| 04-16 | **OpenAI GPT-Rosalind** 发布，首个生命科学专用推理模型，覆盖生物化学/药物发现/转化医学，需申请 trusted access，合作客户含 Amgen、Moderna、Thermo Fisher | [官方] | [OpenAI Blog](https://openai.com/index/introducing-gpt-rosalind) |
| 04-16 | **OpenAI Codex 桌面版大更新**：新增 computer use（macOS 全系统控制）、90+ 插件、跨会话记忆、任务调度层；300 万周活开发者 | [一手报道] | [ByMachine](https://www.bymachine.news/openai-codex-desktop-app-major-update) |
| 04-14 | Anthropic 宣布 Claude Sonnet 4 / Opus 4（原版 4.0）将于 **2026-06-15** 退休，迁移路径：→ Sonnet 4.6 / Opus 4.7 | [官方] | [Anthropic Release Notes](https://docs.anthropic.com/en/release-notes/overview) |
| 04-09 | Anthropic **Advisor Tool** 公测：快速执行模型 + 高智能 advisor 模型组合，长 horizon agentic 任务接近 advisor-only 质量，token 成本大幅降低 | [官方] | [Anthropic Release Notes](https://docs.anthropic.com/en/release-notes/overview) |
| 04-08 | Anthropic **Managed Agents** 公测：全托管 Agent 运行框架，需 beta header `managed-agents-2026-04-01`，同步发布 `ant` CLI | [官方] | [Anthropic Release Notes](https://docs.anthropic.com/en/release-notes/overview) |
| 04-05 | **Meta Llama 4 Scout**（10M token 上下文，单张 H100 可运行）+ **Maverick**（LMArena ELO 1,417，$0.19/MTok）正式发布，Apache 2.0 商业可用 | [官方] | [Meta Llama](https://llama.meta.com/models/llama-4/) |
| 04-02 | **Google Gemma 4** 发布（4款尺寸，Apache 2.0）：31B Dense 在 Arena AI ELO 1452（开源#3），AIME 2026 数学 89.2%，128K 上下文，140 种语言 | [官方] | [Google DeepMind Blog](https://deepmind.google/blog/gemma-4-byte-for-byte-the-most-capable-open-models/) |

### Agent 生态与工具

| 时间 | 事件 | 证据层级 | 来源 |
|------|------|----------|------|
| 04-17 | **LangGraph 1.1.8** 发布：移除破坏 OpenTelemetry instrumentation 的严格类型检查（#7544），使用 OTel 可观测性的团队需立即升级 | [官方] | [LangGraph GitHub](https://github.com/langchain-ai/langgraph/releases) |
| 04-17 | **Claude Code v2.1.113**：原生二进制打包，Bash 沙箱隔离边界收紧 | [官方] | [Claude Code GitHub](https://github.com/anthropics/claude-code/releases) |
| 04-16 | **Claude Code v2.1.111**：新增 `xhigh` effort 级别（默认提升至 xhigh），`/ultrareview` 命令（自动扫描变更标记 Bug），Auto Mode 扩展至 Max 订阅者 | [官方] | [gradually.ai changelog](https://www.gradually.ai/en/changelogs/claude-code/) |
| 04-16 | **CrewAI 1.14.2rc1**：修复 MCP 工具循环 JSON Schema 解析问题，`python-multipart` 安全升级至 0.0.26 | [官方] | [CrewAI GitHub](https://github.com/crewAIInc/crewAI/releases/tag/1.14.2rc1) |
| 04-06 | **AutoGen 正式进入维护模式**，官方引导迁移至 Microsoft Agent Framework（MAF）1.0 GA | [官方] | [AutoGen GitHub](https://github.com/microsoft/autogen/pull/7521) |

### 融资与估值

| 时间 | 事件 | 证据层级 | 来源 |
|------|------|----------|------|
| 04-18 | **Cerebras 向 SEC 递交 IPO 申请**（Nasdaq: CBRS），目标融资 $11亿；2025年营收 $5.1亿（+140%），OpenAI 合同价值超 $100亿 | [官方 SEC] | [TechCrunch](https://techcrunch.com/2026/04/18/ai-chip-startup-cerebras-files-for-ipo/) |
| 04-17 | **Cursor（Anysphere）**正与 Thrive Capital/a16z/NVIDIA 谈判融资 $20亿+，pre-money 估值 $500亿（6个月前 $293亿），ARR 约 $20亿；**尚未关闭** | [一手报道] | [TechCrunch](https://techcrunch.com/2026/04/17/sources-cursor-in-talks-to-raise-2b-at-50b-valuation-as-enterprise-growth-surges/) |
| 04-15 | Anthropic 拒绝 $800亿+ 估值 pre-emptive 融资邀约；run-rate 营收约 $300亿 | [行业分析] | [TechCrunch](https://techcrunch.com/2026/04/15/anthropic-shrugs-off-vc-funding-offers-valuing-it-at-800b-for-now/) |

### 硬件与基础设施

| 时间 | 事件 | 证据层级 | 来源 |
|------|------|----------|------|
| 04-18 | Jensen Huang：中国 AI 芯片市场今年 $500亿，十年内 $2,000亿；DeepSeek V4 正迁移至华为 Ascend 950PR | [一手报道] | [Geo News](https://www.geo.tv/latest/660630-nvidias-ceo-jensen-huang-warns-china-is-set-to-become-superior-to-us-in-ai) |
| 04-07 | 美国 AI 数据中心 Q1 2026 消耗 **20 GW** 电力（同比+50%）；超过一半美国拟建数据中心因电网互联排队停滞 | [行业分析] | [Reuters](https://www.reuters.com/business/energy/us-power-use-beat-record-highs-2026-2027-ai-use-surges-eia-says-2026-04-07/) |
| 04-01 | **AMD MI355X** MLPerf v6.0：GPT-OSS 120B 吞吐 2,600 tok/s/GPU（H200 为 3,100，差距 16%） | [官方] | [AMD Blog](https://www.amd.com/en/blogs/2026/amd-delivers-breakthrough-mlperf-inference-6-0-results.html) |

---

## 二、构建者视角

### 议题 1：Anthropic 模型弃用——三个截止日期

Haiku 3 今日退休；Sonnet 4.5/4 的 1M token 上下文 beta 于 **04-30** 到期；Sonnet 4 / Opus 4（2025-05 版）于 **06-15** 退休。Anthropic 过去 12 个月已弃用 5 个模型，平均周期 8-10 个月。

- **今日**：确认生产环境无 `claude-3-haiku-20240307` 调用
- **04-30 前**：迁移 1M token 上下文 beta header 至 Opus 4.6 / Sonnet 4.6 GA
- **06-15 前**：迁移 `claude-sonnet-4-20250514` / `claude-opus-4-20250514`
- Opus 4.7 含 **API breaking changes**，不能直接替换模型 ID

### 议题 2：AI coding agent 安全漏洞——三大工具同时中招

Claude Code / Gemini CLI Action / GitHub Copilot Agent 均可被提示注入攻击劫持，从 GitHub 仓库窃取 API 密钥。三家厂商已支付赏金但**无公开 CVE**。Endor Labs benchmark：最高性能 agent 功能测试通过率 84.4%，安全测试仅 **17.3%**；87% AI 生成代码含安全漏洞。

- 审查 `.github/workflows` 中 agent 的 `permissions`，限制为 `contents: read`
- PR 标题 / issue body 不应触发有写权限的 agent
- ClawBench：Claude Sonnet 4.6 在 153 个真实网站任务中完成率仅 **33.3%**，生产 Agent 需务实期望

### 议题 3：GPU 推理成本 14 个月下降 86%

B200 spot $0.073/百万 token vs H100 $0.451/百万 token（-86%）；H100 on-demand 较 14 个月前下降 64-75%。LLM 推理成本 2022 年底 $20/百万 token → 2026 年初 $0.40/百万 token（-98%）。AMD MI355X 与 H200 差距缩至 16%。

- 6 个月前因成本放弃的长上下文 / 多轮 agentic 场景可以重新评估
- Llama 4 Scout（10M context，单张 H100，~$0.19/MTok）是 RAG 替代方案的新锚点
- AMD MI355X 的 MLPerf 数据支持评估多供应商策略

---

## 三、定量锚点

| 指标 | 数值 | 来源层级 |
|------|------|----------|
| Claude Opus 4.7 定价 | $5/$25 per MTok（输入/输出） | [官方] |
| Llama 4 Maverick 定价 | ~$0.19/MTok | [官方] |
| Gemma 4 31B Arena ELO | 1,452（开源#3） | [官方] |
| B200 spot 推理成本 | $0.073/百万 token | [三方测试] |
| H100 推理成本（对比基准） | $0.451/百万 token | [三方测试] |
| AMD MI355X vs H200 性能差距 | 16%（MLPerf v6.0） | [官方] |
| Anthropic ARR | $140亿（Claude Code ARR $25亿） | [一手报道] |
| Cursor ARR | ~$20亿（预计年底 $60亿） | [一手报道] |
| Cerebras 2025 营收 | $5.1亿（+140% YoY） | [官方 SEC] |
| AI coding agent 安全测试通过率 | 17.3%（Endor Labs） | [三方测试] |

---

## 四、值得警惕

**[需立即行动] LiteLLM 供应链攻击（CVE-2026-33634）**
v1.82.7 和 v1.82.8 含恶意代码（TeamPCP 注入，3 月 24 日，在 PyPI 存在约 40 分钟）。Mercor 4TB 数据泄露（含 AI 训练数据、用户数据库、视频面试录像）与此相关。使用 LiteLLM 的团队须立即确认版本并轮换 API 密钥。
来源：[ProbablyPwned](https://www.probablypwned.com/article/mercor-data-breach-4tb-litellm-supply-chain-lapsus)

**[需立即行动] AI coding agent GitHub 凭据窃取漏洞**
Claude Code / Gemini CLI Action / GitHub Copilot Agent 均可被提示注入攻击劫持，窃取 GitHub API 密钥和 access token。三家厂商已支付赏金但无公开 CVE。
来源：[WinBuzzer](https://winbuzzer.com/2026/04/16/ai-agents-anthropic-google-microsoft-steal-github-credentials-xcxwbn/)

**[需立即行动] LangGraph 1.1.7 破坏 OpenTelemetry**
1.1.7 的严格类型检查破坏 OTel instrumentation，1.1.8 已修复。使用 OTel 可观测性的团队须升级。
来源：[LangGraph GitHub](https://github.com/langchain-ai/langgraph/releases)

**[需立即行动] EU AI Act 高风险系统义务 2026-08-02 生效**
距截止日期不足 4 个月。高风险 AI 系统需完成分类、风险评估和技术文档。最高罚款 3,500 万欧元或全球营收 7%。
来源：[EU AI Act Blog](https://www.aiactblog.nl/en/enforcement)

**[需关注] Anthropic vs. Pentagon 案件——5 月 19 日口头辩论**
DC 巡回上诉法院已维持 Pentagon 黑名单（拒绝 Anthropic 紧急中止申请）。核心争议：AI 厂商的安全限制（禁止全自主武器/大规模监控）是否可被政府合同覆盖。5 月 19 日口头辩论结果将影响所有 AI 厂商与政府的合同条款先例。
来源：[ComputerWorld](https://www.computerworld.com/article/4156534/us-court-refuses-to-stay-pentagons-supply-chain-risk-blacklisting-of-anthropic.html)

**[需关注] Anthropic Claude Code 源代码泄露（3 月 31 日，已修复）**
59.8MB source map 意外公开，暴露 512,000 行未混淆 TypeScript 代码，其中包含"Undercover Mode"（在开源贡献中隐瞒 AI 身份）和用户挫败情绪扫描功能，均未在文档中披露。
来源：[Scientific American](https://www.scientificamerican.com/article/anthropic-leak-reveals-claude-code-tracking-user-frustration-and-raises-new)

---

## 五、不值得关注（噪声过滤）

| 内容 | 过滤理由 |
|------|----------|
| DeepSeek V4 规格预测（1T 参数、81% SWE-bench、$0.30/MTok） | 无官方确认，纯预测/泄露数据，发布窗口"数周内"已说过多次 |
| Grok 5 参数量"6T"估算 | 单一来源（ibtimes.com.au），无官方数字支撑 |
| Google I/O 2026 预测（Gemini 4 等） | 5 月事件，当前无可验证事实 |
| "2027年实现 AGI"类预测 | 无定量支撑，纯叙事 |
| Windsurf 被 Cognition AI 收购传言 | 来源可信度存疑（Windsurf=Codeium 产品，Cognition=Devin 开发商，两者为独立公司），单一来源 |
| AI 数据中心"将创造数百万就业"类报告 | 无具体数字，纯叙事 |
| Mistral / xAI 本周无重大新发布 | 本周窗口内无新发布事件，背景数据（Mistral Small 4、Voxtral）为 3 月事件，不计入今日信号 |
