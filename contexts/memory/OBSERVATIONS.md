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

---

Date: 2026-04-08

🔴 High: [技术约束] Jackson 2.17.0 有内存泄漏 bug，必须使用 2.17.2。适用于 poros-java-api-client 及所有依赖它的服务。
🟡 Medium: [技术决策] Poros 核心架构细节：poros-high-level-client 有 5.6.3/6.8.10/7.10.0 三版本通过环境变量切换；CircuitBreakerFilter 同时实现两个接口；ResponseConstructor/RestClientPorosImpl 使用反射访问 package-private 构造器（ES 升级时高风险）；Arts v1 依赖 poros-high-level-client，v2 依赖 poros-java-api-client（更轻量但不支持限流）。
🟡 Medium: [技术决策] poros-elasticsearch-plugin 故障降级策略：Eagle API 故障时采用宽松模式（放行请求），可用性优先于安全性；MWS header 缓存 key 只取 appKey 冒号前缀；授权撤销最多 10 分钟延迟（AuthorizationRechecker 周期）。

---

Date: 2026-04-09

🔴 High: [技术约束] hermes Canvas edge API 字段方向与直觉相反：`inputNodeId` = 下游节点（接收方），`outputNodeId` = 上游节点（发送方）。portId = nodeId * 100 + port_index（数据源输出端口 index=1，Join/Output 输入端口 index=1，输出端口 index=2）。已验证，无需 GET canvas 获取 portId。
🔴 High: [技术约束] hermes 生产环境必须用 HTTPS（`https://datamatrix.sankuai.com`）：HTTP 会 302 跳转，POST body 会丢失，导致请求静默失败。适用于所有 hermes Canvas API 调用。
🟡 Medium: [工作流约定] DataMatrix 迁移进度追踪 source of truth 切换至学城文档（contentId: 2756112613，父文档 2732354439），本地文件不再维护。后续 AI 更新进度需用 citadel skill 的 `getDocumentCitadelMd` + `updateDocumentByMd` 流程。

---

Date: 2026-04-11

🔴 High: [架构约束] Eagle SDK 可观测性缺失根因：打点各自为政（高风险查询/慢查询/限流熔断/业务异常 分属 Cat/Rhino/日志三个系统，无统一语义层）。修复方向：统一异常分类（业务异常/系统异常/noise）+ 延迟分层（SDK处理/网络/ES执行）+ 上下文标准化（集群名/索引名/查询模板ID/SDK版本）。这是 Poros SLO 大盘准确性的前置条件。
🟡 Medium: [项目状态] Q2 工作方向确认：主线为"迁移全流程自动化"（6-7 周，hermes_canvas_builder.py 已有基础）；Eagle SDK 可观测性平台为次优先候选。报告存档于 contexts/survey_sessions/work_direction_exploration_20260411.md。
🟡 Medium: [项目状态] ES 客户端全链路可观测性需求文档完成（Q2 OKR P1），存档于 contexts/survey_sessions/es_observability_requirements_20260411.md。四大问题：SLO 大盘失真（version_conflict 混入）、sniffer 健康不可见、客户端配置上报不完整、mtrace 长尾无感知。已建 Sisyphus 执行计划 .sisyphus/plans/es-observability-requirements.md。

---

Date: 2026-04-13

🟡 Medium: [项目状态] Q3 及更长远方向：最优先为候选 A（Eagle SDK 统一可观测性平台，确定性高、影响范围广）；候选 D（DataMatrix 向量搜索）是 12-18 个月大赌注；个人技术品牌路径：可观测性专家 → SDK 架构师 → 搜索基础设施负责人。报告存档于 contexts/survey_sessions/q3_direction_brainstorm_20260411.md。

---

Date: 2026-04-15

🟡 Medium: [架构洞察] opencode session log 存储机制：SQLite 数据库位于 `~/.local/share/opencode/opencode.db`；三张核心表：session/message/part；TextPart 含 assistant 回复正文；长 session compact 后 ToolPart 变为 `[Old tool result content cleared]` 但 assistant text 不受影响；observer/reflector automation sessions 跑完即删（cascade 删除 parts），用户工作 sessions 保留。
🟡 Medium: [项目状态] Pontos AI 研发工作流 v2 定制完成：文档已存入学城（km.sankuai.com/collabpage/2756759579 和 2756669790）。v2 核心：7模块映射规则替代三轮评分、DDL 专项 Zebra 子流程、Lion 开关强制、分层覆盖率门控（handler 80% vs 统一 60%）、MirrorFlow 状态机测试矩阵。

