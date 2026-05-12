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

Date: 2026-04-08

🔴 High: [技术约束] Jackson 2.17.0 有内存泄漏 bug，必须使用 2.17.2。适用于 poros-java-api-client 及所有依赖它的服务。
🟡 Medium: [项目状态] Poros KB 全面初始化完成（2 个 Session）。contexts/projects/eagle-sdk-kb/ 目录结构建立：00_overview/（architecture.md、module_map.md、tech_stack.md）✅、01_modules/ 全部 5 个子模块 design.md ✅、03_features/（high_risk_query_throttle.md、circuit_breaker.md、dsl_filter.md）✅、02_km_summaries/ 已完成 2/7（poros_java_api_client.md、es7_compat_es8.md）⚠️；04_cross_cutting/ 和 05_runbooks/ 待写。
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

Date: 2026-04-15

🟡 Medium: [架构洞察] opencode session log 存储机制确认：SQLite 数据库位于 `~/.local/share/opencode/opencode.db`（105MB，506 session，9034 message）；三张核心表：session/message/part；TextPart 含 assistant 回复正文；长 session compact 后 ToolPart 变为 `[Old tool result content cleared]` 但 assistant text 不受影响；observer/reflector automation sessions 跑完即删（cascade 删除 parts），用户工作 sessions 保留。
🟡 Medium: [项目状态] Pontos (datamatrix) AI 研发工作流定制完成：`docs/survey_sessions/2026-04-15-pipeline-ai-workflow-datamatrix-v1.md` 和 `v2.md` 已写入本地及学城（km.sankuai.com/collabpage/2756759579 和 2756669790，父目录 2757220461）。v2 核心改进：7模块映射规则替代三轮评分、DDL 专项 Zebra 子流程、Lion 开关强制、分层覆盖率门控（handler 80% vs 统一 60%）、MirrorFlow 状态机测试矩阵。
🟡 Medium: [项目状态] Pontos Crane Job 实现完成：`FlinkSlaManageCrane.offlineTerminatedFlinkSlas()` 新增（@Crane("dataserver.flinksla.offlineTerminated")），调用 `RTSlaClient.offlineSla` 下线已终止 MirrorFlow 的 Flink 实时 SLA；`MirrorFlowStatus.offlinedStatuses()` 新增静态工厂方法；幂等性处理：SLA 已 OFFLINE 则跳过；19 个单测全部通过。

---

Date: 2026-04-16

🔴 High: [架构决策] Pontos Blade 多集群选择策略从随机替换为容量感知：新增 `BladeCapacityClient`（调 `blade.sankuai.com/cloudnative/promxy` 查存储使用率）、`selectLeastCapacityDb()` 实现"容量最低优先 + 全超 88% 抛异常 + 全失败降级列表第一个"；查询失败（返回 -1.0）不触发全超阈值异常（防监控抖动）；Lion Key `Pontos.Blade.Capacity.Threshold` 可动态调整阈值。ADR 存档：`contexts/projects/datamatrix-kb/03_requirements/decisions/20260416_blade_cluster_capacity_aware_selection.md`。
🔴 High: [部署前置条件] Pontos Blade 容量感知选择依赖 Lion meta 配置中的 `cluster` 字段（如 `ad-blade-adpdw`）；若未填写，该 mirrorDb 被 skip（日志：`no meta or cluster for mirrorDb=xxx, skip`），新策略静默降级。**上线前必须在 Lion `Pontos.Mirror.Storage.Blade.MirrorDbMeta.{mirrorDb}` 中补全 `cluster` 字段。**
🟡 Medium: [项目状态] DataMatrix KB 新增老云搜服务建档（Session 9）：`01_services/naiads/design.md` + `gotchas.md`、`01_services/joiner/design.md` + `gotchas.md`；迁移对应关系：一个 joiner 应用 → pontos 镜像 + hermes Canvas；joiner `joinSource.xml` 是 `hermes_canvas_builder.py` 的输入来源。
🟡 Medium: [工具建设] 新建 skill `skills/kb-curator/SKILL.md`（KB 维护操作手册）；新建 skill `skills/python-cron-venv-isolation/SKILL.md`（Python cron 任务 .venv 隔离正确配置指南）。

---

Date: 2026-04-19

🟡 Medium: [KB 待办逾期] contexts/projects/datamatrix-kb/AGENTS.md — Session 3 三项待办（P2 学城摘要 Embedding 2734774411/应用迁移 2711712987/spark包管理 2748398827、`04_cross_cutting/data_lineage.md` 填充、`05_runbooks/` 填充）自 2026-04-05 起已 **14 天**未处理，正式触发逾期阈值。
🟡 Medium: [KB 待办逾期临近] contexts/projects/eagle-sdk-kb/AGENTS.md — `02_km_summaries` 仅完成 2/7（5 篇未写）、`04_cross_cutting/` 和 `05_runbooks/` 均为空，自 2026-04-07 初始化起已 **12 天**未推进，距 14 天阈值还剩 2 天。
🟡 Medium: [KB 待办] contexts/projects/datamatrix-kb/AGENTS.md — Session 8 下一步：Lion 配置中各 mirrorDb meta 的 `cluster` 字段未补充（Blade 容量感知选择策略上线前置条件），自 2026-04-16 起已 3 天。

---

Date: 2026-04-20

