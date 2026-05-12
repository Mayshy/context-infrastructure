# Workflow: DataMatrix 缺陷扫描

## 元数据

- **类型**: Workflow
- **适用场景**: DataMatrix 项目（pontos/hermes/athena/kugget/worksheet）存量缺陷扫描、技术债治理、发布前质量门禁
- **相关 Skills**: `spring-boot-patterns`、`java-code-review`、`java-concurrency-review`、`java-performance-smells`
- **代码库路径**: `/Users/shenhuayu/Desktop/Project/`
- **创建日期**: 2026-05-10
- **最后更新**: 2026-05-10

## 与 `workflow_code_review.md` 的区别

| 维度 | workflow_code_review | 本 workflow |
|------|---------------------|------------|
| 扫描对象 | PR 变更（增量） | 模块/服务代码（存量） |
| 触发方式 | 人工，每次 PR | 按需 L1 或定期 L2 |
| 扫描范围 | diff 相关文件 | 指定服务的全部 Java 文件 |
| 输出形式 | Review 报告（行内批注风格） | 结构化缺陷报告（file:line + 分级） |
| 目标 | 阻止坏代码合入 | 治理存量技术债 |

---

## 触发场景

**L1 按需扫描**（聚焦，快速）：
- 怀疑某个模块有特定类型缺陷（如"检查 hermes 的事务问题"）
- 新功能上线前的专项 P0 检查
- 生产故障后的根因类缺陷全量排查

**L2 定期全量扫描**（全面，产出报告）：
- 每月技术债盘点
- 大版本发布前
- 季度代码质量回顾

---

## 7 大缺陷类别（ROI 排序）

> **扫描原则**：每次运行聚焦 1-3 个类别。全部 7 类同时扫会产生噪音，开发者会开始忽略报告。

| ID | 类别 | 优先级 | 引用 Skill | 典型 DataMatrix 案例 |
|----|------|--------|-----------|---------------------|
| CAT-1 | 事务陷阱 | **P0** | `spring-boot-patterns` | hermes 多步写无 @Transactional；@Transactional private 方法 |
| CAT-2 | Mafka 消费安全 | **P0** | `spring-boot-patterns` | AthenaMafkaConsumer catch 后 return true；异常吞噬导致消息永久丢失 |
| CAT-3 | 资源管理 | P1 | `java-code-review` | Blade JDBC 连接未关闭；流/HTTP Client 无超时；Pigeon 调用无 timeout |
| CAT-4 | Null 安全 | P1 | `java-code-review` | 三层链式调用无 null 检查；Optional.get() 未 isPresent |
| CAT-5 | 并发安全 | P1 | `java-concurrency-review` | 静态 HashMap 无同步；Flink 算子实例变量共享状态 |
| CAT-6 | Lion 配置合规 | P1 | `spring-boot-patterns` | 密码 key 无 appKey 隔离；Lion Key 硬编码字符串未走 LionKeyConst |
| CAT-7 | 性能陷阱 | P2 | `java-performance-smells` | N+1 查询；@Transactional 内嵌 Pigeon/HTTP 调用；无界查询无分页 |

---

## Step 0：确定扫描范围

在开始前，明确两个参数：

**参数 1：目标服务**（选一个或多个）
```
pontos   → /Users/shenhuayu/Desktop/Project/pontos/pontos-server/src/main/java/
hermes   → /Users/shenhuayu/Desktop/Project/hermes/hermes-server/src/main/java/
athena   → /Users/shenhuayu/Desktop/Project/athena/athena-api/src/main/java/
kugget   → /Users/shenhuayu/Desktop/Project/kugget/kugget-server/src/main/java/
worksheet → /Users/shenhuayu/Desktop/Project/worksheet/worksheet-server/src/main/java/
全部      → /Users/shenhuayu/Desktop/Project/{pontos,hermes,athena,kugget,worksheet}/
```

**参数 2：目标类别**（选 1-3 个，不要全选）
- 快速检查（15 分钟）→ 选 CAT-1 + CAT-2
- 发布前门禁（30 分钟）→ 选 CAT-1 + CAT-2 + CAT-3
- 全量月度盘点（1-2 小时）→ 全部 7 类，分批执行

---

## Step 1：候选文件定位（grep 确定性扫描）

> **原则**：先用 grep 找到"有嫌疑"的文件，再用 LLM 做语义分析。不要让 LLM 盲目扫描所有文件。

