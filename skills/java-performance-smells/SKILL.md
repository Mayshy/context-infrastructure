---
name: java-performance-smells
description: Java 代码级性能嗅探。仅在 workflow_code_review 的 Phase 3（性能检测）检测到 Java 代码时调用，补充 Java 特有的性能问题模式。不独立触发。技术栈：Java 8+、Stream API、Spark/Flink、Blade JDBC、Spring Boot。
---

# Java 性能嗅探

本 skill 由 `workflow_code_review` 在 Phase 3（性能检测）中针对 Java 代码调用，补充通用 `performance-optimization` skill 未覆盖的 Java 特有模式。

**核心原则：先测量再优化。** 本 skill 标记的是"值得注意的嗅探点"，不是必须修复的 bug。

---

## 快速扫描命令

```bash
# 循环内 regex 编译
grep -rn "\.matches(\|\.split(\|Pattern\.compile" --include="*.java" [目标目录]

# 循环内字符串拼接
grep -rn '"+=' --include="*.java" [目标目录]

# findAll 无分页
grep -rn "findAll()" --include="*.java" [目标目录]

# 未指定容量的集合
grep -rn "new ArrayList<>()\|new HashMap<>()" --include="*.java" [目标目录]
```

---

## 1. 字符串操作

```java
// 🔴 循环内字符串拼接（O(n²)，每次创建新 String）
String result = "";
for (String s : items) {
    result += s;
}

// ✅ StringBuilder
StringBuilder sb = new StringBuilder(items.size() * 16); // 预估容量
for (String s : items) { sb.append(s); }
String result = sb.toString();

// ✅ 或 String.join / Collectors.joining
String result = String.join("", items);

// ✅ Java 9+ 简单拼接无需 StringBuilder（JVM invokedynamic 优化）
String msg = "User " + name + " at " + timestamp; // 这个没问题

// 🟡 String.format 有解析开销，热路径避免
log.debug(String.format("Processing %s id=%d", name, id)); // 慢

// ✅ SLF4J 参数化（懒求值，level 未开启时不拼接）
log.debug("Processing {} id={}", name, id);
```

---

## 2. Regex

```java
// 🔴 循环内 Pattern.compile（每次编译 regex，开销大）
for (String input : inputs) {
    if (input.matches("\\d{3}-\\d{4}")) { // 等价于 Pattern.compile(...).matcher(input).matches()
        process(input);
    }
}

// ✅ 预编译为静态常量
private static final Pattern PHONE = Pattern.compile("\\d{3}-\\d{4}");

for (String input : inputs) {
    if (PHONE.matcher(input).matches()) {
        process(input);
    }
}
```

---

## 3. Stream API（Spark/Flink 场景尤其注意）

```java
// 🔴 紧密循环内重复创建 Stream（百万级迭代时开销显著）
for (int i = 0; i < 1_000_000; i++) {
    boolean found = items.stream().anyMatch(item -> item.getId() == i);
}

// ✅ 预计算查找结构
Set<Integer> itemIds = items.stream()
    .map(Item::getId)
    .collect(Collectors.toSet());
for (int i = 0; i < 1_000_000; i++) {
    boolean found = itemIds.contains(i); // O(1)
}

// 🔴 并行 Stream + 共享可变状态（竞态条件）
List<String> results = new ArrayList<>();
items.parallelStream().forEach(results::add); // 竞态！

// ✅ 并行 Stream 用 collect
List<String> results = items.parallelStream()
    .map(this::process)
    .collect(Collectors.toList());

// ✅ 基本类型 Stream 避免 Boxing
int sum = numbers.stream().mapToInt(Integer::intValue).sum(); // 而非 reduce(0, Integer::sum)
```

**Spark/Flink 特别注意：**
```java
// 🔴 mapPartitions 内每行创建重对象（Pontos HermesImporter 的历史问题）
rdd.mapPartitions(iter -> {
    List<Result> results = new ArrayList<>();
    for (Row row : iter) {
        CSVParser parser = new CSVParser(); // 每行 new，GC 压力大
        results.add(parser.parse(row));
    }
    return results.iterator();
});

// ✅ 每个 partition 复用对象
rdd.mapPartitions(iter -> {
    CSVParser parser = new CSVParser(); // 每个 partition 创建一次
    List<Result> results = new ArrayList<>();
    for (Row row : iter) {
        results.add(parser.parse(row));
    }
    return results.iterator();
});

// 🔴 RDD 多次 Action 未 persist（触发重复计算）
rdd.count();                    // 触发一次计算
rdd.saveAsTextFile("output");   // 再次触发计算！

// ✅ persist 后再执行多个 Action
rdd.persist(StorageLevel.MEMORY_AND_DISK());
rdd.count();
rdd.saveAsTextFile("output");
rdd.unpersist();
```