🔴 High: [架构洞察] OMO 不依赖 ACP 协议，是标准 OpenCode Plugin，通过 Plugin Hook 系统（`chat.params`/`tool`/`experimental.chat.system.transform` 等 10+ 种 Hook）在进程内拦截 LLM 调用参数。`task()` 工具实现原理：category 路由解析模型 → `ctx.client.session.create()` 创建独立 session → `ctx.client.session.promptAsync()` 向新 session 发送 prompt，每个子 agent 是独立 OpenCode session，有独立 context window 和 agent persona。
🔴 High: [架构洞察] 单 Agent 三大结构性缺陷：① Context Rot（注意力机制在长序列下质量退化，非"遗忘"，Lost in the Middle 现象，冗余 context 加速退化）；② 角色混淆（同一 agent 既执行又审查，confirmation bias 结构性存在，无法靠 prompt 修复）；③ 串行瓶颈（agentic loop 单线程）。Multi-agent 解法分别对应：上下文隔离 / 角色分离 / 并行执行。架构约束优于 prompt 约束是核心判断。
🔴 High: [系统修复] observer.py 两个 bug 已修复：① `PROMPT_TEMPLATE` 中 4 个字面量花括号（`{service}`、`{kb名}`、`{待办内容}`、`{天数}`）被 `str.format()` 当成占位符导致 `KeyError: 'service'`，已转义为 `{{...}}`；② 默认扫描日期 `datetime.now()` 改为 `datetime.now() - timedelta(days=1)`，防止 10:30 cron 扫描当天时遗漏下午 session。
🟡 Medium: [项目状态] cs_mafka 数据格式梳理完成，文档已创建：km.sankuai.com/collabpage/2757899226。两种子格式：Joiner（识别特征：无 `parentFields`/Arts 类名，逻辑主键字段 `keyFields`）/ Arts（识别特征：含 `parentFields` 或 Arts 类名，逻辑主键字段 `parentFields`，额外字段 `tags`）。格式识别是字符串匹配（基于第一条消息，后续复用同一 Gson 实例）；DELETE 主键优先取 `fields`，为空降级到 `keyFields`/`parentFields`；无变更时间戳，`changeTime` 取 Pontos 接收时间；字段名大小写不敏感（`TreeMap(CASE_INSENSITIVE_ORDER)`）。
🟡 Medium: [项目状态] OMO 分享文档（km.sankuai.com/collabpage/2757179530）完成第一节全部内容：1.1 单 Agent 结构性问题（含 Context Rot 机制、对照表、Mermaid 流程图）；1.2 Agent 划分三种方式表格（按工具/能力最稳定→按领域知识次稳定→按角色/工序最易变）；1.3 OMO 定位（category 路由、工具权限硬隔离、Hooks/Skills）；1.4 使用路径（官方决策树+五种路径对比表）。
🟡 Medium: [Harness Agent 评估] 当前系统 vs 行业标准七维评级：记忆管理（强，温层缺失+知识流动依赖模型执行质量）；多 Agent 编排（中强，角色设计超前，并行 agent 无共享状态/无冲突解决协议）；自我迭代（中，管道三断点：skill 草稿触发条件保守/草稿无提醒机制/skill 质量无验证闭环）；上下文注入（中，主 agent 强，子 agent 是已知盲点）。行业共识：scaffold 质量几乎与模型质量同等重要（SWE-bench Pro SOTA 45.9%）。
🟡 Medium: [Observer 根因] 4.16 被标记"静默日"的三层叠加原因：① L1 observer 10:30 跑时 4.16 工作 session 尚未开始（16:26 才创建）；② 4.16 的 L1 observer 根本未运行（无 Heartbeat L1 session）；③ L2 Reflector 越权在 18:33 写了当日条目（Reflector 无 session 扫描能力，基于不完整文件变动推断"静默日"）。幂等性过早锁定导致后续无法补救。Reflector 无幂等保护（每次运行无条件触发）是系统性缺陷。
🟡 Medium: [KB 待办逾期] contexts/projects/datamatrix-kb — Session 3 待办（P2 摘要 3 篇已在 Session 11 完成；`04_cross_cutting/data_lineage.md` 和 `05_runbooks/` 两个占位符已在 Session 11 填充）逾期待办已清零。Session 11 新增下一步：P3 摘要（HBase 2716815553、镜像切换细节 2731293914）和血缘查询 API 确认，自 2026-04-20 起计。
🟡 Medium: [KB 待办逾期] contexts/projects/eagle-sdk-kb — 2026-04-20 Session 3 完成全部 7 篇学城摘要 + `04_cross_cutting/deployment_ops.md` + `05_runbooks/` 两个手册，KB 完成度达 100%，逾期待办已清零（此前 13 天未推进）。
🟢 Low: [任务流水] datamatrix-kb Session 11 完成 P2 待办补全：新建 `02_km_summaries/embedding_support.md`、`02_km_summaries/app_migration.md`、`02_km_summaries/spark_flink_packages.md`、`04_cross_cutting/data_lineage.md`、`05_runbooks/es_index_ops.md`、`05_runbooks/spark_flink_debug.md`，更新 INDEX.md。
🟢 Low: [任务流水] eagle-sdk-kb Session 3 完成 KB 补全：新建 `02_km_summaries/arts_client.md`、`snapshot_client.md`、`log_client.md`、`performance_test.md`、`client_features.md`、`04_cross_cutting/deployment_ops.md`、`05_runbooks/troubleshooting.md`、`05_runbooks/version_upgrade.md`，AGENTS.md 完成度表更新为全绿。
🟢 Low: [任务流水] observer.py 修复后手动补跑 4.16 observer（删除错误"静默日"条目，重跑写入 7 条真实工作记录：Blade 容量感知选择、AI 系统架构洞察等）。