---

Date: 2026-04-16

🔴 High: [架构决策] Pontos Blade 多集群选择策略从随机替换为容量感知：新增 `BladeCapacityClient`（调 `blade.sankuai.com/cloudnative/promxy` 查存储使用率）、`selectLeastCapacityDb()` 实现"容量最低优先 + 全超 88% 抛异常 + 全失败降级列表第一个"；查询失败（返回 -1.0）不触发全超阈值异常（防监控抖动）；Lion Key `Pontos.Blade.Capacity.Threshold` 可动态调整阈值。ADR 存档：`contexts/projects/datamatrix-kb/03_requirements/decisions/20260416_blade_cluster_capacity_aware_selection.md`。
🔴 High: [部署前置条件] Pontos Blade 容量感知选择依赖 Lion meta 配置中的 `cluster` 字段（如 `ad-blade-adpdw`）；若未填写，该 mirrorDb 被 skip（日志：`no meta or cluster for mirrorDb=xxx, skip`），新策略静默降级。**上线前必须在 Lion `Pontos.Mirror.Storage.Blade.MirrorDbMeta.{mirrorDb}` 中补全 `cluster` 字段。**

---

Date: 2026-04-20

🟡 Medium: [技术决策] cs_mafka 数据格式：两种子格式：Joiner（识别特征：无 `parentFields`/Arts 类名，逻辑主键字段 `keyFields`）/ Arts（识别特征：含 `parentFields` 或 Arts 类名，逻辑主键字段 `parentFields`，额外字段 `tags`）。格式识别是字符串匹配（基于第一条消息，后续复用同一 Gson 实例）；DELETE 主键优先取 `fields`，为空降级到 `keyFields`/`parentFields`；`changeTime` 取 Pontos 接收时间；字段名大小写不敏感（`TreeMap(CASE_INSENSITIVE_ORDER)`）。文档：km.sankuai.com/collabpage/2757899226。
🟡 Medium: [系统评估] Harness Agent 七维评级（2026-04-20）：记忆管理强（温层缺失+知识流动依赖模型执行质量）；多 Agent 编排中强（并行 agent 无共享状态/无冲突解决协议）；自我迭代中（三断点：skill 草稿触发条件保守/草稿无提醒机制/skill 质量无验证闭环）；上下文注入中（主 agent 强，子 agent 是已知盲点）。行业共识：scaffold 质量几乎与模型质量同等重要（SWE-bench Pro SOTA 45.9%）。

---

Date: 2026-04-21

🔴 High: [技术诊断方法论] ES Sniffer 启动报错根因判断框架：若 stack trace 无 `NoSuchMethodError`/`ClassNotFoundException`，只有 `TimeoutException` 来自 `BasicFuture.get()`，则是**网络层超时**而非依赖版本冲突；Sniffer 线程（`es_rest_client_sniffer[T#1]`）是后台定时线程，报错不阻断 Spring 启动；最可能根因是 `poros-client` 被移除导致 ES host 配置注入丢失（`PorosRestClientBuilder` 使用 `PorosNodesSniffer`/`EagleApiProxy` 提供节点列表）。[已晋升至 bestpractice_ai_debugging_diagnosis.md]

---

Date: 2026-04-23

🔴 High: [分布式系统 Bug 诊断] Athena master 节点感知失效根因：`CuratorCache`（commit `5819f06` 引入）在初始化时会回放 `NODE_CREATED` 事件，触发 `updateMasterNodes()`；若此时 `getServerList()` 返回的 Server 对象 `host` 字段与 `masterConfig.getMasterAddress()` 不一致（IP 格式差异、多网卡、容器网络等），`getIndex()` 返回 -1，`totalSlot` 永久为 0，`findCommands()` 静默返回空列表。与旧 `TreeCache` 语义差异是根本原因。修复方向：对齐 `getServerList()` 中 Server.host 赋值逻辑与 `NetUtils.getAddr()` 使用相同地址来源。
🟡 Medium: [技术诊断] Athena 调度镜像流程卡死根因确认为 `masterCount=0`：`MasterSchedulerBootstrap.findCommands()` 在 `masterCount<=0` 时直接返回空列表；`totalSlot=0` 的两条路径：① `getIndex()` 返回 -1（最常见，地址不匹配）；② `getMasterNodesDirectly()` 返回空集合。待修复。
🟡 Medium: [KB 待办] contexts/projects/datamatrix-kb/AGENTS.md — P3 摘要（HBase 2716815553、镜像切换细节 2731293914）和血缘查询 API 确认（自 2026-04-20 起）；各 mirrorDb Lion meta `cluster` 字段未补充（Blade 容量感知上线前置条件，自 2026-04-16 起）；naiads/joiner 学城文档 contentId 待查补充（自 2026-04-16 起）。

