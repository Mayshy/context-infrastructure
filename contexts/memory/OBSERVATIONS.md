# Memory Observations

这是三层记忆系统的 L1/L2 层。每日观察由 `periodic_jobs/ai_heartbeat/src/v0/observer.py` 自动写入，每周由 `reflector.py` 整理和蒸馏。

## 格式说明

每个日期条目格式如下：

```
Date: YYYY-MM-DD

🔴 High: [方法论/约束] 描述
🟡 Medium: [项目状态/决策] 描述
🟢 Low: [任务流水] 描述
```

### 优先级定义

- **🔴 High**：跨项目通用的经验教训、硬性约束、影响系统架构的重大决策。永久保留，候选晋升为 axiom 或 skill。
- **🟡 Medium**：活跃项目的关键进展、技术决策背景、未来几周仍需参考的信息。
- **🟢 Low**：日常任务流水、瞬时 debug 记录、临时上下文。定期垃圾回收。

## 如何加载记忆

不要全文加载这个文件（可能很大）。按需检索：

```bash
# 搜索特定主题
grep -n "关键词" contexts/memory/OBSERVATIONS.md

# 搜索最近 N 天
grep -A 20 "Date: $(date -v-7d +%Y-%m-%d)" contexts/memory/OBSERVATIONS.md
```

或使用语义搜索（`rules/skills/semantic_search.md`）做跨日期语义检索。

---

<!-- 以下是记录区域，由 observer.py 自动追加 -->

---

Date: 2026-04-06

🔴 High: [架构约束] DataMatrix 的 ES 索引构建采用"Spark 离线构建快照 → S3 → 灰度切流"模式（而非 ES 直写），原因是直写会导致 CPU/IO 争抢和段文件膨胀。切换时副本从 S3 拉取（非从主分片复制），大幅降低主分片压力。这是该系统最核心的设计决策之一，影响所有 hermes 相关开发。
🟡 Medium: [项目状态] DataMatrix KB 大规模建设完成（3 个 Session，共 4 次 commit）。contexts/projects/datamatrix-kb/ 目录结构全部初始化，00_overview/（架构/服务图/技术栈）✅、01_services/ 全部 5 个子服务 design.md ✅、02_km_summaries/ P0+P1 共 8 篇摘要 ✅；仍待补充：P2/P3 摘要（6 篇）、03_requirements/product_backlog.md、04_cross_cutting/data_lineage.md、05_runbooks/。
🟡 Medium: [技术决策] kugget 服务职责已澄清：学城目录分类为"数据质量"有误，实为**索引服务平台**（appkey: com.sankuai.eagle.indexserver），负责索引 Schema 管理和计算任务 DAG，与 hermes 是兄弟服务。已在 contexts/projects/datamatrix-kb/AGENTS.md 中更正。

---

Date: 2026-04-07

🟡 Medium: [新 Skill] skills/release-notes-updater/ 新建（~20:06），用于从 git commit range 提取变更并更新学城 release notes 文档。预置表格模板位于 skills/release-notes-updater/references/table-template.md。触发词：更新 release notes、把最近变更写进 release notes。

---

Date: 2026-04-08

🔴 High: [技术约束] Jackson 2.17.0 有内存泄漏 bug，必须使用 2.17.2。适用于 poros-java-api-client 及所有依赖它的服务。
🟡 Medium: [项目状态] Poros KB 全面初始化完成（2 个 Session）。contexts/projects/poros-kb/ 目录结构建立：00_overview/（architecture.md、module_map.md、tech_stack.md）✅、01_modules/ 全部 5 个子模块 design.md ✅、03_features/（high_risk_query_throttle.md、circuit_breaker.md、dsl_filter.md）✅、02_km_summaries/ 已完成 2/7（poros_java_api_client.md、es7_compat_es8.md）⚠️；04_cross_cutting/ 和 05_runbooks/ 待写。
🟡 Medium: [技术决策] Poros 核心架构细节：poros-high-level-client 有 5.6.3/6.8.10/7.10.0 三版本通过环境变量切换；CircuitBreakerFilter 同时实现两个接口；ResponseConstructor/RestClientPorosImpl 使用反射访问 package-private 构造器（ES 升级时高风险）；Arts v1 依赖 poros-high-level-client，v2 依赖 poros-java-api-client（更轻量但不支持限流）。
🟡 Medium: [技术决策] poros-elasticsearch-plugin 故障降级策略：Eagle API 故障时采用宽松模式（放行请求），可用性优先于安全性；MWS header 缓存 key 只取 appKey 冒号前缀；授权撤销最多 10 分钟延迟（AuthorizationRechecker 周期）。

