# BestPractice: Spark RDD 常见陷阱

> **使用方式**：`read` 本文件，边理解边执行。适用于 Spark 作业设计、代码审查、性能诊断。

---

## When to Use

- 设计或审查 Spark RDD/DataFrame 作业时
- 发现计数器（Accumulator）值异常（偏大）时
- 发现 Spark 作业某个阶段执行了两遍时
- 审查 `mapPartitions` 内的对象创建模式时

---

## 陷阱一：RDD 未 persist，多次 Action 触发重复计算

### 问题

```java
// ❌ repartitionRDD 未 persist
JavaRDD<Row> repartitionRDD = inputRDD.repartition(partitions).mapToPair(lambda);

long count = repartitionRDD.count();          // Action 1：触发 mapToPair lambda
repartitionRDD.saveAsNewAPIHadoopFile(...);   // Action 2：再次触发 mapToPair lambda
```

**后果：**
- `mapToPair` 中的 Accumulator（如 `docAcc`）被累加两次，最终值是实际行数的 2 倍
- 有备集群（双写）时则是 3 倍
- 整个 RDD 计算链被执行两遍，浪费资源

### 修复

```java
// ✅ 先 persist，再执行多个 Action
JavaRDD<Row> repartitionRDD = inputRDD.repartition(partitions).mapToPair(lambda).persist(StorageLevel.MEMORY_AND_DISK());

long count = repartitionRDD.count();          // 触发计算，结果缓存
repartitionRDD.saveAsNewAPIHadoopFile(...);   // 复用缓存，不重新计算

repartitionRDD.unpersist();  // 用完释放
```

**实际案例（Hermes DataSinker）：**
`DataSinker.sinkJoinResultDoubleCluster()` 中 `repartitionRDD.count()` 和 `saveAsNewAPIHadoopFile()` 两次 Action 导致 `docAcc` 最终值是实际行数的 2 倍（有备集群则 3 倍）。

---

## 陷阱二：冗余 count() 导致 repartitionAndSort 执行两遍

### 问题

```java
// ❌ BladeBulkloadExporter 模式
for (String index : indices) {
    JavaRDD<Row> rdd = inputRDD.persist(...);
    long count = rdd.count();                         // Action 1：触发完整计算
    JavaRDD<Row> repartitioned = rdd.repartition(N); // 依赖 rdd，但 rdd 已 persist
    repartitioned.count();                            // Action 2：重复执行 repartitionAndSort
    repartitioned.mapPartitions(...).collect();       // Action 3
}
```

**后果：** 每个 index 串行走 persist→count→repartitionAndSort→count→upload，index 数量多时耗时线性叠加。

### 修复

去掉冗余的 `repartitionedRecordRDD.count()`，只保留最终 Action（`mapPartitions + collect()`）。

---

## 陷阱三：mapPartitions 内每行 new 对象

### 问题

```java
// ❌ HermesImporter 模式：每行 new CSVParser
inputRDD.mapPartitions(rows -> {
    List<Row> result = new ArrayList<>();
    for (Row row : rows) {
        CSVParser parser = new CSVParser(...);  // 每行都 new，百万级数据下 GC 压力显著
        result.add(parser.parse(row));
    }
    return result.iterator();
});
```

### 修复

```java
// ✅ per-partition 复用解析器
inputRDD.mapPartitions(rows -> {
    CSVParser parser = new CSVParser(...);  // 每个 partition 只 new 一次
    List<Row> result = new ArrayList<>();
    for (Row row : rows) {
        result.add(parser.parse(row));
    }
    return result.iterator();
});
```

---

## 诊断清单

遇到 Spark 作业性能问题或计数器异常时，按顺序检查：

- [ ] 同一 RDD 是否被多个 Action 使用？→ 是否已 `persist()`？
- [ ] Accumulator 值是否偏大（2x/3x）？→ 检查是否有未 persist 的 RDD 被多次触发
- [ ] 某阶段是否执行了两遍？→ 检查是否有冗余 `count()`
- [ ] `mapPartitions` 内是否每行 new 重量级对象？→ 提取到 partition 级别初始化

---

## 来源

| 日期 | 来源条目 |
|------|---------|
| 2026-05-08 | 🟡 Hermes 全量计算 `DataSinker.sinkJoinResultDoubleCluster()` docAcc 重复累加 Bug |
| 2026-05-08 | 🟡 Pontos Spark 全量同步 `BladeBulkloadExporter` 冗余 count() |
| 2026-05-08 | 🔴 Pontos Spark 全量同步写入瓶颈分析（HermesImporter 每行 new CSVParser） |