---

Date: 2026-04-26

🔴 High: [方法论] Karpathy LLM Wiki 模式核心范式：raw（原始输入只读）→ wiki（LLM 持续编译合成知识）→ system（schema/索引/日志），关键操作为 Ingest/Query/Lint。与 RAG 的本质区别：知识是累积编译的而非每次重新推导；LLM 职责是写页面、维护交叉引用；人的职责是策展和判断方向。适用于任何需要 AI 长期维护的个人知识库。
🟡 Medium: [架构决策] Notes wiki 页面规范：YAML frontmatter（tags/updated/status/source）+ 第一人称 + 结论优先 + 保留原有个人语气；核心大文件（跨子主题综合）+ 小页面（单一概念+双链）；index.md 每次 ingest/migrate/cleanup 后必须自动更新；log.md 只追加不修改；原文件迁移时保留原位不删除。

---

Date: 2026-04-27

🔴 High: [技术约束] Pontos Flink 实时同步 crossSetConsume 根因确认：`crossSetConsume=false` → `MafkaParameterValidator.getTopicPartitionOffsets()` 只查本地 cell 分区 → `specificStartupOffsets` 只含 pj/jd 两个集群分区；`dispatch.type=default` 是 Broker 侧消费者组内分配策略，与"消费哪些集群"无关，无法通过调整 dispatch.type 扩大消费范围。开启跨地域消费前必须确认 topic 是否为多地域写入（DTS 单地域写入不可开启，有重复消费风险）。
🔴 High: [技术约束] Pontos Blade 批量写入扩展陷阱：`TimedUpdateBladeMirrorFunction` 的定时批量写入（500ms 窗口/100条/rewriteBatchedStatements）已从 DMX 扩展到所有数据源（commit e189d4da），DTS/CS/Hermes/Custom 首次走批量路径；`batchUpdateBlade` 默认 true 意味着影响面极大，上线前需确认各数据源对写入延迟的 SLA 要求。
🔴 High: [方法论] CLI skill vs 非 CLI skill 的核心区分：CLI 型 = frontmatter 有 `requires.bins` + `install` 字段 + `os` 限制，SKILL.md 正文是命令手册；API 型 = HTTP 接口路径+鉴权流程；文件处理型 = 文件格式原理+库用法+scripts/；知识型 = 领域知识+诊断流程。格式统一（SKILL.md），内容侧重不同。
🟡 Medium: [KB 待办逾期] datamatrix-kb：Lion 各 mirrorDb meta `cluster` 字段未补充（Blade 容量感知上线前置条件，自 2026-04-16 起逾期）；naiads/joiner 学城文档 contentId 待查补充（自 2026-04-16 起逾期）；P3 摘要（HBase/镜像切换）和血缘查询 API 确认（自 2026-04-20 起逾期）。

---

Date: 2026-04-28