---

Date: 2026-04-09

🔴 High: [技术约束] hermes Canvas edge API 字段方向与直觉相反：`inputNodeId` = 下游节点（接收方），`outputNodeId` = 上游节点（发送方）。portId = nodeId * 100 + port_index（数据源输出端口 index=1，Join/Output 输入端口 index=1，输出端口 index=2）。已验证，无需 GET canvas 获取 portId。
🔴 High: [技术约束] hermes 生产环境必须用 HTTPS（`https://datamatrix.sankuai.com`）：HTTP 会 302 跳转，POST body 会丢失，导致请求静默失败。适用于所有 hermes Canvas API 调用。
🟡 Medium: [项目状态] DataMatrix 迁移自动化脚本完成 edge 全流程自动化（Session 6）：`contexts/projects/datamatrix-kb/06_migration/hermes_canvas_builder.py` 更新，`add_edge` 重写为 upstream/downstream 语义，portId 公式已通过真实 hermes 生产 API 验证（`dzmgpunishticket` 画布），默认 host 改为 `https://datamatrix.sankuai.com`。
🟡 Medium: [项目状态] DataMatrix 迁移进度追踪 source of truth 切换：`contexts/projects/datamatrix-kb/06_migration/app_tracker.md` 全量同步至学城文档（contentId: 2756112613，父文档 2732354439），本地文件不再维护。后续 AI 更新进度需用 citadel skill 的 `getDocumentCitadelMd` + `updateDocumentByMd` 流程。
🟡 Medium: [技术文档] `contexts/projects/datamatrix-kb/06_migration/hermes_canvas_api.md` 新建完成：hermes Canvas API 完整参考（鉴权 header、componentId 完整映射表、arguments JSON 结构、创建顺序规范、portId 公式、edge 方向约定）。

---

Date: 2026-04-10

🟡 Medium: [工具理解] superpowers:* skills 调研完成：superpowers 不是独立 plugin，是 oh-my-openagent 的内置 skills；obra/superpowers 第三方 plugin 不推荐额外安装（功能高度重叠，维护负担高）；当前配置无需变更。

---

Date: 2026-04-11

🔴 High: [架构约束] Eagle SDK 可观测性缺失根因：打点各自为政（高风险查询/慢查询/限流熔断/业务异常 分属 Cat/Rhino/日志三个系统，无统一语义层）。修复方向：统一异常分类（业务异常/系统异常/noise）+ 延迟分层（SDK处理/网络/ES执行）+ 上下文标准化（集群名/索引名/查询模板ID/SDK版本）。这是 Poros SLO 大盘准确性的前置条件。
🟡 Medium: [项目状态] Q2 工作方向深度探索完成，报告存档于 contexts/survey_sessions/work_direction_exploration_20260411.md。核心诊断：当前工作 ~60% 维护性、~25% 版本迭代、~15% 探索性。Q2 主线确认为"迁移全流程自动化"（6-7 周，hermes_canvas_builder.py 已有基础）；Eagle SDK 可观测性平台为次优先候选。
🟡 Medium: [项目状态] ES 客户端全链路可观测性需求文档完成（Q2 OKR P1 对应），存档于 contexts/survey_sessions/es_observability_requirements_20260411.md。四大问题：SLO 大盘失真（version_conflict 混入）、sniffer 健康不可见、客户端配置上报不完整、mtrace 长尾无感知。已建 Sisyphus 执行计划 .sisyphus/plans/es-observability-requirements.md。
🟡 Medium: [工具建设] semantic_search 工具完成 Friday API 适配：embedding.py 完全重写（requests 替换 OpenAI SDK，batch_size 4，文本截断 1000 字符，指数退避重试）；模型切换为 text-embedding-miffy-002（美团内部）；.knowledge_cache/ 已建索引 14 个文件；向量维度 1024，余弦相似度搜索。
🟡 Medium: [配置变更] opencode.json 大幅扩展 provider 配置（Apr 11 15:25 更新）：新增 Friday-Cheap、Friday-OpenAI、Friday-Anthropic、Friday-Google 四个 provider，覆盖 kimi-k2.5、GLM-5.1、gpt-4.1、gpt-5.4、gpt-5.3-codex、qwen3.5-plus、gemini-3.1-pro-preview、gemini-2.5-pro、aws.claude-sonnet-4.6、aws.claude-opus-4.6；同时新增 shy provider（阿里云 dashscope-intl 接口）。

---

Date: 2026-04-13

