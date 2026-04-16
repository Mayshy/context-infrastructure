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

Date: 2026-04-12

🔴 High: [基础设施故障] ai_heartbeat observer cron 于 Apr 12 10:30 因 `ModuleNotFoundError: No module named 'dotenv'` 静默失败（logs/observer.log 第 21-33 行）：cron 使用系统 python3（非 .venv），.venv/bin/python 路径在该时间点不存在或未正确配置。导致 Apr 12 observer 任务完全跳过，本条目为事后手动补录。根因与 Apr 14 记录一致，修复方向：cron 命令使用 .venv/bin/python。
🟢 Low: [静默日] Apr 12 全天无 opencode 工作 session，无文件变动（find -mtime 扫描结果为空）。无需补录任何项目进展或技术决策。

---

Date: 2026-04-14

🔴 High: [基础设施修复] ai_heartbeat observer cron 的 `ModuleNotFoundError: No module named 'dotenv'` 根因已定位：cron 使用系统 python3 而非 .venv/bin/python，且 .venv 在 Apr 12-13 时不存在。修复方案：在 .venv 中安装 python-dotenv（`python-dotenv-1.2.2` 已于 Apr 13 安装至 `.venv/lib/python3.14/site-packages/dotenv/`），cron 命令需显式使用 `.venv/bin/python`。这是 observer 自动化运行的前置条件，直接影响记忆系统的连续性。
🟢 Low: [静默日] Apr 14 全天无 opencode 工作 session（当日无工作 session 记录），无用户发起的文件变动。observer.log 显示 Apr 14 的 observer 任务已由自动化脚本触发并成功完成（ses_2762cf7d7ffeXfUtrxGcqTj0F3）。

---

Date: 2026-04-15

🔴 High: [架构缺陷] ai_heartbeat observer 是纯 file-based 扫描（find -mtime），无法捕获 session 内的对话决策、被放弃的方案、口头约定约束、跨 session 推理链。修复方向：给 observer 加 session log 扫描模块，读取 `~/.local/share/opencode/opencode.db`（SQLite，`part` 表 TextPart 字段），提取昨天工作 sessions 的 assistant 回复，与 file-based 扫描并行合并写入 OBSERVATIONS.md。
🔴 High: [基础设施修复] ai_heartbeat observer 补录成功：缺失的 2026-04-07/10/11/12 四天条目已通过手动运行 observer.py 补录；reflector 同步运行，产出规则晋升（rules/SOUL.md +18行、rules/WORKSPACE.md +1条路由、contexts/memory/OBSERVATIONS.md 精简57行、contexts/survey_sessions/oh_my_openagent_survey_20260405.md +116行、oh-my-openagent.jsonc +11行、tools/semantic_search/ 两文件更新）。
🟡 Medium: [基础设施状态] ai_heartbeat observer 当前状态：.venv 存在，python-dotenv 1.2.2 已安装，crontab 配置正确；4月13日 10:30 的 cron 因 dotenv 缺失失败，4月13日条目为本 session 手动写入（非 cron 生成）；修复验证通过（4月9日条目成功写入）。
🟡 Medium: [架构洞察] opencode session log 存储机制确认：SQLite 数据库位于 `~/.local/share/opencode/opencode.db`（105MB，506 session，9034 message）；三张核心表：session/message/part；TextPart 含 assistant 回复正文；长 session compact 后 ToolPart 变为 `[Old tool result content cleared]` 但 assistant text 不受影响；observer/reflector automation sessions 跑完即删（cascade 删除 parts），用户工作 sessions 保留。
🟡 Medium: [项目状态] Pontos (datamatrix) AI 研发工作流定制完成：`docs/survey_sessions/2026-04-15-pipeline-ai-workflow-datamatrix-v1.md` 和 `v2.md` 已写入本地及学城（km.sankuai.com/collabpage/2756759579 和 2756669790，父目录 2757220461）。v2 核心改进：7模块映射规则替代三轮评分、DDL 专项 Zebra 子流程、Lion 开关强制、分层覆盖率门控（handler 80% vs 统一 60%）、MirrorFlow 状态机测试矩阵。
🟡 Medium: [项目状态] Pontos Crane Job 实现完成：`FlinkSlaManageCrane.offlineTerminatedFlinkSlas()` 新增（@Crane("dataserver.flinksla.offlineTerminated")），调用 `RTSlaClient.offlineSla` 下线已终止 MirrorFlow 的 Flink 实时 SLA；`MirrorFlowStatus.offlinedStatuses()` 新增静态工厂方法（FAILED/KILLED/SUCCESS_AND_CLEARED/FAILED_AND_CLEARED/KILLED_AND_CLEARED）；幂等性处理：SLA 已 OFFLINE 则跳过不调用 API；19 个单测全部通过。
🟢 Low: [技术细节] Pontos Crane Job 幂等性设计：通过检查 `sla.getStatus().equalsIgnoreCase("OFFLINE")` 实现幂等跳过；dryRun 模式复用现有 `FLINK_SLA_OFFLINE_DRY_RUN` Lion 开关；测试覆盖 ONLINE/OFFLINE/dryRun/noMatch/partialFailure 五个场景。

---

Date: 2026-04-16

🔴 High: [架构升级] ai_heartbeat observer 新增 session log 扫描模块（periodic_jobs/ai_heartbeat/src/v0/session_log_scanner.py，186行）：通过 SQLite 只读连接 ~/.local/share/opencode/opencode.db，按日期范围查询工作 sessions 的 assistant TextPart，过滤自动化/subagent sessions（EXCLUDE_TITLE_PATTERNS），截断后拼接成 digest 注入 PROMPT_TEMPLATE。这直接解决了 Apr 15 识别的"file-based 扫描无法捕获对话决策"架构缺陷。
🟡 Medium: [基础设施状态] observer.py 同步更新（periodic_jobs/ai_heartbeat/src/v0/observer.py）：prompt 步骤编号从 7 步扩展为 8 步，新增 step 4（session digest 注入），step 5-8 对应原 4-7；新增 session_digest 字段注入 PROMPT_TEMPLATE；scan_sessions() 调用含异常捕获（非致命，失败时 fallback 为占位文本）。
🟢 Low: [静默日] Apr 16 全天无 opencode 工作 session（当日无工作 session 记录），无用户发起的文件变动（find -mtime -1 结果均为 Apr 15 变更的延续写入）。