### CAT-1：事务陷阱

```bash
TARGET="{目标路径}"

# 1a. 多步写无事务：找 Service 方法中连续调用 mapper 的文件
grep -rln "Mapper\|\.insert\|\.update\|\.delete\|\.save" \
  --include="*.java" "$TARGET" | \
  xargs grep -L "@Transactional" | \
  grep -i "ServiceImpl"

# 1b. @Transactional 在 private 方法（Spring AOP 不生效）
grep -rn "@Transactional" --include="*.java" "$TARGET" -A1 | \
  grep -B1 "private "

# 1c. @Transactional 方法内有 Pigeon/HTTP 远程调用（持有连接做远程调用）
grep -rln "@Transactional" --include="*.java" "$TARGET" | \
  xargs grep -l "ServiceFactory\|pigeonService\|RestTemplate\|OkHttp\|Retrofit"
```

**预期候选文件数**：hermes 15-40 个，pontos 5-15 个

### CAT-2：Mafka 消费安全

```bash
# 2a. Consumer 中 catch 后 return true/SUCCESS（异常吞噬）
grep -rln "Consumer\|Listener\|Receiver" --include="*.java" "$TARGET" | \
  xargs grep -l "catch\|Exception" | \
  xargs grep -ln "return true\|CONSUME_SUCCESS\|ConsumeStatus.SUCCESS"

# 2b. Consumer 方法无 try-catch（未处理异常会导致消费停止）
grep -rln "@MafkaConsumer\|MafkaClient\|recvMessage\|@MdpMafkaMsgReceive" \
  --include="*.java" "$TARGET"
```

**预期候选文件数**：全库约 8-12 个 Consumer 文件

### CAT-3：资源管理

```bash
# 3a. Pigeon 调用无超时配置
grep -rln "InvokerConfig\|ServiceFactory.getService" \
  --include="*.java" "$TARGET" | \
  xargs grep -L "setTimeout\|setConnectTimeout"

# 3b. Blade JDBC 连接池配置（检查是否有 checkoutTimeout/maxPoolSize）
grep -rln "BladeDataSource" --include="*.java" "$TARGET"

# 3c. InputStream/Connection 未用 try-with-resources
grep -rn "new.*InputStream\|new.*Connection\|new.*Reader" \
  --include="*.java" "$TARGET" | \
  grep -v "try\s*(" | grep -v "//.*new"
```

### CAT-4：Null 安全

```bash
# 4a. Optional.get() 未先检查
grep -rn "\.get()" --include="*.java" "$TARGET" | \
  grep "Optional" | grep -v "isPresent\|orElse\|ifPresent\|map("

# 4b. 三层以上链式调用（高 NPE 风险）
grep -rn "\.[a-zA-Z]*().[a-zA-Z]*().[a-zA-Z]*()" \
  --include="*.java" "$TARGET" | \
  grep -v "//\|import\|test\|Test" | head -30
```

### CAT-5：并发安全

```bash
# 5a. 静态 HashMap/List（多线程共享状态，无同步）
grep -rn "static.*HashMap\|static.*ArrayList\|static.*List<\|static.*Map<" \
  --include="*.java" "$TARGET" | \
  grep -v "final.*Collections\|ConcurrentHashMap\|unmodifiable\|//\|test"

# 5b. Flink 算子中的实例变量（应使用托管状态）
grep -rln "extends.*RichFunction\|extends.*ProcessFunction\|extends.*MapFunction" \
  --include="*.java" "$TARGET" | \
  xargs grep -l "private.*[^static].*;$" 2>/dev/null
```

### CAT-6：Lion 配置合规

```bash
# 6a. Lion Key 硬编码字符串（未走 LionKeyConst 常量）
# 大写字母开头的字符串字面量传给 Lion.get*()
grep -rn 'Lion\.get\w*\s*(\s*"[A-Z]' --include="*.java" "$TARGET"

# 6b. Lion.getStringValue() 单参数版本（无 appKey，无法按服务隔离）
grep -rn "Lion\.getStringValue\s*(" --include="*.java" "$TARGET" | \
  grep -v "GlobalAttribute\|APPKEY\|appkey\|appKey"

# 6c. 含敏感词的 Lion Key（密码/token/secret 裸用）
grep -rn 'Lion\.get\w*.*[Pp]assword\|Lion\.get\w*.*[Ss]ecret\|Lion\.get\w*.*[Tt]oken' \
  --include="*.java" "$TARGET"
```

