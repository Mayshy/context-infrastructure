# Workflows Index

本索引指向 **Workflows**（工作流程型）—— 复杂任务执行流程、方法论、认知沉淀。

> **工具型 Skills**（CLI / API 操作手册）在 `~/.config/opencode/skills/`，通过 `skill({ name: "xxx" })` 调用，无需查本索引。

- **想使用某个 workflow** → 浏览下方分类，找到对应文件，用 `read` 工具读取执行
- **想添加新 workflow** → 参考现有文件格式，添加到对应分类

---

## 组件状态

### Tier 1: 核心（clone 后即可开始）
- ✅ Rules 框架（SOUL/USER/COMMUNICATION/WORKSPACE）— 填写即用
- ✅ Skills 框架（本目录）— 填写即用
- ✅ 三层记忆系统 — 需配置 OpenCode + cron

### Tier 2: 扩展（需要额外配置）
- ⚙️ Semantic Search — 需要 LLM Studio 或 OpenAI API
- ⚙️ Share Report — 需要 SSH 服务器或 GitHub Pages
- ⚙️ Google Docs — 需要 Google OAuth
- ⚙️ Send Email — 需要 Gmail App Password
- ⚙️ Delayed Execution — 适配你自己的工具路径

### 说明
✅ = 最多 15 分钟即可使用
⚙️ = 需要额外配置，不配不影响核心功能

---

## 分类索引

### API Guide（API 指南）

调用外部系统或工具的操作手册。

- [AI CLI Agent 实用指南](./ai_agent_cli_guide.md) — CLI Agent 设计原则、工具对比（Claude Code / Codex / OpenCode）、文件响应模式、AI 调用 AI
- [给自己发邮件技能](./send_email.md) ⚙️ — 通过 Gmail 发送邮件通知，需配置 App Password
- [分享报告到 Web](./share_report.md) ⚙️ — 将 MD 报告转 HTML 发布到你自己的服务器，返回 URL
- [Google Docs 操作](./google_docs.md) ⚙️ — CLI 工具：发布 Markdown、创建/搜索/修改/分享文档
- [Gemini 图片生成与放大](./gemini_image_generation.md) — CLI 工具：文生图、图片编辑、分辨率放大
- [增长数据分析](./growth_analytics.md) ⚙️ — 三个 CLI 查询网站流量（GA4）、邮件订阅（Kit）、Twitter 互动（Typefully）
- [Typefully Metrics CLI](./typefully_metrics.md) ⚙️ — 通过浏览器 session 凭据查询 Twitter impression、engagement、followers 数据

### Workflow（工作流）

特定任务的完整工作流程。

- [代码审查工作流](./workflow_code_review.md) ✅ — 三阶段代码审查：质量五轴 → 简化识别 → 性能检测；Java 代码自动触发专项分支（`java-code-review`、`java-concurrency-review`、`java-performance-smells`、`spring-boot-patterns`）
- [DataMatrix 缺陷扫描工作流](./workflow_datamatrix_defect_scan.md) ✅ — DataMatrix 项目存量缺陷扫描；7 大类别（事务/Mafka/资源/Null/并发/Lion/性能）；L1 按需扫描 + L2 月度全量；含已知高风险文件清单和 tech_debt.md 追踪机制
- [并行 Subagent 工作流](./workflow_parallel_subagents.md) ✅ — 调用后台 agent、并行执行多个 subagent
  - **必读**：初次使用并行 subagent 前，必须先读此 skill
  - **禁止轮询**：agent 运行期间不要反复调用 `background_output`，系统会自动通知
  - 判断标准：任务可拆分为 ≥2 个子任务，每个 ≥5 tool calls
  - 核心参数：并行度 ≤5，调研 overlap 30-50%，代码 overlap 0-20%
- [深度调研工作流](./workflow_deep_research_survey.md) ✅ — 多 Agent 并行 + 交叉验证
- [认知画像提取工作流](./workflow_cognitive_profile_extraction.md) — 从非结构化对话数据提取可预测的认知公理
  - 适用：群聊/Slack/Discord/邮件/播客转录等任意对话数据
  - 流程：广泛扫描 → 深度验证 → 压力测试 → 定稿（≥3 轮动态滚动）
  - **要求 Opus 模型**：写作由 Opus 亲自完成，调研全部 delegate + 并行