🔴 High: [架构设计] Poros SDK 流量组配置 v2 结构设计：以索引为主键（`flowControls` 嵌套数组）优于以集群为主键的扁平结构（vA > vB）；核心优势：语义内聚（同一索引路由策略在一个条目内）、校验逻辑天然按索引隔离（无需 group-by）、`readRatio` 求和语义自然成立。版本识别推荐结构自动识别（`flowControls != null`）而非 `version` 字段（防止忘写 version 导致静默 fallback）。`indexName: null` 表示兜底规则的语义需显式约定（建议改为 `"*"` 或 `defaultFlowControls`）。
🔴 High: [技术 Bug] Pontos `getDefaultMirrorColumnDataType` 存在系统性类型修饰符问题：第一/二轮匹配直接 `return sourceColumnDataType.toLowerCase()` 不做清洗，导致 `int unsigned` 的 `baseType = "int unsigned"`，`generateDefaultValueSchemaStr` 的 switch 全部 miss，DEFAULT 值丢失（静默返回空串）。`containsAny` 的子串陷阱：`bigint` 包含 `int` 导致映射到 INT 而非 LONG。第二轮排序对共享列表 `Arrays.asList(values())` 做 sort 是全局副作用，且注释描述与实际意图相反。HBase 类型映射同样受 `containsAny` 子串陷阱影响（`bigint`→INT，`datetime`→LONG 等）。
🔴 High: [技术约束] Pontos Flink 实时同步三项性能优化方案确认：①DTS/CS 批量写入已通过 commit e189d4da 扩展到所有数据源（SLA 风险：首次走批量路径，上线前需确认各数据源延迟 SLA）；②Blade 连接池调优（`maxPoolSize` 调大）需注意连接池按 `jdbcRef` 缓存、第一次参数生效的陷阱（`ConcurrentHashMap` 缓存，后续调用忽略新参数）；③`keyBy` 后并行度提升（`UpdateBladeMirrorFunction` 单独 `setParallelism`）是最低风险方案，当前继承全局并行度=6，改动一行代码即可。
🟡 Medium: [架构决策] Poros SDK v2 流量组配置 `indexType` 字段命名存在歧义（与 `OperationType.INDEX` 混淆），建议改名为 `matchType`（EXACT/WILDCARD/ALIAS）；与现有 `Dispatcher` 的兼容性需要新增索引名感知的路由层（在 `GroupClients` 层面之上），现有架构是请求级别无感知索引名的。ADR 应记录于 eagle_meta 项目。

---

Date: 2026-05-06

🔴 High: [技术约束] TiDB 批量写入 batch size 建议 ≤200 行/事务（官方 Best Practices 明确：超过 200 行性能下降）。TiDB 与 MySQL 的核心差异：每次 executeBatch() 是分布式 2PC 事务提交，batch 越大 2PC 持有锁越多、commit 越慢；`txn-total-size-limit` 默认 100MB 超出报错。适用于所有 Pontos Blade JDBC 写入场景。[已晋升至 bestpractice_tidb_batch_write.md]
🟡 Medium: [项目状态] pontos Spark 全量同步 Blade 写入速度分析完成：Normal 模式核心杠杆是 export 分区数（`numExportPartitions`/`numExportDataSizePerPartitions`），Bulkload 模式核心是 `bladeBulkloadNumExportPartitions`（默认 2000）。发现并修复 `BladeNormalExportFunction` 中 batchSize 硬编码 bug（未读取 `exportBatchRange` 参数）；`DEFAULT_EXPORT_BATCH_RANGE` 从 50 调整为 200（对齐 TiDB 官方建议的 <200 行/事务，500 有 2PC 性能风险）。
🟡 Medium: [技术决策] pontos MigrateService XML 迁移配置修复：`buildRegisterRequestByXmlJoinSource()` 新增三级 fallback（schemaSource → schemaXml → fieldAndType JSON），新增 `getColumnInfosFromFieldAndType()` 解析 `{"columnFields":[...]}` 格式；修复 `liteapolloshopdata` 等 schemaXml 为空的应用迁移报错。
🟡 Medium: [项目状态] worksheet 服务新增后门接口（`POST /worksheet/api/flow/manage/backdoor/updateNodeAndStatus`）：直接修改 `worksheet_flow_record` 表的 `CurrentNode` 和 `Status` 字段，绕过状态机，仅供运维使用；复用 `AdminControllerAop` 鉴权（非 admin 返回 403），操作打 WARN 日志；同步修复 `AdminControllerTest` 中预存在的 UnnecessaryStubbing，新增两个测试用例，AdminControllerTest 从 1 ERROR 变为 17 run 0 Failures 0 Errors。

---

Date: 2026-05-07

🟡 Medium: [技术诊断] logcenter-esclient ES 写入两类报错根因分析：① `_id too long (11835 bytes)`：`LcUtil.genPrimaryKey()` 将 List/byte[] 类型字段值 toString() 后拼接为 _id（ES 限制 512 bytes），修复方向：对值做类型检查和截断；② `crashUrl field value too long (>32766 bytes)`：URL 被多次 URL 编码（`%25` 嵌套）导致指数级膨胀超出 Lucene keyword term 限制，修复方向：写入前截断或设置 `ignore_above`。