🟡 Medium: [项目状态] Q3 及更长远方向头脑风暴完成，报告存档于 contexts/survey_sessions/q3_direction_brainstorm_20260411.md。结论：Q3 最优先方向为候选 A（Eagle SDK 统一可观测性平台，确定性高、影响范围广）；候选 D（DataMatrix 向量搜索）是 12-18 个月大赌注；个人技术品牌路径：可观测性专家 → SDK 架构师 → 搜索基础设施负责人。

---

Date: 2026-04-14

🔴 High: [架构方法论] Managed Agents 核心设计原则（来源：contexts/survey_sessions/managed_agents_survey_20260413.md）：对 LLM-based 系统，正确做法是设计稳定接口抽象（Session/Harness/Sandbox 三层解耦），让实现可自由替换，而非针对当前模型弱点写 workaround。Harness 补丁会随模型迭代变成技术债。构建 meta-harness 层（能运行任意 harness 的框架）是长期运营系统的正确方向。
🔴 High: [基础设施约束] ai_heartbeat observer cron 任务存在 Python 环境问题：cron 使用系统 python3（非 .venv），导致 `ModuleNotFoundError: No module named 'dotenv'`（logs/observer.log，Apr 13 10:30）。`.venv/bin/python` 实际指向 python3.14，dotenv 可正常 import；问题在于 cron shebang 未使用 .venv。修复路径：将 observer.py shebang 改为 `.venv/bin/python` 或 cron 命令前 source activate。此问题已在 rules/WORKSPACE.md 中有文档记录但尚未修复。
🟡 Medium: [调研完成] Anthropic Managed Agents 深度认知提炼完成，存档于 contexts/survey_sessions/managed_agents_survey_20260413.md。核心结论：Session（append-only 事件流）≠ Context Window；解耦带来 p50 TTFT 下降 ~60%、p95 下降 >90%；安全保证应来自结构（credentials 不进 sandbox），而非行为假设。
🟡 Medium: [规则层更新] rules/ 下多文件于 Apr 13 19:56-19:57 集中更新：SOUL.md（新增"外部系统集成原则"章节，引用 bestpractice_external_system_integration.md）、WORKSPACE.md（内容未见实质变化）、rules/skills/INDEX.md（新增 bestpractice_external_system_integration.md 条目）、rules/skills/bestpractice_external_system_integration.md（新建）。这次更新将"先查 KB 再写代码"从 OBSERVATIONS 观测提升为 L3 规则。
🟡 Medium: [配置变更] oh-my-openagent.jsonc 于 Apr 13 11:25 更新：librarian/explore agent 切换为 minimax/MiniMax-M2.7（原为其他模型），category_default_model 中 quick 路由到 MiniMax-M2.7，artistry 类别路由已移除（当前配置无 artistry/unspecified-high 映射）。
🟢 Low: [包依赖] package.json 更新：@opencode-ai/plugin 升至 1.3.17，@ai-sdk/anthropic 保持 ^3.0.66。

---

Date: 2026-04-15

🟡 Medium: [基础设施状态] ai_heartbeat cron 体系今日运行正常：`periodic_jobs/ai_heartbeat/src/v0/jobs/ai_news_survey.py` 于 08:00 成功触发（logs/ai_news_survey.log），`periodic_jobs/ai_heartbeat/src/v0/jobs/crontab_monitor.py` 于 09:00 成功触发（logs/crontab_monitor.log）；observer cron（10:30）今日尚未触发（logs/observer.log 最新记录为 Apr 14）。crontab 当前已全部使用 `.venv/bin/python` 路径，与 Apr 14 记录的修复方向一致。
🟡 Medium: [基础设施状态] crontab_monitor 今日两次运行（logs/crontab_monitor.log）均显示 `Error: Could not import OpenCodeClient`，说明 crontab_monitor.py 自身存在 Python 路径问题（与 observer.py 历史问题同根因）；但 Autonomous Crontab Auditor session 仍成功创建并完成（ses_2767ae48effe、ses_2715743deff），推测其通过 opencode CLI 而非直接 Python import 完成功能。
🟢 Low: [包依赖] package.json 于 Apr 14 15:57 更新（与 Apr 14 OBSERVATIONS 一致，无新变更）：`@opencode-ai/plugin@1.3.17`，`@ai-sdk/anthropic@^3.0.66`。
🟢 Low: [文件活动] contexts/survey_sessions/managed_agents_survey_20260413.md 在过去 48h 内有访问（mtime 变化），无内容新增，系被 reflector 或本次 observer 读取所致。