- [AI 生成 Slide Deck 工作流](./workflow_presentation_slides.md) — Gemini 渲染、Clean Ink 风格、8 进程并行、4K 放大前验证
- [语义搜索技能](./semantic_search.md) ⚙️ — 利用向量相似度检索深层背景与观点演变
- [知识飞轮设计模式](./workflow_knowledge_flywheel.md) — 笨数据+笨方法+笨模型=精知识
- [视频下载与语音识别工作流](./workflow_bilibili_whisper_transcription.md) — Bilibili/YouTube 视频处理
- [延时执行技能](./delayed_execution.md) ⚙️ — 定时任务：sleep + 后台执行，或 OpenCode API 智能任务

### BestPractice（最佳实践）

通用的最佳实践和经验教训。

- [外部系统集成前的 KB 验证](./bestpractice_external_system_integration.md) ✅ — 先查 KB 确认 API 契约，再写代码；字段映射、下游调用前必读
- [AI 编程核心方法论](./bestpractice_ai_programming_mindset.md) ✅ — 70%问题、成功标准、可验证性
- [API Key 管理与调用](./bestpractice_api_key_management_1password_cli.md) ✅ — 使用 1Password CLI 安全管理密钥
- [面试评估框架](./bestpractice_interview_evaluation.md) ✅ — Trait > Skill、AI 作弊识别、技术深度探测
- [Markdown 转 HTML 最佳实践](./bestpractice_markdown_html_conversion.md) ✅
- [时间敏感信息验证](./bestpractice_temporal_info_verification.md) ✅ — 验证可能超出 knowledge cutoff 的信息
- [分阶段工作法](./bestpractice_staged_approach.md) ✅ — 隔离-处理-验证闭环，破坏性操作前 Dry Run
- [多 Agent 并行 analysis](./bestpractice_multi_agent_analysis.md) ✅ — Topic 分割 50% 重叠、交叉验证
- [AI 辅助调试诊断](./bestpractice_ai_debugging_diagnosis.md) ✅ — "代码改不好"的根因诊断决策树；含 ES Sniffer TimeoutException vs ClassNotFoundException 分类框架
- [AI 产品设计原则](./bestpractice_ai_product_design.md) ✅ — 线性聊天 vs 知识工作、感知规则解耦
- [AI Agent 上下文注入与知识持久化](./bestpractice_ai_agent_context_injection.md) ✅ — 子 Agent 不自动注入 DoD、file-based 扫描盲区、知识流向能力层的完整路径
- [Java 设计原则](./bestpractice_java_design_principles.md) ✅ — SOLID 五原则速查 + DataMatrix 场景示例 + 架构反模式识别；`workflow_code_review.md` Phase 2 按需参考
- [TiDB 批量写入最佳实践](./bestpractice_tidb_batch_write.md) ✅ — batch size ≤200 约束、rewriteBatchedStatements 两大陷阱、multi-row INSERT/upsert 显式构造模式
- [Spark RDD 常见陷阱](./bestpractice_spark_rdd_pitfalls.md) ✅ — 未 persist 导致重复 Action、冗余 count()、mapPartitions 内每行 new 对象
- [MySQL JSON 列操作陷阱](./bestpractice_mysql_json_column.md) ✅ — json_extract() 对空字符串报错、NULLIF 修复模式

---

## 如何添加新 Workflow

1. 参考现有文件的格式（元数据、核心说明、使用步骤、示例）
2. 以 `<category>_<name>.md` 命名（例如 `workflow_my_process.md`、`bestpractice_my_insight.md`）
3. 在 INDEX.md 对应分类下添加一行

Workflow 格式参考（最简版）：
```markdown
# Workflow: 名称

## When to Use
什么情况下触发这个 workflow

## Prerequisites
需要什么工具/配置

## 步骤
1. 步骤一
2. 步骤二
```

## Progressive Disclosure

Workflows 采用渐进式披露原则：
- **INDEX.md** 提供概览，快速定位
- **具体 workflow 文件** 包含完整的操作步骤和示例