---

Date: 2026-05-08

🔴 High: [技术约束] Pontos Blade 全量同步 `BladeNormalExporter` 依赖 JDBC 驱动 `rewriteBatchedStatements=true` 的黑盒重写行为不可靠（Zebra 封装的 BladeDataSource 不保证该参数生效）；已改为显式构造 multi-row INSERT SQL（`INSERT IGNORE INTO t(c1,c2) VALUES(?,?),(?,?),...`），行为透明可控。改造涉及 `SqlUtils.generateMultiRowInsertIgnoreSql`、`SparkJdbcUtils.setValueToPreparedStatement`（新增 rowOffset 重载）、`BladeNormalExporter`（改造 BladeNormalExportFunction）三个文件，TDD 全部 GREEN，`rewriteBatchedStatements=true` 已移除。[已晋升至 bestpractice_tidb_batch_write.md]
🔴 High: [技术约束] PowerMock 2.0.2 + mockito-inline 兼容性 Bug：`verifyStatic(Class, VerificationMode)` 与 `InlineByteBuddyMockMaker` 不兼容，调用时报 `NotAMock`；规避方案：改用等价断言（如 `verify(bladeDataSource, times(N)).getConnection()`）替代 `verifyStatic`。CAT mock 坑：`com.dianping.cat.*` 不能同时出现在 `@PowerMockIgnore` 和 `@PrepareForTest` 中，需加 `@SuppressStaticInitializationFor("com.dianping.cat.Cat")`。
🔴 High: [诊断方法论] MySQL JSON 列 `json_extract()` 对空字符串 `''` 报 `Invalid JSON text: The document is empty`（对 NULL 容忍但对空字符串不容忍）；`IFNULL` 无法保护此场景（函数执行阶段就抛异常）；修复方式：在 SQL 层加 `NULLIF(extension, '')` 将空字符串转为 NULL 后再传入 `json_extract()`。适用于 Hermes 全量同步 SQL 中所有依赖 JSON 列的字段。[已晋升至 bestpractice_mysql_json_column.md]
🔴 High: [技术约束] Pontos Spark 全量同步写入瓶颈分析：Wave 3 任务比 Wave 1 慢 70% 的根因是 Blade 目标表随数据写入变大导致索引维护成本线性上升 + 多 Executor 并发写入锁竞争加剧（而非 Spark 侧问题，GC 时间仅 30s）。另一瓶颈：`HermesImporter` 在 `mapPartitions` 内部每行 `new CSVParser()`（非 per-partition 复用），百万级数据量下 GC 压力显著。[已晋升至 bestpractice_spark_rdd_pitfalls.md]
🟡 Medium: [技术诊断] Hermes 全量计算 `DataSinker.sinkJoinResultDoubleCluster()` 存在 docAcc 重复累加 Bug：`repartitionRDD` 未 `persist()`，`repartitionRDD.count()` 和后续 `saveAsNewAPIHadoopFile()` 两次 Action 均触发 `mapToPair` lambda，导致 `docAcc` 最终值是实际行数的 2 倍（有备集群则 3 倍）；准确值 `recordCount` 被打 log 后丢弃，未上报 `processInstance`。[已晋升至 bestpractice_spark_rdd_pitfalls.md]
🟡 Medium: [技术诊断] Pontos Spark 全量同步 `BladeBulkloadExporter` 存在冗余 count()：`repartitionedRecordRDD.count()` 在下一步 Action（`mapPartitions + collect()`）之前多执行了一次，等于把整个 repartitionAndSort 跑了两遍；各 index 串行走 persist→count→repartitionAndSort→count→upload，index 数量多时线性叠加耗时。[已晋升至 bestpractice_spark_rdd_pitfalls.md]
🟡 Medium: [技术诊断] worksheet 服务 401 根因：`InfFilter`（oceanus-http 基础设施层鉴权）拦截了 `/worksheet/api/v1/**`，非应用层 `DatamatrixToken` 问题；`SpringConfig.java` 中 `auth=true` + `auth-include-uri=/worksheet/api/v1/**`；curl 调用需带 `PORTAL-PROXY-USER: eyJsb2dpbiI6InNoZW5odWF5dSJ9` header（`{"login":"shenhuayu"}` 的 Base64）。
🟡 KB 待办逾期：contexts/projects/datamatrix-kb — Lion 各 mirrorDb meta `cluster` 字段未补充（Blade 容量感知上线前置条件），22 天未处理（自 2026-04-16 起）。
🟡 KB 待办逾期：contexts/projects/datamatrix-kb — naiads/joiner 学城文档 contentId 待查补充，22 天未处理（自 2026-04-16 起）。
🟡 KB 待办逾期：contexts/projects/datamatrix-kb — P3 摘要（HBase 2716815553、镜像切换细节 2731293914）和血缘查询 API 确认，18 天未处理（自 2026-04-20 起）。

