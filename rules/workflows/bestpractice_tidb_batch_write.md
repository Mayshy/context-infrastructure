# BestPractice: TiDB 批量写入

> **使用方式**：`read` 本文件，边理解边执行。适用于涉及 TiDB（Blade）批量 JDBC 写入的所有场景。

---

## When to Use

- 设计或审查 TiDB（Blade）批量写入逻辑时
- 遇到批量写入性能问题或报错时
- 评估 `rewriteBatchedStatements=true` 是否生效时
- 设计 Spark/Flink 到 TiDB 的全量/增量同步时

---

## 核心约束

### 1. Batch Size 上限：≤ 200 行/事务

TiDB 官方 Best Practices 明确：超过 200 行性能下降。

**根因：** 每次 `executeBatch()` 是分布式 2PC 事务提交，batch 越大：
- 2PC 持有锁时间越长
- commit 越慢
- `txn-total-size-limit` 默认 100MB，超出直接报错

**实践建议：**
- 全量同步（Spark）：`DEFAULT_EXPORT_BATCH_RANGE` 设为 200（对齐官方建议）
- 增量同步（Flink）：500ms 窗口/100条 是合理起点，不超过 200 行/批

---

### 2. `rewriteBatchedStatements=true` 的两个陷阱

**陷阱一：对 upsert 语句完全无效**

mysql-connector-java 5.1.49（Zebra BladeDataSource 内核）不对 `INSERT...ON DUPLICATE KEY UPDATE` 执行 batch rewrite。

```java
// ❌ 这个参数对 upsert 无效，每条 SQL 仍单独发送
connection.prepareStatement("INSERT INTO t(c1,c2) VALUES(?,?) ON DUPLICATE KEY UPDATE ...");
```

**正确方案**：在 SQL 层显式构造 multi-row upsert：
```sql
INSERT INTO t(c1,c2) VALUES(?,?),(?,?),(?,?) ON DUPLICATE KEY UPDATE c1=VALUES(c1), c2=VALUES(c2)
```

**陷阱二：Zebra 封装不保证参数生效**

Zebra 封装的 `BladeDataSource` 不保证 `rewriteBatchedStatements=true` 参数透传生效，行为不透明。

**正确方案**：显式构造 multi-row INSERT SQL，行为透明可控：
```sql
-- 全量同步
INSERT IGNORE INTO t(c1,c2) VALUES(?,?),(?,?),(?,?)

-- 增量同步（upsert）
INSERT INTO t(c1,c2) VALUES(?,?),(?,?) ON DUPLICATE KEY UPDATE c1=VALUES(c1), c2=VALUES(c2)
```

---

### 3. 写入瓶颈分析框架

当全量同步写入速度随时间下降时，优先排查：

1. **TiDB 侧索引维护成本**：随数据写入，目标表变大，索引维护成本线性上升（Wave 3 比 Wave 1 慢 70% 的典型根因）
2. **并发写入锁竞争**：多 Executor 并发写同一表时，锁竞争加剧
3. **Spark 侧 GC**：通常不是主因（GC 时间 30s 量级，远小于 IO 等待）
4. **每行 new 对象**：如 `mapPartitions` 内每行 `new CSVParser()`，百万级数据量下 GC 压力显著

---

## 实现参考（Pontos 模式）

### multi-row INSERT IGNORE（全量同步）

```java
// SqlUtils.generateMultiRowInsertIgnoreSql(tableName, columns, batchSize)
// 生成：INSERT IGNORE INTO t(c1,c2) VALUES(?,?),(?,?),...

// SparkJdbcUtils.setValueToPreparedStatement(ps, row, structFields, rowOffset)
// psIndex 公式：rowOffset * structFields.length + pos + 1（1-based）
```

### multi-row upsert（增量同步）

```java
// SqlUtils.generateMultiRowUpsertSql(tableName, columns, batchSize)
// 生成：INSERT INTO t(c1,c2) VALUES(?,?),(?,?) ON DUPLICATE KEY UPDATE c1=VALUES(c1),...
```

---

## 与其他 Workflow 的关系

- 配合 `bestpractice_java_design_principles.md` 的层边界审查
- 涉及 Spark 写入时参考 `bestpractice_spark_rdd_pitfalls.md`

---

## 来源

| 日期 | 来源条目 |
|------|---------|
| 2026-04-27 | 🔴 Pontos Flink 实时同步三项性能优化方案确认 |
| 2026-05-06 | 🔴 TiDB 批量写入 batch size 建议 ≤200 行/事务 |
| 2026-05-08 | 🔴 Pontos Blade 全量同步 `BladeNormalExporter` 显式 multi-row INSERT |
| 2026-05-09 | 🔴 Pontos 增量同步 `rewriteBatchedStatements` 对 upsert 无效 |