### CAT-7：性能陷阱

```bash
# 7a. @Transactional 方法内有 HTTP/RPC 调用（持锁做远程调用）
# 见 CAT-1c，复用结果

# 7b. Service 方法中无分页的全量查询
grep -rln "selectAll\|findAll\|listAll\|getAll\|queryAll" \
  --include="*.java" "$TARGET/service" | \
  xargs grep -l "List<" 2>/dev/null

# 7c. 循环内 DB 调用（N+1 查询）
grep -rn "for.*{" --include="*.java" "$TARGET" -A5 | \
  grep "Mapper\.\|\.select\|\.insert\|\.update" | head -20
```

---

## Step 2：LLM 语义分析

> 对 Step 1 找到的候选文件，逐批做深度分析。每批不超过 5 个文件。

### 分析 Prompt 模板

```
你是 DataMatrix 项目的 Java 代码审查专家。

**技术栈**：Java 8, Spring Boot, Mafka（消息队列）, Pigeon（RPC）, Blade JDBC, Lion（配置中心）, Zebra（DB 连接池）

**本次扫描类别**：{CAT-X 类别名称}

**审查文件**：
{粘贴文件内容或关键片段}

**输出要求**：
1. 只报告置信度 >= 0.7 的发现
2. 每个发现必须包含：file:line 引用、问题描述、严重级别（P0/P1/P2）、修复建议
3. 如果没有发现，明确说"未发现 {类别} 问题"
4. 最多报告 5 个发现（超出写"另有 N 处类似问题"）

**严重级别定义**：
- P0：可导致数据损坏、消息丢失、系统崩溃（必须修复）
- P1：可能引发生产故障，有明确修复路径（本 sprint 修复）
- P2：代码质量问题，不紧急（下个 sprint 处理）

**输出格式**：
### {文件名}
**[P0/P1/P2] {问题标题}**
- 位置：`{文件名}:{行号}`
- 问题：{具体描述}
- 修复：{建议，含代码示例}
```

### 并行分析（多文件时）

当候选文件 > 10 个时，用并行 subagent 分批处理：

```
参考 workflow_parallel_subagents.md：
- 每个 subagent 处理 3-5 个文件
- 并行度 ≤ 5
- 每个 subagent 的 prompt 包含完整的技术栈上下文
- 汇总时：去重（file+line 相同的合并）+ 按 P0/P1/P2 排序
```

---

## Step 3：结果汇总与输出

### 报告模板

```markdown
# DataMatrix 缺陷扫描报告

**扫描日期**：{YYYY-MM-DD}
**扫描范围**：{服务名} / {类别}
**扫描文件数**：{N} 个 Java 文件
**发现问题数**：P0: {n} | P1: {n} | P2: {n}

---

## P0 问题（必须修复）

### [CAT-1] 事务缺失
**hermes/CanvasServiceImpl.java:327**
- 问题：`deleteCanvas()` 依次调用 deleteByPrimaryKey + deleteCanvasNodes + deleteCanvasEdges，三步写操作无 @Transactional，任一步失败会留下孤儿数据
- 修复：在方法上添加 `@Transactional(rollbackFor = Exception.class)`

---

## P1 问题（本 sprint 修复）

...

## P2 问题（下个 sprint 处理）

...

---

## 已知误报说明

{如有误报，在此说明原因，避免下次重复报告}

---

## 下次扫描建议

- 重点关注：{上次未扫描的类别}
- 验证修复：{本次 P0 修复后，下次扫描时验证}
```

---

## Step 4：问题跟踪

> **关键原则**：扫描产出的问题如果没有跟踪机制，会被遗忘。

**P0 问题**：
1. 立即在当前 session 创建修复 todo
2. 优先在下一个 PR 中修复
3. 修复后在下次扫描中验证

**P1/P2 问题**：
1. 追加到 `datamatrix-kb/04_cross_cutting/tech_debt.md`（如不存在则创建）
2. 格式：`| {日期} | {file:line} | {类别} | {描述} | {状态} |`
3. 每月技术债盘点时回顾，标记已修复项