---

Date: 2026-05-09

🔴 High: [技术约束] Pontos 增量同步 `TimedUpdateBladeMirrorFunction` 中 `rewriteBatchedStatements=true` 对 `INSERT...ON DUPLICATE KEY UPDATE` 完全无效（Zebra BladeDataSource 内核为 mysql-connector-java 5.1.49，该版本不对 upsert 语句执行 batch rewrite）；正确方案是在 SQL 层显式构造 multi-row upsert（`INSERT INTO t(c1,c2) VALUES(?,?),(?,?) ON DUPLICATE KEY UPDATE c1=VALUES(c1),...`），与全量同步 `BladeNormalExporter` 的 multi-row INSERT IGNORE 方案保持一致。实现入口：`SqlUtils.generateMultiRowUpsertSql()`。[已晋升至 bestpractice_tidb_batch_write.md]
🔴 High: [技术约束] Poros ES7（`poros-common`）master 节点规避路由最低支持版本为 `0.9.19_ES7`（2023-06-09 发布），含 `SkipMasterNodeSelector`、`PreferCoordinatingOnlyNodeSelector`、`LoadBalanceType` 枚举和 Lion 动态配置体系；**必须使用 `callESDirectly=true` 直连模式**，Poros 代理模式下 Eagle API 不返回节点 roles，selector 静默失效。推荐 `0.9.23_ES7`（Sniffer 独立路由，不跟随业务策略）。
🔴 High: [技术约束] ES5 客户端（`es5-client` / `poros-cli`）**不支持**任何路由策略（`LoadBalanceType`/`SkipMasterNodeSelector` 等），`PorosRestClientBuilder` 从未调用 `setNodeSelector()`，始终使用 `NodeSelector.ANY`。底层基础设施（`NodeSelector` 接口、`Node.Roles`、Sniffer）已具备，但上层未接通，无法通过配置驱动。ES5 集群如有 master 压力问题需升级到 poros ES7 ≥ `0.9.19_ES7`。
🟡 Medium: [技术诊断] DataMatrix Blade 集群慢查询 Top 问题（DAS 12h 数据）：sh1 集群最高频问题为 `Mirror_POIDraftRawData` 表三条 SQL 均使用 `IFNULL(col,?)=?` 导致索引失效（平均扫描 ~114万行，日均 6715 次）；`Mirror_appeal_ticket` 的 `WHERE target_id=?` 缺索引（6531次/40万行）；sh2 集群 `Mirror_search_poi` 的 `WHERE ShopId=? AND 1=1` 扫描 913万行（11196次，ORM 冗余条件 + 缺索引）；hl0 集群无高频 SELECT 慢查询。
🟡 Medium: [技术决策] Pontos MySQL 全量同步（Spark）从库路由现状：`DataSourceUtils.createMysqlDataSourceFromJdbcRef()` 创建 Zebra `GroupDataSource` 时未设置任何 `RouterType`，全量查询走默认路由（主库优先）；`planPartitions()` 在 Driver 端串行对每个物理分表执行 `SELECT MIN/MAX`（N×M 次），无从库保护且串行耗时；Joiner（老云搜）有条件走 SDW 从库（`sdwJdbcRef` 非空时），但 `sdwJdbcRef` 为空则回落主库。
🟡 KB 待办逾期：contexts/projects/datamatrix-kb — Lion 各 mirrorDb meta `cluster` 字段未补充（Blade 容量感知上线前置条件），23 天未处理（自 2026-04-16 起）。
🟡 KB 待办逾期：contexts/projects/datamatrix-kb — naiads/joiner 学城文档 contentId 待查补充，23 天未处理（自 2026-04-16 起）。
🟡 KB 待办逾期：contexts/projects/datamatrix-kb — P3 摘要（HBase 2716815553、镜像切换细节 2731293914）和血缘查询 API 确认，19 天未处理（自 2026-04-20 起）。