---

## 4. Boxing/Unboxing

```java
// 🔴 紧密循环内 boxing（百万次创建 Long 对象）
Long sum = 0L;
for (int i = 0; i < 1_000_000; i++) {
    sum += i; // unbox Long → long，加法，再 box → Long
}

// ✅ 基本类型
long sum = 0L;

// 🔴 Map<Integer, ...> 的 containsKey 触发 boxing
Map<Integer, String> map = new HashMap<>();
int key = 42;
map.containsKey(key); // key 被 box 成 Integer

// 大量 int key 场景考虑 IntObjectHashMap（Eclipse Collections）
```

---

## 5. 集合

```java
// 🟡 List.contains() 在循环中（O(n) 每次）
List<String> allowed = getAllowed();
for (Request r : requests) {
    if (allowed.contains(r.getId())) { } // O(n) × O(n) = O(n²)
}

// ✅ 转 Set
Set<String> allowed = new HashSet<>(getAllowed());
for (Request r : requests) {
    if (allowed.contains(r.getId())) { } // O(1)
}

// 🟢 已知大小时指定初始容量（避免扩容）
List<User> users = new ArrayList<>(expectedSize);
Map<String, User> map = new HashMap<>(expectedSize * 4 / 3 + 1);

// 🔴 无界查询（Blade/MySQL 场景）
List<Row> all = bladeTemplate.query("SELECT * FROM Mirror_xxx"); // 百万行？

// ✅ 分页或 limit
bladeTemplate.query("SELECT * FROM Mirror_xxx LIMIT ? OFFSET ?", pageSize, offset);
```

---

## 6. Blade JDBC 专项（DataMatrix 场景）

```java
// 🔴 rewriteBatchedStatements 对 upsert 无效
// Zebra BladeDataSource 封装的 mysql-connector-java 5.1.49
// 不对 INSERT...ON DUPLICATE KEY UPDATE 执行 batch rewrite

// ✅ 显式构造 multi-row upsert SQL（已在 Pontos 实践）
// SqlUtils.generateMultiRowUpsertSql() / generateMultiRowInsertIgnoreSql()

// 🔴 连接池按 jdbcRef 缓存，首次参数生效后续忽略
// 调整 maxPoolSize 后需重启或等连接池重建

// 🔴 BladeBulkloadExporter 冗余 count()（已知问题）
// repartitionedRDD.count() 在下一步 Action 前多跑一次，等于双倍计算
```

---

## 审查 Checklist

### 🔴 高风险（通常值得修复）
- [ ] 循环内 `String +=`（用 `StringBuilder`）
- [ ] 循环内 `Pattern.compile` / `.matches()`（用静态常量）
- [ ] 无界查询无分页（Blade/MySQL `findAll()`）
- [ ] 并行 Stream 操作共享可变集合
- [ ] Spark `mapPartitions` 内每行 new 重对象
- [ ] RDD 多次 Action 未 `persist()`

### 🟡 中风险（先测量）
- [ ] 紧密循环内 boxing（`Long`/`Integer` 变量）
- [ ] `List.contains()` 在循环中（改 `Set`）
- [ ] Stream 在百万级循环内重复创建

### 🟢 低风险（有空再看）
- [ ] 集合未指定初始容量
- [ ] `String.format` 在日志中（改 SLF4J 参数化）
- [ ] 基本类型 Stream（`mapToInt`/`mapToLong`）未使用

---

## 与通用 performance-optimization skill 的分工

| 关注点 | 使用哪个 skill |
|--------|---------------|
| 测量方法、性能基线建立 | `performance-optimization` |
| N+1 查询、分页、缓存策略 | `performance-optimization` |
| Java 字符串/Regex/Stream/Boxing | **本 skill** |
| Spark/Flink RDD 计算优化 | **本 skill** |
| Blade JDBC 批量写入 | **本 skill** |
