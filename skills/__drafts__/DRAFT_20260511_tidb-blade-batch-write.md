---
name: tidb-blade-batch-write
description: >
  TiDB（Blade）批量写入操作指南。当涉及 Pontos/DataMatrix 向 Blade（TiDB）批量写入时触发，
  包括：设计批量写入方案、诊断写入性能问题、审查 rewriteBatchedStatements 是否有效、
  评估 batch size 选择、编写 multi-row INSERT/upsert SQL。
  触发词：Blade 写入、TiDB 批量、rewriteBatchedStatements、batch size、INSERT IGNORE、upsert、
  BladeNormalExporter、TimedUpdateBladeMirrorFunction。
requires:
  knowledge:
    - Pontos/DataMatrix 项目
    - TiDB（Blade）JDBC 写入
---

# TiDB（Blade）批量写入操作指南

## 触发场景

- 设计或审查向 Blade（TiDB）的批量 JDBC 写入逻辑
- 遇到批量写入性能问题或 `txn-total-size-limit` 报错
- 评估 `rewriteBatchedStatements=true` 是否对当前场景有效
- 编写全量同步（Spark）或增量同步（Flink）的写入 SQL

## 核心知识点

### 1. Batch Size 上限：≤ 200 行/事务

TiDB 官方 Best Practices 明确：超过 200 行性能下降。

根因：每次 `executeBatch()` 是分布式 2PC 事务提交，batch 越大，2PC 持有锁时间越长，commit 越慢。`txn-total-size-limit` 默认 100MB，超出直接报错。

### 2. `rewriteBatchedStatements=true` 的两个陷阱

**陷阱一（增量同步）**：mysql-connector-java 5.1.49（Zebra BladeDataSource 内核）对 `INSERT...ON DUPLICATE KEY UPDATE` 完全不执行 batch rewrite，参数形同虚设。

**陷阱二（全量同步）**：Zebra 封装的 `BladeDataSource` 不保证 `rewriteBatchedStatements=true` 参数透传生效，行为不透明。

**结论**：不要依赖 `rewriteBatchedStatements`，改用显式构造 multi-row SQL。

### 3. 正确方案：显式构造 multi-row SQL

```sql
-- 全量同步（INSERT IGNORE）
INSERT IGNORE INTO t(c1, c2) VALUES (?, ?), (?, ?), (?, ?)

-- 增量同步（upsert）
INSERT INTO t(c1, c2) VALUES (?, ?), (?, ?) ON DUPLICATE KEY UPDATE c1=VALUES(c1), c2=VALUES(c2)
```

Pontos 已实现：`SqlUtils.generateMultiRowInsertIgnoreSql()` 和 `SqlUtils.generateMultiRowUpsertSql()`。

### 4. 写入性能瓶颈排查顺序

1. TiDB 侧：目标表越来越大 → 索引维护成本线性上升（Wave 3 比 Wave 1 慢 70% 的典型原因）
2. 并发锁竞争：多 Executor 并发写同一表
3. Spark 侧 GC：通常不是主因
4. 对象创建：`mapPartitions` 内每行 `new` 重量级对象

## 操作指南

遇到 Blade 写入性能问题时：

1. 确认 batch size：是否 ≤ 200？若 `DEFAULT_EXPORT_BATCH_RANGE` 为 50（旧默认值），调整为 200
2. 检查 `rewriteBatchedStatements`：若代码依赖此参数，改为显式 multi-row SQL
3. 确认 SQL 类型：全量用 `INSERT IGNORE`，增量用 `ON DUPLICATE KEY UPDATE`
4. 性能分析：先看 TiDB 侧索引维护，再看 Spark 侧 GC

## 来源条目

| 日期 | 条目 |
|------|------|
| 2026-04-27 | 🔴 Pontos Blade 批量写入扩展陷阱（commit e189d4da） |
| 2026-05-06 | 🔴 TiDB 批量写入 batch size 建议 ≤200 行/事务 |
| 2026-05-08 | 🔴 BladeNormalExporter 改为显式 multi-row INSERT IGNORE |
| 2026-05-09 | 🔴 TimedUpdateBladeMirrorFunction rewriteBatchedStatements 对 upsert 无效 |

## 相关资源

- Workflow: `rules/workflows/bestpractice_tidb_batch_write.md`（详细设计原则）
- 实现参考：`pontos/src/.../SqlUtils.java`（`generateMultiRowInsertIgnoreSql`/`generateMultiRowUpsertSql`）