---

Date: 2026-05-11

🔴 High: [诊断方法论] Maven 多模块项目 `mvn deploy -pl <module>` 不加 `-am` 时，上游依赖模块不重新构建，直接使用 `~/.m2` 缓存的旧版 SNAPSHOT jar；若上游 SNAPSHOT 已更新而缓存未刷新，Lombok APT 在处理 `@Data`/`@Slf4j` 时会遇到类型不匹配并静默失败，生成残缺 class 文件（`Unresolved compilation problems` 写入 bytecode）；`mvn deploy` 不感知此问题，残缺 jar 成功上传并被 SNAPSHOT `updatePolicy=always` 的下游立即拉取。**正确姿势：`mvn deploy -pl <module> -am -DskipTests`，永远带 `-am`。**
🔴 High: [架构约束] Pontos Spark 全量同步 Scheduler Worker（`hermes-fullsync-job`，appkey `com.sankuai.eagle.scheduler.worker`）使用 Eclipse Aether 从 Maven 仓库拉包到 `/data/appdatas/local-repo/`，SNAPSHOT 策略为 `updatePolicy=always`，每次任务触发都强制拉最新版本；这意味着任何错误的 SNAPSHOT deploy 会在下次任务触发时立即生效，没有缓冲窗口。
🔴 High: [技术约束] Pontos Spark 全量同步写侧（`BladeNormalExporter`）当前**无 Rhino 限流**；读侧有 `clusterRateLimit`/`tableRateLimit`，写侧完全缺失；`maxExecutors × executorCores` 不等于 Blade 写并发数，真正的并发数 = 实际 partition 数（由 import 阶段决定）；短期控制手段：`numImportPartitions` + 调度层并发 DAG 数；长期解决方案：写侧加 Rhino 限流（按 Blade jdbcRef 粒度）。
🟡 Medium: [技术决策] `DtsClient#getDtsTaskSubscription` 新增主键感知：`createTopicAndCreateDtsTask` 签名新增 `List<String> primaryKeys` 参数，调用方（`MirrorFlowFullSyncInitHandler`、`WorkSheetActionController`）从 `dataSourceModel.getColumns()` 过滤 `isPrimaryKey=true` 提取后传入；`watchedTable.partitionField` 和 `watchedTable.primaryKey` 均设置为逗号拼接的主键列表。
🟡 Medium: [技术决策] `HdfsImporter.doImport()` 修复列名解析：CSV 读取后用 `MirrorConfigUtils.getNotSysAddColumnNames(mirrorFlow.getFlowConfig())` 取有序列名，调用 `raw.toDF(columnNames)` 重命名（原为 `_c0,_c1...`）；新增列数防御校验（文件列数 ≠ 配置列数时快速失败），避免静默列错位。核心假设：HDFS 文件物理列顺序与 `columnConfigs` 配置顺序一致。
🟡 Medium: [项目状态] Pontos 批量写入参数分析：`maxExecutors=360` 对应最多 360 个并发 JDBC 连接打到 Blade（高压），`exportBatchRange=400` 低于推荐值（建议 500~800）；建议优先降低 `maxExecutors`（→60~120）、`executorCores`（→2），同时调大 `exportBatchRange`（→500~800）。
🟢 Low: [任务流水] 修复 `MirrorFullSync` 线上 `java.lang.Error: Unresolved compilation problems`（`@Slf4j` log 字段 + `@Data` getter 未生成），根因为 `mvn deploy` 缺 `-am` 导致 Lombok APT 静默失败；修复方案：`mvn deploy -pl pontos-full-sync-job -am -DskipTests`。
🟡 KB 待办逾期：contexts/projects/datamatrix-kb — Lion 各 mirrorDb meta `cluster` 字段未补充（Blade 容量感知上线前置条件），25 天未处理（自 2026-04-16 起）。
🟡 KB 待办逾期：contexts/projects/datamatrix-kb — naiads/joiner 学城文档 contentId 待查补充，25 天未处理（自 2026-04-16 起）。
🟡 KB 待办逾期：contexts/projects/datamatrix-kb — P3 摘要（HBase 2716815553、镜像切换细节 2731293914）和血缘查询 API 确认，21 天未处理（自 2026-04-20 起）。