**tech_debt.md 示例格式**：
```markdown
# DataMatrix 技术债追踪

| 发现日期 | 位置 | 类别 | 描述 | 严重级别 | 状态 |
|---------|------|------|------|---------|------|
| 2026-05-10 | hermes/CanvasServiceImpl.java:327 | CAT-1 事务 | deleteCanvas 三步写无事务 | P0 | 待修复 |
| 2026-05-10 | athena/AthenaMafkaConsumer.java:100 | CAT-2 Mafka | catch 后 return true 吞噬异常 | P0 | 待修复 |
| 2026-05-10 | pontos/HbaseDataSource.java:94 | CAT-6 Lion | HBase 密码 key 无 appKey 隔离 | P1 | 待修复 |
```

---

## 快速参考：已知高风险文件清单

> 基于 2026-05-10 初始扫描，以下文件已确认存在问题，下次扫描优先覆盖：

### P0 确认问题
| 文件 | 行号 | 类别 | 问题摘要 |
|------|------|------|---------|
| `hermes/hermes-server/.../canvas/impl/CanvasServiceImpl.java` | 327 | CAT-1 | deleteCanvas 三步写无事务 |
| `hermes/hermes-server/.../schedule/impl/ScheduleServiceImpl.java` | 103 | CAT-1 | 三表连续 insert 无事务 |
| `hermes/hermes-server/.../embedding/impl/EmbeddingModelServiceImpl.java` | 175 | CAT-1 | model+relation 双写无事务 |
| `pontos/pontos-server/.../service/impl/DataSourceFieldServiceImpl.java` | 48 | CAT-1 | delete+insert 无事务（注释明确说明） |
| `hermes/hermes-server/.../consumer/AthenaMafkaConsumer.java` | 100 | CAT-2 | catch 后 return true，调度状态永久丢失 |
| `worksheet/worksheet-server/.../mafka/EventConsumer.java` | 95 | CAT-2 | 注释自承认 bug，工单事件处理失败无感知 |

### P1 确认问题
| 文件 | 行号 | 类别 | 问题摘要 |
|------|------|------|---------|
| `pontos/pontos-dal/.../dal/data/HbaseDataSource.java` | 94 | CAT-6 | HBase 密码 key 无 appKey，两处重复 |
| `pontos/pontos-realtime-sync-job/.../ManualGenDataChangeEventFunction.java` | 86 | CAT-6 | 同上，重复裸用 |
| `athena/athena-registry/.../ZookeeperRegistryProperties.java` | 48 | CAT-6 | ZK 地址无默认值裸用 |
| `pontos/pontos-server/.../handler/MirrorFlowRealtimeSyncCatchUpHandler.java` | 67 | CAT-4 | 三层链式调用无 null 检查 |
| `worksheet/worksheet-server/.../controller/InternalController.java` | 223 | CAT-4 | getUserInfo().getUserId() 无 null 检查 |
| `kugget/kugget-server/.../service/impl/TaskExecutorVersionServiceImpl.java` | 213 | CAT-1 | deleteAll+循环 insert 无事务 |

---

## 执行示例

### 示例 1：快速 P0 检查（hermes 服务，CAT-1+CAT-2）

```bash
# Step 1：定位候选文件
TARGET="/Users/shenhuayu/Desktop/Project/hermes/hermes-server/src/main/java/"

# CAT-1：找多步写无事务的 ServiceImpl
grep -rln "\.insert\|\.update\|\.delete" --include="*.java" "$TARGET" | \
  xargs grep -L "@Transactional" | grep "ServiceImpl"

# CAT-2：找 Consumer 文件
find "$TARGET" -name "*Consumer*.java" -o -name "*Listener*.java"
```

```
# Step 2：读取候选文件，用 LLM 分析
# 对每个文件：read 文件内容 → 套用上面的 Prompt 模板 → 记录发现

# Step 3：汇总，写入 tech_debt.md
```

### 示例 2：月度全量扫描（全部服务，全部类别）

```
1. 按服务分批：pontos → hermes → athena → kugget → worksheet
2. 每个服务按类别顺序：CAT-1 → CAT-2 → CAT-3 → ... → CAT-7
3. 每类别：grep 定位 → LLM 分析（并行 subagent）→ 记录
4. 最终汇总报告，更新 tech_debt.md
5. P0 问题立即创建修复 todo
```

---

## 健康指标（每月追踪）

| 指标 | 目标 | 当前基线（2026-05） |
|------|------|-------------------|
| P0 未修复数 | 0 | 6 |
| P1 未修复数 | < 10 | ~15 |
| 误报率 | < 5% | 待建立 |
| P0 平均修复时间 | < 1 周 | 待建立 |
| 月新增 P0 数 | 趋势下降 | 待建立 |
